# -*- coding: utf-8 -*-
"""
Created on 2016-09-08

@author: Cheng Shangguan
"""
import sys
import zmq
import simplejson
import subprocess


def execute_command():
    if len(sys.argv) != 2:
        return
    config = simplejson.load(open("event.json", 'r'))
    if sys.argv[1] == "start":
        cmd = '%s %s' % (sys.executable, "event_controller.py")
        subprocess.Popen(cmd, shell=True)
        partitions = config.get('kafka').get('partitions')
        for i in range(0, partitions):
            cmd = '%s %s %d' % (sys.executable, "event_pipeline.py", i)
            subprocess.Popen(cmd, shell=True)
    else:
        cmd_port = config.get('controller').get('cmd_port')
        context = zmq.Context()
        req = context.socket(zmq.REQ)
        endpoint = "tcp://localhost:%d" % cmd_port if sys.platform == "win32" else "ipc://cmd.ipc"
        req.connect(endpoint)
        req.send_string(sys.argv[1])
        print(req.recv_string())
        req.close()
        context.term()

execute_command()
