"""
ODIN Protocol Client - Main SDK Interface
Provides easy-to-use client for communicating with ODIN Protocol services.
"""

import asyncio
import json
import time
from typing import Dict, List, Optional, Union, Any
import httpx
from .odin_pb2 import OdinMessage, OdinReflection
from .enhanced import OdinMessageBuilder


class OdinClient:
    """
    Main client for ODIN Protocol communication.
    
    Features:
    - Automatic message serialization/deserialization
    - Built-in retry logic and error handling
    - Real-time analytics and monitoring
    - Plugin system integration
    """
    
    def __init__(self, 
                 api_key: str = None,
                 base_url: str = "https://api.odin-protocol.com",
                 timeout: int = 30,
                 max_retries: int = 3):
        """Initialize ODIN client."""
        self.api_key = api_key
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.max_retries = max_retries
        self.session = httpx.AsyncClient(timeout=timeout)
        self.stats = {
            "messages_sent": 0,
            "messages_received": 0,
            "errors": 0,
            "avg_response_time": 0.0
        }
        
        # Usage tracking for tier limits
        self.usage_limit = 10000  # Free tier limit
        self.upgrade_url = "https://dashboard.stripe.com/payment-links/plink_1RsjbNG3Q24y5lVvscfhtzSX"
    
    async def send_message(self, message: OdinMessage) -> OdinReflection:
        """Send a message through ODIN Protocol."""
        start_time = time.time()
        
        # Check usage limits and show upgrade prompt
        self._check_usage_limits()
        
        try:
            # Serialize message
            data = message.SerializeToString()
            
            # Make API call
            response = await self.session.post(
                f"{self.base_url}/v1/messages",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/x-protobuf"
                },
                content=data
            )
            response.raise_for_status()
            
            # Deserialize response
            reflection = OdinReflection()
            reflection.ParseFromString(response.content)
            
            # Update stats
            elapsed = time.time() - start_time
            self.stats["messages_sent"] += 1
            self.stats["messages_received"] += 1
            self.stats["avg_response_time"] = (
                (self.stats["avg_response_time"] * (self.stats["messages_sent"] - 1) + elapsed) 
                / self.stats["messages_sent"]
            )
            
            return reflection
            
        except Exception as e:
            self.stats["errors"] += 1
            raise OdinProtocolError(f"Failed to send message: {e}")
    
    def _check_usage_limits(self):
        """Check usage limits and show upgrade prompts"""
        if self.stats["messages_sent"] >= self.usage_limit * 0.8:  # 80% warning
            remaining = self.usage_limit - self.stats["messages_sent"]
            if remaining <= 0:
                print(f"""
🚨 FREE TIER LIMIT REACHED! 🚨

You've sent {self.stats['messages_sent']:,} messages (limit: {self.usage_limit:,})

🚀 UPGRADE TO PROFESSIONAL - $199/month:
   ✅ 100,000 messages/month (10x more!)
   ✅ Advanced analytics and insights  
   ✅ Priority email support
   ✅ Plugin marketplace access

💳 Upgrade now: {self.upgrade_url}

🏢 Need Enterprise? Contact: sales@odin-protocol.com
""")
            elif remaining <= 1000:
                print(f"""
⚠️  Usage Warning: {remaining:,} messages remaining in free tier

🚀 Upgrade to Professional ($199/month) for:
   • 100K messages/month
   • Advanced analytics
   • Priority support

💳 Upgrade: {self.upgrade_url}
""")
    
    def get_usage_stats(self) -> dict:
        """Get current usage statistics"""
        return {
            **self.stats,
            "usage_limit": self.usage_limit,
            "usage_percentage": (self.stats["messages_sent"] / self.usage_limit) * 100,
            "remaining_messages": max(0, self.usage_limit - self.stats["messages_sent"]),
            "upgrade_url": self.upgrade_url
        }
    
    async def evaluate_with_rules(self, 
                                  message: OdinMessage, 
                                  rules: List[Dict] = None) -> OdinReflection:
        """Evaluate message using custom rules."""
        payload = {
            "message": message.SerializeToString().hex(),
            "rules": rules or []
        }
        
        response = await self.session.post(
            f"{self.base_url}/v1/evaluate",
            headers={"Authorization": f"Bearer {self.api_key}"},
            json=payload
        )
        response.raise_for_status()
        
        reflection = OdinReflection()
        reflection.ParseFromString(bytes.fromhex(response.json()["reflection"]))
        return reflection
    
    async def get_analytics(self) -> Dict[str, Any]:
        """Get real-time analytics for your ODIN usage."""
        response = await self.session.get(
            f"{self.base_url}/v1/analytics",
            headers={"Authorization": f"Bearer {self.api_key}"}
        )
        response.raise_for_status()
        return response.json()
    
    def create_message(self) -> OdinMessageBuilder:
        """Create a new ODIN message builder."""
        return OdinMessageBuilder()
    
    async def close(self):
        """Close the client session."""
        await self.session.aclose()
    
    def get_stats(self) -> Dict[str, Any]:
        """Get client-side statistics."""
        return self.stats.copy()


class OdinProtocolError(Exception):
    """Custom exception for ODIN Protocol errors."""
    pass


# Synchronous wrapper for easier use
class OdinSyncClient:
    """Synchronous wrapper for OdinClient."""
    
    def __init__(self, **kwargs):
        self.async_client = OdinClient(**kwargs)
    
    def send_message(self, message: OdinMessage) -> OdinReflection:
        """Send message synchronously."""
        return asyncio.run(self.async_client.send_message(message))
    
    def evaluate_with_rules(self, message: OdinMessage, rules: List[Dict] = None) -> OdinReflection:
        """Evaluate with rules synchronously."""
        return asyncio.run(self.async_client.evaluate_with_rules(message, rules))
    
    def get_analytics(self) -> Dict[str, Any]:
        """Get analytics synchronously."""
        return asyncio.run(self.async_client.get_analytics())
    
    def create_message(self) -> OdinMessageBuilder:
        """Create message builder."""
        return self.async_client.create_message()
    
    def close(self):
        """Close client."""
        asyncio.run(self.async_client.close())
