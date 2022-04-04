import unittest
import logging
import json

from opentracing.mocktracer import MockTracer
from opentracing.mocktracer.text_propagator import field_name_span_id, field_name_trace_id

from opentracing_kafka.tracing_kafka_consumer import TracingKafkaConsumer
from test.mock_message import MockMessage

from mock import patch

logging.getLogger('').handlers = []
logging.basicConfig(level='DEBUG',
                    format='%(asctime)s - [%(filename)10s:%(lineno)s  - %(funcName)10s() ] - %(levelname)s - %(message)s ')


tracer = MockTracer()
kc = TracingKafkaConsumer({'group.id': 'cg-1'}, tracer)


def mock_consumer_poll(consumer=None, timeout=None):
    return MockMessage(key='key', value='value',
                        headers=[(field_name_trace_id, b'1'), (field_name_span_id, b'101'),
                                  ('key1', b'val1')],
                        topic='topic', partition=0, offset=23)

def mock_consumer_poll_none(consumer=None, timeout=None):
    return None


class TestTracingKafkaConsumer(unittest.TestCase):

    @patch('opentracing_kafka.tracing_kafka_consumer.poll', side_effect=mock_consumer_poll)
    def test_should_build_and_finish_child_span_for_one_polled_message(self, mock_consumer_poll_obj):
        msg = kc.poll(1)

        logging.debug('Output Msg: ' + json.dumps(msg.__dict__))

        assert msg.headers() == [(field_name_trace_id, format(1, 'x')), (field_name_span_id, format(1, 'x')),
                                         ('key1', 'val1')]
        assert msg.key() == 'key'
        assert msg.value() == 'value'

        assert msg.topic() == 'topic'
        assert msg.partition() == 0
        assert msg.offset() == 23

    @patch('opentracing_kafka.tracing_kafka_consumer.poll', side_effect=mock_consumer_poll_none)
    def test_should_not_build_and_finish_child_span_for_None_Message(self, mock_consumer_poll_obj):
        msg = kc.poll(1)

        assert msg is None

if __name__ == '__main__':
    unittest.main()
