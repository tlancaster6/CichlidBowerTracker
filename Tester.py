import subprocess

h264_video = '0001_vid.h264'
mp4_video = '0001_vid_test.mp4'
command = ['ffmpeg', '-r', '30', '-i', h264_video, '-c:v', 'copy', '-r', '30', mp4_video, '-y']
subprocess.run(command)
