from math import atan2, sqrt, asin, cos, sin, pi
from LSM303DLHC import LSM303DLHC
from L3GD20 import L3GD20

class MiniImu9(object):
    _GYRO_ADDRESS = 0x6B
    _MAG_ADDRESS = 0x1E
    _ACC_ADDRESS = 0x19
    
    _L3G_CTRL_REG1 = 0x20
    def __init__(self, debug=True):
        self.lsm303 = LSM303DLHC(self._MAG_ADDRESS, self._ACC_ADDRESS, debug)
        self.l3gd20 = L3GD20(self._GYRO_ADDRESS)
    
    def readOrientation(self):
        """ Reads the magnetometer and calculates the roll, pitch, and magnetic heading. """
        (mx, my, mz) = self.readMagnetometer()
        (ax, ay, az) = self.readAccelerometer()
        atotal = sqrt(ax*ax + ay*ay + az*az)
        
        axNormalized = ax/atotal
        ayNormalized = ay/atotal
        pitch = asin(-axNormalized)
        roll = asin(ayNormalized/cos(pitch))
        mxn = mx*cos(pitch)+mz*sin(pitch);
        myn = mx *sin(roll)*sin(pitch)+my*cos(roll)-mz*sin(roll)*cos(pitch);
        heading = atan2(myn, mxn)*180.0/pi
        return (roll*180.0/pi, pitch*180.0/pi, heading)
    
    def readGyro(self):
        return self.l3gd20.readGyrometer()
    
    def readMagnetometer(self):
        return self.lsm303.readMagnetometer()
    
    def readAccelerometer(self):
        return self.lsm303.readAccelerometer()

import time

if __name__=="__main__":
    mi = MiniImu9()
    while True:
        print "Magnetometer:", mi.readMagnetometer()
        print "Acceleromenter:", mi.readAccelerometer()
        print "Orientation:", mi.readOrientation()
        time.sleep(0.2)

