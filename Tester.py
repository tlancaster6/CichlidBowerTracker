from Modules.FileManagers.FileManager import FileManager as FM
from Modules.DataPreparers.FigurePreparer import FigurePreparer as FP
from Modules.DataPreparers.ProjectPreparer import ProjectPreparer as PP
from Modules.DataPreparers.PrepPreparer import PrepPreparer as PrP
from Modules.DataObjects.LogParser import LogParser as LP

# pp_obj = PP('_newtray_MCxCVF2_16_4')

# prp_obj = PrP(pp_obj.projFileManager)
# prp_obj.validateInputData()
# prp_obj.prepData()

projFileManager = FM().retProjFileManager('_newtray_MCxCVF2_16_4')
fp_obj = FP(projFileManager)
fp_obj._createClusterFigures()

# t0 = ca_obj.lp_obj.frames[0].time
# t1 = ca_obj.lp_obj.frames[-1].time

