# Braze MCP Server

A Model Context Protocol (MCP) server that provides comprehensive access to Braze's REST API through Large Language Model tooling. This server enables AI assistants and other MCP clients to interact with your Braze workspace data, analytics, and campaign management functions.  This server only supports read-only API's that don't return PII.

## Table of Contents

- [Overview](#overview)
- [Quick Start with PyPI](#quick-start-with-pypi)
- [MCP Client Configuration](#mcp-client-configuration)
  - [Claude Desktop](#claude-desktop)
  - [Cursor](#cursor)
- [Prerequisites](#prerequisites)
- [Usage Examples](#usage-examples)
- [Troubleshooting](#troubleshooting)
  - [Installation Issues](#installation-issues)
  - [Configuration Issues](#configuration-issues)
  - [Getting Help](#getting-help)
  - [Common Error Messages](#common-error-messages)
- [Contributing](#contributing)

## Overview

This MCP server exposes **2 main tools** that provide access to **38 Braze API functions** across 15 different categories:

### Main MCP Tools

- **`list_functions`** - Lists all available Braze API functions with their descriptions and parameters
- **`call_function`** - Calls a specific Braze API function with provided parameters

### Available Braze API Functions

#### Campaigns (3 functions)
- `get_campaign_list` - Export a list of campaigns with metadata
- `get_campaign_details` - Get detailed information about specific campaigns  
- `get_campaign_dataseries` - Retrieve time series analytics data for campaigns

#### Canvases (4 functions)
- `get_canvas_list` - Export a list of Canvases with metadata
- `get_canvas_details` - Get detailed information about specific Canvases
- `get_canvas_data_summary` - Get summary analytics for Canvas performance
- `get_canvas_data_series` - Retrieve time series analytics data for Canvases

#### Catalogs (3 functions)
- `get_catalogs` - Return a list of catalogs in a workspace
- `get_catalog_items` - Return multiple catalog items and their content with pagination support
- `get_catalog_item` - Return a specific catalog item and its content by ID

#### Custom Attributes (1 function)
- `get_custom_attributes` - Export custom attributes recorded for your app

#### Events (3 functions)
- `get_events_list` - Export a list of custom events recorded for your app
- `get_events_data_series` - Retrieve time series data for custom events
- `get_events` - Get detailed event data with pagination support

#### KPI Analytics (4 functions)
- `get_new_users_data_series` - Daily series of new user counts
- `get_dau_data_series` - Daily Active Users time series data
- `get_mau_data_series` - Monthly Active Users time series data  
- `get_uninstalls_data_series` - App uninstall time series data

#### Purchases (3 functions)
- `get_product_list` - Export paginated list of product IDs
- `get_revenue_series` - Revenue analytics time series data
- `get_quantity_series` - Purchase quantity time series data

#### Segments (3 functions)
- `get_segment_list` - Export list of segments with analytics tracking status
- `get_segment_data_series` - Time series analytics data for segments
- `get_segment_details` - Detailed information about specific segments

#### Sends (1 function)
- `get_send_data_series` - Daily analytics for tracked campaign sends

#### Sessions (1 function)
- `get_session_data_series` - Time series data for app session counts

#### Subscription Groups (2 functions)
- `get_user_subscription_groups` - List and get the subscription groups of a certain user
- `get_subscription_group_status` - Get the subscription state of a user in a subscription group

#### SDK Authentication (1 function)
- `get_sdk_authentication_keys` - List all SDK Authentication keys for your app

#### Messages (1 function)
- `get_scheduled_broadcasts` - List upcoming scheduled campaigns and Canvases

#### Preference Centers (2 functions)
- `get_preference_centers` - List your available preference centers
- `get_preference_center_details` - View details for a specific preference center including HTML content and options

#### CDI Integrations (2 functions)
- `list_integrations` - Return a list of existing CDI integrations
- `get_integration_job_sync_status` - Return past sync statuses for a given CDI integration


## Quick Start with PyPI

The easiest way to use the Braze MCP server is through PyPI installation with `uvx`:

```bash
# Install and run directly
uvx braze-mcp-server@latest
```

## MCP Client Configuration

### Claude Desktop

1. Download [Claude Desktop](https://claude.ai/desktop).
2. Open Claude Desktop. Within **Settings > Developer > Edit Config**, add the following, substituting your API key and base URL:

```json
{
  "mcpServers": {
    "braze": {
      "command": "uvx",
      "args": ["braze-mcp-server@latest"],
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
      "args": ["braze-mcp-server@latest"],
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

## Usage Examples

### Working with Cursor

Once installed and configured in Cursor, you can interact with your Braze data using natural language:

**"Show me my recent canvases"**
```
Cursor will use the MCP server to call get_canvas_list and display your canvases with their IDs, names, and last edited dates.
```

**"Get details about canvas ID 401cc9b3-d9bf-4c73-ac9f-e9dca46d2a36"**
```
Cursor will retrieve detailed canvas information including steps, variants, schedule type, and current status.
```

**"What are my available Braze API functions?"**
```
Cursor will list all 38 available functions across campaigns, canvases, catalogs, events, KPIs, segments, purchases, sessions, SDK authentication, messages, CDI integrations, templates, and more.
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

### Common Error Messages

**"Invalid API key"**
- Double-check your `BRAZE_API_KEY` environment variable
- Ensure the API key is active in your Braze dashboard

**"Endpoint not found" or "404 errors"**
- Verify your `BRAZE_BASE_URL` matches your Braze instance location
- Check that the URL includes `https://` and ends without a trailing slash

**"Permission denied" or "403 errors"**
- Ensure your API key has the required scopes listed in the Prerequisites section
- Some endpoints may require additional permissions in your Braze workspace
