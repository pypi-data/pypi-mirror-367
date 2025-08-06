from .logger import logger
import time
import pika
from .utils import (
    get_partition_queue_name,
    get_backup_queue_name,
    get_dead_letter_queue_name,
)
from threading import Lock
import ssl


class RabbitStore:

    EXCHANGE_OPTIONS = {
        'type': 'direct',
        'durable': True,
        'auto_delete': False,
    }

    QUEUE_OPTIONS = {
        'quorum': True,
        'lazy': True,
        'durable': True,
        'auto_delete': False,
        'backup': False,
        'dead_letters': True,
    }

    def __init__(
        self,
        user=None,
        password=None,
        host=None,
        port=None,
        vhost=None,
        exchange=None,
        tls=None,
        max_retry_seconds=None,
        max_retries=None,
        sleep_seconds_on_retry=None,
        auto_ack=True,
        prefetch=None,
        partitions=None,
        exchange_options=None,
        queue_options=None,
        logger_options=None,
    ):
        if logger_options is not None:
            logger.reload(**logger_options)

        self._user = user or 'guest'
        self._password = password or 'guest'
        self._host = host or 'localhost'
        self._port = port or 5672
        self._vhost = vhost or '/'
        self._exchange = exchange
        self._tls = True if tls else False
        self._max_retry_seconds = (
            max_retry_seconds
            if max_retry_seconds and max_retry_seconds > 0 else None
        )

        self._sleep_seconds_on_retry = (
            sleep_seconds_on_retry
            if sleep_seconds_on_retry and sleep_seconds_on_retry > 0 else 1
        )

        # For infinite retries, max_retries must be None
        self._max_retries = max_retries
        if self._max_retries is None and self._max_retry_seconds is not None:
            self._max_retries = (
                self._max_retry_seconds // self._sleep_seconds_on_retry
            )

        self._auto_ack = auto_ack
        self._prefetch = prefetch if prefetch and prefetch >= 0 else 10
        self._partitions = partitions if partitions and partitions >= 1 else 1

        self._exchange_options = self.__class__.EXCHANGE_OPTIONS.copy()
        if exchange_options:
            self._exchange_options = self._exchange_options | exchange_options

        self._queue_options = self.__class__.QUEUE_OPTIONS.copy()
        if queue_options:
            self._queue_options = self._queue_options | queue_options

        self._declared_queues = set()
        self._declared_logical_queues = set()

        self._message_retries = {}
        self._lock = Lock()

        self._initialized = False
        self._channel = None

    def reconnect(function):
        def _(*args, **kwargs):
            instance = args[0]
            retries = 0

            while True:
                try:
                    return function(*args, **kwargs)

                except Exception as error:
                    time.sleep(instance._sleep_seconds_on_retry)

                    retries += 1
                    if (instance._max_retries == 0
                            or (instance._max_retries
                                and retries >= instance._max_retries)):
                        raise error

                    try:
                        instance.connect(force=True)
                        retries = 0

                    except Exception:
                        logger.exception(
                            'Reconnecting... '
                            f'({retries}/{instance._max_retries or "inf"})',
                        )

        return _

    def thread_safe(function):
        def _(*args, **kwargs):
            instance = args[0]
            with instance._lock:
                return function(*args, **kwargs)

        return _

    @thread_safe
    def connect(self, force=False):
        if self._initialized and not force:
            return

        if force and self._channel:
            RabbitStore._close_channel(self._channel)

        self._channel = self._get_channel()
        self._declare_exchange()

        self._initialized = True

    def _close(self):
        if self._channel:
            RabbitStore._close_channel(self._channel)
            self._channel = None
        self._initialized = False

    @thread_safe
    def close(self):
        return self._close()

    @reconnect
    @thread_safe
    def get_info(self):
        status = {}
        for queue_name in self._declared_queues:
            queue_data = self._channel.queue_declare(queue_name, passive=True)
            status[queue_name] = {
                'messages': queue_data.method.message_count,
                'consumers': queue_data.method.consumer_count,
            }
        return status

    @reconnect
    @thread_safe
    def declare_queue(
        self,
        queue,
        options=None,
    ):
        if options is None:
            options = {}
        options = self._queue_options | options

        if options['dead_letters']:
            self._declare_queue(
                queue,
                options,
                dead_letter=True,
            )

        for partition in range(self._partitions):
            if options['backup']:
                self._declare_queue(
                    queue,
                    options,
                    partition=partition,
                    backup=True,
                )

            self._declare_queue(
                queue,
                options,
                partition=partition,
            )

    def _declare_queue(
        self,
        queue,
        options,
        partition=None,
        dead_letter=False,
        backup=False,
    ):
        arguments = {}
        if options['quorum']:
            arguments['x-queue-type'] = 'quorum'
        else:
            arguments['x-queue-type'] = 'classic'
            if options['lazy']:
                #  Quorum queues cannot be defined as lazy.
                arguments['x-queue-mode'] = 'lazy'

        dead_letter_queue = get_dead_letter_queue_name(queue)

        # Dead letter queue
        if dead_letter:
            queue_name = dead_letter_queue

        # Backup queue
        elif backup:
            backup_queue = get_backup_queue_name(queue, partition)
            queue_name = backup_queue

        # Partition queue
        else:
            self._declared_logical_queues.add(queue)
            partition_queue = get_partition_queue_name(queue, partition)
            self._declared_queues.add(partition_queue)

            queue_name = partition_queue

            if options['dead_letters']:
                arguments['x-dead-letter-exchange'] = self._exchange
                arguments['x-dead-letter-routing-key'] = dead_letter_queue

        self._channel.queue_declare(
            queue_name,
            durable=options['durable'],
            auto_delete=options['auto_delete'],
            arguments=arguments,
        )

        # For fanout exchanges, use empty routing key for binding
        # Otherwise use queue name as routing key
        if self._exchange_options.get('type') == 'fanout':
            binding_key = ''
        else:
            binding_key = queue_name
            
        self._channel.queue_bind(
            exchange=self._exchange,
            queue=queue_name,
            routing_key=binding_key,
        )

    def _declare_exchange(self):
        self._channel.exchange_declare(
            exchange=self._exchange,
            exchange_type=self._exchange_options['type'],
            durable=self._exchange_options['durable'],
            auto_delete=self._exchange_options['auto_delete'],
        )

    def _get_channel(self, prefetch=None):
        if prefetch is None:
            prefetch = self._prefetch

        ssl_options = None
        if self._tls:
            ssl_options = pika.SSLOptions(ssl.SSLContext())

        # Pika's connection is not thread-safe, can't be reused.
        # Thus, neither the channels belonging to it.
        connection = pika.BlockingConnection(
            pika.ConnectionParameters(
                host=self._host,
                port=self._port,
                virtual_host=self._vhost,
                credentials=pika.PlainCredentials(
                    self._user,
                    self._password,
                ),
                ssl_options=ssl_options,
            )
        )

        channel = connection.channel()
        channel.confirm_delivery()
        channel.basic_qos(prefetch_count=prefetch)

        return channel

    @staticmethod
    def _close_channel(channel):
        try:
            connection = channel._connection
            channel.close()
        except Exception:
            pass
        try:
            connection.close()
        except Exception:
            pass
