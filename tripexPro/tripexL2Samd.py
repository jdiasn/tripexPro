import glob
import numpy as np
import pandas as pd
from sys import argv

import writeData
import externalData as extLib
import offsetLib as offLib
import attenuationLib as attLib
import filters as filt 

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
#Ze_KaMax = int(argv[16]) #[dBZ]
#Ze_KaMin = int(argv[17]) #[dBZ]
heightThreshold = int(argv[18]) #[m]
timeWindowLenght = int(argv[19]) #[min]
thresholdPoints = int(argv[20]) #[Threshold of Points]
zeOffsetKa = float(argv[21])
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
          'Ze_Ka':{'offset': zeOffsetKa, 'colRange':(-25, 35), 'freq':35.5},
          'Ze_W':{'offset': 0, 'colRange':(-25, 35), 'freq':95}}
varNames = variable.keys()
#-----------------------------

#--Attenuation correction-----
results, time, height_M, temp, relHum, press = \
   attLib.getAtmAttPantra(cloudNetFilePath, radarFreqs)

interpAttDataList, qualityFlagList = \
   attLib.getInterpQualFlagList(results, time, timeRef, 
                                timeTolerance, height_M,
                                rangeRef, rangeTolerance, 
                                radarFreqs, year, month, day)

interpAttDataList = attLib.changeAttListOrder(interpAttDataList,
                                              variable, radarFreqs)
qualityFlagList = attLib.changeAttListOrder(qualityFlagList, 
                                            variable, radarFreqs)
#-----------------------------


#--Copy temp from CLOUDNET----
tempCel = temp - 273.15
resampledTemp = attLib.getResampledTimeRange(rangeRef, rangeTolerance, timeRef,
                                             time, timeTolerance, tempCel, year,
                                             month, day, height_M)

interpTemp, qualityFlagTemp = attLib.getInterpData(time, timeRef, height_M,
                                                   resampledTemp, tempCel,
                                                   rangeRef)

interpTempDF = pd.DataFrame(index=timeRef, columns=rangeRef, 
                            data=interpTemp.T)

#-----------------------------



#--Offset correction----------
dataFrameList, epoch = offLib.getDataFrameList(fileList, variable)
#--it removes extreme values from Doppler velocity 
dataFrameList = filt.removeOutliersZeKa(dataFrameList, variable)
#--it removes the clutter from X band
dataFrameList = filt.removeClutter(dataFrameList, variable, 'Ze_X', 700)
#--it removes the clutter from Ka band
dataFrameList = filt.removeClutter(dataFrameList, variable, 'Ze_Ka', 400)


shiftedTempDF = interpTempDF*1
shiftedTempDF = offLib.getShiftedTemp(shiftedTempDF, timeRef, rangeRef)

#Attenuation correction
dataFrameListAtt = attLib.applyAttCorr(dataFrameList*1, interpAttDataList, variable)

#offset 
dataFrameListMasked = attLib.applyAttCorr(dataFrameList*1, interpAttDataList, 
					  variable)
  
timeWindow = pd.to_timedelta( timeWindowLenght, unit='m')
timesBegin = pd.date_range(start, end, freq='1min')
timesEnd = pd.date_range(start+timeWindow, end+timeWindow, freq='1min')

#offset X Ka
offsetPairXKa = ['Ze_X','Ze_Ka']
dataFrameListToXKa = attLib.applyAttCorr(dataFrameList*1, interpAttDataList, 
					  variable)

dataFrameListMaskedXKa = offLib.getMaskedDF(dataFrameListToXKa, variable, 
                                            0, -15, heightThreshold,
                                            offsetPairXKa)

maskedTempDFlistXKa = offLib.temperatureMask(shiftedTempDF,
					     dataFrameListMaskedXKa, 
                                             offsetPairXKa, timeRef,
                                             rangeRef)

dataFrame = maskedTempDFlistXKa[offsetPairXKa.index('Ze_X')]
dataFrameRef = maskedTempDFlistXKa[offsetPairXKa.index('Ze_Ka')]
parametersXKa= offLib.getOffset(dataFrame, dataFrameRef,
                                timesBegin, timesEnd, 
				'Ka', 'X')


#offset Ka W
offsetPairKaW = ['Ze_Ka','Ze_W']
dataFrameListToKaW = attLib.applyAttCorr(dataFrameList*1, interpAttDataList, 
					  variable)

dataFrameListMaskedKaW = offLib.getMaskedDF(dataFrameListToKaW, variable, 
                                            -10, -30, heightThreshold,
                                            offsetPairKaW)

