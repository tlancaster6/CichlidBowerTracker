# CichlidBowerTracker
Contains code to run Raspberry Pis/Depth Sensors and analyze the resulting data

## Getting Started
### local machine setup
(1) install anaconda on your local machine, if you have not already. Instructions at 
https://docs.anaconda.com/anaconda/install/

(2) set up your local conda environment by running the following commands in your terminal

conda create -n CichlidBowerTracker python=3.7 <br/>
conda activate CichlidBowerTracker <br/>
pip install spur <br/>
conda install -yc anaconda numpy pandas opencv scipy matplotlib seaborn scikit-learn statsmodels git <br/>
conda install -yc conda-forge scikit-image rclone hmmlearn <br/>
conda install -yc pytorch pytorch torchvision <br/>

(3) download the repo by executing the following commands (in sequence) in your terminal

mkdir -p ~/data <br/>
cd ~/data <br/>
git clone https://github.com/tlancaster6/CichlidBowerTracker.git <br/>

(4) Check if you have already configured the required rclone remote by running 'rclone listremotes', and confirming that
there is a remote called 'cichlidVideo'. If not, initiate a new a rclone remote on your local machine using the command 
'rclone config', and press 'n' to choose the 'New Remote' option. Name the remote 'cichlidVideo', choose 'Dropbox' as
the storage type, leave 'dropbox app client id' and 'dropbox app client secret' blank, select 'No' when asked if you 
want to edit the advanced config, and 'Yes' when asked if you want to use the auto config. Follow the instructions
in that print in the terminal to authorize rclone access. press 'y' to confirm that everything is correct, and 'q' to 
exit the config. 


### PACE setup
(1) After completing the local machine setup, described above, ssh into the RHEL6 PACE headnode with the following 
command (changing "you_username" to your actual username), and enter your password to continue

ssh your_username@login-s.pace.gatech.edu

(2) If you haven't already, execute the following commands to create a symlinked .conda folder in your data directory to 
prevent python environments from filling up your smaller home directory

cd ~/ <br/>
mkdir ~/data/.conda <br/>
ln -s ~/data/.conda .conda <br/>

(3) Load the anaconda module with the following command

module load anaconda3 <br/>

(4) Set up the CichlidBowerTracker conda environment by executing the following commands in sequence. Ignore any 
warnings that 'a newer version of conda exists' and you should update
conda create -n CichlidBowerTracker python=3.7 <br/>
conda activate CichlidBowerTracker <br/>
pip install spur <br/>
conda install -yc anaconda numpy pandas opencv scipy matplotlib seaborn scikit-learn statsmodels git <br/>
conda install -yc conda-forge scikit-image rclone hmmlearn <br/>
conda install -yc pytorch pytorch torchvision cudatoolkit=10.1 <br/>

(5) download the project repository from github using the following commands

cd ~/data <br/>
git clone https://github.com/tlancaster6/CichlidBowerTracker.git <br/>


(6) Configure an rclone remote on PACE. Initiate a new a rclone remote using the command 'rclone config', and press 'n' 
to choose the 'New Remote' option. Name the remote 'cichlidVideo', choose 'Dropbox' as the storage type, leave 
'dropbox app client id' and 'dropbox app client secret' blank, select 'No' when asked if you want to edit the advanced 
config, and 'No' when asked if you want to use the auto config. Without closing your current shell, open a new terminal
window or tab to enter a local shell session, run the command 'conda activate CichlidBowerTracker', and then run the 
command 'rclone authorize "dropbox"'. Follow the on-screen directions to copy your access token, switch to the
PACE connected shell that you left open earlier, paste in your token, and press enter. press 'y' to confirm that 
everything is correct, and 'q' to exit the config. 
 
# Project Pipeline
This section contains basic instructions for running projects through the analysis pipeline. For simplicity, the
use case shown corresponds to running a batch of three projects --  specifically MC6_5, CV10_3, and TI2_4 -- through 
the pipeline. For clarity, some bash commands have been enclosed in single quotes to separate them from surrounding
prose, but these quotes should not be included when actually executing the command. 

## Manual Prep
Note that this stage requires only that the local machine (not PACE) has been set up according to the instructions 
above. 

(1) open the terminal and issue the command 'cd ~/data' to switch to the proper directory <br/>
(2) activate the conda environment using the command 'conda activate CichlidBowerTracker' <br/>
(3) initiate manual prep using the following command:

python3 CichlidBowerTracker.py ManualPrep -p MC6_5 CV10_3 TI2_4

(4) follow on-screen instructions to manually prep the three projects. All required uploads and downloads will occur 
automatically <br/>

