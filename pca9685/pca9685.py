import board
import time
from adafruit_pca9685 import PCA9685
from adafruit_motor import servo

class Motors:
    MIN_ANGLE = -20
    MAX_ANGLE = 22
    MIN_PWM = 4600
    MAX_PWM = 4850
    DELTA_PWM = (MAX_PWM - MIN_PWM) / 100.0

    def __init__(self, freq = 50, dc_ch=0, servo_ch=1):
        self.dc_ch = dc_ch
        self.servo_ch = servo_ch
        # Create the I2C bus interface.
        i2c = board.I2C()  # uses board.SCL and board.SDA
        # Create a simple PCA9685 class instance.
        self.pca = PCA9685(i2c)
        # Set the PWM frequency to 50Hz.
        self.pca.frequency = freq
        self.servo = servo.Servo(self.pca.channels[servo_ch], min_pulse=580, max_pulse=2350)
    
    def set_duty(self, duty=20):
        '''The duty cycle should be a 16-bit value, i.e. 0 to 0xffff,
        which represents what percent of the time the signal is on vs.
        off. A value of 0xffff is 100% brightness, 0 is 0% brightness,
        and in-between values go from 0% to 100% brightness.'''
        if 0 < duty and duty <= 100:
            duty_val = int(65535 * (duty / 100.0))
            self.pca.channels[self.dc_ch].duty_cycle = duty_val 
        else:
            self.pca.channels[self.dc_ch].duty_cycle = 0
        
    def servo_angle(self, angle=0):
        '''Theoretical range: -90-90'''
        if Motors.MIN_ANGLE <= angle and angle <= Motors.MAX_ANGLE: 
            self.servo.angle = angle + 90.0
            
    def velocity(self, v=0):
        '''Theoretical range: 0-100'''
        pwmvalue = Motors.MIN_PWM + int(v * Motors.DELTA_PWM)
        print(pwmvalue)
        self.pca.channels[self.dc_ch].duty_cycle = pwmvalue
            
    def servo_calibration(self):
        for i in range(Motors.MIN_ANGLE, Motors.MAX_ANGLE): 
            self.servo_angle(i)
            print("Left angle: {}".format(i))
            time.sleep(0.5)

    def stop_dc(self):
        self.pca.channels[self.dc_ch].duty_cycle = 0 

    def dc_calibration(self):
        '''f = 50Hz -> T = 20mS. Theoretical range of ESC is between 1 to 2mS.
        However it requires examination
        '''
        for i in range(Motors.MIN_PWM, Motors.MAX_PWM): 
            self.pca.channels[self.dc_ch].duty_cycle = i 
            print("Duty value: {}".format(i))
            time.sleep(0.2)

motors = Motors()
#motors.servo_angle(0)
#motors.servo_calibration()
motors.dc_calibration()
#motors.velocity(50)
#time.sleep(3)
motors.stop_dc()



