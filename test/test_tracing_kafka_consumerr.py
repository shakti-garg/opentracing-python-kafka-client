import unittest
import logging
import json

from opentracing.mocktracer import MockTracer
from opentracing.mocktracer.text_propagator import field_name_span_id, field_name_trace_id

from opentracing_kafka.tracing_kafka_consumer import TracingKafkaConsumer
from test.mock_message import MockMessage

from mock import patch, MagicMock

logging.getLogger('').handlers = []
logging.basicConfig(level='DEBUG',
                    format='%(asctime)s - [%(filename)10s:%(lineno)s  - %(funcName)10s() ] - %(levelname)s - %(message)s ')


tracer = MockTracer()
kc = TracingKafkaConsumer({'group.id': 'cg-1'}, tracer)


mock_poll_msg = MockMessage(key='key', value='value',
                        headers=[(field_name_trace_id, b'1'), (field_name_span_id, b'101'),
                                  ('key1', b'val1')],
                        topic='topic', partition=0, offset=23)

mock_consume_msgs = [
            MockMessage(key='key1', value='value1',
                        headers=[(field_name_trace_id, b'1'), (field_name_span_id, b'101'),
                                  ('key1', b'val1')],
                        topic='topic1', partition=1, offset=11),
            MockMessage(key='key2', value='value2',
                        headers=[(field_name_trace_id, b'2'), (field_name_span_id, b'201'),
                                  ('key2', b'val2')],
                        topic='topic2', partition=2, offset=22)
            ]



class TestTracingKafkaConsumer(unittest.TestCase):

    @patch.object(TracingKafkaConsumer, '_TracingKafkaConsumer__poll_msg')
    def a_test_should_build_and_finish_child_span_for_one_polled_message(self, poll_msg_mock: MagicMock):
        poll_msg_mock.return_value = mock_poll_msg

        msg = kc.poll(1)
        logging.debug('Output Msg: ' + json.dumps(msg.__dict__))

        assert msg.headers() == [(field_name_trace_id, format(1, 'x')), (field_name_span_id, format(1, 'x')),
                                         ('key1', 'val1')]
        assert msg.key() == 'key'
        assert msg.value() == 'value'

        assert msg.topic() == 'topic'
        assert msg.partition() == 0
        assert msg.offset() == 23

    @patch.object(TracingKafkaConsumer, '_TracingKafkaConsumer__poll_msg')
    def b_test_should_not_build_and_finish_child_span_for_none_polled_message(self, poll_msg_mock: MagicMock):
        poll_msg_mock.return_value = None

        msg = kc.poll(1)

        assert msg is None

    @patch.object(TracingKafkaConsumer, '_TracingKafkaConsumer__consume_msgs')
    def c_test_should_build_and_finish_child_span_for_multiple_consumed_message(self, consume_msgs_mock: MagicMock):
        consume_msgs_mock.return_value = mock_consume_msgs

        msgs = kc.consume(2)

        i=1
        for msg in msgs:
            logging.debug('Output Msg: ' + json.dumps(msg.__dict__))

            assert msg.headers() == [(field_name_trace_id, format(i, 'x')), (field_name_span_id, format(i, 'x')),
                                             ('key'+str(i), 'val'+str(i))]
            assert msg.key() == 'key'+str(i)
            assert msg.value() == 'value'+str(i)

            assert msg.topic() == 'topic'+str(i)
            assert msg.partition() == i
            assert msg.offset() == i*11

            i=i+1

    @patch.object(TracingKafkaConsumer, '_TracingKafkaConsumer__consume_msgs')
    def d_test_should_not_build_and_finish_child_span_for_none_consumed_message(self, consume_msgs_mock: MagicMock):
        consume_msgs_mock.return_value = None

        msgs = kc.consume(2)

        assert len(msgs) == 0

if __name__ == '__main__':
    unittest.main()
