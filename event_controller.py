# -*- coding: utf-8 -*-
"""
Created on 2016-09-08

@author: Cheng Shangguan
"""
import sys
import os
from time import sleep
import simplejson
import zmq
from zmq import Again


def stop_event_cluster(controller):
    controller.send_string("stop")
    controller.close()


def restart_event_cluster(controller, partitions):
    controller.send_string("restart")
    sleep(10)


def pause_event_cluster(controller):
    controller.send_string("pause")


def resume_event_cluster(controller):
    controller.send_string("resume")


def run_controller():
    config = simplejson.load(open("event.json", 'r'))
    cmd_port = config.get('controller').get('cmd_port')
    pub_port = config.get('controller').get('pub_port')
    partitions = config.get('kafka').get('partitions')

    context = zmq.Context()
    cmd = context.socket(zmq.REP)
    endpoint = "tcp://*:%d" % cmd_port if sys.platform == "win32" else "ipc://cmd.ipc"
    cmd.bind(endpoint)
    controller = context.socket(zmq.PUB)
    endpoint = "tcp://*:%d" % pub_port if sys.platform == "win32" else "ipc://controller.ipc"
    controller.bind(endpoint)

    running = True
    while running:
        try:
            msg = cmd.recv_string(zmq.NOBLOCK)
        except Again:
            sleep(1)
            continue
        if msg == "stop":
            stop_event_cluster(controller)
            cmd.send_string("Event cluster has been stopped.")
            cmd.close()
            context.term()
            running = False
        if msg == "restart":
            restart_event_cluster(controller, partitions)
            cmd.send_string("Event cluster has been restarted.")
        if msg == "pause":
            pause_event_cluster(controller)
            cmd.send_string("Event cluster has been paused.")
        if msg == "resume":
            pause_event_cluster(controller)
            cmd.send_string("Event cluster has been resumed.")

run_controller()
