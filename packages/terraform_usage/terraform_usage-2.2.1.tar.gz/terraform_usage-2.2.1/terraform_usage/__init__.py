#!/usr/bin/env python3
# -*- coding: latin-1 -*-

"""Get Terraform usage statistics."""
import requests
import time
from datetime import datetime as dt


__version__ = "2.2.1"
__author__ = "Ahmad Ferdaus Abd Razak"


def calculate_date(
    date_string: str
) -> float:
    """Calculate date in Unix epoch for Run lookups."""
    # Get unix epoch of date.
    date = dt.strptime(date_string, "%Y-%m-%dT%H:%M:%S%z")
    return date.timestamp()


def calculate_time(
    time_string: str
) -> float:
    """Calculate time in Unix epoch for Run lookups."""
    # Get unix epoch of date.
    time = dt.strptime(time_string, "%Y-%m-%dT%H:%M:%S%z")
    return time.timestamp()


def calculate_timerange(
    string_start: str,
    string_end: str
) -> float:
    """Calculates the number of seconds between two timestamps."""
    # Get unix epoch of start.
    time_start = dt.strptime(string_start, "%Y-%m-%dT%H:%M:%S%z")
    unix_epoch = int(time_start.timestamp())

    # Get unix epoch of end.
    time_end = dt.strptime(string_end, "%Y-%m-%dT%H:%M:%S%z")
    unix_end = int(time_end.timestamp())

    # Calculate the number of seconds between the two timestamps.
    return unix_end - unix_epoch


def sum_timeranges(
    time_data: list
) -> float:
    """Sums the number of seconds in a list of timeranges."""
    timeranges = [range["time"] for range in time_data]
    return sum(timeranges)


def list_workspaces(
    organization_name: str,
    token: str,
    keyword: str,
    api_url: str,
    page_size: int,
    delay: float
) -> list[dict]:
    """List all Workspaces for an Organization."""
    full_list = []
    page = 1

    # Loop through the Workspace list pagination.
    while page is not None:

        # Workspaces endpoint.
        endpoint = f"organizations/{organization_name}/workspaces"

        # Query string parameters for filtering.
        query = (
            f"page%5Bnumber%5D={page}"
            f"&page%5Bsize%5D={page_size}"
            f"&search%5Bwildcard-name%5D={keyword}"
        ) if keyword != "all" else (
            f"page%5Bnumber%5D={page}"
            f"&page%5Bsize%5D={page_size}"
        )

        # Headers.
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/vnd.api+json",
        }

        # Make the API call and get the response.
        print(f"Getting page {page} of Workspaces.")
        raw_response = requests.get(
            f"{api_url}/{endpoint}?{query}",
            headers=headers
        ).json()

        # Add data from current page to the full list.
        full_list.extend(
            [
                {
                    "id": workspace["id"],
                    "name": workspace["attributes"]["name"]
                } for workspace in raw_response["data"]
            ]
        )

        # Check next page for loop and stop if there's no more.
        page = raw_response["meta"]["pagination"]["next-page"]

        # Terraform Cloud has an API call rate limit of 30 per second.
        time.sleep(delay)

    print(f"Found {len(full_list)} Workspaces.")
    return full_list


def list_resources(
    workspace_id: str,
    token: str,
    api_url: str,
    page_size: int,
    delay: float
) -> list[dict]:
    """List all resources for a Workspace."""
    full_list = []
    page = 1

    # Loop through the resource list pagination.
    while page is not None:

        # Resources endpoint.
        endpoint = f"/workspaces/{workspace_id}/resources"

        # Query string parameters for filtering.
        query = (
            f"page%5Bnumber%5D={page}"
            f"&page%5Bsize%5D={page_size}"
        )

        # Headers.
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/vnd.api+json",
        }

        # Make the API call and get the response.
        print(f"Getting page {page} of resources for Workspace {workspace_id}.")
        raw_response = requests.get(
            f"{api_url}/{endpoint}?{query}",
            headers=headers
        ).json()

        # Add data from current page to the full list.
        full_list.extend(
            [
                {
                    "id": resource["id"],
                    "name": resource["attributes"]["name"],
                    "provider": resource["attributes"]["provider"],
                    "address": resource["attributes"]["address"]
                } for resource in raw_response["data"]
            ]
        )

        # Check next page for loop and stop if there's no more.
        page = raw_response["meta"]["pagination"]["next-page"]

        # Terraform Cloud has an API call rate limit of 30 per second.
        time.sleep(delay)

    print(f"Found {len(full_list)} resources in Workspace {workspace_id}.")
    return full_list


