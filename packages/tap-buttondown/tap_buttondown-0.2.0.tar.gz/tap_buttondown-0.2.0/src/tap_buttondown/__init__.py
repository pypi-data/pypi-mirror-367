import json
import os
import sys
from typing import Dict, Any
import requests
from singer import get_bookmark, write_record, write_schema, get_logger, parse_args
from singer.catalog import Catalog, CatalogEntry, Schema
from singer.utils import strptime_to_utc


REQUIRED_CONFIG_KEYS = ["api_key"]
CONFIG = {}
STATE = {}
LOGGER = get_logger()


class ButtondownAPI:
    """Client for the Buttondown API"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.buttondown.email/v1"
        self.headers = {
            "Authorization": f"Token {api_key}",
            "Content-Type": "application/json"
        }
    
    def get_subscribers(self, page: int = 1, page_size: int = 100) -> Dict[str, Any]:
        """Fetch subscribers from Buttondown API"""
        url = f"{self.base_url}/subscribers"
        params = {
            "page": page,
            "page_size": page_size
        }
        
        response = requests.get(url, headers=self.headers, params=params)
        response.raise_for_status()
        
        return response.json()


def get_abs_path(path: str) -> str:
    """Get absolute path"""
    return os.path.join(os.path.dirname(os.path.realpath(__file__)), path)


def load_schemas() -> Dict[str, Schema]:
    """Load schemas from schemas folder"""
    schemas = {}
    
    # Define subscriber schema based on actual API response
    subscriber_schema = {
        "type": "object",
        "properties": {
            "id": {"type": "string"},
            "creation_date": {"type": "string", "format": "date-time"},
            "email_address": {"type": "string"},
            "notes": {"type": "string"},
            "metadata": {"type": "object"},
            "tags": {"type": "array", "items": {"type": "string"}},
            "referrer_url": {"type": "string"},
            "secondary_id": {"type": "integer"},
            "type": {"type": "string"},
            "source": {"type": "string"},
            "utm_campaign": {"type": "string"},
            "utm_medium": {"type": "string"},
            "utm_source": {"type": "string"},
            "referral_code": {"type": "string"},
            "avatar_url": {"type": "string"},
            "stripe_coupon": {"type": ["null", "string"]},
            "unsubscription_date": {"type": ["null", "string"], "format": "date-time"},
            "churn_date": {"type": ["null", "string"], "format": "date-time"},
            "undeliverability_date": {"type": ["null", "string"], "format": "date-time"},
            "undeliverability_reason": {"type": ["null", "string"]},
            "upgrade_date": {"type": ["null", "string"], "format": "date-time"},
            "unsubscription_reason": {"type": "string"},
            "transitions": {"type": "array", "items": {"type": "object"}},
            "ip_address": {"type": "string"},
            "last_open_date": {"type": ["null", "string"], "format": "date-time"},
            "last_click_date": {"type": ["null", "string"], "format": "date-time"},
            "stripe_customer_id": {"type": ["null", "string"]},
            "subscriber_import_id": {"type": ["null", "string"]},
            "risk_score": {"type": "number"},
            "stripe_customer": {"type": ["null", "object"]}
        }
    }
    
    schemas["subscribers"] = Schema.from_dict(subscriber_schema)
    
    return schemas


def discover() -> Catalog:
    """Discover available streams and schemas"""
    schemas = load_schemas()
    streams = []
    
    for stream_id, schema in schemas.items():
        key_properties = ["id"]
        replication_key = "creation_date"
        
        stream_metadata = [
            {
                "metadata": {
                    "inclusion": "available",
                    "table-key-properties": key_properties,
                    "valid-replication-keys": [replication_key],
                    "schema-name": stream_id,
                },
                "breadcrumb": []
            }
        ]
        
        catalog_entry = CatalogEntry(
            stream=stream_id,
            tap_stream_id=stream_id,
            schema=schema,
            key_properties=key_properties,
            replication_key=replication_key,
            metadata=stream_metadata,
            replication_method="INCREMENTAL"
        )
        
        streams.append(catalog_entry)
    
    return Catalog(streams)


def sync_subscribers(config: Dict[str, Any], state: Dict[str, Any], catalog: Catalog) -> None:
    """Sync subscribers stream"""
    api = ButtondownAPI(config["api_key"])
    
    # Get the subscribers stream from catalog
    subscribers_catalog = catalog.get_stream("subscribers")
    if not subscribers_catalog:
        LOGGER.error("Subscribers stream not found in catalog")
        return
    
    bookmark_column = subscribers_catalog.replication_key
    
    start = get_bookmark(state, "subscribers", bookmark_column, config.get("start_date"))
    if start:
        start = strptime_to_utc(start)
    
    write_schema("subscribers", subscribers_catalog.schema.to_dict(), key_properties=["id"])
    
    page = 1
    total_records = 0
    
    while True:
        try:
            response = api.get_subscribers(page=page, page_size=100)
            
            if not response.get("results"):
                break
            
            subscribers = response["results"]
            
            for subscriber in subscribers:
                # Write record (no transformations needed as API returns correct format)
                write_record("subscribers", subscriber)
                total_records += 1
            
            # Check if we have more pages using the "next" field
            if not response.get("next"):
                break
            
            page += 1
            
        except requests.exceptions.RequestException as e:
            LOGGER.error(f"Error fetching subscribers: {e}")
            break
    
    LOGGER.info(f"Synced {total_records} subscriber records")


def sync(config: Dict[str, Any], state: Dict[str, Any], catalog: Catalog) -> None:
    """Sync all streams"""
    for stream in catalog.streams:
        if stream.tap_stream_id == "subscribers":
            sync_subscribers(config, state, catalog)


def main() -> None:
    """Main entry point"""
    args = parse_args(REQUIRED_CONFIG_KEYS)
    
    config = args.config
    state = args.state
    catalog = args.catalog if args.catalog else discover()
    
    if args.discover:
        catalog = discover()
        json.dump(catalog.to_dict(), sys.stdout, indent=2)
    else:
        sync(config, state, catalog)


if __name__ == "__main__":
    main()
