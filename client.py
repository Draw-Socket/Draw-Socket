## CLIENT ##
import sys
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import socket
from _thread import *

HOST = '172.30.1.62' ## server에 출력되는 ip를 입력해주세요 ##
PORT = 9999

QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
 
class CWidget(QWidget): 
 
    def __init__(self, socket):
 
        super().__init__()

        self.socket = socket
 
        # 전체 폼 박스
        formbox = QHBoxLayout()
        self.setLayout(formbox)
 
        # 좌, 우 레이아웃박스
        left = QVBoxLayout()
        right = QVBoxLayout()
 
        # 그룹박스1 생성 및 좌 레이아웃 배치
        gb = QGroupBox('그리기 종류')        
        left.addWidget(gb)
 
        # 그룹박스1 에서 사용할 레이아웃
        box = QVBoxLayout()
        gb.setLayout(box)        
 
        # 그룹박스 1 의 라디오 버튼 배치
        text = ['line', 'Curve', 'Rectange', 'Ellipse']
        self.radiobtns = []
 
        for i in range(len(text)):
            self.radiobtns.append(QRadioButton(text[i], self))
            self.radiobtns[i].clicked.connect(self.radioClicked)
            box.addWidget(self.radiobtns[i])
 
        self.radiobtns[0].setChecked(True)
        self.drawType = 0
         
        # 그룹박스2
        gb = QGroupBox('펜 설정')        
        left.addWidget(gb)        
 
        grid = QGridLayout()      
        gb.setLayout(grid)        
 
        label = QLabel('선굵기')
        grid.addWidget(label, 0, 0)
 
        self.combo = QComboBox()
        grid.addWidget(self.combo, 0, 1)       
 
        for i in range(1, 21):
            self.combo.addItem(str(i))
 
        label = QLabel('선색상')
        grid.addWidget(label, 1,0)        
         
        self.pencolor = QColor(0,0,0)
        self.penbtn = QPushButton()        
        self.penbtn.setStyleSheet('background-color: rgb(0,0,0)')
        self.penbtn.clicked.connect(self.showColorDlg)
        grid.addWidget(self.penbtn,1, 1)
         
 
        # 그룹박스3
        gb = QGroupBox('붓 설정')        
        left.addWidget(gb)
 
        hbox = QHBoxLayout()
        gb.setLayout(hbox)
 
        label = QLabel('붓색상')
        hbox.addWidget(label)                
 
        self.brushcolor = QColor(0,0,0)
        self.brushbtn = QPushButton()        
        self.brushbtn.setStyleSheet('background-color: rgb(255,255,255)')
        self.brushbtn.clicked.connect(self.showColorDlg)
        hbox.addWidget(self.brushbtn)
 
        # 그룹박스4
        gb = QGroupBox('지우개')        
        left.addWidget(gb)
 
        hbox = QGridLayout()
        gb.setLayout(hbox)        
         
        self.checkbox  =QCheckBox('지우개 동작')
        self.checkbox.stateChanged.connect(self.checkClicked)
        hbox.addWidget(self.checkbox, 0, 0)

        self.comboE = QComboBox()
        hbox.addWidget(self.comboE, 0, 1)       
 
        for i in range(1, 21):
            self.comboE.addItem(str(i))
       
        left.addStretch(1)        
          
        # 우 레이아웃 박스에 그래픽 뷰 추가
        self.view = CView(self, socket)       
        right.addWidget(self.view)        
 
        # 전체 폼박스에 좌우 박스 배치
        formbox.addLayout(left)
        formbox.addLayout(right)
 
        formbox.setStretchFactor(left, 0)
        formbox.setStretchFactor(right, 1)
         
        self.setGeometry(100, 100, 800, 500) 
         
    def radioClicked(self):
        for i in range(len(self.radiobtns)):
            if self.radiobtns[i].isChecked():
                self.drawType = i                
                break
 
    def checkClicked(self):
        pass
             
    def showColorDlg(self):       
         
        # 색상 대화상자 생성      
        color = QColorDialog.getColor()
 
        sender = self.sender()
 
        # 색상이 유효한 값이면 참, QFrame에 색 적용
        if sender == self.penbtn and color.isValid():           
            self.pencolor = color
            self.penbtn.setStyleSheet('background-color: {}'.format( color.name()))
        else:
            self.brushcolor = color
            self.brushbtn.setStyleSheet('background-color: {}'.format( color.name()))
 
 
         
