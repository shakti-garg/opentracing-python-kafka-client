from confluent_kafka.cimpl import Consumer


class TracingKafkaConsumer(Consumer):

    def __init__(self, config, tracer):
        super().__init__(config)
        self.tracer = tracer

    def poll(self, timeout=None):
        with self.tracer.start_span('ConsumerSpan') as span:
            Consumer.poll(self, timeout)
