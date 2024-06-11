from mpu6050 import MPU6050
from hmc5883 import HMC5883
import time
import smbus
from py_qmc5883 import QMC5883L

#0x77 BMP pressure

mpu = MPU6050(0x68)
#hmc = HMC5883(0x1E)
#qmc = QMC5883L(i2c_bus=1, address=0x77)


#bus = smbus.SMBus(1)
#bus.pec = 1  # Enable PEC

#for i in range(13):
#    b = bus.read_byte_data(0x1E, i)
#    print(i, ": ", b)
#    time.sleep(1)
#bus.close()


while True:
    accel = mpu.get_accel_data()
    gyro = mpu.get_gyro_data()
    temperature = mpu.get_temperature()
    print("Accelerometer: x: {}, y: {}, z: {}".format(accel['x'], accel['y'], accel['z']))
    print("Gyroscope: x: {}, y: {}, z: {}".format(gyro['x'], gyro['y'], gyro['z']))
    print("Temperature: {:.2f}".format(temperature))
    
    '''
    if hmc.is_data_available():
        magnet = hmc.get_magneto_data()
        print("Magnetometer: x: {}, y: {}, z: {}".format(magnet['x'], magnet['y'], magnet['z']))
    '''
    
    print("##########################################\n")
    time.sleep(3)

