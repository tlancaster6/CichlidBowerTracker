import datetime, os, subprocess
from time import asctime

from Modules.FileManagers.FileManager import FileManager as FM
from Modules.DataPreparers.PrepPreparer import PrepPreparer as PrP
from Modules.DataPreparers.DepthPreparer import DepthPreparer as DP
from Modules.DataPreparers.ClusterPreparer import ClusterPreparer as CP
from Modules.DataPreparers.MLClusterPreparer import MLClusterPreparer as MLP
from Modules.DataPreparers.FigurePreparer import FigurePreparer as FP
from Modules.DataPreparers.PbsPreparer import PbsPreparer as PBS
from Modules.DataPreparers.OutfilePreparer import OutfilePreparer as OP

class ProjectPreparer():
	# This class takes in a projectID and runs all the appropriate analysis

	def __init__(self, projectID, workers=None, tempDir=None):

		self.projectID = projectID
		self.workers = workers
		self.tempDir = tempDir
		self.fileManager = FM()
		self.projFileManager = self.fileManager.retProjFileManager(projectID, tempDir)
		self.mlFileManager = self.fileManager.retMLFileManager()
		self.log = open(self.projFileManager.analysisLog, 'a')

	def downloadData(self, dtype):
		self.log.write(asctime() + ' -- Downloading Data for {}'.format(self.projectID))
		self.fileManager.createDirs()
		self.projFileManager.downloadData(dtype)
		if dtype in ['Download', 'MLClassification']:
			self.mlFileManager.downloadData()

	def runPrepAnalysis(self, pbs_only, email=None):
		self.fileManager.createDirs()
		self.projFileManager.downloadData('Prep')

		if not pbs_only:
			prp_obj = PrP(self.projFileManager)
			prp_obj.validateInputData()
			prp_obj.prepData()
			self.createUploadFile(prp_obj.uploads)
			self.createAnalysisUpdate('Prep', prp_obj)

		print('prepping PBS scripts')
		pbs_obj = PBS(self.projFileManager, self.workers, email)
		pbs_obj.validateInputData()
		pbs_obj.createPBS()
		self.createUploadFile(pbs_obj.uploads)
		self.createAnalysisUpdate('PacePrep', pbs_obj)

		self.backupAnalysis()
		#self.localDelete()

	def runDepthAnalysis(self):
		self.log.write(asctime() + ' -- Running Depth Analysis for {}'.format(self.projectID))
		dp_obj = DP(self.projFileManager, self.workers)
		dp_obj.validateInputData()
		dp_obj.createSmoothedArray()
		dp_obj.createRGBVideo()
		self.createUploadFile(dp_obj.uploads)
		self.createAnalysisUpdate('Depth', dp_obj)

	def runClusterAnalysis(self, videoIndex):
		self.log.write(asctime() + ' -- Running Cluster Analysis for {0}, video {1}'.format(self.projectID, videoIndex))
		cp_obj = CP(self.projFileManager, self.workers, videoIndex)
		cp_obj.validateInputData()
		cp_obj.runClusterAnalysis()
		self.createUploadFile(cp_obj.uploads)
		self.createAnalysisUpdate('Cluster', cp_obj)

	def createAnnotationFrames(self):
		cp_obj = CP(self.projFileManager, self.workers)
		cp_obj.validateInputData()
		cp_obj.createAnnotationFrames()
		self.createUploadFile(cp_obj.uploads)


	def runMLClusterClassifier(self):
		self.log.write(asctime() + ' -- Running ML Classification for {}'.format(self.projectID))
		mlc_obj = MLP(self.projFileManager, self.mlFileManager)
		mlc_obj.validateInputData()
		mlc_obj.predictVideoLabels()
		self.createUploadFile(mlc_obj.uploads)
		self.createAnalysisUpdate('MLClassifier', mlc_obj)


	def runMLFishDetection(self):
		pass

	def runFiguresCreation(self):
		self.log.write(asctime() + ' -- Running figure creation for {}'.format(self.projectID))
		fc_obj = FP(self.projFileManager)
		fc_obj.validateInputData()
		fc_obj.createAllFigures()

		self.createUploadFile(fc_obj.uploads)
		self.createAnalysisUpdate('Figures', fc_obj)

	def runObjectLabeling(self):
		self.projFileManager.downloadData('ObjectLabeler')
		lc_obj =LC(self.projFileManager)
		lc_obj.validateInputData()

	def parseOutfiles(self):
		self.log.write(asctime() + ' -- Parsing outfiles for {}'.format(self.projectID))
		op_obj = OP(self.projFileManager)
		op_obj.validateInputData()
		op_obj.parseOutfiles()

	def backupAnalysis(self):
		self.log.write(asctime() + ' -- Backing up analysis for {}'.format(self.projectID))
		uploadCommands = set()

		uploadFiles = [x for x in os.listdir(self.fileManager.localUploadDir) if 'UploadData' in x]

		for uFile in uploadFiles:
			with open(self.fileManager.localUploadDir + uFile) as f:
				line = next(f)
				for line in f:
					tokens = line.rstrip().split(',')
					tokens[2] = bool(int(tokens[2]))
					uploadCommands.add(tuple(tokens))

		for command in uploadCommands:
			self.fileManager.uploadData(command[0], command[1], command[2])

		for uFile in uploadFiles:
			pass
			subprocess.run(['rm', '-rf', self.fileManager.localUploadDir + uFile])

		self.fileManager.uploadData(self.fileManager.localAnalysisLogDir, self.fileManager.cloudAnalysisLogDir, False)
		subprocess.run(['rm', '-rf', self.projFileManager.localMasterDir])

	def localDelete(self):
		self.log.write(asctime() + ' -- Deleting local files for {}'.format(self.projectID))
		subprocess.run(['rm', '-rf', self.projFileManager.localMasterDir])

	def createUploadFile(self, uploads):
		self.log.write(asctime() + ' -- Creating upload files for {}'.format(self.projectID))
		with open(self.fileManager.localUploadDir + 'UploadData_' + str(datetime.datetime.now().timestamp()) + '.csv', 'w') as f:
			print('Local,Cloud,Tar', file = f)
			for upload in uploads:
				print(upload[0] + ',' + upload[1] + ',' + str(upload[2]), file = f)

	def createAnalysisUpdate(self, aType, procObj):
		self.log.write(asctime() + ' -- creating {} type analysis update for {}'.format(aType, self.projectID))
		now = datetime.datetime.now()
		with open(self.fileManager.localAnalysisLogDir + 'AnalysisUpdate_' + str(now.timestamp()) + '.csv', 'w') as f:
			print('ProjectID,Type,Version,Date', file = f)
			print(self.projectID + ',' + aType + ',' + procObj.__version__ + '_' + os.getenv('USER') + ',' + str(now), file= f)
