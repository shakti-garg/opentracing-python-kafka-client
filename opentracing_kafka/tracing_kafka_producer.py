import traceback

from confluent_kafka.cimpl import Producer
from opentracing import tags, Format, follows_from

from opentracing_kafka.utils import merge_two_dicts


def default_span_name_provider(topic, key, value):
    return "To_" + topic


def producer_span_tags_provider(topic):
    return {
        tags.SPAN_KIND: tags.SPAN_KIND_PRODUCER,
        tags.COMPONENT: 'python-kafka',
        tags.PEER_SERVICE: 'kafka',
        tags.MESSAGE_BUS_DESTINATION: topic
    }


def error_logs(err):
    return {
        'event': tags.ERROR,
        'error.kind': err.__class__,
        'error.object': err,
        'error.message': str(err),
        'error.stack': traceback.extract_tb(err.__traceback__)
    }


# curried callback function to wrap original 'on_delivery' callback
def create_tracing_delivery_callback(on_delivery_fn, span):
    def tracing_delivery_callback(err, msg):
        if err is not None:
            span.set_tag('error', 'true')
            span.log_kv(error_logs(err))

        if msg is not None:
            span.set_tag('partition', msg.partition())
            span.set_tag('offset', msg.offset())

        if on_delivery_fn is not None:
            on_delivery_fn(err, msg)

        span.finish()

    return tracing_delivery_callback


class TracingKafkaProducer(Producer):

    def __init__(self, config, tracer, span_name_provider=default_span_name_provider, span_tags_providers=[]):
        """
        constructor method

        :param config: dictionary of configurations for kafka producer
        :param tracer: instance of tracer-client
        :param span_name_provider: [optional] function returning span-name
        sample function def::
            def func(topic, key, value):
                return ''

        :param span_tags_providers: [optional] list of functions where each function returns dictionary of tags
        sample function def::
            def func(topic, key, value):
                return {}
        """
        super().__init__(config)

        self.tracer = tracer
        self.span_name_provider = span_name_provider
        self.span_tags_providers = span_tags_providers

    def produce(self, topic, value=None, *args, **kwargs):
        """
        overridden method

        :param topic:
        :param value:
        :param args:
        :param kwargs:
        :return:
        """
        msg_header_dict = dict() if kwargs.get('headers') is None else dict(kwargs.get('headers'))

        parent_context = self.tracer.extract(Format.TEXT_MAP, msg_header_dict)

        user_tags = {}
        for span_tag_provider in self.span_tags_providers:
            user_tags = merge_two_dicts(user_tags, span_tag_provider(topic, kwargs.get('key'), value))

        span = self.tracer.start_span(self.span_name_provider(topic, kwargs.get('key'), value),
                                      references=[follows_from(parent_context)],
                                      tags=merge_two_dicts(producer_span_tags_provider(topic), user_tags))

        # Inject created span context into message header for sending to kafka queue
        self.tracer.inject(span.context, Format.TEXT_MAP, msg_header_dict)
        kwargs['headers'] = list(msg_header_dict.items())

        kwargs['on_delivery'] = create_tracing_delivery_callback(kwargs['on_delivery'], span)

        Producer.produce(self, topic, value, *args, **kwargs)
