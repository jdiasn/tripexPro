def globalAttributes(rootgrpOut):
   
   rootgrpOut.Experiment = 'TRIPEX, Forschungszentrum Juelich'
   rootgrpOut.Instrument = 'Ka Band Cloud Radar MIRA-36, METEK GmbH www.metek.de'
   rootgrpOut.Data = 'Produced by Jose Dias, jdiasnet@uni-koeln.de'
   rootgrpOut.Routines = 'resampleKa.py'

   return rootgrpOut


def timeAttributes(timeRef):
   
   timeRef.long_name = 'time in sec since 01.01.1970 00:00:00'
   timeRef.units = 'seconds'

   return timeRef


def rangeAttributes(rangeRef):

   rangeRef.long_name = 'Range from Ka band radar antenna to the centre of each range gate'
   rangeRef.units = 'm'

   return rangeRef


def variableAttribute(variable, varName, radar):


   # Ze attribute
   if varName == 'Ze':
      
      long_name = 'Equivalent '+radar+' band Reflectivity Factor Ze of all Targets'
      units = 'dBZ'

   if varName == 'Vd':
      
      long_name = radar+' band Mean Doppler velocity'
      units = 'm/s'

   if varName == 'SW':
      
      long_name = radar+' band Peak Width'
      units = 'm/s'
 
   if varName == 'LDR':
      
      long_name = radar+' band Linear De-Polarization Ratio'
      units = 'm/s'
     
   variable.long_name = long_name
   variable.units = units

   return variable


