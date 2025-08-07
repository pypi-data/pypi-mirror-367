"""
Data analysis utilities for BRAIN MCP server.
"""

import csv
import json
import logging
import os
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


def combine_pnl_data(results: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Aggregate PnL data from multiple alphas for portfolio analysis."""
    logger.info(f"Combining PnL data from {len(results)} alphas")
    
    combined_data = {
        "alphas": [],
        "summary": {
            "total_alphas": len(results),
            "successful": 0,
            "failed": 0
        }
    }
    
    for result in results:
        if "pnl" in result:
            combined_data["alphas"].append({
                "alpha_id": result.get("alpha_id"),
                "pnl_data": result["pnl"],
                "metrics": extract_pnl_metrics(result["pnl"])
            })
            combined_data["summary"]["successful"] += 1
        else:
            combined_data["summary"]["failed"] += 1
    
    return combined_data


def combine_test_results(results: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Aggregate test results across multiple alphas."""
    logger.info(f"Combining test results from {len(results)} alphas")
    
    combined_results = {
        "alphas": [],
        "summary": {
            "total_alphas": len(results),
            "passed_all": 0,
            "failed_any": 0,
            "common_failures": {}
        }
    }
    
    for result in results:
        alpha_tests = {
            "alpha_id": result.get("alpha_id"),
            "tests": result.get("tests", {}),
            "overall_pass": all(result.get("tests", {}).values())
        }
        
        combined_results["alphas"].append(alpha_tests)
        
        if alpha_tests["overall_pass"]:
            combined_results["summary"]["passed_all"] += 1
        else:
            combined_results["summary"]["failed_any"] += 1
            
            # Track common failure types
            for test_name, passed in alpha_tests["tests"].items():
                if not passed:
                    if test_name not in combined_results["summary"]["common_failures"]:
                        combined_results["summary"]["common_failures"][test_name] = 0
                    combined_results["summary"]["common_failures"][test_name] += 1
    
    return combined_results


def extract_pnl_metrics(pnl_data: Dict[str, Any]) -> Dict[str, float]:
    """Extract key metrics from PnL data."""
    metrics = {}
    
    if "sharpe" in pnl_data:
        metrics["sharpe"] = pnl_data["sharpe"]
    
    if "returns" in pnl_data:
        returns = pnl_data["returns"]
        if isinstance(returns, list) and returns:
            metrics["total_return"] = sum(returns)
            metrics["avg_return"] = sum(returns) / len(returns)
            metrics["volatility"] = calculate_volatility(returns)
    
    if "drawdown" in pnl_data:
        metrics["max_drawdown"] = pnl_data["drawdown"]
    
    return metrics


def calculate_volatility(returns: List[float]) -> float:
    """Calculate volatility from returns."""
    if len(returns) < 2:
        return 0.0
    
    mean_return = sum(returns) / len(returns)
    variance = sum((r - mean_return) ** 2 for r in returns) / (len(returns) - 1)
    return variance ** 0.5


def save_pnl_data(
    alpha_id: str,
    region: str,
    pnl_data: List[Dict[str, Any]],
    folder_path: str = "alphas_pnl"
) -> Dict[str, str]:
    """Export PnL performance data to CSV files."""
    logger.info(f"Saving PnL data for alpha {alpha_id}")
    
    # Create folder if it doesn't exist
    Path(folder_path).mkdir(parents=True, exist_ok=True)
    
    # Create filename
    filename = f"{alpha_id}_{region}_pnl.csv"
    filepath = Path(folder_path) / filename
    
    # Write CSV file
    with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
        if pnl_data:
            fieldnames = pnl_data[0].keys()
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(pnl_data)
    
    return {
        "filename": filename,
        "filepath": str(filepath),
        "records_saved": len(pnl_data)
    }


def save_yearly_statistics(
    alpha_id: str,
    region: str,
    yearly_stats: List[Dict[str, Any]],
    folder_path: str = "yearly_stats"
) -> Dict[str, str]:
    """Export annual performance statistics to CSV."""
    logger.info(f"Saving yearly statistics for alpha {alpha_id}")
    
    # Create folder if it doesn't exist
    Path(folder_path).mkdir(parents=True, exist_ok=True)
    
    # Create filename
    filename = f"{alpha_id}_{region}_yearly_stats.csv"
    filepath = Path(folder_path) / filename
    
    # Write CSV file
    with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
        if yearly_stats:
            fieldnames = yearly_stats[0].keys()
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(yearly_stats)
    
    return {
        "filename": filename,
        "filepath": str(filepath),
        "records_saved": len(yearly_stats)
    }


def save_simulation_data(
    simulation_result: Dict[str, Any],
    folder_path: str = "simulation_results"
) -> Dict[str, str]:
    """Save complete simulation results to JSON files."""
    alpha_id = simulation_result.get("alpha_id", "unknown")
    logger.info(f"Saving simulation data for alpha {alpha_id}")
    
    # Create folder if it doesn't exist
    Path(folder_path).mkdir(parents=True, exist_ok=True)
    
    # Create filename with timestamp
    import datetime
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{alpha_id}_simulation_{timestamp}.json"
    filepath = Path(folder_path) / filename
    
    # Write JSON file
    with open(filepath, 'w', encoding='utf-8') as jsonfile:
        json.dump(simulation_result, jsonfile, indent=2, ensure_ascii=False)
    
    return {
        "filename": filename,
        "filepath": str(filepath),
        "alpha_id": alpha_id
    }


def expand_nested_data(
    data: List[Dict[str, Any]], 
    preserve_original: bool = True
) -> List[Dict[str, Any]]:
    """Flatten complex nested data structures."""
    logger.info(f"Expanding nested data for {len(data)} records")
    
    expanded_data = []
    
    for record in data:
        expanded_record = record.copy() if preserve_original else {}
        
        # Flatten nested dictionaries
        for key, value in record.items():
            if isinstance(value, dict):
                for nested_key, nested_value in value.items():
                    expanded_key = f"{key}_{nested_key}"
                    expanded_record[expanded_key] = nested_value
                
                # Remove original nested dict if not preserving
                if not preserve_original:
                    expanded_record.pop(key, None)
        
        expanded_data.append(expanded_record)
    
    return expanded_data


def generate_alpha_links(
    alpha_ids: List[str], 
    base_url: str = "https://platform.worldquantbrain.com"
) -> List[Dict[str, str]]:
    """Create clickable HTML links to BRAIN platform alphas."""
    logger.info(f"Generating links for {len(alpha_ids)} alphas")
    
    links = []
    for alpha_id in alpha_ids:
        url = f"{base_url}/alpha/{alpha_id}"
        html_link = f'<a href="{url}" target="_blank">{alpha_id}</a>'
        
        links.append({
            "alpha_id": alpha_id,
            "url": url,
            "html_link": html_link
        })
    
    return links


def prettify_results(results: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Format and organize multiple simulation results."""
    logger.info(f"Prettifying {len(results)} simulation results")
    
    prettified = {
        "summary": {
            "total_simulations": len(results),
            "successful": 0,
            "failed": 0,
            "warnings": 0
        },
        "results": [],
        "errors": []
    }
    
    for result in results:
        status = result.get("status", "UNKNOWN")
        
        if status == "COMPLETE":
            prettified["summary"]["successful"] += 1
            prettified["results"].append({
                "alpha_id": result.get("alpha_id"),
                "status": status,
                "sharpe": result.get("sharpe"),
                "returns": result.get("returns"),
                "location": result.get("location")
            })
        elif status == "WARNING":
            prettified["summary"]["warnings"] += 1
            prettified["results"].append(result)
        else:
            prettified["summary"]["failed"] += 1
            prettified["errors"].append({
                "alpha_id": result.get("alpha_id"),
                "status": status,
                "error": result.get("message", "Unknown error")
            })
    
    return prettified
