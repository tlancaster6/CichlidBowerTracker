# from Modules.DataPreparers.FigurePreparer import FigurePreparer as FP
from Modules.DataPreparers.ProjectPreparer import ProjectPreparer as PP
# from Modules.DataObjects.OutfileParser import OutfileParser as OP
#
pp = PP('TI2_5_newtray', 64, 'LSS')
pp.runPacePrep()
# op = OP(pp.projFileManager)
# op.parseOutfiles()

# import getpass, spur, subprocess
#
# uname = 'tlancaster6'
# pword = getpass.getpass()
# projectID = 'TI2_5_newtray_backup'
# pbs_dir = 'scratch/' + projectID + '/PBS'
# r6_shell = spur.SshShell(hostname='login-s.pace.gatech.edu', username=uname, password=pword)
# testProcess = r6_shell.run(['qsub', 'Tester.pbs'], cwd=pbs_dir, encoding='utf8')
# print(testProcess.output)