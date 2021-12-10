echo "executing workload generation"
cat pod-template.yaml | sed 's/NAME_LABEL/testpod123/' | kubectl apply -f -

echo "waiting 120 seconds"
sleep 60

cat pod-template.yaml | sed 's/NAME_LABEL/testpod123/' | kubectl delete -f -

echo "deleted pod"