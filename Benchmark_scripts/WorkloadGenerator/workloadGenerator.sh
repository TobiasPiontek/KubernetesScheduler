	echo starting workload generation
indexofpod=0
current_timestamp=$(date +%s)
while IFS=, read -r col1 col2 col3 col4
do
   podname="testpod$indexofpod"
   cat idlePod.yaml | sed "s/"NAME_LABEL"/${podname}/g" | sed "s/"TIMEOUT_DURATION"/${col2}/g" | sed "s/"CPU_MILICORES"/${col1}/g" | sed "s/"CRITICAL-LEVEL"/${col4}/g" |  kubectl apply -f -
   #echo $(cat idlePod.yaml | sed "s/"NAME_LABEL"/${podname}/g" | sed "s/"TIMEOUT_DURATION"/${col2}/g" | sed "s/"CPU_MILICORES"/${col1}/g")
   echo "$(date), Performance values: cpumili: $col1, length: $col2, jobdensity: $col3, critial-level: $col4"
   indexofpod=$((indexofpod+1))
   target=$(($current_timestamp + $col3))
   lag_compensate_sleep=$(($target - $(date +%s)))
   current_timestamp=$(($target))
   sleep $lag_compensate_sleep
done < workload.csv

#get current timestamp in miliseconds $(date +%s%M)

#kubectl get pod --field-selector=status.phase==Succeeded #list completed pods
#kubectl delete pod --field-selector=status.phase==Succeeded #delete completed pods