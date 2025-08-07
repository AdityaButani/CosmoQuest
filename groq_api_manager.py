"""
Groq API Key Manager with Robust Fallback Mechanism

This module provides a comprehensive solution for managing multiple Groq API keys
with automatic fallback, rate limiting tracking, and intelligent key rotation.
"""

import os
import time
import json
import logging
import requests
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # If python-dotenv is not available, try manual loading
    env_path = os.path.join(os.path.dirname(__file__), '.env')
    if os.path.exists(env_path):
        with open(env_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key.strip()] = value.strip()

try:
    from config_production import API_CONFIG, QUEST_CONFIG
except ImportError:
    try:
        from config import API_CONFIG, QUEST_CONFIG
    except ImportError:
        # Default configuration if no config files are available
        API_CONFIG = {
            "max_retries": 3,
            "base_retry_delay": 1.0,
            "rate_limit_cooldown": 60,
            "error_cooldown": 30,
            "max_errors_before_cooldown": 3,
            "default_timeout": 30,
            "default_model": "llama-3.3-70b-versatile",
            "default_temperature": 0.7,
            "default_max_tokens": 2000,
            "use_quest_based_rotation": False,
            "enable_smart_rotation": True,
            "log_level": "WARNING",
            "log_api_responses": False,
        }
        QUEST_CONFIG = {
            "quest_models": {},
            "quest_max_tokens": {},
            "quest_temperature": {},
        }

class APIKeyStatus(Enum):
    ACTIVE = "active"
    RATE_LIMITED = "rate_limited"
    ERROR = "error"
    EXHAUSTED = "exhausted"
    COOLING_DOWN = "cooling_down"

