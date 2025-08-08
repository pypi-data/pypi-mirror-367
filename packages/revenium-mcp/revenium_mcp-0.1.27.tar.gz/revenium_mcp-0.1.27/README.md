# Revenium MCP Server

**Connect AI agents to Revenium**

Once you've connected your AI applications to Revenium using any of the supported middleware libraries or via direct API integration, this MCP server allows agents to directly interact with your Revenium account.  Connect Claude, OpenAI, or any MCP-compatible AI assistant to Revenium to configure AI cost alerts & tracking as well as usage-based billing for AI products.

## AI Cost Tracking & Alerting - **Never Be Surprised by Unexpected AI Costs Again**
- Ask AI agents to **set up AI cost alerts to avoid unexpected costs**
- Ask AI agents to track their own costs with Revenium as they carry out actions within your application
- Ask Revenium to **calculate AI cost & usage trends over time** and set up alerts to immediately send slack or email notifications when anomalies occur
- Quickly **investigate the reasons for AI cost spikes**. Identify abnormal changes in spending by agent, API key, product, customer, and more.
- Use AI agents to **integrate Revenium metering into your applications** if not using Revenium's pre-built SDKs

## Usage-based Billing & Chargebacks (Optional)
If or when you're ready to turn AI costs into AI revenue, the Revenium MCP will be there to help quickly make the transition.

- Ask your agent to manage all elements of usage-based billing & cost chargebacks
- Use agents to manage products, customers, subscriptions, and subscriber credentials

