# -*- coding: utf-8 -*-
"""
Created on 2016-09-18

@author: Cheng Shangguan
"""
import sys
from time import time, sleep
from threading import Thread
import simplejson
import msgpack
from kafka import KafkaConsumer, TopicPartition
import zmq
from zmq import Again
from logger import logger
from event_util import BatchCopy

run_sink = True
paused = False


def start_acceptor(context, controller_port):
    global run_sink, paused
    node = context.socket(zmq.SUB)
    endpoint = "tcp://*:%d" % controller_port if sys.platform == "win32" else "ipc://controller.ipc"
    node.connect(endpoint)
    node.setsockopt(zmq.SUBSCRIBE, '')
    while run_sink:
        try:
            cmd = node.recv_string(zmq.NOBLOCK)
        except Again:
            sleep(1)
            continue
        if cmd == "stop" or cmd == "restart":
            run_sink = False
            node.close()
            context.term()
        if cmd == "pause" and not paused:
            paused = True
        if cmd == "resume" and paused:
            paused = False


def start_worker(brokers, topic, group, partition, pipeline_conf, dw_conf, redis_conf, logger):
    global run_sink, paused

    def init_consumer():
        c = KafkaConsumer(
            bootstrap_servers=brokers,
            group_id=group,
            value_deserializer=msgpack.unpackb,
            enable_auto_commit=False
        )
        t_p = TopicPartition(topic, partition)
        c.assign([t_p])
        return c, t_p

    consumer, topic_partition = init_consumer()
    batch_count = pipeline_conf.get("batch_count")
    event_path = pipeline_conf.get("event_path")
    pipeline = BatchCopy(dw_conf, event_path, partition, pipeline_conf.get("tables"), redis_conf, logger, '\x02')
    delay = time()
    count = 0

    while run_sink:
        if paused:
            consumer.pause(topic_partition)
        if consumer.paused() and not paused:
            consumer.resume(topic_partition)
        offset = consumer.position(topic_partition)
        consumer.commit_async()
        records = consumer.poll(1500)
        if records == {}:
            if time() - delay > pipeline_conf.get("interval") and count > 0:
                pipeline.copy_sink()
                count = 0
                delay = time()
            consumer, topic_partition = init_consumer()
            continue
        # offset = consumer.position(topic_partition)
        # consumer.seek(topic_partition, offset)
        pipeline.writelines(records[topic_partition])
        count += len(records[topic_partition])
        if count < batch_count and time() - delay < pipeline_conf.get("interval"):
            continue
        pipeline.copy_sink()
        count = 0
        delay = time()
    consumer.close()
    pipeline.close()


def run_worker():
    partition = int(sys.argv[1])
    config = simplejson.load(open("event.json", 'r'))
    kafka_conf = config.get("kafka")
    brokers = kafka_conf.get("brokers")
    topic = kafka_conf.get("topic")
    group = kafka_conf.get("group")
    pipeline_conf = config.get("pipeline")
    dw_conf = config.get("dw")
    pub_port = config.get('controller').get('pub_port')
    redis_conf = config.get('redis')

    context = zmq.Context()

    worker = Thread(target=start_worker,
                    args=(brokers, topic, group, partition, pipeline_conf, dw_conf, redis_conf, logger))
    worker.start()
    acceptor = Thread(target=start_acceptor, args=(context, pub_port))
    acceptor.start()


run_worker()
