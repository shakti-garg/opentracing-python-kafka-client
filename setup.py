import os

from setuptools import setup, find_packages

work_dir = os.path.dirname(os.path.realpath(__file__))

setup(name='opentracing-python-kafka-client',
      version='1.2',
      description='OpenTracing Instrumentation for Confluent-Kafka-Python library',
      url='https://github.com/shakti-garg/opentracing-python-kafka-client.git',
      author='Shakti Garg',
      author_email='shakti.garg@gmail.com',
      license='Apache License Version 2.0',
      packages=find_packages(exclude=("test", "test.*")),
      install_requires=['confluent-kafka'],
      zip_safe=False)
