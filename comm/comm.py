import socket,configparser, logging, sys, getopt
from time import sleep
import tornado
import tornado.websocket
import tornado.httpserver
from websocket import create_connection


config = configparser.ConfigParser()
config.read('../conf/application.cfg')
env = config.get("system","env")

log = logging.getLogger("RobotArm")
logger_level = config.get("system","logging.level")

log.setLevel(logging.DEBUG)

MODE = "server"

handler = logging.StreamHandler()
file_handler = logging.FileHandler('/var/tmp/socket_server.log')
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)
if env == 'prod':
	file_handler.setFormatter(formatter)
	log.addHandler(file_handler)
log.addHandler(handler)

if env == "prod":
	from gpiozero import AngularServo

class Arm(object):
    def __init__(self, pinsTuple):
        self._pin1, self._pin2, self._pin3, self._pin4 = pinsTuple
        self._servo_base = AngularServo(self._pin1, min_angle=-80, max_angle = 80)
        self._servo_arm1 = AngularServo(self._pin2, min_angle=-80, max_angle = 80)
        self._servo_arm2 = AngularServo(self._pin3, min_angle=-80, max_angle = 80)
        self._servo_claw = AngularServo(self._pin4, min_angle=-80, max_angle = 80)

    def center(self):
        if env == "prod":
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
        if env == "prod":
            self._servo_claw.angle(angle)
            sleep(0.2)
            self._servo_claw.detach()
        log.debug("Claw servo moved to: " + angle)

    def base_pos(self, angle):
        if env == "prod":
            self._servo_base.angle = angle
            sleep(0.2)
            self._servo_base.detach()
        log.debug("Base servo moved to: " + angle)

    def arm1_pos(self, angle):
        if env == "prod":
            self._servo_arm1.angle = angle
            sleep(0.2)
            self._servo_arm1.detach()
        log.debug("Arm1 servo moved to: " + angle)

    def arm2_pos(self, angle):
        if env == "prod":
            self._servo_arm2.angle = angle
            sleep(0.2)
            self._servo_arm2.detach()
        log.debug("Arm2 servo moved to: " + angle)


class EchoWebSocket(tornado.websocket.WebSocketHandler):
    ARM = Arm()
    def open(self):
        log.debug("WebSocket opened")

    def on_message(self, message):
        self.write_message(u"You said: " + message)
        log.debug(u"You said: " + message)
        #TODO logic about servo motors
        ARM.base_pos(message)

    def on_close(self):
        log.debug("WebSocket closed")

class Client(object):
    def __init__(self, host = "", port = 9005):
        self._host = host
        self._port = port
        log.debug("Establishing connection...")
        self._ws = create_connection("ws://localhost:9005/robotarm")
        log.debug("Connection established...")


    def readCamera(self):
        '''
        Simple logic to read from camera and send command to handle servo motors
        '''
        pass

    def send(self, message):
        log.debug("Sending message: " + message)
        self._ws.send(message)


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
        while True:
            data = raw_input("Insert angle :")
            client.send(data)

if __name__ == "__main__":
    main(sys.argv[1:])
