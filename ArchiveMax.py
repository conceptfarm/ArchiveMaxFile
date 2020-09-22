import os
import sys
import platform
import configparser
import traceback

from pathlib import PurePath, Path

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from MaxZipFile import MaxFileZip
from DarkPalette import QtDarkPalette
from AppIcons import AppIcons

palette = QtDarkPalette()
appIcons = AppIcons()


#################
## WORKER CLASS
#################

class WorkerSignals(QObject):
	started = pyqtSignal(tuple)
	finished = pyqtSignal(tuple)
	error = pyqtSignal(tuple)
	result = pyqtSignal(object)
	final = pyqtSignal()
	progress = pyqtSignal(tuple)


class Worker(QRunnable):
	def __init__(self, fn, *args, **kwargs):
		super().__init__()

		# Store constructor arguments (re-used for processing)
		self.setAutoDelete(True)
		self.fn = fn
		self.args = args
		self.kwargs = kwargs
		self.signals = WorkerSignals()

		# Add the callback to our kwargs
		self.kwargs['progress_callback'] = self.signals.progress
		self.kwargs['progress_started'] = self.signals.started
		self.kwargs['progress_error'] = self.signals.error
		self.kwargs['progress_finished'] = self.signals.finished
		
	
	@pyqtSlot()
	def run(self):
		'''
		Initialise the runner function with passed args, kwargs.
		'''
		
		# Retrieve args/kwargs here; and fire processing using them
		try:
			result = self.fn(*self.args, **self.kwargs)
		except:
			traceback.print_exc()
			exctype, value = sys.exc_info()[:2]
			#self.signals.error.emit((exctype, value, traceback.format_exc()))
			#self.signals.error.emit()
		else:
			self.signals.result.emit(result)  # Return the result of the processing
		finally:
			self.signals.final.emit()  # Done


#####################
## DELEGATES
#####################

class ProgressDelegate(QStyledItemDelegate):
	def paint(self, painter, option, index):
		progress = index.data(Qt.UserRole+1000)

		opt = QStyleOptionProgressBar()
		opt.rect = option.rect.adjusted(5,5,-5,-5)
		opt.minimum = 0
		opt.maximum = 100

		opt.progress = progress
		opt.text = "{}%".format(progress)
		opt.textAlignment = Qt.AlignCenter
		opt.textVisible = True
		QApplication.style().drawControl(QStyle.CE_ProgressBar, opt, painter)


class IconDelegate(QStyledItemDelegate):
	def __init__(self, Parent=None):
		super().__init__()
		
		self.emptyIcon = QIcon(QApplication.style().standardIcon(QStyle.SP_CustomBase))
		self.goodIcon = appIcons.qIconFromBase64(appIcons.tickIconB)
		self.errorIcon = appIcons.qIconFromBase64(appIcons.crossIconB)
		self.processingIcon = appIcons.qIconFromBase64(appIcons.arrowIconB)

		self._iconDict = {'empty':self.emptyIcon,'good':self.goodIcon,'error':self.errorIcon,'proc':self.processingIcon}
	

	def paint(self, painter, option, index):
		d = index.data(Qt.UserRole+1001)
		icon = self._iconDict[d]
		#option.rect = option.rect.adjusted(5,5,-5,-5)
		#option.rect.setSize(QSize(15,15))
		icon.paint(painter, option.rect, Qt.AlignCenter)


class RemoveButton2(QWidget):
	def __init__(self, Parent=None):
		super().__init__()
		self.button = QPushButton('', Parent)
		self.button.setIcon(appIcons.qIconFromBase64(appIcons.trashBIconB))
		self.button.setMaximumWidth(40)
		self.pLayout = QHBoxLayout(Parent)
		self.pLayout.addWidget(self.button)
		self.pLayout.setAlignment(Qt.AlignRight)
		self.pLayout.setContentsMargins(0, 0, 0, 0)
		self.setLayout(self.pLayout);
		
class RemoveButton(QPushButton):		
	def __init__(self, Parent=None):
		super().__init__()
		self.trashIcon = appIcons.qIconFromBase64(appIcons.trashIconB)
		self.setIcon(self.trashIcon)
		self.setIconSize(self.trashIcon.actualSize(QSize(50,50)))
		self.setFlat(True)
		self.setMaximumWidth(40)


#####################
## MAIN WINDOW CLASS
#####################

