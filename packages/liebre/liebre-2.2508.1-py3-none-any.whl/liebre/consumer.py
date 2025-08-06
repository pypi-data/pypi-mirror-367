import time
from threading import Thread, Condition, Event
from .utils import (
    get_partition_queue_name,
    get_backup_queue_name,
    get_queue_name,
)
from .logger import logger
from .rabbit_store import RabbitStore
from .message import Message
from .errors import SkipMessageError


class Consumer(RabbitStore):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._callbacks = {}
        self._channel_by_message_queue = {}
        self._threads = []
        self._stopped_consumer = Condition()
        self._stop_consuming = Event()

    @property
    def threads(self):
        return self._threads

    def consume(
        self,
        queue,
        callback,
        queue_options=None,
        backup=False,
    ):
        if queue_options is None:
            queue_options = {}
        queue_options = self._queue_options | queue_options

        thread = Thread(
            target=self._consume_target,
            daemon=True,
            kwargs={
                'queue': queue,
                'callback': callback,
                'queue_options': queue_options,
                'backup': backup,
            },
        )
        self._threads.append(thread)
        thread.start()

    @RabbitStore.thread_safe
    def close(self):
        with self._stopped_consumer:
            self._stopped_consumer.notify_all()
        self._stop_consuming.set()
        self.join()
        super()._close()
        self._callbacks = {}
        self._channel_by_message_queue = {}

    def commit(self, message: Message):
        message_queue = (message.properties.message_id, message.queue)
        if message_queue not in self._channel_by_message_queue:
            raise ValueError('Committing unknown message.')

        channel = self._channel_by_message_queue[message_queue]
        channel.basic_ack(delivery_tag=message.method.delivery_tag)
        del self._channel_by_message_queue[message_queue]

    def is_alive(self):
        for thread in self._threads:
            if not thread.is_alive():
                return False
        return True

    def join(self):
        for thread in self.threads:
            thread.join()

    def _send_to_bottom(
        self,
        message,
        channel,
    ):
        try:
            channel.basic_publish(
                exchange=self._exchange,
                routing_key=message.queue,
                body=message.raw_content,
                properties=message.properties,
                mandatory=True
            )
            if self._auto_ack:
                self.commit(message)

        except Exception as error:
            logger.exception(
                'Could not send message to the bottom of the queue.',
                error=error,
                exchange=self._exchange,
                queue=message.queue,
            )
            raise error

    def _get_message_retries(self, message):
        if message.uid in self._message_retries:
            return self._message_retries[message.uid]
        else:
            return 0

    def _increment_message_retries(self, message):
        self._message_retries[message.uid] = (
            self._message_retries[message.uid]
            + 1 if message.uid in self._message_retries else 1
        )

    def _remove_message_retries(self, message):
        if (message.uid in self._message_retries):
            del self._message_retries[message.uid]

    def _handle_message(
        self,
        channel,
        callback,
        properties,
        message,
        queue_options=None,
        partition_queue=None,
    ):
        if queue_options is None:
            queue_options = {}
        queue_options = self._queue_options | queue_options

        try:
            raw_message = message
            message = Message(
                raw_message,
                properties,
                callback,
                partition_queue,
            )

            retries = self._get_message_retries(message)

            if (queue_options['dead_letters'] and self._max_retries
                    and retries >= self._max_retries):
                logger.error(
                    f'Message rejected after {self._max_retries} retries.',
                    queue=partition_queue,
                    message_id=message.id,
                )
                channel.basic_reject(
                    delivery_tag=callback.delivery_tag,
                    requeue=False,
                )
                return

            if (retries > 0):
                time.sleep(self._sleep_seconds_on_retry)

            message_queue = (message.id, partition_queue)
            self._channel_by_message_queue[message_queue] = channel
            queue = get_queue_name(partition_queue)

            try:
                self._callbacks[queue]['callback'](message)

                if self._auto_ack:
                    self.commit(message)
                self._remove_message_retries(message)

            except Exception as error:
                if not isinstance(error, SkipMessageError):
                    self._increment_message_retries(message)

                    logger.exception(
                        f'Callback error ({retries + 1}/{self._max_retries}).',
                        error=error,
                        exchange=self._exchange,
                        queue=partition_queue,
                        message_id=message.id,
                    )

                # With quorum, the message is sent to bottom by default
                if queue_options['quorum']:
                    channel.basic_nack(
                        delivery_tag=callback.delivery_tag,
                        requeue=True,
                    )

                else:
                    self._send_to_bottom(
                        message,
                        channel,
                    )

        except Exception:
            logger.exception('Could not process the message.')
            try:
                channel.basic_nack(
                    delivery_tag=callback.delivery_tag,
                    requeue=True,
                )
            except Exception:
                pass

    def reconnect_consumer(function):
        def _(*args, **kwargs):
            retries = 0
            instance = args[0]

            while True:
                if instance._stop_consuming.is_set():
                    break

                channel = None
                try:
                    channel = instance._get_channel()
                    return function(
                        instance,
                        channel,
                        *args[1:],
                        **kwargs,
                    )

                except Exception as error:
                    if channel is not None:
                        RabbitStore._close_channel(channel)

                    time.sleep(instance._sleep_seconds_on_retry)

                    retries += 1
                    if (instance._max_retries == 0
                            or (instance._max_retries
                                and retries >= instance._max_retries)):
                        raise error

                    logger.warning(
                        'Reconnecting... '
                        f'({retries}/{instance._max_retries or "inf"})',
                        error=error
                    )

                    try:
                        instance.connect(force=True)
                        channel = instance._get_channel()
                        retries = 0

                    except Exception:
                        logger.exception(
                            'Reconnecting... '
                            f'({retries}/{instance._max_retries or "inf"})',
                        )

        return _

    @reconnect_consumer
    def _consume_target(
        self,
        channel,
        queue,
        callback,
        backup,
        queue_options=None,
    ):
        self._callbacks[queue] = {'callback': callback}

        if queue not in self._declared_logical_queues:
            self.declare_queue(
                queue,
                options=queue_options,
            )

        for partition in range(self._partitions):
            if backup:
                partition_queue = get_backup_queue_name(queue, partition)
            else:
                partition_queue = get_partition_queue_name(queue, partition)

            channel.basic_consume(
                queue=partition_queue,
                auto_ack=False,  # Handled by Liebre
                on_message_callback=(
                    lambda *args, queue_options=queue_options,  #
                    partition_queue=partition_queue, **kwargs:  #
                    self._handle_message(
                        *args,
                        queue_options=queue_options,
                        partition_queue=partition_queue,
                        **kwargs,
                    )
                )
            )

            logger.info(
                'Waiting for messages...',
                queue=partition_queue,
                exchange=self._exchange,
            )

        def start_consuming():
            try:
                channel.start_consuming()
            except Exception as error:
                with self._stopped_consumer:
                    self._stopped_consumer.notify_all()

                logger.warning(
                    'Consumer stopped.',
                    error=error,
                    queue=queue,
                    exchange=self._exchange,
                )

        consume_thread = Thread(target=start_consuming)
        consume_thread.start()

        with self._stopped_consumer:
            self._stopped_consumer.wait()

        try:
            channel.stop_consuming()
        except Exception:
            pass

        consume_thread.join()
        RabbitStore._close_channel(channel)
