from Modules.DataPreparers.FigurePreparer import FigurePreparer as FP
from Modules.DataPreparers.ProjectPreparer import ProjectPreparer as PP
from Modules.DataObjects.OutfileParser import OutfileParser as OP

pp = PP('TI2_5_newtray', 64, 'LSS')
pp.runPacePrep('tlancaster6@gatech.edu')



# op = OP(pp.projFileManager)
# op.parseOutfiles()