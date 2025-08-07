import os
import json
from typing import Dict, Any, List, Callable
import requests
from litellm import completion


class LaughingFaceModule:
    """A callable module that can be invoked with dynamic arguments."""
    def __init__(self, config: Dict[str, Any]):
        self.config = config

    def __call__(self, **kwargs) -> str:
        """Invoke the module with dynamic arguments."""
        system_prompt_template = self.config.get("system_prompt", "")
        user_prompt_template = self.config.get("user_prompt", "")
        model_id = self.config.get("model_id", "openai/gpt-4o-mini")
        temperature = self.config.get("temperature", 0.7)

        try:
            system_prompt = system_prompt_template.format(**kwargs)
            user_prompt = user_prompt_template.format(**kwargs)
        except KeyError as e:
            raise ValueError(f"Missing argument for placeholder: {e}")

        try:
            response = completion(
                model=model_id,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=temperature
            )
            return response["choices"][0]["message"]["content"]
        except Exception as e:
            raise RuntimeError(f"Failed to invoke module {self.config.get('module_name', 'unknown')}: {e}")


# Module-level variables
_api_key = None
_base_dir = ".laughingface/modules"
_api_endpoint = "https://us-central1-dsports-6ab79.cloudfunctions.net"
_initialized = False


def _ensure_directory():
    if not os.path.exists(_base_dir):
        os.makedirs(_base_dir)


def _ensure_initialized():
    if not _initialized:
        raise RuntimeError("LaughingFace not initialized. Call init() first.")


def init(api_key: str = None):
    """Initialize LaughingFace with modules."""
    global _api_key, _initialized
    
    if api_key:
        _api_key = api_key
    
    _api_key = _api_key or os.getenv("LAUGHINGFACE_API_KEY")
    if not _api_key:
        raise EnvironmentError("API key is not set. Pass it to init() or set LAUGHINGFACE_API_KEY in the environment.")
    
    _ensure_directory()
    remote_modules = fetch_remote_modules()

    if not isinstance(remote_modules, dict):
        raise RuntimeError(f"Unexpected data structure: {remote_modules}")

    for module_name, config in remote_modules.items():
        save_local_module(module_name, config)
        
    _initialized = True


# def fetch_remote_modules() -> Dict[str, Any]:
#     try:
#         url = f"{_api_endpoint}/get_data"
#         headers = {"Content-Type": "application/json"}
#         payload = json.dumps({"api_key": _api_key})

#         response = requests.post(url, headers=headers, data=payload)
#         response.raise_for_status()
#         return response.json()

#     except requests.exceptions.HTTPError as http_err:
#         raise RuntimeError(f"HTTP error occurred: {http_err}")
#     except requests.exceptions.RequestException as req_err:
#         raise RuntimeError(f"Request error occurred: {req_err}")
#     except ValueError as json_err:
#         raise RuntimeError(f"Failed to decode JSON: {json_err}")

_api_endpoint = "https://us-central1-dsports-6ab79.cloudfunctions.net"

# def fetch_remote_modules() -> Dict[str, Any]:
#     try:
#         url = f"{_api_endpoint}/get_data"
#         headers = {"Content-Type": "application/json"}
#         payload = json.dumps({"api_key": _api_key})

#         # Debug prints
#         print(f"URL: {url}")
#         print(f"Headers: {headers}")
#         print(f"Payload: {payload}")

#         response = requests.post(url, headers=headers, data=payload)
#         print(f"Response: {response.text}")  # Print raw response
        
#         response.raise_for_status()
#         return response.json()["modules"]

#     except requests.exceptions.HTTPError as http_err:
#         print(f"Full response content: {response.text}")  # Print error response
#         raise RuntimeError(f"HTTP error occurred: {http_err}")
#     except requests.exceptions.RequestException as req_err:
#         raise RuntimeError(f"Request error occurred: {req_err}")
#     except ValueError as json_err:
#         raise RuntimeError(f"Failed to decode JSON: {json_err}")
    

# def fetch_remote_modules() -> Dict[str, Any]:
#     try:
#         url = f"{_api_endpoint}/get_data"
#         headers = {"Content-Type": "application/json"}
#         payload = json.dumps({"api_key": _api_key})

#         response = requests.post(url, headers=headers, data=payload)
#         response.raise_for_status()

#         data = response.json()
#         if not isinstance(data, dict) or "modules" not in data:
#             raise RuntimeError(f"Unexpected response structure: {data}")

#         return data["modules"]

#     except requests.exceptions.HTTPError as http_err:
#         raise RuntimeError(f"HTTP error occurred: {http_err}")
#     except requests.exceptions.RequestException as req_err:
#         raise RuntimeError(f"Request error occurred: {req_err}")
#     except ValueError as json_err:
#         raise RuntimeError(f"Failed to decode JSON: {json_err}")
    
def fetch_remote_modules() -> Dict[str, Any]:
    try:
        url = f"{_api_endpoint}/get_data"
        headers = {"Content-Type": "application/json"}
        payload = json.dumps({"api_key": _api_key})

        response = requests.post(url, headers=headers, data=payload)
        response.raise_for_status()

        data = response.json()
        if not isinstance(data, dict):
            raise RuntimeError(f"Unexpected response structure: {data}")

        # Return the data directly since it's already the modules dict
        return data

    except requests.exceptions.HTTPError as http_err:
        raise RuntimeError(f"HTTP error occurred: {http_err}")
    except requests.exceptions.RequestException as req_err:
        raise RuntimeError(f"Request error occurred: {req_err}")
    except ValueError as json_err:
        raise RuntimeError(f"Failed to decode JSON: {json_err}")    
    
# def save_local_module(module_name: str, config: Dict[str, Any]):
#     config["module_name"] = module_name
#     module_path = os.path.join(_base_dir, f"{module_name}.json")
#     with open(module_path, "w") as f:
#         json.dump(config, f, indent=4)


def save_local_module(module_name: str, config: Dict[str, Any]):
    # Remove .json extension if present
    if module_name.endswith(".json"):
        module_name = module_name[:-5]
    config["module_name"] = module_name
    module_path = os.path.join(_base_dir, f"{module_name}.json")
    with open(module_path, "w") as f:
        json.dump(config, f, indent=4)


def list_modules() -> List[str]:
    _ensure_initialized()
    return [
        f[:-5] for f in os.listdir(_base_dir)
        if os.path.isfile(os.path.join(_base_dir, f)) and f.endswith(".json")
    ]


def load_module(module_name: str) -> Dict[str, Any]:
    _ensure_initialized()
    module_path = os.path.join(_base_dir, f"{module_name}.json")
    if not os.path.exists(module_path):
        raise FileNotFoundError(f"Module {module_name} does not exist")

    with open(module_path, "r") as f:
        return json.load(f)


def module(module_name: str) -> Callable[..., str]:
    _ensure_initialized()
    config = load_module(module_name)
    return LaughingFaceModule(config)