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
		log.Print("Get Node Name", pod.GetName())
		log.Print("Get Namespace ", pod.GetNamespace())
		log.Print("Get Labels: ", pod.GetLabels())
		log.Print("Get Timestamp", pod.GetCreationTimestamp())
		log.Print("", time.Now())
		log.Print("Pod UUID: ", pod.GetUID())
		var labels = pod.GetLabels()
		var starttime = time.Now()
		log.Print(starttime)
		log.Print("Printing label value: ", labels["realtime"])
		if err != nil {
			canNotSchedule[node.Name] = err.Error()
		} else {
			if result {
				if labels["realtime"] == "not-critical" {
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
