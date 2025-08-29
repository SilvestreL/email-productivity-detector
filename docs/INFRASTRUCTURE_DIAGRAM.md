# 🏗️ Diagrama de Infraestrutura - Email Productivity Classifier

## 📊 **Arquitetura Completa do Sistema**

### **Diagrama Principal (Mermaid)**

```mermaid
graph TB
    %% Usuários e Clientes
    User[👤 Usuário Final]
    Client[💻 Cliente Web]
    Mobile[📱 App Mobile]
    API_Client[🔗 Cliente API]

    %% Load Balancer e Gateway
    LB[🌐 Load Balancer<br/>Nginx/HAProxy]
    Gateway[🚪 API Gateway<br/>Kong/Traefik]

    %% Frontend e Interface
    HTML[📄 Interface HTML<br/>index.html]
    Streamlit[🤖 Streamlit App<br/>Porta 8501]

    %% Backend e API
    API[🔗 FastAPI<br/>Porta 8000]
    ML_Model[🤖 Modelo ML<br/>98.39% Acurácia]

    %% Processamento
    File_Processor[📄 Processador<br/>de Arquivos]
    Response_Generator[💬 Gerador<br/>de Respostas]

    %% Storage
    Model_Storage[(💾 Storage<br/>Modelos ML)]
    Data_Storage[(📊 Storage<br/>Dados)]
    Log_Storage[(📋 Storage<br/>Logs)]

    %% Containers e Orquestração
    Docker[🐳 Docker<br/>Container]
    K8s[☸️ Kubernetes<br/>Cluster]

    %% Cloud Services
    Cloud[☁️ Cloud Platform<br/>AWS/GCP/Azure]
    Registry[📦 Container Registry<br/>ECR/GCR/ACR]

    %% Monitoramento
    Monitoring[📊 Monitoramento<br/>Prometheus/Grafana]
    Logging[📋 Logging<br/>ELK Stack]
    Alerting[🚨 Alertas<br/>PagerDuty/Slack]

    %% Conexões - Usuários
    User --> Client
    User --> Mobile
    User --> API_Client

    %% Conexões - Load Balancer
    Client --> LB
    Mobile --> LB
    API_Client --> Gateway

    %% Conexões - Frontend
    LB --> HTML
    LB --> Streamlit

    %% Conexões - Backend
    Gateway --> API
    Streamlit --> API

    %% Conexões - Processamento
    API --> ML_Model
    API --> File_Processor
    API --> Response_Generator

    %% Conexões - Storage
    ML_Model --> Model_Storage
    File_Processor --> Data_Storage
    API --> Log_Storage

    %% Conexões - Containers
    HTML --> Docker
    Streamlit --> Docker
    API --> Docker

    %% Conexões - Orquestração
    Docker --> K8s

    %% Conexões - Cloud
    K8s --> Cloud
    Docker --> Registry

    %% Conexões - Monitoramento
    API --> Monitoring
    API --> Logging
    Monitoring --> Alerting

    %% Estilos
    classDef userClass fill:#e1f5fe
    classDef frontendClass fill:#f3e5f5
    classDef backendClass fill:#e8f5e8
    classDef storageClass fill:#fff3e0
    classDef cloudClass fill:#fce4ec
    classDef monitoringClass fill:#f1f8e9

    class User,Client,Mobile,API_Client userClass
    class HTML,Streamlit frontendClass
    class API,ML_Model,File_Processor,Response_Generator backendClass
    class Model_Storage,Data_Storage,Log_Storage storageClass
    class Cloud,Registry cloudClass
    class Monitoring,Logging,Alerting monitoringClass
```

---

## 🔄 **Fluxo de Dados Detalhado**

### **Diagrama de Fluxo (Mermaid)**

