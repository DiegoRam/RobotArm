import socket,configparser, logging, sys, getopt, thread
from time import sleep
import tornado
import tornado.websocket
import tornado.httpserver
from websocket import WebSocketApp, create_connection


config = configparser.ConfigParser()
config.read('./conf/application.cfg')
env = config.get("system","env")

log = logging.getLogger("Arm")
logger_level = config.get("system","logging.level")

log.setLevel(logging.DEBUG)

MODE = "server"

handler = logging.StreamHandler()
file_handler = logging.FileHandler('/var/tmp/socket_server.log')
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)
if env == 'pi':
	file_handler.setFormatter(formatter)
	log.addHandler(file_handler)
log.addHandler(handler)

if env == 'pi':
	from gpiozero import AngularServo
elif env == 'mac':
    pass

class Arm(object):
    def __init__(self, pinsTuple):
        self._pin1, self._pin2, self._pin3, self._pin4 = pinsTuple
        log.debug("ARM mode: " + env)
        if env == 'pi':
            self._servo_base = AngularServo(self._pin1, min_angle=-100, max_angle = 100)
            self._servo_arm1 = AngularServo(self._pin2, min_angle=-100, max_angle = 100)
            self._servo_arm2 = AngularServo(self._pin3, min_angle=-100, max_angle = 100)
            self._servo_claw = AngularServo(self._pin4, min_angle=-100, max_angle = 100)

    def center(self):
        if env == 'pi':
            self._servo_base.mid()
            self._servo_arm1.mid()
            self._servo_arm2.mid()
            self._servo_claw.mid()
            sleep(0.2)
            self._servo_base.detach()
            self._servo_arm1.detach()
            self._servo_arm2.detach()
            self._servo_claw.detach()

    def claw_pos(self, angle):
        if env == 'pi':
            self._servo_claw.angle(angle)
            sleep(0.2)
            self._servo_claw.detach()
        log.debug("Claw servo moved to: " + str(angle))

    def base_pos(self, angle):
        if env == 'pi':
            self._servo_base.angle = angle
            sleep(0.2)
            self._servo_base.detach()
        log.debug("Base servo moved to: " + str(angle))

    def arm1_pos(self, angle):
        if env == 'pi':
            self._servo_arm1.angle = angle
            sleep(0.2)
            self._servo_arm1.detach()
        log.debug("Arm1 servo moved to: " + str(angle))

    def arm2_pos(self, angle):
        if env == 'pi':
            self._servo_arm2.angle = angle
            sleep(0.2)
            self._servo_arm2.detach()
        log.debug("Arm2 servo moved to: " + str(angle))


class EchoWebSocket(tornado.websocket.WebSocketHandler):
    ARM = Arm((17,11,10,9))
    def open(self):
        log.debug("WebSocket opened")

    def on_message(self, message):
		self.write_message(u"You said: " + message)
		log.debug(u"You said: " + message)
		#TODO logic about servo motors
		h, v = message.split(',')
		self.ARM.base_pos(int(v))
		#self.ARM.arm1_pos(int(v))

    def on_close(self):
        log.debug("WebSocket closed")

class Client(object):
    def __init__(self, host = "", port = 9005):
		self._host = host
		self._port = port
		log.debug("Establishing connection...")
		##self.ws = WebSocketApp("ws://192.168.1.67:9005/robotarm", on_close = on_close, on_message = on_message)
		self.ws = create_connection("ws://192.168.1.67:9005/robotarm")
		log.debug("Connection established...")
		#self.ws.on_open = on_open


    def readCamera(self):
        '''
        Simple logic to read from camera and send command to handle servo motors
        '''
        pass

    def send(self, message):
        log.debug("Sending message: " + message)
        self.ws.send(message)

def on_message(ws, message):
    log.debug("Received from server: " + message)

def on_close(ws):
    log.debug("Client closed...")

def on_open(ws):
	log.debug('Client working....')
	'''
	def run(*args):
        while True:
            data = raw_input("Enter angle: ")
            ws.send(data)
    thread.start_new_thread(run,())
	'''


def main(argv):
    try:
        opts, args = getopt.getopt(argv,"hm:",["mode="])
    except getopt.GetoptError:
        print 'comm.py -m <mode>'
        sys.exit(2)

    for opt, arg in opts:
        if opt == '-h':
            print 'comm.py -m <mode> #prod-dev'
            sys.exit()
        elif opt in ("-m", "--mode"):
            MODE = arg

    log.debug("Mode: " + MODE)
    if MODE == "server":
        app = tornado.web.Application(
            handlers=[
                (r"/robotarm",EchoWebSocket),
            ],
            debug=True
	)
	http_server = tornado.httpserver.HTTPServer(app)
	http_server.listen(9005)
	tornado.ioloop.IOLoop.instance().start()

    elif MODE == "client":
        client = Client()
        client.ws.run_forever()

if __name__ == "__main__":
    main(sys.argv[1:])
