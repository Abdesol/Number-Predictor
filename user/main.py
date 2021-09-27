from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PainterWidget import PainterWidget
import numpy as np
import time
import requests
import json

server_addr = "the_addr/predict/"

class PredictionProcessor(QObject):
    predicted = pyqtSignal(list)
    finished = pyqtSignal()

    @pyqtSlot()
    def run(self, array:np.ndarray):
        try:
            req_dict = {"array":array.tolist()}
            req = requests.post(server_addr, data=json.dumps(req_dict))
            response = req.json()

            if response["Error"]:
                ret = [False, response["Message"]]
            else:
                ret = [True, response["Prediction"]]
        except:
            ret = [False, "Error occurred!"]

        self.predicted.emit(ret)
        self.finished.emit()
        

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setWindowTitle("Number Recognizer")
        self.setFixedSize(400, 460)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.vertical_layout = QVBoxLayout()
        self.vertical_layout.setAlignment(Qt.AlignHCenter)
        self.central_widget.setLayout(self.vertical_layout)

        self.painter_widget = PainterWidget()
        self.vertical_layout.addWidget(self.painter_widget)

        self.label = QLabel()
        self.label.setText("Type any number above")
        self.label.setStyleSheet(f"font-size: 20px;padding:15px")
        self.vertical_layout.addWidget(self.label)
        self.label.setAlignment(Qt.AlignBottom)

        self.btns_layout = QHBoxLayout()
        self.vertical_layout.addLayout(self.btns_layout)

        self.predict_btn = QPushButton()
        self.predict_btn.setFixedSize(120,50)
        self.predict_btn.setText("Predict")
        self.predict_btn.setStyleSheet(f"font-size: 16px")
        self.btns_layout.addWidget(self.predict_btn)

        self.clear_btn = QPushButton()
        self.clear_btn.setFixedSize(120,50)
        self.clear_btn.setText("Clear")
        self.clear_btn.setStyleSheet(f"font-size: 16px")
        self.btns_layout.addWidget(self.clear_btn)

        self.predict_btn.clicked.connect(self.recognizer_clicked)
        self.clear_btn.clicked.connect(self.clear_clicked)

    def recognizer_clicked(self):
        self.predict_btn.setEnabled(False)
        self.label.setText("Waiting ...")
        self.label.repaint()
        get_req = self.painter_widget.get_img()

        if not get_req[0]:
            self.label.setText(get_req[1])
            self.label.repaint()
            self.predict_btn.setEnabled(True)
        else:
            img_array = get_req[1]

            self.predict_obj = PredictionProcessor()
            self.prediction_thread = QThread()

            self.predict_obj.predicted.connect(self.image_predicted)
            self.predict_obj.moveToThread(self.prediction_thread)
            self.predict_obj.finished.connect(self.prediction_thread.quit)
            self.prediction_thread.started.connect(lambda: self.predict_obj.run(img_array))
            self.prediction_thread.start()

    def image_predicted(self, ret):
        if not ret[0]: 
            text = ret[1]
        else:
            text = f"The number is {ret[1]}"

        self.label.setText(text)
        self.label.repaint()
        self.predict_btn.setEnabled(True)

    def clear_clicked(self):
        self.painter_widget.clear_board()



if __name__ == '__main__':
    import sys
    app = QApplication([])
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())