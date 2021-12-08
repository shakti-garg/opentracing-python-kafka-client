![License](https://img.shields.io/github/license/shakti-garg/opentracing-python-kafka-client)
![Open Issues](https://img.shields.io/github/issues-raw/shakti-garg/opentracing-python-kafka-client)
![Open PRs](https://img.shields.io/github/issues-pr-raw/shakti-garg/opentracing-python-kafka-client)
![Contributors](https://img.shields.io/github/contributors/shakti-garg/opentracing-python-kafka-client)

![Build Status](https://img.shields.io/circleci/build/github/shakti-garg/opentracing-python-kafka-client/master)
![Version](https://img.shields.io/pypi/v/opentracing-python-kafka-client)
![Downloads](https://img.shields.io/pypi/dm/opentracing-python-kafka-client)

# opentracing-python-kafka-client
OpenTracing Instrumentation library for Confluent-Kafka-Python applications.

This library provides wrapper implementations over confluent-kafka's consumer and producer interfaces with below features:
- retain the default confluent-kafka producer/consumer functionality and API
- provide capability to create tracing spans whenever a message is produced/consumed
  - default span name for producer is "To_<topic_name>" and for consumer is "From_<topic_name>". It can be overridden from constructor by passing a custom function with kafka message as parameter.
- inject created span context into kafka message header for extraction by another kafka client to continue span chain

## Releases
This python package is released at PyPi: https://pypi.org/project/opentracing-python-kafka-client/.

Release is automated using git-webhook which triggers build and deployment at CircleCI pipeline: https://app.circleci.com/pipelines/github/shakti-garg/opentracing-python-kafka-client.

## Usage

1. Instantiate the relevant tracing kafka client with a opentracing-client instance. Then, use it like the default confluent kafka client.


For producing kafka message:

```pycon
from opentracing_kafka.tracing_kafka_producer import TracingKafkaProducer

conf = {'bootstrap.servers': brokers}
producer = TracingKafkaProducer(conf, tracer)
....
producer.produce(topic_name, key, value, on_delivery=delivery_cb)

```

For consuming kafka message:

```pycon
from opentracing_kafka.tracing_kafka_consumer import TracingKafkaConsumer

conf = {'bootstrap.servers': brokers, 
        'group.id': consumer_group_id}
consumer = TracingKafkaConsumer(conf, tracer)
....
msg = producer.poll(1.0)

```

2. instance `tracer` above is an opentracing-client instance which implements the open-tracing protocol like jaegar and datadog. The complete list of supporter tracer implementation is https://opentracing.io/docs/supported-tracers/

As Jaegar (by CNCF: https://www.jaegertracing.io/) is the most popular one, below is the snippet to create the jaegar tracer instance:
```pycon
from jaeger_client import Config

jaegar_config = {  # usually read from some yaml config
                  'sampler': {
                    'type': 'const',
                    'param': 1,
                  },
                  'logging': True,
                  'local_agent': {
                    'reporting_host': JAEGAR_AGENT_HOST,
                    'reporting_port': JAEGAR_AGENT_PORT
                  }
                }
                
config = Config(
            config=jaegar_config,
            service_name=service_name,
            validate=True,
        )
        
tracer = config.initialize_tracer()
```

## References:
1) What is OpenTracing Protocol: https://opentracing.io/docs/overview/
2) What is Distributed Tracing: https://opentracing.io/docs/overview/what-is-tracing/
3) Tracers Protocol: https://opentracing.io/docs/overview/tracers/
