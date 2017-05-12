
import glob
import numpy as np
import pandas as pd
from netCDF4 import Dataset

import writeData
import tripexLib as trLib


#input File Definitions
path = '/home/jdias/Projects/radarData'
dateName = '20151124'
prefix = 'joyrad94_joyce_compact_'
variableName = 'Ze'
radar = 'W'

#Time Definitions
year = 2015
month = 11
day = 24

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
rangeGateOffSet = -2

#output File Definitions
outputPath = '/home/jdias/Projects/radarDataResampled'
outPutFile = ('_').join(['tripex_3fr_L1_mam', dateName, str(beguinTimeRef)+'.nc'])
outPutFilePath = ('/').join([outputPath, outPutFile])

if variableName == 'Zg':    
   varFinalName = 'Ze'
    
elif variableName == 'vm':
   varFinalName = 'Vd'

else:
   varFinalName = variableName

varNameOutput = ('_').join([varFinalName, radar])



#Files to process
fileList = glob.glob(('/').join([path, prefix+dateName+str(beguinTimeRef)+'*.nc']))
fileList.sort()


for radarFile in fileList:

   #it opens the file 
   print radarFile
   rootgrp = Dataset(radarFile, 'r')
       
   #it gets time and attributes
   timesWAtt = rootgrp.variables['time']
   epochDay, epochMonth, epochYear = getattr(timesWAtt, 'long_name').split(' ')[-2].split('.')
   epochDay, epochMonth, epochYear = int(epochDay), int(epochMonth), int(epochYear)
        
   timesW = timesWAtt[:]
   epoch = pd.datetime(epochYear, epochMonth, epochDay)
   humamTimeW = epoch + pd.to_timedelta(timesW, unit='S')
    
   #it gets the range and corrects for the reference height
   ranges =rootgrp.variables['range'][:] + rangeGateOffSet  
   
   #it gets desireble variable 
   var = rootgrp.variables[variableName][:]
   var[var==-999.] = np.nan 
    
   rootgrp.close()
    
   ##Nearest in time
   varData = pd.DataFrame(index=humamTimeW, columns=ranges, data=var).drop_duplicates()
 
   timeIndexList = trLib.getIndexList(varData, timeRef, timeTolerance)
   varResTimeEmpty = trLib.getEmptyMatrix(len(timeRef), len(ranges))
   varResTimeFilled, usedIndexTime = trLib.getResampledData(varResTimeEmpty, var,
                                                            timeIndexList, usedIndexTime)
    
   ##Nearest in range
   varResTimeFilled = varResTimeFilled.transpose()
   rangeRefTable = varData.transpose()

   rangeIndexList = trLib.getIndexList(rangeRefTable, rangeRef, rangeTolerance)
   varResTimeRangeEmpty = trLib.getEmptyMatrix(len(rangeRef), len(timeRef))
   varResTimeRangeFilled, usedIndexRange = trLib.getResampledData(varResTimeRangeEmpty,
                                                                  varResTimeFilled, 
                                                                  rangeIndexList, 
                                                                  usedIndexRange)


#Final resampled (Time and Range)
varResTimeRangeFilled = np.ma.masked_invalid(varResTimeRangeFilled)



rootgrpOut = writeData.createNetCdf(outPutFilePath)
time_ref = writeData.createTimeDimension(rootgrpOut, timeRefUnix)
range_ref = writeData.createRangeDimension(rootgrpOut, rangeRef)
var_resampled = writeData.createVariable(rootgrpOut, varResTimeRangeFilled.transpose(),
                                        varFinalName, varNameOutput, radar)
rootgrpOut.close()

print 'Done %s'%(varNameOutput)
