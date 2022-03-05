echo "starting deployment process"
IMAGE=tobpio/schedulerextender
echo "building docker image"
echo $(docker build . -t tobpio/schedulerextender:latest)

echo "uploading to docker hub"
echo $(docker push tobpio/schedulerextender)

echo "delete old deployment on Kubernetes"
echo $(sed 's/a\/b:c/'$(echo "${IMAGE}" | sed 's/\//\\\//')'/' extender.yaml | kubectl delete -f -)
sleep 5
echo "create new deployment on Kubernetes"
echo $(sed 's/a\/b:c/'$(echo "${IMAGE}" | sed 's/\//\\\//')'/' extender.yaml | kubectl apply -f -)
echo "waiting for deployment to come online"
sleep 10
#hook into the scheduler extender logs to see scheduling decision meta data
while true
do
	kubectl -n kube-system logs deploy/my-scheduler -c my-scheduler-extender-ctr -f
	sleep 5
done