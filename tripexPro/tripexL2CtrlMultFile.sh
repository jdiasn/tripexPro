#-----------------------------
#Shell script to control the
#resample process for entire 
#data set 
#
#--File Definition------------
inputCloudNetPath='/data/data_hatpro/jue/cloudnet/juelich/processed/categorize'
prefixCloudNet='juelich_categorize.nc'

inputPathL1='/home/jdias/Projects/radarDataResampled/data'
#inputPathL1='/work2/tripex/tripex_level_01'
prefixL1='tripex_3fr_L1_mom'

#outputPathL2='/work/radarData/tripexL2'
outputPathL2='/work2/tripex/tripex_level_02'
#outputPathL2='/home/jdias/Projects/radarDataResampled/testL2'
prefixL2='tripex_3fr_L2_mom'
#-----------------------------

#--Time Definition------------
years=('2015' '2016')
#years=('2015') #test
#---year
for year in ${years[@]}
do

if [ $year == '2015' ]
then
months=('11' '12')
#months=('11') #test
fi

if [ $year == '2016' ]
then
months=('01')
fi

#---month
for month in ${months[@]}
do

if [ $month == '11' ]
then
days=('11' '12' '13' '14' '15' '16' '17' '18' '19' '20'\
      '21' '22' '23' '24' '25' '26' '27' '28' '29' '30')
#days=('11') #test
#days=('24') #test
fi

if [ $month == '12' ]
then
days=('01' '02' '03' '04' '05' '06' '07' '08' '09' '10'\
      '11' '12' '13' '14' '15' '16' '17' '18' '19' '20'\
      '21' '22' '23' '24' '25' '26' '27' '28' '29' '30'\
      '31')
#days=('04' '08' '21' '31')
#days=('31')
fi

if [ $month == '01' ]
then
days=('01' '02' '03' '04')
fi

#---day
for day in ${days[@]}
do

echo Date: $(tput setaf 1) $year $month $day $(tput sgr 0)
#---time


timeFreq=4s
timeTolerance=2s
#-----------------------------

#--Range Definition
beguinRangeRef=100
endRangeRef=12000
rangeFreq=30
rangeTolerance=17
#-----------------------------

#--Radar Offset Definitions---
#
zeKaMax=0
zeKaMin=-11
heightThreshold=5000
timeWindowLenght=60
pointsThreshold=300
zeOffsetKa=3 #dB
#-----------------------------

#--Execution------------------
python tripexL2.py $inputCloudNetPath $prefixCloudNet\
                   $inputPathL1 $prefixL1 $outputPathL2 $prefixL2\
                   $year $month $day $timeFreq $timeTolerance \
                   $beguinRangeRef $endRangeRef $rangeFreq $rangeTolerance\
                   $zeKaMax $zeKaMin $heightThreshold $timeWindowLenght\
                   $pointsThreshold $zeOffsetKa

#-----------------------------

done
done
done
