from marof import getMicroSeconds
from marof.sensor import Sensor
from MiniImu9 import MiniImu9
from marof_lcm import orientation_t

class ImuDaemon(Sensor):
    def __init__(self, name, updateInterval, filt):
        super(ImuDaemon, self).__init__(name, updateInterval, filt)
        self._imu = MiniImu9(debug=True)
        self._roll = None
        self._pitch = None
        self._heading = None

    def sensorStep(self):
        (self._roll, self._pitch, self._heading) = self._imu.readOrientation()
        
    def publishUpdate(self):
        msg = orientation_t()
        msg.time = getMicroSeconds()
        msg.roll = self._roll
        msg.pitch = self._pitch
        msg.heading = self._heading
        self.publish(self.name+"_ORIENTATION", msg)

    @property
    def filterInput(self):
        return (self._roll, self._pitch, self._heading)

if __name__ == "__main__":
    imu = ImuDaemon(name="IMU", updateInterval=0.1, filt=None)
    imu.start()
