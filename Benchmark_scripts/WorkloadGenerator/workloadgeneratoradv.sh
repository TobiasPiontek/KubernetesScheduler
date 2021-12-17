echo starting workload generation
indexofpod=0
while IFS=, read -r col1 col2 col3
current_timestamp=$(date +%s)
do
   echo $(date)
   podname="testpod$indexofpod"
   cat idlePod.yaml | sed "s/"NAME_LABEL"/${podname}/g" | sed "s/"TIMEOUT_DURATION"/${col2}/g" | sed "s/"CPU_MILICORES"/${col1}/g" |  kubectl apply -f -
   echo $(cat idlePod.yaml | sed "s/"NAME_LABEL"/${podname}/g" | sed "s/"TIMEOUT_DURATION"/${col2}/g" | sed "s/"CPU_MILICORES"/${col1}/g")
   echo $col1
   echo $col2
   echo $col3
   indexofpod=$((indexofpod+1))
   target=$(($current_timestamp + $col3))
   lag_compensate_sleep=$(($target - $current_timestamp))
   current_timestamp=$(($target))
   sleep $lag_compensate_sleep
done < workload.csv


#kubectl get pod --field-selector=status.phase==Succeeded #list completed pods
#kubectl delete pod --field-selector=status.phase==Succeeded #delte completed pods