import sys
import zipfile
import codecs
from dataclasses import dataclass
import olefile

from os import path, remove
from pathlib import PurePath, Path
from typing import Optional, Union

from lib.Threading import Callbacks



@dataclass
class OleAsset():
	guid: str = ''
	assetType: str = ''
	assetPath: str = ''
	resolvedPath: str = ''

class MaxFileZip():

	def __init__(self, inFileDict: dict, outputZipDir: PurePath, outZipFile: Optional[PurePath]=None, overwrite: bool=False):
		self.inFileDict = inFileDict
		self.outputZipDir = outputZipDir
		self.outZipFile = outZipFile
		self.overwrite = overwrite
		self.callbacks = Callbacks()
				
	def bitToGUID(self, bits):
		'''
		GUID in Microsoft OLE are stored as mixed endian
		first 3 components are little endian and the last
		two are big endian, 4-2-2-2-6
		'''
		def lEndian(bData):
			return codecs.encode((bData)[::-1], 'hex').decode()

		def bEndian(bData):
			return bData.hex()

		if (len(bits)>16):
			bits = bits.lstrip(b'\x00').rstrip(b'\x00')
		
		if (len(bits)<16):
			return None
		else:
			return(lEndian(bits[:4])+lEndian(bits[4:6])+lEndian(bits[6:8])+bEndian(bits[8:10])+bEndian(bits[10:16]))

	def readStreamByByte(self,stream, nBytes: int):
		"""Reads ole stream by n number of bytes\n
		Stops reading once it hits \x00\x00

		Args:
			stream (OleStream): OLE stream to read
			nBytes (int): Number of bytes at a time

		Yields:
			str: UTF16 decoded string
		"""		
		while True:
			c = stream.read(nBytes)
			if c == b'\x00\x00':
				break
			yield (str(c,'utf-16-le','ignore'))

	def readStream(self, oleStream, hasResolvedPath:bool):
		"""Reads OLE stream

		Args:
			oleStream (OleStream): OLE Stream to read
			hasResolvedPath (bool): If ole file has resolved path

		Yields:
			list: ole metadata
		"""		
		bytesRead = 0
		while True:
			oleAsset = OleAsset()

			# First 16 bytes should be the asset ID
			buf = oleStream.read(16)
			if buf == b'':
				break
			
			oleAsset.guid = self.bitToGUID(buf)
			# 4 bytes padding garbage, skip that
			oleStream.read(4) 

			# Read by 2 bytes (16bit encoding) until null
			# Asset type
			buf = ''
			for b in self.readStreamByByte(oleStream, 2):
				buf = buf + b	
			oleAsset.assetType = buf

			#4 bytes padding garbage, skip that
			oleStream.read(4)

			# Read by 2 bytes (16bit encoding) until null
			# Asset filename
			buf=''
			for b in self.readStreamByByte(oleStream, 2):
				buf = buf + b	
			oleAsset.assetPath = buf

			# Read by 2 bytes (16bit encoding) until null
			# Asset resolved filename
			if (hasResolvedPath):
				# 4 bytes padding garbage, skip that
				oleStream.read(4)
				buf = ''
				for b in self.readStreamByByte(oleStream, 2):
					buf = buf + b	
				oleAsset.resolvedPath = buf

			yield oleAsset

	def collectAssetsPathsFromFile(self, file: str, allAssetsPaths: list = []) -> Optional[list]:
		
		if olefile.isOleFile(file):
			with olefile.OleFileIO(file) as ole:
				oleDirs = ole.listdir()
				streamName = ''
				streamData = b''
				hasResolvedPath = False
				if ole.exists('FileAssetMetaData2'):
					streamName = 'FileAssetMetaData2'
				elif ole.exists('FileAssetMetaData3'):
					streamName = 'FileAssetMetaData3'
					hasResolvedPath = True
				else:
					return None

				oleStream = ole.openstream(streamName)	
				
				for oleAsset in self.readStream(oleStream, hasResolvedPath):

					# Use resolved path instead, if available
					assetPath = oleAsset.resolvedPath if oleAsset.resolvedPath != '' else oleAsset.assetPath
					if assetPath not in allAssetsPaths:
						if oleAsset.assetType == 'XRef':
							#add the xref path to the assets list anyway, we want it to be picked up in missing files collection
							#if it doesn't exist
							allAssetsPaths.append(assetPath)
							if Path(assetPath).exists():
								allAssetsPaths = allAssetsPaths + self.collectAssetsPathsFromFile(assetPath, allAssetsPaths)

						else:
							allAssetsPaths.append(assetPath)

			return allAssetsPaths

	def main(self, **kwargs):

		if kwargs:
			self.callbacks = Callbacks(**kwargs)
		
		zfName = self.outZipFile

		if self.outZipFile == None:
			# If not a single zip, create zip file name from max file name
			zipName = PurePath(list(self.inFileDict.values())[0]).name
			zfName = self.outputZipDir.joinpath(zipName + '.zip')
				
		mfName = str(zfName) + 'Missing Files.txt'
		missingFilesCount = 0
		processedFiles = set()
		
		with zipfile.ZipFile(zfName, 'w', zipfile.ZIP_DEFLATED) as archFile, open(mfName, 'w') as missingFilesFile:
			for row, inMaxFile in self.inFileDict.items():
				self.callbacks.setstarted((row,'proc'))

				allAssetsPaths = self.collectAssetsPathsFromFile(inMaxFile, [])

				if allAssetsPaths == None:
					#error message - not a valid max file
					self.callbacks.seterror((row,'error'))
					continue

				# Adding files from directory 'files'
				for count, assetPath in enumerate(allAssetsPaths):
					if assetPath not in processedFiles:
						if path.exists(assetPath):
							archFile.write(assetPath, assetPath.replace(':','',1).replace(r'\\','',1))
							processedFiles.add(assetPath)
						else:
							missingFilesFile.write(assetPath+'\n')
							processedFiles.add(assetPath)
							missingFilesCount +=1
					
					i = round(((count+1)/len(allAssetsPaths)*100),2)
					self.callbacks.callback((row,i))
					
				archFile.write(inMaxFile, inMaxFile.replace(':','',1))
				
			missingFilesFile.close()
			if missingFilesCount > 0:
				archFile.write(mfName, 'Missing Files.txt')
		
		remove(mfName)
		
		for row, inMaxFile in self.inFileDict.items():
			self.callbacks.setfinished((row,'good'))