from Modules.DataPreparers.FigurePreparer import FigurePreparer as FP
from Modules.DataPreparers.ProjectPreparer import ProjectPreparer as PP

pp = PP('MC6_5')
fp = FP(pp.projFileManager)
ca = fp.ca_obj

fp._createClusterFigures()



