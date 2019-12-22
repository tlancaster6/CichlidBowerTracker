import subprocess, os, sys, datetime


class Tester:

    def __init__(self):
        self.mp4_video = os.getenv('HOME') + '/scratch/TI2_5_newtray/0001_vid.mp4'

    def _convertVideo(self):
        h264_video = self.mp4_video.replace('.mp4', '.h264')
        assert os.path.isfile(h264_video)
        command = ['ffmpeg', '-r', '30', '-i', h264_video, '-c:v', 'copy', '-r', '30', self.mp4_video, '-y']
        print('  VideoConversion: ' + ' '.join(command) + ',Time' + str(datetime.datetime.now()))
        output = subprocess.run(command)

        assert os.path.isfile(self.mp4_video)

        # Ensure the conversion went ok.
        try:
            assert os.stat(self.mp4_video).st_size >= os.stat(h264_video).st_size
        except AssertionError:
            print('Bad Conversion')
            sys.exit()


Tester()._convertVideo()
