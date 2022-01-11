package main

import (
	"log"
	"os/exec"
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
	for _, node := range args.Nodes.Items {
		result, err := p.Func(*pod, node)
		//log.Print("Get Error: ",err.Error())
		log.Print("---------- Start of Log Print ----------")

		log.Print("---------- Geet Metadata of pod ----------")
		log.Print("Get Result (boolean): ", result)
		log.Print("Get Node Name: ", pod.GetName())
		log.Print("Get Namespace: ", pod.GetNamespace())
		log.Print("Get Labels: ", pod.GetLabels())

		log.Print("---------- Get Metadata of node ----------")
		log.Print("Get node status: ", node.Status)
		log.Print("Get managed fields: ", node.GetManagedFields())
		log.Print("Get node cpu capacity: ", node.Status.Capacity.Cpu())
		node.Status.Allocatable.Cpu()
		log.Print("Get node cpu allocatable: ", node.Status.Allocatable.Cpu())
		log.Print("Get node memory capacity: ", node.Status.Capacity.Memory())
		log.Print("Get node memory allocatable: ", node.Status.Allocatable.Memory())
		log.Print("Get Pod capacity: ", node.Status.Capacity.Pods())
		log.Print("Get pod allocatable: ", node.Status.Allocatable.Pods())

		log.Print("Get node spec: ", node.Spec.String())
		log.Print("cpu test print: ", node.Status.Capacity.Cpu().Format)
		log.Print("Node status Node info: ", node.Status.NodeInfo)

		log.Print("node status: ", node.Status.Conditions)
		//log.Print("node status to String: ", node.Status.String())
		log.Print("node status config: ", node.Status.Config.String())
		log.Print("node kind", node.Kind)
		log.Print("node info: ", node.Status.NodeInfo)
		//log.Print("node Images: ", node.Status.Images)

		//block to aquire values
		cmd := exec.Command("echo", "hello")
		stdout, err := cmd.Output()
		if err != nil {
			log.Print(err.Error())
		}
		// Print the output
		log.Print("doing sketchy stuff: ")
		log.Print(string(stdout))
		log.Print("doing sketchy stuff end: ")

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

		log.Print("---------- End of Scheduler Log print ----------")
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
