# CO₂ Aware Scheduler for Kubernetes
Centers

This implementation is based on the [scheduler extender example](https://github.com/everpeace/k8s-scheduler-extender-example)

Documentation of [Kubernetes Scheduler Extender](https://github.com/kubernetes/design-proposals-archive/blob/main/scheduling/scheduler_extender.md)


## run benchmark script:
open **Benchmark_scripts** Folder

execute script in [git bash for windows](https://git-scm.com/download/win) by running:

``sh benchmark.sh``


# 1. Deploy scheduler
there are two ways for deploying the scheduler.

Automatically by using a script

Manually by entering all comands one by one in sequence.

**Prequesite for both approaches:**

- Have an Account at https://hub.docker.com/ .
- Create a repository


## 1.1 Automatically deploy project
- open **deployScheduler.sh**
- adapt the **Image** variable 
  - set it to **USERACCOUNT/REPOSITORYNAME**
- open git bash and enter **sh deployScheduler.sh**
- wait until the log of scheduling container is opened automatically

### 1.1.0 Test deployed scheduler
- open **Test Pods** folder
- choose one file and deploy on kubernetes
  - execute **kubectl apply -f FILENAME**
- in Minikube shell execute **minikube dashboard**
- navigate to pods tab and see if deployment is created and if scheduled


## 1.2 Manually deploy project

### 1.2.0 checkout the repo

```shell
$ git clone git@github.com:everpeace/k8s-scheduler-extender-example.git
$ cd k8s-scheduler-extender-example
$ git submodule update --init
```

### 1.2.1. buid a docker image

```
$ IMAGE=YOUR_ORG/YOUR_IMAGE:YOUR_TAG

$ docker build . -t "${IMAGE}"
$ docker push "${IMAGE}"
```

### 1.2.2. deploy `my-scheduler` in `kube-system` namespace
please see ConfigMap in [extender.yaml](extender.yaml) for scheduler policy json which includes scheduler extender config.

```
# bring up the kube-scheduler along with the extender image you've just built
$ sed 's/a\/b:c/'$(echo "${IMAGE}" | sed 's/\//\\\//')'/' extender.yaml | kubectl apply -f -
```

For ease of observation, start streaming logs from the extender:

```console
$ kubectl -n kube-system logs deploy/my-scheduler -c my-scheduler-extender-ctr -f
[  warn ] 2018/11/07 08:41:40 main.go:84: LOG_LEVEL="" is empty or invalid, fallling back to "INFO".
[  info ] 2018/11/07 08:41:40 main.go:98: Log level was set to INFO
[  info ] 2018/11/07 08:41:40 main.go:116: server starting on the port :80
```

Open up an another termianl and proceed.

### 1.2.3. schedule test pod

you will see pods in **Test Pods** folder will be scheduled by `my-scheduler`.

```
$ kubectl create -f TESTPODNAME.yaml

$ kubectl describe pod NAME_SPECIFIED_IN_POD_DESCRIPTION
Name:         test-pod
...
Events:
  Type    Reason                 Age   From               Message
  ----    ------                 ----  ----               -------
  Normal  Scheduled              25s   my-scheduler       Successfully assigned test-pod to minikube
  Normal  SuccessfulMountVolume  25s   kubelet, minikube  MountVolume.SetUp succeeded for volume "default-token-wrk5s"
  Normal  Pulling                24s   kubelet, minikube  pulling image "nginx"
  Normal  Pulled                 8s    kubelet, minikube  Successfully pulled image "nginx"
  Normal  Created                8s    kubelet, minikube  Created container
  Normal  Started                8s    kubelet, minikube  Started container
```


## License

```
Copyright 2018 Shingo Omura <https://github.com/everpeace>

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

   http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
```
