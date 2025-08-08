# call.py
from requests import request

def substitute(obj, variables):
    if isinstance(obj, str):
        for k, v in variables.items():
            obj = obj.replace(f"<{k}>", str(v)).replace(f"[{k}]", str(v))
        return obj
    elif isinstance(obj, dict):
        return {k: substitute(v, variables) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [substitute(i, variables) for i in obj]
    else:
        return obj


def call_api(config, variables):
    try:
        method = config.get("method", "GET").upper()
        url = substitute(config.get("url"), variables)
        headers = substitute(config.get("headers", {}).copy(), variables)
        params = substitute(config.get("params", {}), variables)
        data = substitute(config.get("data", None), variables)
        json_data = substitute(config.get("json", None), variables)
        timeout = config.get("timeout", 10)

        if "bearer_token" in config:
            headers["Authorization"] = f"Bearer {substitute(config['bearer_token'], variables)}"

        resp = request(
            method=method,
            url=url,
            headers=headers,
            params=params,
            data=data,
            json=json_data,
            timeout=timeout
        )
        return resp
    except Exception as e:
        return str(e)