## Initiating Project Analysis
(1) open the terminal and issue the command 'cd ~/data' to switch to the proper directory <br/>
(2) activate the conda environment using the command 'conda activate CichlidBowerTracker' <br/>
(3) initiate analysis using the following command:

python3 CichlidBowerTracker.py TotalProjectAnalysis PACE -p MC6_5 CV10_3 TI2_4

(4) when prompted, enter the username and password you use for PACE <br/>
(5) leave the terminal open until it indicates that it is safe to close the local shell

## Monitoring Progress
(1) open two terminal windows. In one, log into the RHEL6 headnode using the command 
'ssh your_username@login-s.pace.gatech.edu'. In the terminal window, log into the RHEL7 headnode using the command
'ssh your_username@login7-d.pace.gatech.edu'. Enter your username and password whenever prompted <br/>
(2) to see all of your current jobs, their job id's, and their status, run the command 'qstat -u your_username' 
(with "your_username changed to your actual username) in both shells. Most of your jobs will show up in the RHEL6 
shell, but the jobs that require a GPU (and only those jobs) will only show up in the RHEL7 shell. Jobs with a status
of "C" have completed (either successfully or unsuccessfully), jobs with a status of "Q" are ready to start but waiting
for resources, jobs with a status of "H" are waiting for another job to finish successfully before attempting to start, 
and jobs with a status of "R" are actively running. <br/>
(3) to see more information about a particular job, use the command 'qstat -f job_id', with job_id replaced with an 
actual job id number

## Tips and Tricks
(1) When you run TotalProjectAnalysis with multiple projects, they will be automatically staggered to reduce resource
usage spikes. This lets you initiate TotalProjectAnalysis on a large batch of projects without having to worry about
them fighting for the same nodes all the time. Still, it's usually easier to run in batches smaller than ten projects, 
and let all projects in the batch run to completion before submitting a new batch. Doing so allows you to go in after 
each batch and check for projects that failed, troubleshoot the cause, and clean up any leftover files before starting
the next batch.

## Troubleshooting Failed Analysis
When everything goes according to plan, your job ends as soon as you've initiated project analysis. Everything else 
should run automatically, including the upload to Dropbox and deletion of these files from PACE. Unfortunately, this
will not always be the case. Analysis of a particular project can fail for numerous reasons, including but not limited 
to a bad configuration, PACE outages and hiccups, and missing or corrupted data. When this happens, you'll need to do
some cleanup and troubleshooting. 

First, log into the RHEL6 and RHEL7 headnodes, and run 'qstat -u your_username' to see your current jobs. If the status
of every jobs is "C", or nothing prints, congrats -- all projects in the batch ran successfully, and you'll find the
results on Dropbox. If any of the jobs are marked "Q" or "R", chances are the batch needs some more time -- some portion 
of it is either actively running or just waiting on resources to become available. If, however, some of your jobs are
marked "H", and the rest are marked "C", you have a problem -- at least one of those jobs marked "C" must have thrown an 
error, leaving the jobs marked "H" to wait in vain for it to complete successfully. You have a few options here.

First, the bare minimum: if you have tons of projects to run, and can't be bothered to investigate the occasional bad
seed, you can just purge the leftover files and move on to your next batch. To do this, ssh into the RHEL6 or RHEL7
headnode and use the command 'ls ~/scratch' to list the contents of your scratch directory. Look for directories named
after projects that were in your batch. When a project completes the pipeline and uploads, these directories get 
deleted, so any such directories remaining after a batch has run correspond to projects that failed. It's a good idea to
jot down these project names so you can come back to them at a later date. Now, assuming you aren't keeping anything
important in you scratch directory, you can simply run the command 'rm -r scratch/*' to empty it and you're ready for 
the next  batch. Alternatively, you can cd into the scratch directory, and use the 'rm -r' command to remove the project
directories individually, as well as the two directories called '__UploadCommands' and '__AnalysisLog'

If, however, you's like to know why a particular project failed (and maybe even fix it), or if every project you run
fails and you'd like to know why, you can start digging into the debugging logs. Log into the RHEL6 or RHEL7 headnode, 
cd into your scratch directory, and use ls to list the contents. Pick a failed project, cd into that project's 
directory, and then into the directory called "Troubleshooting". Here, you'll find a number of files with the ".out"
suffix, each containing the console output generated during a particular job, including any error messages. Use these
to figure out what went wrong, use scp to make a local copy of any files you want to keep, and clean out the scratch
directory as described in the previous paragraph. You can now start a new batch, or try rerunning a failed project
if you think you fixed the problem. 

