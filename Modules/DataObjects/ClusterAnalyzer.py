import numpy as np
import pandas as pd
import datetime
import sys
import math

from Modules.DataObjects.LogParser import LogParser as LP



class ClusterAnalyzer:

    def __init__(self, projFileManager):
        self.projFileManager = projFileManager
        self.bids = ['c', 'p', 'b', 'f', 't', 'm', 's', 'd', 'o', 'x']
        self.lp_obj = LP(projFileManager.localLogfile)
        self._loadData()

    def _loadData(self):
        self.transM = np.load(self.projFileManager.localTransMFile)
        self.clusterData = pd.read_csv(self.projFileManager.localAllLabeledClustersFile, index_col='TimeStamp',
                                       parse_dates=True, infer_datetime_format=True)
        self._appendDepthCoordinates()

    def _appendDepthCoordinates(self):
        # adds columns containing X and Y in depth coordinates to all cluster csv
        if 'Y_depth' not in list(self.clusterData.columns):
            self.clusterData['Y_depth'] = self.clusterData.apply(
                lambda row: (self.transM[0][0] * row.Y + self.transM[0][1] * row.X + self.transM[0][2]) / (
                        self.transM[2][0] * row.Y + self.transM[2][1] * row.X + self.transM[2][2]), axis=1)
        if 'X_depth' not in list(self.clusterData.columns):
            self.clusterData['X_depth'] = self.clusterData.apply(
                lambda row: (self.transM[1][0] * row.Y + self.transM[1][1] * row.X + self.transM[1][2]) / (
                        self.transM[2][0] * row.Y + self.transM[2][1] * row.X + self.transM[2][2]), axis=1)
        self.clusterData.round({'X_Depth': 0, 'Y_Depth': 0})

        self.clusterData.to_csv(self.projFileManager.localAllLabeledClustersFile)

    def sliceDataframe(self, t0=None, t1=None, bid=None, columns=None, input_frame=None):
        df_slice = self.clusterData.dropna().sort_index() if input_frame is None else input_frame
        if t0 is not None:
            self._checkTimes(t0, t1)
            df_slice = df_slice[t0:t1]
        if bid is not None:
            df_slice = df_slice[df_slice.modelAll_18_pred == bid]
        if columns is not None:
            df_slice = df_slice[columns]
        return df_slice

    def returnClusterCounts(self, t0, t1, bid='all'):
        self._checkTimes(t0, t1)
        if bid == 'all':
            df_slice = self.sliceDataframe(t0=t0, t1=t1)
            row = df_slice.modelAll_18_pred.value_counts().to_dict
            return row
        else:
            df_slice = self.sliceDataframe(t0=t0, t1=t1, bid=bid)
            cell = df_slice.modelAll_18_pred.count()
            return cell

    def _checkTimes(self, t0, t1=None):
        if t1 is None:
            if type(t0) != datetime.datetime:
                raise Exception('Timepoints to must be datetime.datetime objects')
            return
        # Make sure times are appropriate datetime objects
        if type(t0) != datetime.datetime or type(t1) != datetime.datetime:
            raise Exception('Timepoints to must be datetime.datetime objects')
        if t0 > t1:
            print('Warning: Second timepoint ' + str(t1) + ' is earlier than first timepoint ' + str(t0),
                  file=sys.stderr)

