# Braze MCP Server

A Model Context Protocol (MCP) server that provides comprehensive access to Braze's REST API through Large Language Model tooling. This server enables AI assistants and other MCP clients to interact with your Braze workspace data, analytics, and campaign management functions.  This server only supports read-only API's that don't return PII.

## Table of Contents

- [Overview](#overview)
- [Prerequisites](#prerequisites)
- [Quick Start with PyPI](#quick-start-with-pypi)
- [MCP Client Configuration](#mcp-client-configuration)
  - [Claude Desktop](#claude-desktop)
  - [Cursor](#cursor)
- [Usage Examples](#usage-examples)
- [Troubleshooting](#troubleshooting)
  - [Installation Issues](#installation-issues)
  - [Configuration Issues](#configuration-issues)
  - [Getting Help](#getting-help)
- [Contributing](#contributing)

## Overview

This MCP server exposes **2 main tools** that provide access to **42 Braze API functions** across 16 different categories:

### Main MCP Tools

- **`list_functions`** - Lists all available Braze API functions with their descriptions and parameters
- **`call_function`** - Calls a specific Braze API function with provided parameters

### Available Braze API Functions

#### Campaigns (3 functions)
- `get_campaign_list` - [Export a list of campaigns with metadata](https://www.braze.com/docs/api/endpoints/export/campaigns/get_campaigns)
- `get_campaign_details` - [Get detailed information about specific campaigns](https://www.braze.com/docs/api/endpoints/export/campaigns/get_campaign_details)
- `get_campaign_dataseries` - [Retrieve time series analytics data for campaigns](https://www.braze.com/docs/api/endpoints/export/campaigns/get_campaign_analytics)

#### Canvases (4 functions)
- `get_canvas_list` - [Export a list of Canvases with metadata](https://www.braze.com/docs/api/endpoints/export/canvas/get_canvases)
- `get_canvas_details` - [Get detailed information about specific Canvases](https://www.braze.com/docs/api/endpoints/export/canvas/get_canvas_details)
- `get_canvas_data_summary` - [Get summary analytics for Canvas performance](https://www.braze.com/docs/api/endpoints/export/canvas/get_canvas_analytics_summary)
- `get_canvas_data_series` - [Retrieve time series analytics data for Canvases](https://www.braze.com/docs/api/endpoints/export/canvas/get_canvas_analytics)

#### Catalogs (3 functions)
- `get_catalogs` - [Return a list of catalogs in a workspace](https://www.braze.com/docs/api/endpoints/catalogs/catalog_management/synchronous/get_list_catalogs)
- `get_catalog_items` - [Return multiple catalog items and their content with pagination support](https://www.braze.com/docs/api/endpoints/catalogs/catalog_items/synchronous/get_catalog_items_details_bulk)
- `get_catalog_item` - [Return a specific catalog item and its content by ID](https://www.braze.com/docs/api/endpoints/catalogs/catalog_items/synchronous/get_catalog_item_details)

#### Custom Attributes (1 function)
- `get_custom_attributes` - [Export custom attributes recorded for your app](https://www.braze.com/docs/api/endpoints/export/canvas/get_canvas_analytics)

#### Events (3 functions)
- `get_events_list` - [Export a list of custom events recorded for your app](https://www.braze.com/docs/api/endpoints/export/custom_events/get_custom_events)
- `get_events_data_series` - [Retrieve time series data for custom events](https://www.braze.com/docs/api/endpoints/export/custom_events/get_custom_events_analytics)
- `get_events` - [Get detailed event data with pagination support](https://www.braze.com/docs/api/endpoints/export/custom_events/get_custom_events_data)

#### KPI Analytics (4 functions)
- `get_new_users_data_series` - [Daily series of new user counts](https://www.braze.com/docs/api/endpoints/export/kpi/get_kpi_daily_new_users_date)
- `get_dau_data_series` - [Daily Active Users time series data](https://www.braze.com/docs/api/endpoints/export/kpi/get_kpi_dau_date)
- `get_mau_data_series` - [Monthly Active Users time series data](https://www.braze.com/docs/api/endpoints/export/kpi/get_kpi_mau_30_days)
- `get_uninstalls_data_series` - [App uninstall time series data](https://www.braze.com/docs/api/endpoints/export/kpi/get_kpi_uninstalls_date)

#### Purchases (3 functions)
- `get_product_list` - [Export paginated list of product IDs](https://www.braze.com/docs/api/endpoints/export/purchases/get_list_product_id)
- `get_revenue_series` - [Revenue analytics time series data](https://www.braze.com/docs/api/endpoints/export/purchases/get_revenue_series)
- `get_quantity_series` - [Purchase quantity time series data](https://www.braze.com/docs/api/endpoints/export/purchases/get_number_of_purchases)

#### Segments (3 functions)
- `get_segment_list` - [Export list of segments with analytics tracking status](https://www.braze.com/docs/api/endpoints/export/segments/get_segment)
- `get_segment_data_series` - [Time series analytics data for segments](https://www.braze.com/docs/api/endpoints/export/segments/get_segment_analytics)
- `get_segment_details` - [Detailed information about specific segments](https://www.braze.com/docs/api/endpoints/export/segments/get_segment_details)

#### Sends (1 function)
- `get_send_data_series` - [Daily analytics for tracked campaign sends](https://www.braze.com/docs/api/endpoints/export/campaigns/get_send_analytics)

#### Sessions (1 function)
- `get_session_data_series` - [Time series data for app session counts](https://www.braze.com/docs/api/endpoints/export/sessions/get_sessions_analytics)

#### Subscription Groups (2 functions)
- `get_user_subscription_groups` - [List and get the subscription groups of a certain user](https://www.braze.com/docs/api/endpoints/subscription_groups/get_list_user_subscription_groups)
- `get_subscription_group_status` - [Get the subscription state of a user in a subscription group](https://www.braze.com/docs/api/endpoints/subscription_groups/get_list_user_subscription_group_status)

#### SDK Authentication (1 function)
- `get_sdk_authentication_keys` - [List all SDK Authentication keys for your app](https://www.braze.com/docs/api/endpoints/sdk_authentication/get_sdk_authentication_keys)

#### Messages (1 function)
- `get_scheduled_broadcasts` - [List upcoming scheduled campaigns and Canvases](https://www.braze.com/docs/api/endpoints/messaging/schedule_messages/get_messages_scheduled)

#### Preference Centers (2 functions)
- `get_preference_centers` - [List your available preference centers](https://www.braze.com/docs/api/endpoints/preference_center/get_list_preference_center)
- `get_preference_center_details` - [View details for a specific preference center including HTML content and options](https://www.braze.com/docs/api/endpoints/preference_center/get_view_details_preference_center)

#### Templates (4 functions)
- `get_content_blocks_list` - [List your available content blocks](https://www.braze.com/docs/api/endpoints/templates/content_blocks_templates/get_list_email_content_blocks)
- `get_content_blocks_info` - [Get information on your content blocks](https://www.braze.com/docs/api/endpoints/templates/content_blocks_templates/get_see_email_content_blocks_information)
- `get_email_templates_list` - [List your available email templates](https://www.braze.com/docs/api/endpoints/templates/email_templates/get_list_email_templates)
- `get_email_template_info` - [Get information on your email templates](https://www.braze.com/docs/api/endpoints/templates/email_templates/get_see_email_template_information)

#### CDI Integrations (2 functions)
- `list_integrations` - [Return a list of existing CDI integrations](https://www.braze.com/docs/api/endpoints/cdi/get_integration_list)
- `get_integration_job_sync_status` - [Return past sync statuses for a given CDI integration](https://www.braze.com/docs/api/endpoints/cdi/get_job_sync_status)


## Prerequisites

This project uses [uv](https://github.com/astral-sh/uv) for dependency management and Python package handling.

### Installing uv

**macOS and Linux:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

For more installation options, see the [uv documentation](https://docs.astral.sh/uv/getting-started/installation/).

### API key creation

Follow the steps in the [Braze documentation](https://www.braze.com/docs/api/basics/#creating-rest-api-keys) to create a new API key.  We highly recommend using a separate key for your MCP integration to ensure that the correct scopes are selected. Below is a mapping of endpoints to their required API key scopes:

| Endpoint | Required API Key Scope |
|----------|------------------------|
| `/custom_attributes/list` | `custom_attributes.get` |
| `/campaigns/data_series` | `campaigns.data_series` |
| `/campaigns/details` | `campaigns.details` |
| `/campaigns/list` | `campaigns.list` |
| `/catalogs` | `catalogs.get` |
| `/catalogs/{catalog_name}/items` | `catalogs.get_items` |
| `/catalogs/{catalog_name}/items/{item_id}` | `catalogs.get_item` |
| `/sends/data_series` | `sends.data_series` |
| `/canvas/data_series` | `canvas.data_series` |
| `/canvas/data_summary` | `canvas.data_summary` |
| `/canvas/details` | `canvas.details` |
| `/canvas/list` | `canvas.list` |
| `/events/list` | `events.list` |
| `/events/data_series` | `events.data_series` |
| `/events` | `events.get` |
| `/kpi/new_users/data_series` | `kpi.new_users.data_series` |
| `/kpi/dau/data_series` | `kpi.dau.data_series` |
| `/kpi/mau/data_series` | `kpi.mau.data_series` |
| `/kpi/uninstalls/data_series` | `kpi.uninstalls.data_series` |
| `/purchases/product_list` | `purchases.product_list` |
| `/purchases/revenue_series` | `purchases.revenue_series` |
| `/purchases/quantity_series` | `purchases.quantity_series` |
| `/preference_center/v1/list` | `preference_center.list` |
| `/preference_center/v1/{id}` | `preference_center.get` |
| `/segments/list` | `segments.list` |
| `/segments/data_series` | `segments.data_series` |
| `/segments/details` | `segments.details` |
| `/sessions/data_series` | `sessions.data_series` |
| `/subscription/user/status` | `subscription.groups.get` |
| `/subscription/status/get` | `subscription.status.get` |
| `/app_group/sdk_authentication/keys` | `sdk_authentication.keys` |
| `/messages/scheduled_broadcasts` | `messages.schedule_broadcasts` |
| `/cdi/integrations` | `cdi.integration_list` |
| `/cdi/integrations/{integration_id}/job_sync_status` | `cdi.integration_job_status` |
| `/content_blocks/list` | `content_blocks.list` |
| `/content_blocks/info` | `content_blocks.info` |
| `/templates/email/list` | `templates.email.list` |
| `/templates/email/info` | `templates.email.info` |

> ⚠️ **WARNING**: Ensure you do not add more scopes than required to ensure the agent does not have the ability to make writes or deletes!

**Required environment variables**
The following values are required for the server to run:

- **`BRAZE_BASE_URL`** - Your Braze REST endpoint (e.g., `https://rest.iad-01.braze.com`)
- **`BRAZE_API_KEY`** - Your Braze API key with appropriate permissions

For more information about creating or retrieving these values, see [the Braze API documentation](https://www.braze.com/docs/api/basics/#braze-rest-api-collection).

## Quick Start with PyPI

The Braze MCP server is available on PyPI and can be used directly in your MCP client configuration without manual installation.

## MCP Client Configuration

> **Note**: If you encounter `spawn uvx ENOENT` or similar `uvx` execution errors, you may need to specify the full path to `uvx` instead of just `"uvx"` in your configuration. Use `which uvx` to find your `uvx` path, then replace `"command": "uvx"` with `"command": "/Users/your-username/.local/bin/uvx"` (or your actual path).

### Claude Desktop

1. Download [Claude Desktop](https://claude.ai/desktop).
2. Open Claude Desktop. Within **Settings > Developer > Edit Config**, add the following, substituting your API key and base URL:

```json
{
  "mcpServers": {
    "braze": {
      "command": "uvx",
      "args": ["--native-tls", "braze-mcp-server@latest"],
      "env": {
        "BRAZE_API_KEY": "your-braze-api-key-here",
        "BRAZE_BASE_URL": "https://rest.iad-01.braze.com"
      }
    }
  }
}
```

3. Save the configuration and restart Claude Desktop.
4. Verify the connection by asking a question like "List my Braze campaigns".

### Cursor

1. Download [Cursor](https://cursor.sh/).
2. Open Cursor. Within **Settings > Cursor Settings > MCP Tools > Add Custom MCP**, add the following configuration:

```json
{
  "mcpServers": {
    "braze": {
      "command": "uvx",
      "args": ["--native-tls", "braze-mcp-server@latest"],
      "env": {
        "BRAZE_API_KEY": "your-braze-api-key-here",
        "BRAZE_BASE_URL": "https://rest.iad-01.braze.com"
      }
    }
  }
}
```

3. Save the configuration and restart Cursor.
4. Verify the connection by using the MCP tools to interact with your Braze data.

## Usage Examples

### Working with Agents

Once installed and configured in Cursor / Claude, you can interact with your Braze data using natural language:

**"Show me my recent canvases"**
```
The agent will use the MCP server to call get_canvas_list and display your canvases with their IDs, names, and last edited dates.
```

**"Get details about canvas ID 401cc9b3-d9bf-4c73-ac9f-e9dca46d2a36"**
```
The agent will retrieve detailed canvas information including steps, variants, schedule type, and current status.
```

**"What are my available Braze API functions?"**
```
The agent will list all 38 available functions across campaigns, canvases, catalogs, events, KPIs, segments, purchases, sessions, SDK authentication, messages, CDI integrations, templates, and more.
```

## Troubleshooting

### Installation Issues

**Problem**: `uvx` command not found
```bash
# Solution: Install uv first
curl -LsSf https://astral.sh/uv/install.sh | sh
# Then restart your terminal
```

**Problem**: Package installation fails
```bash
# Solution: Try installing with explicit Python version
uvx --python 3.12 braze-mcp-server@latest
```

### Configuration Issues

**Problem**: MCP client can't find the Braze server
1. Verify your MCP client configuration syntax is correct
2. Restart your MCP client after configuration changes
3. Check that `uvx` is in your system PATH

**Problem**: Authentication errors
1. Verify your `BRAZE_API_KEY` is correct and active
2. Ensure your `BRAZE_BASE_URL` matches your Braze instance
3. Check that your API key has the required scopes (see Prerequisites section)

**Problem**: Connection timeouts or network errors
1. Verify your `BRAZE_BASE_URL` is correct for your instance
2. Check your network connection and firewall settings
3. Ensure you're using HTTPS in your base URL

### Getting Help

If you encounter issues not covered here:

1. **Check the logs**: Your MCP client may provide error details in its logs or console
2. **Verify API access**: Test your API key directly with Braze's API documentation
3. **Start fresh**: Try creating a new API key with the required scopes
4. **Report issues**: Open an issue on the project repository with:
   - Your MCP client (Claude Desktop, Cursor, etc.)
   - Error messages or logs
   - Your configuration (with API key redacted)
