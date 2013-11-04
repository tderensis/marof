from math import sin, cos, sqrt, asin, atan2, degrees
from marof import getMicroSeconds
from marof.sensor import Sensor, MiniImu9v2
from marof_lcm import magnetometer_t, accelerometer_t, gyroscope_t, orientation_t

class ImuDaemon(Sensor):
    """ A sensor daemon to read the IMU and publish the results over LCM. """
    
    def __init__(self, name, updateInterval, filt):
        super(ImuDaemon, self).__init__(name, updateInterval, filt)
        self._imu = MiniImu9v2(debug=True)
        (_mx, _my, _mz, _ax, _ay, _az, _gx, _gy, _gz) = (None,)*9

    def sensorStep(self):
        (self._mx, self._my, self._mz) = self._imu.readMagnetometer()
        (self._ax, self._ay, self._az) = self._imu.readAccelerometer()
        (self._gx, self._gy, self._gz) = self._imu.readGyroscope()
        
    def publishUpdate(self):
        now = getMicroSeconds()
        
        msg = magnetometer_t()
        (msg.time, msg.mx, msg.my, msg.mz) = (now, self._mx, self._my, self.mz)
        self.publish("MAGNETOMETER", msg)
        
        msg = accelerometer_t()
        (msg.time, msg.ax, msg.ay, msg.az) = (now, self._ax, self._ay, self.az)
        self.publish("ACCELEROMETER", msg)
        
        msg = gyroscope_t()
        (msg.time, msg.gx, msg.gy, msg.gz) = (now, self._gx, self._gy, self.gz)
        self.publish("GYROSCOPE", msg)
        
        msg = orientation_t()
        msg.time = now
        (msg.roll, msg.pitch, msg.heading) = self.magAcc2Orientation(self._mx, self._my, self._mz, 
                                                                     self._ax, self._ay, self._az)
        self.publish("ORIENTATION", msg)

    @property
    def filterInput(self):
        return None # Not used right now
    
    def magAcc2Orientation(self, mx, my, mz, ax, ay, az):
        """ Convert magnetic field and acceleration into orientation.
        
        :returns: a tuple (roll, pitch, heading) in degrees
        """
        atotal = sqrt(ax*ax + ay*ay + az*az)
        axNormalized = ax/atotal
        ayNormalized = ay/atotal
        
        pitch = asin(-axNormalized)
        roll = asin(ayNormalized/cos(pitch))
        
        mxn = mx * cos(pitch) + mz * sin(pitch);
        myn = mx * sin(roll) * sin(pitch) + my * cos(roll) - mz * sin(roll) * cos(pitch);
        heading = degrees(atan2(myn, mxn)) % 360
        return (degrees(roll), degrees(pitch), heading)


if __name__ == "__main__":
    imu = ImuDaemon(name="IMU", updateInterval=0.05, filt=None)
    imu.start()
