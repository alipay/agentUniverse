# K8S Deployment Guide for AgentUniverse

AgentUniverse offers standardized working environment images to support the containerized deployment of the AgentUniverse project on Kubernetes (K8S) clusters. This guide will instruct you on how to deploy and establish a highly available cluster in K8S using this working environment image.

## 1. Resource Configuration

First, configure the necessary resource files. Use the following YAML configuration file to define the required Namespace, Deployment, and Service resources.

```
apiVersion: v1
kind: Namespace
metadata:
  name: agent-namespace

---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: agentuniverse-deployment
  namespace: agent-namespace
  labels:
    app: agentuniverse
spec:
  replicas: 3
  selector:
    matchLabels:
      app: agentuniverse
  template:
    metadata:
      labels:
        app: agentuniverse
    spec:
      containers:
      - name: agentuniverse-container
        image: registry.cn-hangzhou.aliyuncs.com/agent_universe/agent_universe:0.0.5_centos8_beta
        ports:
        - containerPort: 8888
        command: ["/bin/bash", "-c"]
        args: ["git clone git@code.alipay.com:finresearchsys/agentUniverse-sample-app-internal.git; mv agentUniverse-sample-app-internal/sample_standard_app /usr/local/etc/workspace/project; /bin/bash --login /usr/local/etc/workspace/shell/start.sh"]
        env:
        - name: OPENAI_API_KEY
          value: "XXX"

---
apiVersion: v1
kind: Service
metadata:
  name: agentuniverse-service
  namespace: agent-namespace
spec:
  selector:
    app: agentuniverse
  ports:
  - protocol: TCP
    port: 9999
    targetPort: 8888
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