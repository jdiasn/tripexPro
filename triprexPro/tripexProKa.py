import glob
import numpy as np
import pandas as pd
from netCDF4 import Dataset

import writeData
import tripexLib as trLib


#input File Definitions
path = '/home/jdias/Projects/radarData'
prefix = 'joyrad94_joyce_compact_'

radar = 'Ka'

#variableName = 'Zg'
#variableName = 'VEL'
#variableName = 'RMS'
variableName = 'LDR'

#Time Definitions
year = 2015
month = 11
day = 24
dateName = str(year)+str(month)+str(day)
beguinTimeRef = 17
endTimeRef = beguinTimeRef + 1

start = pd.datetime(year, month, day,beguinTimeRef, 0, 0)
end = pd.datetime(year, month, day, endTimeRef, 0, 0)

timeRef = pd.date_range(start, end, freq='4S')
timeRefUnix = np.array(timeRef,float)
usedIndexTime = np.ones((len(timeRef)))*np.nan
timeTolerance = '2S'

#Range Definitions
beguinRangeRef = 100
endRangeRef = 12000

rangeRef = np.arange(beguinRangeRef, endRangeRef, 30)
usedIndexRange = np.ones((len(rangeRef)))*np.nan
rangeTolerance = '17'

rangeGateOffSet = 0 #Ka
#rangeGateOffSet = -2 #W
#rangeGateOffSet = -17.5 #X


#output File Definitions
outputPath = '/home/jdias/Projects/radarDataResampled'
outPutFile = ('_').join(['tripex_3fr_L1_mam', dateName, str(beguinTimeRef)+'.nc'])
outPutFilePath = ('/').join([outputPath, outPutFile])

#output variable  name
if variableName == 'Zg':    
   varFinalName = 'Ze'
    
elif variableName == 'vm' or variableName == 'VEL':
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
   varData = pd.DataFrame(index=humamTimeW, columns=ranges, data=var).drop_duplicates()
 
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






