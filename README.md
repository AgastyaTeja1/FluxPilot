# FluxPilot LLM Pipeline

An end-to-end, production-grade system to fine-tune, orchestrate, track, and serve a domain-specific Granite LLM.  
Designed for security, observability, configuration-driven deployments across AWS, GCP, Docker-Compose, Kubernetes, and Helm.

---

## Key Features

- **Training & Tracking**  
  - Fine-tune the Granite LLM via Hugging Face + PyTorch  
  - MLflow autologging, experiment tracking & model registry  
  - Configurable hyperparameters via central `config/config.yaml` & environment variables  

- **Orchestration**  
  - Prefect flow with retries, logging, and MLflow integration  
  - CLI entrypoint for scheduled or ad-hoc runs  

- **Inference Service**  
  - FastAPI + Gunicorn for high-concurrency serving  
  - API key / AWS Secrets Manager authentication  
  - Structured JSON logging (python-json-logger)  
  - Prometheus metrics endpoint (`/metrics`)  
  - OpenTelemetry tracing with OTLP exporter  

- **Configuration Management**  
  - Single `config/config.yaml` with `default` + `dev`/`staging`/`prod` profiles  
  - Pydantic-based loaders in `training/config.py`, `serving/config.py`, `orchestrator/config.py`  

- **Security & Secrets**  
  - API keys stored & rotated in AWS Secrets Manager  
  - Fallback to `API_KEYS` env var  
  - No secrets in code; `.env.example` provided  

- **Testing & QA**  
  - Unit tests (pytest) for training, serving, orchestrator  
  - Integration test spins up Docker-Compose and validates `/generate`  
  - Locust load-test script included  

- **Deployment Options**  
  - **Local**: `docker-compose up` (MLflow, training, serving)  
  - **AWS**: Terraform for ECR, IAM roles, CloudWatch + GitHub Actions CI/CD → SageMaker  
  - **GCP**: Artifact Registry + GKE manifests  
  - **Kubernetes**: Vanilla YAML + Helm chart with HPA, Ingress, Secrets  

---

## Repository Layout
  ```bash
  fluxpilot-llm-pipeline/
  ├── config/ # Central config YAML
  │ └── config.yaml
  ├── training/ # Fine-tuning code & deps
  │ ├── config.py
  │ ├── data_loader.py
  │ ├── hf_utils.py
  │ ├── train.py
  │ └── requirements.txt
  ├── serving/ # FastAPI inference service
  │ ├── auth.py
  │ ├── config.py
  │ ├── logging.py
  │ ├── metrics.py
  │ ├── tracing.py
  │ ├── app.py
  │ ├── gunicorn_conf.py
  │ └── requirements.txt
  ├── orchestrator/ # Prefect orchestration & config
  │ ├── config.py
  │ └── flow.py
  ├── tests/ # Unit, integration & load tests
  │ ├── unit/
  │ ├── integration/
  │ └── load/
  ├── k8s/ # Kubernetes manifests
  │ ├── deployment.yaml
  │ ├── service.yaml
  │ ├── hpa.yaml
  │ └── ingress.yaml
  ├── helm/ # Helm chart
  │ └── fluxpilot/
  │ ├── Chart.yaml
  │ ├── values.yaml
  │ └── templates/
  ├── terraform/ # AWS infra provisioning
  ├── .github/workflows/ci-cd.yaml # GitHub Actions CI/CD
  ├── docker/ # Dockerfiles & compose
  ├── .env.example # Example env vars & secrets paths
  ├── README.md
  ```

---

## Prerequisites

- **Docker & Docker-Compose**  
- **Python 3.10+**  
- **Terraform 1.0+**  
- **AWS CLI** (for Terraform & manual tests)  
- **kubectl & Helm** (for k8s/Helm deploy)  

---

## Local Development

1. **Clone & configure**  
   ```bash
   git clone https://github.com/your_org/fluxpilot-llm-pipeline.git
   cd fluxpilot-llm-pipeline
   cp .env.example .env
   # Fill in any local overrides (e.g. BASE_MODEL, API_KEYS)
   ```

2. **Run MLflow & Train**
  ```bash
  docker-compose up -d mlflow
  docker-compose run --rm train
  # MLflow UI: http://localhost:5000
  ```

3. **Serve Model**
  ```bash
  # Copy best checkpoint into serving/model
  mkdir -p serving/model && cp -r outputs/checkpoint-* serving/model/
  docker-compose up -d serve
  # API at http://localhost:8080
  ```

4. **Run Prefect Flow**
  ```bash
  prefect deployment build orchestrator/flow.py:fluxpilot_flow \
    -n "fluxpilot" --apply
  prefect deployment run fluxpilot
  ```

## Testing
  ```bash
  pip install -r training/requirements.txt
  pip install -r serving/requirements.txt pytest locust
  pytest
  locust -f tests/load/locustfile.py --host http://localhost:8080
  ```

##  AWS Deployment

1. **Provision infra**
  ```bash
  cd terraform
  terraform init
  terraform apply -auto-approve
  # Note outputs: ECR repo URL, IAM role ARN, CloudWatch log group
  ```
2. **Set GitHub Secrets**

- AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY,

- AWS_ACCOUNT_ID, AWS_REGION,

- ECR_REPOSITORY, SAGEMAKER_ENDPOINT_NAME,

- SAGEMAKER_EXECUTION_ROLE_ARN, PREFECT_API_TOKEN, etc.

3. **Push to main**

- GitHub Actions will build, test, push Docker → ECR

- Create/update SageMaker model & endpoint

4. **Invoke Endpoint**
  ```bash
  aws sagemaker-runtime invoke-endpoint \
    --endpoint-name fluxpilot-endpoint \
    --body '{"prompt":"Hello"}' \
    --content-type application/json response.json
  cat response.json
  ```

## Kubernetes & Helm
  ```bash
  # Deploy via kubectl
  kubectl apply -f k8s/

  # Or use Helm for parameterized deploy
  helm repo add fluxpilot https://your_org.github.io/helm-charts
  helm install fluxpilot fluxpilot/fluxpilot \
    --set image.repository=<YOUR_REGISTRY>/fluxpilot-serve \
    --set image.tag=latest
  ```

## Observability & Monitoring

- Logs: Structured JSON via /serving/logging.py

- Metrics: Prometheus at /metrics

- Tracing: OTLP exporter via /serving/tracing.py

## Security
- API Key Auth: Header X-API-KEY checked against AWS Secrets Manager

- Secrets: No creds in code; use AWS Secrets Manager / env vars

