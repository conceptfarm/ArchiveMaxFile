import sys
import zipfile
import codecs

import olefile

from os import path, remove


class MaxFileZip():

	def __init__(self, inMaxFile, outZipFile, overwrite=False, progress_callback=None):
		self.inMaxFile = inMaxFile
		self.outZipFile = outZipFile
		self.overwrite = overwrite



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

	def readStreamByByte(self,stream,nBytes):
		while True:
			c = stream.read(nBytes)
			if c == b'\x00\x00':
				break
			yield (str(c,'utf-16-le','ignore'))

	def readStream(self, stream, hasResolvedPath):
		bytesRead = 0
		while True:
			assetMetaData=[]

			#First 16 bytes should be the asset ID
			buf = stream.read(16)
			if buf == b'':
				break
			
			assetMetaData.append(self.bitToGUID(buf))
			#4 bytes padding garbage, skip that
			stream.read(4) 

			#Read by 2 bytes (16bit encoding) until null
			#Asset type
			buf=''
			for b in self.readStreamByByte(stream,2):
				buf=buf+b	
			assetMetaData.append(buf)

			#4 bytes padding garbage, skip that
			stream.read(4)

			#Read by 2 bytes (16bit encoding) until null
			#Asset filename
			buf=''
			for b in self.readStreamByByte(stream,2):
				buf=buf+b	
			assetMetaData.append(buf)

			#Read by 2 bytes (16bit encoding) until null
			#Asset resolved filename
			if (hasResolvedPath):
				#4 bytes padding garbage, skip that
				stream.read(4)
				buf=''
				for b in self.readStreamByByte(stream,2):
					buf=buf+b	
				assetMetaData.append(buf)

			yield assetMetaData


	#print( sys.getfilesystemencoding()	)

	def main(self, **kwargs):
		progress_callback = kwargs['progress_callback']
		
		if olefile.isOleFile(self.inMaxFile):
			with olefile.OleFileIO(self.inMaxFile) as ole:
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
					exit()

				oleStream = ole.openstream(streamName)
				
				allAssetMetaData=[]
				
				for a in self.readStream(oleStream,hasResolvedPath):
					#print(a)
					allAssetMetaData.append(a)

				zfName = self.outZipFile
				mfName = 'Missing Files.txt'
				missingFilesCount = 0

				with zipfile.ZipFile(zfName, 'w', zipfile.ZIP_DEFLATED) as archFile, open(mfName, 'w') as missingFilesFile:

					# Adding files from directory 'files'
					for count, data in enumerate(allAssetMetaData):
						if path.exists(data[2]):
							archFile.write(data[2], data[2].replace(':','',1))
						else:
							missingFilesFile.write(data[2]+'\n')
							missingFilesCount +=1

						#i = (count+1)/len(allAssetMetaData)*100
						#print(i)
						
						if progress_callback != None:
							try:
								i = round(((count+1)/len(allAssetMetaData)*100),2)
								progress_callback.emit(i)
							except:
								print('error')
						
					missingFilesFile.close()
					
					archFile.write(self.inMaxFile, self.inMaxFile.replace(':','',1))
					if missingFilesCount > 0:
						archFile.write(mfName)
					#archFile.close()
				remove(mfName)

'''

#use:
inF = 'C:/Python37/15-01-21_CIYE_Set.max'
outF = 'C:/Python37/15-01-21_CIYE_Set.zip'

gr = MaxFileZip(inF, outF, False, None)
gr.main()

'''

