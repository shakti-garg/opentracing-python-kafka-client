from confluent_kafka.cimpl import Producer


class TracingKafkaProducer(Producer):

    def __init__(self, config, tracer):
        super().__init__(config)
        self.tracer = tracer

    def produce(self, topic, value=None, *args, **kwargs):
        with self.tracer.start_span('ProducerSpan') as span:
            span.log_kv({'event': 'produce message', 'life': 42})
            Producer.produce(self, topic, value, *args, **kwargs)
