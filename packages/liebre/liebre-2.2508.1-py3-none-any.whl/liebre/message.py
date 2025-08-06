from .utils import deserialize_content


class Message:

    def __init__(
        self,
        content,
        properties,
        method,
        queue,
    ):
        self.content = deserialize_content(content)
        self.raw_content = content
        self.properties = properties
        self.method = method
        self.queue = queue

    @property
    def id(self):
        return self.properties.message_id

    @property
    def uid(self):
        return (self.id, self.queue)
