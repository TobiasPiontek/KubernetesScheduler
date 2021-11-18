package main

import (
	"log"

	v1 "k8s.io/api/core/v1"
	schedulerapi "k8s.io/kubernetes/pkg/scheduler/apis/extender/v1"
)

type Prioritize struct {
	Name string
	Func func(pod v1.Pod, nodes []v1.Node) (*schedulerapi.HostPriorityList, error)
}

func (p Prioritize) Handler(args schedulerapi.ExtenderArgs) (*schedulerapi.HostPriorityList, error) {
	log.Print("info of priority: ", args.Pod)
	//fmt.Println(p.Func(*args.Pod, args.Nodes.Items))
	return p.Func(*args.Pod, args.Nodes.Items)
}
