import time
import cv2
import sys
import os
import datetime
import subprocess

sys.path.insert(0, '/home/pi/autonom/camera')
sys.path.insert(0, '/home/pi/autonom/gy87')
sys.path.insert(0, '/home/pi/autonom/gps')

from gps_thread import GPS_Thread
from mycamera import MyCamera
from mpu6050 import MPU6050

LOGFILE = "/home/pi/autonom/roadlog.txt"
IMAGEPATH = "/home/pi/autonom/images/"
file = open(LOGFILE, "a")

gps = GPS_Thread(baud=4800)
cam = MyCamera()
mpu = MPU6050(0x68)

gps.start()
time.sleep(5)

# make an image directory
if not "images" in os.listdir(): os.mkdir("images")

print("[INFO] waiting for GSP signal... ")
while True:
    position = gps.get_position()
    satellites = gps.get_num_satellites()
    if position[0] is not None and position[1] is not None:
        print("\n[INFO] GSP position information is acquired!")
        break
    else:
        print("{}".format(satellites), end='')
        time.sleep(1)

gpsdatetime = gps.get_date_time()
gpstimestamp = datetime.datetime(gpsdatetime[0], gpsdatetime[1], gpsdatetime[2], gpsdatetime[4], gpsdatetime[5], gpsdatetime[6])
gpstimestamp = gpstimestamp.strftime("%Y-%m-%d-%H:%M:%S")
print("[INFO] GPS time: {}".format(gpstimestamp))
#subprocess.call(['sudo', 'date', '--set=\"' + synctime + '\"'], shell=True)

print("[INFO] start data acquisition...")
while True:
    # generate timestamp
    timestamp = datetime.datetime.now()
    timestamp = timestamp.strftime("%Y-%m-%d-%H:%M:%S")

    position = gps.get_position()
    speed = gps.get_speed()
    
    # read image and add timestamp
    frame = cam.read() #RGB image
    (R, G, B) = cv2.split(frame)
    image = cv2.merge([B, G, R])
    cv2.putText(frame, timestamp, (10, frame.shape[0]-10), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (0,0,255, 1))
    
    # save image with a new name
    entry = "img_" + timestamp
    filename = IMAGEPATH + entry + ".jpg" 
    cv2.imwrite(filename, image)
    
    # read inertial data
    accel = mpu.get_accel_data()
    gyro = mpu.get_gyro_data()
    
    cv2.imshow("Image", image)
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

    file.write("{}, {:.3f}, {:.3f}, {:.1f}, {:.3f}, {:.3f}, {:.3f}, {:.3f}, {:.3f}, {:.3f}\n".format(
        timestamp, position[0], position[1], speed, accel['x'], accel['y'], accel['z'], gyro['x'], gyro['y'], gyro['z']))
    
cv2.destroyAllWindows()
file.close()
gps.stop()
print("[INFO] end of data acquisition")