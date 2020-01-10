import argparse, sys, subprocess
from Modules.DataPreparers.AnalysisPreparer import AnalysisPreparer as AP
from Modules.DataPreparers.ProjectPreparer import ProjectPreparer as PP

parser = argparse.ArgumentParser()
subparsers = parser.add_subparsers(help='Available Commands', dest='command')

trackerParser = subparsers.add_parser('CollectData',
                                      help='This command runs on Raspberry Pis to collect depth and RGB data')

summarizeParser = subparsers.add_parser('UpdateAnalysisSummary',
                                        help='This command identifies any new projects that can be analyzed and merges any updates that are new')

prepParser = subparsers.add_parser('ManualPrep',
                                   help='This command takes user interaction to identify depth crops, RGB crops, and register images')
prepParser.add_argument('-p', '--ProjectIDs', nargs='+', required=True, type=str,
                        help='Manually identify the projects you want to analyze. If All is specified, all non-prepped projects will be analyzed')
prepParser.add_argument('-w', '--Workers', type=int,
                        help='Use if you want to control how many workers this analysis uses', default=14)
prepParser.add_argument('-g', '--GPUs', type=int, help='Use if you want to control how many GPUs this analysis uses',
                        default=1)
prepParser.add_argument('-t', '--TempDir', type=str,
                        help='Optional. Manually designate the temp directory. Default is LSS, the local scratch storage on PACE',
                        default='LSS')
prepParser.add_argument('-m', '--Email', type=str,
                            help='Optional. Enter an email that will receive updates during PACE analysis',
                            default=None)

projectParser = subparsers.add_parser('ProjectAnalysis',
                                      help='This command performs a single type of analysis of the project. It is meant to be chained together to perform the entire analysis')
projectParser.add_argument('AnalysisType', type=str,
                           choices=['Download', 'Depth', 'Cluster', 'CreateFrames', 'MLClassification',
                                    'MLFishDetection', 'Figures', 'Backup', 'Outfiles', 'PBS'],
                           help='What type of analysis to perform')
projectParser.add_argument('ProjectID', type=str, help='Which projectID you want to identify')
projectParser.add_argument('-w', '--Workers', type=int,
                           help='Use if you want to control how many workers this analysis uses', default=1)
projectParser.add_argument('-g', '--GPUs', type=int, help='Use if you want to control how many GPUs this analysis uses',
                           default=1)
projectParser.add_argument('-d', '--DownloadOnly', action='store_true',
                           help='Use if you only want to download the data for a specific analysis')
projectParser.add_argument('-v', '--VideoIndex', type=int, help='Restrict cluster analysis to single video')
projectParser.add_argument('-t', '--TempDir', type=str,
                           help='Optional. Manually designate the temp directory. Enter LSS to use local scratch storage on PACE',
                           default=None)
projectParser.add_argument('-m', '--Email', type=str,
                           help='Optional. Enter an email that will receive updates during PACE analysis',
                           default=None)

totalProjectsParser = subparsers.add_parser('TotalProjectAnalysis',
                                            help='This command runs the entire pipeline on list of projectIDs')
totalProjectsParser.add_argument('Computer', type=str, choices=['NURF', 'SRG', 'PACE'],
                                 help='What computer are you running this analysis from?')
totalProjectsParser.add_argument('-p', '--ProjectIDs', nargs='+', required=True, type=str,
                                 help='Manually identify the projects you want to analyze. If All is specified, all non-prepped projects will be analyzed')
totalProjectsParser.add_argument('-m', '--Email', type=str,
                                 help='Optional. Enter an email that will receive updates during PACE analysis',
                                 default=None)

args = parser.parse_args()

if args.command is None:
    parser.print_help()

if args.command == 'UpdateAnalysisSummary':

    ap_obj = AP()
    ap_obj.updateAnalysisFile()

elif args.command == 'ManualPrep':

    ap_obj = AP()
    if ap_obj.checkProjects(args.ProjectIDs):
        sys.exit()

    for projectID in args.ProjectIDs:
        pp_obj = PP(projectID, args.Workers, args.TempDir)
        pp_obj.runPrepAnalysis()
        pp_obj.runPacePrep(args.Email)

    ap_obj.updateAnalysisFile(newProjects=False, projectSummary=False)

elif args.command == 'ProjectAnalysis':

    if args.DownloadOnly and args.AnalysisType in ['Download', 'Backup']:
        print('DownloadOnly flag cannot be used with Download or Backup AnalysisType')
        sys.exit()

    args.ProjectIDs = args.ProjectID  # format that parseProjects expects

    pp_obj = PP(args.ProjectID, args.Workers, args.TempDir)

    if args.AnalysisType == 'Download' or args.DownloadOnly:
        pp_obj.downloadData(args.AnalysisType)

    elif args.AnalysisType == 'PBS':
        pp_obj.downloadData('PBS')

    elif args.AnalysisType == 'Depth':
        pp_obj.runDepthAnalysis()

    elif args.AnalysisType == 'Cluster':
        pp_obj.runClusterAnalysis(args.VideoIndex)

    elif args.AnalysisType == 'CreateFrames':
        pp_obj.createAnnotationFrames()

    elif args.AnalysisType == 'MLClassification':
        pp_obj.runMLClusterClassifier()

    elif args.AnalysisType == 'MLFishDetection':
        pp_obj.runMLFishDetection()

    elif args.AnalysisType == 'Figures':
        pp_obj.runFiguresCreation()

    elif args.AnalysisType == 'Backup':
        pp_obj.backupAnalysis()

    elif args.AnalysisType == 'Outfiles':
        pp_obj.parseOutfiles()

