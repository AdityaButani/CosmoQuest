"""
Configuration file for CosmosQuest API Management

This file contains settings that can be easily modified to tune the behavior
of the Groq API manager without changing the core code.
"""

# API Manager Configuration
API_CONFIG = {
    # Retry settings
    "max_retries": 3,
    "base_retry_delay": 1.0,  # seconds
    
    # Cooldown periods
    "rate_limit_cooldown": 60,  # seconds to wait after rate limit
    "error_cooldown": 30,       # seconds to wait after multiple errors
    "max_errors_before_cooldown": 3,  # errors before cooldown
    
    # Request settings
    "default_timeout": 30,      # seconds
    "default_model": "llama-3.3-70b-versatile",
    "default_temperature": 0.7,
    "default_max_tokens": 2000,
    
    # Strategy settings
    "use_quest_based_rotation": False,  # If True, assign one key per quest
    "enable_smart_rotation": True,      # If True, use intelligent key rotation
    
    # Logging
    "log_level": "INFO",  # DEBUG, INFO, WARNING, ERROR
    "log_api_responses": False,  # Log full API responses (for debugging)
}

# Quest-specific settings
QUEST_CONFIG = {
    # Different models for different quest types (if needed)
    "quest_models": {
        1: "llama-3.3-70b-versatile",  # Foundations
        2: "llama-3.3-70b-versatile",  # Mechanisms  
        3: "llama-3.3-70b-versatile",  # Advanced Systems
        4: "llama-3.3-70b-versatile",  # Applications
        5: "llama-3.3-70b-versatile",  # Innovations
    },
    
    # Different token limits for different quests
    "quest_max_tokens": {
        1: 2000,
        2: 2500,  # Slightly more for mechanisms
        3: 2500,  # More for advanced content
        4: 2000,
        5: 2500,  # More for comprehensive content
    },
    
    # Temperature settings for creativity vs consistency
    "quest_temperature": {
        1: 0.6,  # More consistent for foundations
        2: 0.7,  # Balanced
        3: 0.7,  # Balanced
        4: 0.8,  # More creative for applications
        5: 0.8,  # More creative for innovations
    }
}

# Fallback configuration
FALLBACK_CONFIG = {
    "enable_openai_fallback": True,
    "fallback_model": "gpt-3.5-turbo",
    "fallback_timeout": 30,
    "enable_content_fallback": True,  # Use pre-generated content if all APIs fail
}

# Monitoring and alerting
MONITORING_CONFIG = {
    "enable_usage_tracking": True,
    "track_token_usage": True,
    "alert_on_key_exhaustion": True,
    "alert_on_high_error_rate": True,
    "error_rate_threshold": 0.1,  # 10% error rate triggers alert
}
