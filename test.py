import requests


def get_latest_version(package_name):
    url = f"https://search.maven.org/solrsearch/select?q=g:{package_name}&rows=20&wt=json"
    response = requests.get(url)
    response_json = response.json()
    docs = response_json.get("response", {}).get("docs", [])

    versions = [doc["v"] for doc in docs if "v" in doc]
    return versions


# Fetching the latest version of org.jfrog.buildinfo:build-info-extractor-gradle
get_latest_version("org.jfrog.buildinfo")
