package main

import (
	"log"

	v1 "k8s.io/api/core/v1"
	schedulerapi "k8s.io/kubernetes/pkg/scheduler/apis/extender/v1"
)

//global variable
var x bool = false

type Predicate struct {
	Name string
	Func func(pod v1.Pod, node v1.Node) (bool, error)
}

func GetX() bool {
	return x
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
		log.Print("Node properties: ", pod.GetName())
		log.Print("Node properties: ", pod.GetNamespace())
		log.Print("Node properties: ", pod.GetLabels())
		log.Print("Node properties: ", pod.GetManagedFields())
		if err != nil {
			canNotSchedule[node.Name] = err.Error()
		} else {
			if result {
				//canNotSchedule[node.Name] = err.Error()
				//canNotSchedule[node.Name] = err.Error()
				//log.Print("Delaying the pod start for 30 seconds")
				//time.Sleep(30 * time.Second)
				canSchedule = append(canSchedule, node)
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
