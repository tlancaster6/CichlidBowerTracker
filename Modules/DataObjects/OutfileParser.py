import os, glob, re
import pandas as pd

"""Reads the output/error files produced by a PACE run and parses the information into a dataframe"""


class OutfileParser:

    def __init__(self, projFileManager):
        self.projFileManager = projFileManager

    def validateInputData(self):
        assert len(glob.glob(self.projFileManager.localTroubleshootingDir + '*.out*')) > 0,\
            'Error: No Outfiles in Local Troubleshooting Directory'

    def parseOutfiles(self):
        regexes = {'video': re.compile(r'Processing video: Videos/(?P<video>.*),'),
                   'requested': re.compile(r'Resources:(?P<requested>.*)\n'),
                   'used': re.compile(r'Rsrc Used:(?P<used>.*)\n'),
                   'start': re.compile(r'Begin PBS Prologue (?P<start>.*)\n'),
                   'end': re.compile(r'End PBS Epilogue (?P<end>.*)\n'),
                   'outcome': re.compile(r'PBS: job killed: (?P<outcome>.*)\n')}

        rows = []
        for f_name in glob.glob(self.projFileManager.localTroubleshootingDir + '*.out*'):
            row = {}
            with open(f_name) as f:
                line = f.readline()
                while line:
                    for key, rx in regexes.items():
                        match = rx.search(line)
                        if match:
                            if (key == 'requested') or (key == 'used'):
                                row.update([tuple(item.split('=', 1)) for item in re.split(r',|(?=.):(?=\D)', match.group(key))])
                            else:
                                row.update({key: match.group(key)})
                            if 'outcome' not in row.keys():
                                row.update({'outcome': 'successful'})
                    line = f.readline()
            rows.append(row)
        all_data = pd.DataFrame(rows)
        all_data.to_csv(self.projFileManager.localTroubleshootingDir + 'outfileSummary.csv')

