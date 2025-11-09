import google.generativeai as genai
import anthropic
from openai import OpenAI
import time
import uuid
import requests
import json
import zipfile
import os
from kubernetes import client, config, watch

api_keys = {}
sorted_companies = {}
timings = {}

def load_k8s_config():
    """Load Kubernetes config - try in-cluster first, then local"""
    try:
        config.load_incluster_config()
        print("Loaded in-cluster Kubernetes config")
    except config.ConfigException:
        print("Could not load in-cluster config, trying local kubeconfig")
        try:
            config.load_kube_config()
            print("Loaded local Kubernetes config")
        except config.ConfigException:
            print("Could not load Kubernetes config")
            raise

def addAPIKey(company, key):
    api_keys[company] = key

def tester(subprompt, n):
    global sorted_companies, timings
    results = {}
    timings = {}

    print("Testing API speeds...")

    def ping_api(company, model):
        start = time.perf_counter()
        try:
            url = "https://openrouter.ai/api/v1/chat/completions"
            headers = {
                "Authorization": f"Bearer {api_keys[company]}",
                "Content-Type": "application/json"
            }
            payload = {
                "model": model,
                "messages": [{"role": "user", "content": subprompt}]
            }
            response = requests.post(url, headers=headers, json=payload, timeout=20)
            elapsed = time.perf_counter() - start
            return response.text, elapsed
        except Exception as e:
            return f"Error: {e}", float("inf")

    for company, model in {
        "google": "google/gemini-2.0-flash-001",
        "anthropic": "anthropic/claude-haiku-4.5",
        "openai": "openai/gpt-4o",
    }.items():
        if company in api_keys:
            text, elapsed = ping_api(company, model)
            results[company] = text
            timings[company] = elapsed

    sorted_items = sorted(results.items(), key=lambda item: timings[item[0]])
    sorted_companies = dict(sorted_items)

    print("API timing results:", timings)
    assignPods(subprompt, n)
    return sorted_companies, timings

def assignPods(subprompt, n):
    valid_timings = {k: v for k, v in timings.items() if v != float('inf')}
    if not valid_timings:
        print("No valid API responses to assign pods")
        return

    speeds = [1/t for t in valid_timings.values()]
    total_speed = sum(speeds)

    for i, company in enumerate(valid_timings.keys()):
        proportion = speeds[i] / total_speed
        pods_assigned = max(1, round(proportion * n))
        print(f"⚙️ Assigning {pods_assigned} pod(s) to {company}")
        for _ in range(pods_assigned):
            create_k8s_job(company, subprompt, api_keys[company])

    wait_for_jobs_and_zip()

def create_k8s_job(company, subprompt, api_key):
    load_k8s_config()
    batch_v1 = client.BatchV1Api()
    job_name = f"squarenetes-{company}-{uuid.uuid4().hex[:6]}"

    container = client.V1Container(
        name="worker",
        image="squarenetes-worker:latest",
        image_pull_policy="Never",
        env=[
            client.V1EnvVar(name="COMPANY", value=company),
            client.V1EnvVar(name="SUBPROMPT", value=subprompt),
            client.V1EnvVar(name="API_KEY", value=api_key),
        ],
        volume_mounts=[client.V1VolumeMount(mount_path="/outputs", name="output-volume")]
    )

    volume = client.V1Volume(
        name="output-volume",
        empty_dir=client.V1EmptyDirVolumeSource()
    )

    template = client.V1PodTemplateSpec(
        metadata=client.V1ObjectMeta(labels={"job": job_name}),
        spec=client.V1PodSpec(restart_policy="Never", containers=[container], volumes=[volume])
    )

    job_spec = client.V1JobSpec(template=template, backoff_limit=1)
    job = client.V1Job(
        api_version="batch/v1",
        kind="Job",
        metadata=client.V1ObjectMeta(name=job_name),
        spec=job_spec
    )

    batch_v1.create_namespaced_job(body=job, namespace="default")
    print(f"Created Job: {job_name}")
    return job_name

def wait_for_jobs_and_zip():
    load_k8s_config()
    v1 = client.CoreV1Api()
    w = watch.Watch()
    namespace = "default"
    outputs_dir = "outputs"
    os.makedirs(outputs_dir, exist_ok=True)

    print("⏳ Waiting for pods to complete...")
    completed_jobs = set()

    for event in w.stream(v1.list_namespaced_pod, namespace=namespace, timeout_seconds=60):
        pod = event["object"]
        pod_name = pod.metadata.name
        status = pod.status.phase
        if status == "Succeeded" and pod_name not in completed_jobs:
            print(f"Collecting logs from {pod_name}")
            try:
                logs = v1.read_namespaced_pod_log(name=pod_name, namespace=namespace)
                with open(f"{outputs_dir}/{pod_name}.txt", "w", encoding="utf-8") as f:
                    f.write(logs)
            except Exception as e:
                print(f"Could not read logs from {pod_name}: {e}")
            completed_jobs.add(pod_name)

    zip_path = "output.zip"
    with zipfile.ZipFile(zip_path, "w") as zf:
        for file in os.listdir(outputs_dir):
            zf.write(os.path.join(outputs_dir, file), file)
    print(f"Zipped all outputs into {zip_path}")