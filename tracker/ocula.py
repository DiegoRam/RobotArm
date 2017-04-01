import freenect, configparser, logging, utils
import cv2
import frame_convert2
from trackers import CircleTracker, BallTracker
from time import sleep
from comm.comm import Client

config = configparser.ConfigParser()
config.read('./conf/application.cfg')
env = config.get("system","env")

log = logging.getLogger("Ocula")
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

def mapValue(value, in_min, in_max, out_min, out_max):
	"""
	Returns a new value mapped in a desired range.

	Parameters:
	value: value to be mapped
	in_min - in_max: limits of the range where the value is
	out_min - out_max: limits of the range where the value will be mapped
	"""
	val = (value - in_min) * (out_max - out_min) / (in_max - in_min) + out_min
	if val > out_max:
		return out_max
	elif val < out_min:
		return out_min
	else:
		return val

class Ocula(object):
    def __init__(self, debug = True):
		self._window_depth = cv2.namedWindow('Depth')
		self._window_video = cv2.namedWindow('Video')
		self._circle_tracker = CircleTracker()
		self._ball_tracker = BallTracker()
		self._shouldDrawDebugRects = debug
		self.client = Client()
		#self.client.ws.run_forever()


    def _get_depth(self):
        log.debug("Reading depth...")
        return frame_convert2.pretty_depth_cv(freenect.sync_get_depth()[0])

    def _get_video(self):
        log.debug("Reading video frame...")
        return frame_convert2.video_cv(freenect.sync_get_video()[0])

    def _draw_on_image(self, frame, circles):
        if len(circles) > 0 :
            utils.draw_str(frame, (25, 100), "I saw balls!: " + str(len(circles)))

        if self._shouldDrawDebugRects:
            self._ball_tracker.drawDebugRects(frame)

    def show(self, depth_frame, video_frame):
        cv2.imshow('Depth', depth_frame)
        cv2.imshow('Video', video_frame)

    def _track(self, frame):
        '''
        self._circle_tracker.update(frame)
        circles = self._circle_tracker.elements
        if len(circles) > 0 :
            log.debug("Balls tracked: " + str(len(circles)))
            for circle in circles:
                print(circle.rect)
        '''
        self._ball_tracker.update(frame)
        frame = frame.copy()
        balls = self._ball_tracker.elements
        if len(balls) > 0 :
            log.debug("Balls tracked: " + str(len(balls)))
            for ball in balls:
                print(ball.rect)

		self._draw_on_image(frame,balls)
		message = str(mapValue(balls[0].rect[0], 0,270, -100, 100)) + ',' + str(mapValue(balls[0].rect[1], 0,200, -100, 100))
		self.client.send(message)


    def run(self):
        while True:
            sleep(0.2)
            depth_frame = self._get_depth()
            frame = self._get_video()
            self._track(frame)
            self.show(depth_frame, frame)
            if cv2.waitKey(10) == 27:
                break

if __name__ == "__main__":
    log.debug("Starting ocula application...")
    sleep(2) ## time to warming up the camera
    Ocula().run()
