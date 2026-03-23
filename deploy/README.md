> ### 🚀 Deployment Guide
> #### Prerequisites
> 1. A Kubernetes Cluster (Minikube/EKS/GKE).
> 2. An **OpenRouter API Key**.
>
> #### Required Environment Variables
> | Variable | Description | Default |
> | :--- | :--- | :--- |
> | `OPENROUTER_API_KEY` | Your Llama-3 API Key (Stored in K8s Secret) | **Required** |
> | `LLM_MODEL` | The model ID from OpenRouter | `meta-llama/llama-3-8b-instruct` |
> | `S3_ENDPOINT` | Endpoint for diagnostic storage | `http://s3mock:9090` |
>
> #### Step 1: Create the Secret
> ```bash
> kubectl create secret generic owl-secrets --from-literal=OPENROUTER_API_KEY='your_key'
> ```
> #### Step 2: Deploy Owl
> ```bash
> kubectl apply -f agent-rbac.yaml
> kubectl apply -f agent-deploy.yaml
> ```

---
