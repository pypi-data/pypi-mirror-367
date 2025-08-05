# tap-buttondown

A [Singer](https://singer.io) tap for extracting data from the [Buttondown API](https://buttondown.email/api).

## Installation

```bash
pip install tap-buttondown
```

Or run directly with `uvx`.

```bash
uvx tap-buttondown --help

# Example with CSV target
uvx tap-buttondown --config config.json | uvx --with setuptools target-csv
```

## Configuration

Create a `config.json` file with your Buttondown API key:

```json
{
  "api_key": "your_buttondown_api_key_here"
}
```

You can find your API key in your [Buttondown dashboard](https://buttondown.email/settings/api).

## Usage

### Discover available streams

```bash
tap-buttondown --config config.json --discover
```

This will output a catalog of available streams in JSON format.

### Run the tap

```bash
tap-buttondown --config config.json --catalog catalog.json
```

Or to use the default catalog:

```bash
tap-buttondown --config config.json
```

### State management

To maintain state between runs (for incremental syncs):

```bash
tap-buttondown --config config.json --state state.json
```

## Streams

### Subscribers

The `subscribers` stream extracts subscriber data from your Buttondown newsletter.

**Schema:**
- `id` (string): Unique subscriber ID
- `creation_date` (datetime): When the subscriber was created
- `email_address` (string): Subscriber email address
- `notes` (string): Notes about the subscriber
- `metadata` (object): Custom metadata
- `tags` (array): Tags associated with the subscriber
- `referrer_url` (string): Referrer URL
- `secondary_id` (integer): Secondary identifier
- `type` (string): Subscriber type (e.g., "unactivated", "regular", "undeliverable")
- `source` (string): Source of the subscription
- `utm_campaign` (string): UTM campaign parameter
- `utm_medium` (string): UTM medium parameter
- `utm_source` (string): UTM source parameter
- `referral_code` (string): Referral code
- `avatar_url` (string): Avatar URL
- `stripe_coupon` (string, nullable): Stripe coupon
- `unsubscription_date` (datetime, nullable): When the subscriber unsubscribed
- `churn_date` (datetime, nullable): When the subscriber churned
- `undeliverability_date` (datetime, nullable): When the subscriber became undeliverable
- `undeliverability_reason` (string, nullable): Reason for undeliverability
- `upgrade_date` (datetime, nullable): When the subscriber upgraded
- `unsubscription_reason` (string): Reason for unsubscription
- `transitions` (array): Transition history
- `ip_address` (string): IP address
- `last_open_date` (datetime, nullable): Last email open date
- `last_click_date` (datetime, nullable): Last email click date
- `stripe_customer_id` (string, nullable): Stripe customer ID
- `subscriber_import_id` (string, nullable): Import ID
- `risk_score` (number): Risk score
- `stripe_customer` (object, nullable): Stripe customer data

**Replication Method:** INCREMENTAL
**Replication Key:** `creation_date`

## Development

This project is managed with `uv`.

### Setup

1. Clone the repository
1. Create a `config.json` file with your API key

### Testing

```bash
# Discover streams
uv run tap-buttondown --config config.json --discover

# Run sync
uv run tap-buttondown --config config.json
```

## License

This project is licensed under the MIT License.
