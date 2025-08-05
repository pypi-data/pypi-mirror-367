from typing import List, Optional, Dict, Any
import requests
from pydantic import BaseModel

class Event(BaseModel):
    name: str
    customer_id: str
    unit_name: str

class SkopeClient:
    def __init__(self, api_key: str, base_url: str = "https://skope-v3.onrender.com"):
        """Initialize the Skope client.
        
        Args:
            api_key: Your Skope API key
            base_url: The base URL of the Skope API (default: https://skope-v3.onrender.com)
        """
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.session.headers.update({
            'x-api-key': api_key,
            'Content-Type': 'application/json'
        })

    def upload_events(self, events: List[Event]) -> Dict[str, Any]:
        """Upload multiple events to Skope in batch.
        
        Args:
            events: List of Event objects to upload
            
        Returns:
            Dict containing the upload response
            
        Raises:
            requests.exceptions.RequestException: If the request fails
        """
        response = self.session.post(
            f"{self.base_url}/api/events",
            json=[event.model_dump() for event in events]
        )
        response.raise_for_status()
        return response.json() 
