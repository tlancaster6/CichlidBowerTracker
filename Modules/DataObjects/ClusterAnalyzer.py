import numpy as np
import pandas as pd
from sklearn.neighbors import KernelDensity
from skimage import morphology
import datetime
import sys
from skimage.morphology import binary_opening as opening
from skimage.morphology import binary_closing as closing
from skimage.morphology import disk
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
        with open(self.projFileManager.localTrayFile) as f:
            line = next(f)
            tray = line.rstrip().split(',')
            self.tray_r = [int(x) for x in tray]

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
        # self.clusterData.round({'X_Depth': 0, 'Y_Depth': 0})

        self.clusterData.to_csv(self.projFileManager.localAllLabeledClustersFile)

    def sliceDataframe(self, t0=None, t1=None, bid=None, columns=None, input_frame=None, cropped=False):
        df_slice = self.clusterData if input_frame is None else input_frame
        df_slice = df_slice.dropna(subset=['Model18_All_pred']).sort_index()
        if t0 is not None:
            self._checkTimes(t0, t1)
            df_slice = df_slice[t0:t1]
        if bid is not None:
            df_slice = df_slice[df_slice.Model18_All_pred == bid]
        if columns is not None:
            df_slice = df_slice[columns]
        if cropped:
            df_slice = df_slice[(df_slice.X_depth > self.tray_r[1]) & (df_slice.X_depth < self.tray_r[3]) &
                                (df_slice.Y_depth > self.tray_r[0]) & (df_slice.Y_depth < self.tray_r[2])]
            df_slice.X_depth = df_slice.X_depth - self.tray_r[1]
            df_slice.Y_depth = df_slice.Y_depth - self.tray_r[0]
        return df_slice

    def returnClusterCounts(self, t0, t1, bid='all', cropped=False):
        self._checkTimes(t0, t1)
        df_slice = self.sliceDataframe(cropped=cropped)
        if bid == 'all':
            df_slice = self.sliceDataframe(t0=t0, t1=t1, input_frame=df_slice)
            row = df_slice.Model18_All_pred.value_counts().to_dict
            return row
        else:
            df_slice = self.sliceDataframe(t0=t0, t1=t1, bid=bid, input_frame=df_slice)
            cell = df_slice.Model18_All_pred.count()
            return cell

    def returnClusterKDE(self, t0, t1, bid, cropped=False, bandwidth=10.0):
        df_slice = self.sliceDataframe(t0=t0, t1=t1, bid=bid, cropped=cropped, columns=['X_depth', 'Y_depth'])
        n_events = len(df_slice.index)
        x_bins = int(self.tray_r[3] - self.tray_r[1])
        y_bins = int(self.tray_r[2] - self.tray_r[0])
        yy, xx = np.mgrid[0:y_bins, 0:x_bins]
        if n_events == 0:
            z = np.zeros_like(xx)
        else:
            xy_sample = np.vstack([xx.ravel(), yy.ravel()]).T
            xy_train = df_slice.to_numpy()
            kde = KernelDensity(bandwidth=bandwidth, kernel='epanechnikov').fit(xy_train)
            z = np.exp(kde.score_samples(xy_sample)).reshape(xx.shape)
            z = (z * n_events) / (z.sum() * (self.projFileManager.pixelLength ** 2))
        return z

    def returnBowerLocations(self, t0, t1, denoise=False, cropped=False, bandwidth=10.0):

        self._checkTimes(t0, t1)
        timeChange = t1 - t0

        if timeChange.total_seconds() < 7300:  # 2 hours or less
            totalThreshold = self.projFileManager.hourlyClusterThreshold
            minPixels = self.projFileManager.hourlyMinPixels
            denoiseRadius = self.projFileManager.hourlyDenoiseRadius
        elif timeChange.total_seconds() < 129600:  # 2 hours to 1.5 days
            totalThreshold = self.projFileManager.dailyClusterThreshold
            minPixels = self.projFileManager.dailyMinPixels
            denoiseRadius = self.projFileManager.dailyDenoiseRadius
        else:  # 1.5 days or more
            totalThreshold = self.projFileManager.totalClusterThreshold
            minPixels = self.projFileManager.totalMinPixels
            denoiseRadius = self.projFileManager.totalDenoiseRadius

        z_scoop = self.returnClusterKDE(t0, t1, 'c', cropped=cropped, bandwidth=bandwidth)
        scoop_binary = np.where(z_scoop >= totalThreshold, True, False)
        if denoise:
            scoop_binary = closing(opening(scoop_binary, disk(denoiseRadius)), disk(denoiseRadius))
        scoop_binary = morphology.remove_small_objects(scoop_binary, minPixels).astype(int)

        z_spit = self.returnClusterKDE(t0, t1, 'p', cropped=cropped, bandwidth=bandwidth)
        spit_binary = np.where(z_spit >= totalThreshold, True, False)
        if denoise:
            spit_binary = closing(opening(spit_binary, disk(denoiseRadius)), disk(denoiseRadius))
        spit_binary = morphology.remove_small_objects(spit_binary, minPixels).astype(int)

        bowers = spit_binary - scoop_binary
        return bowers

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
