#!/opt/psychopy/PsychoPy-2025.1.1-Python3.10/.venv/bin/python
import pandas as pd
import sys
fpath = sys.argv[1]
if len(sys.argv)>2:
    key = sys.argv[2]
    df = pd.read_hdf(fpath, key=key)
else:
    df = pd.read_hdf(fpath)

df.to_csv(sys.stdout, index=False)
