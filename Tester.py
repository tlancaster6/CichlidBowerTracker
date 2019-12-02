from Modules.FileManagers.ProjFileManager import ProjFileManager as PFM
from Modules.DataPreparers.FigurePreparer import FigurePreparer as FP
from Modules.DataPreparers.ProjectPreparer import ProjectPreparer as PP

pp = PP('MC6_5')
fp = FP(pp.projFileManager)
fp._createClusterFigures()
