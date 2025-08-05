"""Fetch proto files from the Tektii strategy proto repository.

This script retrieves all proto files from the proto/trading/v1 directory
in the tektii-strategy-proto repository and saves them locally.
"""

import os

import requests


def fetch_proto_files() -> None:
    """Fetch all proto files from the trading/v1 directory in GitHub."""
    print("Fetching proto files from GitHub...")

    try:
        # Repo info
        owner = "Tektii"
        repo = "tektii-strategy-proto"
        path = "proto/trading/v1"
        branch = "main"

        # Proto files to fetch
        proto_files = ["common.proto", "market_data.proto", "orders.proto", "service.proto"]

        # Create directory structure
        os.makedirs("./proto/trading/v1", exist_ok=True)

        # Headers for GitHub API
        headers = {
            "Accept": "application/vnd.github.v3.raw",
        }

        # Fetch each proto file
        for proto_file in proto_files:
            file_path = f"{path}/{proto_file}"
            url = f"https://api.github.com/repos/{owner}/{repo}/contents/{file_path}?ref={branch}"

            print(f"  Fetching {proto_file}...")
            response = requests.get(url, headers=headers)
            response.raise_for_status()

            # Save the file
            local_path = f"./proto/trading/v1/{proto_file}"
            with open(local_path, "wb") as f:
                f.write(response.content)
            print(f"  ✓ Saved {proto_file}")

    except requests.RequestException as e:
        print(f"Error fetching proto files: {e}")
        raise e
    except EnvironmentError as e:
        print(f"EnvironmentError: {e}")
        raise e
    else:
        print("All proto files fetched and saved successfully.")


if __name__ == "__main__":
    fetch_proto_files()