```mermaid
sequenceDiagram
    participant U as 👤 Usuário
    participant LB as 🌐 Load Balancer
    participant S as 🤖 Streamlit
    participant API as 🔗 FastAPI
    participant ML as 🤖 Modelo ML
    participant RG as 💬 Gerador Respostas
    participant FP as 📄 Processador Arquivos
    participant DB as 💾 Storage

    Note over U,DB: Fluxo de Classificação de Email

    U->>LB: 1. Acessa aplicação
    LB->>S: 2. Redireciona para Streamlit

    alt Upload de Arquivo
        U->>S: 3a. Faz upload de arquivo
        S->>FP: 4a. Processa arquivo
        FP->>API: 5a. Envia texto extraído
    else Texto Direto
        U->>S: 3b. Insere texto
        S->>API: 4b. Envia texto
    end

    API->>ML: 6. Classifica email
    ML->>API: 7. Retorna resultado

    API->>RG: 8. Gera resposta automática
    RG->>API: 9. Retorna resposta

    API->>DB: 10. Salva log
    API->>S: 11. Retorna resultado completo
    S->>U: 12. Exibe resultado

    Note over U,DB: Fluxo via API REST

    U->>API: 13. Requisição REST
    API->>ML: 14. Classifica
    ML->>API: 15. Resultado
    API->>U: 16. Resposta JSON
```

---

## 🐳 **Arquitetura Docker**

### **Diagrama de Containers (Mermaid)**

```mermaid
graph LR
    %% Containers
    subgraph "🐳 Docker Containers"
        Nginx[🌐 Nginx<br/>Porta 80]
        Streamlit[🤖 Streamlit<br/>Porta 8501]
        API[🔗 FastAPI<br/>Porta 8000]
        ML[🤖 ML Model<br/>Joblib]
    end

    %% Volumes
    subgraph "💾 Volumes"
        Model_Vol[(Model Data)]
        Log_Vol[(Logs)]
        Config_Vol[(Config)]
    end

    %% Networks
    subgraph "🌐 Networks"
        Frontend_Net[Frontend Network]
        Backend_Net[Backend Network]
    end

    %% Conexões
    Nginx --> Streamlit
    Nginx --> API
    Streamlit --> ML
    API --> ML

    %% Volumes
    ML --> Model_Vol
    API --> Log_Vol
    Nginx --> Config_Vol

    %% Networks
    Nginx --> Frontend_Net
    Streamlit --> Backend_Net
    API --> Backend_Net

    %% Estilos
    classDef containerClass fill:#e3f2fd
    classDef volumeClass fill:#f3e5f5
    classDef networkClass fill:#e8f5e8

    class Nginx,Streamlit,API,ML containerClass
    class Model_Vol,Log_Vol,Config_Vol volumeClass
    class Frontend_Net,Backend_Net networkClass
```

---

## ☁️ **Arquitetura Cloud**

### **Diagrama Multi-Cloud (Mermaid)**

```mermaid
graph TB
    %% Usuários
    Users[👥 Usuários Globais]

    %% CDN
    CDN[🌍 CDN<br/>CloudFront/Cloud CDN]

    %% Clouds
    subgraph "☁️ AWS"
        ALB[AWS ALB]
        ECS[ECS Cluster]
        RDS[RDS Database]
        S3[S3 Storage]
        CloudWatch[CloudWatch]
    end

    subgraph "☁️ Google Cloud"
        GCLB[Google Cloud LB]
        GCR[Cloud Run]
        Firestore[Firestore]
        GCS[Cloud Storage]
        Stackdriver[Stackdriver]
    end

    subgraph "☁️ Azure"
        ALB_Azure[Azure LB]
        ACI[Container Instances]
        CosmosDB[Cosmos DB]
        BlobStorage[Blob Storage]
        Monitor[Azure Monitor]
    end

    %% Conexões
    Users --> CDN
    CDN --> ALB
    CDN --> GCLB
    CDN --> ALB_Azure

    ALB --> ECS
    GCLB --> GCR
    ALB_Azure --> ACI

    ECS --> RDS
    ECS --> S3
    GCR --> Firestore
    GCR --> GCS
    ACI --> CosmosDB
    ACI --> BlobStorage

    ECS --> CloudWatch
    GCR --> Stackdriver
    ACI --> Monitor

    %% Estilos
    classDef userClass fill:#e1f5fe
    classDef cdnClass fill:#fff3e0
    classDef awsClass fill:#ffebee
    classDef gcpClass fill:#e8f5e8
    classDef azureClass fill:#e3f2fd

    class Users userClass
    class CDN cdnClass
    class ALB,ECS,RDS,S3,CloudWatch awsClass
    class GCLB,GCR,Firestore,GCS,Stackdriver gcpClass
    class ALB_Azure,ACI,CosmosDB,BlobStorage,Monitor azureClass
```

