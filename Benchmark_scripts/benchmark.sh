function waitToNextMinute {
   currentTime=$(date +%s)
   seconds=$(($(date +%s)%60)) #get seconds of current time
   timeToSleep=$((60-$seconds))
   sleep $timeToSleep
}

echo logging cluster info
echo mili cores, percent

start_time=$(date +%s)
end_time=$(date +%s)
elapsed=$(( end_time - start_time ))

echo $(date)
echo "waiting for clear minute"
waitToNextMinute

while [ $elapsed -lt 86400 ]
do
   echo $(date)
   sentence=$(kubectl top nodes --use-protocol-buffers)
   echo $sentence | cut -d" " -f7
   echo $sentence | cut -d" " -f8
   elapsed=$(( end_time - start_time ))
   waitToNextMinute
done