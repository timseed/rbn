from PyQt5 import QtCore, QtGui, QtWidgets
from rbn import *
import logging


class qtrbn(QtCore.QThread,rbn):
    """
    Same as the beacon class however this emits a signal called BEACON

    Note: This needs to inherit from 2 classes and the emit need to be of type QObject else it does not like to play
    """

    RBN = QtCore.pyqtSignal(list)
    def __init__(self):
         QtCore.QThread.__init__(self)
         self.logger = logging.getLogger(__name__)

    def process_line(self,line_of_data):
            """
            Send the Array via a QT Signal so other objects can pick it up
            Return the list
            :return:
            """
            self.logger.debug('in process_line')
            next_station = super(qtrbn,self).process_line(line_of_data)
            self.logger.debug("Emit RBN")
            self.RBN.emit(next_station)
            return next_station

    def loop(self,lines=10):
        """
        Get n posts from the RBN Network
        :param lines:
        :return:
        """
        self.logger.info("running loop")
        while lines>0:
            a=self._tn.read_until('ZZZ',1)
            if len(a)>0:
                self.logger.info("Got some data")
                #print(''+a,end='')
                self.process_line(a)
            else:
                self.logger.warning('No Data received')
            lines=lines-1

    def run(self):
            self.logger.debug("run called")
            while(1):
                self.loop(10)