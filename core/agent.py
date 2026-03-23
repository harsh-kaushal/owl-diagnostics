import os
import time
import requests
from kubernetes import client, config, watch

# Configuration
LLM_ENDPOINT = os.getenv("LLM_ENDPOINT", "https://openrouter.ai/api/v1")
LLM_API_KEY = os.getenv("OPENROUTER_API_KEY")
LLM_MODEL = os.getenv("LLM_MODEL", "meta-llama/llama-3-8b-instruct")

def get_ai_fix(pod_name, logs):
    """Universal LLM Client for OpenRouter/OpenAI API"""
    headers = {
        "Authorization": f"Bearer {LLM_API_KEY}",
        "HTTP-Referer": "https://github.com/harsh-kaushal/owl-diagnostics",
        "Content-Type": "application/json"
    }
    
    prompt = f"Identify the error in these K8s logs for pod {pod_name} and provide a concise 2-step fix:\n{logs}"
    
    try:
        response = requests.post(
            f"{LLM_ENDPOINT}/chat/completions",
            headers=headers,
            json={
                "model": LLM_MODEL,
                "messages": [{"role": "user", "content": prompt}]
            },
            timeout=15
        )
        response.raise_for_status() # Check for HTTP errors
        data = response.json()
        return data['choices'][0]['message']['content']
    except Exception as e:
        return f"AI Diagnostic failed: {str(e)}"

def watch_events():
    # Service Account Auth logic
    try:
        config.load_incluster_config()
    except config.ConfigException:
        config.load_kube_config()

    v1 = client.CoreV1Api()
    w = watch.Watch()

    print(f"🦉 OWL Agent started. Monitoring cluster...")
    
    # We use a set to avoid spamming the same crash multiple times in one loop
    processed_pods = set()

    for event in w.stream(v1.list_pod_for_all_namespaces):
        pod = event['object']
        pod_id = f"{pod.metadata.namespace}/{pod.metadata.name}"
        
        # Check if pod is in CrashLoopBackOff
        status = pod.status.container_statuses
        if status and any(s.state.waiting and s.state.waiting.reason == 'CrashLoopBackOff' for s in status):
            
            if pod_id in processed_pods:
                continue
                
            print(f"Crash detected: {pod_id}")
            
            # Extract Logs
            try:
                # Try getting logs from the previous failed instance first
                logs = v1.read_namespaced_pod_log(
                    pod.metadata.name, 
                    pod.metadata.namespace, 
                    previous=True, 
                    tail_lines=50
                )
            except Exception:
                # Fallback to current logs if no previous exists
                logs = v1.read_namespaced_pod_log(
                    pod.metadata.name, 
                    pod.metadata.namespace, 
                    tail_lines=50
                )

            # Get AI Suggestion
            suggestion = get_ai_fix(pod.metadata.name, logs)
            print(f"Suggested Fix for {pod.metadata.name}:\n{suggestion}\n")
            
            processed_pods.add(pod_id)
            
            # Simple cleanup of set to prevent memory growth in long-running pods
            if len(processed_pods) > 100:
                processed_pods.clear()

if __name__ == "__main__":
    # Ensure API Key is present
    if not LLM_API_KEY:
        print("Error: OPENROUTER_API_KEY environment variable not set.")
        exit(1)
    watch_events()