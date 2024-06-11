from picamera2 import Picamera2
from threading import Thread
import time
import datetime

class MyCamera:
    def __init__(self, color_space='BGR888', resolution=(1024, 768)):
        self.warming_time = 1.0
        self.camera = Picamera2()
        self.camera_config = self.camera.create_preview_configuration({'format': color_space, 'size': resolution})
        self.camera.configure(self.camera_config)
        self.frame = None
        self.camera.start()
        time.sleep(self.warming_time)
        print("[Camera] camera config:\n {}".format(self.camera_config["main"]))
            
    def read(self):
        '''Return the frame most recently read'''
        return self.camera.capture_array()
    
    def set_color_space():
        pass


class FPS:
    def __init__(self):
        '''start, stop time of the investigation period
        and the number of frames'''
        self._start = None
        self._end = None
        self.num_frames = 0
        
    def start(self):
        '''start the timer'''
        self._start = datetime.datetime.now()
         
    def stop(self):
        '''start the timer'''
        self._end = datetime.datetime.now()
        
    def update(self):
        '''increment the total number of frames'''
        self.num_frames += 1
        
    def elapsed(self):
        '''return the total number seconds between end and start'''
        return (self._end - self._start).total_seconds()
    
    def fps(self):
        '''approximated frames per second'''
        return self.num_frames / self.elapsed()