import os
import sys
import configparser
import tempfile

from pathlib import PurePath, Path

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from lib.MaxZipFile import MaxFileZip
from lib.DarkPalette import QtDarkPalette
from lib.AppIcons import AppIcons
from lib.Threading import Worker
from lib.TableWidget import FileTable

PALETTE = QtDarkPalette()
APPICONS = AppIcons()

#####################
## MAIN WINDOW CLASS
#####################

class MainWindow(QMainWindow):
	
	def __init__(self, droppedFiles: set, zipFileDir: str):
		super().__init__()
		self.left = 150
		self.top = 150
		self.width = 800
		self.height = 480
		self.fileTable = None
		self.droppedFiles = droppedFiles
		self.zipFileDir = zipFileDir
		self.threadpool = QThreadPool().globalInstance()
		self.threadpoolQLength = 0
		self.threadpool.setMaxThreadCount(2)

		self.archiveDir = False
		self.singleCheck = False
		self.singleFile = False

		self.diskIcon = APPICONS.qIconFromBase64(APPICONS.diskIconB)		
		self.folderIcon = APPICONS.qIconFromBase64(APPICONS.folderIconB)
		self.maxFilePix = APPICONS.qPixmapFromBase64(APPICONS.maxFileIconB)
		
		self.setupUi(self)

	def setupUi(self, MainWindow):
		self.setGeometry(self.left, self.top, self.width, self.height)
		self.setWindowIcon(appIcon)
		self.setWindowTitle('Max File Archiver')
		self.centralwidget = QWidget(MainWindow)
		self.centralwidget.setObjectName('centralwidget')
		
		self.verticalLayout = QVBoxLayout(self.centralwidget)
		self.verticalLayout.setObjectName('verticalLayout')
		
		self.table_gl = QGridLayout()
		self.table_gl.setContentsMargins(-1, -1, -1, 8)
		self.table_gl.setSpacing(6)
		self.table_gl.setObjectName('table_gl')

		self.fileTable = FileTable(0, 4, self)
		self.fileTable.setObjectName('table')
		self.fileTable.addFilesToView(self.droppedFiles)
		
		self.table_gl.addWidget(self.fileTable, 0, 0, 1, 1)	
		
		#ADD MORE AREA
		self.gridLayoutAddMore = QGridLayout()
		self.gridLayoutAddMore.setContentsMargins(0, 0, 0, 0)
		
		self.dragAndDropLabel_1 = QLabel("Drag and Drop 3ds Max Files here", self)
		self.dragAndDropLabel_1.setMinimumSize(QSize(120, 60))
		self.dragAndDropLabel_1.setAlignment(Qt.AlignCenter)
		
		self.dragAndDropLabel_2 = QLabel("", self)
		self.dragAndDropLabel_2.setFixedSize(QSize(32, 60))
		self.dragAndDropLabel_2.setAlignment(Qt.AlignCenter)
		self.dragAndDropLabel_2.setPixmap(self.maxFilePix)
		
		sI = QSpacerItem(40, 40,QSizePolicy.Expanding, QSizePolicy.Minimum)
		sI2 = QSpacerItem(40, 40,QSizePolicy.Expanding, QSizePolicy.Minimum)
		
		self.gridLayoutAddMore.addItem(sI, 1, 0, 1, 1)
		self.gridLayoutAddMore.addWidget(self.dragAndDropLabel_2, 1, 1, 1, 1)
		self.gridLayoutAddMore.addWidget(self.dragAndDropLabel_1, 1, 2, 1, 1)
		self.gridLayoutAddMore.addItem(sI2, 1, 3, 1, 1)

		#OUTPUT DIR AREA
		self.processDir_gl = QGridLayout()
		self.processDir_gl.setContentsMargins(0, 8, 0, 8)
		self.processDir_gl.setSpacing(6)
		self.processDir_gl.setObjectName('processDir_gl')

		self.zipFileDir_txt = QLineEdit(self.zipFileDir, self.centralwidget)
		self.zipFileDir_txt.setPlaceholderText('C:\\Temp\\3dsMaxArchives\\')
		sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
		sizePolicy.setHorizontalStretch(1)
		sizePolicy.setVerticalStretch(0)
		#sizePolicy.setHeightForWidth(self.zipFileDir_txt.sizePolicy().hasHeightForWidth())
		self.zipFileDir_txt.setSizePolicy(sizePolicy)
		self.zipFileDir_txt.setMinimumSize(QSize(0, 22))
		self.zipFileDir_txt.setObjectName('zipFileDir_txt')
		
		self.zipFileDir_lbl = QLabel(self.centralwidget)
		self.zipFileDir_lbl.setText('Save Archive Zip Files To:')
		self.zipFileDir_lbl.setMinimumSize(QSize(130, 22))
		self.zipFileDir_lbl.setObjectName('zipFileDir_lbl')
		
		self.zipFileDir_btn = QPushButton(self.centralwidget)
		self.zipFileDir_btn.setText('')
		self.zipFileDir_btn.setIcon(self.folderIcon)
		self.zipFileDir_btn.setIconSize(self.folderIcon.actualSize(QSize(50,50)))
		self.zipFileDir_btn.setMinimumSize(QSize(40, 22))
		self.zipFileDir_btn.setMaximumSize(QSize(40, 16777215))
		self.zipFileDir_btn.setObjectName('zipFileDir_btn')
		
		self.singleZipFile_chb = QCheckBox('Archive to Single File', self.centralwidget)
		self.singleZipFile_chb.setCheckState(False)
		self.singleZipFile_chb.setObjectName('singleZipFile_chb')
		
		
		self.singleZipFile_txt = QLineEdit('', self.centralwidget)
		self.singleZipFile_txt.setEnabled(False)
		self.singleZipFile_txt.setPlaceholderText('Example.zip')
		self.singleZipFile_txt.setSizePolicy(sizePolicy)
		self.singleZipFile_txt.setMinimumSize(QSize(0, 22))
		self.singleZipFile_txt.setObjectName('singleZipFile_txt')


		self.processDir_gl.addWidget(self.zipFileDir_lbl, 0, 0, 1, 1)
		self.processDir_gl.addWidget(self.zipFileDir_txt, 0, 1, 1, 1)
		self.processDir_gl.addWidget(self.zipFileDir_btn, 0, 2, 1, 1)
		self.processDir_gl.addWidget(self.singleZipFile_chb, 1, 0, 1, 1)
		self.processDir_gl.addWidget(self.singleZipFile_txt, 1, 1, 1, 2)
		self.processDir_gl.setColumnStretch(1, 1)

		#PROCESS BUTTON AREA
		self.process_gl = QGridLayout()
		self.process_gl.setContentsMargins(-1, -1, -1, 8)
		self.process_gl.setSpacing(6)
		
		self.process_btn = QPushButton(self.centralwidget)
		self.process_btn.setText('  Archive')
		self.process_btn.setMinimumSize(QSize(80, 40))
		self.process_btn.setMaximumSize(QSize(16777215, 40))
		self.process_btn.setIcon(self.diskIcon)
		self.process_btn.setIconSize(self.diskIcon.actualSize(QSize(50,50)))
		self.process_btn.setObjectName('process_btn')

		self.list_assets_btn = QPushButton(self.centralwidget)
		self.list_assets_btn.setText('List All File Assets')
		self.list_assets_btn.setMinimumSize(QSize(80, 40))
		self.list_assets_btn.setMaximumSize(QSize(16777215, 40))
		self.list_assets_btn.setObjectName('list_assets_btn')

		
		if Path(self.zipFileDir.strip()).is_dir() == False or (self.zipFileDir) == '':
			self.process_btn.setEnabled(False)
		else:
			print(self.zipFileDir, 'path')
			self.process_btn.setEnabled(True)
			self.archiveDir = True

		self.process_gl.addWidget(self.process_btn, 1, 1, 1, 1)
		self.process_gl.addWidget(self.list_assets_btn, 2, 1, 1, 1)
		self.process_gl.setColumnStretch(1, 1)
			
		self.verticalLayout.addLayout(self.gridLayoutAddMore)
		self.verticalLayout.addLayout(self.table_gl)
		self.verticalLayout.addLayout(self.processDir_gl)
		self.verticalLayout.addLayout(self.process_gl)

		MainWindow.setCentralWidget(self.centralwidget)
		QMetaObject.connectSlotsByName(self)
		
		# Enable dragging and dropping onto the GUI
		self.setAcceptDrops(True)
		self.show()	
	


	######################
	## FUNCTIONS        ##
	######################
		
	def writeToConfig(self, setting, key, value):
		#config = configparser.ConfigParser()
		config.read(configFileName)
		config.set(setting, key, value)
		
		with open(configFileName, 'w') as configfile:
			config.write(configfile)

	def setEnabledControlls(self, state):
		self.fileTable.setEnabled(state)
		self.zipFileDir_btn.setEnabled(state)
		self.zipFileDir_txt.setEnabled(state)
		self.process_btn.setEnabled(state)
		self.singleZipFile_chb.setEnabled(state)
		self.list_assets_btn.setEnabled(state)
		
		if self.singleZipFile_chb.checkState() == 2:
			self.singleZipFile_txt.setEnabled(state)
		
		self.setAcceptDrops(state)
	
	def checkReadyToArchive(self):
		if (self.archiveDir == True and self.singleFile == True and self.singleCheck == True) or \
		(self.archiveDir == True and self.singleFile == False and self.singleCheck == False):
			self.process_btn.setEnabled(True)
		else:
			self.process_btn.setEnabled(False)

	######################
	## BUTTON FUNCTIONS ##
	######################
		
	@pyqtSlot()
	def on_zipFileDir_btn_clicked(self):
		defaultDir = self.zipFileDir_txt.text() if self.zipFileDir_txt.text() != '' else QDir.home().dirName()
		dirPath = QFileDialog.getExistingDirectory(self, 'Select a directory',defaultDir, QFileDialog.ShowDirsOnly)
		
		if dirPath:
			self.zipFileDir_txt.setText(dirPath)
			self.writeToConfig('ArchiveMaxSettings', 'zipFileDir', dirPath)
			self.archiveDir = True
			self.checkReadyToArchive()

	@pyqtSlot(str)
	def on_zipFileDir_txt_textEdited(self, text):
		if Path(text).is_dir() == False or text == '':
			self.archiveDir = False
		else:
			self.archiveDir = True
		self.checkReadyToArchive()

	@pyqtSlot(int)		
	def on_singleZipFile_chb_stateChanged(self, state):
		if state == 0: #False
			self.singleCheck = False
			self.singleFile = False
			self.singleZipFile_txt.setEnabled(False)
			self.singleZipFile_txt.setText('')
		elif state == 2: #True
			self.singleZipFile_txt.setEnabled(True)
			self.singleZipFile_txt.setText('')
			self.singleCheck = True
		self.checkReadyToArchive()

	@pyqtSlot(str)
	def on_singleZipFile_txt_textEdited(self, text):
		if text == '':
			self.singleFile = False
		else:
			self.singleFile = True
		self.checkReadyToArchive()
	
	@pyqtSlot()
	def on_process_btn_clicked(self):
		self.fileTable.resetProgressBars()
		self.setEnabledControlls(False)
		
		#collect row data into a dict {row: maxfilepath}
		rowData = { row: self.fileTable.item(row,1).data(0) for row in range(self.fileTable.rowCount()) }
		processData = None
		outPutZipFile = None
		zipFileDir = self.zipFileDir_txt.text()
		zipFileName = self.singleZipFile_txt.text()
		
		if self.singleZipFile_chb.checkState()==2:
			#for single file make a list of one dict
			processData = [rowData]
			
			# check that the zip file ends with .zip
			if not zipFileName.endswith('.zip'):
				zipFileName = zipFileName + '.zip'
			
			outPutZipFile = PurePath(zipFileDir, zipFileName)
		else:
			#for multi files make a list of dicts
			processData = [{c:rowData[c]} for c in range(len(rowData))]
				
		for data in processData:		
			maxZip = MaxFileZip(data, PurePath(zipFileDir), outPutZipFile, True)
			
			worker = Worker(maxZip.main)
			worker.signals.started.connect(self.fileTable.setIconData)
			worker.signals.progressValue.connect(self.fileTable.setPBData)
			worker.signals.error.connect(self.fileTable.setIconData)
			worker.signals.finished.connect(self.fileTable.setFinishedData)

			self.threadpool.start(worker)

	@pyqtSlot()
	def on_list_assets_btn_clicked(self):
		#collect row data into a dict
		maxFiles = [self.fileTable.item(row,1).data(0) for row in range(self.fileTable.rowCount())]
		allAssetsPaths = set()
		for maxFile in maxFiles:
			# init class
			maxZip = MaxFileZip(None, None, None, True)
			fileAssetsPaths = maxZip.collectAssetsPathsFromFile(maxFile, [])
			allAssetsPaths.update(fileAssetsPaths)
		
		allAssetsPaths = list(allAssetsPaths)
		allAssetsPaths.sort()
		tempFile = tempfile.NamedTemporaryFile(mode = 'w+', newline='\n',suffix='.txt',delete=False)
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


	###########################
	## DRAG + DROP FUNCTIONS ##
	###########################
	# The following three methods set up dragging and dropping for the app
	def dragEnterEvent(self, e):
		if e.mimeData().hasUrls:
			e.accept()
		else:
			e.ignore()

	def dragMoveEvent(self, e):
		if e.mimeData().hasUrls:
			e.accept()
		else:
			e.ignore()

	def dropEvent(self, e):
		'''
		Drop files directly onto the widget
		File locations are stored in fname
		:param e:
		:return:
		'''
		newFiles = set()
		if e.mimeData().hasUrls:
			e.setDropAction(Qt.CopyAction)
			e.accept()
			for url in e.mimeData().urls():
				fname = url.toLocalFile()
				if PurePath(fname).suffix == '.max' and fname not in self.fileTable.droppedFiles:
					newFiles.add(fname)

			self.fileTable.addFilesToView(newFiles)
		else:
			e.ignore()


if __name__ == '__main__':
	import sys
	app = QApplication(sys.argv)
	app.setStyle('Fusion')
	app.setPalette(PALETTE)

	#dirSet = set()
	dirSet:set  = {r'U:\Documents\3ds Max 2024\scenes\global_test_10.max'}
	
	for arg in sys.argv:
		if PurePath(arg).suffix.lower() == '.max':
			dirSet.add(arg)
	
	#sort the list , chech the code below make sure it's right
	#dirList = sorted(dirList, key=lambda i: (os.path.basename(i)))
	
	configFileName = 'ArchiveMax.ini'
	config = configparser.ConfigParser()

	zipFileDir: str = ''
	
	appIcon = APPICONS.qIconFromBase64(APPICONS.clampB)
	
	try:
		config.read(configFileName)
		zipFileDir = (config['ArchiveMaxSettings']['zipFileDir'])
	except:
		print('Didnt Pass')
		config['ArchiveMaxSettings'] = {'zipFileDir':''}
		with open(configFileName, 'w') as configfile:
			config.write(configfile)

	ex = MainWindow(dirSet, zipFileDir)
	sys.exit(app.exec_())