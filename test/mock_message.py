from confluent_kafka.cimpl import KafkaError


class MockMessage:
    """
    The Mock object of Message which represents either a single consumed or produced message, or an event (:py:func:`error()` is not None).
    """

    def __init__(self, headers=[], key=None, value=None, error=None, topic=None, partition=None,
                 offset=None, timestamp=None):
        self._headers = headers
        self._key = key
        self._value = value

        self._error = error

        self._topic = topic
        self._partition = partition
        self._offset = offset
        self._timestamp = timestamp

    def add_header(self, key, value):
        self._headers.append((key, value))

    def set_headers(self, headers):
        self._headers = headers

    def set_key(self, key):
        self._key = key

    def set_value(self, value):
        self._value = value

    def set_value(self, error):
        if TypeError(error) is KafkaError:
            self._error = error

    def error(self):
        return self._error

    def headers(self):
        return self._headers

    def key(self):
        return self._key

    def value(self):
        return self._value

    def topic(self):
        return self._topic

    def partition(self):
        return self._partition

    def offset(self):
        return self._offset

    def timestamp(self):
        return self._timestamp



