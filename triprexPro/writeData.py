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
      rootgrpOut.createDimension('time_ref', None)
      time_ref = rootgrpOut.createVariable('time_ref', np.int64, ('time_ref',))
      time_ref[:] = timeRef
      time_ref = dataAttribute.timeAttributes(time_ref)
      return time_ref

   except:
      return None


def createRangeDimension(rootgrpOut, rangeRef):

   try:
      rootgrpOut.createDimension('range_ref', len(rangeRef))
      range_ref = rootgrpOut.createVariable('range_ref', np.float32, 
		                           ('range_ref',), fill_value=np.nan)
      range_ref[:] = rangeRef
      range_ref = dataAttribute.rangeAttributes(range_ref)
      return range_ref

   except:
      return None


def createVariable(rootgrpOut, variable, varName, varNameOutput, radar):

   try:
    
      var_nearest = rootgrpOut.createVariable(varNameOutput, np.float32,
                                             ('time_ref','range_ref'), 
                                             fill_value=np.nan)
      var_nearest[:] = variable
      var_nearest = dataAttribute.variableAttribute(var_nearest, varName,
                                                   radar)
      return var_nearest

   except:
      return None



