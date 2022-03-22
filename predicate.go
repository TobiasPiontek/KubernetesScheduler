package main

import (
	"encoding/csv"
	"log"
	"os"
	"os/exec"
	"regexp"
	"strconv"
	"strings"
	"time"

	v1 "k8s.io/api/core/v1"
	schedulerapi "k8s.io/kubernetes/pkg/scheduler/apis/extender/v1"
)

var co2_data [][]string
var workload_data_prediction []float64

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

		//Block to assign server state variables
		cpulimit := getCPUUtilization()

		log.Print("---------- Start of Log Print ----------")

		log.Print("---------- Geet Metadata of pod ----------")
		log.Print("Get Result (boolean): ", result)
		//log.Print("Get Node Name: ", pod.GetName())
		//log.Print("Get Namespace: ", pod.GetNamespace())
		//log.Print("Get Labels: ", pod.GetLabels())

		//log.Print("---------- Get Metadata of node ----------")
		//log.Print("Get node status: ", node.Status) lots of info but current resource limit not encoded
		//log.Print("Get managed fields: ", node.GetManagedFields()) //results in messy printout coded in unreadable way
		//log.Print("Get node cpu capacity: ", node.Status.Capacity.Cpu())
		//log.Print("Get node cpu allocatable: ", node.Status.Allocatable.Cpu())
		//log.Print("Get node memory capacity: ", node.Status.Capacity.Memory())
		//log.Print("Get node memory allocatable: ", node.Status.Allocatable.Memory())
		//log.Print("Get Pod capacity: ", node.Status.Capacity.Pods())
		//log.Print("Get pod allocatable: ", node.Status.Allocatable.Pods())

		//log.Print("Get node spec: ", node.Spec.String()) //details about ip address room
		//log.Print("Node status Node info: ", node.Status.NodeInfo)//runtime information

		//log.Print("node status: ", node.Status.Conditions)
		//log.Print("node status config: ", node.Status.Config.String()) //usefull for logs, in case some resource limits the node

		log.Print("---------- Get timestamp of pod ----------")
		//log.Print("Get pod timestamp: ", pod.GetCreationTimestamp())
		log.Print("Get pod unix timestamp: ", pod.GetCreationTimestamp().Unix(), "curent time is: ", time.Now().Unix())
		log.Print("Get pod hour: ", pod.GetCreationTimestamp().Hour())
		log.Print("Get pod minute: ", pod.GetCreationTimestamp().Minute())
		log.Print("Get pod seconds: ", pod.GetCreationTimestamp().Second())
		log.Print("Get Pod resource limits: ", pod.Spec.Containers[0].Resources.Limits.Cpu().MilliValue())
		//pod.GetCreationTimestamp().Time.Unix()
		//log.Print("---------- Get timestamp of scheduler instance ----------")
		//log.Print("scheduler timestamp: ", time.Now())
		//log.Print("scheduler unix timestamp: ", time.Now().Unix())
		//log.Print("get scheduler hour: ", time.Now().Hour())
		//log.Print("Get scheduler minute: ", time.Now().Minute())
		//log.Print("Get scheduler second: ", time.Now().Second())

		log.Print("cpu Limit of node as float is: ", cpulimit)

		log.Print("---------- End of Scheduler Log print ----------")

		log.Print("Pod UUID: ", pod.GetUID())
		var labels = pod.GetLabels()
		var starttime = time.Now()
		log.Print(starttime)
		log.Print("Printing label value: ", labels["realtime"]) //printing whether critical pod or not for debugging purposes

		var start_of_co2_window int
		var end_of_co2_window int
		start_of_co2_window, end_of_co2_window = get_co2_time_window()
		log.Print("Start: ", start_of_co2_window, " End: ", end_of_co2_window)
		log.Print("current time system time: ", time.Now().Hour())
		var hour_utc_plus_one = (time.Now().Hour() + 1) % 24
		log.Print("current hour utc+1 adapted is: ", hour_utc_plus_one) //used on code level, as changing container time zone did not work

		var workloadlimit = 0.95 - workload_data_prediction[hour_utc_plus_one]*0.1
		log.Print("workload for current hour is: ", workload_data_prediction[hour_utc_plus_one])
		log.Print("Current workload limit is: ", workloadlimit)

		var podage = pod.GetCreationTimestamp().Unix() - time.Now().Unix()
		var maximum_shift_time = int64(86400) // 24 hours, after this a pod is basically treated as a critical pod
		log.Print("Current pod waiting for: ", podage, " seconds")

		log.Print("Pod priority class is: ", pod.Spec.PriorityClassName)

		if err != nil {
			canNotSchedule[node.Name] = err.Error()
		} else {
			if result {
				if pod.Spec.PriorityClassName == "not-critical" && podage < maximum_shift_time && (cpulimit > workloadlimit ||
					(hour_utc_plus_one < start_of_co2_window || hour_utc_plus_one > end_of_co2_window)) {
					log.Print("can not schedule!")
					if cpulimit > workloadlimit {
						log.Print("Reason for not schedule: CPU reservation limit exceeded!")
						log.Print("Limit currently is: ", workloadlimit)
					}
					if hour_utc_plus_one < start_of_co2_window || hour_utc_plus_one > end_of_co2_window {
						log.Print("Reason for not schedule: Out of optimal CO2 time window!")
					}
				} else {
					resourcePercentagePod := (float64(pod.Spec.Containers[0].Resources.Limits.Cpu().MilliValue()) / float64(node.Status.Capacity.Cpu().MilliValue()))
					log.Print("cpu Limit of node as float is: ", cpulimit)
					log.Print("Get Pod resource percentage: ", resourcePercentagePod)
					log.Print("can schedule!")
					log.Print("Get pod creation timestamp: ", pod.GetCreationTimestamp())
					log.Print("Get Node Name: ", pod.GetName())
					log.Print("Get Labels: ", pod.GetLabels())

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

//simple function to read in a csv file as a 2d list
func readCsvFile(filePath string) [][]string {
	f, err := os.Open(filePath)
	if err != nil {
		log.Fatal("Unable to read input file "+filePath, err)
	}
	defer f.Close()

	csvReader := csv.NewReader(f)
	records, err := csvReader.ReadAll()
	if err != nil {
		log.Fatal("Unable to parse file as CSV for "+filePath, err)
	}
	return records
}

func read_workload_prediction(filePath string) []float64 {
	var workload_data [][]string
	workload_data = readCsvFile(filePath)
	workload_data_float := make([]float64, len(workload_data))
	for i := 0; i < len(workload_data); i++ {
		workload_data_float[i], _ = strconv.ParseFloat(workload_data[i][0], 64)
	}
	return workload_data_float
}

//external function call for main, to trigger the csv parsing on startup of the scheduler (only performed once)
func initialize_lookup_tables() {
	//log.Print(exec.Command("ls"))
	co2_data = readCsvFile("../usr/bin/average_co2_emissions.csv")
	//get_current_day_as_float()
	var start, end = get_co2_time_window()
	log.Print("time window of today is: ", start, ", to: ", end)
	workload_data_prediction = read_workload_prediction("../usr/bin/workload_prediction.csv")
	//log.Print(workload_data_prediction)
	//log.Print(co2_data)
	//log.Print(co2_data[0])
	//log.Print(len(co2_data[0]))
	//log.Print(len(co2_data))
}

//helper method to extract the current day
func get_current_day_as_float() []float64 {
	today := time.Now()
	year, week := today.ISOWeek()

	weekday := (int((today.Day() + 1) % 7)) //conversion between Python and GO weekdays Monday = 0 in Python sunday = 0 in go
	log.Print("iso week is: ", week, ", year: ", year)
	log.Print("weekday is: ", today.Weekday(), ", ", today.Day())
	log.Print("weekday is: ", weekday)
	lookupvalue := weekday + (week-1)*7

	//lookupvalue = 78
	//convert the sub string array to a float array

	log.Print("get index for lookup: ", lookupvalue, " , Excel row: ", lookupvalue+1)

	converted := make([]float64, len(co2_data[lookupvalue]))
	for index, element := range co2_data[lookupvalue] {
		//log.Print("Index: ", index, ", Element: ", element)
		value, _ := strconv.ParseFloat(element, 64)
		converted[index] = value
	}
	log.Print("start CO2 value of day: ", converted[0])
	return converted
}

//calculate minimum time window for predicted timeframe
//returns the start hour and the endhour of the optimal time window as:
//starttime, endtime
func get_co2_time_window() (int, int) {
	var windows_size = 6
	var current_day = get_current_day_as_float()
	var co2_sum float64 = 100000000
	var startindex int = 0
	for index := 0; index < len(current_day)-windows_size; index++ {
		var co2_sum_new float64 = 0
		for i := index; i < index+windows_size; i++ {
			co2_sum_new = co2_sum_new + current_day[i%len(current_day)]
		}
		if co2_sum_new < co2_sum {
			co2_sum = co2_sum_new
			startindex = index
		}
	}
	return startindex, startindex + windows_size
}

//This method extracts parameters out of the kubernetes server kubectl api
func getCPUUtilization() float64 {
	//block to aquire values
	cmd := exec.Command("kubectl", "describe", "nodes")
	stdout, err := cmd.Output()
	//catch in case the api gets unresponsive some time.
	if err != nil {
		var defaultLimit float64 = 1.0 //default to 100 percent usage, esentially blocking until service comes up again
		log.Print(err.Error())
		return defaultLimit
	}
	//create regex that gets the cpu line
	//regex that does not work because of instruction set :(
	//Allocated resources:(.|\n)*cpu(\s)*(\d)*m(\s)*\(\K(\d)*
	getCpu := regexp.MustCompile("cpu(\\s)*(\\d)*m(\\s)*\\((\\d)*")

	cpuResultConsole := getCpu.FindStringSubmatch(string(stdout))
	cpuResultRelevantString := cpuResultConsole[0]
	//extract the percentage value of the cpu utilization
	cpuResultRelevantString = cpuResultRelevantString[(strings.IndexByte(cpuResultRelevantString, '(') + 1):]
	var cpuLimit float64
	cpuLimit, err = strconv.ParseFloat(cpuResultRelevantString, 64)
	cpuLimit = cpuLimit / 100
	return cpuLimit
}
