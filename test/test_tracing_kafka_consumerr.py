import unittest

from opentracing.mocktracer import MockTracer
from opentracing.mocktracer.text_propagator import field_name_span_id, field_name_trace_id

from opentracing_kafka.tracing_kafka_consumer import TracingKafkaConsumer
from test.mock_message import MockMessage

tracer = MockTracer()
kc = TracingKafkaConsumer({'group.id': 'cg-1'}, tracer)


class TestTracingKafkaConsumer(unittest.TestCase):
    def test_should_build_and_finish_child_span(self):
        msg = MockMessage(key='key', value='value',
                          headers=[(field_name_trace_id, b'1'), (field_name_span_id, b'101'),
                                   ('key1', b'val1')],
                          topic='topic', partition=0, offset=23)

        kc.build_and_finish_child_span(msg)

        assert msg.headers() == [(field_name_trace_id, format(1, 'x')), (field_name_span_id, format(1, 'x')),
                                 ('key1', 'val1')]
        assert msg.key() == 'key'
        assert msg.value() == 'value'

        assert msg.topic() == 'topic'
        assert msg.partition() == 0
        assert msg.offset() == 23


if __name__ == '__main__':
    unittest.main()
