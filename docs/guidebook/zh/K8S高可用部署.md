AgentUniverse 提供标准的工作环境镜像，以支持在 Kubernetes (K8S) 集群上容器化部署 AgentUniverse 工程。本指南将指导你如何基于该工作环境镜像，在 K8S 上部署和搭建一个高可用集群。

## 1. 资源配置

首先，配置必要的资源文件。使用以下 YAML 配置文件定义所需的 Namespace、Deployment 和 Service 资源。

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
        image: reg.docker.alibaba-inc.com/agentframeworkbiz/agentuniverse:0.0.4_20240507154953
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