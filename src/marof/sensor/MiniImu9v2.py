from numpy import array, mat, mean
from numpy.linalg import lstsq
from math import sqrt, sin, cos, radians, pi
import time
import unittest

from LSM303DLHC import LSM303DLHC
from L3GD20 import L3GD20

class MiniImu9v2(object):
    """ A combined magnetometer and linear accelerometer (LSM303DLHC) with a gyroscope (L3GD20).
    Each chip also contains temperature sensors.
    
    This class contains functions for returning raw sensor readings and calibrated readings.
    Use the calibration routines to get calibration matrices and pass them to this class.
    
    :todo: test calibration procedures. write the magnetometer calibration procedure
    :param debug: default False, print debug messages
    :param accMat: acceleration calibration matrix
    :param magMat: magnetometer calibration matrix
    :param gyroBias: gyroscope bias in each direction
    :param tempBias: temperature bias in Celsius
    """
    _GYRO_ADDRESS = 0x6B
    _MAG_ADDRESS = 0x1E
    _ACC_ADDRESS = 0x19
    
    
    def __init__(self, debug=False, accMat=None, magMat=None, gyroBias=None, tempBias=None):
        self.lsm303 = LSM303DLHC(self._MAG_ADDRESS, self._ACC_ADDRESS, debug)
        self.l3gd20 = L3GD20(self._GYRO_ADDRESS, debug)
        
        if accMat is None:
            self.accMat = mat(((1, 0, 0, 0),
                               (0, 1, 0, 0),
                               (0, 0, 1, 0),
                               (0, 0, 0, 0)))
        else:
            self.accMat = accMat
        
        if magMat is None:
            self.magMat = mat(((1, 0, 0, 0),
                               (0, 1, 0, 0),
                               (0, 0, 1, 0),
                               (0, 0, 0, 0)))
        else:
            self.magMat = magMat
        
        if gyroBias is None:
            self.gyroBias = (0, 0, 0)
        else:
            self.gyroBias = gyroBias
        
        if tempBias is None:
            self.tempBias = 0
        else:
            self.tempBias = tempBias
    
    def readTemperatureRaw(self):
        """ Read the temperature in Celsius without applying calibration. 
        
        :returns: temperature in Celsius
        """
        return self.lsm303.readTemperature() # the LSM303DLHC has higher temperature resolution
    
    def readMagnetometerRaw(self):
        """ Read the magnetometer without applying calibration.
        
        :returns: the magnetic field in each direction in Gauss as a tuple (mx, my, mz)
        """
        return self.lsm303.readMagnetometer()
    
    def readAccelerometerRaw(self):
        """ Read the accelerometer without applying calibration. 
        
        :returns: the linear acceleration in G (1G = 9.8m/s) as a tuple (ax, ay, az)
        """
        return self.lsm303.readAccelerometer()

    def readGyroscopeRaw(self):
        """ Read the gyroscope without applying calibration. 
        
        :returns: the angular velocity about each axis in deg/s as a tuple (gx, gy, gz)
        """
        return self.l3gd20.readGyroscope()

    def readTemperature(self):
        """ Get the calibrated temperature. 
        
        :returns: calibrated temperature in Celsius
        """
        return self.applyTempCalibration(self.readTemperatureRaw())
    
    def readMagnetometer(self):
        """ Get the calibrated magnetic field in each direction. 
        
        :returns: the calibrated magnetic field in each direction in Gauss as a tuple (mx, my, mz)
        """
        return self.applyMagCalibration(self.readMagnetometerRaw())
    
    def readAccelerometer(self):
        """ Get the calibrated linear acceleration in each direction.
        
        :returns: the calibrated linear acceleration in G (1G = 9.8m/s) as a tuple (ax, ay, az)
        """
        return self.applyAccCalibration(self.readAccelerometerRaw())

    def readGyroscope(self):
        """ Get the calibrated angular velocity about each axis.
        
        :returns: the angular velocity about each axis in deg/s as a tuple (gx, gy, gz)
        """
        return self.applyGyroCalibration(self.readGyroscopeRaw())
    
    def applyMagCalibration(self, raw):
        """ Apply the magnetometer calibration on the raw sensor reading.
        
        :param raw: the raw reading (mx, my, mz) in Gauss
        :returns: the calibrated reading (mxc, myc, mzc) in Gauss
        """
        raw = mat(raw + (1,))
        return map(tuple, array(raw*self.magMat))[0][0:3]
    
    def applyAccCalibration(self, raw):
        """ Apply the accelerometer calibration on the raw sensor reading.
        
        :param raw: the raw reading (ax, ay, az) in G
        :returns: the calibrated reading (axc, ayc, azc) in G
        """
        raw = mat(raw + (1,))
        return map(tuple, array(raw*self.accMat))[0][0:3]
    
    def applyGyroCalibration(self, raw):
        """ Apply the gyroscope calibration on the raw sensor reading.
        
        :param raw: the raw reading (gx, gy, gz) in deg/s
        :returns: the calibrated reading (gxc, gyc, gzc) in deg/s
        """
        return (raw[0]-self.gyroBias[0], raw[1]-self.gyroBias[1], raw[2]-self.gyroBias[2])
    
    def applyTempCalibration(self, raw):
        """ Apply the temperature calibration on the raw sensor reading.
        
        :param raw: the raw temperature reading in Celsius
        :returns: the calibrated temperature in Celsius
        """
        return raw - self.tempBias
    
    def averageReadings(self, func, num=50, T=0.1):
        l = []
        for _ in xrange(num):
            l.append(func())
            time.sleep(T)
        return mat(mean(l, axis=0))
    
    def calibrateAccelerometer(self):
        print "Starting the accelerometer calibration routine."
        print "This calibration will require you to place your accelerometer in various positions."
        print "Make sure you know what coordinate system you will be working in."
        custom = False
        i = raw_input("Use custom positions (y/N):")
        if i.lower() == "y" or i.lower() == "yes":
            custom = True
        print ""
        A = [] # raw readings
        B = [] # expected readings
        
        if custom:
            print "Using custom positions. You can use sin, cos, radians, pi, and sqrt."
            print "For example, if the Z_b axis is facing downwards, pitch is 30 degrees, and"
            print "roll is 0 degrees, then: Expected ax = -sin(radians(30)), Expected ay = 0, and"
            print "Expected az = cos(radians(30)) \n"
            done = False
            while not done:
                print "Enter the expected accelerations:"
                ax = None
                while ax is None:
                    eval("ax =" + raw_input("Expected ax = "))
                ay = None
                while ay is None:
                    eval("ay =" + raw_input("Expected ay = "))
                az = None
                while az is None:
                    eval("az =" + raw_input("Expected az = "))
                
                totalA = sqrt(ax*ax + ay*ay + az*az)
                if totalA < 0.99 or totalA > 1.01:
                    print "Expected acceleration should have a magnitude of 1."
                    continue
                else:
                    print "Hold..."
                    A.append(self.averageReadings(self.readAccelerometerRaw).append(1))
                    B.append((ax,ay,az))
                    
                i = raw_input("Done? (y/N):")
                if i.lower() == "y" or i.lower() == "yes":
                    done = True
        else:
            raw_input("Place the Z_b axis pointing down and press Enter...")
            print "Hold..."
            A.append(self.averageReadings(self.readAccelerometerRaw).append(1))
            B.append((0,0,1))
            print "Done"
            
            raw_input("Place the Z_b axis pointing up and press Enter...")
            print "Hold..."
            A.append(self.averageReadings(self.readAccelerometerRaw).append(1))
            B.append((0,0,-1))
            print "Done"
            
            raw_input("Place the Y_b axis pointing down and press Enter...")
            print "Hold..."
            A.append(self.averageReadings(self.readAccelerometerRaw).append(1))
            B.append((0,1,0))
            print "Done"
            
            raw_input("Place the Y_b axis pointing up and press Enter...")
            print "Hold..."
            A.append(self.averageReadings(self.readAccelerometerRaw).append(1))
            B.append((0,-1,0))
            print "Done"
            
            raw_input("Place the X_b axis pointing down and press Enter...")
            print "Hold..."
            A.append(self.averageReadings(self.readAccelerometerRaw).append(1))
            B.append((1,0,0))
            print "Done"
            
            raw_input("Place the X_b axis pointing up and press Enter...")
            print "Hold..."
            A.append(self.averageReadings(self.readAccelerometerRaw).append(1))
            B.append((-1,0,0))
            print "Done"
        
        print "\nThe calibration matrix is:"
        print lstsq(mat(A), mat(B))[0]
        
        print "To finalize the calibration add this matrix to a configuration file."
        
    def calibrateGyroscope(self):
        print "Starting the gyroscope calibration routine."
        print "This will remove the static bias from the sensor."
        
        print ""
        raw_input("Place the gyroscope in a static position and press Enter.")
        print "Hold..."
        print "(gx, gy, gz):", self.averageReadings(self.readGyroscopeRaw, num=200, T=1/40.0)

        print "To finalize the calibration add this matrix to a configuration file."

    def calibrateMagnetometer(self):
        print "Starting the magnetometer calibration routine."
        
        

