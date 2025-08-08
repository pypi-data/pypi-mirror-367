from sanic import Sanic, response, Blueprint
from sanic.exceptions import Forbidden, SanicException
from sanic.response import html
from requests import request
from time import time
from .rate_limit import rate_limit
from .call import call_api
import json
import hashlib
import sys



class verification:    
    def hash_api_key(key: str) -> str:
        return hashlib.sha256(key.encode('utf-8')).hexdigest()

    def get_user_by_api_key(provided_key: str, users: dict) -> tuple:
        provided_key_hash = verification.hash_api_key(provided_key)
        for username, data in users.items():
            if data.get("api_key_hash") == provided_key_hash:
                return username, data
        return None, None

def main(config_path: str, is_string: bool = False):
    print(config_path)
    def replace_keys(_str, _keys):
        for k, v in _keys.items():
            replaced = _str.replace(f'[{k}]', v)
            print(f"Replaced [{k}] with {v} in config_str")
        return replaced
    app = Sanic("API_Proxy")
    bp = Blueprint("proxy_routes")

    if is_string:
        config = config_path
    else:
        path = config_path.strip('\'"')  # Remove single or double quotes
        with open(path) as f:
            config = f.read()
            
    print(config)

    foo = json.loads(config)
    keys = foo["keys"]
    replaced = replace_keys(config, keys)
    config = json.loads(replaced)
    users = config["users"]
    othervars = config.get("open-vars", {})
    routes = list(config["routes"].keys())
    route_to_api_key = config["routes"]
    apis = config["apis"]
    keys = config["keys"]


    def make_handler(api_name, api_config):
        cors_enabled = str(api_config.get("cors", "False")).lower() == "true"
        require_api_key = api_config.get("require_api_key", True)
        rate_limit_cfg = api_config.get("rate_limit", {"limit": 5, "window": 60})

        async def handler(request, **path_vars):
            # 1. Optionally check API Key authorization
            api_key = request.headers.get("X-API-Key") or request.args.get("api_key")
            username, user_data = None, None
            if require_api_key:
                if not api_key:
                    raise Forbidden("Missing API Key")
                username, user_data = verification.get_user_by_api_key(api_key, users)
                if not user_data:
                    raise Forbidden("Invalid API Key")
                if api_name not in user_data.get("allowed_apis", []):
                    raise Forbidden("API access denied for this key")

            merged_vars = {
                **othervars,
                **{k: v for k, v in request.args.items()},
                **{k: v[0] if isinstance(v, list) else v for k, v in request.form.items()},
                **path_vars
            }

            result = call_api(api_config, merged_vars)
            try:
                resp = response.text(result.text)
            except Exception:
                resp = response.text(str(result))

            if cors_enabled:
                resp.headers["Access-Control-Allow-Origin"] = "*"
                resp.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, OPTIONS"
                resp.headers["Access-Control-Allow-Headers"] = "*"
            return resp

        # Per-API rate limiting
        limit = int(rate_limit_cfg.get("limit", 5))
        window = int(rate_limit_cfg.get("window", 60))
        handler = rate_limit(limit, window, scope="ip")(handler)

        return handler

    for route in routes:
        api_key = route_to_api_key[route]
        config_entry = apis[api_key]
        method = config_entry.get("method", "GET").upper()
        handler = make_handler(api_key, config_entry)
        app.add_route(handler, f"/{route}", methods=[method, "OPTIONS"], name=f"handler_{route}")

    @bp.route("/<path:path>", methods=["GET", "POST", "PUT", "DELETE"])
    async def proxy(request, path):
        api_key = request.args.get("api_key") or request.headers.get("X-API-Key")
        if not api_key or not is_valid_key(api_key):
            return response.json({"error": "Invalid API Key"}, status=401)
    
    app.run(host="127.0.0.1", port=8000, debug=True, single_process=True)