from sys import argv
import glob
import numpy as np
import pandas as pd
from netCDF4 import Dataset

import writeData
import tripexLib as trLib

#input File Path
path = argv[1]
#output File Path
outputPath = argv[2]
#-----------------------------

#--Time Definitions-----------
year = int(argv[3])
month = int(argv[4])
day = int(argv[5])
beguinTimeRef = int(argv[6])
timeFreq = argv[7]
timeTolerance = argv[8]

dateName = str(year)+str(month)+str(day)
endTimeRef = beguinTimeRef + 1
start = pd.datetime(year, month, day,beguinTimeRef, 0, 0)
end = pd.datetime(year, month, day, endTimeRef, 0, 0)
timeRef = pd.date_range(start, end, freq=timeFreq)
timeRefUnix = np.array(timeRef,float)
usedIndexTime = np.ones((len(timeRef)))*np.nan
#-----------------------------

#--Range Definitions----------
beguinRangeRef = int(argv[9])
endRangeRef = int(argv[10])
rangeFreq = int(argv[11])
rangeTolerance = int(argv[12])
rangeRef = np.arange(beguinRangeRef, endRangeRef, rangeFreq)
usedIndexRange = np.ones((len(rangeRef)))*np.nan
#-----------------------------

#--Radar variables------------
radar = argv[13]
rangeGateOffSet = float(argv[14]) #X
variableName = argv[15] #X
#-----------------------------

#output File Definitions
outPutFile = ('_').join(['tripex_3fr_L1_momTest', dateName,
                       str(beguinTimeRef)+'.nc'])
outPutFilePath = ('/').join([outputPath, outPutFile])
print outPutFilePath


#output variable  name
if variableName == 'Zg':    
   varFinalName = 'Ze'
    
elif variableName == 'vm' or variableName == 'VELg':
   varFinalName = 'Vd'

elif variableName == 'RMS':
   varFinalName = 'SW'

else:
   varFinalName = variableName

varNameOutput = ('_').join([varFinalName, radar])



#Files to process
fileList = trLib.getFileList(path, dateName,
			    beguinTimeRef, radar)

#creat a function ------------------
listAux = []
for nameFile in fileList:
   rootgrp = Dataset(nameFile, 'r')
   elv = rootgrp.variables['elv'][:]
   lenRange = len(rootgrp.variables['range'])
   if len(np.argwhere(elv !=90))==0:
      listAux.append(nameFile)
   rootgrp.close()
#-----------------------------------


varAux = np.zeros((len(timeRef), len(rangeRef)))
varAux = varAux.transpose()#*-999.

fileList = listAux

varResTimeEmpty = trLib.getEmptyMatrix(len(timeRef), lenRange)
varResTimeRangeEmpty = trLib.getEmptyMatrix(len(rangeRef), len(timeRef))

for radarFile in fileList:

   #it opens the file 
   print radarFile
   rootgrp = Dataset(radarFile, 'r')
     
   epoch = trLib.getEpochTime(rootgrp, radar)
   timesW = rootgrp.variables['time'][:]

   #timesW = timesWAtt[:]
   humamTimeW = epoch + pd.to_timedelta(timesW, unit='S')
    
   #it gets the range and corrects for the reference height
   ranges =rootgrp.variables['range'][:] + rangeGateOffSet
   elv = rootgrp.variables['elv'][:]

   varResTimeRangeEmpty = trLib.getEmptyMatrix(len(rangeRef), len(timeRef))

   #it gets desireble variable 
   var = rootgrp.variables[variableName][:]

   if varFinalName == 'Ze':
      var = 10*np.log10(var)   
   else:
      pass

   var = np.ma.masked_invalid(var)
   np.ma.set_fill_value(var, np.nan)

   rootgrp.close()
    
   ##Nearest in time
   varData = pd.DataFrame(index=humamTimeW, columns=ranges, data=var)
   varData['times'] = timesW
   varData = varData.drop_duplicates(subset=['times'])

 
   timeIndexList = trLib.getIndexList(varData, timeRef, timeTolerance)
   #varResTimeEmpty = trLib.getEmptyMatrix(len(timeRef), len(ranges))
   varResTimeFilled, usedIndexTime = trLib.getResampledData(varResTimeEmpty, var,
                                                            timeIndexList, usedIndexTime)
    
   ##Nearest in range
   varResTimeFilled = varResTimeFilled.transpose()
   rangeRefTable = varData.transpose()

   rangeIndexList = trLib.getIndexList(rangeRefTable, rangeRef, rangeTolerance)
   #varResTimeRangeEmpty = trLib.getEmptyMatrix(len(rangeRef), len(timeRef))
   varResTimeRangeFilled, usedIndexRange = trLib.getResampledData(varResTimeRangeEmpty,
                                                                  varResTimeFilled, 
                                                                  rangeIndexList, 
                                                                  usedIndexRange)
    
   varResTimeRangeEmpty = varResTimeRangeFilled*1
   #test = varResTimeRangeFilled
  
#Final resampled (Time and Range)
varResTimeRangeFilled = np.ma.masked_invalid(varResTimeRangeFilled)

#To write the data
rootgrpOut = writeData.createNetCdf(outPutFilePath)
time_ref = writeData.createTimeDimension(rootgrpOut, timeRefUnix)
range_ref = writeData.createRangeDimension(rootgrpOut, rangeRef)
var_resampled = writeData.createVariable(rootgrpOut, varResTimeRangeFilled.transpose(),
                                        varFinalName, varNameOutput, radar)
rootgrpOut.close()

print 'Done %s'%(varNameOutput)






