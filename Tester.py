import subprocess, os, sys

h264_video = '0001_vid.h264'
mp4_video = '0001_vid_test.mp4'
command = ['ffmpeg', '-r', '30', '-i', h264_video, '-c:v', 'copy', '-r', '30', mp4_video, '-y']
subprocess.run(command)
assert os.path.isfile(mp4_video)
try:
    assert os.stat(mp4_video).st_size >= os.stat(h264_video).st_size
except AssertionError:
    print('Bad Conversion')
    sys.exit()
