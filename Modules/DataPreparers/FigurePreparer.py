from Modules.DataObjects.LogParser import LogParser as LP
from Modules.DataObjects.DepthAnalyzer import DepthAnalyzer as DA
from Modules.DataObjects.ClusterAnalyzer import ClusterAnalyzer as CA

from matplotlib import (cm, colors, gridspec, ticker)
import matplotlib.pyplot as plt
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
		self.lp_obj = LP(projFileManager.localLogfile)
		self.da_obj = DA(projFileManager)
		self.ca_obj = CA(projFileManager)

	def validateInputData(self):
		assert os.path.exists(self.projFileManager.localLogfile)
		assert os.path.exists(self.projFileManager.localFiguresDir)
		assert os.path.exists(self.projFileManager.localSmoothDepthFile)
		assert os.path.exists(self.projFileManager.localAnalysisDir)
		assert os.path.exists(self.projFileManager.localAllLabeledClustersFile)
		assert os.path.exists(self.projFileManager.localTransMFile)
		self.uploads = [(self.projFileManager.localAnalysisDir, self.projFileManager.cloudAnalysisDir, 0),
						(self.projFileManager.localFiguresDir, self.projFileManager.cloudFiguresDir, 0)]


	def _createDepthFigures(self, hourlyDelta=2):
		# figures based on the depth data

		# Create summary figure of daily values
		figDaily = plt.figure(num=1, figsize=(11, 8.5))
		figDaily.suptitle(self.lp_obj.projectID + ' Daily Depth Summary')
		gridDaily = gridspec.GridSpec(3, 1)

		# Create summary figure of hourly values
		figHourly = plt.figure(num=2, figsize=(11, 8.5))
		figHourly.suptitle(self.lp_obj.projectID + ' Hourly Depth Summary')

		start_day = self.lp_obj.frames[0].time.replace(hour=0, minute=0, second=0, microsecond=0)
		totalChangeData = vars(self.da_obj.returnVolumeSummary(self.lp_obj.frames[0].time, self.lp_obj.frames[-1].time))

		# Show picture of final depth
		topGrid = gridspec.GridSpecFromSubplotSpec(1, 3, subplot_spec=gridDaily[0])
		topAx1 = figDaily.add_subplot(topGrid[0])
		topAx1_ax = topAx1.imshow(self.da_obj.returnHeight(self.lp_obj.frames[-1].time, cropped=True), vmin=50, vmax=70)
		topAx1.set_title('Final Depth (cm)')
		topAx1.tick_params(colors=[0, 0, 0, 0])
		plt.colorbar(topAx1_ax, ax=topAx1)

		# Show picture of total depth change
		topAx2 = figDaily.add_subplot(topGrid[1])
		topAx2_ax = topAx2.imshow(self.da_obj.returnHeightChange(
			self.lp_obj.frames[0].time, self.lp_obj.frames[-1].time, cropped=True), vmin=-5, vmax=5)
		topAx2.set_title('Total Depth Change (cm)')
		topAx2.tick_params(colors=[0, 0, 0, 0])
		plt.colorbar(topAx2_ax, ax=topAx2)

		# Show picture of pit and castle mask
		topAx3 = figDaily.add_subplot(topGrid[2])
		topAx3_ax = topAx3.imshow(self.da_obj.returnHeightChange(self.lp_obj.frames[0].time, self.lp_obj.frames[-1].time, cropped = True, masked = True), vmin = -5, vmax = 5)
		topAx3.set_title('Masked Depth Change (cm)')
		topAx3.tick_params(colors=[0, 0, 0, 0])
		plt.colorbar(topAx3_ax, ax=topAx3)

		# Create figures and get data for daily Changes
		dailyChangeData = []
		w_ratios = ([1.0] * self.lp_obj.numDays) + [0.25]
		midGrid = gridspec.GridSpecFromSubplotSpec(3, self.lp_obj.numDays + 1, subplot_spec=gridDaily[1], width_ratios=w_ratios)
		v = 2
		for i in range(self.lp_obj.numDays):
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
		plt.colorbar(cm.ScalarMappable(norm=colors.Normalize(vmin=-v, vmax=v), cmap='viridis'), cax=cax)

		figHourly = plt.figure(figsize=(11, 8.5))
		gridHourly = plt.GridSpec(self.lp_obj.numDays, int(24 / hourlyDelta) + 2, wspace=0.05, hspace=0.05)
		bounding_ax = figHourly.add_subplot(gridHourly[:, :])
		bounding_ax.xaxis.set_visible(False)
		bounding_ax.set_ylabel('Day')
		bounding_ax.set_ylim(self.lp_obj.numDays + 0.5, 0.5)
		bounding_ax.yaxis.set_major_locator(ticker.MultipleLocator(base=1.0))
		bounding_ax.set_yticklabels(range(self.lp_obj.numDays + 1))
		sns.despine(ax=bounding_ax, left=True, bottom=True)

		hourlyChangeData = []
		v = 1
		for i in range(0, self.lp_obj.numDays):
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
			current_ax.imshow(self.da_obj.returnBowerLocations(stop - datetime.timedelta(hours=24), stop, cropped=True, denoise=True), vmin=-v, vmax=v)
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

		bottomGrid = gridspec.GridSpecFromSubplotSpec(2, 1, subplot_spec=gridDaily[2], hspace=0.05)
		bIAx = figDaily.add_subplot(bottomGrid[1])
		bIAx.axhline(linewidth=1, alpha=0.5, y=0)
		bIAx.scatter(dailyDT['Midpoint'], dailyDT['bowerIndex'])
		bIAx.scatter(hourlyDT['Midpoint'], hourlyDT['bowerIndex'])
		bIAx.set_xlabel('Day')
		bIAx.set_ylabel('Bower\nIndex')
		bIAx.xaxis.set_major_locator(ticker.MultipleLocator(base=1.0))

		volAx = figDaily.add_subplot(bottomGrid[0], sharex=bIAx)
		volAx.plot(dailyDT['Midpoint'], dailyDT['bowerVolume'])
		volAx.plot(hourlyDT['Midpoint'], hourlyDT['bowerVolume'])
		volAx.set_ylabel('Volume\nChange')
		plt.setp(volAx.get_xticklabels(), visible=False)

		figDaily.savefig(self.projFileManager.localFiguresDir + 'DailyDepthSummary.pdf')
		figHourly.savefig(self.projFileManager.localFiguresDir + 'HourlyDepthSummary.pdf')

		plt.close('all')

	def _createClusterFigures(self):
		# figures based on the cluster data

		# semi-transparent scatterplots showing the spatial distrubtion of each cluster classification each day
		fig, axes = plt.subplots(10, self.lp_obj.numDays, figsize=(8.5, 11))
		fig.suptitle(self.lp_obj.projectID + ' Daily Cluster Distributions')
		t0 = self.lp_obj.master_start.replace(hour=0, minute=0, second=0, microsecond=0)
		df_cropped = self.ca_obj.sliceDataframe(cropped=True)
		x_limits = (df_cropped.X_depth.min(), df_cropped.X_depth.max())
		y_limits = (df_cropped.Y_depth.max(), df_cropped.Y_depth.min())
		for i in range(self.lp_obj.numDays):
			t1 = t0 + datetime.timedelta(hours=24)
			df_slice = self.ca_obj.sliceDataframe(t0=t0, t1=t1, input_frame=df_cropped)
			for j, bid in enumerate(self.ca_obj.bids):
				df_slice_slice = self.ca_obj.sliceDataframe(input_frame=df_slice, bid=bid)
				sns.scatterplot(x='X_depth', y='Y_depth', data=df_slice_slice, ax=axes[j, i], s=10,
								linewidth=0, alpha=0.1)
				axes[j, i].tick_params(colors=[0, 0, 0, 0])
				axes[j, i].set(xlabel=None, ylabel=None, aspect='equal', xlim=x_limits, ylim=y_limits)
				if j == 0:
					axes[0, i].set_title('day %i' % (i + 1))
				if i == 0:
					axes[j, 0].set_ylabel(str(bid))
			t0 = t1
		fig.savefig(self.projFileManager.localFiguresDir + 'DailyClusterDistributions.pdf')
		plt.close(fig=fig)

		# heatmaps of the estimated daily scoop and spit areal densities
		fig, axes = plt.subplots(2, self.lp_obj.numDays, figsize=(1.5 * self.lp_obj.numDays, 4))
		fig.suptitle(self.lp_obj.projectID + ' Daily Scoop Spit Heatmaps')
		t0 = self.lp_obj.master_start.replace(hour=0, minute=0, second=0, microsecond=0)
		vmax = 0
		cbar_reference = None
		subplot_handles = []
		for i in range(self.lp_obj.numDays):
			t1 = t0 + datetime.timedelta(hours=24)
			z_scoop = self.ca_obj.returnClusterKDE(t0=t0, t1=t1, bid='c', cropped=True)
			z_spit = self.ca_obj.returnClusterKDE(t0=t0, t1=t1, bid='p', cropped=True)
			z = z_spit - z_scoop
			im = axes[0, i].imshow(z, cmap='viridis', interpolation='none')
			subplot_handles.append(im)
			axes[0, i].set(title='day %i' % (i + 1), xlabel=None, ylabel=None, aspect='equal')
			axes[0, i].tick_params(colors=[0, 0, 0, 0])
			if np.max(np.abs(z)) > vmax:
				vmax = np.max(np.abs(z))
				cbar_reference = im
			bowers = self.ca_obj.returnBowerLocations(t0, t1, denoise=True, cropped=True)
			axes[1, i].imshow(bowers, cmap='viridis', vmin=-1, vmax=1)
			axes[1, i].set(xlabel=None, ylabel=None, aspect='equal')
			axes[1, i].tick_params(colors=[0, 0, 0, 0])
			t0 = t1
		for im in subplot_handles:
			im.set_clim(-vmax, vmax)
		cbar = fig.colorbar(cbar_reference, ax=axes[0, :].tolist(), shrink=0.7)
		cbar.set_label(r'$spits/cm^2$ - $scoops/cm^2$')
		cbar = fig.colorbar(cm.ScalarMappable(norm=colors.Normalize(vmin=-1, vmax=1), cmap=cm.get_cmap('viridis', 3)),
					 ax=axes[1, :].tolist(), shrink=0.7)
		cbar.set_label('bower region')
		cbar.set_ticks([-1, 0, 1])

		fig.savefig(self.projFileManager.localFiguresDir + 'DailyScoopSpitDensities.pdf')
		plt.close(fig=fig)



	def _createCombinedFigures(self):
		# create figures based on a combination of cluster and depth data

		# plot overlap of daily bower regions identified from depth and cluster data
		fig, axes = plt.subplots(3, self.lp_obj.numDays, figsize=(1.5 * self.lp_obj.numDays, 6))
		fig.suptitle(self.lp_obj.projectID + ' Bower Identification Consistency')
		t0 = self.lp_obj.master_start.replace(hour=0, minute=0, second=0, microsecond=0)
		for i in range(self.lp_obj.numDays):
			t1 = t0 + datetime.timedelta(hours=24)

			depth_bowers = self.da_obj.returnBowerLocations(t0, t1, denoise=True, cropped=True)
			axes[0, i].imshow(depth_bowers, cmap='viridis', vmin=-1, vmax=1)
			axes[0, i].set(xlabel=None, ylabel=None, aspect='equal')
			axes[0, i].tick_params(colors=[0, 0, 0, 0])

			cluster_bowers = self.ca_obj.returnBowerLocations(t0, t1, denoise=True, cropped=True)
			axes[1, i].imshow(cluster_bowers, cmap='viridis', vmin=-1, vmax=1)
			axes[1, i].set(xlabel=None, ylabel=None, aspect='equal')
			axes[1, i].tick_params(colors=[0, 0, 0, 0])

			bower_intersection = np.where((depth_bowers == cluster_bowers) & (depth_bowers != 0), True, False)
			bower_intersection_area = np.count_nonzero(bower_intersection)
			bower_union = np.where((depth_bowers != 0) | (cluster_bowers != 0), True, False)
			bower_union_area = np.count_nonzero(bower_union)
			if bower_intersection_area == bower_union_area == 0:
				similarity = 1.0
			elif (bower_intersection_area == 0) | (bower_union_area == 0):
				similarity = 0.0
			else:
				similarity = bower_intersection_area / bower_union_area

			axes[2, i].imshow(-1 *((2 * bower_intersection) - bower_union), cmap='bwr', vmin=-1, vmax=1)
			axes[2, i].set(xlabel='J = {0:.3f}'.format(similarity), ylabel=None, aspect='equal')
			axes[2, i].tick_params(colors=[0, 0, 0, 0])

			t0 = t1

		axes[0, 0].set_ylabel('Depth Bowers')
		axes[1, 0].set_ylabel('Cluster Bowers')
		axes[2, 0].set_ylabel('Overlap')

		cbar = fig.colorbar(cm.ScalarMappable(norm=colors.Normalize(vmin=-1, vmax=1), cmap=cm.get_cmap('viridis', 3)),
							ax=axes[0, :].tolist(), shrink=0.7)
		cbar.set_label('bower region')
		cbar.set_ticks([-1, 0, 1])
		cbar.set_ticklabels(['-', '0', '+'])

		cbar = fig.colorbar(cm.ScalarMappable(norm=colors.Normalize(vmin=-1, vmax=1), cmap=cm.get_cmap('viridis', 3)),
							ax=axes[1, :].tolist(), shrink=0.7)
		cbar.set_label('bower region')
		cbar.set_ticks([-1, 0, 1])
		cbar.set_ticklabels(['-', '0', '+'])

		cbar = fig.colorbar(cm.ScalarMappable(norm=colors.Normalize(vmin=-1, vmax=1), cmap=cm.get_cmap('bwr', 3)),
							ax=axes[2, :].tolist(), shrink=0.7)
		cbar.set_label('Labels Agree?')
		cbar.set_ticks([-1, 1])
		cbar.set_ticklabels(['Y', 'N'])

		fig.savefig(self.projFileManager.localFiguresDir + 'BowerIdentificationConsistency.pdf')
		plt.close(fig=fig)

	def createAllFigures(self, hourlyDelta=2):
		self._createCombinedFigures()
		self._createClusterFigures()
		self._createDepthFigures(hourlyDelta=hourlyDelta)
