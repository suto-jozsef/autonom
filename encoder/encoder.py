import RPi.GPIO as GPIO  
import time
import threading 
from math import pi

class Encoder:
    def __init__(self, pin = 16, radius = 3.75, st = 1.0, dist_per_cycle = 24):
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
        self.distance = 0.0
        self.dist_per_cycle = dist_per_cycle
        GPIO.setmode(GPIO.BCM)      
        GPIO.setup(self.pin, GPIO.IN)   
        self.capture_thread = threading.Thread(target=self.count_pulses)
        self.stop_event = threading.Event() 
    
    def start(self):
        print("[Encoder] starting encoder thread...")
        self.capture_thread.start()
        
    def stop(self):
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
            
            self.total_pulses += pulses
            
            #pulse count method - w=2pi*n/N*dt - calculate angular speed (rad / s)
            omega = (2.0 * pi * pulses) / self.st

            # calculate linear velocity v = r * w
            self.velocity = omega * (self.radius / 100.0)
            self.distance += self.velocity * self.st

            # take into account the time intervals when the vehicle was moving
            if 0.0 < self.velocity:
                self.accum_velocity += self.velocity
                self.measurements += 1
    
    def get_velocity(self):
        return self.velocity
    
    def get_distance_from_velocity(self):
        return self.distance
    
    def get_distance_from_pulses(self):
        return self.total_pulses * (self.dist_per_cycle / 100.0)

    def get_total_pulses(self):
        return self.total_pulses
    
    def get_measurements(self):
        return self.measurements
    
    def get_avgvelocity(self):
        if 0 < self.measurements:
            return self.accum_velocity / self.measurements
        else:
            return 0.0
