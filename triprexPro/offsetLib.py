import numpy as np
from netCDF4 import Dataset
import pandas as pd
import tripexLib as trLib
import glob


def getDataFrameList(fileList, variableDic):

    dataFrameList = []

    varNames = variableDic.keys()
    for i, variable in enumerate(varNames):
        dataFrameList.append(pd.DataFrame())

    for fileName in fileList:
    
    #print fileName 
        rootgrpRe = Dataset(fileName, 'r')
        times = rootgrpRe.variables['time'][:]
        ranges = rootgrpRe.variables['altitude'][:]
    
        epoch = trLib.getEpochTime(rootgrpRe, 'X')
        times = epoch+pd.to_timedelta(times, unit='s')
    
        for i, variable in enumerate(varNames):
    
            try:
                data = rootgrpRe.variables[variable][:]
	        data = data + variableDic[variable]['offset']               

            except:
                if variable == 'halt':
                    data = np.ones((len(times), len(ranges)))*ranges
                else:
                    data = np.ones((len(times), len(ranges)))*np.nan
               
            dataFrame = pd.DataFrame(data=data, columns=ranges, index=times)
            dataFrameList[i] = dataFrameList[i].append(dataFrame)
        
        rootgrpRe.close()

    for i, variable in enumerate(varNames):
        dataFrameList[i]['times']=dataFrameList[i].index
        dataFrameList[i]=dataFrameList[i].drop_duplicates(subset='times')
        del dataFrameList[i]['times']
    
    return dataFrameList, epoch


def getMaskedDF(dataFrameList, variable,
                ZeKaMax, ZeKaMin, heightMin,
                offsetPair):

    varNames = variable.keys()
    kaIndex = varNames.index('Ze_Ka')
    kaThresholdMax = dataFrameList[kaIndex]>=ZeKaMax
    kaThresholdMin = dataFrameList[kaIndex]<=ZeKaMin
    
    cloudKa = dataFrameList[kaIndex]/dataFrameList[kaIndex]

    for varNameCorr in offsetPair:
        
        varIndex = varNames.index(varNameCorr)
	
        dataFrameList[varIndex][cloudKa!=1]=np.nan
#        dataFrameList[varIndex].loc[:,dataFrameList[varIndex].columns 
#                                    < heightMin]=np.nan
        dataFrameList[varIndex][kaThresholdMax]=np.nan
        dataFrameList[varIndex][kaThresholdMin]=np.nan
        
    var0 = varNames.index(offsetPair[0])
    var1 = varNames.index(offsetPair[1])

    return dataFrameList[var0], dataFrameList[var1]


def getOffset(dataFrame, dataFrameRef,
              timesBegin, timesEnd):
    
    offSetAr = np.zeros(1440) + np.nan
    stdDiffAr = np.zeros(1440) + np.nan
    validPointsAr = np.zeros(1440) + np.nan
    stdZe_RefAr = np.zeros(1440) + np.nan

    for i in range(len(timesBegin)):
        newStart = timesBegin[i]
        newEnd = timesEnd[i]

        Ze_Rad = dataFrame[newStart:newEnd]
        Ze_Ref = dataFrameRef[newStart:newEnd]

        Ze_Rad = np.ma.masked_invalid(Ze_Rad)
        Ze_Ref = np.ma.masked_invalid(Ze_Ref)    
        Ze_Diff = Ze_Rad - Ze_Ref
 
        offset = np.mean(Ze_Diff)
        stdDiff = np.std(Ze_Diff)
        stdZe_Ref = np.std(Ze_Ref)
   
        if offset is np.ma.masked:
       		 offset = np.nan
        if stdDiff is np.ma.masked:
	         stdDiff = np.nan    
        if stdZe_Ref is np.ma.masked:
        	 stdZe_Ref = np.nan
 
        invalidPoints = Ze_Diff[np.isnan(Ze_Diff)].shape[0]
        totalPoints = Ze_Diff.shape[0]*Ze_Diff.shape[1]
        validPoints = totalPoints - invalidPoints
    
        offSetAr[i] = offset
        stdDiffAr[i] = stdDiff
        validPointsAr[i] = validPoints
        stdZe_RefAr[i] = stdZe_Ref
        
    return offSetAr, stdDiffAr, validPointsAr, stdZe_RefAr
        

def getParameterTimeSerie(parameters, timeFreq):
    
    repeatParameter = 60. / float(timeFreq[:-1]) 
    offsetTimeSerie = np.repeat(parameters[0],repeatParameter)
    stdDiffTimeSerie = np.repeat(parameters[1],repeatParameter)
    validPointsTimeSerie = np.repeat(parameters[2],repeatParameter)
    stdKaTimeSerie = np.repeat(parameters[3],repeatParameter)
    
    return (offsetTimeSerie, stdDiffTimeSerie, 
           validPointsTimeSerie, stdKaTimeSerie)


def applyOffsetCorr(dataFrameToCorret, offset,
                    validPoints, thresholdPoints):
    
    offset[validPoints<thresholdPoints]=0
    dataFrameCorrected = dataFrameToCorret + offset
    
    return dataFrameCorrected


def getParamDF(parameter, timeRef, rangeRef):
        
    parameter[np.isnan(parameter)]=0
    parameterDF=pd.DataFrame(index=timeRef, columns=rangeRef,
                          data=np.tile(parameter,(len(rangeRef),1)).T)
    
    return parameterDF


def getShiftedTemp(interpTempDF, timeRef, rangeRef):
    
    interpTempDF[interpTempDF > 0] = 1 
    interpTempDF[interpTempDF < 0] = -1

    tempArr = np.array(interpTempDF).T
    baseArr = np.zeros((40, tempArr.shape[1]))+1
    shiftedTempArr = np.vstack((baseArr, tempArr))
    shiftedTempArr = np.delete(shiftedTempArr,
                               range(shiftedTempArr.shape[0]-40,
                                     shiftedTempArr.shape[0]),0)

    shiftedTempArr[tempArr>0]=2
    shiftedTempDF = pd.DataFrame(index=timeRef, 
                                 columns=rangeRef, 
                                 data=shiftedTempArr.T)
    
    return shiftedTempDF



def temperatureMask(shiftedTempMaskDF, dataFrameListToMask,
                   variableToMask, timeRef, rangeRef, variableDic):

    dfList = []
    varNames = variableDic.keys()
    shiftedTempMaskArr = np.array(shiftedTempMaskDF)
    for variable in variableToMask:
        
        dataArr = np.array(dataFrameListToMask[varNames.index(variable)])
        maskedData = np.ma.masked_where(shiftedTempMaskArr > 0, dataArr)
        
        maskedDataDF = pd.DataFrame(index=timeRef, columns=rangeRef, data=maskedData)
        
        dfList+=[maskedDataDF]
        
    return dfList

