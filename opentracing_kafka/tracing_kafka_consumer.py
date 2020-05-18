from confluent_kafka.cimpl import Consumer
from opentracing import Format, tags, follows_from

from opentracing_kafka.utils import merge_two_dicts


def default_span_name_provider(msg):
    return "From_" + msg.topic()


def consumer_span_tags_provider(msg):
    return {
        tags.SPAN_KIND: tags.SPAN_KIND_CONSUMER,
        tags.COMPONENT: 'python-kafka',
        tags.PEER_SERVICE: 'kafka',
        tags.MESSAGE_BUS_DESTINATION: msg.topic(),
        'partition': msg.partition(),
        'offset': msg.offset()
    }


class TracingKafkaConsumer(Consumer):

    def __init__(self, config, tracer, span_name_provider=default_span_name_provider, span_tags_providers=[]):
        """
        constructor method

        :param config: dictionary of configurations for kafka producer
        :param tracer: instance of tracer-client
        :param span_name_provider: [optional] function returning span-name
        sample function def::
            def func(msg):
                return ''

        :param span_tags_providers: [optional] list of functions where each function returns dictionary of tags
        sample function def::
            def func(msg):
                return {}
        """
        super().__init__(config)

        self.tracer = tracer
        self.span_name_provider = span_name_provider
        self.span_tags_providers = span_tags_providers

    def poll(self, timeout=None):
        """
        overridden method

        :param timeout:
        :return:
        """
        msg = Consumer.poll(self, timeout)

        if msg is not None:
            self.build_and_finish_child_span(msg)

        return msg

    def consume(self, num_messages=1, *args, **kwargs):
        """
        overridden method

        :param num_messages:
        :param args:
        :param kwargs:
        :return:
        """
        msgs = Consumer.consume(self, num_messages, *args, **kwargs)

        for msg in msgs:
            if msg is not None:
                self.build_and_finish_child_span(msg)

        return msgs

    def build_and_finish_child_span(self, msg):
        msg_header_text_dict = dict((key, binary_value.decode("utf-8")) for key, binary_value in msg.headers())

        parent_context = self.tracer.extract(Format.TEXT_MAP, msg_header_text_dict)

        user_tags = {}
        for span_tag_provider in self.span_tags_providers:
            user_tags = merge_two_dicts(user_tags, span_tag_provider(msg))

        span = self.tracer.start_span(self.span_name_provider(msg), references=[follows_from(parent_context)],
                                      tags=merge_two_dicts(consumer_span_tags_provider(msg), user_tags))
        span.finish()

        # Inject created span context into message header for extraction by client to continue span chain
        self.tracer.inject(span.context, Format.TEXT_MAP, msg_header_text_dict)
        msg.set_headers(list(msg_header_text_dict.items()))
