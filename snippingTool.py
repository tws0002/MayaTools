import sys
from PyQt5 import QtWidgets, QtCore, QtGui
from PIL import ImageGrab


class MyWidget(QtWidgets.QWidget):
	def __init__(self):
		super(MyWidget, self).__init__()
		img = ImageGrab.grab
		size = img().size
		screen_width = size[0]
		screen_height = size[1]
		self.setGeometry(0, 0, screen_width, screen_height)
		self.setWindowTitle(' ')
		self.begin = QtCore.QPoint()
		self.end = QtCore.QPoint()
		self.setWindowOpacity(0.3)
		QtWidgets.QApplication.setOverrideCursor(
			QtGui.QCursor(QtCore.Qt.CrossCursor)
		)
		self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
		print('Capture the screen...')
		self.show()

	def paintEvent(self, event):
		qp = QtGui.QPainter(self)
		qp.setPen(QtGui.QPen(QtGui.QColor('black'), 3))
		qp.setBrush(QtGui.QColor(128, 128, 255, 128))
		qp.drawRect(QtCore.QRect(self.begin, self.end))

	def mousePressEvent(self, event):
		self.begin = event.pos()
		self.end = self.begin
		self.update()

	def mouseMoveEvent(self, event):
		self.end = event.pos()
		self.update()

	def mouseReleaseEvent(self, event):
		self.close()

		x1 = min(self.begin.x(), self.end.x())
		y1 = min(self.begin.y(), self.end.y())
		x2 = max(self.begin.x(), self.end.x())
		y2 = max(self.begin.y(), self.end.y())
		

		img = ImageGrab.grab(bbox=(x1, y1, x2, y2))
		img.save('capture.png')
		img.show()
		# img = cv2.cvtColor(np.array(img), cv2.COLOR_BGR2RGB)

		# cv2.imshow('Captured Image', img)
		# cv2.waitKey(0)
		# cv2.destroyAllWindows()
test = MyWidget()