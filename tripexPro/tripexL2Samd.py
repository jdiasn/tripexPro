import glob
import numpy as np
import pandas as pd
from sys import argv

import writeData
import externalData as extLib
import offsetLib as offLib
import attenuationLib as attLib
import filters as filt
import qualityFlag as qFlag 

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

hatproPath = argv[22]
hatproFileID = argv[23]

#--Files to work--------------- 
cloudNetFile = ('_').join([year+month+day,cloudNetFileID])
cloudNetFilePath = ('/').join([cloudNetPath, year, cloudNetFile])

hatproFile = ('_').join([hatproFileID, year+month+day+'*.nc'])
hatproFilePath = ('/').join([hatproPath, year[2:]+month, hatproFile])
hatproFileName = glob.glob(hatproFilePath)[0]

#print cloudNetFilePath

fileDate = ('').join([year, month, day])
print ('/').join([dataPathRe,fileId+'_'+fileDate+'*.nc'])
fileList = glob.glob(('/').join([dataPathRe,fileId+'_'+fileDate+'*.nc']))
fileList = sorted(fileList)
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

#print 'temp'
#print tempCel[0]
#print 'press'
#print press[0]
#print 'hum'
#print relHum[0]


resampledTemp = attLib.getResampledTimeRange(rangeRef, rangeTolerance, timeRef,
                                             time, timeTolerance, tempCel, year,
                                             month, day, height_M)

interpTemp, qualityFlagTemp = attLib.getInterpData(time, timeRef, height_M,
                                                   resampledTemp, tempCel,
                                                   rangeRef)

interpTempDF = pd.DataFrame(index=timeRef, columns=rangeRef, 
                            data=interpTemp.T)

#-----------------------------

#print interpTempDF[100]

#--Copy press from CLOUDNET----
resampledPress = attLib.getResampledTimeRange(rangeRef, rangeTolerance, timeRef,
                                              time, timeTolerance, press, year,
                                              month, day, height_M)

interpPress, qualityFlagPress = attLib.getInterpData(time, timeRef, height_M,
                                                    resampledPress, press,
                                                    rangeRef)

interpPressDF = pd.DataFrame(index=timeRef, columns=rangeRef, 
                             data=interpPress.T)

#-----------------------------

#print interpPressDF[100]

#--Copy relHum from CLOUDNET----
resampledRelHum = attLib.getResampledTimeRange(rangeRef, rangeTolerance, timeRef,
                                               time, timeTolerance, relHum, year,
                                               month, day, height_M)

interpRelHum, qualityFlagRelHum = attLib.getInterpData(time, timeRef, height_M,
                                                       resampledRelHum, relHum,
                                                       rangeRef)

interpRelHumDF = pd.DataFrame(index=timeRef, columns=rangeRef, 
                              data=interpRelHum.T)

#-----------------------------
#print interpRelHumDF[100]


#--Offset correction----------
dataFrameList, epoch = offLib.getDataFrameList(fileList, variable)
#dataFrameListNoCorrec, epoch = offLib.getDataFrameList(fileList, variable)


#it removes extreme values from reflectively velocity 
dataFrameList = filt.removeOutliersZeKa(dataFrameList, variable)
#it removes the clutter from X band
dataFrameList = filt.removeClutter(dataFrameList, variable, 'Ze_X', 700)
#it removes the clutter from Ka band
dataFrameList = filt.removeClutter(dataFrameList, variable, 'Ze_Ka', 400)
#it removes the clutter from W band
dataFrameList = filt.removeClutter(dataFrameList, variable, 'Ze_W', 370)


shiftedTempDF = interpTempDF.copy()
shiftedTempDF = offLib.getShiftedTemp(shiftedTempDF, timeRef, rangeRef)


#Attenuation correction
dataFrameListAtt = attLib.applyAttCorr(dataFrameList*1, interpAttDataList, variable)

#offset 
dataFrameListMasked = attLib.applyAttCorr(dataFrameList*1, interpAttDataList, 
					  variable)
  
timeWindow = pd.to_timedelta( timeWindowLenght, unit='m')
timesBegin = pd.date_range(start-timeWindow, end-timeWindow, freq='1min')
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

###(I mutipled the offset by -1 ) ( ## testing the offset)
percentDfWKa = offLib.getParamDF(parametersWKaTS[5]*1, timeRef, rangeRef)
offsetWKaDF = offLib.getParamDF(parametersWKaTS[0]*1, timeRef, rangeRef)
validPointWKaDF = offLib.getParamDF(parametersWKaTS[2]*1, timeRef, rangeRef)
correlXKaDF = offLib.getParamDF(parametersXKaTS[4]*1, timeRef, rangeRef)

