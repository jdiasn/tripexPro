def globalAttributes(rootgrpOut):
   
   rootgrpOut.Title = 'Regridded and corrected ground-based X, Ka, W-Band Doppler cloud radar moments obtained during the TRIple-frequency and Polarimetric radar Experiment for improving process observation of winter precipitation (TRIPEx) campaign at JOYCE supersite (Research Center Juelich)'
   rootgrpOut.Institution = 'Emmy-Noether Group OPTIMIce, Institute for Geophysics and Meteorology (IGMK), University of Cologne'
   rootgrpOut.Contact_person = 'Stefan Kneifel, skneifel@meteo.uni-koeln.de'
   rootgrpOut.Source = 'METEOR-50-DX (X-Band radar owned by KIT), Metek MIRA-35 (Ka-Band radar JOYRAD-35 owned by IGMK), RPG-FMCW-94-SP (W-Band radar JOYRAD-94 owned by IGMK)' 
   rootgrpOut.History = 'Data processed with tripexPro.py by University of Cologne'
   rootgrpOut.Dependencies = 'External'
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
  
   radar = radar.capitalize()
   if radar == 'X':
      commentZe = 'The original reflectivities have been re-gridded onto a common time-height grid and have been corrected for gas attenuation; relative calibrated has been applied with Ka-Band radar in the high altitude ice part when possible. Note that the reflectivity resolution of the instrument is only 0.5 dB.'

      commentVel = 'Sign convention: Negative when moving towards the radar. Note that the radar antenna had to continuously rotate (bird bath scan) in order to record data. The antenna seemed to had a slight mis-pointing thus a sinusoidal modulation is sometimes visible depending on the horizontal wind. This signature disappears with longer averaging.'

      commentOff = 'After reflectivities have been corrected for gas attenuation for each frequency, the remaining offsets due to wet radome etc. have been estimated by using 30 min of data, regions at least 1km above the zero degree isotherm and reflectivities smaller than 0 dBz. Assuming the Ka-band radar as our reference, we assume that for X and Ka-band these low-reflectivity ice clouds represent Rayleigh scatterers and hence the reflectivities should match. A quality flag is provided indicating the reliability of the correction applied. The user can simply go back to the attenuation-only corrected reflectivities by subtracting this offset to the corrected reflectivity values.'

   elif radar == 'Ka':
      commentZe = 'The original reflectivities have been re-gridded onto a common time-height grid and have been corrected for gas attenuation; relative calibration has been performed with rain cases observed together with PARSIVEL.'
      
      commentVel = 'Sign convention: Negative when moving towards the radar. Note that we are suspecting a slight mispointing of the antenna in the order of 0.5 degree off-zenith. This needs more in-depths investigation but can lead to offsets in the order of 0.1-0.3 m/s in case of strong horizontal winds.'

   elif radar == 'W':
      commentZe = 'The original reflectivities have been re-gridded onto a common time-height grid and have been corrected for gas attenuation; relative calibrated has been applied with Ka-Band radar in the high altitude ice part when possible.'
      
      commentVel = 'Sign convention: Negative when moving towards the radar'

      commentOff = 'After reflectivities have been corrected for gas attenuation for each frequency, the remaining offsets due to wet radome, liquid water attenuation, etc. have been estimated by using 30 min data, regions at least 1km above the zero degree isotherm and reflectivities smaller than -10dBZ. Assuming the Ka-band radar as our reference, we assume that for W and Ka-band these low-reflectivity ice clouds represent Rayleigh scatterers and hence the reflectivities should match. A quality flag is provided indicating the reliability of the correction applied. The user can simply go back to the attenuation-only corrected reflectivities by subtracting this offset to the corrected reflectivity values'

   if varName == 'dbz':
      standard_name = 'equivalent_reflectivity_factor'
      long_name = 'equivalent reflectivity factor {radar}-Band'.format(radar=radar)
      units = 'dBZ'
      finalComment = commentZe
   
   elif varName == 'rv':
      standard_name = 'radial_velocity_of_scatterers_away_from_instrument'
      long_name = 'mean Doppler velocity {radar}-Band'.format(radar=radar)
      units = 'm s-1'
      finalComment = commentVel

   elif varName == 'sw':
      long_name = 'radar spectral width {radar}-Band'.format(radar=radar)
      units = 'm s-1'
 
   elif varName == 'ldr':
      long_name = 'radar linear depolarization ratio {radar}-Band'.format(radar=radar)
      units = 'dB'
 
   elif varName == 'pia':
      long_name = 'path integrated attenuation {radar}-Band (two-way) due to gaseous atmosphere'.format(radar=radar)
      units = 'dBZ'
      finalComment = 'Two-way path integrated attenuation due to dry gases and water vapor calculated with radiative transfer model PAMTRA and thermodynamic profiles from CloudNet product for JOYCE site. Simply subtract these values from the corrected reflectivities in order to restore the uncorrected reflectivities.'

   elif varName == 'offset':
      long_name = 'relative offset of {radar}-Band compared to reference Ka-Band'.format(radar=radar)
      units = 'dBZ'
      finalComment = commentOff

   elif varName == 'freq_sb':
      standard_name = 'sensor_band_central_radiation_frequency'
      long_name = 'operating frequency of {radar}-Band radar'.format(radar=radar)
      units = 's-1'

   elif varName == 'radar_beam_width':
      long_name = '3dB beam width of the {radar}-Band radar'.format(radar=radar)
      units = 'degree'

   elif varName == 'lon':
      standard_name = 'longitude'	
      long_name = 'longitude of reference radar system' 
      finalComment = 'Longitude of the reference radar (W-Band) location in decimals.'
      units = 'degrees_east'

   elif varName == 'lat':
      standard_name = 'latitude'	
      long_name = 'latitude of reference radar system' 
      finalComment = 'Latitude of the reference radar (W-Band) location in decimals.'
      units = 'degrees_north'

   elif varName == 'zsl':
      standard_name = 'altitude' 
      long_name = 'altitude above mean sea level'
      finalComment = 'altitude above mean sea level of the reference radar (W-Band) location'
      units = 'm'

   elif varName == 'quality_flag_offset':
      long_name = 'quality flag indicating reliability of the offset correction for the {radar}-Band data'.format(radar=radar)
      finalComment = 'Bits 0 to 5: empty; Bit 6: 0 if the liquid water path is less than 200 g m-2, 1 if the liquid water path is greater than 200 g m-2; Bit 7: 0 no rain, 1 rain; Bits 8 to 13: empty; Bit 14: 0 if offset correlation is greater than 0.7, 1 if offset correlation is less than 0.7; Bit 15: 0 if the number of points used to calculate the of offset is greater than 300, 1 if the number of points is less than 300. If Bit 14 or higher is set, we recommend not to use the calculated offsets but e.g. rather interpolate between time periods with high-quality offset estimates.'
      units = '1'

   try: 
         variable.standard_name = standard_name
   except:
         print 'no standard_name to write'
 	 pass
  
   try:
         variable.long_name = long_name
   except:
         print 'no long_name to write'
         pass

   try:
         variable.units = units
   except:
         print 'no units to write'
         pass

   try:
        variable.comments = finalComment
   except:
        print 'no comment to write'
        pass

   return variable




