import numpy as np
import pandas as pd
import glob
from netCDF4 import Dataset

def getEmptyMatrix(rows, cols):

   emptyMatrix = np.ones((rows, cols))
   emptyMatrix[:] = np.nan
   emptyMatrix = np.ma.masked_invalid(emptyMatrix)
    
   return emptyMatrix

def getEpochTime(rootgrp, radar):

   if radar == 'W':
      long_name = getattr(rootgrp.variables['time'], 'long_name').split(' ')  
      date = long_name[-2]
      time = long_name[-1]
            
   elif radar == 'X':
      long_name = getattr(rootgrp.variables['time'], 'long_name').split(' ')  
      date = long_name[-2]
      time = long_name[-1]

   else:
      long_name = getattr(rootgrp.variables['time'], 'long_name').split(' ')
      date = long_name[-3]
      time = long_name[-2]
         
   epoch = pd.to_datetime(' '.join([date, time]))
    
   return epoch

   
def getFileList(dataPath, date, beguinTime, radar):
   
   
   beguinTime = str(beguinTime)
   if radar == 'W':
      prefix = 'joyrad94_joyce_compact_'
      suffix = ('').join([beguinTime,'.nc'])
      fileNameSearch = ('*').join([date, suffix])
      fileNameSearch = ('').join([prefix, fileNameSearch])
      fileNameSearch = ('/').join([dataPath, fileNameSearch])
    
   elif radar == 'X':
      suffix = 'kixpol.nc'
      fileNameSearch = ('*').join([date, suffix])
      fileNameSearch = ('/').join([dataPath, fileNameSearch])
        
   else:
      suffix = 'mmclx.00'
      fileNameSearch = ('*').join([beguinTime, suffix])
      fileNameSearch = ('_').join([date,fileNameSearch])
      fileNameSearch = ('/').join([dataPath, fileNameSearch])

   fileList = glob.glob(fileNameSearch)
   #fileList = fileList.sort()
   #print fileNameSearch
   return fileList

 

def getIndexList(dataTable, reference, tolerance):
    
   indexList = []
   for value in reference:
    
      index = getNearestIndex(dataTable, value, tolerance)
      indexList.append(index)

   return indexList


def getNearestIndex(timeRef, timeStamp, tolerance):

   try:
      index = timeRef.index.get_loc(timeStamp, method='nearest', 
                                   tolerance=tolerance)
    
   except:
      index = np.nan
    
   return index


def getResampledData(emptyMatrixData, variableData, indexList, usedIndex):
    
   usedIndex = []
   for i,index in enumerate(indexList):

      try:
         emptyMatrixData[i] = variableData[int(index)]
         usedIndex[i] = int(index)
       
      except:
         pass
    
   return emptyMatrixData, usedIndex
