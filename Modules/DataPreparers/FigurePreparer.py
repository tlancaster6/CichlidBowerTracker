from Modules.DataObjects.LogParser import LogParser as LP
from Modules.DataObjects.DepthAnalyzer import DepthAnalyzer as DA
from Modules.FileManagers.ProjFileManager import ProjFileManager as PFM
import matplotlib.pyplot as plt
import matplotlib as mpl
import pandas as pd
import numpy as np
import seaborn as sns
import datetime
import os

class FigurePreparer:
	# This class takes in directory information and a logfile containing depth information and performs the following:
	# 1. Identifies tray using manual input
	# 2. Interpolates and smooths depth data
	# 3. Automatically identifies bower location
	# 4. Analyze building, shape, and other pertinent info of the bower

	def __init__(self, projFileManager):
		self.__version__ = '1.0.0'
		self.projFileManager = projFileManager
		self.lp = LP(projFileManager.localLogfile)
		self.da_obj = DA(projFileManager)
		self.clusterData = self._combineVideoData()

	def validateInputData(self):
		# Needs to be modified
		assert os.path.exists(self.projFileManager.localLogfile)
		assert os.path.exists(self.projFileManager.localFiguresDir)
		assert os.path.exists(self.projFileManager.localSmoothDepthFile)
		assert os.path.exists(self.projFileManager.localTroubleshootingDir)
		assert os.path.exists(self.projFileManager.localAnalysisDir)
		assert os.path.exists(self.projFileManager.localAllLabeledClustersFile)
		assert os.path.exists(self.projFileManager.localTransMFile)
		self.uploads = [(self.projFileManager.localTroubleshootingDir, self.projFileManager.cloudTroubleshootingDir, 0),
						(self.projFileManager.localAnalysisDir, self.projFileManager.cloudAnalysisDir, 0)]

	def _combineVideoData(self):
		# adds columns to all cluster csv
		transM = np.load(self.projFileManager.localTransMFile)
		clusterData = pd.read_csv(self.projFileManager.localAllLabeledClustersFile, index_col='TimeStamp')
		if 'Y_depth' not in list(clusterData.columns):
			clusterData['Y_depth'] = clusterData.apply(
				lambda row: (transM[0][0] * row.Y + transM[0][1] * row.X + transM[0][2]) / (
							transM[2][0] * row.Y + transM[2][1] * row.X + transM[2][2]), axis=1)
		if 'X_depth' not in list(clusterData.columns):
			clusterData['X_depth'] = clusterData.apply(
				lambda row: (transM[1][0] * row.Y + transM[1][1] * row.X + transM[1][2]) / (
							transM[2][0] * row.Y + transM[2][1] * row.X + transM[2][2]), axis=1)
		clusterData.to_csv(self.projFileManager.localAllLabeledClustersFile)
		return clusterData

	def _createDepthFigures(self, hourlyDelta=2):
		# Create summary figure of daily values
		figDaily = plt.figure(num=1, figsize=(11, 8.5))
		figDaily.suptitle(self.lp.projectID + ' DailySummary')
		gridDaily = mpl.gridspec.GridSpec(3, 1)

		# Create summary figure of hourly values
		figHourly = plt.figure(num=2, figsize=(11, 8.5))
		figHourly.suptitle(self.lp.projectID + ' HourlySummary')
		gridHourly = plt.GridSpec(self.lp.numDays, int(24/hourlyDelta) + 2, wspace=0.02, hspace=0.02)

		start_day = self.lp.frames[0].time.replace(hour=0, minute=0, second=0, microsecond=0)
		totalChangeData = vars(self.da_obj.returnVolumeSummary(self.lp.frames[0].time, self.lp.frames[-1].time))

		# Show picture of final depth
		topGrid = mpl.gridspec.GridSpecFromSubplotSpec(1, 3, subplot_spec=gridDaily[0])
		topAx1 = figDaily.add_subplot(topGrid[0])
		topAx1_ax = topAx1.imshow(self.da_obj.returnHeight(self.lp.frames[-1].time, cropped=True), vmin=50, vmax=70)
		topAx1.set_title('Final Depth (cm)')
		topAx1.tick_params(colors=[0, 0, 0, 0])
		plt.colorbar(topAx1_ax, ax=topAx1)

		# Show picture of total depth change
		topAx2 = figDaily.add_subplot(topGrid[1])
		topAx2_ax = topAx2.imshow(self.da_obj.returnHeightChange(
			self.lp.frames[0].time, self.lp.frames[-1].time, cropped=True), vmin=-5, vmax=5)
		topAx2.set_title('Total Depth Change (cm)')
		topAx2.tick_params(colors=[0, 0, 0, 0])
		plt.colorbar(topAx2_ax, ax=topAx2)

		# Show picture of pit and castle mask
		topAx3 = figDaily.add_subplot(topGrid[2])
		topAx3_ax = topAx3.imshow(self.da_obj.returnHeightChange(self.lp.frames[0].time, self.lp.frames[-1].time, cropped = True, masked = True), vmin = -5, vmax = 5)
		topAx3.set_title('Masked Depth Change (cm)')
		topAx3.tick_params(colors=[0, 0, 0, 0])
		plt.colorbar(topAx3_ax, ax=topAx3)

		# Create figures and get data for daily Changes
		dailyChangeData = []
		w_ratios = ([1.0] * self.lp.numDays) + [0.25]
		midGrid = mpl.gridspec.GridSpecFromSubplotSpec(3, self.lp.numDays + 1, subplot_spec=gridDaily[1], width_ratios=w_ratios)
		v = 2
		for i in range(self.lp.numDays):
			start = start_day + datetime.timedelta(hours=24 * i)
			stop = start_day + datetime.timedelta(hours=24 * (i + 1))
			dailyChangeData.append(vars(self.da_obj.returnVolumeSummary(start, stop)))
			dailyChangeData[i]['Day'] = i + 1
			dailyChangeData[i]['Midpoint'] = i + 1 + .5
			dailyChangeData[i]['StartTime'] = str(start)

			current_axs = [figDaily.add_subplot(midGrid[n, i]) for n in [0, 1, 2]]
			current_axs[0].imshow(self.da_obj.returnHeightChange(start_day, stop, cropped=True), vmin=-v, vmax=v)
			current_axs[0].set_title('Day %i' % (i + 1))
			current_axs[1].imshow(self.da_obj.returnHeightChange(start, stop, cropped=True), vmin=-v, vmax=v)
			current_axs[2].imshow(self.da_obj.returnHeightChange(start, stop, masked=True, cropped=True), vmin=-v, vmax=v)
			[ax.tick_params(colors=[0, 0, 0, 0]) for ax in current_axs]
			[ax.set_adjustable('box') for ax in current_axs]
		cax = figDaily.add_subplot(midGrid[:, -1])
		plt.colorbar(mpl.cm.ScalarMappable(norm=mpl.colors.Normalize(vmin=-v, vmax=v), cmap='viridis'), cax=cax)

		figHourly = plt.figure(figsize=(11, 8.5))
		figHourly.suptitle(self.lp.projectID + ' Hourly Summary')
		gridHourly = plt.GridSpec(self.lp.numDays, int(24 / hourlyDelta) + 2, wspace=0.05, hspace=0.05)
		bounding_ax = figHourly.add_subplot(gridHourly[:, :])
		bounding_ax.xaxis.set_visible(False)
		bounding_ax.set_ylabel('Day')
		bounding_ax.set_ylim(self.lp.numDays + 0.5, 0.5)
		bounding_ax.yaxis.set_major_locator(mpl.ticker.MultipleLocator(base=1.0))
		bounding_ax.set_yticklabels(range(self.lp.numDays + 1))
		sns.despine(ax=bounding_ax, left=True, bottom=True)

		hourlyChangeData = []
		v = 1
		for i in range(0, self.lp.numDays):
			for j in range(int(24 / hourlyDelta)):
				start = start_day + datetime.timedelta(hours=24 * i + j * hourlyDelta)
				stop = start_day + datetime.timedelta(hours=24 * i + (j + 1) * hourlyDelta)

				hourlyChangeData.append(vars(self.da_obj.returnVolumeSummary(start, stop)))
				hourlyChangeData[-1]['Day'] = i + 1
				hourlyChangeData[-1]['Midpoint'] = i + 1 + ((j + 0.5) * hourlyDelta) / 24
				hourlyChangeData[-1]['StartTime'] = str(start)

				current_ax = figHourly.add_subplot(gridHourly[i, j])

				current_ax.imshow(self.da_obj.returnHeightChange(start, stop, cropped=True), vmin=-v, vmax=v)
				current_ax.set_adjustable('box')
				current_ax.tick_params(colors=[0, 0, 0, 0])
				if i == 0:
					current_ax.set_title(str(j * hourlyDelta) + '-' + str((j + 1) * hourlyDelta))

			current_ax = figHourly.add_subplot(gridHourly[i, -2])
			current_ax.imshow(self.da_obj.returnBowerLocations(stop - datetime.timedelta(hours=24), stop, cropped=True), vmin=-v, vmax=v)
			current_ax.set_adjustable('box')
			current_ax.tick_params(colors=[0, 0, 0, 0])
			if i == 0:
				current_ax.set_title('Daily\nMask')

			current_ax = figHourly.add_subplot(gridHourly[i, -1])
			current_ax.imshow(self.da_obj.returnHeightChange(stop - datetime.timedelta(hours=24), stop, cropped=True),
							  vmin=-v, vmax=v)
			current_ax.set_adjustable('box')
			current_ax.tick_params(colors=[0, 0, 0, 0])
			if i == 0:
				current_ax.set_title('Daily\nChange')

		totalDT = pd.DataFrame([totalChangeData])
		dailyDT = pd.DataFrame(dailyChangeData)
		hourlyDT = pd.DataFrame(hourlyChangeData)

		writer = pd.ExcelWriter(self.projFileManager.localFiguresDir + 'DataSummary.xlsx')
		totalDT.to_excel(writer, 'Total')
		dailyDT.to_excel(writer, 'Daily')
		hourlyDT.to_excel(writer, 'Hourly')
		writer.save()

		bottomGrid = mpl.gridspec.GridSpecFromSubplotSpec(2, 1, subplot_spec=gridDaily[2], hspace=0.05)
		bIAx = figDaily.add_subplot(bottomGrid[1])
		bIAx.axhline(linewidth=1, alpha=0.5, y=0)
		bIAx.scatter(dailyDT['Midpoint'], dailyDT['bowerIndex'])
		bIAx.scatter(hourlyDT['Midpoint'], hourlyDT['bowerIndex'])
		bIAx.set_xlabel('Day')
		bIAx.set_ylabel('Bower\nIndex')
		bIAx.xaxis.set_major_locator(mpl.ticker.MultipleLocator(base=1.0))

		volAx = figDaily.add_subplot(bottomGrid[0], sharex=bIAx)
		volAx.plot(dailyDT['Midpoint'], dailyDT['bowerVolume'])
		volAx.plot(hourlyDT['Midpoint'], hourlyDT['bowerVolume'])
		volAx.set_ylabel('Volume\nChange')
		plt.setp(volAx.get_xticklabels(), visible=False)

		figDaily.savefig(self.projFileManager.localFiguresDir + 'DailyDepthSummary.pdf')
		figHourly.savefig(self.projFileManager.localFiguresDir + 'HourlyDepthSummary.pdf')

		plt.close('all')

