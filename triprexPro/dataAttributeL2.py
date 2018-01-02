def globalAttributes(rootgrpOut):
   
   rootgrpOut.Experiment = 'TRIPEX, Forschungszentrum Juelich'
   rootgrpOut.Instruments = 'JOYRAD-94 94.4 GHz cloud radar (W band), JOYRAD-35 35.5 GHz cloud radar (Ka band), KIXPOL 9.4 GHz radar (KIT) (X band)'
   rootgrpOut.Data = 'Produced by Jose Dias, jdiasnet@uni-koeln.de'
   rootgrpOut.Processed_with = 'tripexPro*.py'
   rootgrpOut.Institution = 'Data processed within the Emmy-Noether Group OPTIMIce, Institute for Geophysics and Meteorology, University of Cologne, Germany'
   rootgrpOut.comment = 'This dataset (level 2) was produced using the level 1 dataset from TRIPEx. Offset and  attenuation corrections were applied to correct the reflectivities'
   rootgrpOut.Latitude = '50.908547 N'
   rootgrpOut.Longitude = '6.413536 E'
   rootgrpOut.Altitude = 'Altitude of the JOYCE (www.joyce.cloud) platform: 111m asl'

   return rootgrpOut


def timeAttributes(timeRef):
   
   timeRef.long_name = 'time in sec since 01.01.1970 00:00:00'
   timeRef.units = 's'

   return timeRef


def rangeAttributes(rangeRef):

   rangeRef.long_name = 'Vertical distance of the center radar range gates to the JOYCE platform + 1.5m (altitude of W band center range gates)'
   rangeRef.units = 'm'

   return rangeRef


def variableAttribute(variable, varName, radar):

   if radar == 'X':
      source = 'KIXPOL 9.4 GHz radar (KIT) TRIPEx Level 1'
      velocityLim = '+/- 80 m s-1'

   if radar == 'Ka':
      source = 'JOYRAD-35 35.5 GHz cloud radar TRIPEx Level 1'
      velocityLim = '+/- 20 m s-1'

   if radar == 'W':
      source = 'JOYRAD-94 94 GHz cloud radar TRIPEx Level 1'
      velocityLim = '+/- 18 m s-1'

   if varName == 'Ze':
      long_name = 'Equivalent '+radar+' band Reflectivity Factor Ze of all Targets. Offset and Attenuation corrections were applied'
      finalSource = source
      units = 'dBZ'

   if varName == 'Attenuation':
      long_name = radar+' band atmospheric 2 way attenuation'
      units = 'dB'
      finalSource = 'Calculated with PAMTRA using CLOUDNET atmospheric profiles'

   if varName == 'Offset':
      long_name = radar+' band offset correction'
      finalSource = 'Offset was calculated for each minute using a moving time window of 10 minutes. Ze from Ka band was used as reference.'
      units = 'dB'
 
   if varName == 'ValidData':
      long_name = 'Number of points used to calculate the '+radar+' band offset.'
      finalSource = 'Offset routine' 
      units = '--'
    
     
   variable.long_name = long_name
   variable.units = units
   variable.source = finalSource

   return variable




