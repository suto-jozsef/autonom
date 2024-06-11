import time
import cv2
from mycamera import MyCamera 

#camera = Picamera2()
#camera_config = camera.create_preview_configuration({'format': 'RGB888', 'size': (640,480)})
#camera.configure(camera_config)
#config = camera.preview_configuration(main={"size": (640, 480)})
#camera.configure(config)
#picam2.start_preview(Preview.QTGL)
#camera.start()
time.sleep(2)
cam = MyCamera()

while 1:
    frame = cam.read() #camera.capture_array()
    cv2.imshow("Image", frame)
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break
cv2.destroyAllWindows()