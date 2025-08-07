# CNHK MCP Server

[![PyPI version](https://badge.fury.io/py/cnhkmcp.svg)](https://badge.fury.io/py/cnhkmcp)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A Model Context Protocol (MCP) server for quantitative research and data analysis. This package provides comprehensive tools for research, simulation, and data analysis workflows.

## Features

### 🔐 Authentication & Session Management
- Secure authentication with platform API
- Automatic token refresh and session persistence
- Credential storage and management

### 🚀 Research & Simulation
- **Single & Batch Simulations**: Submit individual models or batch process up to 10 models simultaneously
- **Smart Waiting**: Intelligent monitoring with automatic retry logic
- **Multi-Model Support**: Regular and advanced simulation strategies
- **Real-time Monitoring**: Track simulation progress and completion status

### 📊 Data Analysis & Export
- **Performance Analytics**: Performance analysis, statistical metrics, analytical tools
- **Portfolio Analysis**: Aggregate data from multiple models
- **Data Export**: CSV export for performance data and statistics
- **Result Archival**: JSON export for complete simulation results

### 🔍 Research Tools
- **Data Discovery**: Explore available datasets, data fields, and operators
- **Validation Tools**: Correlation checks and analysis tools
- **Forum Integration**: Access community forum posts and discussions
- **Quality Assurance**: Comprehensive validation before submission

### 📈 Advanced Features
- **Batch Processing**: Parallel processing of multiple models with configurable batch sizes
- **Data Transformation**: Flatten complex nested data structures for analysis
- **Link Generation**: Create clickable links to platform resources
- **Error Handling**: Comprehensive error tracking and reporting

## Installation

### From PyPI (Recommended)

```bash
pip install cnhkmcp
```

### From Source

```bash
git clone https://github.com/cnhk/cnhkmcp.git
cd cnhkmcp
pip install -e .
```

## Quick Start

### 1. Basic Setup

First, start the MCP server:

```bash
cnhkmcp-server
```

### 2. Authentication

```python
# The server will automatically handle authentication
# You can also configure credentials in config files
```

### 3. Basic Simulation

```python
# Example simulation request
{
  "tool": "create_simulation",
  "arguments": {
    "type": "REGULAR",
    "settings": {
      "instrumentType": "EQUITY",
      "region": "USA", 
      "universe": "TOP3000",
      "delay": 1,
      "decay": 0,
      "neutralization": "SUBUNIV",
      "truncation": 0.08,
      "testPeriod": "P1Y6M",
      "unitHandling": "VERIFY",
      "nanHandling": "ELIMINATE",
      "language": "FASTEXPR",
      "visualization": true
    },
    "regular": "close"
  }
}
```

## Configuration

### Credentials Configuration

Create a `config/cnhk-config.json` file:

```json
{
  "credentials": {
    "email": "your-email@example.com",
    "password": "your-password"
  },
  "defaults": {
    "instrumentType": "EQUITY",
    "region": "USA",
    "universe": "TOP3000",
    "delay": 1,
    "decay": 0,
    "neutralization": "SUBUNIV",
    "truncation": 0.08,
    "testPeriod": "P1Y6M",
    "unitHandling": "VERIFY",
    "nanHandling": "ELIMINATE",
    "language": "FASTEXPR",
    "visualization": true
  }
}
```

## Available Tools

### Core Research Tools

| Tool | Description | Use Case |
|------|-------------|----------|
| `authenticate` | 🔐 Authenticate with platform | Required first step |
| `create_simulation` | 🚀 Submit expressions for simulation | Single model research |
| `create_multi_simulation` | 🚀 Batch submit multiple models | Batch research |
| `wait_for_simulation` | ⏳ Smart simulation waiting | Monitor completion |
| `get_simulation_status` | ⏱️ Check simulation progress | Status monitoring |

### Alpha Management

| Tool | Description | Use Case |
|------|-------------|----------|
| `get_alpha_details` | 📊 Get alpha metadata and results | Result extraction |
| `get_user_alphas` | 📋 Retrieve user's alpha list | Portfolio management |
| `submit_alpha` | ✅ Submit alpha for evaluation | Production submission |
| `set_alpha_properties` | ⚙️ Update alpha properties | Alpha organization |

### Data Analysis

| Tool | Description | Use Case |
|------|-------------|----------|
| `get_alpha_pnl` | 📈 Get PnL data | Performance analysis |
| `get_alpha_yearly_stats` | 📊 Get yearly statistics | Annual performance |
| `combine_pnl_data` | 📈 Aggregate PnL from multiple alphas | Portfolio analysis |
| `save_simulation_data` | 💾 Export simulation results | Data archival |
| `save_pnl_data` | 📤 Export PnL to CSV | External analysis |

### Validation & Quality

| Tool | Description | Use Case |
|------|-------------|----------|
| `check_production_correlation` | 🔍 Check production correlation | Pre-submission validation |
| `check_self_correlation` | 🔍 Check self-correlation | Uniqueness validation |
| `get_submission_check` | ✅ Comprehensive submission check | Quality assurance |
| `get_alpha_checks` | 🧪 Detailed validation results | Debug validation issues |

### Data Discovery

| Tool | Description | Use Case |
|------|-------------|----------|
| `get_datasets` | 🔍 List available datasets | Data exploration |
| `get_datafields` | 📊 Get data fields | Field discovery |
| `get_operators` | ⚙️ Get available operators | Expression building |
| `get_instrument_options` | 🔧 Get configuration options | Setup assistance |

### Forum & Community

| Tool | Description | Use Case |
|------|-------------|----------|
| `get_forum_post` | 📄 Extract forum post content | Community research |
| `search_forum_posts` | 🔍 Search forum discussions | Topic discovery |

## Usage Examples

### Example 1: Basic Alpha Research Workflow

```python
# 1. Authenticate
await authenticate({
    "email": "user@example.com",
    "password": "password"
})

# 2. Create simulation
simulation = await create_simulation({
    "type": "REGULAR",
    "settings": {
        "instrumentType": "EQUITY",
        "region": "USA",
        "universe": "TOP3000",
        "delay": 1,
        "decay": 0,
        "neutralization": "SUBUNIV", 
        "truncation": 0.08,
        "testPeriod": "P1Y6M",
        "unitHandling": "VERIFY",
        "nanHandling": "ELIMINATE",
        "language": "FASTEXPR",
        "visualization": True
    },
    "regular": "close"
})

# 3. Wait for completion
result = await wait_for_simulation({
    "simulationId": simulation["id"],
    "maxWaitTime": 1800
})

# 4. Get detailed results
details = await get_alpha_details({
    "alphaId": result["alpha_id"]
})
```

### Example 2: Batch Alpha Processing

```python
# Get user's alphas
alphas = await get_user_alphas({
    "stage": "IS",
    "limit": 50
})

# Extract alpha IDs
alpha_ids = [alpha["id"] for alpha in alphas["results"]]

# Batch process for correlations  
correlations = await batch_process_alphas({
    "alphaIds": alpha_ids,
    "operation": "get_correlations",
    "batchSize": 5
})
```

### Example 3: Multi-Simulation

```python
# Create multiple simulations
multi_sim = await create_multi_simulation({
    "simulations": [
        {
            "type": "REGULAR",
            "settings": {...},
            "regular": "close"
        },
        {
            "type": "REGULAR", 
            "settings": {...},
            "regular": "open"
        }
        # ... up to 10 total
    ]
})
```

### Example 4: Forum Research

```python
# Get forum post content
post = await get_forum_post({
    "postUrlOrId": "32995186681879-常用模板分析",
    "includeComments": True
})

# Search forum posts
search_results = await search_forum_posts({
    "searchQuery": "模板",
    "maxResults": 20
})
```

## Advanced Features

### Batch Processing

Process multiple alphas efficiently:

```python
results = await batch_process_alphas({
    "alphaIds": ["alpha1", "alpha2", "alpha3"],
    "operation": "get_details",  # or "get_pnl", "get_stats", "get_correlations"
    "batchSize": 3
})
```

### Data Export

Export results for external analysis:

```python
# Save simulation data
save_result = await save_simulation_data({
    "simulationResult": simulation_data,
    "folderPath": "my_results"
})

# Export PnL data to CSV
csv_result = await save_pnl_data({
    "alphaId": "alpha123",
    "region": "USA",
    "pnlData": pnl_data,
    "folderPath": "pnl_exports"
})
```

### Data Analysis

Combine and analyze multiple alphas:

```python
# Combine PnL data from multiple alphas
combined = await combine_pnl_data({
    "results": [result1, result2, result3]
})

# Expand nested data structures
expanded = await expand_nested_data({
    "data": complex_data,
    "preserveOriginal": True
})
```

## Error Handling

The server provides comprehensive error handling:

- **Authentication Errors**: Automatic token refresh
- **Rate Limiting**: Built-in retry logic with exponential backoff
- **Network Errors**: Automatic reconnection and retry
- **Validation Errors**: Detailed error messages with suggestions

## Logging

Configure logging level in your environment:

```bash
export CNHK_MCP_LOG_LEVEL=INFO  # DEBUG, INFO, WARNING, ERROR
```

## Development

### Setting up Development Environment

```bash
git clone https://github.com/cnhk/cnhkmcp.git
cd cnhkmcp
pip install -e ".[dev]"
```

### Running Tests

```bash
pytest
```

### Code Formatting

```bash
black src/
isort src/
```

## Requirements

- Python 3.8+
- Platform account access
- Chrome/Chromium browser (for forum functionality)

## Dependencies

- `mcp>=1.0.0`: Model Context Protocol SDK
- `httpx>=0.25.0`: HTTP client
- `pydantic>=2.0.0`: Data validation
- `selenium>=4.0.0`: Web automation
- `beautifulsoup4>=4.12.0`: HTML parsing

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

- 📖 [Documentation](https://github.com/cnhk/cnhkmcp/blob/main/README.md)
- 🐛 [Issue Tracker](https://github.com/cnhk/cnhkmcp/issues)
- 💬 [Discussions](https://github.com/cnhk/cnhkmcp/discussions)

## Changelog

### v1.0.0
- Initial release
- Core MCP server functionality
- Alpha simulation and management
- Forum integration
- Data analysis tools
- Batch processing capabilities

---

**CNHK MCP Server** - Bringing quantitative research capabilities to AI assistants through the Model Context Protocol.
