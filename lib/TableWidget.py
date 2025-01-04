from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from lib.DarkPalette import QtDarkPalette
from lib.AppIcons import AppIcons
from lib.ContextMenu import ContextMenu

APPICONS = AppIcons()

#####################
## DELEGATES
#####################

class ProgressDelegate(QStyledItemDelegate):
	def paint(self, painter, option, index):
		progress = index.data(Qt.DisplayRole)
		
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
		self.goodIcon = APPICONS.qIconFromBase64(APPICONS.tickIconB)
		self.errorIcon = APPICONS.qIconFromBase64(APPICONS.crossIconB)
		self.processingIcon = APPICONS.qIconFromBase64(APPICONS.arrowIconB)

		self._iconDict = {'empty': self.emptyIcon,'good': self.goodIcon, 'error': self.errorIcon, 'proc': self.processingIcon}
	

	def paint(self, painter, option, index):
		d = index.data(Qt.DecorationRole)
		icon = self._iconDict[d]
		#option.rect = option.rect.adjusted(5,5,-5,-5)
		#option.rect.setSize(QSize(15,15))
		icon.paint(painter, option.rect, Qt.AlignCenter)
		
class RemoveButton(QPushButton):		
	def __init__(self, parent=None):
		super().__init__(parent=parent)
		self.trashIcon = APPICONS.qIconFromBase64(APPICONS.trashIconB)
		self.setIcon(self.trashIcon)
		self.setIconSize(self.trashIcon.actualSize(QSize(50,50)))
		self.setFlat(True)
		self.setMaximumWidth(40)

class FileTable(QTableWidget):
	PALETTE = QtDarkPalette()
	PALETTE.setColor(QPalette.Highlight, QColor(40, 40, 40))
	PALETTE.setColor(QPalette.HighlightedText, Qt.white)
	
	def __init__(self, rows, columns, Parent=None):
		super().__init__(rows, columns, Parent)
		self.droppedFiles: set = set()
		self.parent = self.parent()
		
		# Context menu
		self.menu = ContextMenu(self)
		
		# Delegates
		self.progDelegate = ProgressDelegate(self)
		self.iconDelegate = IconDelegate(self)
		
		# Default settings
		self.setItemDelegateForColumn(2, self.progDelegate)
		self.setItemDelegateForColumn(0, self.iconDelegate)
		self.horizontalHeader().setSectionResizeMode(1,QHeaderView.Stretch)
		self.horizontalHeader().hide()
		self.verticalHeader().hide()
		self.setColumnWidth(0,10)
		self.setColumnWidth(2,250)
		self.setColumnWidth(3,40)
		self.setSelectionBehavior(QAbstractItemView.SelectRows)
		self.setSelectionMode(QAbstractItemView.SingleSelection)
		self.setState(QAbstractItemView.NoState)
		
		# Tweaked selection style colours
		fileTablePal = QtDarkPalette()
		fileTablePal.setColor(QPalette.Highlight, QColor(40, 40, 40))
		fileTablePal.setColor(QPalette.HighlightedText, Qt.white)
		self.setPalette(self.PALETTE)

		self.threadpool = QThreadPool().globalInstance()
		# self.parentPool = self.parent().threadpool
		# assert(self.threadpool == self.parentPool)
	
	@pyqtSlot()
	def removeTableItem(self):
		row = self.currentRow()
		fileName = self.item(row,1).data(0)
		self.droppedFiles.remove(fileName)
		self.removeRow(row)
	
	def resetProgressBars(self):
		for row in range(self.rowCount()):
			self.item(row,2).setData(Qt.DisplayRole,0)
			self.item(row,0).setData(Qt.DecorationRole,'empty')

	def setPBData(self,data):
		self.item(data[0],2).setData(Qt.DisplayRole, data[1])

	def setIconData(self, data):
		self.item(data[0],0).setData(Qt.DecorationRole, data[1])

	def setFinishedData(self, data):
		if data:
			existingData = self.item(data[0],0).data(Qt.DecorationRole)
			
			if(existingData != 'error'):
				self.item(data[0],0).setData(Qt.DecorationRole,data[1])
		
		if (self.threadpool.activeThreadCount()) == 0:
			self.parent.setEnabledControlls(True)


	def contextMenuEvent(self, event):
		self.menu.showMenu(event)

	def addFilesToView(self, files):
		existingRows = self.rowCount()
		
		for r, (file) in enumerate(files):
			newRow = r + existingRows
			it_id = QTableWidgetItem()
			it_id.setData(Qt.DecorationRole, 'empty')
			it_file = QTableWidgetItem(file)
			it_progress = QTableWidgetItem()
			it_progress.setData(Qt.DisplayRole, 0)
			it_button = QTableWidgetItem()
			
			self.insertRow(self.rowCount())
			
			for c, item in enumerate((it_id, it_file, it_progress, it_button)):
				self.setItem(newRow, c, item)
				# not sure why this is here but it disables
				# row selection behaviour
				# if c == 3: 
				# 	item.setFlags(Qt.NoItemFlags)
				removeButton = RemoveButton(parent=self)
				removeButton.clicked.connect(self.removeTableItem)
				self.setCellWidget(newRow, 3, removeButton)
		
		self.droppedFiles.update(files)
