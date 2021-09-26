import sys
import cv2
import os
import numpy as np
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

class PainterWidget(QWidget):
    img_size =  320 # both width and height
    temp_file_name = "test.png"
    def __init__(self):
        super(PainterWidget, self).__init__()
        self.setFixedSize(self.img_size, self.img_size)
        self.tracing_xy = []
        self.lineHistory = []
        self.pen = QPen(Qt.black, 18, Qt.SolidLine)
        
        self.setAutoFillBackground(True)
        pal = self.palette()
        pal.setColor(QPalette.Background, QColor.fromRgb(222, 222, 222))
        self.setPalette(pal)

    def resizeEvent(self, QResizeEvent):
        size:QSize = QResizeEvent.size()
        if size.height() < size.width():
            cached_pixmap = size.height()
        else:
            pass

    def paintEvent(self, QPaintEvent):
        self.painter = QPainter()
        self.draw(self)

    def draw(self, dev):
        self.painter.begin(dev)
        self.painter.setPen(self.pen)

        start_x_temp = 0
        start_y_temp = 0

        if self.lineHistory:
            for line_n in range(len(self.lineHistory)):
                for point_n in range(1, len(self.lineHistory[line_n])):
                    start_x, start_y = self.lineHistory[line_n][point_n-1][0], self.lineHistory[line_n][point_n-1][1]
                    end_x, end_y = self.lineHistory[line_n][point_n][0], self.lineHistory[line_n][point_n][1]
                    self.painter.drawLine(start_x, start_y, end_x, end_y)

        for x, y in self.tracing_xy:
            if start_x_temp == 0 and start_y_temp == 0:
                self.painter.drawLine(self.start_xy[0][0], self.start_xy[0][1], x, y)
            else:
                self.painter.drawLine(start_x_temp, start_y_temp, x, y)

            start_x_temp = x
            start_y_temp = y

        self.painter.end()

    def mousePressEvent(self, QMouseEvent):
        self.start_xy = [(QMouseEvent.pos().x(), QMouseEvent.pos().y())]

    def mouseMoveEvent(self, QMouseEvent):
        self.tracing_xy.append((QMouseEvent.pos().x(), QMouseEvent.pos().y()))
        self.update()

    def mouseReleaseEvent(self, QMouseEvent):
        self.lineHistory.append(self.start_xy+self.tracing_xy)
        self.tracing_xy = []

    def clear_board(self):
        current_brush = self.painter.brush()
        self.painter.setBrush(self.painter.background())
        self.draw(self)
        self.painter.setBrush(current_brush)
        self.lineHistory = []
        self.tracing_xy = []

        self.update()

    def get_img(self):
        if len(self.lineHistory) < 1 and len(self.tracing_xy) < 1:
            return [False, "The drawing pad is empty"]
        num_img = QImage(self.img_size, self.img_size, QImage.Format_RGB32)
        num_img.fill(Qt.white)
        self.draw(num_img)
        num_img.save(self.temp_file_name)

        num_img_imp = cv2.imread(self.temp_file_name)
        os.remove(self.temp_file_name)
        
        num_img_imp = cv2.cvtColor(num_img_imp, cv2.COLOR_BGR2GRAY)
        num_img_imp = cv2.resize(num_img_imp, (28,28), interpolation = cv2.INTER_AREA)

        img_array = np.array(num_img_imp)
        img_array = img_array.flatten()
        img_lst = img_array.tolist()

        for i,s in enumerate(img_lst):
            img_lst[i] = 255 - s
        
        img_array = np.array(img_lst)
        return [True, img_array]
