import RPi.GPIO as GPIO  
import time
import threading 
from math import pi


class Encoder:
    def __init__(self, pin = 16, radius = 3.75, st = 1.0):
        '''
        radius - radius of the wheel in cm
        st - sampling time interval in second
        '''
        self.pin = pin
        self.st = st
        self.radius = radius
        self.total_pulses = 0
        self.measurements = 0
        self.accum_velocity = 0
        self.velocity = 0.0
        GPIO.setmode(GPIO.BCM)      
        GPIO.setup(self.pin, GPIO.OUT)   
        self.capture_thread = threading.Thread(target=self.count_pulses)
        self.stop_event = threading.Event() 
    
    def start(self):
        print("[Encoder] starting encoder thread...")
        self.capture_thread.start()
        
    def stop(self):
        print("[Encoder] Avg speed: {}".format(self.accum_velocity / self.measurements))
        print("[Encoder] stop encoder thread")
        self.stop_event.set()

    def count_pulses(self):
        while not self.stop_event.is_set():
            start = time.time()
            state = True
            pulses = 0

            #count #pulses per sampling interval
            while (time.time() - start) < self.st:             
                if not GPIO.input(self.pin):
                    if state:
                        pulses += 1
                        state = False 
                else:
                    state = True
            
            self.measurements += 1
            self.total_pulses += pulses
            
            #pulse count method - w=2pi*n/N*dt - calculate angular speed (rad / s)
            omega = (2.0 * pi * pulses) / self.st

            # calculate linear velocity v = r * w
            self.velocity = omega * (self.radius / 100.0)
            self.accum_velocity += self.velocity
    
    def get_velocity(self):
        return self.velocity
    
    def get_avgvelocity(self):
        if self.accum_velocity != 0:
            return self.accum_velocity / self.measurements




  