if args.command == 'TotalProjectAnalysis':

    ap_obj = AP()
    if ap_obj.checkProjects(args.ProjectIDs):
        sys.exit()

    if args.Computer == 'PACE':
        import spur, getpass, time
        uname = input('Username: ')
        pword = getpass.getpass()
        datamover_shell = spur.SshShell(hostname='iw-dm-4.pace.gatech.edu', username=uname, password=pword)
        r6_shell = spur.SshShell(hostname='login-s.pace.gatech.edu', username=uname, password=pword)
        r7_shell = spur.SshShell(hostname='login7-d.pace.gatech.edu', username=uname, password=pword)
        wait = False

    f = open('Analysis.log', 'w')

    for projectID in args.ProjectIDs:
        if args.Computer == 'SRG':
            print('Analyzing projectID: ' + projectID, file=f)
            downloadProcess = subprocess.run(
                ['python3', 'CichlidBowerTracker.py', 'ProjectAnalysis', 'Download', projectID], stderr=subprocess.PIPE,
                stdout=subprocess.PIPE, encoding='utf-8')

            print(downloadProcess.stdout, file=f)
            depthProcess = subprocess.Popen(
                ['python3', 'CichlidBowerTracker.py', 'ProjectAnalysis', 'Depth', projectID, '-w', '1'],
                stderr=subprocess.PIPE, stdout=subprocess.PIPE, encoding='utf-8')
            clusterProcess = subprocess.Popen(
                ['python3', 'CichlidBowerTracker.py', 'ProjectAnalysis', 'Cluster', projectID, '-w', '23'],
                stderr=subprocess.PIPE, stdout=subprocess.PIPE, encoding='utf-8')
            depthOut = depthProcess.communicate()
            clusterOut = clusterProcess.communicate()
            print(depthOut[0], file=f)
            print(clusterOut[0], file=f)
            mlProcess = subprocess.run(
                ['python3', 'CichlidBowerTracker.py', 'ProjectAnalysis', 'MLClassification', projectID],
                stderr=subprocess.PIPE, stdout=subprocess.PIPE, encoding='utf-8')
            print(mlProcess.stdout, file=f)
            # print(mlProcess.stderr, file = f)

            error = False
            if depthOut[1] != '':
                print('DepthError: ' + depthOut[1])
                print('DepthError: ' + depthOut[1], file=f)
                error = True

            if clusterOut[1] != '':
                print('ClusterError: ' + clusterOut[1])
                print('ClusterError: ' + clusterOut[1], file=f)
                error = True

            if mlProcess.stderr != '':
                print('MLError: ' + mlProcess.stderr)
                print('MLError: ' + mlProcess.stderr, file=f)
                error = True

            if error:
                f.close()
                sys.exit()

            backupProcess = subprocess.run(
                ['python3', 'CichlidBowerTracker.py', 'ProjectAnalysis', 'Backup', projectID], stderr=subprocess.PIPE,
                stdout=subprocess.PIPE, encoding='utf-8')

        elif args.Computer == 'NURF':
            print('Analyzing projectID: ' + projectID, file=f)
            downloadProcess = subprocess.run(
                ['python3', 'CichlidBowerTracker.py', 'ProjectAnalysis', 'Download', projectID], stderr=subprocess.PIPE,
                stdout=subprocess.PIPE, encoding='utf-8')
            print(downloadProcess.stdout, file=f)
            depthProcess = subprocess.Popen(
                ['python3', 'CichlidBowerTracker.py', 'ProjectAnalysis', 'Depth', projectID, '-w', '1'],
                stderr=subprocess.PIPE, stdout=subprocess.PIPE, encoding='utf-8')
            clusterProcess = subprocess.Popen(
                ['python3', 'CichlidBowerTracker.py', 'ProjectAnalysis', 'Cluster', projectID, '-w', '23'],
                stderr=subprocess.PIPE, stdout=subprocess.PIPE, encoding='utf-8')
            depthOut = depthProcess.communicate()
            clusterOut = clusterProcess.communicate()
            print(depthOut[0], file=f)
            print(clusterOut[0], file=f)

            if depthOut[1] != '' or clusterOut[1] != '':
                print('DepthError: ' + depthOut[1])
                print('ClusterError: ' + clusterOut[1])
                sys.exit()
            backupProcess = subprocess.run(
                ['python3', 'CichlidBowerTracker.py', 'ProjectAnalysis', 'Backup', projectID], stderr=subprocess.PIPE,
                stdout=subprocess.PIPE, encoding='utf-8')

        elif args.Computer == 'PACE':
            pbs_dir = 'scratch/' + projectID + '/PBS'
            code_dir = 'data/CichlidBowerTracker'

            print(time.asctime() + ' -- Analyzing projectID: ' + projectID, file=f)
            print(time.asctime() + ' -- Analyzing projectID: ' + projectID)

            print(time.asctime() + ' -- gathering necessary files', file=f)
            print(time.asctime() + ' -- gathering necessary files')

            pbsDownloadCommand = ('module load anaconda3; '
                                  'source activate CichlidBowerTracker;'
                                  'python3 CichlidBowerTracker.py ProjectAnalysis PBS {}'.format(projectID))
            datamover_shell.run(['sh', '-c', pbsDownloadCommand], cwd=code_dir, encoding='utf-8')


            print(time.asctime() + ' -- Submitting pbs scripts', file=f)
            print(time.asctime() + ' -- Submitting pbs scripts')

            if wait:
                downloadCommand = ['qsub', '-W', 'depend=after:{}'.format(job_ids['backup']), 'Download.pbs']
                downloadProcess = r6_shell.run(downloadCommand, cwd=pbs_dir, encoding='utf-8')
                job_ids.update({'download': str(downloadProcess.output)[:-2]})

            else:
                wait = True
                downloadCommand = ['qsub', 'Download.pbs']
                downloadProcess = r6_shell.run(downloadCommand, cwd=pbs_dir, encoding='utf-8')
                job_ids = {'download': str(downloadProcess.output)[:-2]}

            print(job_ids)
            depthCommand = ['qsub', '-W', 'depend=afterok:{}'.format(job_ids['download']), 'DepthAnalysis.pbs']
            print(depthCommand)
            depthProcess = r6_shell.run(depthCommand, cwd=pbs_dir, encoding='utf-8')
            job_ids.update({'depth': str(depthProcess.output)[:-2]})

            clusterCommand = ['qsub', '-W', 'depend=afterok:{}'.format(job_ids['download']), 'ClusterAnalysis.pbs']
            clusterProcess = r6_shell.run(clusterCommand, cwd=pbs_dir, encoding='utf-8')
            job_ids.update({'cluster': str(clusterProcess.output)[:-2]})

            clusterProcessWrapupCommand = ['qsub', '-W', 'depend=afterok:{}'.format(job_ids['cluster']),
                                           'PostClusterAnalysis.pbs']
            clusterProcessWrapup = r6_shell.run(clusterProcessWrapupCommand, cwd=pbs_dir, encoding='utf-8')
            job_ids.update({'clusterWrapup': str(clusterProcessWrapup.output)[:-2]})

            classifierProcessCommand = ['qsub', '-W', 'depend=afterok:{}'.format(job_ids['clusterWrapup']),
                                        'MLClusterClassifier.pbs']
            classifierProcess = r7_shell.run(classifierProcessCommand, cwd=pbs_dir, encoding='utf-8')
            job_ids.update({'classifier': str(classifierProcess.output)[:-2]})

            figureCommand = ['qsub', '-W',
                             'depend=afterok:{}'.format(job_ids['classifier']), 'FigurePreparer.pbs']
            figureProcess = r6_shell.run(figureCommand, cwd=pbs_dir, encoding='utf-8')
            job_ids.update({'figures': str(figureProcess.output)[:-2]})

            outfileCommand = ['qsub', '-W', 'depend=afterok:{}'.format(job_ids['figures']), 'OutfilePreparer.pbs']
            outfileProcess = r6_shell.run(outfileCommand, cwd=pbs_dir, encoding='utf-8')
            job_ids.update({'oufile': str(outfileProcess.output)[:-2]})

            backupCommand = ['qsub', '-W', 'depend=afterok:{}'.format(job_ids['outfile']), 'Backup.pbs']
            backupProcess = r6_shell.run(backupCommand, cwd=pbs_dir, encoding='utf-8')
            job_ids.update({'backup': str(backupProcess.output)[:-2]})

            print(time.asctime() + ' -- jobs submitted. Job IDs: ', file=f)
            print(time.asctime() + ' -- jobs submitted. Job IDs: ')
            for job, job_id in job_ids.items():
                print('   ' + job + ':' + job_id, file=f)
                print('   ' + job + ':' + job_id)
            print('\n\n')
            print('\n\n', file=f)

    if args.Computer == 'PACE':
        print('finalizing submission')

        template_dir = 'data/CichlidBowerTracker/PbsTemplates'
        updateAnalysisCommand = ['qsub', '-W', 'depend=after:{}'.format(job_ids['backup']), 'UpdateAnalysis.pbs']
        updateAnalysisProcess = r6_shell.run(updateAnalysisCommand, cwd=template_dir, encoding='utf-8')

        print('All jobs for all projects submitted. Safe to close local shell')

    else:
        f.close()
        summarizeProcess = subprocess.run(['python3', 'CichlidBowerTracker.py', 'UpdateAnalysisSummary'])
