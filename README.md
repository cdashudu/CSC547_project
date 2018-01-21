# Code

clientmonitor.py  collects information about docker container statistics from the nodes (ip mentioned in the webserverips list inside the file)

server.py sends the container statistics to the swarm master node.

# Presentation

Presentation slide Deck 

https://docs.google.com/presentation/d/1H9INK3F7KEyIIEjWz130lOGO8EKkBK7WuoDxZ4mrblk/edit#slide=id.p

# Writeup

## Docker Swarm


### Introduction

The cluster management and orchestration features embedded in the Docker Engine are built using swarmkit. Swarmkit is a separate project which implements Docker’s orchestration layer and is used directly within Docker.

A swarm consists of multiple Docker hosts which run in swarm mode and act as managers (to manage membership and delegation) and workers (which run swarm services). A given Docker host can be a manager, a worker, or perform both roles. When you create a service, you define its optimal state (number of replicas, network and storage resources available to it, ports the service exposes to the outside world, and more). Docker works to maintain that desired state. For instance, if a worker node becomes unavailable, Docker schedules that node’s tasks on other nodes. A task is a running container which is part of a swarm service and managed by a swarm manager, as opposed to a standalone container.

A simple architechture of a docker swarm is shown below

<img width="671" alt="screen shot 2017-11-19 at 6 46 25 pm" src="https://user-images.githubusercontent.com/23710533/33034683-98bc2870-cdf6-11e7-9578-7ff408c2446f.png">


### Advantages

There are several features offered by docker swarm. Few of them are mentioned below

Cluster management integrated with Docker Engine

We can deploy both kinds of nodes, managers and workers, using the Docker Engine, no additional installation software required. 

Scaling

For each service, you can declare the number of tasks you want to run. When you scale up or down, the swarm manager automatically adapts by adding or removing tasks to maintain the desired state.

Service discovery

Swarm manager nodes assign each service in the swarm a unique DNS name and load balances running containers. You can query every container running in the swarm through a DNS server embedded in the swarm.

Rolling updates

At rollout time you can apply service updates to nodes incrementally. The swarm manager lets you control the delay between service deployment to different sets of nodes. If anything goes wrong, you can roll-back a task to a previous version of the service.
Load balancing
You can expose the ports for services to an external load balancer. Internally, the swarm lets you specify how to distribute service containers between nodes.

### Dynamic Scaling

The scaling feature offered by docker swarm can be utilised and a number of applications can be developed for acheiving dynamic scaling of container in case of heavy traffic.
For example as we have shown in the demo, we can develop a python client which resides in each of the docker swarm node, reporting the docker container statistics to the swarm master. Depending on the statistics for example CPU utilisation on each container , the swarm master can take decisions on the scaling the application.

A simple flow diagram and a design is show below.

<img width="609" alt="screen shot 2017-11-19 at 6 38 00 pm" src="https://user-images.githubusercontent.com/23710533/33033977-65b48a0a-cdf4-11e7-876f-1fb966c83b81.png">


<img width="511" alt="screen shot 2017-11-19 at 6 48 25 pm" src="https://user-images.githubusercontent.com/23710533/33033970-61547d6c-cdf4-11e7-9b12-ba0d113f60f6.png">



### Monitoring

We have anaylsed two different tools for monitring the container statistics on each node in the cluster. one of them is manomarks visualzer and the other cAdvisor from google.


cAdvisor

cAdvisor (Container Advisor) provides container users an understanding of the resource usage and performance characteristics of their running containers. It is a running daemon that collects, aggregates, processes, and exports information about running containers. Specifically, for each container it keeps resource isolation parameters, historical resource usage, histograms of complete historical resource usage and network statistics. This data is exported by container and machine-wide.

Visualiser

Each node in the swarm will show all tasks running on it. When a service goes down it'll be removed. When a node goes down it won't, instead the circle at the top will turn red to indicate it went down. Tasks will be removed. Occasionally the Remote API will return incomplete data, for instance the node can be missing a name. The next time info for that node is pulled, the name will update.

### Setup and Instructions

* Intiliasing docker swarm to be run on the node which would be swarm master

	docker swarm init --advertise-addr=<ip address of the swarm master node>
* For a node to join the swarm run the following command 

	docker swarm join-token manager/worker
	
* Dynamic Scaling
	
	* push server.py to all worker nodes in the swarm cluster and run python server.py  (make sure the docker client for python is installed pip install docker)

	* push clientmonitor.py to the swarm master and run python clientmonitor.py  (edit the python file to include the worker node ip addresses)

	* run a sample web application in the docker swarm as a service

		docker service create --name cloudapp --constraint=node.role!=manager --publish 8080:8080 --reserve-memory="256m" --limit-memory="256m" --reserve-cpu="0.25" --limit-cpu="0.25" cddashud/tomcat-sampleapp /usr/local/tomcat/bin/catalina.sh run 


	* stress testing for the web application

		install apache benchmark for stress testing and run the following command 
		
		ab -n 100000 -c 1000 http://<ip address>:8080/shoppingcart/

* Monitoring tools

	*The manomarks visualiser
		
		docker service create --name visualizer --publish 9000:8080 --constraint=node.role==manager --mount=type=bind,src=/var/run/docker.sock,dst=/var/run/docker.sock dockersamples/visualizer

	* cAdvisor 
		
		docker service create --mode=global --name cadvisor --publish 8000:8080 \
		  --mount type=bind,source=/,target=/rootfs,readonly=true \
		  --mount type=bind,source=/var/run,target=/var/run,readonly=false \
		  --mount type=bind,source=/sys,target=/sys,readonly=true \
		  --mount type=bind,source=/var/lib/docker/,target=/var/lib/docker,readonly=true \
		  google/cadvisor:latest 
		  
