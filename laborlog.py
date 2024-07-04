import inputs
import datetime
import sys
import time

sys.path.insert(0, '/home/pi/autonom/pca9685')
sys.path.insert(0, '/home/pi/autonom/dsp')
sys.path.insert(0, '/home/pi/autonom/gy87')
sys.path.insert(0, '/home/pi/autonom/encoder')

from dsp import MovingAvg
from pca9685 import Motors
from mpu6050 import MPU6050
from encoder import Encoder

def remap(oldvalue, oldmax, oldmin, newmax, newmin):
    oldrange = (oldmax - oldmin)  
    newrange = (newmax - newmin)  
    newvalue = (((oldvalue - oldmin) * newrange) / oldrange) + newmin
    return newvalue

pads = inputs.devices.gamepads
PROGRAM_LOOP = True
VERBOSE = False
dc_pwm = 35
servo_angle = 0

#speedavg = MovingAvg(1)
#angleavg = MovingAvg(1)
motors = Motors()
#avgspeed = 0.0
#avgangle = 0.0

mpu = MPU6050(0x68)

if len(pads) == 0:
    raise Exception("Couldn't find any Gamepads!")
else:
    print("Devices:\n {}".format(inputs.devices.gamepads))
    print("Starting program...")

while PROGRAM_LOOP:
    LOG = False
    LOOP = True

    # generate timestamp
    timestamp = datetime.datetime.now()
    timestamp = timestamp.strftime("%Y-%m-%d-%H:%M:%S")

    LOGFILE = "/home/pi/autonom/labor_data/laborlog_" + timestamp + ".txt"
    file = open(LOGFILE, "a")

    # initialize and start encoder thread
    encoder = Encoder(pin = 16, st = 1.0)
    encoder.start()

    while LOOP:
        # read inertial data
        accel = mpu.get_accel_data()
        gyro = mpu.get_gyro_data()

        # # read velocity from encoder
        velocity = encoder.get_velocity()

        if LOG:
            file.write("{:.1f}, {:.1f}, {:.3f}, {:.3f}, {:.3f}, {:.3f}, {:.3f}\n".format(
                velocity, accel['x'], accel['y'], accel['z'], gyro['x'], gyro['y'], gyro['z']))

        # read joystick events
        events = inputs.get_gamepad()

        for event in events:         
            if event.code == "BTN_C" and int(event.state) == 1:
                motors.servo_angle(0)
                motors.stop_dc()
                LOOP = False
                PROGRAM_LOOP = False
            # finalize data acquisition cycle
            elif event.code == "BTN_SOUTH" and int(event.state) == 1:
                motors.servo_angle(0)
                motors.stop_dc()
                LOOP = False
                print("[INFO] End of driving...")
            # start data acquisition cycle with fixed pwm rate
            elif event.code == "BTN_EAST" and int(event.state) == 1:
                LOG = True
                motors.servo_angle(0)
                motors.velocity(dc_pwm)
                print("[INFO] Start driving...")
                cycle_start = time.time()
            elif event.code == "ABS_HAT0Y":
                if int(event.state) == -1 and dc_pwm <= 95:
                    dc_pwm += 5
                elif int(event.state) == 1 and dc_pwm >= 5:
                    dc_pwm -= 5
                motors.velocity(dc_pwm)
                if VERBOSE: print("[INFO] dc pwm: {}".format(dc_pwm))
            elif event.code == "ABS_HAT0X":
                if int(event.state) == -1 and servo_angle < 15:
                    servo_angle += 1
                elif int(event.state) == 1 and servo_angle >= -15:
                    servo_angle -= 1
                motors.servo_angle(servo_angle)
                if VERBOSE: print("[INFO] angle: {}".format(servo_angle))
            # start data acquisition with fixed pwm rate
            elif event.code == "ABS_Y":
                joyvalue = int(event.state) - 128
                if joyvalue <= 0:
                    dc_pwm = remap(abs(joyvalue), 128, 0, 100, 0)
                    #speedavg.update(speed)
                    #avgspeed = speedavg.get_avg()
                    motors.velocity(dc_pwm)
                    if VERBOSE: print("[INFO] dc pwm: {}".format(dc_pwm))
            elif event.code == "ABS_Z":
                joyvalue = int(event.state) - 128
                angle = remap(joyvalue, 128, -128, Motors.MAX_ANGLE, Motors.MIN_ANGLE)
                #angleavg.update(angle)
                #avgangle = angleavg.get_avg()
                motors.servo_angle(-angle)
                if VERBOSE: print("[INFO] angle: {}".format(angle)) 
    
    print("[INFO] avg velocity: {:.2f} m/s".format(encoder.get_avgvelocity()))
    print("[INFO] distance: {:.2f}, {:.2f} m".format(encoder.get_distance_from_velocity(), encoder.get_distance_from_pulses()))
    print("[INFO] # pulses: {}".format(encoder.get_total_pulses()))
    print("[INFO] cycle time: {:.2f} s".format(time.time() - cycle_start))
    file.write("{:.1f}, {:.1f}, {}\n".format(encoder.get_avgvelocity(), encoder.get_distance_from_velocity(), 
                                             encoder.get_total_pulses()))
    file.close()
    encoder.stop() 
print("[INFO] End of program")