maskedTempDFlistKaW = offLib.temperatureMask(shiftedTempDF,
                                             dataFrameListMaskedKaW, 
                                             offsetPairKaW, timeRef,
                                             rangeRef)
 
dataFrame = maskedTempDFlistKaW[offsetPairKaW.index('Ze_W')]
dataFrameRef = maskedTempDFlistKaW[offsetPairKaW.index('Ze_Ka')]
parametersWKa= offLib.getOffset(dataFrame, dataFrameRef,
                                timesBegin, timesEnd,
                                'Ka', 'W')

parametersXKaTS = offLib.getParameterTimeSerie(parametersXKa, timeFreq)
parametersWKaTS = offLib.getParameterTimeSerie(parametersWKa, timeFreq)

###(I mutipled the offset by -1 )
offsetWKaDF = offLib.getParamDF(parametersWKaTS[0]*1, timeRef, rangeRef)
validPointWKaDF = offLib.getParamDF(parametersWKaTS[2]*1, timeRef, rangeRef)
correlXKaDF = offLib.getParamDF(parametersXKaTS[4]*1, timeRef, rangeRef)

offsetWKaDF = offsetWKaDF*(-1)
dataFrameListAtt[varNames.index('Ze_W')] = \
   offLib.applyOffsetCorr(dataFrameListAtt[varNames.index('Ze_W')],
                          offsetWKaDF*1, validPointWKaDF, 
                          thresholdPoints)

offsetXKaDF = offLib.getParamDF(parametersXKaTS[0]*1, timeRef, rangeRef)
validPointXKaDF = offLib.getParamDF(parametersXKaTS[2]*1, timeRef, rangeRef)
correlWKaDF = offLib.getParamDF(parametersWKaTS[4]*1, timeRef, rangeRef)
offsetXKaDF = offsetXKaDF*(-1)
dataFrameListAtt[varNames.index('Ze_X')] = \
   offLib.applyOffsetCorr(dataFrameListAtt[varNames.index('Ze_X')],
                          offsetXKaDF*1, validPointXKaDF, 
                          thresholdPoints)

#-----------------------------



#--Copy press from CLOUDNET----
resampledPress = attLib.getResampledTimeRange(rangeRef, rangeTolerance, timeRef,
                                              time, timeTolerance, press, year,
                                              month, day, height_M)

interpPress, qualityFlagPress = attLib.getInterpData(time, timeRef, height_M,
                                                    resampledPress, tempCel,
                                                    rangeRef)

interpPressDF = pd.DataFrame(index=timeRef, columns=rangeRef, 
                             data=interpPress.T)

#-----------------------------


#--Copy relHum from CLOUDNET----
resampledRelHum = attLib.getResampledTimeRange(rangeRef, rangeTolerance, timeRef,
                                               time, timeTolerance, relHum, year,
                                               month, day, height_M)

interpRelHum, qualityFlagRelHum = attLib.getInterpData(time, timeRef, height_M,
                                                       resampledPress, relHum,
                                                       rangeRef)

interpRelHumDF = pd.DataFrame(index=timeRef, columns=rangeRef, 
                              data=interpRelHum.T)

#-----------------------------


#--radar definitions --------

externalData = {'freq_sb_x':{'data':np.array(9.4*10**9,np.float32)},
		'freq_sb_ka':{'data':np.array(35.5*10**9,np.float32)},
		'freq_sb_w':{'data':np.array(94*10**9,np.float32)},
		'radar_beam_width_x':{'data':np.array(1.3,np.float32)},
		'radar_beam_width_ka':{'data':np.array(0.6,np.float32)},
		'radar_beam_width_w':{'data':np.array(0.5,np.float32)},
		'lat':{'data':50.9086},
		'lon':{'data':6.4135},
		'zsl':{'data':112.5}
}


bnds = {'time_bnds':{'data':np.ones((len(timeRef), 2))*\
		     np.array([np.float(timeTolerance[:-1])*(-1),
                               np.float(timeTolerance[:-1])])},
        'range_bnds':{'data':np.ones((len(rangeRef),2))*\
                      np.array([np.float(rangeTolerance)*(-1), 
                                np.float(rangeTolerance)])}

}

#-----------------------------


