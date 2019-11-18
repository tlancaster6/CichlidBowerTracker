from Modules.FileManagers.ProjFileManager import ProjFileManager as PFM
from Modules.DataPreparers.FigurePreparer import FigurePreparer as FP
from Modules.DataPreparers.ProjectPreparer import ProjectPreparer as PP

pp = PP('MC22_2')
pp.downloadData('Figures')
fp = FP(pp.projFileManager)
fp.validateInputData()
fp._createDepthFigures()
