import os
import time
import requests
from kubernetes import client, config, watch

# Configuration from Environment Variables (Set via Terraform/K8s Manifests)
S3_ENDPOINT = os.getenv("S3_ENDPOINT", "http://s3mock:9090")
LLM_ENDPOINT = os.getenv("LLM_ENDPOINT", "http://host.minikube.internal:11434/v1")
LLM_MODEL = os.getenv("LLM_MODEL", "llama3")

def get_ai_fix(pod_name, logs):
    """
    Sends logs to the Universal LLM API. 
    Works with Ollama, vLLM, or OpenAI.
    """
    print(f"--- Requesting AI Analysis for {pod_name} ---")
    prompt = f"""
    The following Kubernetes pod just crashed: {pod_name}
    Here are the last 50 lines of logs:
    {logs}
    
    Instruction: Identify the error and provide a 2-step fix.
    """
    
    try:
        response = requests.post(
            f"{LLM_ENDPOINT}/chat/completions",
            json={
                "model": LLM_MODEL,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.2
            },
            timeout=30
        )
        return response.json()['choices'][0]['message']['content']
    except Exception as e:
        return f"Failed to connect to AI: {str(e)}"

def watch_events():
    # Load K8s config (In-cluster if deployed, local if running via proxy)
    try:
        config.load_incluster_config()
    except:
        config.load_kube_config()

    v1 = client.CoreV1Api()
    w = watch.Watch()

    print(f"OWL Agent started. Monitoring cluster for Crashes...")
    
    # Watch for Pod events
    for event in w.stream(v1.list_pod_for_all_namespaces):
        pod = event['object']
        status = pod.status.container_statuses
        
        # Logic: Check if any container is in CrashLoopBackOff
        if status:
            for container in status:
                if container.state.waiting and container.state.waiting.reason == "CrashLoopBackOff":
                    pod_name = pod.metadata.name
                    ns = pod.metadata.namespace
                    
                    print(f"ALERT: {pod_name} in {ns} is crashing!")
                    
                    # 1. Fetch Logs (previous=True captures the log from the crash)
                    try:
                        logs = v1.read_namespaced_pod_log(pod_name, ns, previous=True, tail_lines=50)
                    except:
                        logs = v1.read_namespaced_pod_log(pod_name, ns, tail_lines=50)

                    # 2. Get the AI Diagnostic
                    suggestion = get_ai_fix(pod_name, logs)
                    
                    # 3. Output (In the next step, we add Slack/S3 reporting)
                    print(f"PROPOSED FIX:\n{suggestion}\n")
                    
                    # Sleep briefly to avoid spamming events for the same crash
                    time.sleep(10)

if __name__ == "__main__":
    watch_events()