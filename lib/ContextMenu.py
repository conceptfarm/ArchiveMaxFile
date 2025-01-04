import os
from pathlib import Path
import tempfile
from typing import Optional

#PyQt Classes
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *


from lib.Threading import Worker, Callbacks
from lib.MaxZipFile import MaxFileZip
from lib.ProgressWindow import ProgressWindow

class ContextMenu(QMenu):
	def __init__(self, parent):
		super().__init__(parent)
		self.mainWindow = self.findMainWindow()
		self.fileTable = parent
		self.threadpool = QThreadPool().globalInstance()
		self.updateAction = self.addAction('')
	
	def findMainWindow(self) -> Optional[QMainWindow]:
		# Global function to find the (open) QMainWindow in application
		app = QApplication.instance()
		for widget in app.topLevelWidgets():
			if isinstance(widget, QMainWindow):
				return widget
		return None
			
	def showMenu(self, event):
		self.index = self.fileTable.indexAt(event.pos())
		if self.index.isValid():
			maxFile = self.index.data()
			self.updateAction.setText(f'List Assets for: {maxFile}')
			self.updateAction.setEnabled(True)
			# Connection can be made to more than one function
			# disconnect previous connections just in case
			try:
				self.updateAction.disconnect()
			except:
				pass
							
			self.updateAction.triggered.connect(lambda: self.getFileAssetsTriggered(maxFile))
		else:
			self.updateAction.setText('No selection')
			self.updateAction.setEnabled(False)
		
		self.exec(event.globalPos())

	def getFileAssetsTriggered(self, maxfile):
		self.progressWindow = ProgressWindow(self.fileTable, label='Loading...', showLog=False, min=0, max=0)
		self.progressWindow.show()

		QApplication.processEvents()
		
		self.threadpool.setMaxThreadCount(1)
		worker = Worker(self.getFileAssets, None, maxfile)
		worker.signals.finished.connect(self.progressWindow.close)
		self.threadpool.start(worker)	
		
	def getFileAssets(self, maxFile, **kwargs):
		allAssetsPaths = set()

		maxZip = MaxFileZip(None, None, None, True)
		fileAssetsPaths = maxZip.collectAssetsPathsFromFile(maxFile, [])
		allAssetsPaths.update(fileAssetsPaths)
		
		allAssetsPaths = list(allAssetsPaths)
		allAssetsPaths.sort()
		tempFile = tempfile.NamedTemporaryFile(mode = 'w+', newline='\n', suffix='.txt', delete=False)
		dataWritten = False
		with tempFile as assetLogFile:
			for p in allAssetsPaths :
				# if 'X:\\' in p: # and not os.path.exists(p):
				try:
					assetLogFile.write(p+'\n')
					dataWritten = True
				except:
					print(p)
		if dataWritten:
			os.startfile(tempFile.name, 'open')

	
