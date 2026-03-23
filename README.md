> # 🦉 OWL: Autonomous K8s Diagnostic Agent
> **OWL (Observe, Watch, Learn)** is an AI-driven Kubernetes controller that automates root-cause analysis for container failures.
>
> ### ✨ Features
> * **Real-time Monitoring:** Watches for `CrashLoopBackOff` events across all namespaces.
> * **Contextual Inference:** Automatically extracts logs from failed containers and uses **Llama-3 (via OpenRouter)** to suggest precise fixes.
> * **Zero-Cost Simulation:** Integrated with **S3Mock** and **LocalStack** for air-gapped testing.
>
> ### 🛠️ Quick Start
> 1. **Setup Mocks:** `kubectl apply -f utilities/s3mock.yaml`
> 2. **Configure Secrets:** (Refer to `/deploy` docs)
> 3. **Launch Agent:** `kubectl apply -f deploy/`
> 4. **Trigger a Crash:** `kubectl apply -f utilities/buggy-app.yaml`
>
> ### 🛡️ Security
> * **RBAC:** Operates under a least-privilege ServiceAccount.
> * **Secrets:** Uses K8s Secrets for API keys; no hardcoded credentials.