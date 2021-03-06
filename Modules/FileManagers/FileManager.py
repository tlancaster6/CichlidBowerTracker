import os, subprocess, pdb
from Modules.FileManagers.ProjFileManager import ProjFileManager as ProjFM
from Modules.FileManagers.mlFileManager import MLFileManager as MLFM
from Modules.FileManagers.AnFileManager import AnFileManager as AnFM

class FileManager():
	def __init__(self):
		self.system = 'computer' # Initially assume  that we are on a laptop/desktop/server
		self.rcloneRemote = 'cichlidVideo'
		# self.cloudMasterDir = self.rcloneRemote + ':McGrath/Apps/CichlidPiData/'
		self.cloudMasterDir = self.rcloneRemote + ':BioSci-McGrath/Apps/CichlidPiData/'
		if 'pace' in os.uname()[1]:
			self.localMasterDir = os.getenv('HOME') + '/scratch/'
		else:
			self.localMasterDir = os.getenv('HOME') + '/Temp/CichlidAnalyzer/'
		self.mountedDropboxMasterDir = os.getenv('HOME') + '/Dropbox (GaTech)/McGrath/Apps/CichlidPiData/'
		
		self.analysisDir = '__AnalysisLog/'
		self.localAnalysisLogDir = self.localMasterDir + self.analysisDir
		self.cloudAnalysisLogDir = self.cloudMasterDir + self.analysisDir
		self.analysisSummaryFile = 'AnalyzedProjects.xlsx'
		self.localAnalysisSummaryFile = self.localAnalysisLogDir + self.analysisSummaryFile		

		self.localUploadDir = self.localMasterDir + '__UploadCommands/'

		self._identifyPiDirectory() # Determine if we are on a raspberry pi and if so identify directory
		
	def retProjFileManager(self, projectID, tempDir=None):
		return ProjFM(self.localMasterDir, self.cloudMasterDir, projectID, tempDir)

	def retMLFileManager(self):
		return MLFM(self.localMasterDir, self.cloudMasterDir)

	def retAnFileManager(self):
		return AnFM(self.localMasterDir, self.cloudMasterDir)

	def createDirs(self):
		self._createDirectory(self.localUploadDir)
		self._createDirectory(self.localAnalysisLogDir)

	def _identifyPiDirectory(self):
		writableDirs = []
		try:
			possibleDirs = os.listdir('/media/pi')
		except FileNotFoundError:
			return

		for d in possibleDirs:

			try:
				with open('/media/pi/' + d + '/temp.txt', 'w') as f:
					print('Test', file = f)
				with open('/media/pi/' + d + '/temp.txt', 'r') as f:
					for line in f:
						if 'Test' in line:
							writableDirs.append(d)
			except:
				pass
			try:
				os.remove('/media/pi/' + d + '/temp.txt')
			except FileNotFoundError:
				continue
		
		if len(writableDirs) == 1:
			self.localMasterDir = '/media/pi/' + d + '/'
			self.system = 'pi'
		elif len(writableDirs) == 0:
			raise Exception('No writable drives in /media/pi/')
		else:
			raise Exception('Multiple writable drives in /media/pi/. Options are: ' + str(writableDirs))

	def _createDirectory(self, directory):
		print('creating {}'.format(directory))
		if not os.path.exists(directory):
			os.makedirs(directory)

	def _downloadFile(self, dfile):
		print('downloading {}'.format(dfile))
		subprocess.call(['rclone', 'copy', self.cloudMasterDir + dfile, self.localMasterDir], stderr = subprocess.PIPE)
		if not os.path.exists(self.localMasterDir + dfile):
			raise FileNotFoundError('Unable to download ' + dfile + ' from ' + self.cloudMasterDir)

	def downloadDirectory(self, directory):
		print('downloading {}'.format(directory))
		# First try to download tarred Directory
		tar_directory = directory[:-1] + '.tar'
		output = subprocess.run(['rclone', 'copy', self.cloudMasterDir + tar_directory, self.localMasterDir, '--fast-list', '--checkers', '40', '--transfers', '40', '--tpslimit', '10'],stdout=subprocess.PIPE, stderr=subprocess.STDOUT, encoding='utf-8')
		if os.path.exists(self.localMasterDir + tar_directory):
			# print(output.stdout)
			output = subprocess.run(['tar', '-xf', self.localMasterDir + tar_directory, '-C', self.localMasterDir], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, encoding='utf-8')
			# print(output.stdout)
			if not os.path.exists(self.localMasterDir + directory):
				raise FileNotFoundError('Unable to untar ' + tar_directory)
			else:
				subprocess.run(['rm', '-f', self.localMasterDir + tar_directory])

		else:
			output = subprocess.run(['rclone', 'copy', self.cloudMasterDir + directory, self.localMasterDir + directory],stdout=subprocess.PIPE, stderr=subprocess.STDOUT, encoding='utf-8')
			# print(output.stdout)
			if not os.path.exists(self.localMasterDir + directory):
				raise FileNotFoundError('Unable to download ' + directory + ' from ' + self.cloudMasterDir)

	def uploadData(self, directory1, directory2, tar=False):
		print('uploading {} to {}'.format(directory1, directory2))
		if tar:
			if directory1[-1] == '/':
				directory1 = directory1[:-1]

			directory1_path = '/'.join(directory1.split('/')[0:-1])

			output = subprocess.run(['tar', '-cf', directory1 + '.tar', '-C', directory1_path, directory1.split('/')[-1]], stderr=subprocess.PIPE)
			command = ['rclone', 'copy', directory1 +'.tar', directory2]
		else:
			command = ['rclone', 'copy', directory1, directory2]
		#print(command)
		output = subprocess.run(command, stdout = subprocess.PIPE, stderr = subprocess.PIPE, encoding = 'utf-8')
		if output.stderr != '':
			print(command)
			print(output.stderr)
			return 1
		return 0