class MainWindow(QMainWindow):
	
	def __init__(self, droppedFiles, zipFileDir):
		super().__init__()
		self.left = 150
		self.top = 150
		self.width = 800
		self.height = 480
		self.droppedFiles = droppedFiles
		self.zipFileDir = zipFileDir
		self.threadpool = QThreadPool().globalInstance()
		self.threadpoolQLength = 0
		self.threadpool.setMaxThreadCount(2)

		self.archiveDir = False
		self.singleCheck = False
		self.singleFile = False

		self.diskIcon = appIcons.qIconFromBase64(appIcons.diskIconB)		
		self.folderIcon = appIcons.qIconFromBase64(appIcons.folderIconB)
		self.maxFilePix = appIcons.qPixmapFromBase64(appIcons.maxFileIconB)
		
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

		self.w = QTableWidget(0,4)
		self.w.setObjectName('table')
		self.w.setSelectionMode(QAbstractItemView.NoSelection)
		self.w.setState(QAbstractItemView.NoState)
		#self.w.setShowGrid(False)
		#self.w.setStyleSheet("QTableWidget::item {padding-left: 10px; border-bottom: 1px solid white} QTableWidget {background-color: #353535; border-width:5px}")

		self.progDelegate = ProgressDelegate(self.w)
		self.iconDelegate = IconDelegate(self.w)
		self.w.setItemDelegateForColumn(2, self.progDelegate)
		self.w.setItemDelegateForColumn(0, self.iconDelegate)
		self.w.horizontalHeader().setSectionResizeMode(1,QHeaderView.Stretch)
		self.w.horizontalHeader().hide()
		self.w.verticalHeader().hide()
		self.w.setColumnWidth(0,10)
		self.w.setColumnWidth(2,250)
		self.w.setColumnWidth(3,40)
		
		#self.model = QStandardItemModel(0, 3)
		self.addFilesToView(self.droppedFiles, self.w)
		
		self.table_gl.addWidget(self.w, 0, 0, 1, 1)	
		
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
		#self.processDir_gl.setColumnMinimumWidth(3, 140)



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
		#sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
		#sizePolicy.setHorizontalStretch(1)
		#sizePolicy.setVerticalStretch(0)
		#sizePolicy.setHeightForWidth(self.zipFileDir_txt.sizePolicy().hasHeightForWidth())
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
		#self.process_btn.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Maximum)
		self.process_btn.setIcon(self.diskIcon)
		self.process_btn.setIconSize(self.diskIcon.actualSize(QSize(50,50)))
		self.process_btn.setObjectName('process_btn')

		
		if Path(self.zipFileDir.strip()).is_dir() == False or (self.zipFileDir) == '':
			self.process_btn.setEnabled(False)
		else:
			print(self.zipFileDir, 'path')
			self.process_btn.setEnabled(True)
			self.archiveDir = True

		self.process_gl.addWidget(self.process_btn, 1, 1, 1, 1)
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

	def addFilesToView(self, files, view):
		existingRows = view.rowCount()
		for r, (file) in enumerate(files):
			newRow = r + existingRows
			it_id = QTableWidgetItem()
			it_id.setData(Qt.UserRole+1001, 'empty')
			it_file = QTableWidgetItem(file)
			it_progress = QTableWidgetItem()
			it_progress.setData(Qt.UserRole+1000, 0)
			it_button = QTableWidgetItem()
			
			
			view.insertRow(view.rowCount())
			
			for c, item in enumerate((it_id, it_file, it_progress, it_button)):
				view.setItem(newRow, c, item)
				if c != 3: item.setFlags(Qt.NoItemFlags)
				removeButton = RemoveButton(self.w)
				#removeButton = QPushButton('Remove', self.w)
				removeButton.clicked.connect(self.removeRow)
				view.setCellWidget(newRow,3,removeButton)
		
	def writeToConfig(self, setting, key, value):
		#config = configparser.ConfigParser()
		config.read(configFileName)
		config.set(setting, key, value)
		
		with open(configFileName, 'w') as configfile:
			config.write(configfile)

	def setPBData(self,data):

		self.w.item(data[0],2).setData(Qt.UserRole+1000,data[1])

	def setIconData(self, data):
		self.w.item(data[0],0).setData(Qt.UserRole+1001,data[1])

	def setFinishedData(self, data):
		existingData = self.w.item(data[0],0).data(Qt.UserRole+1001)
		
		if(existingData != 'error'):
			self.w.item(data[0],0).setData(Qt.UserRole+1001,data[1])
		
		if (self.threadpool.activeThreadCount()) == 0:
			self.setEnabledControlls(True)

	def maxZipFiles(self, file):
		maxZip = MaxFileZip(file, (file+'.zip'), True)

	def setEnabledControlls(self, state):
		self.w.setEnabled(state)
		self.zipFileDir_btn.setEnabled(state)
		self.zipFileDir_txt.setEnabled(state)
		self.process_btn.setEnabled(state)
		self.singleZipFile_chb.setEnabled(state)
		
		if self.singleZipFile_chb.checkState() == 2:
			self.singleZipFile_txt.setEnabled(state)
		
		self.setAcceptDrops(state)
	
	def resetProgressBars(self):
		for row in range(self.w.rowCount()):
			self.w.item(row,2).setData(Qt.UserRole+1000,0)
			self.w.item(row,0).setData(Qt.UserRole+1001,'empty')

	def checkReadyToArchive(self):
		if (self.archiveDir == True and self.singleFile == True and self.singleCheck == True) or \
		(self.archiveDir == True and self.singleFile == False and self.singleCheck == False):
			self.process_btn.setEnabled(True)
		else:
			self.process_btn.setEnabled(False)
		#print(self.archiveDir, self.singleCheck, self.singleFile)

	######################
	## BUTTON FUNCTIONS ##
	######################
	
	def removeRow(self):
		#print(self.sender().parent().parent().currentRow())
		#print(self.sender())
		r = (self.sender().parent().parent().currentRow())
		self.sender().parent().parent().removeRow(r)
	
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
		self.resetProgressBars()
		self.setEnabledControlls(False)
		
		#collect row data into a dict
		rawData = {row:self.w.item(row,1).data(0) for row in range(self.w.rowCount()) }
		processData = None
		outPutZipFile = None
		
		if self.singleZipFile_chb.checkState()==2:
			#for single file make a list of one dict
			processData = [rawData]
			
			if (self.singleZipFile_txt.text())[-4:] != '.zip':
				self.singleZipFile_txt.setText(self.singleZipFile_txt.text() + '.zip')
			
			outPutZipFile = PurePath(self.zipFileDir_txt.text(),self.singleZipFile_txt.text())
		else:
			#for multi files make a list of dicts
			processData = [{c:rawData[c]} for c in range(len(rawData))]
			
		
		for data in processData:		
			print(data)
			maxZip = MaxFileZip(data, PurePath(self.zipFileDir_txt.text()), outPutZipFile, True)
			
			worker = Worker(maxZip.main)
			worker.signals.started.connect(self.setIconData)
			worker.signals.progress.connect(self.setPBData)
			worker.signals.error.connect(self.setIconData)
			worker.signals.finished.connect(self.setFinishedData)

			self.threadpool.start(worker)


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
				fname = str(PurePath((url.toLocalFile())))
				if PurePath(fname).suffix == '.max' and fname not in self.droppedFiles:
					newFiles.add(fname)

			self.addFilesToView(newFiles, self.w)
			self.droppedFiles.update(newFiles)
		else:
			e.ignore()


if __name__ == '__main__':
	import sys
	app = QApplication(sys.argv)
	app.setStyle('Fusion')
	app.setPalette(palette)

	dirList = set()
	#dirList = {'C:\\Python37\\NEWS.txt','C:\\Python37\\15-01-21_CIYE_Set.max','C:\\Python37\\assetTest.max','C:\\Python37\\field_skin.max'}
	
	for arg in sys.argv:
		if PurePath(arg).suffix == '.max':
			dirList.add(str(PurePath(arg)))
	
	#sort the list , chech the code below make sure it's right
	#dirList = sorted(dirList, key=lambda i: (os.path.basename(i)))
	
	configFileName = 'ArchiveMax.ini'
	config = configparser.ConfigParser()

	zipFileDir = ''
	
	appIcon = appIcons.qIconFromBase64(appIcons.clampB)
	
	try:
		config.read(configFileName)
		zipFileDir = (config['ArchiveMaxSettings']['zipFileDir'])
	except:
		print('Didnt Pass')
		config['ArchiveMaxSettings'] = {'zipFileDir':''}
		with open(configFileName, 'w') as configfile:
			config.write(configfile)



	ex = MainWindow(dirList, zipFileDir)
	sys.exit(app.exec_())
