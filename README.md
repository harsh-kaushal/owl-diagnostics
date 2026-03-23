# 🦉 OWL: Autonomous K8s Diagnostic Agent
**OWL (Observe, Watch, Learn)** is an AI-driven Kubernetes controller that automates root-cause analysis for container failures.

### ✨ Features
* **Real-time Monitoring:** Watches for `CrashLoopBackOff` events across all namespaces.
* **Contextual Inference:** Automatically extracts logs from failed containers and uses **Llama-3 (via OpenRouter)** to suggest precise fixes.
* **Zero-Cost Simulation:** Integrated with **S3Mock** and **LocalStack** for air-gapped testing.

### 🛠️ Quick Start
Deploy the entire stack (Mocks, Secrets, and Agent) with a single command:

1. **Build the Agent:** `make build`
2. **Deploy the Stack:** `make setup KEY='your_openrouter_api_key'`
3. **Trigger a Crash:** `make test`

Watch the agent's logic in real-time:
`kubectl logs -f deployment/owl-diagnostics-agent`

### 🛡️ Security
* **RBAC:** Operates under a least-privilege ServiceAccount.
* **Secrets:** Uses K8s Secrets for API keys; no hardcoded credentials.

## 💡 Example Diagnostic Output
![Alt text](images/Output.png?raw=true)