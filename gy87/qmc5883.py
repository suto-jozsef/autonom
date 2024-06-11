"""
Raspberry OS implementation for interfacing with an QMC5883 via I2C. 
Author: Jozsef Suto
Year: 2024
Version: 1.0
"""

import smbus           
from time import sleep         

class QMC5883:
    # registers
    X_LSB = 0x00
    Y_LSB = 0x02
    Z_LSB = 0x04
    
    STATUS_REG = 0x06
    TEMPERATURE_LSB = 0x07
    CNTR_REG1 = 0x09
    CNTR_REG2 = 0x0A
    SET_RESET = 0x0B
 
    def __init__(self, address, frequency=10, oversample=512):
        self.address = address
        self.bus = smbus.SMBus(1)
        mask = 0b00010001
        
        if frequency == 10:
            pass
        elif frequency == 50:
            mask = mask | 0b00000100
        elif frequency == 100:
            mask = mask | 0b00001000
        elif frequency == 200:
            mask = mask | 0b00001100
        else:
            print("[QMC5883 ERROR] Unavailable frequency value!")
            
        if oversample == 512:
            pass
        elif oversample == 256:
            mask = mask | 0b01000000
        elif oversample == 128:
            mask = mask | 0b10000000
        elif oversample == 64:
            mask = mask | 0b11000000
        else:
            print("[QMC5883 ERROR] Unavailable oversample rate!")
            
        # soft reset
        self.bus.write_byte_data(self.address, QMC5883.CNTR_REG2, 0x80)
        # disable interrupt, no roll-over, no soft-reset
        self.bus.write_byte_data(self.address, QMC5883.CNTR_REG2, 0x01)    
        # set_reset register constant 0x01
        self.bus.write_byte_data(self.address, QMC5883.SET_RESET, 0x01)
        # set frequency, resolution, and mode
        self.bus.write_byte_data(self.address, QMC5883.CNTR_REG1, mask)
    
        cntr = self.bus.read_byte_data(self.address, QMC5883.CNTR_REG1)
        
        if (cntr & 0b01):
            mode = "continuous"
        else:
            mode = "standby"
        
        if (cntr & 0b1100) == 0:
            freq = 10
        elif (cntr & 0b1100) == 4:
            freq = 50
        elif (cntr & 0b1100) == 8:
            freq = 100
        else:
            freq = 200
            
        print("QMC5883 configuration:\nMode: {}\nFrequency: {}Hz".format(mode, freq))
 
    def read_word(self, register):
        """Read a 16-bit registers and convers its value from 2's complement to integer"""
        # Read the data from the registers
        low = self.bus.read_byte_data(self.address, register)
        high = self.bus.read_byte_data(self.address, register + 1)
 
        value = (high << 8) + low
 
        if (value >= 32768):
            # negative sign
            return -32768 + (value & 0x7FFF)
        else:
            return value
        
    def get_magneto_data(self):
        """Returns the X, Y and Z values from the magnetometer"""
        # Read the raw data from the MPU-6050
        x = self.read_word(QMC5883.X_LSB)
        y = self.read_word(QMC5883.Y_LSB)
        z = self.read_word(QMC5883.Z_LSB)
 
        return {'x': x, 'y': y, 'z': z}
    
    def get_temperature(self):
        """Returns the temperature value"""
        # Read the raw data from the MPU-6050
        temperature = self.read_word(QMC5883.TEMPERATURE_LSB)
        return temperature
    
    def is_data_available(self):
        status = self.bus.read_byte_data(self.address, QMC5883.STATUS_REG)
        print(status)
        return (status & 0x01)