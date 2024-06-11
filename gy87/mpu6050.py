"""
Raspberry OS implementation for interfacing with an MPU-6050 via I2C. 
Author: Jozsef Suto
Year: 2024
Version: 1.0
"""

import smbus           
from time import sleep         

class MPU6050:
    # registers
    CONFIG = 0x1A
    ACCEL_CONFIG = 0x1C
    GYRO_CONFIG = 0x1B
    INT_PIN_CFG = 0x37
    USER_CTRL = 0x6a
    
    ACCEL_XOUT0 = 0x3B
    ACCEL_XOUT1 = 0x3C
    ACCEL_YOUT0 = 0x3D
    ACCEL_YOUT1 = 0x3E
    ACCEL_ZOUT0 = 0x3F
    ACCEL_ZOUT1 = 0x40
    
    TEMP_OUT0 = 0x41
    TEMP_OUT1 = 0x42
 
    GYRO_XOUT0 = 0x43
    GYRO_XOUT1 = 0x44
    GYRO_YOUT0 = 0x45
    GYRO_YOUT1 = 0x46
    GYRO_ZOUT0 = 0x47
    GYRO_ZOUT1 = 0x48
    
    PWR_MGMT_1 = 0x6B
    PWR_MGMT_2 = 0x6C
    ################################################################
    
    # constants
    ACCEL_RANGE_2G = GYRO_RANGE_250DEG = 0x00	#AFS_SEL = FSEL=0 
    ACCEL_RANGE_4G = GYRO_RANGE_500DEG = 0x08	#AFS_SEL = FSEL=1
    ACCEL_RANGE_8G = GYRO_RANGE_1000DEG = 0x10	#AFS_SEL = FSEL=2
    ACCEL_RANGE_16G = GYRO_RANGE_2000DEG = 0x18	#AFS_SEL = FSEL=3
    
    GYRO_RANGES = {250: GYRO_RANGE_250DEG, 500: GYRO_RANGE_500DEG,
                   1000: GYRO_RANGE_1000DEG, 2000: GYRO_RANGE_2000DEG}
    
    ACCEL_RANGES = {2: ACCEL_RANGE_2G, 4: ACCEL_RANGE_4G,
                    8: ACCEL_RANGE_8G, 16: ACCEL_RANGE_16G}
    
    ACCEL_FREQ = {260: 0, 184: 1, 94: 2, 44: 3, 21: 4, 10: 5, 5: 6}
 
    ACCEL_SCALE_MODIFIER_2G = 16384.0
    ACCEL_SCALE_MODIFIER_4G = 8192.0
    ACCEL_SCALE_MODIFIER_8G = 4096.0
    ACCEL_SCALE_MODIFIER_16G = 2048.0
 
    GYRO_SCALE_MODIFIER_250DEG = 131.0
    GYRO_SCALE_MODIFIER_500DEG = 65.5
    GYRO_SCALE_MODIFIER_1000DEG = 32.8
    GYRO_SCALE_MODIFIER_2000DEG = 16.4
    
    GRAVITIY_MS2 = 9.80665
 
    def __init__(self, address, accel_range=4, accel_freq=94, gyro_range=500):
        self.address = address
        self.bus = smbus.SMBus(1)

        self.set_gyro_range(gyro_range)
        self.set_accel_range(accel_range)
        self.set_accel_freq(accel_freq)
        
        # Allow HMC magnetometer to be accessible 
        self.bus.write_byte_data(self.address, MPU6050.INT_PIN_CFG, 0x02)
        self.bus.write_byte_data(self.address, MPU6050.USER_CTRL, 0x00)
 
        # Wake up the MPU-6050 since it starts in sleep mode
        self.set_power_management(sleep=0, cycle=0, temp_on_off=0, clk=0)
        
        init_accel_range = self.read_accel_range(raw=False)
        init_gyro_range = self.read_gyro_range()
        init_accel_freq = self.read_accel_freq()
        print("MPU6050 configuration:\nAcceleration range: {}G\nGyroscope range: {}deg\nAcceleration sampling rate: {}\n".format(
            init_accel_range, init_gyro_range, init_accel_freq))
 
    # I2C communication methods
    def read_word(self, register):
        """Read a 16-bit registers and convers its value from 2's complement to integer"""
        # Read the data from the registers
        high = self.bus.read_byte_data(self.address, register)
        low = self.bus.read_byte_data(self.address, register + 1)
 
        value = (high << 8) + low
 
        if (value >= 32768):
            # negative sign
            return -32768 + (value & 0x7FFF)
        else:
            return value
    
    def read_accel_range(self, raw=False):
        """Reads the range the accelerometer"""
        # Get the raw value
        raw_data = self.bus.read_byte_data(self.address, MPU6050.ACCEL_CONFIG)
 
        if raw is True:
            return raw_data
        elif raw is False:
            if raw_data == MPU6050.ACCEL_RANGE_2G:
                return 2
            elif raw_data == MPU6050.ACCEL_RANGE_4G:
                return 4
            elif raw_data == MPU6050.ACCEL_RANGE_8G:
                return 8
            elif raw_data == MPU6050.ACCEL_RANGE_16G:
                return 16
            else:
                return -1
            
    def read_accel_freq(self):
        """Reads the sampling rate of accelerometer"""
        key = -1
        reg = self.bus.read_byte_data(self.address, MPU6050.CONFIG)
 
        for k, v in self.ACCEL_FREQ.items():
            if v == int(reg):
                key = k
                break
        
        return key
 
    def read_gyro_range(self, raw = False):
        """Reads the range the gyroscope"""
        # Get the raw value
        raw_data = self.bus.read_byte_data(self.address, MPU6050.GYRO_CONFIG)
 
        if raw is True:
            return raw_data
        elif raw is False:
            if raw_data == MPU6050.GYRO_RANGE_250DEG:
                return 250
            elif raw_data == MPU6050.GYRO_RANGE_500DEG:
                return 500
            elif raw_data == MPU6050.GYRO_RANGE_1000DEG:
                return 1000
            elif raw_data == MPU6050.GYRO_RANGE_2000DEG:
                return 2000
            else:
                return -1
    
    def set_power_management(self, sleep=0, cycle=0, temp_on_off=0, clk=0):
        """ Set power configuration. At turn on, the device is in sleep mode (default value 0x40) """
        config = ((sleep & 0b1) << 6) | ((cycle & 0b1) << 5) | ((temp_on_off & 0b1) << 3) | (clk & 0b111)
        self.bus.write_byte_data(self.address, MPU6050.PWR_MGMT_1, config)
     
    def set_gyro_range(self, gyro_range):
        """ Set gyroscope range using the pre-defined ranges """        
        config = MPU6050.GYRO_RANGES.get(gyro_range)
        
        if config: 
            # Write the new range to the ACCEL_CONFIG register
            self.gyro_range = config
            self.bus.write_byte_data(self.address, MPU6050.GYRO_CONFIG, config)
        else:
            print("[MPU6050 ERROR] Unknown gyroscope range!")
            
    def set_accel_freq(self, freq):
        """ 0 - 260Hz, 1 - 184Hz, 2 - 94Hz, 3 - 44Hz, 4 - 21Hz, 5 - 10Hz, 6 - 5Hz """        
        config = MPU6050.ACCEL_FREQ.get(freq)
        
        if config: 
            # Write the new range to the ACCEL_CONFIG register
            self.accel_freq = config
            self.bus.write_byte_data(self.address, MPU6050.CONFIG, config)
        else:
            print("[MPU6050 ERROR] Unknown sampling rate!")
        
    def set_accel_range(self, accel_range):
        """ Set acceleration range using the pre-defined ranges """       
        config = MPU6050.ACCEL_RANGES.get(accel_range)
        
        if config: 
            # Write the new range to the ACCEL_CONFIG register
            self.accel_range = config
            self.bus.write_byte_data(self.address, MPU6050.ACCEL_CONFIG, config)
        else:
            print("[MPU6050 ERROR] Unknown acceleration range!")
            
    def get_accel_data(self, g=False):
        """ Returns the X, Y and Z values from the accelerometer.
            If g is True, it will return the data in g
            If g is False, it will return the data in m/s^2
        """
        # Read the data from the MPU-6050
        x = self.read_word(MPU6050.ACCEL_XOUT0)
        y = self.read_word(MPU6050.ACCEL_YOUT0)
        z = self.read_word(MPU6050.ACCEL_ZOUT0)
 
        if self.accel_range == MPU6050.ACCEL_RANGE_2G:
            accel_scale_modifier = MPU6050.ACCEL_SCALE_MODIFIER_2G
        elif self.accel_range == MPU6050.ACCEL_RANGE_4G:
            accel_scale_modifier = MPU6050.ACCEL_SCALE_MODIFIER_4G
        elif self.accel_range == MPU6050.ACCEL_RANGE_8G:
            accel_scale_modifier = MPU6050.ACCEL_SCALE_MODIFIER_8G
        elif self.accel_range == MPU6050.ACCEL_RANGE_16G:
            accel_scale_modifier = MPU6050.ACCEL_SCALE_MODIFIER_16G
        else:
            print("[MPU6050 ERROR] Unknown acceleration range of instance!")
            accel_scale_modifier = MPU6050.ACCEL_SCALE_MODIFIER_4G
 
        x = x / accel_scale_modifier
        y = y / accel_scale_modifier
        z = z / accel_scale_modifier
 
        if g is True:
            return {'x': x, 'y': y, 'z': z}
        else:
            x = x * self.GRAVITIY_MS2
            y = y * self.GRAVITIY_MS2
            z = z * self.GRAVITIY_MS2
            return {'x': x, 'y': y, 'z': z}
        
    def get_temperature(self):
        """ Reads the temperature from MPU-6050"""
        # Get the raw data
        raw_temp = self.read_word(self.TEMP_OUT0)
 
        # Temperature in degrees C = (TEMP_OUT Register Value as a signed quantity)/340 + 36.53
        return (raw_temp / 340) + 36.53
    
    def get_gyro_data(self):
        """Returns the X, Y and Z values from the gyroscope"""
        # Read the raw data from the MPU-6050
        x = self.read_word(MPU6050.GYRO_XOUT0)
        y = self.read_word(MPU6050.GYRO_YOUT0)
        z = self.read_word(MPU6050.GYRO_ZOUT0)
 
        if self.gyro_range == MPU6050.GYRO_RANGE_250DEG:
            gyro_scale_modifier = MPU6050.GYRO_SCALE_MODIFIER_250DEG
        elif self.gyro_range == MPU6050.GYRO_RANGE_500DEG:
            gyro_scale_modifier = MPU6050.GYRO_SCALE_MODIFIER_500DEG
        elif self.gyro_range == MPU6050.GYRO_RANGE_1000DEG:
            gyro_scale_modifier = MPU6050.GYRO_SCALE_MODIFIER_1000DEG
        elif self.gyro_range == MPU6050.GYRO_RANGE_2000DEG:
            gyro_scale_modifier = MPU6050.GYRO_SCALE_MODIFIER_2000DEG
        else:
            print("[MPU6050 ERROR] Unknown gyroscope range of instance!")
            gyro_scale_modifier = MPU6050.GYRO_SCALE_MODIFIER_250DEG
 
        x = x / gyro_scale_modifier
        y = y / gyro_scale_modifier
        z = z / gyro_scale_modifier
 
        return {'x': x, 'y': y, 'z': z}