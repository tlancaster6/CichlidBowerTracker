import os
import numpy as np
from string import Template
from Modules.DataObjects.LogParser import LogParser as LP

class PbsPreparer:

    def __init__(self, projFileManager, workers, email):
        self.projFileManager = projFileManager
        self.workers = workers
        self.email = email
        self.__version__ = '1.0.0'

    def validateInputData(self):
        assert os.path.exists(self.projFileManager.localLogfile)
        assert os.path.exists(self.projFileManager.localPbsDir)

        self.uploads = [(self.projFileManager.localPbsDir, self.projFileManager.cloudPbsDir, '0')]

    def createPBS(self):

        # Generate Depth Analysis PBS
        d = {'PROJECT_ID': self.projFileManager.projectID, 'EMAIL': self.email}
        infile = open(os.path.join(os.getcwd(), 'Modules', 'PbsTemplates', 'DepthAnalysis.pbs'), 'r')
        mod = Template(infile.read()).safe_substitute(d)
        infile.close()
        if self.email is None:
            mod = mod.replace('#PBS -M None\n#PBS -m abe\n', '')
        outfile = open(self.projFileManager.localPbsDir + 'DepthAnalysis.pbs', 'w')
        outfile.write(mod)
        outfile.close()

        # generate Cluster Analysis PBS
        array_max = str(LP(self.projFileManager.localLogfile).numDays - 1)
        d = {'ARRAY_MAX': array_max,
             'PROJECT_ID': self.projFileManager.projectID,
             'TMPDIR': self.projFileManager.localTempDir,
             'WORKERS': self.workers,
             'LOCAL_SCRATCH': str(int(np.ceil(80000 / self.workers))) + 'm',
             'EMAIL': self.email,
             'BRAND': 'amd' if self.workers > 28 else 'intel'}
        infile = open(os.path.join(os.getcwd(), 'Modules', 'PbsTemplates', 'ClusterAnalysis.pbs'), 'r')
        mod = Template(infile.read()).safe_substitute(d)
        infile.close()
        if self.email is None:
            mod = mod.replace('#PBS -M None\n#PBS -m abe\n', '')
        outfile = open(self.projFileManager.localPbsDir + 'ClusterAnalysis.pbs', 'w')
        outfile.write(mod)
        outfile.close()

        # Generate Post-Cluster-Analysis PBS
        d = {'PROJECT_ID': self.projFileManager.projectID, 'EMAIL': self.email}
        infile = open(os.path.join(os.getcwd(), 'Modules', 'PbsTemplates', 'PostClusterAnalysis.pbs'), 'r')
        mod = Template(infile.read()).safe_substitute(d)
        infile.close()
        if self.email is None:
            mod = mod.replace('#PBS -M None\n#PBS -m abe\n', '')
        outfile = open(self.projFileManager.localPbsDir + 'PostClusterAnalysis.pbs', 'w')
        outfile.write(mod)
        outfile.close()

        # Generate ML Cluster Classifer PBS
        d = {'PROJECT_ID': self.projFileManager.projectID,
             'EMAIL': self.email,
             'TMPDIR': self.projFileManager.localTempDir}
        infile = open(os.path.join(os.getcwd(), 'Modules', 'PbsTemplates', 'MLClusterClassifier.pbs'), 'r')
        mod = Template(infile.read()).safe_substitute(d)
        infile.close()
        if self.email is None:
            mod = mod.replace('#PBS -M None\n#PBS -m abe\n', '')
        outfile = open(self.projFileManager.localPbsDir + 'MLClusterClassifier.pbs', 'w')
        outfile.write(mod)
        outfile.close()

        # Generate Figure Prep PBS
        d = {'PROJECT_ID': self.projFileManager.projectID, 'EMAIL': self.email}
        infile = open(os.path.join(os.getcwd(), 'Modules', 'PbsTemplates', 'FigurePreparer.pbs'), 'r')
        mod = Template(infile.read()).safe_substitute(d)
        infile.close()
        if self.email is None:
            mod = mod.replace('#PBS -M None\n#PBS -m abe\n', '')
        outfile = open(self.projFileManager.localPbsDir + 'FigurePreparer.pbs', 'w')
        outfile.write(mod)
        outfile.close()

        # Generate Outfile Prep PBS
        d = {'PROJECT_ID': self.projFileManager.projectID, 'EMAIL': self.email}
        infile = open(os.path.join(os.getcwd(), 'Modules', 'PbsTemplates', 'OutfilePreparer.pbs'), 'r')
        mod = Template(infile.read()).safe_substitute(d)
        infile.close()
        if self.email is None:
            mod = mod.replace('#PBS -M None\n#PBS -m abe\n', '')
        outfile = open(self.projFileManager.localPbsDir + 'OutfilePreparer.pbs', 'w')
        outfile.write(mod)
        outfile.close()

        # Generate Backup PBS
        d = {'PROJECT_ID': self.projFileManager.projectID, 'EMAIL': self.email}
        infile = open(os.path.join(os.getcwd(), 'Modules', 'PbsTemplates', 'Backup.pbs'), 'r')
        mod = Template(infile.read()).safe_substitute(d)
        infile.close()
        if self.email is None:
            mod = mod.replace('#PBS -M None\n#PBS -m abe\n', '')
        outfile = open(self.projFileManager.localPbsDir + 'Backup.pbs', 'w')
        outfile.write(mod)
        outfile.close()