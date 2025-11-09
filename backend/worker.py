import os
import time
import requests
import json

subprompt = os.getenv("SUBPROMPT")
company = os.getenv("COMPANY")
api_key = os.getenv("API_KEY")

try:
    start = time.perf_counter()

    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    if company == "google":
        model = "google/gemini-2.0-flash-001"
    elif company == "anthropic":
        model = "anthropic/claude-haiku-4.5"
    elif company == "openai":
        model = "openai/gpt-4o"
    else:
        raise ValueError(f"Unknown company: {company}")

    payload = {"model": model, "messages": [{"role": "user", "content": subprompt}]}
    
    resp = requests.post(url, headers=headers, json=payload, timeout=30)
    resp.raise_for_status()
    result = resp.json()

    elapsed = round(time.perf_counter() - start, 2)
    print(json.dumps(result, indent=2))

    if "choices" in result and len(result["choices"]) > 0:
        content = result["choices"][0]["message"]["content"]
        print(content)
    else:
        print(f" {company} finished in {elapsed}s")
        print(json.dumps(result, indent=2))

except Exception as e:
    import traceback
    traceback.print_exc()
    raise