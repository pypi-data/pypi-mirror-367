import requests
import datetime

class Issue:
    def __init__(self, client, issue_id):
        """
        Initialize Issue object.
        
        Args:
            client: YouTrackClient instance
            issue_id: ID of the issue (e.g., 'AI-123')
        """
        self.client = client
        self.id = issue_id
    
    def get_work_items(self, limit=None, skip=None):
        """Get work items for the issue."""
        url = f"{self.client.base_url}/api/issues/{self.id}/timeTracking/workItems"
        params = {
            'fields': 'id,author(name),date,text,duration(minutes)',
            '$top': limit,
            '$skip': skip
        }

        response = requests.get(url, headers=self.client.headers, params=params)
        response.raise_for_status()

        return response.json()

    def add_work_item(self, duration, date=None, description=None):
        """Add work item to the issue."""
        if date is None:
            date = datetime.datetime.now().timestamp() * 1000 
        elif isinstance(date, str):
            date = datetime.datetime.strptime(date, "%d/%m/%Y").timestamp() * 1000            
            
        url = f"{self.client.base_url}/api/issues/{self.id}/timeTracking/workItems"

        data = {
            "duration": {
                "minutes": self._parse_duration(duration)
            },
            "date": date,
            "text": description
        }
        
        response = requests.post(url, headers=self.client.headers, json=data)
        response.raise_for_status()
        
        return response.json()
    
    def _parse_duration(self, duration):
        """Convert duration string or minutes to minutes."""
        if isinstance(duration, int):
            return duration
            
        total_minutes = 0
        
        if "h" in duration:
            hours_part = duration.split("h")[0].strip()
            total_minutes += int(hours_part) * 60
            duration = duration.split("h")[1]
            
        if "m" in duration:
            minutes_part = duration.split("m")[0].strip()
            if minutes_part:
                total_minutes += int(minutes_part)
                
        return total_minutes