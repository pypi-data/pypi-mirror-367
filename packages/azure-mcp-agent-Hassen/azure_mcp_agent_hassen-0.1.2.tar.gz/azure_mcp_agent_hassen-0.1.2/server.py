import os
import subprocess
from pathlib import Path
from mcp.server.fastmcp import FastMCP
import asyncio
import json
import time
import logging
import sys

# Set up logging to a file
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("mcp_logs.txt"),
        logging.StreamHandler()          # <-- this sends logs to stdout
    ]
)
# Check if running in container
container_mode = "--container-mode" in sys.argv
server_name = "Azure MCP Agent (Container)" if container_mode else "Azure MCP Agent (Local)"
logging.debug("container mode is .")
logging.debug("container mode is .")
logging.debug(container_mode)

mcp = FastMCP("Azure MCP Agent", stateless_http=True, host="0.0.0.0", port=3333)
import platform

if platform.system() == "Windows":
    AZ_CMD = r"C:\Program Files (x86)\Microsoft SDKs\Azure\CLI2\wbin\az.cmd"
else:
    AZ_CMD = "az"
STORAGE_FILE = Path("azure_auth_data.json")

# -- Utility Functions --

def az(*args):
    env = os.environ.copy()
    result = subprocess.run(
        [AZ_CMD, *args, "--output", "json"],
        capture_output=True,
        text=True,
        env=env
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr)
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError as e:
        logging.error(f"JSON decode error: {str(e)}, stdout: {result.stdout}")
        raise RuntimeError(f"Failed to parse JSON output: {str(e)}, stdout: {result.stdout}")

def save_session(subs):
    STORAGE_FILE.write_text(json.dumps(subs, indent=2))

def load_session():
    if STORAGE_FILE.exists():
        return json.loads(STORAGE_FILE.read_text())
    return None

def ensure_cost_extension_installed():
    try:
        az("extension", "add", "--name", "costmanagement")
        logging.debug("costmanagement extension installed.")
    except RuntimeError as e:
        if "already installed" in str(e):
            logging.debug("costmanagement extension already installed.")
        else:
            logging.error(f"Failed to install costmanagement extension: {e}")

# -- Tools --

