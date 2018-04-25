from netCDF4 import Dataset
import dataAttributeL1
import dataAttributeL2
import dataAttributeL2Samd
import numpy as np

def defineAttr(prefix):
   
   if prefix == 'tripex_3fr_L1_mom':
      dataAttribute = dataAttributeL1 

   elif prefix == 'tripex_3fr_L2_mom':
      dataAttribute = dataAttributeL2 

   elif prefix == 'tripex_joy_tricr00_l1_any_v00_':
      dataAttribute = dataAttributeL2Samd

   return dataAttribute

def createNetCdf(outPutFilePath, prefix):

   dataAttribute = defineAttr(prefix)

   try:
      rootgrpOut = Dataset(outPutFilePath, 'a', format='NETCDF4')
    
   except:
      rootgrpOut = Dataset(outPutFilePath, 'w', format='NETCDF4')

   rootgrpOut = dataAttribute.globalAttributes(rootgrpOut)

   return rootgrpOut


def createTimeDimension(rootgrpOut, timeRef, prefix):

   dataAttribute = defineAttr(prefix)

   try:
      rootgrpOut.createDimension('time', None)
      time_ref = rootgrpOut.createVariable('time', np.float64, ('time',))
      time_ref[:] = timeRef
      time_ref = dataAttribute.timeAttributes(time_ref)
      return time_ref

   except:
      return None


def createRangeDimension(rootgrpOut, rangeRef, prefix):

   dataAttribute = defineAttr(prefix)

   try:
      rootgrpOut.createDimension('range', len(rangeRef))
      range_ref = rootgrpOut.createVariable('range', np.float32,
		                           ('range',), fill_value=np.nan)
      range_ref[:] = rangeRef
      range_ref = dataAttribute.rangeAttributes(range_ref)
      return range_ref

   except:
      return None


def createVariable(rootgrpOut, variable, varName, varNameOutput, radar, prefix):

   dataAttribute = defineAttr(prefix)

   try:
    
      var_nearest = rootgrpOut.createVariable(varNameOutput, np.float32,
                                             ('time','altitude'), 
                                             fill_value=np.nan)
      var_nearest[:] = variable
      var_nearest = dataAttribute.variableAttribute(var_nearest,
                                                   varName,
                                                   radar)
      return var_nearest

   except:
      return None


def createDeviation(rootgrpOut, variable, varName, radar, prefix):

   dataAttribute = defineAttr(prefix)

   dimension = varName.split('_')[-1]
   varNameOutput = '_'.join([varName, radar])
 
   if varName == 'time':
      varType = np.int64
      
   else: 
      varType = np.float32

   try:
    
      var_nearest = rootgrpOut.createVariable(varNameOutput, varType,
                                             (dimension), fill_value=np.nan)
      var_nearest[:] = variable
      var_nearest = dataAttribute.variableAttribute(var_nearest, 
                                                   varName, radar)
      return var_nearest

   except:
      return None

def create1Dvariable(rootgrpOut, variable, varName, sensor, prefix):

   dataAttribute = defineAttr(prefix)
   varNameOutput = varName   

   try:
      var_nearest = rootgrpOut.createVariable(varNameOutput, np.float32,
                                           ('time'), fill_value=np.nan)
      var_nearest[:] = variable
      var_nearest = dataAttribute.variableAttribute(var_nearest,
                                                 varName, sensor)
      return var_nearest

   except:
      return None
  

