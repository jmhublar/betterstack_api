#!/usr/bin/env python3

import os
import sys
import argparse
import requests
import json

BASE_URL = "https://uptime.betterstack.com/api/v2/incidents"

def fetch_incidents_page(
    api_key, 
    url=None, 
    page=1, 
    per_page=50, 
    from_date=None, 
    to_date=None, 
    monitor_id=None, 
    heartbeat_id=None
):
    """
    Fetch a single page of incidents from the BetterStack Incidents API.
    Either by building the URL with query params (page/per_page) or by 
    using a full 'next' link if provided.

    Returns the JSON response as a dict.
    """
    if not url:
        # Build the initial URL for the first page
        url = BASE_URL
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    
    # If we haven't been given a full 'next' URL, build params
    params = {}
    if page:
        params["page"] = page
    if per_page:
        params["per_page"] = per_page
    if from_date:
        params["from"] = from_date
    if to_date:
        params["to"] = to_date
    if monitor_id:
        params["monitor_id"] = monitor_id
    if heartbeat_id:
        params["heartbeat_id"] = heartbeat_id

    # If we have a 'next' URL, it already includes query params,
    # so only attach params if 'url' is still the base endpoint.
    if url == BASE_URL:
        response = requests.get(url, headers=headers, params=params)
    else:
        response = requests.get(url, headers=headers)
    
    response.raise_for_status()
    return response.json()

def fetch_all_incidents(
    api_key, 
    from_date=None, 
    to_date=None, 
    monitor_id=None, 
    heartbeat_id=None, 
    per_page=50
):
    """
    Fetch ALL incidents by following pagination.next link until it's null.
    Returns a list of all incident objects (each is a dict).
    """
    all_incidents = []
    
    # Start by fetching page=1
    current_page_data = fetch_incidents_page(
        api_key=api_key,
        page=1,
        per_page=per_page,
        from_date=from_date,
        to_date=to_date,
        monitor_id=monitor_id,
        heartbeat_id=heartbeat_id
    )
    
    while True:
        incidents_page = current_page_data.get("data", [])
        all_incidents.extend(incidents_page)

        pagination = current_page_data.get("pagination", {})
        next_url = pagination.get("next")
        
        if not next_url:
            break
        
        # Fetch the next page using the 'next' URL
        current_page_data = fetch_incidents_page(
            api_key=api_key,
            url=next_url,
        )
    
    return all_incidents

def main():
    parser = argparse.ArgumentParser(
        description="Fetch all incidents from BetterStack's Incidents API, output as JSON array."
    )
    parser.add_argument(
        "--api-key",
        default=None,
        help="BetterStack API key (or set BETTERSTACK_API_KEY env var)."
    )
    parser.add_argument(
        "--from-date",
        default=None,
        help="Fetch incidents starting from this date (YYYY-MM-DD)."
    )
    parser.add_argument(
        "--to-date",
        default=None,
        help="Fetch incidents until this date (YYYY-MM-DD)."
    )
    parser.add_argument(
        "--monitor-id",
        type=int,
        default=None,
        help="Filter by Monitor ID."
    )
    parser.add_argument(
        "--heartbeat-id",
        type=int,
        default=None,
        help="Filter by Heartbeat ID."
    )
    parser.add_argument(
        "--per-page",
        type=int,
        default=50,
        help="Number of incidents per page (default=50)."
    )
    args = parser.parse_args()

    # Resolve API key from CLI or environment
    api_key = args.api_key or os.getenv("BETTERSTACK_API_KEY")
    if not api_key:
        print("Error: No API key provided (use --api-key or set BETTERSTACK_API_KEY).", file=sys.stderr)
        sys.exit(1)

    # Fetch incidents
    incidents = fetch_all_incidents(
        api_key=api_key,
        from_date=args.from_date,
        to_date=args.to_date,
        monitor_id=args.monitor_id,
        heartbeat_id=args.heartbeat_id,
        per_page=args.per_page
    )

    # Print as a single JSON array
    # so we can pipe it into `jq` for further processing.
    print(json.dumps(incidents, indent=2))

if __name__ == "__main__":
    main()