---

## 📊 **Monitoramento e Observabilidade**

### **Diagrama de Monitoramento (Mermaid)**

```mermaid
graph TB
    %% Aplicação
    App[🤖 Email Classifier App]

    %% Métricas
    subgraph "📊 Métricas"
        Prometheus[Prometheus]
        Grafana[Grafana Dashboard]
        Metrics[Custom Metrics]
    end

    %% Logs
    subgraph "📋 Logs"
        Fluentd[Fluentd]
        Elasticsearch[Elasticsearch]
        Kibana[Kibana]
    end

    %% Traces
    subgraph "🔍 Traces"
        Jaeger[Jaeger]
        Zipkin[Zipkin]
    end

    %% Alertas
    subgraph "🚨 Alertas"
        AlertManager[AlertManager]
        PagerDuty[PagerDuty]
        Slack[Slack]
        Email[Email]
    end

    %% Conexões
    App --> Prometheus
    App --> Fluentd
    App --> Jaeger

    Prometheus --> Grafana
    Prometheus --> Metrics
    Prometheus --> AlertManager

    Fluentd --> Elasticsearch
    Elasticsearch --> Kibana

    Jaeger --> Zipkin

    AlertManager --> PagerDuty
    AlertManager --> Slack
    AlertManager --> Email

    %% Estilos
    classDef appClass fill:#e8f5e8
    classDef metricsClass fill:#e3f2fd
    classDef logsClass fill:#fff3e0
    classDef tracesClass fill:#f3e5f5
    classDef alertsClass fill:#ffebee

    class App appClass
    class Prometheus,Grafana,Metrics metricsClass
    class Fluentd,Elasticsearch,Kibana logsClass
    class Jaeger,Zipkin tracesClass
    class AlertManager,PagerDuty,Slack,Email alertsClass
```

---

## 🔒 **Segurança e Compliance**

### **Diagrama de Segurança (Mermaid)**

```mermaid
graph TB
    %% Ameaças
    Threats[🚨 Ameaças Externas]

    %% Camadas de Segurança
    subgraph "🛡️ Camadas de Segurança"
        WAF[WAF<br/>Web Application Firewall]
        DDoS[DDoS Protection]
        SSL[SSL/TLS<br/>Encryption]
        Auth[Authentication<br/>& Authorization]
        Network[Network<br/>Security]
        Container[Container<br/>Security]
        Data[Data<br/>Encryption]
    end

    %% Componentes
    subgraph "🔐 Componentes Seguros"
        API_Gateway[API Gateway<br/>with Auth]
        Secure_App[Secure Application]
        Secure_DB[Secure Database]
        Backup[Encrypted Backup]
    end

    %% Conexões
    Threats --> WAF
    WAF --> DDoS
    DDoS --> SSL
    SSL --> Auth
    Auth --> Network
    Network --> Container
    Container --> Data

    Data --> API_Gateway
    API_Gateway --> Secure_App
    Secure_App --> Secure_DB
    Secure_DB --> Backup

    %% Estilos
    classDef threatClass fill:#ffebee
    classDef securityClass fill:#e8f5e8
    classDef componentClass fill:#e3f2fd

    class Threats threatClass
    class WAF,DDoS,SSL,Auth,Network,Container,Data securityClass
    class API_Gateway,Secure_App,Secure_DB,Backup componentClass
```

