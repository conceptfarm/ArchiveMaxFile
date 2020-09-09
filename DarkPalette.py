from PyQt5.QtGui import QPalette, QColor
from PyQt5.QtCore import Qt

class QtDarkPalette(QPalette):
	def __init__(self):
		super().__init__()

		self.baseAltColour = QColor(53, 53, 53)
		self.baseColour = QColor(25, 25, 25)
		self.highlightColour = QColor(42, 130, 218)

		self.setColor(QPalette.Disabled, QPalette.Button, self.baseAltColour)
		self.setColor(QPalette.Disabled, QPalette.ButtonText, self.baseAltColour)

		self.setColor(QPalette.Window, self.baseAltColour)
		self.setColor(QPalette.WindowText, Qt.white)
		self.setColor(QPalette.Base, self.baseColour)
		self.setColor(QPalette.AlternateBase, self.baseAltColour)
		self.setColor(QPalette.ToolTipBase, Qt.white)
		self.setColor(QPalette.ToolTipText, Qt.white)
		self.setColor(QPalette.Text, Qt.white)
		self.setColor(QPalette.Active, QPalette.Button, self.baseAltColour)
		self.setColor(QPalette.Active, QPalette.ButtonText, Qt.white)
		self.setColor(QPalette.BrightText, Qt.red)
		self.setColor(QPalette.Link, self.highlightColour)
		self.setColor(QPalette.Highlight, self.highlightColour)
		self.setColor(QPalette.HighlightedText, Qt.black)

	#QColor to RGB CSS string
	def toRGBCSS(self, qColour):
		return 'rgb('+str(qColour.red())+','+str(qColour.green())+','+str(qColour.blue())+')'