import yaml
import os


def load_config(filename):
    with open(filename, "r") as file:
        config = yaml.safe_load(file)
    return config


config_data = load_config("config.yaml")
proxy_config = config_data.get("proxy", {})

if proxy_config.get("enabled", False):
    proxy_url = proxy_config.get("url")
    if not proxy_url:
        raise ValueError("Proxy URL is not provided")
    os.environ["http_proxy"] = proxy_url
    os.environ["https_proxy"] = proxy_url
    os.environ["HTTP_PROXY"] = proxy_url
    os.environ["HTTPS_PROXY"] = proxy_url

    exclude = proxy_config.get("exclude", [])
    if exclude:
        if not isinstance(exclude, list):
            raise ValueError("Exclude should be a list of strings")

    # Add localhost
    exclude.append("localhost")
    exclude.append("127.0.0.1")

    os.environ["no_proxy"] = ",".join(exclude)
    os.environ["NO_PROXY"] = ",".join(exclude)
