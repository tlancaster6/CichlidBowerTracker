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
                        help='Use if you want to control how many workers this analysis uses', default=1)
prepParser.add_argument('-g', '--GPUs', type=int, help='Use if you want to control how many GPUs this analysis uses',
                        default=1)

pacePrepParser = subparsers.add_parser('PacePrep',
                                       help='This command generates the pbs scripts that will be necessary to run analysis of a project on PACE')
pacePrepParser.add_argument('-p', '--ProjectIDs', nargs='+', required=True, type=str,
                            help='Manually identify the projects you want to analyze')
pacePrepParser.add_argument('-t', '--TempDir', type=str,
                            help='Optional. Manually designate the temp directory. Enter LSS to use local scratch storage on PACE',
                            default=None)
pacePrepParser.add_argument('-m', '--Email', type=str,
                            help='Optional. Enter an email that will receive updates during PACE analysis',
                            default=None)
pacePrepParser.add_argument('-w', '--Workers', type=int,
                            help='Use if you want to control the max number of workers used for an individual job',
                            default=64)

projectParser = subparsers.add_parser('ProjectAnalysis',
                                      help='This command performs a single type of analysis of the project. It is meant to be chained together to perform the entire analysis')
projectParser.add_argument('AnalysisType', type=str,
                           choices=['Download', 'Depth', 'Cluster', 'CreateFrames', 'MLClassification',
                                    'MLFishDetection', 'Figures', 'Backup', 'Outfiles'],
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
        pp_obj = PP(projectID, args.Workers)
        pp_obj.runPrepAnalysis()

    # pp_obj.backupAnalysis()
    ap_obj.updateAnalysisFile(newProjects=False, projectSummary=False)

elif args.command == 'PacePrep':
    ap_obj = AP()
    if ap_obj.checkProjects(args.ProjectIDs):
        sys.exit()

    for projectID in args.ProjectIDs:
        pp_obj = PP(projectID, args.Workers, args.TempDir)
        pp_obj.runPacePrep(args.Email)

elif args.command == 'ProjectAnalysis':

    if args.DownloadOnly and args.AnalysisType in ['Download', 'Backup']:
        print('DownloadOnly flag cannot be used with Download or Backup AnalysisType')
        sys.exit()

    args.ProjectIDs = args.ProjectID  # format that parseProjects expects

    pp_obj = PP(args.ProjectID, args.Workers, args.TempDir)

    if args.AnalysisType == 'Download' or args.DownloadOnly:
        pp_obj.downloadData(args.AnalysisType)

    elif args.AnalysisType == 'PacePrep':
        pp_obj.runPacePrep(args.Email)

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
        local_shell = spur.LocalShell()
        pids = ' '.join(args.ProjectIDs)
        email = '' if args.Email is None else ' -m ' + args.Email
        pacePrepCommands = ('conda activate CichlidBowerTracker; '
                            'python3 CichlidBowerTracker.py PacePrep -t LSS -p {0}{1}'.format(pids, email))
        local_shell.run(['sh', '-c', pacePrepCommands])
        datamover_shell = spur.SshShell(hostname='iw-dm-4.pace.gatech.edu', username=uname, password=pword)
        r6_shell = spur.SshShell(hostname='login-s.pace.gatech.edu', username=uname, password=pword)
        r7_shell = spur.SshShell(hostname='login7-d.pace.gatech.edu', username=uname, password=pword)

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
            code_dir = 'data/CichlidBowerTracker/'

            print(time.asctime() + ' -- Analyzing projectID: ' + projectID, file=f)
            print(time.asctime() + ' -- Analyzing projectID: ' + projectID)

            print(time.asctime() + ' -- Downloading data to Pace', file=f)
            print(time.asctime() + ' -- Downloading data to Pace')

            downloadCommand = ('module load anaconda3; '
                               'conda activate CichlidBowerTracker; '
                               'python3 CichlidBowerTracker.py ProjectAnalysis Download {}'.format(projectID))
            downloadProcess = datamover_shell.run(['sh', '-c', downloadCommand], cwd=code_dir, encoding='utf-8')
            print(time.asctime() + ' -- Submitting pbs scripts', file=f)
            print(time.asctime() + ' -- Submitting pbs scripts')
            depthProcess = r6_shell.run(['qsub', 'DepthAnalysis.pbs'], cwd=pbs_dir, encoding='utf-8')
            clusterProcess = r6_shell.run(['qsub', 'ClusterAnalysis.pbs'], cwd=pbs_dir, encoding='utf-8')
            job_ids = {'depth': str(depthProcess.output), 'cluster': str(clusterProcess.output)}
            clusterProcessWrapup = r6_shell.run(
                ['sh', '-c', 'qsub -W depend=afterok:{} PostClusterAnalysis.pbs'.format(job_ids['cluster'])], cwd=pbs_dir,
                encoding='utf-8')
            classifierProcess = r7_shell.run(
                ['sh', '-c', 'qsub -W depend=afterok:{} MLClusterClassifier.pbs'.format(str(clusterProcessWrapup.output))],
                cwd=pbs_dir, encoding='utf-8')
            job_ids.update({'classifier': str(classifierProcess.output)})
            figureCommand = ['qsub', '-W', 'depend=afterok:{0}:{1}'.format(job_ids['cluster'], job_ids['classifier']),
                 'FigurePreparer.pbs']
            figureProcess = r6_shell.run(figureCommand, cwd=pbs_dir, encoding='utf-8')
            job_ids.update({'figures': str(figureProcess.output)})
            outfileCommand = ['qsub', '-W', 'depend=afterok:{}'.format(job_ids['figures']), 'OutfilePreparer.pbs']
            outfileProcess = r6_shell.run(outfileCommand, cwd=pbs_dir, encoding='utf-8')

            print(time.asctime() + ' -- All jobs submitted. Job IDs: ', file=f)
            print(time.asctime() + ' -- All jobs submitted. Job IDs: ')
            for job, job_id in job_ids.items():
                print('   ' + job + ':' + job_id, file=f)
                print('   ' + job + ':' + job_id)

            time.sleep(600)

            print(time.asctime() + ' -- Backing up analysis to Dropbox')
            backupCommand = ('module load anaconda3; '
                             'conda activate CichlidBowerTracker; '
                             'python3 CichlidBowerTracker.py ProjectAnalysis Backup {}'.format(projectID))
            backupProcess = datamover_shell.run(['sh', '-c', backupCommand], encoding='utf-8')

            print(time.asctime() + ' -- Analysis complete for ' + projectID + '\n\n')

    f.close()
    summarizeProcess = subprocess.run(['python3', 'CichlidBowerTracker.py', 'UpdateAnalysisSummary'])
