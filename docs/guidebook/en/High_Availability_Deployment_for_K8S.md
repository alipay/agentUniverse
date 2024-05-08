# K8S Deployment Guide for AgentUniverse

AgentUniverse offers standardized working environment images to support the containerized deployment of the AgentUniverse project on Kubernetes (K8S) clusters. This guide will instruct you on how to deploy and establish a highly available cluster in K8S using this working environment image.

## 1. Resource Configuration

First, configure the necessary resource files. Use the following YAML configuration file to define the required Namespace, Deployment, and Service resources.

```
1apiVersion: v1
2kind: Namespace
3metadata:
4  name: agent-namespace
5---
6apiVersion: apps/v1
7kind: Deployment
8metadata:
9  name: agentuniverse-deployment
10  namespace: agent-namespace
11  labels:
12    app: agentuniverse
13spec:
14  replicas: 3
15  selector:
16    matchLabels:
17      app: agentuniverse
18  template:
19    metadata:
20      labels:
21        app: agentuniverse
22    spec:
23      containers:
24      - name: agentuniverse-container
25        image: reg.docker.alibaba-inc.com/agentframeworkbiz/agentuniverse:0.0.4_20240507154953
26        ports:
27        - containerPort: 8888
28        command: ["/bin/bash", "-c"]
29        args: ["git clone git@code.alipay.com:finresearchsys/agentUniverse-sample-app-internal.git; mv agentUniverse-sample-app-internal/sample_standard_app /usr/local/etc/workspace/project; /bin/bash --login /usr/local/etc/workspace/shell/start.sh"]
30        env:
31        - name: OPENAI_API_KEY
32          value: "XXX"
33---
34apiVersion: v1
35kind: Service
36metadata:
37  name: agentuniverse-service
38  namespace: agent-namespace
39spec:
40  selector:
41    app: agentuniverse
42  ports:
43  - protocol: TCP
44    port: 9999
45    targetPort: 8888
```

## 2. Build Resources

Create and apply the configuration file:

```
kubectl apply -f agentuniverse.yaml
```

## 3. Verify the Resources

Ensure all resources are correctly deployed:

```
kubectl get all -n agent-namespace
```

![img](https://intranetproxy.alipay.com/skylark/lark/0/2024/png/11756835/1715074945141-c27ec861-3977-4a66-b418-be678da692fe.png)

## 4. Accessing AgentUniverse Service from Inside the Cluster

To access the AgentUniverse service from inside the cluster, use the following command line example:

```
kubectl exec -it [correct Pod name] -n agent-namespace -- curl http://agentuniverse-service:9999
```

### 4.1 Example

#### 4.1.1 Connectivity Test

```
kubectl exec -it agentuniverse-deployment-55cfd778d-g7d9d -n agent-namespace -- curl http://agentuniverse-service:9999/echo
```

![img](https://intranetproxy.alipay.com/skylark/lark/0/2024/png/11756835/1715075060982-58821843-c944-48b9-bfbc-0e7548eb0fc1.png)

#### 4.1.2 Q&A Test

```
kubectl exec -it agentuniverse-deployment-55cfd778d-g7d9d -n agent-namespace -- curl -X POST -H "Content-Type: application/json" -d '{"service_id":"demo_service","params":{"input":"(18+3-5)/2*4=?"}}' http://agentuniverse-service:9999/service_run
```

![img](https://intranetproxy.alipay.com/skylark/lark/0/2024/png/11756835/1715075202571-b76a62fa-46cf-4212-94e1-ffb7ae7aa942.png)