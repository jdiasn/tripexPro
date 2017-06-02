import glob
import numpy as np
import pandas as pd
from sys import argv
from netCDF4 import Dataset

import writeData
import tripexLib as trLib


#input File Path
path = argv[1]
#output File Path
outputPath = argv[2]
#prefix
prefix = argv[3]
#-----------------------------

#--Time Definitions-----------
year = int(argv[4])
month = int(argv[5])
day = int(argv[6])
beguinTimeRef = int(argv[7])
timeFreq = argv[8]
timeTolerance = argv[9]

dateName = str(year)+str(month)+str(day)
endTimeRef = beguinTimeRef + 1
start = pd.datetime(year, month, day,beguinTimeRef, 0, 0)
end = pd.datetime(year, month, day, endTimeRef, 0, 0)
timeRef = pd.date_range(start, end, freq=timeFreq)
timeRefUnix = np.array(timeRef,float)
usedIndexTime = np.ones((len(timeRef)))*np.nan
#-----------------------------

#--Range Definitions----------
beguinRangeRef = int(argv[10])
endRangeRef = int(argv[11])
rangeFreq = int(argv[12])
rangeTolerance = int(argv[13])
rangeRef = np.arange(beguinRangeRef, endRangeRef, rangeFreq)
usedIndexRange = np.ones((len(rangeRef)))*np.nan
#-----------------------------

#--Radar variables------------
radar = argv[14]
rangeGateOffSet = float(argv[15]) 
variableName = argv[16] 
#-----------------------------

#output File Definitions
outPutFile = ('_').join([prefix, dateName,
                       str(beguinTimeRef)+'.nc'])
outPutFilePath = ('/').join([outputPath, outPutFile])
print outPutFilePath

#output variable name
if variableName == 'Zg':    
   varFinalName = 'Ze'
 
elif variableName == 'vm' or variableName == 'vd':
   varFinalName = 'v'

elif variableName == 'sigma':
   varFinalName = 'SW'

else:
   varFinalName = variableName

varNameOutput = ('_').join([varFinalName, radar])


#Files to process
fileList = trLib.getFileList(path, dateName,
			    beguinTimeRef, radar)


#fileList = glob.glob(('/').join([path, prefix+dateName+str(beguinTimeRef)+'*.nc']))
#fileList.sort()

#creat a function ------------------
#listAux = []
#for nameFile in fileList:
#   rootgrp = Dataset(nameFile, 'r')
#   elv = rootgrp.variables['elv'][:]
#   if len(np.argwhere(elv !=90))==0:
#     listAux.append(nameFile)
#fileList = listAux
#-----------------------------------

#To Ka version----------------------
#varResTimeEmpty = trLib.getEmptyMatrix(len(timeRef), len(ranges))
#varResTimeRangeEmpty = trLib.getEmptyMatrix(len(rangeRef), len(timeRef))
#-----------------------------------

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
    
   #it gets desireble variable 
   var = rootgrp.variables[variableName][:]
   #Ka version ------------
   #if radar == 'Ka': 
   #   var = np.log10(var)
   #-----------------------
   if radar == 'W':
      var[var==-999.] = np.nan 
   if radar == 'X' and varFinalName == 'Ze':
      var[var==-32] = np.nan
   var = np.ma.masked_invalid(var)
    
   rootgrp.close()
    
   ##Nearest in time -------
   varData = pd.DataFrame(index=humamTimeW, columns=ranges, data=var)
   varData['times'] = humamTimeW
   varData = varData.drop_duplicates(subset=['times'])

   timeIndexList = trLib.getIndexList(varData, timeRef, timeTolerance)
 
   #empty data frame
   emptyDataFrame = pd.DataFrame(index=timeRef, columns=varData.columns)   
   resampledTime = trLib.getResampledDataPd(emptyDataFrame, varData,
                                           timeIndexList)

   #varResTimeEmpty = trLib.getEmptyMatrix(len(timeRef), len(ranges))
   #varResTimeFilled, usedIndexTime = trLib.getResampledData(varResTimeEmpty,
   #                                                        var, timeIndexList, 
   #                                                       usedIndexTime)
#   timeDeviation = timeRef.second-pd.to_datetime(list(resampledTime.times)).second
   
#   resampledTime['delta_time']=timeDeviation

#   intTimeTol = int(timeTolerance[:-1])
   #print intTimeTol 
#   timeDevCorrection = 60. + resampledTime.delta_time[resampledTime.delta_time<-intTimeTol]
 #  resampledTime.loc[resampledTime.delta_time<-intTimeTol,'delta_time']=timeDevCorrection
 #  timeDeviation = resampledTime.delta_time

   timeDeviation = trLib.getDeviationPd(timeRef, resampledTime, timeTolerance)

   del resampledTime['times']

   #it replaces original resampledTime with resampledTime transposed
   resampledTime = resampledTime.T 
   #-----------------------


   ##Nearest in range -----
   resampledTime['ranges']=ranges

   rangeIndexList = trLib.getIndexList(resampledTime, rangeRef, rangeTolerance)
   emptyDataFrame = pd.DataFrame(index=rangeRef, columns=resampledTime.columns)
   #varResTimeRangeFilled, usedIndexRange = trLib.getResampledData(varResTimeRangeEmpty,
   #                                                               varResTimeFilled, 
   #                                                               rangeIndexList, 
   #                                                               usedIndexRange)

   resampledTimeRange = trLib.getResampledDataPd(emptyDataFrame, resampledTime,
                                                rangeIndexList)  
#   rangeDeviation = rangeRef - resampledTimeRange.ranges
   rangeDeviation = trLib.getDeviationPd(rangeRef, resampledTimeRange)
   del resampledTimeRange['ranges']  

   #Calculate time deviation
  # timeDeviation = trLib.getDeviation(timeRef, humamTimeW, usedIndexTime)
  # auxTimeDeviation[timeDeviation!=-999] = timeDeviation[timeDeviation!=-999]
 

   #-----------------------



#Calculate range deviation
#rangeDeviation = trLib.getDeviation(rangeRef, ranges, usedIndexRange)
#Final resampled (Time and Range)
#varResTimeRangeFilled = np.ma.masked_invalid(varResTimeRangeFilled)
#print resampledTimeRange
#writing data in file
rootgrpOut = writeData.createNetCdf(outPutFilePath)
time_ref = writeData.createTimeDimension(rootgrpOut, timeRefUnix)
range_ref = writeData.createRangeDimension(rootgrpOut, rangeRef)

timeDeviation = np.array(timeDeviation.astype(np.float32))
time_dev = writeData.createDeviation(rootgrpOut, timeDeviation,
                                    'delta_time', radar)

rangeDeviation = np.array(rangeDeviation.astype(np.float32))
range_dev = writeData.createDeviation(rootgrpOut, rangeDeviation,
                                          'delta_altitude', radar)

resampledTimeRange = np.array(resampledTimeRange.T.astype(np.float32))
var_resampled = writeData.createVariable(rootgrpOut, resampledTimeRange,
                                        varFinalName, varNameOutput, radar)
rootgrpOut.close()

print 'Done %s'%(varNameOutput)
