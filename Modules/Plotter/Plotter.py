from Modules.DataObjects.LogParser import LogParser as LP
from Modules.DataObjects.DepthAnalyzer import DepthAnalyzer as DA
from Modules.DataObjects.ClusterAnalyzer import ClusterAnalyzer as CA

from matplotlib import (cm, colors, gridspec, ticker)
import statsmodels.api as sm
from statsmodels.formula.api import ols
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import seaborn as sns
import datetime
import os

class Plotter:

    def __init__(self, projFileManager):
        self.__version__ = '1.0.2'
        self.projFileManager = projFileManager
        self.lp_obj = LP(projFileManager.localLogfile)
        self.da_obj = DA(projFileManager)
        self.ca_obj = CA(projFileManager)
        self.uploads = []

    def validateInputData(self):
        assert os.path.exists(self.projFileManager.localLogfile)
        assert os.path.exists(self.projFileManager.localFiguresDir)
        assert os.path.exists(self.projFileManager.localSmoothDepthFile)
        assert os.path.exists(self.projFileManager.localAnalysisDir)
        assert os.path.exists(self.projFileManager.localAllLabeledClustersFile)
        assert os.path.exists(self.projFileManager.localTransMFile)
        self.uploads = [(self.projFileManager.localAnalysisDir, self.projFileManager.cloudAnalysisDir, 0),
                        (self.projFileManager.localFiguresDir, self.projFileManager.cloudFiguresDir, 0)]

    def get_regression_data(self, whole_trial=False, td=10):
        df = {'depth': []}
        for bid in self.ca_obj.bids:
            df.update({bid: []})

        if whole_trial:
            start_day = self.lp_obj.frames[0].time.replace(hour=0, minute=0, second=0, microsecond=0)
            for i in range(0, self.lp_obj.numDays):
                t0 = start_day + datetime.timedelta(hours=24 * i + 8)
                t1 = t0 + datetime.timedelta(hours=10)
                df['depth'].append(list(self.da_obj.returnHeightChange(t0, t1, cropped=True)[10:-10, 10:-10].ravel()))
            df['depth'] = [sum(i) for i in zip(*df['depth'])]
            t0 = self.lp_obj.frames[0].time
            t1 = self.lp_obj.frames[-1].time
            for bid in self.ca_obj.bids:
                df[bid].extend(list(self.ca_obj.returnClusterKDE(t0, t1, bid, cropped=True)[10:-10, 10:-10].ravel()))

        else:
            start_day = self.lp_obj.frames[0].time.replace(hour=0, minute=0, second=0, microsecond=0)
            for i in range(1, self.lp_obj.numDays - 1):
                for j in range(int(10 / td)):
                    t0 = start_day + datetime.timedelta(hours=24 * i + j * td + 8)
                    t1 = start_day + datetime.timedelta(hours=24 * i + (j + 1) * td + 8)
                    df['depth'].extend(list(self.da_obj.returnHeightChange(
                        t0, t1, cropped=True)[10:-10, 10:-10].ravel()))
                    for bid in self.ca_obj.bids:
                        df[bid].extend(list(self.ca_obj.returnClusterKDE(
                            t0, t1, bid, cropped=True)[10:-10, 10:-10].ravel()))

        df = pd.DataFrame(df)
        df = df.dropna()
        return df

    def plot_all_behaviors(self):
        fig, axes = plt.subplots(11)
        t0 = self.lp_obj.frames[0].time
        t1 = self.lp_obj.frames[-1].time
        for i, bid in enumerate(self.ca_obj.bids):
            axes[i].imshow(self.ca_obj.returnClusterKDE(t0, t1, bid, cropped=True))
        axes[-1].imshow(self.da_obj.returnHeightChange(t0, t1, cropped=True))

    def multiple_linear_regression(self):
        df = self.get_regression_data()
        model = ols('depth ~ {}'.format('+'.join(self.ca_obj.bids)), data=df).fit()
        m = model.params
        r_squared = model.rsquared
        print(model.summary())
        return model