#--Copy data from L1----------
data = None
variableToCopy={'v_X':{'data':data, 'offset':0, 'outName':'rv_x'},
                'v_Ka':{'data':data, 'offset':0, 'outName':'rv_ka'},
                'v_W':{'data':data, 'offset':0, 'outName':'rv_w'},
                'SW_X':{'data':data, 'offset':0, 'outName':'sw_x'},
                'SW_Ka':{'data':data, 'offset':0, 'outName':'sw_ka'},
                'SW_W':{'data':data, 'offset':0, 'outName':'sw_w'},
                'LDR_Ka':{'data':data, 'offset':0, 'outName':'ldr_ka'},
                }

dataCopiedDFList, epoch = offLib.getDataFrameList(fileList, 
                                                  variableToCopy)

variableToCopyTemp={}
for variable in variableToCopy.keys():

    outName = variableToCopy[variable]['outName']
    variableToCopyTemp[outName]={'data':data}

for variable in variableToCopy.keys():
    
    varNamesToCopy = variableToCopy.keys()
    outName = variableToCopy[variable]['outName']
    variableToCopyTemp[outName]['data'] = \
   	 dataCopiedDFList[varNamesToCopy.index(variable)]

variableToCopy = variableToCopyTemp

#-----------------------------


#--Write data-----------------

variableOutPut={'dbz_x':{'data':dataFrameListAtt[varNames.index('Ze_X')]},
                'dbz_ka':{'data':dataFrameListAtt[varNames.index('Ze_Ka')]},
                'dbz_w':{'data':dataFrameListAtt[varNames.index('Ze_W')]},
                'pia_x':{'data':interpAttDataList[varNames.index('Ze_X')]},
                'pia_ka':{'data':interpAttDataList[varNames.index('Ze_Ka')]},
                'pia_w':{'data':interpAttDataList[varNames.index('Ze_W')]},
                'offset_x':{'data':offsetXKaDF},
                'offset_w':{'data':offsetWKaDF},
              }

#for indexWrite, timeStart in enumerate(timesBeginWrite):
        
dateName = start.strftime('%Y%m%d')
    
outPutFile = ('_').join([prefixL2, dateName+'.nc'])
outPutFilePath = ('/').join([outputPath, outPutFile])
    
timeRefWrt = dataFrameList[0].index
timeRefUnixWrt = np.array(timeRefWrt, float)
timeRefUnixWrt = timeRefUnixWrt/10.**9
  
rootgrpOut = writeData.createNetCdf(outPutFilePath, prefixL2)
time_ref = writeData.createTimeDimension(rootgrpOut, timeRefUnixWrt, prefixL2)
range_ref = writeData.createRangeDimension(rootgrpOut, rangeRef, prefixL2)
nv_dim = writeData.createNvDimension(rootgrpOut, prefixL2)
    
for varNameOut in variableOutPut.keys():

    varFinalName, radar=varNameOut.split('_')
    dataDF = variableOutPut[varNameOut]['data']
    dataToWrite = np.array(dataDF.astype(np.float32))
    var_Written = writeData.createVariable(rootgrpOut, dataToWrite,
                                           varFinalName, varNameOut,
                                           radar, prefixL2)

#It writes the data from L1 in L2 file
for varNameOut in variableToCopy.keys():

    #it removes the noise from v_Ka
    if varNameOut == 'v_Ka':
            
        indexV_Ka = variableToCopy.keys().index('v_Ka')
        indexZe_Ka = varNames.index('Ze_Ka')    
        variableToCopy['v_ka']['data'] = \
                filt.removeVelNoiseKa(dataFrameListAtt[indexZe_Ka],
                                      dataCopiedDFList[indexV_Ka])
    #-------------------------------       


    varFinalName, radar=varNameOut.split('_')        
    dataDF = variableToCopy[varNameOut]['data']
    dataToWrite = np.array(dataDF.astype(np.float32))
    var_Written = writeData.createVariable(rootgrpOut, dataToWrite,
                                           varFinalName, varNameOut,
                                           radar, prefixL2)
        

for varNameOut in externalData.keys():

    varListName = varNameOut.split('_')
    if len(varListName) > 1:
	    varFinalName = '_'.join(varListName[:-1])
            sensor = varListName[-1]
    else:
	varFinalName = varListName[0]
        sensor = ''        
    dataDF = externalData[varNameOut]['data']
    dataToWrite = np.array(dataDF)
    var_Written = writeData.createOneValvariable(rootgrpOut, dataToWrite,
                                                varFinalName, sensor, prefixL2)

for varNameOut in bnds.keys():
	
    dimName, varName = varNameOut.split('_')
    dataToWrite = bnds[varNameOut]['data']
    var_Written = writeData.createBndsVariable(rootgrpOut, dataToWrite,
                                               varNameOut, dimName)
 

rootgrpOut.close()


#-----------------------------




