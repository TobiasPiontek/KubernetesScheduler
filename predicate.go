package main

import (
	"log"
	"time"

	v1 "k8s.io/api/core/v1"
	schedulerapi "k8s.io/kubernetes/pkg/scheduler/apis/extender/v1"
)

type Predicate struct {
	Name string
	Func func(pod v1.Pod, node v1.Node) (bool, error)
}

func (p Predicate) Handler(args schedulerapi.ExtenderArgs) *schedulerapi.ExtenderFilterResult {
	pod := args.Pod
	canSchedule := make([]v1.Node, 0, len(args.Nodes.Items))
	canNotSchedule := make(map[string]string)
	log.Print("Testprint of the Predicate handler!")
	for _, node := range args.Nodes.Items {
		result, err := p.Func(*pod, node)
		//log.Print("Get Error: ",err.Error())
		log.Print("Get Result (boolean): ", result)
		log.Print("Get Node Name: ", pod.GetName())
		log.Print("Get Namespace: ", pod.GetNamespace())
		log.Print("Get Labels: ", pod.GetLabels())

		log.Print("---------- Get timestamp of pod ----------")
		log.Print("Get pod timestamp: ", pod.GetCreationTimestamp())
		log.Print("Get pod unix timestamp: ", pod.GetCreationTimestamp().Unix())
		log.Print("Get pod hour: ", pod.GetCreationTimestamp().Hour())
		log.Print("Get pod minute: ", pod.GetCreationTimestamp().Minute())
		log.Print("Get pod seconds: ", pod.GetCreationTimestamp().Second())

		log.Print("---------- Get timestamp of scheduler instance ----------")
		log.Print("scheduler timestamp: ", time.Now())
		log.Print("scheduler unix timestamp: ", time.Now().Unix())
		log.Print("get scheduler hour: ", time.Now().Hour())
		log.Print("Get scheduler minute: ", time.Now().Minute())
		log.Print("Get scheduler second: ", time.Now().Second())

		//node.Status.

		log.Print("Pod UUID: ", pod.GetUID())
		var labels = pod.GetLabels()
		var starttime = time.Now()
		log.Print(starttime)
		log.Print("Printing label value: ", labels["realtime"])
		if err != nil {
			canNotSchedule[node.Name] = err.Error()
		} else {
			if result { //blocked before 11 or after 20  mind one hour offset
				// < 12 means blocked before 13:00
				if labels["realtime"] == "not-critical" && (time.Now().Hour() < 12 || time.Now().Hour() > 20) {
					log.Print("can not schedule!")
					canNotSchedule[node.Name] = err.Error()
				} else {
					log.Print("can schedule!")
					canSchedule = append(canSchedule, node)
				}
			}
		}
	}

	result := schedulerapi.ExtenderFilterResult{
		Nodes: &v1.NodeList{
			Items: canSchedule,
		},
		FailedNodes: canNotSchedule,
		Error:       "",
	}

	return &result
}
