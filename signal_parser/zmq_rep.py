import time
import json
import logging
logging.basicConfig(filename='zmq_rep.log',level=logging.INFO)

from datetime import datetime

import signal_parser.parser as parser
from signal_parser import mt4_date_converter

from threading import Thread

import zmq

class ZMQ_Rep(Thread):

    def __init__(self):
        Thread.__init__(self)
        self.daemon = True
        #  -- create
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.REP)
        self.socket.bind("tcp://*:10001")
        logging.info("BOUND")
        self.bound = True
        self.start()        

    def stop_and_die():
        self.bound = False
        self.unbind("tcp://*:10001")
        self.terminate()
        self.join()

    def run(self):
        while self.bound:
            #  Wait for next request from client
            message = self.socket.recv()
            logging.info("Received request: %s" % message)
            
            result = parser.parseSignal(message.decode('utf-8'))
            if not result:
                result = json.dumps({"ok": False, "res": result}, default = mt4_date_converter)
            else:
                result = json.dumps({"ok": True, "res": result.canonical()}, default = mt4_date_converter)

            logging.info("Sent response: %s" % result)
            self.socket.send_string(result)

# -- Usage:
if __name__ == '__main__':
    rep = ZMQ_Rep() # -- zmq rep parser will be bound in port 10001
    rep.run()

