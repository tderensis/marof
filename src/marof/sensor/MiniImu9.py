from math import atan2, sqrt, asin, cos, sin, pi
from LSM303DLHC import LSM303DLHC
from L3GD20 import L3GD20

class MiniImu9(object):
    """ A combined magnetometer and linear accelerometer (LSM303DLHC) with a gyroscope (L3GD20).
    Each chip also contains temperature sensors.
    
    :param debug: default False, print debug messages
    """
    
    _GYRO_ADDRESS = 0x6B
    _MAG_ADDRESS = 0x1E
    _ACC_ADDRESS = 0x19
    
    
    def __init__(self, debug=False):
        self.lsm303 = LSM303DLHC(self._MAG_ADDRESS, self._ACC_ADDRESS, debug)
        self.lsm303.enableTemperature(True)
        self.l3gd20 = L3GD20(self._GYRO_ADDRESS, debug)
    
    def readOrientation(self):
        """ Reads the magnetometer and calculates the roll, pitch, and magnetic heading. 
        
        :returns: a tuple (roll, pitch, heading) in degrees
        """
        (mx, my, mz) = self.readMagnetometer()
        (ax, ay, az) = self.readAccelerometer()
        atotal = sqrt(ax*ax + ay*ay + az*az)
        
        axNormalized = ax/atotal
        ayNormalized = ay/atotal
        pitch = asin(-axNormalized)
        roll = asin(ayNormalized/cos(pitch))
        mxn = mx * cos(pitch) + mz * sin(pitch);
        myn = mx * sin(roll) * sin(pitch) + my * cos(roll) - mz * sin(roll) * cos(pitch);
        heading = atan2(myn, mxn)*180.0/pi
        return (roll*180.0/pi, pitch*180.0/pi, heading)
    
    def readTemperature(self):
        """ Read the temperature. 
        
        :returns: temperature in Celsius
        """
        return self.lsm303.readTemperature() # the LSM303DLHC has higher temperature resolution
    
    def readMagnetometer(self):
        """ Read the magnetometer. 
        
        :returns: the magnetic field in each direction in Gauss as a tuple (mx, my, mz)
        """
        return self.lsm303.readMagnetometer()
    
    def readAccelerometer(self):
        """ Read the accelerometer. 
        
        :returns: the linear acceleration in G (1G = 9.8m/s) as a tuple (ax, ay, az)
        """
        return self.lsm303.readAccelerometer()

    def readGyroscope(self):
        """ Read the gyroscope. 
        
        :returns: the angular velocity about each axis in deg/s as a tuple (gx, gy, gz)
        """
        return self.l3gd20.readGyroscope()


import time
import unittest

class TestMiniImu9(unittest.TestCase):
    """ Unit tests for the MiniImu9 class. """
    
    def setUp(self):
        self.miniImu = MiniImu9(debug=True)

    def testMagnetometer(self):
        for _ in xrange(10):
            (mx, my, mz) = self.miniImu.readMagnetometer()
            mTotal = sqrt(mx*mx + my*my + mz*mz)
            print "mx:", mx, "my:", my, "mz:", mz, "mTotal:", mTotal, "Gauss"
            time.sleep(0.1)
            
    def testAccelerometer(self):
        for _ in xrange(10):
            (ax, ay, az) = self.miniImu.readAccelerometer()
            aTotal = sqrt(ax*ax + ay*ay + az*az)
            print "ax:", ax, "ay:", ay, "az:", az, "aTotal:", aTotal, "G"
            time.sleep(0.1)
            
    def testGyroscope(self):
        for _ in xrange(10):
            (gx, gy, gz) = self.miniImu.readGyroscope()
            gTotal = sqrt(gx*gx + gy*gy + gz*gz)
            print "gx:", gx, "gy:", gy, "gz:", gz, "gTotal:", gTotal, "deg/s"
            time.sleep(0.1)
    
    def testTemperature(self):
        for _ in xrange(20):
            temp = self.miniImu.readTemperature()
            print "temp:", temp, "C"
            time.sleep(0.1)
            
    def testOrientation(self):
        for _ in xrange(10):
            (roll, pitch, heading) = self.miniImu.readOrientation()
            print "roll:", roll, "pitch:", pitch, "heading:", heading
            time.sleep(0.1)
            
if __name__=="__main__":
    unittest.main()
