import inputs
import datetime
import sys

sys.path.insert(0, '/home/pi/autonom/pca9685')
sys.path.insert(0, '/home/pi/autonom/dsp')
sys.path.insert(0, '/home/pi/autonom/gy87')

from dsp import MovingAvg
from pca9685 import Motors
from mpu6050 import MPU6050

def remap(oldvalue, oldmax, oldmin, newmax, newmin):
    oldrange = (oldmax - oldmin)  
    newrange = (newmax - newmin)  
    newvalue = (((oldvalue - oldmin) * newrange) / oldrange) + newmin
    return newvalue

pads = inputs.devices.gamepads
LOOP = True

speedavg = MovingAvg(3)
angleavg = MovingAvg(3)
motors = Motors()
avgspeed = 0.0
avgangle = 0.0

mpu = MPU6050(0x68)

# generate timestamp
timestamp = datetime.datetime.now()
timestamp = timestamp.strftime("%Y-%m-%d-%H:%M:%S")

LOGFILE = "/home/pi/autonom/labor_data/laborlog_" + timestamp + ".txt"
file = open(LOGFILE, "a")

if len(pads) == 0:
    raise Exception("Couldn't find any Gamepads!")
else:
    print("Devices:\n {}".format(inputs.devices.gamepads))
    print("Start driving...")

    while LOOP:
         # read inertial data
        accel = mpu.get_accel_data()
        gyro = mpu.get_gyro_data()

        events = inputs.get_gamepad()

        for event in events:
            if event.code == "BTN_SOUTH":
                motors.servo_angle(0)
                motors.stop_dc()
                file.close()
                LOOP = False
            elif event.code == "ABS_Y":
                joyvalue = int(event.state) - 128
                if joyvalue <= 0:
                    speed = remap(abs(joyvalue), 128, 0, 100, 0)
                    speedavg.update(speed)
                    avgspeed = speedavg.get_avg()
                    motors.velocity(avgspeed)
                    print("speed: {}".format(avgspeed))

                    file.write("{:.1f}, {:.1f}, {:.1f}, {:.3f}, {:.3f}, {:.3f}, {:.3f}, {:.3f}\n".format(
                               avgspeed, avgangle, accel['x'], accel['y'], accel['z'], gyro['x'], gyro['y'], gyro['z']))
            elif event.code == "ABS_Z":
                joyvalue = int(event.state) - 128
                angle = remap(joyvalue, 128, -128, Motors.MAX_ANGLE, Motors.MIN_ANGLE)
                angleavg.update(angle)
                avgangle = angleavg.get_avg()
                motors.servo_angle(avgangle)
                #print("angle: {}".format(avgangle)) 
            #print(event.code) #, event.state
    
    print("End of driving...")