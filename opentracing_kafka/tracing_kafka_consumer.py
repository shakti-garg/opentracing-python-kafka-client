from confluent_kafka.cimpl import Consumer
from opentracing import Format, tags


class TracingKafkaConsumer(Consumer):

    def __init__(self, config, tracer):
        super().__init__(config)
        self.tracer = tracer

    def poll(self, timeout=None):
        msg = Consumer.poll(self, timeout)

        if msg is not None:
            self.build_and_finish_child_span(msg)

        return msg

    def consume(self, num_messages=1, *args, **kwargs):
        msgs = Consumer.consume(self, num_messages, args, kwargs)

        for msg in msgs:
            if msg is not None:
                self.build_and_finish_child_span(msg)

        return msgs

    def build_and_finish_child_span(self, msg):
        parent_context = self.tracer.extract(Format.TEXT_MAP, dict(msg.headers()))
        consumer_oper = "From_" + msg.topic()
        consumer_tags = {tags.SPAN_KIND: tags.SPAN_KIND_CONSUMER,
                         tags.COMPONENT: 'python-kafka', tags.PEER_SERVICE: 'kafka',
                         tags.MESSAGE_BUS_DESTINATION: msg.topic(),
                         'partition': msg.partition(), 'offset': msg.offset()
                         }

        span = self.tracer.start_span(consumer_oper, child_of=parent_context, tags=consumer_tags)
        span.finish()

        # Inject created span context into message header for extraction by client to continue span chain
        msg_header_dict = dict(msg.headers())
        self.tracer.inject(span.context, Format.TEXT_MAP, msg_header_dict)
        msg.set_headers(list(msg_header_dict.items()))