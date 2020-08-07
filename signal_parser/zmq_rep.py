import time
import zmq
import json
from datetime import datetime

from signal_parser import parser
from signal_parser import mt4_date_converter

#def mt4_date_converter(o):
#    if isinstance(o, datetime):
#        return o.strftime("%Y.%m.%d %H:%M")

from threading import Thread

class ZMQ_Rep(Thread):

    def __init__(self):
        Thread.__init__(self)
        self.daemon = True

        #  -- create
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.REP)
        self.socket.bind("tcp://*:10001")
        self.start()

    def stop_and_die():
        self.bound = False
        self.unbind("tcp://*:10001")
        self.terminate()
        self.join()

    def run(self):
        while self.bound:
            print("OK")

            #  Wait for next request from client
            message = socket.recv()
            print("Received request: %s" % message)
            
            result = parser.parseSignal(message.decode('utf-8'))
            if not result:
                result = json.dumps({"ok": False, "res": result}, default = mt4_date_converter)
            else:
                result = json.dumps({"ok": True, "res": result.canonical()}, default = mt4_date_converter)

            print("Sent response: %s" % result)
            socket.send_string(result)

# -- Usage:
# rep = ZMQ_Rep() # -- zmq rep parser will be bound in port 10001

