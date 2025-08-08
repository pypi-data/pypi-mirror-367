import requests


def run_workflow(BASE_URL, API_KEY, inputs):
    """
    dify工作流调用
    :param BASE_URL: dify工作流地址
    :param API_KEY: dify工作流API密钥
    :param inputs: 工作流输入json参数，如 {"input": "TestContent"}
    :return: 
      直接返回json数据，如 {"result": "TestResult"}
    """
    
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
        return response.json()["data"]["outputs"]
    else:
        print(f"错误: {response.status_code}")
        print(response.text)
        return response.text