@mcp.tool()
async def az_cmd(cmd: str) -> str:
    args = [AZ_CMD] + cmd.split()
    proc = await asyncio.create_subprocess_exec(
        *args,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    stdout, stderr = await proc.communicate()

    if proc.returncode != 0:
        return f"❌ Erreur : {stderr.decode()}"

    return stdout.decode()

@mcp.tool()
def launch_login():
    try:
        subprocess.Popen(f'start "" "{AZ_CMD}" login', shell=True)
        logging.debug("passed save session ")
        return {"status": "launched", "message": "Login window opened"}
    except Exception as e:
        return {"status": "error", "error": str(e)}

@mcp.tool()
def list_subscriptions():
    try:
        # Step 1: Check if user is logged in
        check_login = subprocess.run(
            [AZ_CMD, "account", "show"],
            capture_output=True,
            text=True
        )
        logging.debug("Checked if user is logged in using 'az account show'...")

        if check_login.returncode != 0:
            logging.warning("User is NOT logged in. Azure CLI output:\n%s", check_login.stderr)
            return {
                "status": "not_logged_in",
                "message": "Login not complete. Please run login first.",
                "az_output": check_login.stderr
            }

        logging.debug("User is logged in. Proceeding to list subscriptions...")

        # Step 2: List subscriptions
        subs = az("account", "list")
        logging.debug("Subscriptions retrieved: %s", subs)

        # Step 3: Save session to JSON
        save_session(subs)
        logging.debug("Subscriptions saved to file")

        return {
            "status": "ok",
            "subscriptions": subs
        }

    except Exception as e:
        logging.exception("An unexpected error occurred during list_subscriptions.")
        return {
            "status": "error",
            "error": str(e)
        }

@mcp.tool()
def say_hello():
    try:
        return {"message": "MCP is alive"}
    except Exception as e:
        logging.error(f"say_hello error: {e}")
        return {"error": str(e)}

@mcp.tool()
def get_vm_usage_and_cost():
    """Fetch details and costs of all Azure VMs for the subscription using az consumption usage list."""
    logging.debug("Starting get_vm_usage_and_cost")
    result = {
        "status": "ok",
        "vms": [],
        "total_cost": 0.0,
        "currency": None,
        "debug": []
    }

    try:
        # Load subscriptions
        logging.debug("Loading subscriptions")
        result["debug"].append("Loading subscriptions")
        subs = load_session()
        if not subs:
            logging.warning("No subscriptions found")
            result["debug"].append("No subscriptions found")
            return {
                "status": "not_logged_in",
                "message": "Please log in first using 'launch login' and complete the login process.",
                "debug": result["debug"]
            }

        # Use the first subscription
        sub = subs[0]
        sub_id = sub.get("id")
        logging.debug(f"Using subscription ID: {sub_id}")
        result["debug"].append(f"Using subscription ID: {sub_id}")

        # Get all VMs in the subscription
        logging.debug("Fetching VM list")
        result["debug"].append("Fetching VM list")
        try:
            vms = az("vm", "list", "--subscription", sub_id)
            for vm in vms:
                result["vms"].append({
                    "name": vm.get("name"),
                    "resource_group": vm.get("resourceGroup"),
                    "location": vm.get("location"),
                    "status": vm.get("powerState", "Unknown"),
                    "subscription_id": sub_id
                })
            logging.debug(f"Found {len(vms)} VMs")
            result["debug"].append(f"Found {len(vms)} VMs")
        except RuntimeError as e:
            logging.error(f"VM list failed: {str(e)}")
            result["debug"].append(f"VM list failed: {str(e)}")
            result["vm_error"] = f"Failed to fetch VMs: {str(e)}"

        # Query cost using az consumption usage list
        logging.debug("Fetching cost data")
        result["debug"].append("Fetching cost data")
        try:
            time_period_from = time.strftime("%Y-%m-%d", time.gmtime(time.time() - 30 * 24 * 3600))
            time_period_to = time.strftime("%Y-%m-%d", time.gmtime())

            usage_data = az(
                "consumption", "usage", "list",
                "--subscription", sub_id,
                "--start-date", time_period_from,
                "--end-date", time_period_to
            )

            total_cost = 0.0
            currency = None
            for usage in usage_data:
                try:
                    cost_raw = usage.get("pretaxCost")
                    if cost_raw in [None, "None", ""]:
                        continue
                    cost = float(cost_raw)
                    total_cost += cost
                    if not currency:
                        currency = usage.get("currency")
                except (ValueError, TypeError) as e:
                    logging.warning(f"Skipping invalid cost value: {cost_raw} due to error: {e}")
                    continue

            result["total_cost"] = total_cost
            result["currency"] = currency
            logging.debug(f"Total cost: {total_cost} {currency}")
            result["debug"].append(f"Total cost: {total_cost} {currency}")

        except RuntimeError as e:
            logging.error(f"Cost query failed: {str(e)}")
            result["debug"].append(f"Cost query failed: {str(e)}")
            result["cost_error"] = f"Failed to fetch cost data: {str(e)}"

        return result

    except Exception as e:
        logging.error(f"Unexpected error: {str(e)}")
        result["debug"].append(f"Unexpected error: {str(e)}")
        return {
            "status": "error",
            "error": f"Failed to fetch VM usage or cost: {str(e)}",
            "debug": result["debug"]
        }
def main():
    mcp.run()

# -- Run MCP Server --

if __name__ == "__main__":
    # Run the server with HTTP transport on port 3333
    logging.info("Starting Azure MCP Server on HTTP at 0.0.0.0:3333")
    
    # Use FastMCP's built-in HTTP transport
    main()
