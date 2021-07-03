# Cloud Cache System

## Description

This project implements a cloud-based caching system.\
The cache is composed by dynamic number of cloud instances (nodes), all runs the same code in parallel.\
A load balancer is routing the client's requests to one of the system's nodes, which handle and process the request./
There are three client endpoints to this system (**port = 8080**):

  1. `GET /put?str_key=key_value&data=data_value` add *data_value* to *key_value* in the cache.
  2. `GET /get?str_key=key_value` retrieve *key_value* data from the cache.  
  3. `GET /cache` display the system cache state.

The system use an internal HTTP vpc network, for nodes communication and manage the cache.

## Setup

***To run this app you'll need your AWS credentials!***

### Set the Admin Instance Environment

To start this app we need to set the environment on an admin instance that manage the nodes.\
Connect your EC2 instance via SSH and run the following commands in the shell:

``` bash
git clone https://github.com/tomergroisman/cloud-cache.git
cd cloud-cache
source run.sh
```

## Run

The app will start automatically after the `run.sh` script will finish its execution.\
To interact with the app, retrieve your load balancer url endpoint by navigating to:\
`AWS console => EC2 => Load Balancing => Load Balancers => Basic configuration => DNS name`\
Start interacting with the app by making GET requests to the provided endpoints (above).

## Scenarios

We're able to handle, without data loss, the following scenarios:

* Putting and getting data across multiple keys, that will reside in different nodes: as described above using the API endpoints.
* Losing a node and not losing any data: The moment the system recognizes that a lose of a node, it triggers a rearrangement of the data according to the new number of nodes.
* Adding a new node to the system and extending its capacity: exactly the same handling as in the 'losing node' scenario.

## Modifying the System

You can increase the number of nodes by executing
``` bash
source scripts/add_node.sh
```
from the project's root directory.

### Have Fun
