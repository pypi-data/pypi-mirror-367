"""
Lambda Cloud CLI entry point. Commands include login/logout, instance management, firewall rules,
SSH key registration, filesystem actions, and self-update tools.
"""

# ─────────────────────────────────────────────
# 🔧 Standard library imports
# ─────────────────────────────────────────────
import os
import sys
import time
import subprocess
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional

# ─────────────────────────────────────────────
# 🌐 Third-party libraries
# ─────────────────────────────────────────────
import requests
import typer
import pkg_resources

# ─────────────────────────────────────────────
# 📦 Internal modules
# ─────────────────────────────────────────────
from lambda_cloud_cli.lambda_api_client import LambdaAPIClient
from lambda_cloud_cli.config import load_api_key, save_api_key, delete_api_key

app = typer.Typer()
client=None

UPDATE_CHECK_INTERVAL_HOURS = 24
UPDATE_CACHE_FILE = Path.home() / ".lambda-cli" / "last_version_check"

# ─────────────────────────────────────────────
# 🔧 Utility Functions
# ─────────────────────────────────────────────

def get_client():
    global client
    if client is None:
        API_KEY = os.environ.get("API_KEY") or load_api_key()
        if not API_KEY:
            typer.echo("❌ No API key set. Run: lambda-cli login")
            raise typer.Exit(code=1)
        client = LambdaAPIClient(api_key=API_KEY)
    return client

# ─────────────────────────────────────────────
# 🚀 CLI Commands
# ─────────────────────────────────────────────

@app.command(name="login")
def login():
    """Set your Lambda Cloud API key"""
    api_key = typer.prompt("🔐 Enter your Lambda Cloud API key", hide_input=True)
    save_api_key(api_key)
    typer.echo("✅ API key saved.")
    
@app.command(name="logout",help="Remove your stored API key")
def logout():
    """Remove your stored API key"""
    if delete_api_key():
        typer.echo("✅ API key removed. You are now logged out.")
    else:
        typer.echo("ℹ️  No API key was stored.")

@app.command(name="list-instances")
def list_instances():
    instances = get_client().list_instances().get("data", [])
    if not instances:
        typer.secho("ℹ️  No instances found in your account.", fg=typer.colors.YELLOW)
        return

    for inst in instances:
        typer.echo(f"{inst['id']}: {inst['name']} ({inst['status']})")

@app.command(name="terminate",help="Terminate an instance by ID")
def terminate(instance_id: str):
    result = get_client().terminate_instances([instance_id])
    typer.echo(result)

@app.command(name="launch-instance",help="Launch a Lambda Cloud instance")
def launch_instance(
    region_name: str = typer.Option(..., "--region-name", help="Lambda region (e.g. us-west-1)"),
    instance_type: str = typer.Option(..., "--instance-type", help="Instance type (e.g. gpu_1x_a10)"),
    ssh_key_name: str = typer.Option(..., "--ssh-key-name", help="Your SSH key name"),
    name: str = typer.Option("lambda-cli-instance", "--name", help="Optional instance name"),
    image_id: Optional[str] = typer.Option(None, "--image-id", help="Optional image ID")
):
    payload = {
        "region_name": region_name,
        "instance_type_name": instance_type,
        "ssh_key_names": [ssh_key_name],
        "name": name
    }

    if image_id:
        payload["image"] = {"id": image_id}

    result = get_client().launch_instance(payload)
    typer.echo("🚀 Launch request sent!")
    typer.echo(result)

    if 'error' in result:
        typer.secho(f"❌ {result['error'].get('message', 'Unknown error')}", fg=typer.colors.RED)
        suggestion = result['error'].get('suggestion')
        if suggestion:
            typer.echo(f"💡 {suggestion}")
    else:
        typer.secho("✅ Instance launched successfully!", fg=typer.colors.GREEN)
        typer.echo(result)

@app.command(name="update-instance-name", help="Rename an existing instance")
def update_instance_name(
    instance_id: str = typer.Option(..., "--instance-id", help="Instance ID to rename"),
    new_name: str = typer.Option(..., "--new-name", help="New name for the instance")
):
    """Renames an instance by its ID"""
    result = get_client().update_instance_name(instance_id, new_name)
    typer.echo(result)

@app.command(name="list-instance-types")
def list_instance_types():
    types_dict = get_client().list_instance_types().get("data", {})
    for type_data in types_dict.values():
        inst = type_data.get("instance_type", {})
        name = inst.get("name", "unknown")
        gpus = inst.get("specs", {}).get("gpus", "?")
        typer.echo(f"{name} ({gpus} GPUs)")

@app.command(name="get-firewall-rules")
def get_firewall_rules():
    rules = get_client().get_firewall_rules().get("data", [])
    for rule in rules:
        typer.echo(rule)

@app.command(name="get-firewall-rulesets")
def get_firewall_rulesets():
    rulesets = get_client().get_firewall_rulesets().get("data", [])
    for rs in rulesets:
        typer.echo(f"{rs['id']}: {rs['name']}")

@app.command(name="get-firewall-ruleset-by-id")
def get_firewall_ruleset_by_id(ruleset_id: str):
    result = get_client().get_firewall_ruleset_by_id(ruleset_id)
    typer.echo(result)

@app.command(name="delete-firewall-ruleset")
def delete_firewall_ruleset(ruleset_id: str):
    result = get_client().delete_firewall_ruleset(ruleset_id)
    typer.echo(result)

