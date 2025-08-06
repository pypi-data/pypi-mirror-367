import random
import uuid
from pika import BasicProperties
from pika import DeliveryMode
from threading import Lock
from .logger import logger
from .utils import (
    get_partition_queue_name,
    serialize_content,
    get_backup_queue_name,
)
from .rabbit_store import RabbitStore


class Producer(RabbitStore):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._producer_lock = Lock()  # Make produce() thread-safe

    @RabbitStore.reconnect
    def produce(
        self,
        queue,
        content,
        correlation_id=None,
        message_id=None,
        queue_options=None,
    ):
        if queue_options is None:
            queue_options = {}
        queue_options = self._queue_options | queue_options

        if queue not in self._declared_logical_queues:
            self.declare_queue(
                queue,
                options=queue_options,
            )

        if message_id is None:
            message_id = str(uuid.uuid4())

        # Uniform distribution of messages across the queue partitions
        partition = random.randint(0, self._partitions - 1)
        partition_queue = get_partition_queue_name(queue, partition)

        queue_names = [partition_queue]
        if queue_options['backup']:
            backup_queue = get_backup_queue_name(queue, partition)
            queue_names.append(backup_queue)

        properties = BasicProperties(
            message_id=message_id,
            correlation_id=correlation_id,
            delivery_mode=DeliveryMode.Transient  # Delivery confirmation
        )

        serialized_content = serialize_content(content)

        logger.debug(
            'Producing message... ',
            exchange=self._exchange,
            queue=partition_queue,
        )

        with self._producer_lock:
            for queue_name in queue_names:
                # For fanout exchanges, use empty routing key
                # Otherwise use queue name as routing key
                if self._exchange_options.get('type') == 'fanout':
                    routing_key = ''
                else:
                    routing_key = queue_name
                    
                self._channel.basic_publish(
                    exchange=self._exchange,
                    routing_key=routing_key,
                    body=serialized_content,
                    properties=properties,
                    mandatory=True
                )

        logger.debug(
            'Message published.',
            exchange=self._exchange,
            queue=partition_queue,
        )