---

## 📈 **Escalabilidade e Performance**

### **Diagrama de Escalabilidade (Mermaid)**

```mermaid
graph TB
    %% Load Balancer
    LB[🌐 Load Balancer]

    %% Auto Scaling Groups
    subgraph "📈 Auto Scaling Groups"
        ASG1[ASG 1<br/>Min: 2, Max: 10]
        ASG2[ASG 2<br/>Min: 2, Max: 10]
        ASG3[ASG 3<br/>Min: 2, Max: 10]
    end

    %% Instâncias
    subgraph "🖥️ Instâncias"
        Instance1[Instance 1<br/>CPU: 2, RAM: 4GB]
        Instance2[Instance 2<br/>CPU: 2, RAM: 4GB]
        Instance3[Instance 3<br/>CPU: 2, RAM: 4GB]
        Instance4[Instance 4<br/>CPU: 2, RAM: 4GB]
        Instance5[Instance 5<br/>CPU: 2, RAM: 4GB]
        Instance6[Instance 6<br/>CPU: 2, RAM: 4GB]
    end

    %% Cache
    subgraph "⚡ Cache Layer"
        Redis[Redis Cluster]
        CDN[CDN Cache]
    end

    %% Database
    subgraph "💾 Database"
        Primary[Primary DB]
        Replica1[Read Replica 1]
        Replica2[Read Replica 2]
    end

    %% Conexões
    LB --> ASG1
    LB --> ASG2
    LB --> ASG3

    ASG1 --> Instance1
    ASG1 --> Instance2
    ASG2 --> Instance3
    ASG2 --> Instance4
    ASG3 --> Instance5
    ASG3 --> Instance6

    Instance1 --> Redis
    Instance2 --> Redis
    Instance3 --> Redis
    Instance4 --> Redis
    Instance5 --> Redis
    Instance6 --> Redis

    LB --> CDN

    Instance1 --> Primary
    Instance2 --> Primary
    Instance3 --> Replica1
    Instance4 --> Replica1
    Instance5 --> Replica2
    Instance6 --> Replica2

    %% Estilos
    classDef lbClass fill:#e3f2fd
    classDef asgClass fill:#e8f5e8
    classDef instanceClass fill:#fff3e0
    classDef cacheClass fill:#f3e5f5
    classDef dbClass fill:#ffebee

    class LB lbClass
    class ASG1,ASG2,ASG3 asgClass
    class Instance1,Instance2,Instance3,Instance4,Instance5,Instance6 instanceClass
    class Redis,CDN cacheClass
    class Primary,Replica1,Replica2 dbClass
```

---

## 🎯 **Resumo da Arquitetura**

### **Componentes Principais**

1. **🌐 Frontend**

   - Interface HTML responsiva
   - Aplicação Streamlit
   - Load Balancer (Nginx)

2. **🔗 Backend**

   - API REST (FastAPI)
   - Modelo de Machine Learning
   - Processador de arquivos
   - Gerador de respostas

3. **🐳 Containerização**

   - Docker containers
   - Docker Compose
   - Kubernetes (opcional)

4. **☁️ Cloud**

   - Multi-cloud support
   - Auto-scaling
   - Load balancing

5. **📊 Monitoramento**

   - Métricas (Prometheus/Grafana)
   - Logs (ELK Stack)
   - Traces (Jaeger)
   - Alertas

6. **🔒 Segurança**
   - WAF
   - SSL/TLS
   - Authentication
   - Data encryption

### **Especificações Técnicas**

- **Performance**: 98.39% acurácia, < 10ms latência
- **Escalabilidade**: Auto-scaling de 2 a 10 instâncias
- **Disponibilidade**: 99.9% uptime
- **Segurança**: Múltiplas camadas de proteção
- **Monitoramento**: Observabilidade completa

---

**🏗️ Arquitetura completa e escalável para produção!**
