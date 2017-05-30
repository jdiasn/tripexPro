from netCDF4 import Dataset
import dataAttribute
import numpy as np

def createNetCdf(outPutFilePath):

   try:
      rootgrpOut = Dataset(outPutFilePath, 'a', format='NETCDF4')
    
   except:
      rootgrpOut = Dataset(outPutFilePath, 'w', format='NETCDF4')

   rootgrpOut = dataAttribute.globalAttributes(rootgrpOut)

   return rootgrpOut


def createTimeDimension(rootgrpOut, timeRef):

   try:
      rootgrpOut.createDimension('time', None)
      time_ref = rootgrpOut.createVariable('time', np.int64, ('time',))
      time_ref[:] = timeRef
      time_ref = dataAttribute.timeAttributes(time_ref)
      return time_ref

   except:
      return None


def createRangeDimension(rootgrpOut, rangeRef):

   try:
      rootgrpOut.createDimension('altitude', len(rangeRef))
      range_ref = rootgrpOut.createVariable('altitude', np.float32,
		                           ('altitude',), fill_value=np.nan)
      range_ref[:] = rangeRef
      range_ref = dataAttribute.rangeAttributes(range_ref)
      return range_ref

   except:
      return None


def createVariable(rootgrpOut, variable, varName, varNameOutput, radar):

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


def createRangeDeviation(rootgrpOut, variable, varName, varNameOutput, radar):

   try:
    
      var_nearest = rootgrpOut.createVariable(varNameOutput, np.float32,
                                             ('altitude'), fill_value=np.nan)
      var_nearest[:] = variable
      var_nearest = dataAttribute.variableAttribute(var_nearest, 
                                                   varName,
                                                   radar)
      return var_nearest

   except:
      return None

