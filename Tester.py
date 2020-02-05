from Modules.FileManagers.FileManager import FileManager as FM
from Modules.DataPreparers.FigurePreparer import FigurePreparer as FP
from Modules.DataPreparers.ProjectPreparer import ProjectPreparer as PP
from Modules.DataPreparers.PrepPreparer import PrepPreparer as PrP

# pp_obj = PP('MC6_5', 14, 'LSS')
# pp_obj.projFileManager.downloadData('Prep')
# prp_obj = PrP(pp_obj.projFileManager)
# prp_obj.validateInputData()
# prp_obj.prepData()

projFileManager = FM().retProjFileManager('MC6_5')
fp_obj = FP(projFileManager)
fp_obj.createAllFigures()

# t0 = ca_obj.lp_obj.frames[0].time
# t1 = ca_obj.lp_obj.frames[-1].time

