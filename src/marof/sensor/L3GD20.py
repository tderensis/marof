from Adafruit_I2C import Adafruit_I2C
import struct

class L3GD20(object):
    """ A gyro
    
    :param gyroAddr: the address of the gyro
    """
    
    def __init__(self, gyroAddr, debug=False):
        # init gyro
        self.gyroAddr = gyroAddr
        self.gyroEnabled = True
        self.gyro = Adafruit_I2C(gyroAddr, debug)
        self.enableGyro(self.gyroEnabled)
        
    def enableGyro(self, enable):
        """ Enable or disable the magnetometer. 
        
        :param enable: If True, enable the magnetometer in continuous-conversion mode.
                       If False, put the magnetometer in sleep mode.
        """
        if enable:
            self.magnetometer.write8(self._MAG_MR_REG_M, 0x00) # continuous-conversion mode
        else:
            self.magnetometer.write8(self._MAG_MR_REG_M, 0x02) # sleep mode
        self.gyroEnabled = enable
        
    def readGyrometer(self):
        """ Read the magnetometer and return Gauss in each directon as a tuple. 
        
        :returns: (x, y, z) in Gauss
        """
        # Data pointer is updated automatically after reading each byte from the magnetometer
        data = self.magnetometer.readList(self._MAG_OUT_X_H_M, 6)

        # Convert to 2s complement and convert to Gauss
        x = struct.unpack('h', struct.pack('BB', data[0], data[1]))[0]/self._lsbPerGauss
        z = struct.unpack('h', struct.pack("BB", data[2], data[3]))[0]/self._lsbPerGauss
        y = struct.unpack('h', struct.pack('BB', data[4], data[5]))[0]/self._lsbPerGauss
        return (x, y, z)
    