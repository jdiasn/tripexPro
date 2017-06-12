#-----------------------------
#Shell script to control the
#resample process for a single file
#
#--File Definition------------
inputPath='/home/jdias/Projects/radarData'
outputPath='/home/jdias/Projects/radarDataResampled'
prefix='tripex_3fr_L1_mom'
#-----------------------------

#--Time Definition------------
year=2015
month=11
day=11
beguinTime=23
timeFreq=4s
timeTolerance=2s
#-----------------------------

#--Range Definition
beguinRangeRef=0
endRangeRef=12000
rangeFreq=30
rangeTolerance=17
#-----------------------------

#--X band Radar setup---------
#
radar='X'
rangeOffSet=-15.5
#variables=('Ze' 'vd')
variables=('Ze')
for variable in ${variables[@]}
do
python tripexL1.py $inputPath $outputPath $prefix $year $month \
                    $day $beguinTime $timeFreq $timeTolerance \
                    $beguinRangeRef $endRangeRef $rangeFreq \
                    $rangeTolerance $radar $rangeOffSet $variable
done
#-----------------------------
echo Radar: $(tput setaf 3) $radar Done $(tput sgr 0)


#--W band Radar setup---------
#
radar='W'
rangeOffSet=0
variables=('Ze' 'vm' 'sigma')
for variable in ${variables[@]}
do
python tripexL1.py $inputPath $outputPath $prefix $year $month \
                    $day $beguinTime $timeFreq $timeTolerance \
                    $beguinRangeRef $endRangeRef $rangeFreq \
                    $rangeTolerance $radar $rangeOffSet $variable
done
#-----------------------------
echo Radar: $(tput setaf 3) $radar Done $(tput sgr 0)


#--Ka band Radar setup---------
#
radar='Ka'
rangeOffSet=2
variables=('Zg' 'VELg' 'RMS' 'LDR')
for variable in ${variables[@]}
do
python tripexL1.py $inputPath $outputPath $prefix $year $month \
                      $day $beguinTime $timeFreq $timeTolerance \
                      $beguinRangeRef $endRangeRef $rangeFreq \
                      $rangeTolerance $radar $rangeOffSet $variable
done
#-----------------------------
echo Radar: $(tput setaf 3) $radar Done $(tput sgr 0)