[![Version](https://img.shields.io/badge/version-0.1.27-blue)](https://github.com/revenium/revenium-mcp)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![MCP Compatible](https://img.shields.io/badge/MCP-Compatible-purple)](https://modelcontextprotocol.io)

---

## AI Cost Analytics & Alerting Tools

The MCP provides the appropriate tools for each use case depending on your chosen startup profile. Below is a summary:

### **Alert Management**
Set up intelligent monitoring for costs, usage, and performance metrics.
- Create budget threshold and spike detection alerts 
- Get notified via Slack or email when patterns change
- *Example: "Alert me when monthly costs for Anthropic exceed $500"*
- *Example: "Create a spike detection alert when token use exceeds 1,500,000 tokens per hour"*
- *Example: "Alert when my error rate exceeds 5% every 5 minutes"*
- *Example: "Set up cost per transaction monitoring so any single AI call costing more than $1.50 triggers an immediate Slack alert"*

### **Slack Integration**
- *Example: "Set up a Slack notification channel for Revenium alerts"*
- *Example: "Add a new slack channel for all customer spending alerts"*
- *Example: "Send all product spending anaomalies to the Slack channel #product-spend-alerts."*

### **AI Business Analytics**
Analyze costs, usage patterns, and performance.
- Cost trend analysis and breakdowns
- *Example: "Summarize my costs for the last day/week/month and highlight any anomalies"*
- *Example: "Explain why costs grew last week"*
- *Example: "Show me a breakdown of AI costs last month by provider/customer/product/agent"*

#### Common Use Cases

**"Why did my costs spike yesterday?"**
- *"Analyze cost anomalies in the last 7 days focusing on abnormal spending by model or API key"*
- *"Detect what caused my cost increase yesterday. Only focus on anomalies larger than $20 vs. the norm"*

**"Find anomalies across all dimensions"**  
- *"Show me cost anomalies in the last month across all providers, models, agents, API keys, and customers"*
- *"Analyze all dimensions for cost spikes above $150 in the past 30 days"*

**"Detect small but significant anomalies to identify early changes in behavior before they become large issues"**
- *"Find API key anomalies in the last week using aggressive sensitivity"*


### **AI Metering Management**
Track AI usage, token consumption, and transaction data with comprehensive integration guidance.
- Get assistance creating a new custom integration from your AI agents to Revenium
- Get comprehensive implementation guidance with working code examples for Python and JavaScript
- Submit AI transaction data and verify successful processing

- *Example: "Get Python integration guide with working code examples for AI transaction metering"*
- *Example: "Get JavaScript integration guide with official npm package references"*
- *Example: "Check the status of transaction tx_12345"*
- *Example: "Help me integrate this python AI function with Revenium's AI metering API"*
- *Example: "Generate test transaction data from our application and ensure all metadata is properly mapped in Revenium."*

---

## Installation

### Prerequisites

- **Python 3.11+** with pip
- **Your Revenium API key**
- **Optional**: [uv/uvx](https://github.com/astral-sh/uv)

### Install Python Package

**Option 1: Installation with uvx**
```bash
# Install uv if you don't have it
pip install uv
export REVENIUM_API_KEY=your_key
uvx revenium-mcp
```

**Option 2: Package Installation in Virtual Environment**

```bash
# Create and activate virtual environment
python -m venv revenium-mcp-env
source revenium-mcp-env/bin/activate  # On Windows: revenium-mcp-env\Scripts\activate
export REVENIUM_API_KEY=your_key
pip install revenium-mcp
```

### Choose Your Profile & Start the Server

The MCP server supports two profiles to match your use case:

#### **Profile Overview**

| Profile | Tools | Target Users | Use Cases |
|---------|-------|--------------|-----------|
| **Starter** (default) | 7 tools | Cost monitoring & alerts | Cost analysis, AI transaction metering |
| **Business** | 15 tools | Product & subscription management, usage-based billing, comprehensive analytics |

The server uses the **Starter** profile by default. To use the **Business** profile, set the `TOOL_PROFILE` environment variable:



**With uvx:**
```bash
# Starter Profile (7 tools) - Cost monitoring, alerts, AI metering integration (default)
export REVENIUM_API_KEY=your_key
uvx revenium-mcp

# Business Profile (15 tools) - Usage-based billing & AI Analytics
export REVENIUM_API_KEY=your_key
TOOL_PROFILE=business uvx revenium-mcp
```

### For Claude Code

Choose one of the following integration methods. Both use the **Starter** profile by default. To use the **Business** profile, add `-e TOOL_PROFILE=business` to the command:

**Option 1: Installation with uvx**
```bash
# Install uv if you don't have it  
pip install uv

# Starter profile (default)
claude mcp add revenium \
  -e REVENIUM_API_KEY=your_api_key_here \
  -- uvx revenium-mcp

# Business profile (for advanced features)
claude mcp add revenium \
  -e REVENIUM_API_KEY=your_api_key_here \
  -e TOOL_PROFILE=business \
  -- uvx revenium-mcp
```

**Option 2: Installation with python virtual environment**
```bash
# Create and activate virtual environment
python -m venv revenium-mcp-env
source revenium-mcp-env/bin/activate  # On Windows: revenium-mcp-env\Scripts\activate

# Install package
pip install revenium-mcp

# Add to Claude Code using venv python (starter profile - default)
claude mcp add revenium \
  -e REVENIUM_API_KEY=your_api_key_here \
  -- ./revenium-mcp-env/bin/python -m revenium_mcp

# For business profile, add the environment variable:
claude mcp add revenium \
  -e REVENIUM_API_KEY=your_api_key_here \
  -e TOOL_PROFILE=business \
  -- ./revenium-mcp-env/bin/python -m revenium_mcp
```

#### Claude Code Slash Commands
Add the [slash commands](https://github.com/revenium/revenium-mcp/tree/main/.claude/commands) here for easy access to spending summaries and analysis of spending anomalies.  

---
### For Cursor / Augment IDE (or any IDE allowing MCP JSON import)

**Install uv:**
pip install uv

**Configure MCP server:**

1. Open Cursor/Augment settings (Ctrl/Cmd + ,) | (Cmd + Shift + P for Augment)
2. Navigate to Extensions → MCP or create `~/.cursor/mcp.json` | for Augment, import JSON below into MCP settings
3. Add server configuration:

**Standard Configuration:**
```json
{
  "mcpServers": {
    "revenium": {
      "command": "uvx",
      "args": ["revenium-mcp"],
      "env": {
        "REVENIUM_API_KEY": "your_api_key_here"
      }
    }
  }
}
```

### Overriding Default Values in IDE / MCP Client (Advanced Use Cases)

You can override the automatically loaded values if needed:

**When you might need overrides:**
- Multi-tenant environments: Switching organizations in a multi-tenant Revenium installation 
- Custom email preferences: Change default email address for alert configuration
- Custom API endpoints: When not using Revenium's default API endpoints

### Required Configuration

| Variable | Required | Description | Example |
|----------|----------|-------------|---------|
| `REVENIUM_API_KEY` | ✅ | Your account API key from the API Keys page in Revenium | `hak_1234567890abcdef` |

### Automatically Loaded Values

These values are loaded from your account and can be overridden if needed:

| Variable | Override When | Example |
|----------|---------------|---------|
| `REVENIUM_TEAM_ID` | Multi-tenant environments | `ABC123x` |
| `REVENIUM_TENANT_ID` | Operating on behalf of different tenant | `DEF456n` |
| `REVENIUM_OWNER_ID` | Non-primary user scenarios | `GHI789z` |
| `REVENIUM_DEFAULT_EMAIL` | Custom alert email preferences | `alerts@company.com` |

### Optional Configuration

| Variable | Required | Description | Example |
|----------|----------|-------------|---------|
| `REVENIUM_BASE_URL` | ⚪ | API endpoint URL (defaults to main Revenium instance) | `https://api.revenium.io/meter` |
| `REVENIUM_APP_BASE_URL` | ⚪ | Defines which Revenium web application instance to use for Slack channel configurations (defaults to main Revenium instance) | `https://ai.revenium.io` |
| `LOG_LEVEL` | ⚪ | Logging verbosity level | `DEBUG` |
| `REQUEST_TIMEOUT` | ⚪ | API request timeout in seconds | `30` |


---

## Usage-Based Billing Tools (Optional)

### 📊 **Product Management**
Create and manage your AI products, pricing tiers, and billing models.
- Design usage-based or subscription pricing
- Design chargeback models so that all AI spending is invoiced to the correct internal department
- Set up free tiers and graduated pricing for SaaS products
- *Example: "Create a Gold Tier AI product with $199 per month base fee plus usage-based pricing that charges 1.10x the actual AI costs"*
- *Example: "Create a new product called 'Smart Analytics' with usage-based pricing"*
- *Example: "Set up a free tier with 1000 API calls, then charge a 25% premium on my AI costs for every call"*
- *Example: "Show me the number of subscribers for each of my products"*

### 👥 **Customer Management**
Handle customer relationships, organizations, and user hierarchies.
- Manage customer or internal organizations used for cost attribution
- Create & manage subscribers (internal or external)
- Track customer usage

- *Example: "List all organizationss and their subscription status"*

### 📋 **Subscription Management**
Control customer subscriptions, billing cycles, and plan changes.
- Create and modify customer subscriptions
- Track subscription analytics
- *Example: "Create a monthly subscription for customer ABC Corp to the product 'analytics-suite'"*
- *Example: "Show me all active subscriptions to the AI Analytics product"*
- *Example: "List subscriptions that are about to expire this month"*


## 🔍 Troubleshooting

#### Authentication Errors
- Verify your API key is correct and active
- Use the diagnostic tool to check configuration status
- Ensure the base URL is correct for your environment
- Check that the `/users/me` endpoint is accessible with your API key

#### Configuration Priority
The system loads configuration values in this priority order:
1. **MCP client JSON configuration `env` section** (highest priority)
2. **System environment variables**
3. **Automatically loaded values** from Revenium's API

Use the `system_diagnostics` tool to see exactly which values are being used from each source.

---

## License

**License**: MIT License

---
