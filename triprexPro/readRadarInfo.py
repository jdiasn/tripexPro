import pandas as pd
import numpy as np
import datetime

def getFileList(radar, year, month, day, beguinTimeRef):
   outputPath = '/home/jdias/Projects/radarDataResampled/radarInfo'

   #input
   #radar = 'X'
   #year = 2015
   #month = 11
   #day = 24
   #beguinTimeRef = 17

   endTimeRef = beguinTimeRef + 1
   start = pd.datetime(year, month, day,beguinTimeRef, 0, 0)
   end = pd.datetime(year, month, day, endTimeRef, 0, 0)

   if radar == 'Ka':
      outputInfoName = 'kaBandInfo.csv'
      outputFile = ('/').join([outputPath, outputInfoName])
      readData=pd.read_csv(outputFile, index_col='Unnamed: 0')
      date=readData.time_long_name.str.split(' ').str[-3:]#.str.split('.')
    
   if radar == 'W':
      outputInfoName = 'wBandInfo.csv'
      outputFile = ('/').join([outputPath, outputInfoName])
      readData=pd.read_csv(outputFile, index_col='Unnamed: 0')    
      date=readData.time_long_name.str.split(' ').str[-2:]
    
   if radar == 'X':
      outputInfoName = 'xBandInfo.csv'
      outputFile = ('/').join([outputPath, outputInfoName])
      readData=pd.read_csv(outputFile, index_col='Unnamed: 0')
      date=readData.time_long_name.str.split(' ').str[-2:]

   epoch = pd.to_datetime(date.str.get(0))
   humanDateMin=pd.to_timedelta(readData.min_time, unit='s')+epoch
   humanDateMax=pd.to_timedelta(readData.max_time, unit='s')+epoch
   readData['humanDateMin']=humanDateMin
   readData['humanDateMax']=humanDateMax

   if radar == 'X':
      #fazer a busca com tempo em segundos
      #X band
      tempFrame = readData[readData.elv==90.]
      tempFrame = tempFrame[tempFrame.humanDateMin<=start]
      tempFrame = tempFrame[tempFrame.humanDateMax>end]
   else:
      #fazer a busca com tempo em segundos
      #Ka and W band
      tempFrame = readData[readData.elv==90.]
      tempFrame = tempFrame[tempFrame.humanDateMin>=start]
      tempFrame = tempFrame[tempFrame.humanDateMax<end]

   finalFileList = tempFrame.filePath.values
   return list(finalFileList)