offsetWKaDF = offsetWKaDF*(-1)
dataFrameListAtt[varNames.index('Ze_W')] = \
   offLib.applyOffsetCorr(dataFrameListAtt[varNames.index('Ze_W')],
                          offsetWKaDF*1, validPointWKaDF, 
                          thresholdPoints)

percentDfXKa = offLib.getParamDF(parametersXKaTS[5]*1, timeRef, rangeRef)
offsetXKaDF = offLib.getParamDF(parametersXKaTS[0]*1, timeRef, rangeRef)
validPointXKaDF = offLib.getParamDF(parametersXKaTS[2]*1, timeRef, rangeRef)
correlWKaDF = offLib.getParamDF(parametersWKaTS[4]*1, timeRef, rangeRef)

offsetXKaDF = offsetXKaDF*(-1)
dataFrameListAtt[varNames.index('Ze_X')] = \
   offLib.applyOffsetCorr(dataFrameListAtt[varNames.index('Ze_X')],
                          offsetXKaDF*1, validPointXKaDF, 
                          thresholdPoints)

#-----------------------------

#the sensitivity filter was deactivated after because it 
#the quality flags gives a better result 
# ---> replace the ln equation to log10 equation and coefficients 
#Sensitivity threshold--------
#sensParam = {'x':{'a':2.20442085e+01, 'b':6.68034993e-05},
#	     'ka':{'a':2.05036407e+01, 'b':3.02177078e-06},
#             'w':{'a':1.53829088e+01, 'b':1.25574808e-06},
#	    }

#sensParam = {'x':{'a':2.19838341e+01, 'b':7.13026702e-05},
#             'ka':{'a':2.05355423e+01, 'b':3.25989869e-06},
#             'w':{'a':1.53829088e+01, 'b':1.25574808e-06},
#            }

#or dataFrameListAtt it should be att
#dataFrameListAtt = filt.sensitivityFilter(dataFrameListAtt, variable,
#                                       'Ze_X', sensParam['x'])
#
#dataFrameListAtt = filt.sensitivityFilter(dataFrameListAtt, variable,
#                                       'Ze_Ka', sensParam['ka'])
#
#dataFrameListAtt = filt.sensitivityFilter(dataFrameListAtt, variable,
#                                       'Ze_W', sensParam['w'])
#-----------------------------





#--Quality Flags--------------

rainFlag = qFlag.getRainFlag(cloudNetFilePath, timeRef, 'rainFlag',
                             year, month, day)
rainFlagDF = offLib.getParamDF(rainFlag['rainFlag'], timeRef, rangeRef)

lwpFlag = qFlag.getLwpFlag(hatproFileName, timeRef, 'lwpFlag',
                           year, month, day)
lwpFlagDF = offLib.getParamDF(lwpFlag['lwpFlag'], timeRef, rangeRef)



#offset flag X band
valPoinFlagXKaDF = qFlag.getFlag(validPointXKaDF, 300)
corrFlagXKaDF = qFlag.getFlag(correlXKaDF, 0.70)

varFlagXKaDF = qFlag.getVarianceFlag(dataFrameListAtt[varNames.index('Ze_X')],
                                    dataFrameListAtt[varNames.index('Ze_Ka')])

finalFlagXKa = qFlag.getUnifiedFlag(rainFlagDF, lwpFlagDF,
                                    corrFlagXKaDF, valPoinFlagXKaDF)

finalFlagXKaDF = offLib.getParamDF(finalFlagXKa['flag'], timeRef, rangeRef) 
finalFlagXKaDF = finalFlagXKaDF + varFlagXKaDF


#offset flag W band
valPoinFlagWKaDF = qFlag.getFlag(validPointWKaDF, 300)
corrFlagWKaDF = qFlag.getFlag(correlWKaDF, 0.70)

varFlagKaWDF = qFlag.getVarianceFlag(dataFrameListAtt[varNames.index('Ze_Ka')],
                                    dataFrameListAtt[varNames.index('Ze_W')])

finalFlagWKa = qFlag.getUnifiedFlag(rainFlagDF, lwpFlagDF,
                                    corrFlagWKaDF, valPoinFlagWKaDF)

finalFlagWKaDF = offLib.getParamDF(finalFlagWKa['flag'], timeRef, rangeRef)
finalFlagWKaDF = finalFlagWKaDF + varFlagKaWDF
#-----------------------------



