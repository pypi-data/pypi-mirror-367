"""
API client for platform interactions.
"""

import asyncio
import json
import logging
import time
from typing import Any, Dict, List, Optional, Union

import httpx
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

logger = logging.getLogger(__name__)


class ApiClient:
    """Client for interacting with the WorldQuant BRAIN platform API."""

    def __init__(self):
        self.base_url = "https://api.worldquantbrain.com"
        self.jwt_token: Optional[str] = None
        self.auth_credentials: Optional[Dict[str, str]] = None
        self.is_authenticating = False
        
        # Create HTTP client
        self.client = httpx.AsyncClient(
            base_url=self.base_url,
            timeout=30.0,
            headers={
                "User-Agent": "BRAIN-MCP-Server/1.0.0"
            }
        )

    def _log(self, message: str, level: str = "INFO") -> None:
        """Log message to stderr to avoid MCP protocol interference."""
        logger.info(f"[{level}] {message}")

    async def _make_request(
        self, 
        method: str, 
        endpoint: str, 
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """Make HTTP request with automatic token refresh."""
        request_headers = {}
        
        if self.jwt_token:
            request_headers["Cookie"] = f"t={self.jwt_token}"
        
        if headers:
            request_headers.update(headers)

        try:
            response = await self.client.request(
                method=method,
                url=endpoint,
                json=data,
                params=params,
                headers=request_headers
            )
            
            # Handle authentication errors
            if response.status_code in [401, 403] and self.auth_credentials and not self.is_authenticating:
                self._log("Authentication expired, refreshing token")
                await self._refresh_authentication()
                
                # Retry request with new token
                if self.jwt_token:
                    request_headers["Cookie"] = f"t={self.jwt_token}"
                    response = await self.client.request(
                        method=method,
                        url=endpoint,
                        json=data,
                        params=params,
                        headers=request_headers
                    )
            
            response.raise_for_status()
            return response.json()
            
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error: {e.response.status_code} - {e.response.text}")
            raise
        except Exception as e:
            logger.error(f"Request error: {e}")
            raise

    async def _refresh_authentication(self) -> None:
        """Refresh authentication token."""
        if not self.auth_credentials:
            raise ValueError("No credentials available for authentication refresh")
        
        await self.authenticate(
            self.auth_credentials["email"],
            self.auth_credentials["password"]
        )

    async def authenticate(self, email: str, password: str) -> Dict[str, Any]:
        """Authenticate with BRAIN platform."""
        self.is_authenticating = True
        self._log("Authenticating with BRAIN platform")
        
        try:
            auth_data = {
                "email": email,
                "password": password,
                "remember": True
            }
            
            response = await self._make_request("POST", "/authentication", data=auth_data)
            
            # Extract JWT token from response
            if "token" in response:
                self.jwt_token = response["token"].get("token") or response["token"].get("jwt")
                self.auth_credentials = {"email": email, "password": password}
                self._log("Authentication successful")
            
            return response
            
        finally:
            self.is_authenticating = False

    async def create_simulation(self, simulation_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new simulation."""
        self._log("Creating simulation")
        return await self._make_request("POST", "/simulations", data=simulation_data)

    async def create_multi_simulation(self, simulations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Create multiple simulations."""
        self._log(f"Creating {len(simulations)} simulations")
        data = {"simulations": simulations}
        return await self._make_request("POST", "/multi-simulations", data=data)

    async def get_simulation_status(self, simulation_id: str) -> Dict[str, Any]:
        """Get simulation status."""
        return await self._make_request("GET", f"/simulations/{simulation_id}")

    async def wait_for_simulation(
        self, 
        simulation_id: str, 
        max_wait_time: int = 1800,
        retry_interval: int = 10
    ) -> Dict[str, Any]:
        """Wait for simulation to complete with intelligent retry logic."""
        self._log(f"Waiting for simulation {simulation_id} to complete")
        start_time = time.time()
        
        while time.time() - start_time < max_wait_time:
            try:
                result = await self.get_simulation_status(simulation_id)
                status = result.get("status", "UNKNOWN")
                
                if status in ["COMPLETE", "WARNING"]:
                    self._log(f"Simulation completed with status: {status}")
                    return result
                elif status in ["ERROR", "CANCELLED", "TIMEOUT", "FAIL"]:
                    self._log(f"Simulation failed with status: {status}", "ERROR")
                    return result
                else:
                    self._log(f"Simulation status: {status}, waiting...")
                    await asyncio.sleep(retry_interval)
                    
            except Exception as e:
                self._log(f"Error checking simulation status: {e}", "WARNING")
                await asyncio.sleep(retry_interval)
        
        raise TimeoutError(f"Simulation {simulation_id} did not complete within {max_wait_time} seconds")

    async def get_alpha_details(self, alpha_id: str) -> Dict[str, Any]:
        """Get alpha details."""
        return await self._make_request("GET", f"/alphas/{alpha_id}")

    async def get_alpha_pnl(self, alpha_id: str, pnl_type: str = "pnl") -> Dict[str, Any]:
        """Get alpha PnL data."""
        params = {"type": pnl_type}
        return await self._make_request("GET", f"/alphas/{alpha_id}/pnl", params=params)

    async def get_alpha_yearly_stats(self, alpha_id: str) -> Dict[str, Any]:
        """Get alpha yearly statistics."""
        return await self._make_request("GET", f"/alphas/{alpha_id}/yearly-stats")

    async def get_user_alphas(
        self, 
        stage: str, 
        limit: int = 100, 
        offset: int = 0
    ) -> Dict[str, Any]:
        """Get user's alphas."""
        params = {
            "stage": stage,
            "limit": limit,
            "offset": offset
        }
        return await self._make_request("GET", "/alphas", params=params)

    async def get_user_profile(self, user_id: str = "self") -> Dict[str, Any]:
        """Get user profile information."""
        endpoint = "/user" if user_id == "self" else f"/users/{user_id}"
        return await self._make_request("GET", endpoint)

    async def get_datasets(self, **kwargs) -> Dict[str, Any]:
        """Get available datasets."""
        return await self._make_request("GET", "/datasets", params=kwargs)

    async def get_datafields(self, **kwargs) -> Dict[str, Any]:
        """Get available data fields."""
        return await self._make_request("GET", "/datafields", params=kwargs)

    async def get_operators(self) -> Dict[str, Any]:
        """Get available operators."""
        return await self._make_request("GET", "/operators")

    async def get_instrument_options(self) -> Dict[str, Any]:
        """Get instrument configuration options."""
        return await self._make_request("GET", "/instrument-options")

    async def submit_alpha(self, alpha_id: str) -> Dict[str, Any]:
        """Submit alpha for evaluation."""
        return await self._make_request("POST", f"/alphas/{alpha_id}/submit")

    async def set_alpha_properties(self, alpha_id: str, **properties) -> Dict[str, Any]:
        """Update alpha properties."""
        return await self._make_request("PUT", f"/alphas/{alpha_id}", data=properties)

    async def get_production_correlation(self, alpha_id: str) -> Dict[str, Any]:
        """Get production correlation data."""
        return await self._make_request("GET", f"/alphas/{alpha_id}/production-correlation")

    async def get_self_correlation(self, alpha_id: str) -> Dict[str, Any]:
        """Get self-correlation data."""
        return await self._make_request("GET", f"/alphas/{alpha_id}/self-correlation")

    async def check_production_correlation(
        self, 
        alpha_id: str, 
        threshold: float = 0.7
    ) -> Dict[str, Any]:
        """Check production correlation threshold."""
        params = {"threshold": threshold}
        return await self._make_request("GET", f"/alphas/{alpha_id}/check-production-correlation", params=params)

    async def check_self_correlation(
        self, 
        alpha_id: str, 
        threshold: float = 0.7
    ) -> Dict[str, Any]:
        """Check self-correlation threshold."""
        params = {"threshold": threshold}
        return await self._make_request("GET", f"/alphas/{alpha_id}/check-self-correlation", params=params)

    async def get_submission_check(self, alpha_id: str) -> Dict[str, Any]:
        """Get submission check results."""
        return await self._make_request("GET", f"/alphas/{alpha_id}/submission-check")

    async def get_alpha_checks(self, alpha_id: str, include_details: bool = True) -> Dict[str, Any]:
        """Get comprehensive alpha validation checks."""
        params = {"includeDetails": include_details}
        return await self._make_request("GET", f"/alphas/{alpha_id}/checks", params=params)

    async def get_record_sets(self, alpha_id: str) -> Dict[str, Any]:
        """Get available record sets for alpha."""
        return await self._make_request("GET", f"/alphas/{alpha_id}/record-sets")

    async def get_record_set_data(self, alpha_id: str, record_set_name: str) -> Dict[str, Any]:
        """Get specific record set data."""
        return await self._make_request("GET", f"/alphas/{alpha_id}/record-sets/{record_set_name}")

    async def batch_process_alphas(
        self, 
        alpha_ids: List[str], 
        operation: str, 
        batch_size: int = 5
    ) -> Dict[str, Any]:
        """Process multiple alphas in parallel."""
        self._log(f"Batch processing {len(alpha_ids)} alphas with operation: {operation}")
        
        results = []
        errors = []
        
        for i in range(0, len(alpha_ids), batch_size):
            batch = alpha_ids[i:i + batch_size]
            batch_tasks = []
            
            for alpha_id in batch:
                if operation == "get_details":
                    task = self.get_alpha_details(alpha_id)
                elif operation == "get_pnl":
                    task = self.get_alpha_pnl(alpha_id)
                elif operation == "get_stats":
                    task = self.get_alpha_yearly_stats(alpha_id)
                elif operation == "get_correlations":
                    task = self.get_production_correlation(alpha_id)
                else:
                    raise ValueError(f"Unknown operation: {operation}")
                
                batch_tasks.append((alpha_id, task))
            
            # Execute batch
            for alpha_id, task in batch_tasks:
                try:
                    result = await task
                    results.append({"alpha_id": alpha_id, "result": result})
                except Exception as e:
                    errors.append({"alpha_id": alpha_id, "error": str(e)})
        
        return {
            "results": results,
            "errors": errors,
            "total_processed": len(results) + len(errors),
            "success_count": len(results),
            "error_count": len(errors)
        }

    async def get_forum_post(
        self, 
        post_url_or_id: str,
        email: str,
        password: str,
        include_comments: bool = True,
        headless: bool = True
    ) -> Dict[str, Any]:
        """Get forum post content using Selenium."""
        self._log("Retrieving forum post content")
        
        # Set up Chrome options
        chrome_options = Options()
        if headless:
            chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        
        driver = None
        try:
            driver = webdriver.Chrome(options=chrome_options)
            
            # Determine if URL or ID
            if post_url_or_id.startswith("http"):
                url = post_url_or_id
            else:
                url = f"https://support.worldquantbrain.com/hc/zh-cn/community/posts/{post_url_or_id}"
            
            # Navigate to forum post
            driver.get(url)
            
            # Login if required
            try:
                login_button = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((By.LINK_TEXT, "登录"))
                )
                login_button.click()
                
                # Enter credentials
                email_field = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.ID, "user_email"))
                )
                email_field.send_keys(email)
                
                password_field = driver.find_element(By.ID, "user_password")
                password_field.send_keys(password)
                
                submit_button = driver.find_element(By.NAME, "commit")
                submit_button.click()
                
                # Wait for redirect back to post
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "post-header"))
                )
                
            except Exception:
                # Already logged in or no login required
                pass
            
            # Extract post content
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            
            # Get main post content
            post_header = soup.find('div', class_='post-header')
            post_content = soup.find('div', class_='post-content')
            
            title = post_header.find('h1').get_text(strip=True) if post_header else "No title"
            content = post_content.get_text(strip=True) if post_content else "No content"
            
            # Get author and date
            author_info = post_header.find('div', class_='post-author') if post_header else None
            author = author_info.get_text(strip=True) if author_info else "Unknown"
            
            result = {
                "title": title,
                "content": content,
                "author": author,
                "url": url,
                "comments": []
            }
            
            # Get comments if requested
            if include_comments:
                comments = soup.find_all('div', class_='comment')
                for comment in comments:
                    comment_author = comment.find('div', class_='comment-author')
                    comment_content = comment.find('div', class_='comment-content')
                    
                    if comment_content:
                        result["comments"].append({
                            "author": comment_author.get_text(strip=True) if comment_author else "Unknown",
                            "content": comment_content.get_text(strip=True)
                        })
            
            return result
            
        finally:
            if driver:
                driver.quit()

    async def search_forum_posts(
        self,
        search_query: str,
        email: str,
        password: str,
        max_results: int = 50,
        headless: bool = True
    ) -> Dict[str, Any]:
        """Search forum posts."""
        self._log(f"Searching forum for: {search_query}")
        
        chrome_options = Options()
        if headless:
            chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        
        driver = None
        try:
            driver = webdriver.Chrome(options=chrome_options)
            
            # Navigate to forum search
            search_url = f"https://support.worldquantbrain.com/hc/zh-cn/community/search?utf8=✓&query={search_query}"
            driver.get(search_url)
            
            # Login if required (similar to get_forum_post)
            # ... login logic ...
            
            # Extract search results
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            results = []
            
            search_results = soup.find_all('div', class_='search-result')
            for result in search_results[:max_results]:
                title_elem = result.find('a', class_='search-result-link')
                if title_elem:
                    results.append({
                        "title": title_elem.get_text(strip=True),
                        "url": title_elem.get('href'),
                        "snippet": result.get_text(strip=True)
                    })
            
            return {
                "query": search_query,
                "results": results,
                "total_found": len(results)
            }
            
        finally:
            if driver:
                driver.quit()

    async def close(self) -> None:
        """Close the HTTP client."""
        await self.client.aclose()
