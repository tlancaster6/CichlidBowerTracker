import os
from string import Template
from Modules.DataObjects.LogParser import LogParser as LP

class PbsPreparer:

    def __init__(self, projFileManager, workers):
        self.projFileManager = projFileManager
        self.workers = workers
        self.__version__ = '1.0.0'

    def validateInputData(self):
        assert os.path.exists(self.projFileManager.localLogfile)
        assert os.path.exists(self.projFileManager.localPbsDir)

        self.uploads = [(self.projFileManager.localPbsDir, self.projFileManager.cloudPbsDir, '0')]

    def createPBS(self):

        array_max = str(LP(self.projFileManager.localLogfile).numDays - 1)
        d = {'ARRAY_MAX': array_max,
             'PROJECT_ID': self.projFileManager.projectID,
             'TMPDIR': self.projFileManager.localTempDir,
             'WORKERS': self.workers}
        infile = open(os.path.join(os.getcwd(), 'Modules', 'PbsTemplates', 'ClusterAnalysis.pbs'), 'r')
        mod = Template(infile.read()).safe_substitute(d)
        infile.close()
        outfile = open(self.projFileManager.localPbsDir + 'ClusterAnalysis.pbs', 'w')
        outfile.write(mod)
        outfile.close()

        # Generate Post-Cluster-Analysis PBS
        d = {'PROJECT_ID': self.projFileManager.projectID}
        infile = open(os.path.join(os.getcwd(), 'Modules', 'PbsTemplates', 'PostClusterAnalysis.pbs'), 'r')
        mod = Template(infile.read()).safe_substitute(d)
        infile.close()
        outfile = open(self.projFileManager.localPbsDir + 'PostClusterAnalysis.pbs', 'w')
        outfile.write(mod)
        outfile.close()



