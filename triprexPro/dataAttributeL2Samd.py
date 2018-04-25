def globalAttributes(rootgrpOut):
   
   rootgrpOut.Title = 'Regridded and corrected ground-based X, Ka, W-Band Doppler cloud radar moments obtained during the TRIple-frequency and Polarimetric radar Experiment for improving process observation of winter precipitation (TRIPEx) campaign at JOYCE supersite (Research Center Juelich)'
   rootgrpOut.Institution = 'Emmy-Noether Group OPTIMIce, Institute for Geophysics and Meteorology (IGMK), University of Cologne'
   rootgrpOut.Contact_person = 'Stefan Kneifel, skneifel@meteo.uni-koeln.de'
   rootgrpOut.Source = 'METEOR-50-DX (X-Band radar owned by KIT), Metek MIRA-35 (Ka-Band radar JOYRAD-35 owned by IGMK), RPG-FMCW-94-SP (W-Band radar JOYRAD-94 owned by IGMK)' 
   rootgrpOut.History = 'Data processed with tripexPro.py by University of Cologne'
   rootgrpOut.Conventions = 'CF-1.6 where applicable'
   rootgrpOut.Author = 'Jose Dias Neto (jdiasnet@uni-koeln.de)'
   rootgrpOut.Comments = 'The original radar moment data were re-gridded in height and time; attenuation and offset corrections have been applied but can be reversed by the user since the corrections applied are stored; polarimetry data is limited to LDR since all radar data are from zenith-only operation.'
   rootgrpOut.License = 'For non-commercial use only. This data is subject to the HD(CP)2 data policy to be found at hdcp2.zmaw.de and in the HD(CP)2 Observation Data Product Standard'

   return rootgrpOut


def timeAttributes(timeRef):
  
   timeRef.standard_name = 'time'
   timeRef.long_name = 'time'
   timeRef.comments = 'center of averaging period'  
   timeRef.units = 'seconds since 1970-01-01 00:00:00 UTC'
   timeRef.bounds = 'time_bnds'

   return timeRef


def rangeAttributes(rangeRef):

   rangeRef.long_name = 'distance from sensor to center of each range gates along the line of sight'
   rangeRef.comments = 'Vertical distance (because zenith operation only) of the center radar range gates to the antenna of the reference radar (W band)'
   rangeRef.units = 'm'
   rangeRef.bounds = "range_bnds" 

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

   if varName == 'Ze' and radar == 'Ka':
      offset_correction = 'The Joyrad-35 reflectivites was deviated from Parsivel in -3dB. In this level, 3dB was added in order to correct it'
      variable.offset_correction = offset_correction 

   if varName == 'Attenuation':
      long_name = radar+' band atmospheric 2 way attenuation'
      units = 'dB'
      finalSource = 'Calculated with PAMTRA using CLOUDNET atmospheric profiles'

   if varName == 'Offset':
      long_name = radar+' band offset correction'
      finalSource = 'Offset was calculated for each minute using a moving time window of 10 minutes. Ze from Ka band was used as reference.'
      units = 'dB'

   if varName == 'Correlation':
      long_name = 'Correlation between '+radar+' and Ka band'
      finalSource = 'Correlation was calculated for each minute using a moving time window of 60 minutes.'
      units = '--'
 
   if varName == 'ValidData':
      long_name = 'Number of points used to calculate the '+radar+' band offset.'
      finalSource = 'Offset routine' 
      units = '--'

   if varName == 'Temperature':
      long_name = 'Temperature from CLOUDNET'
      finalSource = 'Temperature from CLOUDNET was interpolated to radar grid'
      units = 'C'

   if varName == 'Pressure':
      long_name = 'Pressure from CLOUDNET'
      finalSource = 'Pressure from CLOUDNET was interpolated to radar grid'
      units = 'Pa'
 
   if varName == 'RelHum':
      long_name = 'Relative humidity from CLOUDNET'
      finalSource = 'Humidity from CLOUDNET was interpolated to radar grid'
      units = '%'
    
   if varName == 'v':
      long_name = radar+' band Mean Doppler velocity (Sign convention: Negative when moving towards the radar) '
      units = 'm s-1'
      variable.Nyquist_velocity = velocityLim

   if varName == 'SW':
      long_name = radar+' band Spectrum Width'
      units = 'm s-1'
 
   if varName == 'LDR':
      long_name = radar+' band Linear De-Polarization Ratio'
      units = 'dB'
    
   if varName == 'delta_altitude':
      long_name = radar+' band vertical distance of the original range resolution to the vertical grid (var:altitude) used to resample the data'
      units = 'm'

   if varName == 'delta_time':
      long_name = radar+' band temporal difference between the original time resolution and the time vector used to resample the data'
      units = 's'

 
   if varName == 'IWV':
      long_name = 'Integrated water vapor'
      finalSource = 'Integrated water vapor retrieved by Microwave Radiometer'
      units = 'kg m-2'

   if varName == 'IWVFlag':
      long_name = 'Integrated water vapor quality flag'
      finalSource = 'Integrated water vapor quality flag'
      units = ''

   if varName == 'LWP':
      long_name = 'Liquid water path'
      finalSource = 'Liquid water path retrieved by Microwave Radiometer'
      units = 'kg m-2'

   if varName == 'LWPFlag':
      long_name = 'Liquid water path quality flag'
      finalSource = 'Liquid water path quality flag'
      units = ''

   if varName == 'AccRainFall':
      long_name = 'Accumulated rain fall'
      finalSource = 'Accumulated rain fall retrieved by Pluvio'
      units = 'mm'

   if varName == 'rainFallRate':
      long_name = 'Rain fall rate'
      finalSource = 'Rain fall rate retrieved by Pluvio'
      units = 'mm -h'

   if varName == 'CldBaseHeight':
      long_name = 'Cloud base height'
      finalSource = 'Cloud base height retrieved by Ceilometer'
      units = 'm'

     
   variable.long_name = long_name
   variable.units = units
   variable.source = finalSource

   return variable




