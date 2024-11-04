from typing import List, Dict, Optional
from datetime import datetime

class PodcastMemory:
    def __init__(self):
        self.episode_lists: Dict[str, List[Dict]] = {}
        self.last_updated: Dict[str, str] = {}
        
    def store_episodes(self, podcast_name: str, episodes: List[Dict]):
        """Store episodes for a specific podcast."""
        self.episode_lists[podcast_name] = episodes
        self.last_updated[podcast_name] = datetime.now().isoformat()
        
    def get_episodes(self, podcast_name: str) -> Optional[List[Dict]]:
        """Retrieve episodes for a specific podcast."""
        return self.episode_lists.get(podcast_name)
    
    def get_episode_by_title(self, podcast_name: str, title: str) -> Optional[Dict]:
        """Find a specific episode by title."""
        episodes = self.get_episodes(podcast_name)
        if not episodes:
            return None
        
        # Case-insensitive partial match
        title = title.lower()
        for episode in episodes:
            if title in episode.get('title', '').lower():
                return episode
        return None
    
    def search_episodes(self, query: str) -> List[Dict]:
        """Search across all stored episodes."""
        results = []
        query = query.lower()
        
        for podcast_name, episodes in self.episode_lists.items():
            for episode in episodes:
                # Search in title, subtitle, and discussed topics
                searchable_text = ' '.join([
                    str(episode.get('title', '')),
                    str(episode.get('subtitle', '')),
                    str(episode.get('Discussed Topics', ''))
                ]).lower()
                
                if query in searchable_text:
                    results.append({
                        'podcast_name': podcast_name,
                        **episode
                    })
        
        return results
    
    def get_all_podcasts(self) -> List[str]:
        """Get list of all stored podcast names."""
        return list(self.episode_lists.keys())
    
    def clear_podcast(self, podcast_name: str):
        """Clear stored episodes for a specific podcast."""
        self.episode_lists.pop(podcast_name, None)
        self.last_updated.pop(podcast_name, None)
    
    def clear_all(self):
        """Clear all stored episodes."""
        self.episode_lists.clear()
        self.last_updated.clear()

# Create a global instance
podcast_memory = PodcastMemory()
