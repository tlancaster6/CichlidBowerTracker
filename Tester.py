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
# dfs = []
# for trial in ['CV10_3', 'TI2_4', 'TI3_3', 'MC6_5', 'MC16_2', 'MCxCVF1_12a_1', 'MCxCVF1_12b_1']:
#     print(trial)
#     projFileManager = FM().retProjFileManager(trial)
#     plotter = Plotter(projFileManager)
#     dfs.append(plotter.get_regression_data(whole_trial=True))
# df = pd.concat(dfs)
# g = sns.clustermap(np.abs(df).corr(), cmap='viridis', annot=True, fmt='.3f', cbar=True, vmin=-1, vmax=1, figsize=(10, 10))
# g.savefig('/home/tlancaster6/Desktop/heatmaps/kde_heatmap_all_trials.pdf')
# plt.close()
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

dfs = []
for trial in ['MCxCVF1_12a_1', 'MCxCVF1_12b_1']:
    print(trial)
    projFileManager = FM().retProjFileManager(trial)
    plotter = Plotter(projFileManager)
    dfs.append(plotter.get_regression_data(whole_trial=True))
df = pd.concat(dfs)
g = sns.clustermap(np.abs(df).corr(), cmap='viridis', annot=True, fmt='.3f', cbar=True, vmin=-1, vmax=1, figsize=(10, 10))
g.savefig('/home/tlancaster6/Desktop/heatmaps/kde_heatmap_all_hybrids.pdf')
plt.close()

# model = ols('depth ~ {}'.format('+'.join(plotter.ca_obj.bids)), data=df).fit()
# t0 = ca_obj.lp_obj.frames[0].time
# t1 = ca_obj.lp_obj.frames[-1].time

