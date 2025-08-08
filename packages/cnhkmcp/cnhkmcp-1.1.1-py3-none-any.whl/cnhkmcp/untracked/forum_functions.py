#!/usr/bin/env python3
"""
WorldQuant BRAIN Forum Functions - Python Version
Comprehensive forum functionality including glossary, search, and post viewing.
"""

import asyncio
import re
import sys
import time
from datetime import datetime
from typing import Dict, Any, List, Optional

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import requests

# Initialize forum MCP server
try:
    from mcp.server.fastmcp import FastMCP
    forum_mcp = FastMCP('brain_forum_server')
except ImportError:
    # Fallback for testing
    forum_mcp = None

# Import BRAIN API authentication
try:
    from platform_functions import brain_client
    BRAIN_API_AVAILABLE = True
except ImportError:
    BRAIN_API_AVAILABLE = False
    brain_client = None

def log(message: str, level: str = "INFO"):
    """Log message with timestamp."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] [{level}] {message}", file=sys.stderr)

class ForumClient:
    """Forum client for WorldQuant BRAIN support site."""
    
    def __init__(self):
        self.base_url = "https://support.worldquantbrain.com"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36'
        })
        self.brain_authenticated = False
    
    async def test_brain_authentication(self, email: str, password: str) -> Dict[str, Any]:
        """Test BRAIN API authentication before proceeding with forum operations."""
        if not BRAIN_API_AVAILABLE:
            return {
                "success": False,
                "error": "BRAIN API not available. Please ensure platform_functions.py is in the same directory.",
                "recommendation": "Install or configure BRAIN API client first."
            }
        
        try:
            log("🔐 Testing BRAIN API authentication...", "INFO")
            
            # Test authentication using BRAIN API
            auth_result = await brain_client.authenticate(email, password)
            
            if auth_result.get('status') == 'authenticated' or 'user' in auth_result:
                self.brain_authenticated = True
                log("✅ BRAIN API authentication successful", "SUCCESS")
                return {
                    "success": True,
                    "message": "BRAIN API authentication successful",
                    "brain_auth": auth_result
                }
            else:
                log("❌ BRAIN API authentication failed", "ERROR")
                return {
                    "success": False,
                    "error": "BRAIN API authentication failed",
                    "brain_auth_result": auth_result
                }
                
        except Exception as e:
            log(f"❌ BRAIN API authentication error: {str(e)}", "ERROR")
            return {
                "success": False,
                "error": f"BRAIN API authentication error: {str(e)}",
                "recommendation": "Please check your credentials and try again."
            }
    
    def setup_chrome_options(self, headless: bool = True) -> Options:
        """Setup Chrome options for web scraping."""
        options = Options()
        
        if headless:
            options.add_argument('--headless')
        
        # Performance optimizations
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_argument('--log-level=3')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-web-security')
        options.add_argument('--disable-features=VizDisplayCompositor')
        options.add_argument('--disable-gpu')
        options.add_argument('--disable-extensions')
        options.add_argument('--disable-images')
        options.add_argument('--disable-javascript')
        options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36')
        
        return options
    
    async def create_driver(self, headless: bool = True) -> webdriver.Chrome:
        """Create and configure Chrome WebDriver."""
        options = self.setup_chrome_options(headless)
        driver = webdriver.Chrome(options=options)
        
        # Set aggressive timeouts for speed
        driver.set_page_load_timeout(30)
        driver.implicitly_wait(10)
        
        return driver
    
    async def login_to_forum(self, driver: webdriver.Chrome, email: str, password: str) -> bool:
        """Login to the WorldQuant BRAIN forum."""
        try:
            log("Opening login page", "WORK")
            driver.get("https://support.worldquantbrain.com/hc/en-us/signin")
            await asyncio.sleep(3)
            
            # Handle Cookie popup quickly
            try:
                cookie_button = WebDriverWait(driver, 35).until(
                    EC.element_to_be_clickable((By.XPATH, '//button[span[text()="Accept"]]'))
                )
                cookie_button.click()
                log("Cookie accepted", "WORK")
                await asyncio.sleep(1)
            except TimeoutException:
                log("No cookie popup found", "WORK")
            
            # Quick login
            log("Performing fast login", "WORK")
            email_input = WebDriverWait(driver, 35).until(
                EC.presence_of_element_located((By.NAME, "email"))
            )
            password_input = WebDriverWait(driver, 35).until(
                EC.presence_of_element_located((By.NAME, "currentPassword"))
            )
            
            email_input.clear()
            email_input.send_keys(email)
            password_input.clear()
            password_input.send_keys(password)
            
            login_button = WebDriverWait(driver, 35).until(
                EC.element_to_be_clickable((By.XPATH, '//button[@type="submit"]'))
            )
            login_button.click()
            log("Login submitted", "WORK")
            await asyncio.sleep(3)
            
            return True
            
        except Exception as e:
            log(f"Login failed: {str(e)}", "ERROR")
            return False

    async def get_glossary_terms(self, email: str, password: str, headless: bool = False) -> Dict[str, Any]:
        """Extract glossary terms from the forum."""
        # First test BRAIN API authentication
        auth_test = await self.test_brain_authentication(email, password)
        if not auth_test.get("success"):
            return {
                "error": "Authentication test failed",
                "auth_test_result": auth_test,
                "recommendation": "Please authenticate with BRAIN API first before accessing forum features."
            }
        
        driver = None
        try:
            log("Starting glossary extraction process", "INFO")
            
            # Add timeout protection
            async def extraction_with_timeout():
                return await self._perform_glossary_extraction(email, password, headless)
            
            # Run with 5-minute timeout
            result = await asyncio.wait_for(extraction_with_timeout(), timeout=300)
            return result
            
        except asyncio.TimeoutError:
            log("Glossary extraction timed out after 5 minutes", "ERROR")
            return {"error": "Glossary extraction timed out after 5 minutes"}
        except Exception as e:
            log(f"Glossary extraction failed: {str(e)}", "ERROR")
            return {"error": str(e)}
        finally:
            if driver:
                try:
                    driver.quit()
                except:
                    pass
    
    async def _perform_glossary_extraction(self, email: str, password: str, headless: bool) -> Dict[str, Any]:
        """Perform the actual glossary extraction."""
        driver = None
        try:
            driver = await self.create_driver(headless)
            
            # Login
            if not await self.login_to_forum(driver, email, password):
                raise Exception("Failed to login to forum")
            
            # Navigate to glossary page
            log("Navigating to glossary page", "WORK")
            driver.get("https://support.worldquantbrain.com/hc/en-us/articles/4902349883927-Click-here-for-a-list-of-terms-and-their-definitions")
            await asyncio.sleep(5)
            
            # Extract content
            log("Extracting glossary content", "WORK")
            page_source = driver.page_source
            soup = BeautifulSoup(page_source, 'html.parser')
            
            # Parse glossary terms
            terms = self._parse_glossary_terms(page_source)
            
            log(f"Extracted {len(terms)} glossary terms", "SUCCESS")
            return {
                "terms": terms,
                "total_count": len(terms),
                "extraction_timestamp": datetime.now().isoformat()
            }
            
        finally:
            if driver:
                try:
                    driver.quit()
                except:
                    pass
    
    def _parse_glossary_terms(self, content: str) -> List[Dict[str, str]]:
        """Parse glossary terms from HTML content."""
        terms = []
        lines = content.split('\n')
        
        current_term = None
        current_definition = []
        is_collecting_definition = False
        found_first_real_term = False
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Skip navigation and metadata lines at the beginning
            if not found_first_real_term and self._is_navigation_or_metadata(line):
                continue
            
            # Check if this line looks like a term
            if self._looks_like_term(line) and not is_collecting_definition:
                # Mark that we found the first real term
                if not found_first_real_term:
                    found_first_real_term = True
                
                # Save previous term if exists
                if current_term and current_definition:
                    terms.append({
                        "term": current_term.strip(),
                        "definition": " ".join(current_definition).strip()
                    })
                
                current_term = line
                current_definition = []
                is_collecting_definition = True
            elif is_collecting_definition and found_first_real_term:
                # Check if this is the start of a new term
                if self._looks_like_term(line):
                    # Save current term
                    if current_term and current_definition:
                        terms.append({
                            "term": current_term.strip(),
                            "definition": " ".join(current_definition).strip()
                        })
                    
                    current_term = line
                    current_definition = []
                else:
                    # Add to definition
                    if current_definition:
                        current_definition.append(line)
                    else:
                        current_definition = [line]
        
        # Don't forget the last term
        if current_term and current_definition and found_first_real_term:
            terms.append({
                "term": current_term.strip(),
                "definition": " ".join(current_definition).strip()
            })
        
        # Filter out invalid terms and improve quality
        return [term for term in terms if 
                len(term["term"]) > 0 and 
                len(term["definition"]) > 10 and  # Ensure meaningful definitions
                not self._is_navigation_or_metadata(term["term"]) and
                "ago" not in term["definition"] and  # Remove timestamp-like definitions
                "minute read" not in term["definition"]]  # Remove reading time

    def _looks_like_term(self, line: str) -> bool:
        """Check if a line looks like a glossary term."""
        # Skip very long lines (likely definitions)
        if len(line) > 100:
            return False
        
        # Skip navigation and metadata
        if self._is_navigation_or_metadata(line):
            return False
        
        # Skip lines that start with common definition words
        definition_starters = ['the', 'a', 'an', 'this', 'that', 'it', 'is', 'are', 'was', 'were', 'for', 'to', 'in', 'on', 'at', 'by', 'with']
        first_word = line.lower().split(' ')[0]
        if first_word and first_word in definition_starters:
            return False
        
        # Check if line has characteristics of a term
        # Terms are often short, may be all caps, or start with capital
        is_short = len(line) <= 80
        starts_with_capital = bool(re.match(r'^[A-Z]', line))
        has_all_caps = bool(re.match(r'^[A-Z\s\-\/\(\)]+$', line))
        has_reasonable_length = len(line) >= 2
        
        return is_short and has_reasonable_length and (starts_with_capital or has_all_caps)
    
    def _is_navigation_or_metadata(self, line: str) -> bool:
        """Check if a line is navigation or metadata."""
        navigation_patterns = [
            r'^\d+ days? ago$',
            r'~\d+ minute read',
            r'^Follow',
            r'^Not yet followed',
            r'^Updated$',
            r'^AS\d+$',
            r'^[A-Z] - [A-Z] - [A-Z]',  # Letter navigation
            r'^A$',
            r'^B$',
            r'^[A-Z]$'  # Single letters
        ]
        
        return any(re.match(pattern, line.strip()) for pattern in navigation_patterns)

    async def search_forum_posts(self, email: str, password: str, search_query: str, 
                               max_results: int = 50, headless: bool = True) -> Dict[str, Any]:
        """Search forum posts."""
        # First test BRAIN API authentication
        auth_test = await self.test_brain_authentication(email, password)
        if not auth_test.get("success"):
            return {
                "error": "Authentication test failed",
                "auth_test_result": auth_test,
                "recommendation": "Please authenticate with BRAIN API first before accessing forum features."
            }
        
        driver = None
        try:
            log("Starting forum search process", "INFO")
            log(f"Search query: '{search_query}'", "INFO")
            log(f"Max results: {max_results}", "INFO")
            
            driver = await self.create_driver(headless)
            
            # Login
            if not await self.login_to_forum(driver, email, password):
                raise Exception("Failed to login to forum")
            
            # Navigate to search
            encoded_query = requests.utils.quote(search_query)
            search_url = f"https://support.worldquantbrain.com/hc/zh-cn/search?utf8=%E2%9C%93&query={encoded_query}"
            log(f"Opening search URL: {search_url}", "WORK")
            
            driver.get(search_url)
            await asyncio.sleep(2)
            
            # Collect results with pagination
            all_results = []
            page_num = 1
            
            log("Starting result collection with pagination", "WORK")
            
            while len(all_results) < max_results:
                log(f"Processing page {page_num}", "INFO")
                
                # Wait for search results
                try:
                    WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, '.search-results-list, .search-result-list-item'))
                    )
                except TimeoutException:
                    log(f"No search results found on page {page_num}", "WARNING")
                    break
                
                # Extract results from current page
                page_source = driver.page_source
                soup = BeautifulSoup(page_source, 'html.parser')
                page_results = self._extract_search_results(soup, page_num)
                
                if not page_results:
                    log(f"No more results found on page {page_num}", "INFO")
                    break
                
                all_results.extend(page_results)
                
                # Check if we have enough results
                if len(all_results) >= max_results:
                    all_results = all_results[:max_results]
                    break
                
                # Try to go to next page
                if not await self._go_to_next_search_page(driver, soup):
                    log("No more pages available", "INFO")
                    break
                
                page_num += 1
                await asyncio.sleep(1)
            
            # Analyze results
            analysis = self._analyze_search_results(all_results, search_query)
            
            log(f"Search completed. Found {len(all_results)} results", "SUCCESS")
            return {
                "success": True,
                "results": all_results,
                "total_found": len(all_results),
                "search_query": search_query,
                "analysis": analysis,
                "search_timestamp": datetime.now().isoformat(),
                "auth_status": "authenticated"
            }
            
        except Exception as e:
            log(f"Search failed: {str(e)}", "ERROR")
            return {"error": str(e)}
        finally:
            if driver:
                try:
                    driver.quit()
                except:
                    pass
    
    def _extract_search_results(self, soup: BeautifulSoup, page_num: int) -> List[Dict[str, Any]]:
        """Extract search results from a page."""
        results = []
        
        # Look for search result items using the correct selector - they are <li> elements
        result_items = soup.find_all('li', class_='search-result-list-item')
        
        for item in result_items:
            try:
                # Extract title and link from the h2 element
                title_elem = item.find('h2', class_='search-result-title')
                if title_elem:
                    link_elem = title_elem.find('a', class_='results-list-item-link')
                    if link_elem:
                        title = link_elem.get_text().strip()
                        link = link_elem.get('href', '')
                        if link and not link.startswith('http'):
                            link = f"https://support.worldquantbrain.com{link}"
                    else:
                        title = title_elem.get_text().strip()
                        link = ""
                else:
                    title = "No title"
                    link = ""
                
                # Extract description
                desc_elem = item.find('div', class_='search-results-description')
                description = desc_elem.get_text().strip() if desc_elem else ""
                
                # Extract votes
                votes_elem = item.find('span', class_='search-result-votes')
                votes = "0"
                if votes_elem:
                    votes_text = votes_elem.get_text().strip()
                    votes_match = re.search(r'(\d+)\s*票', votes_text)
                    if votes_match:
                        votes = votes_match.group(1)
                
                # Extract comments
                comments_elem = item.find('span', class_='search-result-meta-count')
                comments = "0"
                if comments_elem:
                    comments_text = comments_elem.get_text().strip()
                    comments_match = re.search(r'(\d+)\s*条评论', comments_text)
                    if comments_match:
                        comments = comments_match.group(1)
                
                # Extract author and date from meta-group
                author = "Unknown"
                date = "Unknown"
                
                meta_group = item.find('ul', class_='meta-group')
                if meta_group:
                    meta_items = meta_group.find_all('li', class_='meta-data')
                    for meta_item in meta_items:
                        meta_text = meta_item.get_text().strip()
                        # Check if it's a date (contains 年)
                        if '年' in meta_text and '月' in meta_text and '日' in meta_text:
                            date = meta_text
                        # Check if it's an author (alphanumeric code like SH90982)
                        elif re.match(r'^[A-Z]{2}\d+$', meta_text):
                            author = meta_text
                
                results.append({
                    "title": title,
                    "link": link,
                    "description": description,
                    "author": author,
                    "date": date,
                    "votes": votes,
                    "comments": comments,
                    "page": page_num
                })
                
            except Exception as e:
                log(f"Error extracting result: {str(e)}", "WARNING")
                continue
        
        return results
    
    async def _go_to_next_search_page(self, driver: webdriver.Chrome, soup: BeautifulSoup) -> bool:
        """Navigate to the next search page."""
        try:
            # Look for next page link
            next_link = soup.find('a', string=re.compile(r'next|下一页', re.IGNORECASE))
            if not next_link:
                next_link = soup.find('a', {'rel': 'next'})
            
            if next_link and next_link.get('href'):
                next_url = next_link['href']
                if not next_url.startswith('http'):
                    next_url = f"https://support.worldquantbrain.com{next_url}"
                
                driver.get(next_url)
                await asyncio.sleep(2)
                return True
            
            return False
            
        except Exception as e:
            log(f"Error navigating to next page: {str(e)}", "WARNING")
            return False
    
    def _analyze_search_results(self, results: List[Dict[str, Any]], search_query: str) -> Dict[str, Any]:
        """Analyze search results for insights."""
        if not results:
            return {"message": "No results found"}
        
        # Basic statistics
        total_results = len(results)
        
        # Categorize results by type
        categories = {}
        for result in results:
            title = result.get('title', '').lower()
            if 'tutorial' in title or 'guide' in title:
                categories['tutorials'] = categories.get('tutorials', 0) + 1
            elif 'api' in title or 'reference' in title:
                categories['api_docs'] = categories.get('api_docs', 0) + 1
            elif 'error' in title or 'issue' in title or 'problem' in title:
                categories['troubleshooting'] = categories.get('troubleshooting', 0) + 1
            elif 'competition' in title or 'event' in title:
                categories['competitions'] = categories.get('competitions', 0) + 1
            else:
                categories['general'] = categories.get('general', 0) + 1
        
        # Find most relevant results (containing search terms)
        search_terms = search_query.lower().split()
        relevant_results = []
        
        for result in results:
            title = result.get('title', '').lower()
            snippet = result.get('snippet', '').lower()
            text = f"{title} {snippet}"
            
            term_matches = sum(1 for term in search_terms if term in text)
            if term_matches > 0:
                relevant_results.append({
                    "result": result,
                    "relevance_score": term_matches / len(search_terms)
                })
        
        # Sort by relevance
        relevant_results.sort(key=lambda x: x['relevance_score'], reverse=True)
        
        return {
            "total_results": total_results,
            "categories": categories,
            "most_relevant": relevant_results[:5] if relevant_results else [],
            "search_terms": search_terms
        }

    async def read_full_forum_post(self, email: str, password: str, post_url_or_id: str, 
                                 headless: bool = False, include_comments: bool = True) -> Dict[str, Any]:
        """Read a complete forum post with optional comments."""
        # First test BRAIN API authentication
        auth_test = await self.test_brain_authentication(email, password)
        if not auth_test.get("success"):
            return {
                "error": "Authentication test failed",
                "auth_test_result": auth_test,
                "recommendation": "Please authenticate with BRAIN API first before accessing forum features."
            }
        
        driver = None
        try:
            log("Starting forum post reading process", "INFO")
            
            # Determine if input is URL or article ID
            is_url = post_url_or_id.startswith('http')
            if is_url:
                post_url = post_url_or_id
            else:
                post_url = f"https://support.worldquantbrain.com/hc/zh-cn/community/posts/{post_url_or_id}"
            
            log(f"Target URL: {post_url}", "INFO")
            log(f"Include comments: {include_comments}", "INFO")
            
            driver = await self.create_driver(headless)
            
            # Login
            if not await self.login_to_forum(driver, email, password):
                raise Exception("Failed to login to forum")
            
            # Navigate directly to post URL
            log(f"Opening post: {post_url}", "WORK")
            driver.get(post_url)
            log("Post page loaded, extracting content immediately", "WORK")
            
            # Wait minimal time for content to appear
            await asyncio.sleep(2)
            
            # Extract post content quickly
            post_data = {}
            page_source = driver.page_source
            soup = BeautifulSoup(page_source, 'html.parser')
            
            # Extract post title
            title = soup.select_one('.post-title, h1, .article-title')
            if not title:
                title = soup.select_one('title')
            post_data['title'] = title.get_text().strip() if title else 'Unknown Title'
            
            # Extract post author
            author = soup.select_one('.post-author, .author, .article-author')
            if not author:
                author = soup.select_one('.comment-author')
            post_data['author'] = author.get_text().strip() if author else 'Unknown Author'
            
            # Extract post date
            date = soup.select_one('.post-date, .date, .article-date, time')
            if not date:
                time_element = soup.select_one('time')
                if time_element:
                    date = time_element.get('datetime') or time_element.get('title') or time_element.get_text().strip()
                else:
                    date = 'Unknown Date'
            else:
                date = date.get_text().strip()
            post_data['date'] = date if date else 'Unknown Date'
            
            # Extract post content
            post_content = soup.select_one('.post-body, .article-body, .content, .post-content')
            if not post_content:
                post_content = soup.select_one('article, main')
            
            if post_content:
                post_data['content_html'] = str(post_content)
                post_data['content_text'] = post_content.get_text().strip()
            else:
                post_data['content_html'] = 'No content found'
                post_data['content_text'] = 'No content found'
            
            post_data['url'] = post_url
            post_data['current_url'] = driver.current_url
            
            log(f"Post content extracted: \"{post_data['title']}\"", "SUCCESS")
            
            comments = []
            total_comments = 0
            
            # Extract comments conditionally
            if include_comments:
                log("Extracting comments...", "WORK")
                comments = await self._extract_forum_comments_full(driver, soup)
                total_comments = len(comments)
                log(f"Extracted {total_comments} comments", "SUCCESS")
            else:
                log("Skipping comment extraction (includeComments=false)", "INFO")
            
            return {
                "success": True,
                "post": post_data,
                "comments": comments,
                "total_comments": total_comments,
                "extracted_at": datetime.now().isoformat(),
                "processing_time": "full_extraction_with_comments" if include_comments else "post_only_extraction",
                "include_comments": include_comments,
                "auth_status": "authenticated"
            }
            
        except Exception as e:
            log(f"Failed to read forum post: {str(e)}", "ERROR")
            return {"error": str(e)}
        finally:
            if driver:
                try:
                    driver.quit()
                except:
                    pass

    async def _extract_forum_comments_full(self, driver, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """Extract all comments from forum post with pagination support."""
        all_comments = []
        page_num = 1
        
        try:
            # First extract comments from current page source
            page_comments = self._parse_comments_from_html(soup)
            all_comments.extend(page_comments)
            log(f"Found {len(page_comments)} comments on page {page_num}", "INFO")
            
            # Check for pagination and continue if needed
            while True:
                try:
                    # Look for next page button
                    next_button = driver.find_element(By.CSS_SELECTOR, "span.pagination-next-text, .pagination-next, .next")
                    next_text = next_button.text
                    
                    if "下一页" in next_text or "Next" in next_text or "next" in next_text.lower():
                        log(f"Found next page, continuing to page {page_num + 1}", "INFO")
                        next_button.click()
                        await asyncio.sleep(2)  # Minimal wait for next page
                        
                        # Extract comments from new page
                        new_page_source = driver.page_source
                        new_soup = BeautifulSoup(new_page_source, 'html.parser')
                        new_page_comments = self._parse_comments_from_html(new_soup)
                        
                        if len(new_page_comments) == 0:
                            break
                        
                        all_comments.extend(new_page_comments)
                        page_num += 1
                        log(f"Found {len(new_page_comments)} comments on page {page_num}", "INFO")
                    else:
                        break
                except Exception as e:
                    log("No more pages found", "INFO")
                    break
            
            return all_comments
            
        except Exception as e:
            log(f"Error in comment extraction: {str(e)}", "WARNING")
            return all_comments

    def _parse_comments_from_html(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """Parse comments from HTML using BeautifulSoup."""
        comments = []
        
        # Try multiple selectors for comments
        comment_selectors = [
            'ul#comments.comment-list li.comment',
            '.comment-list .comment',
            '.comments .comment',
            'li.comment',
            '.comment-item'
        ]
        
        comment_elements = None
        
        for selector in comment_selectors:
            comment_elements = soup.select(selector)
            if comment_elements:
                log(f"Found comments using selector: {selector}", "INFO")
                break
        
        if not comment_elements:
            log("No comments found on this page", "INFO")
            return comments
        
        for index, element in enumerate(comment_elements):
            try:
                comment = {}
                
                # Extract comment ID
                comment['id'] = element.get('id') or f"comment-{index}"
                
                # Extract author
                author_element = element.select_one('.comment-author a, .author a, .comment-author')
                comment['author'] = author_element.get_text().strip() if author_element else 'Unknown Author'
                comment['author_link'] = author_element.get('href') if author_element else ''
                
                # Extract date
                time_element = element.select_one('.meta-data time, time, .date, .comment-date')
                if time_element:
                    comment['date'] = time_element.get('datetime') or time_element.get('title') or time_element.get_text().strip()
                    comment['date_display'] = time_element.get('title') or time_element.get_text().strip()
                else:
                    comment['date'] = 'Unknown Date'
                    comment['date_display'] = 'Unknown Date'
                
                # Extract content
                content_element = element.select_one('.comment-body, .comment-content, .content')
                if content_element:
                    comment['content_html'] = str(content_element)
                    comment['content_text'] = content_element.get_text().strip()
                else:
                    comment['content_html'] = ''
                    comment['content_text'] = ''
                
                # Extract votes
                vote_element = element.select_one('.vote-up span, .votes, .vote-count')
                comment['votes'] = vote_element.get_text().strip() if vote_element else '0'
                
                # Extract status
                status_element = element.select_one('.status-label, .status, .badge')
                comment['status'] = status_element.get_text().strip() if status_element else '普通评论'
                
                if comment['content_text']:
                    comments.append(comment)
                
            except Exception as e:
                log(f"Error parsing comment {index}: {str(e)}", "WARNING")
        
        return comments

# Initialize forum client
forum_client = ForumClient()

# MCP Tools for Forum Functions
if forum_mcp:
    @forum_mcp.tool()
    async def get_glossary_terms(email: str, password: str, headless: bool = False) -> Dict[str, Any]:
        """
        📚 Extract glossary terms from WorldQuant BRAIN forum.
        
        Args:
            email: Your BRAIN platform email address
            password: Your BRAIN platform password
            headless: Run browser in headless mode (default: False)
        
        Returns:
            Glossary terms with definitions
        """
        try:
            return await forum_client.get_glossary_terms(email, password, headless)
        except Exception as e:
            return {"error": str(e)}

    @forum_mcp.tool()
    async def search_forum_posts(email: str, password: str, search_query: str, 
                               max_results: int = 50, headless: bool = True) -> Dict[str, Any]:
        """
        🔍 Search forum posts on WorldQuant BRAIN support site.
        
        Args:
            email: Your BRAIN platform email address
            password: Your BRAIN platform password
            search_query: Search term or phrase
            max_results: Maximum number of results to return (default: 50)
            headless: Run browser in headless mode (default: True)
        
        Returns:
            Search results with analysis
        """
        try:
            return await forum_client.search_forum_posts(email, password, search_query, max_results, headless)
        except Exception as e:
            return {"error": str(e)}

    @forum_mcp.tool()
    async def read_full_forum_post(email: str, password: str, post_url_or_id: str, 
                                  headless: bool = False, include_comments: bool = True) -> Dict[str, Any]:
        """
        📖 Read a full forum post with optional comments.
        
        Args:
            email: Your BRAIN platform email address
            password: Your BRAIN platform password
            post_url_or_id: URL or ID of the post to read
            headless: Run browser in headless mode (default: False)
            include_comments: Include comments in the result (default: True)
        
        Returns:
            Complete forum post with all content
        """
        try:
            return await forum_client.read_full_forum_post(email, password, post_url_or_id, headless, include_comments)
        except Exception as e:
            return {"error": str(e)}

if __name__ == "__main__":
    print("📚 WorldQuant BRAIN Forum Functions Server Starting...", file=sys.stderr)
    if forum_mcp:
        forum_mcp.run()
    else:
        print("FastMCP is not available. Please install it to run the server.", file=sys.stderr) 