def get_run_metadata(
    workspace_id: str,
    token: str,
    api_url: str
) -> dict:
    """Get Run details for a Workspace."""
    # Runs endpoint.
    endpoint = f"/workspaces/{workspace_id}/runs"

    # Query string parameters for filtering.
    query = (
        "page%5Bnumber%5D=1"
        "&page%5Bsize%5D=1"
    )

    # Headers.
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/vnd.api+json",
    }

    # Make the API call and get the response.
    raw_response = requests.get(
        f"{api_url}/{endpoint}?{query}",
        headers=headers
    ).json()

    return raw_response["meta"]["status-counts"]


def get_run_details(
    workspace_id: str,
    token: str,
    start_date: str,
    end_date: str,
    api_url: str,
    page_size: int,
    delay: float
) -> dict:
    """Get Run times for a Workspace."""
    full_list = []
    page = 1

    # Loop through the Run list pagination.
    while page is not None:

        # Runs endpoint.
        endpoint = f"/workspaces/{workspace_id}/runs"

        # Query string parameters for filtering.
        query = (
            f"page%5Bnumber%5D={page}"
            f"&page%5Bsize%5D={page_size}"
        )

        # Headers.
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/vnd.api+json",
        }

        # Make the API call and get the response.
        print(f"Getting page {page} of Runs.")
        raw_response = requests.get(
            f"{api_url}/{endpoint}?{query}",
            headers=headers
        ).json()

        try:

            # Add data from current page to the full list.
            full_list.extend(
                [
                    {
                        "id": run["id"],
                        "status": run["attributes"]["status"],
                        "time": calculate_timerange(
                            run["attributes"]["status-timestamps"]["planning-at"],
                            run["attributes"]["status-timestamps"][
                                f"{run['attributes']['status'].replace('_', '-')}"
                                "-at"]
                        )
                    } for run in raw_response["data"]
                    if (
                        calculate_time(
                            run["attributes"]["status-timestamps"]["planning-at"]
                        ) >= calculate_date(start_date)
                    ) and (
                        calculate_time(
                            run["attributes"]["status-timestamps"][
                                f"{run['attributes']['status'].replace('_', '-')}"
                                "-at"]
                        ) <= calculate_date(end_date)
                    )
                ]
            )

        except KeyError:

            print("Skipping run due to missing attribute(s).")

        # Ensure data is within range, or break out of the loop if not.
        try:

            if (
                calculate_time(
                    raw_response["data"][-1]["attributes"]["status-timestamps"][
                        f"{raw_response['data'][-1]['attributes']['status'].replace('_', '-')}"
                        "-at"]
                ) < calculate_date(start_date)
            ):
                break

        except IndexError:

            print("No runs to process. This Workspace might use a local backend execution.")
            break

        except KeyError:

            print("Skipping run due to missing attribute(s).")
            break

        # Check next page for loop and stop if there's no more.
        page = raw_response["meta"]["pagination"]["next-page"]

        # Terraform Cloud has an API call rate limit of 30 per second.
        time.sleep(delay)

    # Sum the number of Runs.
    all_runs = len(full_list)

    # Sum the number of successful applies.
    successful_applies = len([
        run["id"] for run in full_list
        if run["status"] == "applied"
    ])

    # Sum the timeranges for all Runs.
    total_time = sum_timeranges(full_list)

    return {
        "workspace_id": workspace_id,
        "all_runs": all_runs,
        "successful_applies": successful_applies,
        "total_time": total_time
    }


def analyze_runs(
    workspaces: list,
    token: str,
    start_date: str,
    end_date: str,
    mode: str,
    api_url: str,
    page_size: int,
    delay: float
) -> list[dict]:
    """Analyze Runs by Workspace."""
    full_list = []

    # Initialize date range for Run lookups.
    start_date = (
        "1970-01-01T00:00:00+00:00"
        if start_date == "all"
        else f"{start_date}T00:00:00+00:00"
    )
    end_date = (
        f"{str(dt.now().date())}T23:59:59+00:00"
        if end_date == "all"
        else f"{end_date}T23:59:59+00:00"
    )

    # Loop through Workspaces.
    for workspace in workspaces:

        # Get Runs by Workspace.
        print(f"Getting Run data for Workspace {workspace['name']}.")

        # Simple mode.
        if mode == "basic":
            runs = get_run_metadata(
                workspace["id"],
                token,
                api_url
            )

            # Add data to the full list.
            full_list.append(
                {
                    "workspace": workspace["name"],
                    "all_runs": runs["total"],
                    "successful_applies": runs["applied"]
                }
            )

        # Advanced mode.
        if mode == "advanced":
            runs = get_run_details(
                workspace["id"],
                token,
                start_date,
                end_date,
                api_url,
                page_size,
                delay
            )

            # Add data to the full list.
            full_list.append(
                {
                    "workspace": workspace["name"],
                    "all_runs": runs["all_runs"],
                    "successful_applies": runs["successful_applies"],
                    "total_time": runs["total_time"]
                }
            )

        # Terraform Cloud has an API call rate limit of 30 per second.
        time.sleep(delay)

    return full_list


