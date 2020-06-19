from Modules.FileManagers.FileManager import FileManager as FM
from Modules.Plotter.Plotter import Plotter
from Modules.DataPreparers.FigurePreparer import FigurePreparer as FP
from Modules.DataPreparers.ProjectPreparer import ProjectPreparer as PP
from Modules.DataPreparers.PrepPreparer import PrepPreparer as PrP
from Modules.DataObjects.LogParser import LogParser as LP
import pandas as pd
import numpy as np
from statsmodels.formula.api import ols
import seaborn as sns
import matplotlib.pyplot as plt
from scipy.stats import pearsonr
import sys

# pp_obj = PP('_newtray_MCxCVF2_16_4')

# prp_obj = PrP(pp_obj.projFileManager)
# prp_obj.validateInputData()
# prp_obj.prepData()

# exit_status = 0
# for trial in ['CV10_3', 'TI2_4', 'TI3_3', 'MC6_5', 'MC16_2', 'MCxCVF1_12a_1', 'MCxCVF1_12b_1']:
#     projFileManager = FM().retProjFileManager(trial)
#     fp = FP(projFileManager)
#     fp.validateInputData()
#     if 'Model18_All_pred' not in fp.ca_obj.clusterData.keys():
#         print('check keys for {}'.format(trial))
#         exit_status = 1
#
# if exit_status != 0:
#     sys.exit()
# else:
#     print('all required data present')
#
# for trial in ['CV10_3', 'TI2_4', 'TI3_3', 'MC6_5', 'MC16_2', 'MCxCVF1_12a_1', 'MCxCVF1_12b_1']:
#     projFileManager = FM().retProjFileManager(trial)
#     projFileManager.downloadData(dtype='Figures')

# dfs = []
# for trial in ['CV10_3', 'TI2_4', 'TI3_3', 'MC6_5', 'MC16_2', 'MCxCVF1_12a_1', 'MCxCVF1_12b_1']:
#     print(trial)
#     projFileManager = FM().retProjFileManager(trial)
#     figurePrepper = FP(projFileManager)
#     figurePrepper.createAllFigures()
#     plotter = Plotter(projFileManager)
#     dfs.append(plotter.get_regression_data(whole_trial=True))
# df = pd.concat(dfs)
# g = sns.clustermap(np.abs(df).corr(), cmap='viridis', annot=True, fmt='.3f', cbar=True, vmin=-1, vmax=1, figsize=(10, 10))
# plt.close()
# g.savefig('/Users/tuckerlancaster/Desktop/heatmaps/kde_heatmap_all_trials_abs.pdf')
# g = sns.clustermap(df.corr(), cmap='viridis', annot=True, fmt='.3f', cbar=True, vmin=-1, vmax=1, figsize=(10, 10))
# g.savefig('/Users/tuckerlancaster/Desktop/heatmaps/kde_heatmap_all_trials_signed.pdf')
# plt.close()
#
# with open('/Users/tuckerlancaster/Desktop/heatmaps/kde_correlation_values_all_trials_abs.txt', 'w') as f:
#     f.write('x, y, r, p\n')
#     for x in df.keys():
#         for y in df.keys():
#             r, p = pearsonr(np.abs(df[x]), np.abs(df[y]))
#             f.write('{}, {}, {}, {}\n'.format(x, y, r, p))
#
# with open('/Users/tuckerlancaster/Desktop/heatmaps/kde_correlation_values_all_trials_signed.txt', 'w') as f:
#     f.write('x, y, r, p\n')
#     for x in df.keys():
#         for y in df.keys():
#             r, p = pearsonr(df[x], df[y])
#             f.write('{}, {}, {}, {}\n'.format(x, y, r, p))



# pid = 'MC6_5'
# pfm = FM().retProjFileManager(pid)
# fp = FP(pfm)
# fp.createAllFigures()

#
# dfs = []
# for trial in ['CV10_3', 'TI2_4', 'TI3_3']:
#     print(trial)
#     projFileManager = FM().retProjFileManager(trial)
#     plotter = Plotter(projFileManager)
#     dfs.append(plotter.get_regression_data(whole_trial=True))
# df = pd.concat(dfs)
# g = sns.clustermap(np.abs(df).corr(), cmap='viridis', annot=True, fmt='.3f', cbar=True, vmin=-1, vmax=1, figsize=(10, 10))
# g.savefig('/home/tlancaster6/Desktop/heatmaps/kde_heatmap_pit_diggers.pdf')
# plt.close()
#
# dfs = []
# for trial in ['MC6_5', 'MC16_2']:
#     print(trial)
#     projFileManager = FM().retProjFileManager(trial)
#     plotter = Plotter(projFileManager)
#     dfs.append(plotter.get_regression_data(whole_trial=True))
# df = pd.concat(dfs)
# g = sns.clustermap(np.abs(df).corr(), cmap='viridis', annot=True, fmt='.3f', cbar=True, vmin=-1, vmax=1, figsize=(10, 10))
# g.savefig('/home/tlancaster6/Desktop/heatmaps/kde_heatmap_all_castle_builders.pdf')
# plt.close()

# dfs = []
# for trial in ['MCxCVF1_12a_1', 'MCxCVF1_12b_1']:
#     print(trial)
#     projFileManager = FM().retProjFileManager(trial)
#     plotter = Plotter(projFileManager)
#     dfs.append(plotter.get_regression_data(whole_trial=True))
# df = pd.concat(dfs)
# g = sns.clustermap(np.abs(df).corr(), cmap='viridis', annot=True, fmt='.3f', cbar=True, vmin=-1, vmax=1, figsize=(10, 10))
# g.savefig('/home/tlancaster6/Desktop/heatmaps/kde_heatmap_all_hybrids.pdf')
# plt.close()

# model = ols('depth ~ {}'.format('+'.join(plotter.ca_obj.bids)), data=df).fit()
# t0 = ca_obj.lp_obj.frames[0].time
# t1 = ca_obj.lp_obj.frames[-1].time

pids = ['CV10_3', 'CV_fem_con1', 'CV_fem_con2', 'CV_fem_con3',
       'CV_male_con1', 'CV_male_con2', 'CV_male_con3', 'CV_male_con4',
       'CV_social_male_con1', 'CV_social_male_con1_2',
       'CV_social_male_con2', 'CV_social_male_con3',
       'CV_social_male_con3_2', 'MC16_2', 'MC6_5', 'MC9_1', 'MC_fem_con1',
       'MC_fem_con2', 'MC_fem_con3', 'MC_male_con1', 'MC_male_con2',
       'MC_male_con3', 'MC_male_con4', 'MC_social_male_con1',
       'MC_social_male_con1_2', 'MC_social_male_con2',
       'MC_social_male_con3', 'MCxCVF1_12a_1', 'MCxCVF1_12b_1', 'TI2_4',
       'TI3_3', 'TI_male_con1', 'TI_male_con2', 'TI_social_fem_con1',
       'TI_social_male_con1', 'TI_social_male_con2']

for pid in pids:
    pp = PP(pid)
    pp.downloadData('Prep')
    prp = PrP(pp.projFileManager)
    prp.validateInputData()
    prp._cropVideo()
    pp.createUploadFile(prp.uploads)
    pp.backupAnalysis()

