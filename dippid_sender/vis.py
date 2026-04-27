import numpy as np
import pyqtgraph as pg
from pyqtgraph.Qt import QtCore # timer
import os


# plot it like its hot
class Plotter:
    def __init__(self, capability, y_range=(-2,2), buffer_size=500):

        self.buffer_size = buffer_size
        self.capability = capability        # added this to be able to manage plots independently for different capabilities

        # create plot item 
        self.plot = pg.PlotItem(title=capability)
        self.plot.setYRange(y_range[0], y_range[1])

        if capability == 'accelerometer':
            self.plot.addLegend(brush='k', offset=(10,10))
            self.x_data = np.zeros(buffer_size)
            self.y_data = np.zeros(buffer_size)
            self.z_data = np.zeros(buffer_size)
            self.lineplot_x = self.plot.plot(pen='r', name='X')
            self.lineplot_y = self.plot.plot(pen='g', name='Y')
            self.lineplot_z = self.plot.plot(pen='b', name='Z')
       
        elif capability == 'button_1':
            self.button_data = np.zeros(buffer_size)
            self.lineplot_btn = self.plot.plot(pen='y', name='Status')


    def update(self, data):
        if self.capability == 'accelerometer':
            # get rid of oldest data point
            self.x_data = np.roll(self.x_data, -1)
            self.y_data = np.roll(self.y_data, -1)
            self.z_data = np.roll(self.z_data, -1)

            # new data
            self.x_data[-1] = float(data['x'])
            self.y_data[-1] = float(data['y'])
            self.z_data[-1] = float(data['z'])

            # update plot
            self.lineplot_x.setData(self.x_data)
            self.lineplot_y.setData(self.y_data)
            self.lineplot_z.setData(self.z_data)

        elif self.capability == 'button_1':
            self.button_data = np.roll(self.button_data, -1)
            self.button_data[-1] = float(data)
            self.lineplot_btn.setData(self.button_data)


# is it a bird? is it a plane? no, its a window with plots!
class Visualizer:
    def __init__(self, sensor, update_freq=10, width=500, height=500):

        self.sensor = sensor

        # create application and main window
        self.app = pg.mkQApp() 
        self.win = pg.GraphicsLayoutWidget(title="DIPPID Visualizer")
        self.win.resize(width, height)
         
        self.plots = {
            'accelerometer': Plotter("accelerometer", (-3, 3)),
            'button_1': Plotter('button_1', (-0.5, 1.5))
        }
        
        # add plots to the main window
        for plot in self.plots.values():
            self.win.addItem(plot.plot)
            self.win.nextRow()
        
        # update data every whatever ms value in update_freq
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update)
        self.timer.start(update_freq)
        
        self.win.closeEvent = self.close_event
    

    def update(self):
        # get latest data from sensor and update plots:
        for capability, plot in self.plots.items():
            if self.sensor.has_capability(capability):
                plot.update(self.sensor.get_value(capability))


    def close_event(self, e):
        self.timer.stop()
        self.app.quit()
        os._exit(0)
    
    def run(self):
        self.win.show()
        self.app.exec()