def create_csv(
    data: list,
    filename: str,
    mode: str
) -> None:
    """Create CSV file from Workspace Run data."""
    import csv

    # Create CSV file.
    print(f"Creating CSV file {filename}.")
    with open(filename, "w", newline="") as file:
        writer = csv.writer(file)

        # Create field names based on mode.
        if mode == "basic":
            field = [
                "workspace",
                "all_runs",
                "successful_applies"
            ]
        if mode == "advanced":
            field = [
                "workspace",
                "all_runs",
                "successful_applies",
                "total_time"
            ]

        writer.writerow(field)

        # Write data to CSV file.
        print(f"Writing data to {filename}.")
        for datapoint in data:
            writer.writerow(datapoint)


def main():
    """Execute module as a script."""
    import argparse

    # Get and parse command line arguments.
    myparser = argparse.ArgumentParser(
        add_help=True,
        allow_abbrev=False,
        description="Retrieve and analyze Terraform Cloud usage data.",
        usage="%(prog)s [options]"
    )
    myparser.add_argument(
        "-V",
        "--version",
        action="version",
        version=f"{__file__} {__version__}"
    )
    myparser.add_argument(
        "-o",
        "--organization",
        action="store",
        help="[REQUIRED] Terraform Cloud organization name",
        required=True,
        type=str
    )
    myparser.add_argument(
        "-t",
        "--token",
        action="store",
        help="[REQUIRED] Terraform Cloud API token",
        required=True,
        type=str
    )
    myparser.add_argument(
        "-k",
        "--keyword",
        action="store",
        help="[OPTIONAL: default = all] Terraform Cloud Workspace name pattern",
        required=False,
        default="all",
        type=str
    )
    myparser.add_argument(
        "-f",
        "--filename",
        action="store",
        help="[OPTIONAL: default = report.csv] CSV report filename",
        required=False,
        default="report.csv",
        type=str
    )
    myparser.add_argument(
        "-s",
        "--start_date",
        action="store",
        help="[OPTIONAL: default = all] start date for advanced mode Run lookups",
        required=False,
        default="all",
        type=str
    )
    myparser.add_argument(
        "-e",
        "--end_date",
        action="store",
        help="[OPTIONAL: default = all] end date for advanced mode Run lookups",
        required=False,
        default="all",
        type=str
    )
    myparser.add_argument(
        "-m",
        "--mode",
        action="store",
        help="[OPTIONAL: default = basic] execution mode (basic or advanced)",
        required=False,
        default="basic",
        type=str
    )
    myparser.add_argument(
        "-u",
        "--url",
        action="store",
        help="[OPTIONAL: default = https://app.terraform.io/api/v2] Terraform Cloud API URL",
        required=False,
        default="https://app.terraform.io/api/v2",
        type=str
    )
    myparser.add_argument(
        "-p",
        "--page-size",
        action="store",
        help="[OPTIONAL: default = 50] number of items per page",
        required=False,
        default=50,
        type=int
    )
    myparser.add_argument(
        "-d",
        "--delay",
        action="store",
        help="[OPTIONAL: default = 1.0] delay (in seconds) between API calls",
        required=False,
        default=1.0,
        type=float
    )
    args = myparser.parse_args()
    organization = args.organization
    token = args.token
    keyword = args.keyword
    filename = args.filename
    start_date = args.start_date
    end_date = args.end_date
    mode = args.mode
    api_url = args.url
    page_size = args.page_size
    delay = args.delay

    # Print run parameters.
    print("Run parameters:")
    print(f"Organization: {organization}")
    print(f"Keyword: {keyword}")
    print(f"Filename: {filename}")
    print(f"Start date: {start_date}")
    print(f"End date: {end_date}")
    print(f"Mode: {mode}")
    print(f"API URL: {api_url}")
    print(f"Page size: {page_size}")
    print(f"Delay: {delay}")
    print("-------")

    # Get Workspaces.
    workspaces = list_workspaces(
        organization,
        token,
        keyword,
        api_url,
        page_size,
        delay
    )

    # Analyze Runs.
    runs = analyze_runs(
        workspaces,
        token,
        start_date,
        end_date,
        mode,
        api_url,
        page_size,
        delay
    )

    # Create CSV file from data.
    create_csv(
        [run.values() for run in runs],
        filename,
        mode
    )