@dataclass
class APIKeyInfo:
    """Information about an API key and its usage status"""
    key: str
    name: str
    status: APIKeyStatus
    last_used: Optional[datetime] = None
    rate_limit_reset: Optional[datetime] = None
    error_count: int = 0
    total_requests: int = 0
    successful_requests: int = 0
    last_error: Optional[str] = None
    cooldown_until: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for logging"""
        data = asdict(self)
        # Convert datetime objects to strings
        for key, value in data.items():
            if isinstance(value, datetime):
                data[key] = value.isoformat()
            elif isinstance(value, APIKeyStatus):
                data[key] = value.value
        return data

class GroqAPIManager:
    """
    Manages multiple Groq API keys with intelligent fallback and rotation.
    
    Features:
    - Automatic fallback between keys when rate limits are hit
    - Intelligent key rotation to distribute load
    - Retry logic with exponential backoff
    - Comprehensive error handling and logging
    - Rate limit tracking and recovery
    """
    
    def __init__(self, log_level: int = None):
        # Set up logging
        log_level = log_level or getattr(logging, API_CONFIG.get("log_level", "INFO"))
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(log_level)
        
        # API configuration from config file
        self.api_url = "https://api.groq.com/openai/v1/chat/completions"
        self.default_model = API_CONFIG.get("default_model", "llama-3.3-70b-versatile")
        self.default_timeout = API_CONFIG.get("default_timeout", 30)
        
        # Load API keys from environment
        self.api_keys: List[APIKeyInfo] = self._load_api_keys()
        
        # Configuration parameters from config file
        self.max_retries = API_CONFIG.get("max_retries", 3)
        self.base_retry_delay = API_CONFIG.get("base_retry_delay", 1.0)
        self.rate_limit_cooldown = API_CONFIG.get("rate_limit_cooldown", 60)
        self.error_cooldown = API_CONFIG.get("error_cooldown", 30)
        self.max_errors_before_cooldown = API_CONFIG.get("max_errors_before_cooldown", 3)
        
        # Strategy configuration
        self.use_quest_based_rotation = API_CONFIG.get("use_quest_based_rotation", False)
        self.enable_smart_rotation = API_CONFIG.get("enable_smart_rotation", True)
        self.log_api_responses = API_CONFIG.get("log_api_responses", False)
        
        # Statistics
        self.stats = {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "key_switches": 0,
            "rate_limit_hits": 0
        }
        
        self.logger.info(f"GroqAPIManager initialized with {len(self.api_keys)} API keys")
    
    def _load_api_keys(self) -> List[APIKeyInfo]:
        """Load API keys from environment variables"""
        keys = []
        key_names = ["GROQ_API_KEY", "GROQ_API_KEY2", "GROQ_API_KEY3", "GROQ_API_KEY4"]
        
        for name in key_names:
            key_value = os.getenv(name)
            if key_value:
                keys.append(APIKeyInfo(
                    key=key_value,
                    name=name,
                    status=APIKeyStatus.ACTIVE
                ))
                self.logger.info(f"Loaded API key: {name}")
            else:
                self.logger.warning(f"API key not found: {name}")
        
        if not keys:
            raise ValueError("No Groq API keys found in environment variables")
        
        return keys
    
    def _get_next_available_key(self) -> Optional[APIKeyInfo]:
        """Get the next available API key for use"""
        now = datetime.now()
        
        # First, try to find an active key
        for key_info in self.api_keys:
            if (key_info.status == APIKeyStatus.ACTIVE and 
                (key_info.cooldown_until is None or key_info.cooldown_until <= now)):
                return key_info
        
        # If no active keys, try keys that might have recovered from rate limiting
        for key_info in self.api_keys:
            if (key_info.status == APIKeyStatus.RATE_LIMITED and
                key_info.rate_limit_reset and key_info.rate_limit_reset <= now):
                key_info.status = APIKeyStatus.ACTIVE
                key_info.rate_limit_reset = None
                self.logger.info(f"Key {key_info.name} recovered from rate limit")
                return key_info
        
        # If no keys are available, try cooling down keys
        for key_info in self.api_keys:
            if (key_info.status == APIKeyStatus.COOLING_DOWN and
                key_info.cooldown_until and key_info.cooldown_until <= now):
                key_info.status = APIKeyStatus.ACTIVE
                key_info.cooldown_until = None
                key_info.error_count = 0  # Reset error count
                self.logger.info(f"Key {key_info.name} recovered from cooldown")
                return key_info
        
        return None
    
    def _handle_api_response(self, response: requests.Response, key_info: APIKeyInfo) -> Tuple[bool, Optional[Dict[str, Any]]]:
        """Handle API response and update key status accordingly"""
        now = datetime.now()
        
        if response.status_code == 200:
            # Success
            key_info.successful_requests += 1
            key_info.last_used = now
            key_info.error_count = 0  # Reset error count on success
            
            try:
                data = response.json()
                content = data['choices'][0]['message']['content'].strip()
                self.logger.info(f"Successful API call using {key_info.name}")
                
                # More robust JSON parsing with fallback handling
                try:
                    parsed_content = json.loads(content)
                    # Validate that we have a proper response structure
                    if isinstance(parsed_content, dict):
                        return True, parsed_content
                    else:
                        self.logger.error(f"API response is not a valid dictionary: {type(parsed_content)}")
                        return False, None
                except json.JSONDecodeError as json_err:
                    self.logger.error(f"JSON decode error for key {key_info.name}: {str(json_err)}")
                    self.logger.error(f"Raw content: {content[:500]}...")
                    # Mark this as an error to trigger fallback
                    key_info.error_count += 1
                    return False, None
                    
            except (KeyError, IndexError) as e:
                self.logger.error(f"Invalid API response structure from {key_info.name}: {str(e)}")
                key_info.error_count += 1
                return False, None
            except Exception as e:
                self.logger.error(f"Unexpected error parsing response from {key_info.name}: {str(e)}")
                key_info.error_count += 1
                return False, None
        
        elif response.status_code == 429:
            # Rate limit hit
            key_info.status = APIKeyStatus.RATE_LIMITED
            key_info.rate_limit_reset = now + timedelta(seconds=self.rate_limit_cooldown)
            self.stats["rate_limit_hits"] += 1
            
            # Try to get reset time from headers
            reset_time = response.headers.get('x-ratelimit-reset-requests')
            if reset_time:
                try:
                    key_info.rate_limit_reset = datetime.fromtimestamp(int(reset_time))
                except (ValueError, TypeError):
                    pass
            
            self.logger.warning(f"Rate limit hit for {key_info.name}, cooldown until {key_info.rate_limit_reset}")
            return False, {"rate_limit": True, "key": key_info.name}
        
        else:
            # Other errors
            key_info.error_count += 1
            key_info.last_error = f"HTTP {response.status_code}: {response.text[:200]}"
            
            if key_info.error_count >= self.max_errors_before_cooldown:
                key_info.status = APIKeyStatus.COOLING_DOWN
                key_info.cooldown_until = now + timedelta(seconds=self.error_cooldown)
                self.logger.error(f"Key {key_info.name} put on cooldown after {key_info.error_count} errors")
            
            self.logger.error(f"API error for {key_info.name}: {response.status_code} - {response.text[:200]}")
            return False, None
    
    def _make_request_with_key(self, key_info: APIKeyInfo, prompt: str, 
                              model: str = None, temperature: float = 0.7, 
                              max_tokens: int = 2000) -> Tuple[bool, Optional[Dict[str, Any]]]:
        """Make a single API request with a specific key"""
        headers = {
            "Authorization": f"Bearer {key_info.key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": model or self.default_model,
            "messages": [{"role": "system", "content": prompt}],
            "temperature": temperature,
            "max_tokens": max_tokens
        }
        
        key_info.total_requests += 1
        self.stats["total_requests"] += 1
        
        try:
            response = requests.post(
                self.api_url, 
                headers=headers, 
                json=payload, 
                timeout=self.default_timeout
            )
            
            return self._handle_api_response(response, key_info)
            
        except requests.exceptions.RequestException as e:
            key_info.error_count += 1
            key_info.last_error = f"Request exception: {str(e)}"
            self.logger.error(f"Request failed for {key_info.name}: {str(e)}")
            return False, None
    
    def make_request(self, prompt: str, model: str = None, temperature: float = None, 
                    max_tokens: int = None, max_retries: int = None, quest_num: int = None) -> Optional[Dict[str, Any]]:
        """
        Make an API request with automatic fallback and retry logic.
        
        Args:
            prompt: The prompt to send to the API
            model: The model to use (uses quest-specific or default if None)
            temperature: Sampling temperature (uses quest-specific or default if None)
            max_tokens: Maximum tokens in response (uses quest-specific or default if None)
            max_retries: Maximum number of retries (uses instance default if None)
            quest_num: Quest number for quest-specific configuration
        
        Returns:
            Dictionary containing the parsed response, or None if all keys fail
        """
        # Apply quest-specific configurations
        if quest_num:
            model = model or QUEST_CONFIG.get("quest_models", {}).get(quest_num, self.default_model)
            temperature = temperature or QUEST_CONFIG.get("quest_temperature", {}).get(quest_num, API_CONFIG.get("default_temperature", 0.7))
            max_tokens = max_tokens or QUEST_CONFIG.get("quest_max_tokens", {}).get(quest_num, API_CONFIG.get("default_max_tokens", 2000))
        else:
            model = model or self.default_model
            temperature = temperature or API_CONFIG.get("default_temperature", 0.7)
            max_tokens = max_tokens or API_CONFIG.get("default_max_tokens", 2000)
        
        max_retries = max_retries or self.max_retries
        attempt = 0
        
        # If quest-based rotation is enabled, try to get quest-specific key first
        if self.use_quest_based_rotation and quest_num:
            quest_key = self.get_key_for_quest(quest_num)
            if quest_key:
                success, result = self._make_request_with_key(
                    quest_key, prompt, model, temperature, max_tokens
                )
                if success:
                    self.stats["successful_requests"] += 1
                    return result
                # If quest-specific key fails, continue with normal rotation
        
        while attempt < max_retries:
            # Get next available key
            key_info = self._get_next_available_key()
            
            if not key_info:
                self.logger.error("No available API keys found")
                # Wait a bit before retrying in case keys recover
                if attempt < max_retries - 1:
                    time.sleep(self.base_retry_delay * (2 ** attempt))
                    attempt += 1
                    continue
                else:
                    break
            
            # Make the request
            success, result = self._make_request_with_key(
                key_info, prompt, model, temperature, max_tokens
            )
            
            if success:
                self.stats["successful_requests"] += 1
                return result
            
            # If we hit a rate limit, try the next key immediately
            if result and result.get("rate_limit"):
                self.stats["key_switches"] += 1
                self.logger.info(f"Switching from {key_info.name} due to rate limit")
                continue
            
            # For other errors, implement exponential backoff
            if attempt < max_retries - 1:
                delay = self.base_retry_delay * (2 ** attempt)
                self.logger.info(f"Retrying in {delay} seconds (attempt {attempt + 1}/{max_retries})")
                time.sleep(delay)
            
            attempt += 1
        
        self.stats["failed_requests"] += 1
        self.logger.error(f"All API keys exhausted after {max_retries} attempts")
        return None
    
    def get_status(self) -> Dict[str, Any]:
        """Get current status of all API keys and manager statistics"""
        now = datetime.now()
        
        status = {
            "timestamp": now.isoformat(),
            "stats": self.stats.copy(),
            "keys": []
        }
        
        for key_info in self.api_keys:
            key_status = key_info.to_dict()
            
            # Add additional computed fields
            if key_info.total_requests > 0:
                key_status["success_rate"] = key_info.successful_requests / key_info.total_requests
            else:
                key_status["success_rate"] = 0.0
            
            # Check if key is currently available
            key_status["available"] = (
                key_info.status == APIKeyStatus.ACTIVE and
                (key_info.cooldown_until is None or key_info.cooldown_until <= now) and
                (key_info.rate_limit_reset is None or key_info.rate_limit_reset <= now)
            )
            
            status["keys"].append(key_status)
        
        return status
    
    def reset_key_status(self, key_name: str = None) -> bool:
        """
        Reset the status of a specific key or all keys to ACTIVE.
        Useful for manual recovery or testing.
        """
        if key_name:
            for key_info in self.api_keys:
                if key_info.name == key_name:
                    key_info.status = APIKeyStatus.ACTIVE
                    key_info.error_count = 0
                    key_info.cooldown_until = None
                    key_info.rate_limit_reset = None
                    key_info.last_error = None
                    self.logger.info(f"Reset status for key: {key_name}")
                    return True
            return False
        else:
            for key_info in self.api_keys:
                key_info.status = APIKeyStatus.ACTIVE
                key_info.error_count = 0
                key_info.cooldown_until = None
                key_info.rate_limit_reset = None
                key_info.last_error = None
            self.logger.info("Reset status for all keys")
            return True
    
    def get_key_for_quest(self, quest_num: int) -> Optional[APIKeyInfo]:
        """
        Get a specific key for a quest (alternative strategy: one key per quest).
        This provides a simple round-robin approach where each quest uses a specific key.
        """
        if not self.api_keys:
            return None
        
        # Use modulo to cycle through keys based on quest number
        key_index = (quest_num - 1) % len(self.api_keys)
        key_info = self.api_keys[key_index]
        
        # Check if the assigned key is available
        now = datetime.now()
        if (key_info.status == APIKeyStatus.ACTIVE and 
            (key_info.cooldown_until is None or key_info.cooldown_until <= now) and
            (key_info.rate_limit_reset is None or key_info.rate_limit_reset <= now)):
            return key_info
        
        # If assigned key is not available, fall back to any available key
        return self._get_next_available_key()

# Global instance for use throughout the application
groq_manager = GroqAPIManager()

def get_groq_manager() -> GroqAPIManager:
    """Get the global Groq API manager instance"""
    return groq_manager
