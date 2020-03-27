# import time
# from matplotlib import pyplot as plt
# import numpy as np
#
# def live_update_demo(blit = True):
#     x = np.linspace(0,50., num=100)
#     X,Y = np.meshgrid(x,x)
#     fig = plt.figure()
#     ax2 = fig.add_subplot(2, 1, 2)
#
#     fig.canvas.draw()   # note that the first draw comes before setting data
#     h2, = ax2.plot(x, lw=3)
#     text = ax2.text(0.8,1.5, "")
#     ax2.set_ylim([-1,1])
#
#
#     if blit:
#         # cache the background
#         ax2background = fig.canvas.copy_from_bbox(ax2.bbox)
#
#     t_start = time.time()
#     k=0.
#     for i in np.arange(1000):
#         h2.set_ydata(np.sin(x/3.+k))
#         tx = 'Mean Frame Rate:\n {fps:.3f}FPS'.format(fps= ((i+1) / (time.time() - t_start)) )
#         text.set_text(tx) #print tx
#         k+=0.11
#         if blit:
#             # restore background
#             fig.canvas.restore_region(ax2background)
#
#             # redraw just the points
#             ax2.draw_artist(h2)
#
#             # fill in the axes rectangle
#             fig.canvas.blit(ax2.bbox)
#             # in this post http://bastibe.de/2013-05-30-speeding-up-matplotlib.html
#             # it is mentionned that blit causes strong memory leakage.
#             # however, I did not observe that.
#
#         else:
#             # redraw everything
#             fig.canvas.draw()
#             fig.canvas.flush_events()
#
#
#         plt.pause(0.000000000001)
#         #plt.pause calls canvas.draw(), as can be read here:
#         #http://bastibe.de/2013-05-30-speeding-up-matplotlib.html
#         #however with Qt4 (and TkAgg??) this is needed. It seems,using a different backend,
#         #one can avoid plt.pause() and gain even more speed.
#
# live_update_demo(True) # 28 fps
# #live_update_demo(False) # 18 fps

#######################################################################################################################
import sys
import time
from pyqtgraph.Qt import QtCore, QtGui
import numpy as np
import pyqtgraph as pg
import serial
import re

class ReadLine:
    def __init__(self, s):
        self.buf = bytearray()
        self.s = s

    def readline(self):
        i = self.buf.find(b"\n")
        if i >= 0:
            r = self.buf[:i+1]
            self.buf = self.buf[i+1:]
            return r
        while True:
            i = max(1, min(2048, self.s.in_waiting))
            data = self.s.read(i)
            i = data.find(b"\n")
            if i >= 0:
                r = self.buf + data[:i+1]
                self.buf[0:] = data[i+1:]
                return r
            else:
                self.buf.extend(data)

class App(QtGui.QMainWindow):
    def __init__(self, parent=None):
        super(App, self).__init__(parent)

        #### Create Gui Elements ###########
        self.mainbox = QtGui.QWidget()
        self.setCentralWidget(self.mainbox)
        self.mainbox.setLayout(QtGui.QVBoxLayout())

        self.canvas = pg.GraphicsLayoutWidget()
        self.mainbox.layout().addWidget(self.canvas)

        self.label = QtGui.QLabel()
        self.mainbox.layout().addWidget(self.label)

        self.view = self.canvas.addViewBox()
        self.view.setAspectLocked(True)
        self.view.setRange(QtCore.QRectF(0,0, 100, 100))

        #  image plot
        #self.img = pg.ImageItem(border='w')
        #self.view.addItem(self.img)

        self.canvas.nextRow()
        #  line plot
        self.otherplot = self.canvas.addPlot()
        self.h2 = self.otherplot.plot(pen='y')
        ### Fuck knows what I am doing
        self.arduinoData = serial.Serial('com3', 9600,timeout=None)  # Creating our serial object named arduinoData
        self.readSerialLine = ReadLine(self.arduinoData)
        #### Set Data  #####################

        self.x = np.linspace(0,50., num=100)
        self.X,self.Y = np.meshgrid(self.x,self.x)

        self.counter = 0
        self.fps = 0.
        self.lastupdate = time.time()
        self.ydata = np.zeros([100])
        #### Start  #####################
        self._update()

    def _update(self):
        while (self.arduinoData.inWaiting() == 0):  # Wait here until there is data
            pass  # do nothing
        arduinoString = self.readSerialLine.readline()  # read the line of text from the serial port
        arduinoString = str(arduinoString)
        dataArray = arduinoString.split(':')
        data = re.sub('[^0-9\.]', '', dataArray[-1])
        try:
            littleSignal = float(data)

            #self.ydata = np.sin(self.x/3.+ self.counter/9.)
            self.ydata = np.append(self.ydata,[littleSignal])
            if len(self.ydata) == 101:
                self.ydata = self.ydata[1:]
            #self.img.setImage(self.data)
            self.h2.setData(self.ydata)

            now = time.time()
            dt = (now-self.lastupdate)
            if dt <= 0:
                dt = 0.000000000001
            fps2 = 1.0 / dt
            self.lastupdate = now
            self.fps = self.fps  * 0.9 + fps2 * 0.1
            tx = 'Mean Frame Rate:  {fps:.3f} FPS'.format(fps=self.fps )
            self.label.setText(tx)

        except:
            pass
        QtCore.QTimer.singleShot(1, self._update)
        self.counter += 1


if __name__ == '__main__':


    app = QtGui.QApplication(sys.argv)
    thisapp = App()

    thisapp.show()
    sys.exit(app.exec_())
