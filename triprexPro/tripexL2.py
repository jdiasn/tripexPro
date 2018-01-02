import glob
import numpy as np
import pandas as pd
from sys import argv

import writeData
import offsetLib as offLib
import attenuationLib as attLib

#--File Paths Definition------
#cloudNetFiles input
cloudNetPath = argv[1]
cloudNetFileID = argv[2]
#tripexL1FilesL1 input
dataPathRe = argv[3]
fileId = argv[4]
#tripexL1FilesL2 output
outputPath = argv[5]
prefixL2 = argv[6]
#-----------------------------

#--Time Definitions-----------
year = argv[7]
month = argv[8]
day = argv[9]
timeFreq= argv[10]
timeTolerance = argv[11]

#Define the reference time
start = pd.datetime(int(year), int(month),
                    int(day), 0,0,0)
end = pd.datetime(int(year), int(month),
                  int(day), 23,59,59)

timeRef = pd.date_range(start, end, freq=timeFreq)
#timesRef use the index from tripex data
#-----------------------------

#--Range Definitions----------
beguinRangeRef = int(argv[12]) #botton
endRangeRef = int(argv[13]) #top #original 12000
rangeFreq = int(argv[14]) #rangeFreq
rangeTolerance = int(argv[15]) #tol
rangeRef = np.arange(beguinRangeRef, endRangeRef, rangeFreq)
#rangeRef use the columns from tripex data
#-----------------------------

#--Radar Variables------------
#Definitions to apply the offset correction
Ze_KaMax = int(argv[16]) #[dBZ]
Ze_KaMin = int(argv[17]) #[dBZ]
heightThreshold = int(argv[18]) #[m]
timeWindowLenght = int(argv[19]) #[min]
thresholdPoints = int(argv[20]) #[Threshold of Points]
#------------------------------

cloudNetFile = ('_').join([year+month+day,cloudNetFileID])
cloudNetFilePath = ('/').join([cloudNetPath, year, cloudNetFile])
#print cloudNetFilePath

fileDate = ('').join([year, month, day])
print ('/').join([dataPathRe,fileId+'_'+fileDate+'*.nc'])
fileList = glob.glob(('/').join([dataPathRe,fileId+'_'+fileDate+'*.nc']))


#Radar Frequency
radarFreqs = [9.4, 35.5, 95]#[GHz]

#variables to be corrected
variable={'Ze_X':{'offset': 0, 'colRange':(-25, 35), 'freq':9.4},
          'Ze_Ka':{'offset': 0, 'colRange':(-25, 35), 'freq':35.5},
          'Ze_W':{'offset': 0, 'colRange':(-25, 35), 'freq':95}}
varNames = variable.keys()





