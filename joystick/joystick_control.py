import inputs
import sys

sys.path.insert(0, '/home/pi/autonom/pca9685')
sys.path.insert(0, '/home/pi/autonom/dsp')

from dsp import MovingAvg
from pca9685 import Motors

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

if len(pads) == 0:
    raise Exception("Couldn't find any Gamepads!")
else:
    print("Devices:\n {}".format(inputs.devices.gamepads))
    print("Start driving...")

    while LOOP:
        events = inputs.get_gamepad()
        for event in events:
            if event.code == "BTN_SOUTH":
                motors.servo_angle(0)
                motors.stop_dc()
                LOOP = False
            elif event.code == "ABS_Y":
                joyvalue = int(event.state) - 128
                if joyvalue <= 0:
                    speed = remap(abs(joyvalue), 128, 0, 100, 0)
                    speedavg.update(speed)
                    avgspeed = speedavg.get_avg()
                    motors.velocity(avgspeed)
                    print("speed: {}".format(avgspeed))
            elif event.code == "ABS_Z":
                joyvalue = int(event.state) - 128
                angle = remap(joyvalue, 128, -128, Motors.MAX_ANGLE, Motors.MIN_ANGLE)
                angleavg.update(angle)
                avgangle = angleavg.get_avg()
                motors.servo_angle(avgangle)
                print("angle: {}".format(avgangle)) 
            #print(event.code) #, event.state
    
    print("End of driving...")