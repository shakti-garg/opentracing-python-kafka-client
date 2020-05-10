import traceback

from confluent_kafka.cimpl import Producer
from opentracing import tags, Format


def error_logs(err) :
    error_logs['event'] = tags.ERROR
    error_logs['error.kind'] = err.__name__
    error_logs['error.object'] = err
    error_logs['error.message'] = str(err)

    error_logs['error.stack'] = traceback.print_tb(err.__traceback__)

    return error_logs;


# curried callback function to wrap original 'on_delivery' callback
def create_tracing_delivery_callback(self, on_delivery_fn, span):
    def tracing_delivery_callback(err, msg):
        if err is not None:
            span.set_tag('error', 'true')
            span.log_kv(error_logs(err))

        if on_delivery_fn is not None:
            on_delivery_fn(err, msg)

        span.finish()

    return tracing_delivery_callback


class TracingKafkaProducer(Producer):

    def __init__(self, config, tracer):
        super().__init__(config)
        self.tracer = tracer

    def produce(self, topic, value=None, *args, **kwargs):
        if kwargs['headers'] is None:
            raise RuntimeError('message headers must be passed as parameters, ex: "headers = <>"')

        parent_context = self.tracer.extract(Format.TEXT_MAP, dict(kwargs['headers']))
        producer_oper = "To_" + topic
        producer_tags = {tags.SPAN_KIND: tags.SPAN_KIND_PRODUCER,
                         tags.COMPONENT: 'python-kafka', tags.PEER_SERVICE: 'kafka',
                         tags.MESSAGE_BUS_DESTINATION: topic
                         }

        span = self.tracer.start_span(producer_oper, child_of=parent_context, tags=producer_tags)

        # Inject created span context into message header for sending to kafka queue
        msg_header_dict = dict(kwargs['headers'])
        self.tracer.inject(span.context, Format.TEXT_MAP, msg_header_dict)
        kwargs['headers'] = list(msg_header_dict.items())

        kwargs['on_delivery'] = create_tracing_delivery_callback(kwargs['on_delivery'], span)

        Producer.produce(self, topic, value, args, kwargs)
