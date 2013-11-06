Getting Started
---------------

The :py:class:`marof.MarofModule` and :py:class:`marof.MarofModuleHandler` allows you to quickly 
create modules that use LCM to communicate even over a network. To create your own module, 
you must extend the MarofModule class and the two abstract methods: step() and publishUpdate(). 
The step() method is where all of the main calculations happen and publishUpdate() is where the
LCM message is formed and published.

.. autoclass:: marof.MarofModule
			:members:
			:private-members:
			
The MarofModuleHandler handles all incoming messages for a module. The handler handles
general configuration messages to start, stop, pause, and resume the module. More subscriptions
can be can be added for messages to modify the module in other ways. To prevent the handler
from modifying the module in a non-thread-safe way the runLater(command) method in the
MarofModule can be called to add commands to a queue.

.. autoclass:: marof.MarofModuleHandler
			:members:
			:private-members:
			
A more specific type of module is a :py:class:`marof.sensor.Sensor`, which uses a filter. 
A sensor must override the filterInput property in addition to the sensorStep() and 
publishUpdate() functions.

.. autoclass:: marof.sensor.Sensor
			:members:
			:private-members:
			:noindex:
			
An example sensor::

	T = 1/100.0
	lpf = FirstOrderLpf(cutoff=0.05, samplingInterval=T)
	sensor = SensorExample(name="SENSOR_EXAMPLE", updateInterval=T, filt=lpf)
	handler = MarofModuleHandler(sensor)
	handler.subscribe("CONFIG_MY_SENSOR", sensor.handleMessage)
	handler.startModule() # start module on separate thread (optional, can also be started via LCM)
	handler.start() 

Full examples can be found in SensorExamples.py and HeadingPid.py.