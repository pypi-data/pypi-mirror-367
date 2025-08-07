import requests
import os

GITHUB_RAW_BASE = "https://raw.githubusercontent.com/nabeelxdd/pip-nabeelxd/main/pip-storage/"

def fetch_file(filename: str) -> str:
    """Fetch the raw Python file content from GitHub pip-storage."""
    if not filename.endswith(".py"):
        filename += ".py"
    url = GITHUB_RAW_BASE + filename
    response = requests.get(url)
    if response.status_code == 200:
        return response.text
    else:
        raise FileNotFoundError(f"File '{filename}' not found in GitHub repository.")

def run(filename: str):
    """Fetch a Python script from GitHub and execute it."""
    code = fetch_file(filename)
    module_globals = {}
    exec(code, module_globals)
    # Auto-run main() if present
    if "main" in module_globals and callable(module_globals["main"]):
        module_globals["main"]()

def save(filename: str, save_as: str = None):
    """Fetch a Python script from GitHub and save it as a local file."""
    code = fetch_file(filename)
    if save_as is None:
        save_as = filename if filename.endswith(".py") else filename + ".py"
    with open(save_as, "w") as f:
        f.write(code)
    print(f"File saved as '{save_as}'")