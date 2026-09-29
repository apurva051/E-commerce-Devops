# ShopSphere Microservices Application Code

An end-to-end microservices application deployed on AWS using Docker, Kubernetes (K3s), Terraform, Jenkins, GitHub Actions, ArgoCD, Helm, Ansible, SonarQube, Prometheus, and Grafana.

## Architecture

```text
Developer
   │
   ▼
GitHub
   │
   ▼
CI/CD ──► SonarQube ──► Docker Build ──► Docker Hub
   │
   ▼
GitOps Repository
   │
   ▼
ArgoCD
   │
   ▼
K3s Cluster
   │
   ├── Frontend
   ├── API Gateway
   ├── Product Service
   ├── Order Service
   ├── User Service
   └── MongoDB
   │
   ▼
AWS ALB
   │
   ▼
Application Users

Monitoring:
K3s ──► Prometheus ──► Grafana ──► Alerts

Infrastructure:
Terraform ──► AWS VPC / Subnets / EC2
Ansible ──► K3s Node Configuration
```

## Tech Stack

* **Cloud:** AWS
* **Infrastructure as Code:** Terraform
* **Containers:** Docker
* **Orchestration:** Kubernetes / K3s
* **CI/CD:** Jenkins, GitHub Actions
* **GitOps:** ArgoCD
* **Configuration Management:** Ansible
* **Packaging:** Helm
* **Code Quality:** SonarQube
* **Monitoring:** Prometheus, Grafana
* **Load Balancing:** AWS Application Load Balancer
* **Application:** FastAPI-based microservices, MongoDB

## Key Implementations

* Provisioned AWS infrastructure using Terraform.
* Built and deployed a multi-node K3s cluster.
* Containerized microservices using Docker.
* Implemented CI/CD pipelines for build, validation, and deployment workflows.
* Used SonarQube for static code analysis.
* Implemented GitOps deployment using ArgoCD.
* Packaged Kubernetes workloads using Helm.
* Used Ansible for Kubernetes node configuration.
* Exposed the frontend through Kubernetes NodePort and an AWS ALB.
* Configured Prometheus and Grafana for cluster monitoring.
* Created Grafana dashboards for CPU, memory, pods, namespaces, and container restarts.
* Configured alerts for infrastructure conditions such as high CPU usage.

## Repositories

* **Application:** `production-microservices-app-code`
* **GitOps:** `ecommerce-gitops`

## Deployment Flow

```text
Code
 ↓
GitHub
 ↓
CI/CD
 ↓
SonarQube + Docker Build
 ↓
Docker Hub
 ↓
GitOps Repository
 ↓
ArgoCD
 ↓
K3s
 ↓
AWS ALB
 ↓
Users
```

## Monitoring Flow

```text
K3s Cluster
    ↓
Prometheus
    ↓
Grafana
    ↓
Dashboards + Alerts
```

## Future Improvements

* HPA and advanced Kubernetes autoscaling
* Centralized logging
* Distributed tracing
* AWS private-subnet architecture
* Automated infrastructure deployment through CI/CD
* Additional security and resilience testing
