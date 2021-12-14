#calculate the remaining time to queue the next log api call precisely
duration=1200
cpumili=10
#function block
function waitToNextMinute {
   currentTime=$(date +%s)
   seconds=$(($(date +%s)%60)) #get seconds of current time
   timeToSleep=$((60-$seconds))
   sleep $timeToSleep
}

#waitToNextMinute

for podindex in {1..100}
do
   podname="testpod$podindex"
   echo $podname
   echo "Deploy Pod: $i"
   cat idlePod.yaml | sed "s/"NAME_LABEL"/${podname}/g" | sed "s/"TIMEOUT_DURATION"/${duration}/g" | sed "s/"CPU_MILICORES"/${cpumili}/g" |  kubectl apply -f -
   echo $(cat idlePod.yaml | sed "s/"NAME_LABEL"/${podname}/g" | sed "s/"TIMEOUT_DURATION"/${duration}/g" | sed "s/"CPU_MILICORES"/${cpumili}/g") >> log.txt
   sleep 10
done

echo "waiting for completion"
sleep 1200
kubectl get pod --field-selector=status.phase==Succeeded #list completed pods
kubectl delete pod --field-selector=status.phase==Succeeded #delte completed pods

echo "deleted completed pods"