# QGraphicsView display QGraphicsScene
class CView(QGraphicsView):
    
    def __init__(self, parent, socket):
 
        super().__init__(parent)       
        self.socket = socket
        start_new_thread(self.server_message, (client_socket,))

        self.scene = QGraphicsScene()        
        self.setScene(self.scene)
 
        self.items = []
         
        self.start = QPointF()
        self.end = QPointF()
 
        self.setRenderHint(QPainter.HighQualityAntialiasing)

    def server_message(self, client_socket):
        while True:
            data = client_socket.recv(1024)
            data = str(data.decode())
            print("recive : ", data)

            data = data.split()

                
            if(data[0] == "0"):
                sx = int(data[1])
                sy = int(data[2])
                ex = int(data[3])
                ey = int(data[4])
                line = QLineF(sx, sy, ex, ey)
                pen = QPen(QColor(int(data[5]),int(data[6]),int(data[7])), int(data[8]))
                self.scene.addLine(line, pen)
            elif(data[0] == "1"):
                pen = QPen(QColor(int(data[5]),int(data[6]),int(data[7])), int(data[8]))
                # Path 이용
                path = QPainterPath()
                path.moveTo(QPointF(int(data[1]), int(data[2])))
                path.lineTo(QPointF(int(data[3]), int(data[4])))
                self.scene.addPath(path, pen)
                
            elif(data[0] == "2"):
                brush = QBrush(QColor(int(data[5]),int(data[6]),int(data[7])))
                rect = QRectF(QPointF(int(data[1]), int(data[2])), QPointF(int(data[3]), int(data[4])))
                cPen = QPen(brush.color(), 1)
                self.scene.addRect(rect, cPen, brush)
            
            elif(data[0] == "3"):
                brush = QBrush(QColor(int(data[5]),int(data[6]),int(data[7])))
                rect = QRectF(QPointF(int(data[1]), int(data[2])), QPointF(int(data[3]), int(data[4])))
                rPen = QPen(brush.color(), 1)
                self.scene.addEllipse(rect, rPen, brush)
    

    
    def moveEvent(self, e):
        rect = QRectF(self.rect())
        rect.adjust(0,0,-2,-2)
 
        self.scene.setSceneRect(rect)
 
    def mousePressEvent(self, e):
 
        if e.button() == Qt.LeftButton:
            # 시작점 저장
            self.start = e.pos()
            self.end = e.pos()        
 
    def mouseMoveEvent(self, e):  
         
        if e.buttons() & Qt.LeftButton:           
 
            self.end = e.pos()
 
            if self.parent().checkbox.isChecked():
                pen = QPen(QColor(255,255,255), self.parent().comboE.currentIndex())
                path = QPainterPath()
                path.moveTo(self.start)
                path.lineTo(self.end)
                self.scene.addPath(path, pen)
                self.start = e.pos()
                return None
 
            pen = QPen(self.parent().pencolor, self.parent().combo.currentIndex())
 
            # 직선 그리기
            if self.parent().drawType == 0:
                 
                # 장면에 그려진 이전 선을 제거            
                if len(self.items) > 0:
                    self.scene.removeItem(self.items[-1])
                    del(self.items[-1])                
 
                # 현재 선 추가
                line = QLineF(self.start.x(), self.start.y(), self.end.x(), self.end.y())                
                self.items.append(self.scene.addLine(line, pen))

                
 
            # 곡선 그리기
            if self.parent().drawType == 1:

                # Path 이용
                path = QPainterPath()
                path.moveTo(self.start)
                path.lineTo(self.end)
                self.scene.addPath(path, pen)

                server_message = "1 "
                server_message += str(self.start.x()) + " "
                server_message += str(self.start.y()) + " "
                server_message += str(self.end.x()) + " "
                server_message += str(self.end.y()) + " "
                server_message += str(self.parent().pencolor.red()) + " "
                server_message += str(self.parent().pencolor.green()) + " "
                server_message += str(self.parent().pencolor.blue()) + " "
                server_message += str(self.parent().combo.currentIndex()) + " "

                client_socket.send(server_message.encode())
                 
                # 시작점을 다시 기존 끝점으로
                self.start = e.pos()
 
            # 사각형 그리기
            if self.parent().drawType == 2:
                brush = QBrush(self.parent().brushcolor)
 
                if len(self.items) > 0:
                    self.scene.removeItem(self.items[-1])
                    del(self.items[-1])
 
 
                rect = QRectF(self.start, self.end)
                rPen = QPen(brush.color(), 1)
                self.items.append(self.scene.addRect(rect, rPen, brush))
                 
            # 원 그리기
            if self.parent().drawType == 3:
                brush = QBrush(self.parent().brushcolor)
 
                if len(self.items) > 0:
                    self.scene.removeItem(self.items[-1])
                    del(self.items[-1])
 
 
                rect = QRectF(self.start, self.end)
                cPen = QPen(brush.color(), 1)
                self.items.append(self.scene.addEllipse(rect, cPen, brush))
 
 
    def mouseReleaseEvent(self, e):        
 
        if e.button() == Qt.LeftButton:
 
            if self.parent().checkbox.isChecked():
                return None
 
            pen = QPen(self.parent().pencolor, self.parent().combo.currentIndex())
 
            if self.parent().drawType == 0:
 
                self.items.clear()
                line = QLineF(self.start.x(), self.start.y(), self.end.x(), self.end.y())
                 
                self.scene.addLine(line, pen)
            
                server_message = "0 "
                server_message += str(self.start.x()) + " "
                server_message += str(self.start.y()) + " "
                server_message += str(self.end.x()) + " "
                server_message += str(self.end.y()) + " "
                server_message += str(self.parent().pencolor.red()) + " "
                server_message += str(self.parent().pencolor.green()) + " "
                server_message += str(self.parent().pencolor.blue()) + " "
                server_message += str(self.parent().combo.currentIndex()) + " "

                client_socket.send(server_message.encode())
 
            if self.parent().drawType == 2:
 
                brush = QBrush(self.parent().brushcolor)
 
                self.items.clear()
                rect = QRectF(self.start, self.end)
                cPen = QPen(brush.color(), 1)
                self.scene.addRect(rect, cPen, brush)
            
                server_message = "2 "
                server_message += str(self.start.x()) + " "
                server_message += str(self.start.y()) + " "
                server_message += str(self.end.x()) + " "
                server_message += str(self.end.y()) + " "
                server_message += str(self.parent().brushcolor.red()) + " "
                server_message += str(self.parent().brushcolor.green()) + " "
                server_message += str(self.parent().brushcolor.blue())
                client_socket.send(server_message.encode())
 
            if self.parent().drawType == 3:
 
                brush = QBrush(self.parent().brushcolor)
 
                self.items.clear()
                rect = QRectF(self.start, self.end)
                rPen = QPen(brush.color(), 1)
                self.scene.addEllipse(rect, rPen, brush)

                server_message = "3 "
                server_message += str(self.start.x()) + " "
                server_message += str(self.start.y()) + " "
                server_message += str(self.end.x()) + " "
                server_message += str(self.end.y()) + " "
                server_message += str(self.parent().brushcolor.red()) + " "
                server_message += str(self.parent().brushcolor.green()) + " "
                server_message += str(self.parent().brushcolor.blue())
                client_socket.send(server_message.encode())

if __name__ == '__main__':


    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((HOST, PORT))
    
    print('>> Connect Server')

    app = QApplication(sys.argv)
    w = CWidget(socket)
    w.show()
    sys.exit(app.exec_())

    client_socket.close()