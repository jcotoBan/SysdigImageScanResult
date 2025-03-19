import os
import json
import requests
import yaml

def load_config():
    with open("config.yaml", "r") as file:
        return yaml.safe_load(file)

def get_base_url(region):
    region_urls = {
        "us1": "https://secure.sysdig.com/secure/vulnerability/v1beta1",
        "us2": "https://us2.app.sysdig.com/secure/vulnerability/v1beta1",
        "us4": "https://app.us4.sysdig.com/secure/vulnerability/v1beta1",
        "eu1": "https://eu1.app.sysdig.com/secure/vulnerability/v1beta1",
        "au1": "https://app.au1.sysdig.com/secure/vulnerability/v1beta1",
        "me2": "https://app.me2.sysdig.com/secure/vulnerability/v1beta1",
        "in1": "https://app.in1.sysdig.com/secure/vulnerability/v1beta1"
    }
    return region_urls.get(region, region_urls["us1"])

def get_results(api_key, region, result_type):
    base_url = get_base_url(region)
    url = f"{base_url}/pipeline-results" if result_type == "p" else f"{base_url}/runtime-results"
    
    headers = {"Authorization": f"Bearer {api_key}"}
    response = requests.get(url, headers=headers)
    
    if response.status_code != 200:
        print(f"Failed to fetch {result_type} results: HTTP {response.status_code}")
        exit(1)
    
    return response.json()

def fetch_detailed_results(api_key, region, result_id):
    base_url = get_base_url(region)
    url = f"{base_url}/results/{result_id}"
    
    headers = {"Authorization": f"Bearer {api_key}"}
    response = requests.get(url, headers=headers)
    
    if response.status_code != 200:
        print(f"Failed to fetch details for result ID {result_id}: HTTP {response.status_code}")
        return
    
    result_data = response.json()
    print(f"Details for Result ID {result_id}:\n{json.dumps(result_data, indent=2)}")

def main():
    config = load_config()
    
    api_key = config.get("token")
    region = config.get("region", "us4")
    result_type = config.get("option", "r").lower()
    image_name = config.get("image_name")
    
    if result_type not in ["p", "r"]:
        print("Invalid option in config.yaml. Please set 'option' to 'p' for pipeline or 'r' for runtime.")
        exit(1)
    
    results = get_results(api_key, region, result_type)
    
    for entry in results.get("data", []):
        if entry.get("mainAssetName") == image_name:
            print(f"Found Asset: {entry['mainAssetName']} (Result ID: {entry['resultId']})")
            fetch_detailed_results(api_key, region, entry['resultId'])
            return
    
    print("No matching asset found.")

if __name__ == "__main__":
    main()
