#fill in the name of a docker hub Repository to push to (needs to be created and logged in in local docker account)
IMAGE=tobpio/schedulerextender
echo "starting deployment process"
echo "building docker image"
echo $(docker build . -t ${IMAGE}:latest)

echo "uploading to docker hub"
echo $(docker push ${IMAGE})

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
	echo "..."
	kubectl -n kube-system logs deploy/my-scheduler -c my-scheduler-extender-ctr -f
	sleep 5
done