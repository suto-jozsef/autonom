"""
Raspberry OS implementation for interfacing with an HMC5883 via I2C. 
Author: Jozsef Suto
Year: 2024
Version: 1.0
"""

import smbus           
from time import sleep         

class HMC5883:
    # registers
    CONFA = 0x00
    CONFB = 0x01
    MODE_REG = 0x02
    
    X_MSB = 0x03
    Z_MSB = 0x05
    Y_MSB = 0x07
    
    STATUS_REG = 0x09
    ID_REG1 = 0x0A
    ID_REG2 = 0x0B
    ID_REG3 = 0x0C

    def __init__(self, address, frequency=15, averaging=8, gain=0):
        self.address = address
        self.bus = smbus.SMBus(1)
        cra = 0b01110000
        crb = 0b00000000
        
        if frequency == 15:
            pass
        elif frequency == 3:
            cra = (mask & 0b11100011) | 0b00001000
        elif frequency == 30:
            cra = (mask & 0b11100011) | 0b00010100
        elif frequency == 75:
            cra = (mask & 0b11100011) | 0b00011000
        else:
            print("[HMC5883 ERROR] Unavailable frequency value!")
            
        if averaging == 8:
            pass
        elif averaging == 4:
            cra = mask & 0b01011111
        elif averaging == 2:
            cra = mask & 0b00111111
        elif averaging == 1:
            cra = mask & 0b00011111
        else:
            print("[HMC5883 ERROR] Unavailable oversample rate!")
            
        if gain == 0:
            self.gain_div = 1370
        elif gain == 1:
            self.gain_div = 1090
            crb = crb | 0b00100000
        elif gain == 2:
            self.gain_div = 820
            crb = crb | 0b01000000
        elif gain == 3:
            self.gain_div = 660
            crb = crb | 0b01100000
        elif gain == 4:
            self.gain_div = 440
            crb = crb | 0b10000000
        elif gain == 5:
            self.gain_div = 390
            crb = crb | 0b10100000
        elif gain == 6:
            self.gain_div = 330
            crb = crb | 0b11000000
        elif gain == 7:
            self.gain_div = 230
            crb = crb | 0b11100000
        else:
            print("[HMC5883 ERROR] Unavailable oversample rate!")
            
        # frequenvy, sample averaging, measurement mode
        #self.bus.write_byte_data(self.address, HMC5883.CONFA, cra)
        # gain settings
        self.bus.write_byte_data(self.address, HMC5883.CONFB, crb)           
        # continuous measurement mode
        self.bus.write_byte_data(self.address, HMC5883.MODE_REG, 0x00)
    
        cntr = self.bus.read_byte_data(self.address, HMC5883.MODE_REG)
        
        if (cntr & 0b11) == 0:
            mode = "continuous"
        elif (cntr & 0b11) == 1:
            mode = "single measurement"
        else:
            mode = "standby"
        
        cntr = self.bus.read_byte_data(self.address, HMC5883.CONFA)
        
        if ((cntr & 0b11100) >> 2) == 0:
            freq = 0.75
        elif ((cntr & 0b11100) >> 2) == 1:
            freq = 1.5
        elif ((cntr & 0b11100) >> 2) == 2:
            freq = 3
        elif ((cntr & 0b11100) >> 2) == 3:
            freq = 7.5
        elif ((cntr & 0b11100) >> 2) == 4:
            freq = 15
        elif ((cntr & 0b11100) >> 2) == 5:
            freq = 30
        elif ((cntr & 0b11100) >> 2) == 6:
            freq = 75
        else:
            freq = -1
            
        print("HMC883 configuration:\nMode: {}\nFrequency: {}Hz\nID: {}".format(mode, freq, self.get_id()))
 
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
        
    def get_magneto_data(self, g_unit=False):
        """Returns the X, Y and Z values from the magnetometer"""
        # Read the raw data from the MPU-6050
        x = self.read_word(HMC5883.X_MSB)
        y = self.read_word(HMC5883.Y_MSB)
        z = self.read_word(HMC5883.Z_MSB)
        
        if g_unit:
            x /= self.gain_div
            y /= self.gain_div
            z /= self.gain_div
 
        return {'x': x, 'y': y, 'z': z}
    
    def is_data_available(self):
        status = self.bus.read_byte_data(self.address, HMC5883.STATUS_REG)
        return (status & 0x01)
    
    def get_id(self):
        id1 = self.bus.read_byte_data(self.address, HMC5883.ID_REG1)
        id2 = self.bus.read_byte_data(self.address, HMC5883.ID_REG2)
        id3 = self.bus.read_byte_data(self.address, HMC5883.ID_REG3)
        return chr(id1) + chr(id2) + chr(id3)