#--radar definitions --------

coordenates = {'lat':{'data':50.9086},
	      'lon':{'data':6.4135},
	      'zsl':{'data':112.5}
}



externalData = {'freq_sb_x':{'data':np.array(9.4*10**9,np.float32)},
		'freq_sb_ka':{'data':np.array(35.5*10**9,np.float32)},
		'freq_sb_w':{'data':np.array(94*10**9,np.float32)},
		'radar_beam_width_x':{'data':np.array(1.3,np.float32)},
		'radar_beam_width_ka':{'data':np.array(0.6,np.float32)},
		'radar_beam_width_w':{'data':np.array(0.5,np.float32)},
}


#pd.to_timedelta(2,)


bnds = {'time_bnds':{'data': offLib.getTimeBnds(timeRef, timeTolerance)},
        'range_bnds':{'data':offLib.getRangeBnds(rangeRef, rangeTolerance)}
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
                'LDRg_Ka':{'data':data, 'offset':0, 'outName':'ldr_ka'},
		#'KDP_X':{'data':data, 'offset':0, 'outName':'kdp_x'},
		'PhiDP_X':{'data':data, 'offset':0, 'outName':'phidp_x'},
		'RhoHV_X':{'data':data, 'offset':0, 'outName':'rhohv_x'},
		'ZDR_X':{'data':data, 'offset':0, 'outName':'zdr_x'},
 		 }

dataCopiedDFList, epoch = offLib.getDataFrameList(fileList, 
                                                  variableToCopy)
print epoch	
#it removes the clutter from X band
dataFrameList = filt.removeClutter(dataCopiedDFList, variableToCopy, 'v_X', 700)
dataFrameList = filt.removeClutter(dataCopiedDFList, variableToCopy, 'SW_X', 700)

#dataFrameList = filt.removeClutter(dataCopiedDFList, variableToCopy, 'KDP_X', 700)
dataFrameList = filt.removeClutter(dataCopiedDFList, variableToCopy, 'PhiDP_X', 700)
dataFrameList = filt.removeClutter(dataCopiedDFList, variableToCopy, 'RhoHV_X', 700)
dataFrameList = filt.removeClutter(dataCopiedDFList, variableToCopy, 'ZDR_X', 700)

#it removes the clutter from Ka band
dataFrameList = filt.removeClutter(dataCopiedDFList, variableToCopy, 'v_Ka', 400)
dataFrameList = filt.removeClutter(dataCopiedDFList, variableToCopy, 'SW_Ka', 400)
dataFrameList = filt.removeClutter(dataCopiedDFList, variableToCopy, 'LDRg_Ka', 400)


#it removes the clutter from W band
dataFrameList = filt.removeClutter(dataCopiedDFList, variableToCopy, 'v_W', 370)
dataFrameList = filt.removeClutter(dataCopiedDFList, variableToCopy, 'SW_W', 370)


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

#from IPython.core.debugger import Tracer ; Tracer()()
#--Write data-----------------

variableOutPut={'dbz_x':{'data':dataFrameListAtt[varNames.index('Ze_X')]},
                'dbz_ka':{'data':dataFrameListAtt[varNames.index('Ze_Ka')]},
                'dbz_w':{'data':dataFrameListAtt[varNames.index('Ze_W')]},
                'pia_x':{'data':interpAttDataList[varNames.index('Ze_X')]},
                'pia_ka':{'data':interpAttDataList[varNames.index('Ze_Ka')]},
                'pia_w':{'data':interpAttDataList[varNames.index('Ze_W')]},
                'offset_x':{'data':offsetXKaDF},
                'offset_w':{'data':offsetWKaDF},
               # 'valDat_x':{'data':validPointXKaDF},
               # 'valDat_w':{'data':validPointWKaDF},
               # 'correlation_X':{'data':correlXKaDF},
               # 'correlation_W':{'data':correlWKaDF},
               # 'corrFlag_x':{'data':corrFlagXKaDF},
               # 'pointFlag_x':{'data':valPoinFlagXKaDF},
               # 'corrFlag_w':{'data':corrFlagWKaDF},
               # 'pointFlag_w':{'data':valPoinFlagWKaDF},
	       # 'rainFlag_x':{'data':rainFlagDF},
	       # 'lwpFlag_x':{'data':lwpFlagDF},
	        'pa':{'data':interpPressDF},	
                'hur':{'data':interpRelHumDF},
 	        'ta':{'data':interpTempDF},
		'quality_flag_offset_x':{'data':finalFlagXKaDF},
		'quality_flag_offset_w':{'data':finalFlagWKaDF},
              }

