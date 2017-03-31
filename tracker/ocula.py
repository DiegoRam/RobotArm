import freenect, configparser, logging
import cv2
import frame_convert2

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
if env == 'pi':
	file_handler.setFormatter(formatter)
	log.addHandler(file_handler)
log.addHandler(handler)


while True:

class Ocula(object):
    def __init__(self):
        self._window_depth = cv2.namedWindow('Depth')
        self._window_video = cv2.namedWindow('Video')

    def _get_depth(self):
        log.debug("Reading depth...")
        return frame_convert2.pretty_depth_cv(freenect.sync_get_depth()[0])

    def _get_video(self):
        log.debug("Reading video frame...")
        return frame_convert2.video_cv(freenect.sync_get_video()[0])

    def run(self):
        while True:
            cv2.imshow('Depth', get_depth())
            cv2.imshow('Video', get_video())
            if cv2.waitKey(10) == 27:
                break

if __name__ == "__main__":
    log.degug("Starting ocula application...")
    sleep(2) ## time to warming up the camera
    Ocula.run()
