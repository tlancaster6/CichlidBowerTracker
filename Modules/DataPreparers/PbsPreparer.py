import os
from string import Template
from Modules.DataObjects.LogParser import LogParser as LP

class PbsPreparer:

    def __init__(self, projFileManager):
        self.projFileManager = projFileManager

    def createPBS(self):
        assert os.path.exists(self.projFileManager.localLogfile)
        array_max = str(LP(self.projFileManager.localLogfile).numDays - 1)
        d = {'ARRAY_MAX': array_max,
             'PROJECT_ID': self.projFileManager.projectID,
             'TMPDIR': self.projFileManager.localTempDir}
        infile = open(os.path.join(os.getcwd(), 'Modules', 'PbsTemplates', 'ClusterAnalysis.pbs'), 'r')
        mod = Template(infile.read()).safe_substitute(d)
        infile.close()
        outfile = open(self.projFileManager.localPbsDir + 'ClusterAnalysis.pbs', 'w')
        outfile.write(mod)
        outfile.close()