#for indexWrite, timeStart in enumerate(timesBeginWrite):
        
dateName = start.strftime('%Y%m%d')
    
outPutFile = ('_').join([prefixL2, dateName+'000000.nc'])
outPutFilePath = ('/').join([outputPath, outPutFile])
    
timeRefUnixWrt = np.array(timeRef, float)
timeRefUnixWrt = timeRefUnixWrt/10.**9
  
rootgrpOut = writeData.createNetCdf(outPutFilePath, prefixL2)


for varNameOut in sorted(coordenates.keys()):

    varListName = varNameOut.split('_')
    if len(varListName) > 1:
	    varFinalName = '_'.join(varListName[:-1])
            sensor = varListName[-1]
    else:
	varFinalName = varListName[0]
        sensor = ''        
    dataDF = coordenates[varNameOut]['data']
    dataToWrite = np.array(dataDF)
    var_Written = writeData.createOneValvariable(rootgrpOut, dataToWrite,
                                                varFinalName, sensor, prefixL2)

#for varNameOut in sorted(bnds.keys()):
	
#    dimName, varName = varNameOut.split('_')
#    dataToWrite = bnds[varNameOut]['data']
#    var_Written = writeData.createBndsVariable(rootgrpOut, dataToWrite,
#                                               varNameOut, dimName)
 
nv_dim = writeData.createNvDimension(rootgrpOut, prefixL2)
 
time_ref = writeData.createTimeDimension(rootgrpOut, timeRefUnixWrt, prefixL2)
dataToWrite = bnds['time_bnds']['data']
var_Written = writeData.createBndsVariable(rootgrpOut, dataToWrite,
                                           'time_bnds', 'time')
 
range_ref = writeData.createRangeDimension(rootgrpOut, rangeRef, prefixL2)
dataToWrite = bnds['range_bnds']['data']
var_Written = writeData.createBndsVariable(rootgrpOut, dataToWrite,
                                           'range_bnds', 'range')


for varNameOut in sorted(variableOutPut.keys()):

    varListName = varNameOut.split('_')
    if len(varListName) > 1:
	varFinalName = '_'.join(varListName[:-1])
        radar = varListName[-1]

    else:
	varFinalName = varListName[0]
        radar = ''        
 
    dataDF = variableOutPut[varNameOut]['data']

    if varFinalName == 'quality_flag_offset':
	dataToWrite = np.array(dataDF.astype(np.uint16))
        var_Written = writeData.createVariable(rootgrpOut, dataToWrite,
                                               varFinalName, varNameOut,
                                               radar, prefixL2, np.uint16)

    else:
        dataToWrite = np.array(dataDF.astype(np.float32))
        var_Written = writeData.createVariable(rootgrpOut, dataToWrite,
                                               varFinalName, varNameOut,
                                               radar, prefixL2, np.float32)

#It writes the data from L1 in L2 file
for varNameOut in sorted(variableToCopy.keys()):

    #it removes the noise from v_Ka
    if varNameOut == 'rv_ka':
            
        #indexV_Ka = variableToCopy.keys().index('rv_ka')
        #indexZe_Ka = varNames.index('Ze_Ka')    
        variableToCopy['rv_ka']['data'] = \
                filt.removeVelNoiseKa(variableOutPut['dbz_ka']['data'],
                                      variableToCopy['rv_ka']['data'])

    elif (varNameOut == 'kdp_x') or (varNameOut == 'phidp_x')\
        or (varNameOut == 'rhohv_x') or (varNameOut == 'zdr_x'):

        variableToCopy[varNameOut]['data'] = \
                filt.removeVelNoiseKa(variableToCopy['rv_x']['data'],
                                      variableToCopy[varNameOut]['data'])
                #filt.removeVelNoiseKa(variableOutPut['rv_x']['data'],
                 #                     variableToCopy[varNameOut]['data'])



    else:
        pass
    #-------------------------------       


    varFinalName, radar=varNameOut.split('_')        
    dataDF = variableToCopy[varNameOut]['data'] 
    dataToWrite = np.array(dataDF.astype(np.float32))
    var_Written = writeData.createVariable(rootgrpOut, dataToWrite,
                                               varFinalName, varNameOut,
                                               radar, prefixL2, np.float32)
        

for varNameOut in sorted(externalData.keys()):

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

 

rootgrpOut.close()


#-----------------------------




