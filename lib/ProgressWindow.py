

#PyQt Classes
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

class ProgressWindow(QDialog):
	def __init__(self, parent=None, label:str='', showPBar:bool=True, showLbl:bool=True, label2:str='', showPBar2:bool=False, showLbl2:bool=False, enableOK:bool=True, okText:str='', enableCancel:bool=True, cancelText:str='', max:int=0, min:int=0, winFlags=Qt.FramelessWindowHint, **kwargs):
		super().__init__(parent)
		self.kwargs = kwargs
		self.okButton = None
		self.cancelButton = None

		self.lbl = QLabel('')
		self.lbl.setText(label)
		self.lbl.setAlignment(Qt.AlignCenter)
		if not showLbl:
			self.lbl.hide()
		
		self.pbar = QProgressBar(self)
		self.pbar.setFixedHeight(10)
		self.pbar.setValue(0)
		self.pbar.setMaximum(max)
		self.pbar.setMinimum(min)
		self.pbar.setTextVisible(False)
		if not showPBar:
			self.pbar.hide()

		self.lbl2 = QLabel('')
		self.lbl2.setText(label2)
		self.lbl2.setAlignment(Qt.AlignCenter)
		if not showLbl2:
			self.lbl2.hide()

		self.pbar2 = QProgressBar(self)
		self.pbar2.setFixedHeight(10)
		self.pbar2.setValue(0)
		self.pbar2.setMaximum(max)
		self.pbar2.setMinimum(min)
		self.pbar2.setTextVisible(False)
		if not showPBar2:
			self.pbar2.hide()
		
		self.buttonBox = QDialogButtonBox(self)
		if okText != '':
			self.okButton = self.buttonBox.addButton(okText,  QDialogButtonBox.AcceptRole)
			self.okButton.setEnabled(enableOK)
			self.buttonBox.accepted.connect(self.accept)
		if cancelText != '':
			self.cancelButton = self.buttonBox.addButton(cancelText,  QDialogButtonBox.RejectRole)
			self.cancelButton.setEnabled(enableCancel)
			self.buttonBox.rejected.connect(self.reject)


		self.layout = QVBoxLayout()
		self.layout.addWidget(self.lbl)
		self.layout.addWidget(self.pbar)
		self.layout.addWidget(self.lbl2)
		self.layout.addWidget(self.pbar2)
		self.layout.addWidget(self.buttonBox)
		self.layout.setAlignment(self.buttonBox, Qt.AlignCenter)
		self.setLayout(self.layout)
		self.setWindowFlag(winFlags)
		self.adjustSize()
		self.setWidth()
		self.centerToParent()
		self.setObjectName('progressWindow')
		self.setWindowModality(Qt.WindowModal)
	
	def setWidth(self):
		if self.kwargs.get('width'):
			self.resize(self.kwargs['width'], self.height())
	
	def validatePbarFormat(self, frmt: str) -> str:
		# %p - is replaced by the percentage completed. 
		# %v - is replaced by the current value.
		# %m - is replaced by the total number of steps.
		# The default value is "%p%".
		if frmt == '%p' or frmt == '%v' or frmt == '%m':
			return frmt
		else:
			return '%p'

	def setFormat(self, val):
		if self.pbar:
			if isinstance(val, tuple):
				val1, val2 = val
				if val1: 
					self.pbar.setFormat(self.validatePbarFormat(val1))
				if val2: 
					self.pbar2.setFormat(self.validatePbarFormat(val2))
			else:
				if val: 
					self.pbar.setFormat(self.validatePbarFormat(val))
				
	def setValue(self, val):
		if self.pbar:
			if isinstance(val, tuple):
				val1, val2 = val
				if val1:
					self.pbar.setValue(val1)
				if val2:
					self.pbar2.setValue(val2)
			else:
				self.pbar.setValue(val)
	
	def getValue(self):
		if self.pbar:		
			return self.pbar.value()
		else:
			return 0
		
	def setMinimum(self, val):
		if self.pbar:
			if isinstance(val, tuple):
				val1, val2 = val
				if val1: 
					self.pbar.setMinimum(val1)
				if val2: 
					self.pbar2.setMinimum(val2)
			else:
				self.pbar.setMinimum(val)
				
	def setMaximum(self, val):
		if self.pbar:
			if isinstance(val, tuple):
				val1, val2 = val
				if val1: 
					self.pbar.setMaximum(val1)
				if val2: 
					self.pbar2.setMaximum(val2)
			else:		
				self.pbar.setMaximum(val)
	
	def setLabelText(self, val):
		if self.lbl:
			if isinstance(val, tuple):
				val1, val2 = val
				if val1: 
					self.lbl.setText(val1)
				if val2: 
					self.lbl2.setText(val2)
			else:		
				self.lbl.setText(val)
	
	def enableOK(self):
		if self.okButton:
			self.okButton.setEnabled(True)
	
	def enableCancel(self):
		if self.cancelButton:
			self.cancelButton.setEnabled(True)
	
	def onFinish(self, *args):
		for arg in args:
			arg()
	
	def centerToParent(self):
		if self.parent() != None:
			pw = self.parent().size().width()
			ph = self.parent().size().height()
			w = self.size().width()
			h = self.size().height()
			x = self.parent().mapToGlobal(QPoint(0,0)).x()
			y = self.parent().mapToGlobal(QPoint(0,0)).y()
			c = QPoint(int(x + pw/2.0 - w/2.0), int(y + ph/2.0 - h/2.0))
			self.move(c)
		else:
			print('No Parent defined')