class TestMiniImu9v2(unittest.TestCase):
    """ Unit tests for the MiniImu9 class. """
    
    def setUp(self):
        self.miniImu = MiniImu9v2(debug=True)

    def testMagnetometer(self):
        for _ in xrange(10):
            raw = (mx, my, mz) = self.miniImu.readMagnetometerRaw()
            mTotal = sqrt(mx*mx + my*my + mz*mz)
            print "mx:", mx, "my:", my, "mz:", mz, "mTotal:", mTotal, "Gauss"
            
            (mx, my, mz) = self.miniImu.applyMagCalibration(raw)
            mTotal = sqrt(mx*mx + my*my + mz*mz)
            print "Calibrated: mx:", mx, "my:", my, "mz:", mz, "mTotal:", mTotal, "Gauss"
            time.sleep(0.1)
            
    def testAccelerometer(self):
        for _ in xrange(10):
            raw = self.miniImu.readAccelerometer()
            (ax, ay, az) = raw
            aTotal = sqrt(ax*ax + ay*ay + az*az)
            print "ax:", ax, "ay:", ay, "az:", az, "aTotal:", aTotal, "G"
            
            (ax, ay, az) = self.miniImu.applyAccCalibration(raw)
            aTotal = sqrt(ax*ax + ay*ay + az*az)
            print "Calibrated: ax:", ax, "ay:", ay, "az:", az, "aTotal:", aTotal, "G"
            time.sleep(0.1)
            
    def testGyroscope(self):
        for _ in xrange(10):
            raw = (gx, gy, gz) = self.miniImu.readGyroscope()
            gTotal = sqrt(gx*gx + gy*gy + gz*gz)
            print "gx:", gx, "gy:", gy, "gz:", gz, "gTotal:", gTotal, "deg/s"
            
            (gx, gy, gz) = self.miniImu.applyGyroCalibration(raw)
            gTotal = sqrt(gx*gx + gy*gy + gz*gz)
            print "gx:", gx, "gy:", gy, "gz:", gz, "gTotal:", gTotal, "deg/s"
            time.sleep(0.1)
    
    def testTemperature(self):
        for _ in xrange(20):
            temp = self.miniImu.readTemperature()
            print "temp:", temp, "C"
            time.sleep(0.1)

            
if __name__=="__main__":
    suite = unittest.TestLoader().loadTestsFromTestCase(TestMiniImu9v2)
    unittest.TextTestRunner(verbosity=2).run(suite)
    
