
from marof import MarofModule, MarofModuleHandler

from marof_lcm import configModule_t

class SensorExample(MarofModule):
    """ An example sensor to show an example implementation. """
    
    def __init__(self, name, updateInterval):
        super(SensorExample, self).__init__(name, updateInterval)
    
    def publishUpdate(self):
        print "Publishing update..."
        return
        
    def step(self):
        print "Doing sensor step..."
        return
        
    def handleMessage(self, channel, data):
        print "Got data on channel:", channel
        print "Data:", data
        

if __name__ == "__main__":
    sensor = SensorExample(name="SENSOR_EXAMPLE", updateInterval=0.1)
    handler = MarofModuleHandler(sensor)
    handler.subscribe("CONFIG_MY_SENSOR", sensor.handleMessage)
    handler.start()
    sensor.start()