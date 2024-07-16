import inputs
import datetime
import sys
import time

sys.path.insert(0, '/home/pi/autonom/pca9685')
sys.path.insert(0, '/home/pi/autonom/gy87')
sys.path.insert(0, '/home/pi/autonom/encoder')

from pca9685 import Motors
from mpu6050 import MPU6050
from encoder import Encoder

dc_pwm = 41
loopcount = 0

motors = Motors()
mpu = MPU6050(0x68)

 # generate timestamp
timestamp = datetime.datetime.now()
timestamp = timestamp.strftime("%Y-%m-%d-%H:%M:%S")

LOGFILE = "/home/pi/autonom/labor_data/laborlog_" + timestamp + ".txt"
file = open(LOGFILE, "a")

# initialize and start encoder thread
encoder = Encoder(pin = 16, st = 1.0)
encoder.start()

print("[INFO] Start driving...")
motors.servo_angle(0.25)
motors.velocity(dc_pwm)

try:
    start = time.time()
    while True:
        # read inertial data
        accel = mpu.get_accel_data()
        gyro = mpu.get_gyro_data()

        # read velocity from encoder
        velocity = encoder.get_velocity()

        loopcount += 1

        file.write("{:.1f}, {:.1f}, {:.3f}, {:.3f}, {:.3f}, {:.3f}, {:.3f}\n".format(
                    velocity, accel['x'], accel['y'], accel['z'], gyro['x'], gyro['y'], gyro['z']))
except KeyboardInterrupt:
    pass

motors.velocity(0)
print(loopcount)
print("[INFO] avg velocity: {:.2f} m/s".format(encoder.get_avgvelocity()))
print("[INFO] distance: {:.2f}, {:.2f} m".format(encoder.get_distance_from_velocity(), encoder.get_distance_from_pulses()))
print("[INFO] # pulses: {}".format(encoder.get_total_pulses()))
file.write("{:.1f}, {:.1f}, {}\n".format(encoder.get_avgvelocity(), encoder.get_distance_from_velocity(), 
                                         encoder.get_total_pulses()))
file.close()
encoder.stop() 
print("[INFO] End of program")