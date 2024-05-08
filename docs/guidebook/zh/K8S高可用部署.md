AgentUniverse 提供标准的工作环境镜像，以支持在 Kubernetes (K8S) 集群上容器化部署 AgentUniverse 工程。本指南将指导你如何基于该工作环境镜像，在 K8S 上部署和搭建一个高可用集群。

## 1. 资源配置

首先，配置必要的资源文件。使用以下 YAML 配置文件定义所需的 Namespace、Deployment 和 Service 资源。

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

## 2. 构建资源

创建并应用上述配置文件：

```
kubectl apply -f agentuniverse.yaml
```

## 3. 验证资源

确认所有资源是否正确部署：

```
kubectl get all -n agent-namespace
```

![img](https://intranetproxy.alipay.com/skylark/lark/0/2024/png/11756835/1715074945141-c27ec861-3977-4a66-b418-be678da692fe.png)

## 4. 从集群内部访问 AgentUniverse 服务

要从集群内部访问 AgentUniverse 服务，请使用以下命令行示例：

```
kubectl exec -it [正确的Pod名称] -n agent-namespace -- curl http://agentuniverse-service:9999
```

### 4.1 示例

#### 4.1.1 联通性测试

```
kubectl exec -it agentuniverse-deployment-55cfd778d-g7d9d -n agent-namespace -- curl http://agentuniverse-service:9999/echo
```

![img](https://intranetproxy.alipay.com/skylark/lark/0/2024/png/11756835/1715075060982-58821843-c944-48b9-bfbc-0e7548eb0fc1.png)

#### 4.1.2 问答测试

```
kubectl exec -it agentuniverse-deployment-55cfd778d-g7d9d -n agent-namespace -- curl -X POST -H "Content-Type: application/json" -d '{"service_id":"demo_service","params":{"input":"(18+3-5)/2*4=?"}}' http://agentuniverse-service:9999/service_run
```

![img](https://intranetproxy.alipay.com/skylark/lark/0/2024/png/11756835/1715075202571-b76a62fa-46cf-4212-94e1-ffb7ae7aa942.png)