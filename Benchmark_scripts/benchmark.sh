logFileName="utilization-logs.csv"
function waitToNextMinute {
   currentTime=$(date +%s)
   seconds=$(($(date +%s)%60)) #get seconds of current time
   timeToSleep=$((60-$seconds))
   sleep $timeToSleep
}
echo logging cluster info
start_time=$(date +%s)
end_time=$(date +%s)
elapsed=$(( end_time - start_time ))
echo $(date)
echo "waiting for clear minute"
echo "Date,CPUMili,CPUPercent,MemoryBytesUsage,MemoryPercentUsage"
waitToNextMinute
while [ $elapsed -lt 86400 ]
do
   logTimeStamp=$(date +"%T")
   kubePerformanceOutput=$(kubectl top nodes --use-protocol-buffers)
   logCPUMili=$(echo $kubePerformanceOutput | cut -d" " -f7)
   logCPUPercent=$(echo $kubePerformanceOutput | cut -d" " -f8)
   logMemoryUsageBytes=$(echo $kubePerformanceOutput | cut -d" " -f9)
   logMemoryUsagePercent=$(echo $kubePerformanceOutput | cut -d" " -f10)
   logLine=$logTimeStamp,$logCPUMili,$logCPUPercent,$logMemoryUsageBytes,$logMemoryUsagePercent
   echo $logLine >> $logFileName
   echo $logLine
   elapsed=$(( end_time - start_time ))
   waitToNextMinute
done