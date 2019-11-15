from Modules.FileManagers.ProjFileManager import ProjFileManager as PFM
from Modules.DataPreparers.FigurePreparer import FigurePreparer as FP


lmd = '/home/tlancaster6/CichlidBowerTrackerData/'
cmd = 'cichlidVideo:BioSci-McGrath/Apps/CichlidPiData/'
pid = 'MC22_2'
pfm = PFM(lmd, cmd, pid)
fp = FP(pfm)
