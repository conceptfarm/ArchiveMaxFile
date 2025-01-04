import traceback
import sys

from PyQt5.QtCore import QObject, QRunnable, pyqtSignal, pyqtSlot


class WorkerSignals(QObject):
	started = pyqtSignal(tuple)
	finished = pyqtSignal(object)
	error = pyqtSignal(tuple)
	result = pyqtSignal(object)
	progressMin = pyqtSignal(object)
	progressMax = pyqtSignal(object)
	progressValue = pyqtSignal(object)
	progressFormat = pyqtSignal(object)
	progressLabel = pyqtSignal(object)
	progressLog = pyqtSignal(str)
	progressNone = pyqtSignal()

class Worker(QRunnable):
	def __init__(self, fn, progressType=None, *args, **kwargs):
		super().__init__()

		# Store constructor arguments (re-used for processing)
		self.setAutoDelete(True)
		self.fn = fn
		self.args = args
		self.kwargs = kwargs
		self.signals = WorkerSignals()

		# Add the callback to our kwargs
		self.kwargs['progress_callback'] = self.signals.progressValue	
		self.kwargs['progress_started'] = self.signals.started
		self.kwargs['progress_error'] = self.signals.error
		self.kwargs['progress_finished'] = self.signals.finished
		
		self.kwargs['progress_setmin'] = self.signals.progressMin
		self.kwargs['progress_setmax'] = self.signals.progressMax
		self.kwargs['progress_setformat'] = self.signals.progressFormat
		self.kwargs['progress_setlabel'] = self.signals.progressLabel
		self.kwargs['progress_setlog'] = self.signals.progressLog
	
	@pyqtSlot()
	def run(self):
		'''
		Initialise the runner function with passed args, kwargs.
		'''
		
		# Retrieve args/kwargs here; and fire processing using them
		result = None
		try:
			result = self.fn(*self.args, **self.kwargs)
		except:
			traceback.print_exc()
			exctype, value = sys.exc_info()[:2]
			self.signals.error.emit((exctype, value, traceback.format_exc()))
		else:
			self.signals.result.emit(result)  # Return the result of the processing
		finally:
			self.signals.finished.emit(result)  # Done

class Callbacks():
	def __init__(self, **kwargs) -> None:
		self.progress_callback = None
		self.progress_setformat = None
		self.progress_setlabel = None
		self.progress_setmin = None
		self.progress_setmax = None
		self.progress_setlog = None
		self.progress_setstarted = None
		self.var = None
		self.setupVars(**kwargs)
	
	def setupVars(self, **kwargs):
		try:
			self.progress_callback = kwargs['progress_callback']
		except:
			pass
		
		try:
			self.progress_setstarted = kwargs['progress_started']
		except:
			pass

		try:
			self.progress_finished = kwargs['progress_finished']
		except:
			pass

		try:
			self.progress_error = kwargs['progress_error']
		except:
			pass

		try:
			self.progress_setformat = kwargs['progress_setformat']
		except:
			pass
		
		try:
			self.progress_setlabel = kwargs['progress_setlabel']
		except:
			pass
		
		try:
			self.progress_setmin = kwargs['progress_setmin']
		except:
			pass
		
		try:
			self.progress_setmax = kwargs['progress_setmax']
		except:
			pass
		
		try:
			self.progress_setlog = kwargs['progress_setlog']
		except:
			pass
	
	def setmax(self, var):
		try:
			self.progress_setmax.emit(var)
		except:
			pass
	
	def setmin(self, var):
		try:
			self.progress_setmin.emit(var)
		except:
			pass

	def setlabel(self, var):
		try:
			self.progress_setlabel.emit(var)
		except:
			pass
	
	def setlog(self, var):
		try:
			self.progress_setlog.emit(var)
		except:
			pass

	def setformat(self, var):
		try:
			self.progress_setformat.emit(var)
		except:
			pass
	
	def setstarted(self, var):
		try:
			self.progress_setstarted.emit(var)
		except:
			pass
	
	def setfinished(self, var):
		try:
			self.progress_finished.emit(var)
		except:
			pass
	
	def seterror(self, var):
		try:
			self.progress_error.emit(var)
		except:
			pass

	def callback(self, var):
		try:
			self.progress_callback.emit(var)
		except Exception as e: 
			print(e)