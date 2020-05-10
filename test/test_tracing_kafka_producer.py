import unittest

from opentracing.mocktracer import MockTracer

from opentracing_kafka.tracing_kafka_producer import TracingKafkaProducer, error_logs

tracer = MockTracer()
kp = TracingKafkaProducer({}, tracer)


class TestTracingKafkaProducer(unittest.TestCase):
    def test_error_logs(self):
        try:
            raise RuntimeError('Error is raised')
        except RuntimeError as err:
            error_logs_dict = error_logs(err)
            print(error_logs_dict)


if __name__ == '__main__':
    unittest.main()
