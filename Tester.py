from Modules.DataPreparers.ProjectPreparer import ProjectPreparer as PP

pp_obj = PP('TI2_5_newtray', workers=28, tempDir='LSS')
pp_obj.runPacePrep('tlancaster6@gatech.edu')