@app.command(name="create-firewall-ruleset")
def create_firewall_ruleset(name: str, region: str):
    rules = [
        {
            "protocol": "tcp",
            "port_range": [22, 22],
            "source_network": "0.0.0.0/0",
            "description": "Allow SSH from anywhere"
        }
    ]
    result = get_client().create_firewall_ruleset(name, region, rules)
    typer.echo(result)

@app.command(name="update-firewall-ruleset")
def update_firewall_ruleset(ruleset_id: str, name: str):
    rules = [
        {
            "protocol": "tcp",
            "port_range": [22, 22],
            "source_network": "0.0.0.0/0",
            "description": "Allow SSH from anywhere"
        }
    ]
    result = get_client().update_firewall_ruleset(ruleset_id, name, rules)
    typer.echo(result)

@app.command(name="patch-global-firewall")
def patch_global_firewall():
    rules = [
        {
            "protocol": "tcp",
            "port_range": [22, 22],
            "source_network": "0.0.0.0/0",
            "description": "Allow SSH from anywhere"
        }
    ]
    result = get_client().patch_global_firewall_ruleset(rules)
    typer.echo(result)

@app.command(name="get-global-firewall")
def get_global_firewall():
    result = get_client().get_global_firewall_ruleset()
    typer.echo(result)

@app.command(name="list-ssh-keys",help="List your registered SSH keys")
def list_ssh_keys():
    keys = get_client().list_ssh_keys().get("data", [])
    for key in keys:
        typer.echo(f"{key['id']}: {key['name']} - {key['public_key'][:40]}...")

@app.command(name="add-ssh-key")
def add_ssh_key(name: str, public_key: str):
    result = get_client().add_ssh_key(name, public_key)
    typer.echo(result)

@app.command(name="delete-ssh-key")
def delete_ssh_key(key_id: str):
    result = get_client().delete_ssh_key(key_id)
    typer.echo(result)

@app.command(name="list-file-systems")
def list_file_systems():
    filesystems = get_client().list_file_systems().get("data", [])
    for fs in filesystems:
        typer.echo(f"{fs['id']}: {fs['name']} in {fs['region']}")

@app.command(name="create-file-system")
def create_file_system(name: str, region: str):
    result = get_client().create_file_system(name, region)
    typer.echo(result)

@app.command(name="delete-file-system")
def delete_file_system(fs_id: str):
    result = get_client().delete_file_system(fs_id)
    typer.echo(result)

@app.command(name="list-images",help="Show available images in your account")
def list_images():
    images = get_client().list_images().get("data", [])
    for img in images:
        region = img.get("region", {}).get("name", "unknown")
        typer.echo(f"{img['id']}: {img['name']} ({region})")

@app.command(name="self-update", help="Check for updates and upgrade to the latest version")
def self_update(yes: bool = typer.Option(False, "--yes", help="Skip confirmation")):
    """Upgrade lambda-cloud-cli to the latest version from PyPI"""
    package = "lambda-cloud-cli"

    def get_latest_version_from_pypi(package, retries=3, delay=5):
        url = f"https://pypi.org/pypi/{package}/json"
        for attempt in range(retries):
            try:
                response = requests.get(url, timeout=5)
                return response.json()["info"]["version"]
            except Exception as e:
                if attempt < retries - 1:
                    time.sleep(delay)
                else:
                    raise e

    try:
        installed = pkg_resources.get_distribution(package).version
    except pkg_resources.DistributionNotFound:
        installed = None

    try:
        latest = get_latest_version_from_pypi(package)
    except Exception:
        typer.echo("❌ Could not fetch latest version info from PyPI.")
        raise typer.Exit(code=1)

    typer.echo(f"📦 Installed: {installed or 'Not installed'}")
    typer.echo(f"🌍 Latest: {latest}")

    if installed == latest:
        typer.secho("✅ You're already using the latest version.", fg=typer.colors.GREEN)
        raise typer.Exit()

    if not yes:
        confirm = typer.confirm(f"⬆️  Update to version {latest}?")
        if not confirm:
            typer.echo("🚫 Update cancelled.")
            raise typer.Exit()

    typer.echo("🔄 Updating...")
    subprocess.run([
        sys.executable, "-m", "pip", "install",
        "--upgrade", "--force-reinstall", "--no-cache-dir", package
    ])
    typer.secho("✅ Update complete!", fg=typer.colors.GREEN)

#try:
#    current = pkg_resources.get_distribution("lambda-cloud-cli").version
#    latest = requests.get("https://pypi.org/pypi/lambda-cloud-cli/json", timeout=3).json()["info"]["version"]
#    if current != latest:
#        print(f"📢 New version available: {current} → {latest}\n👉 Run: lambda-cli self-update")
#except:
#    pass  # fail silently

def should_check_version():
    UPDATE_CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)
    if UPDATE_CACHE_FILE.exists():
        last_checked = datetime.fromtimestamp(UPDATE_CACHE_FILE.stat().st_mtime)
        if datetime.now() - last_checked < timedelta(hours=UPDATE_CHECK_INTERVAL_HOURS):
            return False
    return True

if should_check_version():
    try:
        current = pkg_resources.get_distribution("lambda-cloud-cli").version
        latest = requests.get("https://pypi.org/pypi/lambda-cloud-cli/json", timeout=3).json()["info"]["version"]
        if current != latest:
            print(f"📢 New version available: {current} → {latest}\n👉 Run: lambda-cli self-update")
    except:
        pass  # fail silently

    # ✅ Update the timestamp
    UPDATE_CACHE_FILE.touch()

app()



