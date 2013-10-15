"""
Code adapted from Eli Bendersky (eliben@gmail.com)
"""
import sys, select, signal, threading, time
from PyQt4.QtCore import SIGNAL, Qt
from PyQt4.QtGui import (QApplication, QMainWindow, QMessageBox, QFileDialog, QWidget, QLineEdit,
                         QPushButton, QCheckBox, QLabel, QSlider, QHBoxLayout, QVBoxLayout, QAction,
                         QIcon, QSizePolicy)

from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QTAgg
from matplotlib.figure import Figure

import lcm
from marof_lcm import * # Import everything so that we can decode any type

class PlotLcm(QMainWindow):
    """ A class to plot an LCM type over time. """
    
    def __init__(self, parent=None):
        QMainWindow.__init__(self, parent)
        self.setWindowTitle('LCM Plotter')

        self.createMenu()
        self.createMainFrame()
        
        # Each channel has data and axis associated with it. 
        # Dictionary key is the channel name and property.
        self.data = {}
        self.axes = {}
        self.lastPlot = None
        
        # Stop the program if CTRL-C is received
        self._stopEvent = threading.Event()
        signal.signal(signal.SIGINT, self.handleSigint)
        
        self._lcm = lcm.LCM()
        self.handlerThread = threading.Thread(target=self.pollLcm)
        self.handlerThread.setDaemon(True)
        self.handlerThread.start()
        
        self.connect(self, SIGNAL('redraw()'), self.on_draw)
        self.drawingThread = threading.Thread(target=self.drawLoop)
        self.drawingThread.setDaemon(True)
        self.drawingThread.start()
        
    def _cleanup(self):
        self._stopEvent.set()
        #self.handlerThread.join()
        #self.drawingThread.join()
        
    def handleSigint(self, *args):
        self._cleanup()
        QApplication.quit()
        
    def pollLcm(self):
        while not self._stopEvent.isSet():
            rc = select.select([self._lcm.fileno()], [], [self._lcm.fileno()], 0.05)
            if len(rc[0]) > 0 or len(rc[2]) > 0:
                self._lcm.handle()
            
    def drawLoop(self):
        while not self._stopEvent.isSet():
            self.emit(SIGNAL("redraw()"))
            time.sleep(0.5)
            
    def handleMessage(self, channel, msg):
        for (lcmChannel, lcmType, lcmProperty) in self.data.keys():
            if lcmChannel == channel:
                data = eval(lcmType + ".decode(msg)." + lcmProperty)
                self.data[(lcmChannel, lcmType, lcmProperty)].append(data)
        
    def save_plot(self):
        file_choices = "PNG (*.png)|*.png"
        
        path = unicode(QFileDialog.getSaveFileName(self, 
                        'Save file', '', 
                        file_choices))
        if path:
            self.canvas.print_figure(path, dpi=self.dpi)
            self.statusBar().showMessage('Saved to %s' % path, 2000)
    
    def on_about(self):
        msg = """ Plot an LCM message
        """
        QMessageBox.about(self, "About the demo", msg.strip())
    
    def on_draw(self):
        """ Redraws the figure
        """
        for (channel, lcmType, lcmProperty) in self.axes.keys():
            axis = self.axes[(channel, lcmType, lcmProperty)]
            axis.clear()
            axis.grid(self.gridCheckBox.isChecked())
            axis.plot(self.data[(channel, lcmType, lcmProperty)])
            axis.set_title(channel + ": " + lcmProperty)
            
        self.canvas.draw()
    
    def addPlot(self):
        channel = str(self.channelTextbox.text()).strip()
        lcmType = str(self.typeTextbox.text()).strip()
        lcmProperty = str(self.propertyTextbox.text()).strip()
        
        if not self.checkInputs(channel, lcmType, lcmProperty):
            return
        
        self.data[(channel, lcmType, lcmProperty)] = []
        n = len(self.data)
        i = 0
        self.fig.clear() # Clear the old plot first
        for key in self.data.keys():
            i = i + 1
            self.axes[key] = self.fig.add_subplot(n, 1, i)
        
        self.lastPlot = (channel, lcmType, lcmProperty)
        self._lcm.subscribe(channel, self.handleMessage)
        
    def mergePlot(self):
        channel = str(self.channelTextbox.text()).strip()
        lcmType = str(self.typeTextbox.text()).strip()
        lcmProperty = str(self.propertyTextbox.text()).strip()
        
        if not self.checkInputs(channel, lcmType, lcmProperty):
            return
        
        # Add data to last plot  
    
    def checkInputs(self, channel, lcmType, lcmProperty):
        # Error checking cause nobody is perfect...
        if channel == "":
            print "Warning: No channel given"
            return False
        
        try:
            __import__("marof_lcm." + lcmType)
        except ImportError:
            print "Warning: The LCM type is not in scope"
            return False
        else:
            try:
                eval("getattr(" + lcmType + ", lcmProperty)")
            except Exception:
                print "Warning: The LCM property for this type does not exist"
                return False
        
        # Clear the data and don't create a new axis if there is already data for this        
        if self.data.has_key((channel, lcmType, lcmProperty)):
            print "This data already exists:", channel
            self.data[(channel, lcmType, lcmProperty)] = []
            return False
        
        return True
    
    def createMainFrame(self):
        self.mainFrame = QWidget()
        
        self.dpi = 72
        self.fig = Figure((5.0, 2.5), dpi=self.dpi, tight_layout=True)
        self.canvas = FigureCanvasQTAgg(self.fig)
        self.canvas.setParent(self.mainFrame)
        self.canvas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        self.mpl_toolbar = NavigationToolbar2QTAgg(self.canvas, self.mainFrame)
        
        # Other GUI controls
        # 
        self.channelTextbox = QLineEdit()
        self.channelTextbox.setMinimumWidth(100)
        self.typeTextbox = QLineEdit()
        self.typeTextbox.setMinimumWidth(100)
        self.propertyTextbox = QLineEdit()
        self.propertyTextbox.setMinimumWidth(100)
        #self.connect(self.textbox, SIGNAL('editingFinished ()'), self.on_draw)
        
        self.addPlotButton = QPushButton("Add Plot")
        self.connect(self.addPlotButton, SIGNAL('clicked()'), self.addPlot)
        
        self.mergePlotButton = QPushButton("Merge Plot")
        self.connect(self.mergePlotButton, SIGNAL('clicked()'), self.mergePlot)
        
        self.gridCheckBox = QCheckBox("Show Grid")
        self.gridCheckBox.setChecked(False)
        self.connect(self.gridCheckBox, SIGNAL('stateChanged(int)'), self.on_draw)
        
        slider_label = QLabel('Bar width (%):')
        self.slider = QSlider(Qt.Horizontal)
        self.slider.setRange(1, 100)
        self.slider.setValue(20)
        self.slider.setTracking(True)
        self.slider.setTickPosition(QSlider.TicksBothSides)
        self.connect(self.slider, SIGNAL('valueChanged(int)'), self.on_draw)
        
        #
        # Layout with box sizers
        # 
        hbox = QHBoxLayout()
        
        for w in [self.channelTextbox, self.typeTextbox, self.propertyTextbox, 
                  self.addPlotButton, self.mergePlotButton, self.gridCheckBox, 
                  slider_label, self.slider]:
            hbox.addWidget(w)
            hbox.setAlignment(w, Qt.AlignVCenter)
        
        vbox = QVBoxLayout()
        vbox.addWidget(self.canvas)
        vbox.addWidget(self.mpl_toolbar)
        vbox.addLayout(hbox)
        
        self.mainFrame.setLayout(vbox)
        self.setCentralWidget(self.mainFrame)
        
    def createMenu(self):
        
        # File menu        
        fileMenu = self.menuBar().addMenu("File")
        
        saveMenuItem = self.create_action("&Save plot",
            shortcut="Ctrl+S", slot=self.save_plot, 
            tip="Save the plot")
        
        quitAction = self.create_action("&Quit", slot=self.close, 
            shortcut="Ctrl+Q", tip="Close the application")
        
        self.add_actions(fileMenu, 
            (saveMenuItem, None, quitAction))
        
        # Help menu
        helpMenu = self.menuBar().addMenu("Help")
        aboutAction = self.create_action("&About", 
            shortcut='F1', slot=self.on_about, 
            tip='About the demo')
        
        self.add_actions(helpMenu, (aboutAction,))

    def add_actions(self, target, actions):
        for action in actions:
            if action is None:
                target.addSeparator()
            else:
                target.addAction(action)

    def create_action(  self, text, slot=None, shortcut=None, 
                        icon=None, tip=None, checkable=False, 
                        signal="triggered()"):
        action = QAction(text, self)
        if icon is not None:
            action.setIcon(QIcon(":/%s.png" % icon))
        if shortcut is not None:
            action.setShortcut(shortcut)
        if tip is not None:
            action.setToolTip(tip)
            action.setStatusTip(tip)
        if slot is not None:
            self.connect(action, SIGNAL(signal), slot)
        if checkable:
            action.setCheckable(True)
        return action

    def closeEvent(self, event):
        self._cleanup() # stop the drawing thread before exiting
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    form = PlotLcm()
    form.show()
    sys.exit(app.exec_())
    