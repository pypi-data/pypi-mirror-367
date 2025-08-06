import requests


def run_workflow(BASE_URL, API_KEY, inputs):

    # 设置请求头
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    url = f"{BASE_URL}/workflows/run"

    payload = {
        "inputs": inputs,
        "response_mode": "blocking",
        "user": "zhaoyz77"
    }

    response = requests.post(url, headers=headers, json=payload)

    if response.status_code == 200:
        return response.json()
    else:
        print(f"错误: {response.status_code}")
        print(response.text)
        return None