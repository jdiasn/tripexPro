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

#--Files to work--------------- 
cloudNetFile = ('_').join([year+month+day,cloudNetFileID])
cloudNetFilePath = ('/').join([cloudNetPath, year, cloudNetFile])
#print cloudNetFilePath

fileDate = ('').join([year, month, day])
print ('/').join([dataPathRe,fileId+'_'+fileDate+'*.nc'])
fileList = glob.glob(('/').join([dataPathRe,fileId+'_'+fileDate+'*.nc']))
#-----------------------------

#--Radar definitions----------
#Radar Frequency
radarFreqs = [9.4, 35.5, 95]#[GHz]

#variables to be corrected
variable={'Ze_X':{'offset': 0, 'colRange':(-25, 35), 'freq':9.4},
          'Ze_Ka':{'offset': 0, 'colRange':(-25, 35), 'freq':35.5},
          'Ze_W':{'offset': 0, 'colRange':(-25, 35), 'freq':95}}
varNames = variable.keys()
#-----------------------------

#--Attenuation correction-----
results, time, height_M = attLib.getAtmAttPantra(cloudNetFilePath, radarFreqs)

interpAttDataList, qualityFlagList = \
   attLib.getInterpQualFlagList(results, time, timeRef, 
                                timeTolerance, height_M,
                                rangeRef, rangeTolerance, 
                                radarFreqs, year, month, day)

interpAttDataList = attLib.changeAttListOrder(interpAttDataList, variable, radarFreqs)
qualityFlagList = attLib.changeAttListOrder(qualityFlagList, variable, radarFreqs)
#-----------------------------

#--Offset correction----------
dataFrameList, epoch = offLib.getDataFrameList(fileList, variable.keys())

#Attenuation correction
dataFrameListAtt = attLib.applyAttCorr(dataFrameList*1, interpAttDataList, variable)

#offset 
dataFrameListMasked = attLib.applyAttCorr(dataFrameList*1, interpAttDataList, 
					  variable)
dataFrameListMasked = offLib.getMaskedDF(dataFrameListMasked, variable, 
                                         Ze_KaMax, Ze_KaMin, heightThreshold)
   
timeWindow = pd.to_timedelta( timeWindowLenght, unit='m')
timesBegin = pd.date_range(start, end, freq='1min')
timesEnd = pd.date_range(start+timeWindow, end+timeWindow, freq='1min')

dataFrame = dataFrameListMasked[variable.keys().index('Ze_X')]
dataFrameRef = dataFrameListMasked[variable.keys().index('Ze_Ka')]
parametersXKa= offLib.getOffset(dataFrame, dataFrameRef,
                                timesBegin, timesEnd)
    
dataFrame = dataFrameListMasked[variable.keys().index('Ze_W')]
dataFrameRef = dataFrameListMasked[variable.keys().index('Ze_Ka')]
parametersWKa= offLib.getOffset(dataFrame, dataFrameRef,
                                timesBegin, timesEnd)

parametersXKaTS = offLib.getParameterTimeSerie(parametersXKa, timeFreq)
parametersWKaTS = offLib.getParameterTimeSerie(parametersWKa, timeFreq)

###(I mutipled the offset by -1 )
offsetWKaDF = offLib.getParamDF(parametersWKaTS[0]*1, timeRef, rangeRef)
validPointWKaDF = offLib.getParamDF(parametersWKaTS[2]*1, timeRef, rangeRef)
offsetWKaDF = offsetWKaDF*(-1)
dataFrameListAtt[varNames.index('Ze_W')] = \
   offLib.applyOffsetCorr(dataFrameListAtt[varNames.index('Ze_W')],
                          offsetWKaDF*1, validPointWKaDF, 
                          thresholdPoints)

offsetXKaDF = offLib.getParamDF(parametersXKaTS[0]*1, timeRef, rangeRef)
validPointXKaDF = offLib.getParamDF(parametersXKaTS[2]*1, timeRef, rangeRef)
offsetXKaDF = offsetXKaDF*(-1)
dataFrameListAtt[varNames.index('Ze_X')] = \
   offLib.applyOffsetCorr(dataFrameListAtt[varNames.index('Ze_X')],
                          offsetXKaDF*1, validPointXKaDF, 
                          thresholdPoints)

#-----------------------------

#--Write data-----------------
timeWindowWrite = pd.to_timedelta(3599, unit='s')
timesBeginWrite = pd.date_range(start, end, freq='60min')
timesEndWrite = pd.date_range(start+timeWindowWrite, 
                              end+timeWindowWrite,
                              freq='60min')

variableOutPut={'Ze_X':{'data':dataFrameListAtt[varNames.index('Ze_X')]},
                'Ze_Ka':{'data':dataFrameListAtt[varNames.index('Ze_Ka')]},
                'Ze_W':{'data':dataFrameListAtt[varNames.index('Ze_W')]},
                'Attenuation_X':{'data':interpAttDataList[varNames.index('Ze_X')]},
                'Attenuation_Ka':{'data':interpAttDataList[varNames.index('Ze_Ka')]},
                'Attenuation_W':{'data':interpAttDataList[varNames.index('Ze_W')]},
                'Offset_X':{'data':offsetXKaDF},
                'Offset_W':{'data':offsetWKaDF},
                'ValidData_X':{'data':validPointXKaDF},
                'ValidData_Ka':{'data':validPointWKaDF},
               }

for indexWrite, timeStart in enumerate(timesBeginWrite):
    
    timeEnd = timesEndWrite[indexWrite]
    dateName = timeStart.strftime('%Y%m%d_%H')
    
    outPutFile = ('_').join([prefixL2, dateName+'.nc'])
    outPutFilePath = ('/').join([outputPath, outPutFile])
    
    timeRefWrt = dataFrameList[0][timeStart:timeEnd].index
    timeRefUnixWrt = np.array(timeRefWrt, float)
    timeRefUnixWrt = timeRefUnixWrt/10.**9
    
    rootgrpOut = writeData.createNetCdf(outPutFilePath, prefixL2)
    time_ref = writeData.createTimeDimension(rootgrpOut, timeRefUnixWrt, prefixL2)
    range_ref = writeData.createRangeDimension(rootgrpOut, rangeRef, prefixL2)
    
    for varNameOut in variableOutPut.keys():

        varFinalName, radar=varNameOut.split('_')
        dataDF = variableOutPut[varNameOut]['data']
        dataToWrite = np.array(dataDF[timeStart:timeEnd].astype(np.float32))
        var_Written = writeData.createVariable(rootgrpOut, dataToWrite,
                                               varFinalName, varNameOut,
                                               radar, prefixL2)
    
rootgrpOut.close()


#-----------------------------




