import feedparser
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timezone
import asyncio
import aiohttp
from typing import List, Dict
import re

class NewsAggregator:
    def __init__(self):
        self.sources = {
            "BBC": "http://feeds.bbci.co.uk/news/rss.xml",
            "CNN": "http://rss.cnn.com/rss/edition.rss",
            "Reuters": "https://feeds.reuters.com/reuters/topNews",
            "TechCrunch": "https://techcrunch.com/feed/",
            "The Guardian": "https://www.theguardian.com/international/rss",
            "Al Jazeera": "https://www.aljazeera.com/xml/rss/all.xml",
            "NPR": "https://feeds.npr.org/1001/rss.xml"
        }
    
    async def fetch_all_sources(self) -> List[Dict]:
        """Fetch articles from all news sources"""
        all_articles = []
        
        for source_name, feed_url in self.sources.items():
            try:
                print(f"📰 Fetching from {source_name}...")
                articles = await self.fetch_from_source(source_name, feed_url)
                all_articles.extend(articles)
                
                # Small delay between sources
                await asyncio.sleep(1)
                
            except Exception as e:
                print(f"❌ Error fetching from {source_name}: {e}")
                continue
        
        print(f"✅ Total articles fetched: {len(all_articles)}")
        return all_articles
    
    async def fetch_from_source(self, source_name: str, feed_url: str) -> List[Dict]:
        """Fetch articles from a single RSS source"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(feed_url, timeout=30) as response:
                    if response.status == 200:
                        content = await response.text()
                        return self.parse_rss_feed(content, source_name)
                    else:
                        print(f"HTTP {response.status} for {source_name}")
                        return []
        except Exception as e:
            print(f"Error fetching {source_name}: {e}")
            return []
    
    def parse_rss_feed(self, rss_content: str, source_name: str) -> List[Dict]:
        """Parse RSS feed content and extract articles"""
        try:
            feed = feedparser.parse(rss_content)
            articles = []
            
            for entry in feed.entries[:10]:  # Limit to 10 articles per source
                try:
                    # Extract article content
                    content = self.extract_content(entry)
                    
                    # Parse published date
                    pub_date = self.parse_date(entry)
                    
                    # Create article object
                    article = {
                        "title": entry.title,
                        "content": content,
                        "url": entry.link,
                        "source": source_name,
                        "published_date": pub_date,
                        "author": getattr(entry, 'author', None),
                        "category": self.extract_category(entry),
                        "tags": self.extract_tags(entry),
                        "image_url": self.extract_image(entry)
                    }
                    
                    # Only add if we have substantial content
                    if len(content) > 100:
                        articles.append(article)
                        
                except Exception as e:
                    print(f"Error parsing entry from {source_name}: {e}")
                    continue
            
            return articles
            
        except Exception as e:
            print(f"Error parsing RSS from {source_name}: {e}")
            return []
    
    def extract_content(self, entry) -> str:
        """Extract main content from RSS entry"""
        content = ""
        
        # Try different content fields
        if hasattr(entry, 'content') and entry.content:
            content = entry.content[0].value
        elif hasattr(entry, 'summary') and entry.summary:
            content = entry.summary
        elif hasattr(entry, 'description') and entry.description:
            content = entry.description
        
        # Clean HTML tags
        if content:
            soup = BeautifulSoup(content, 'html.parser')
            content = soup.get_text().strip()
            
            # Remove extra whitespace
            content = re.sub(r'\s+', ' ', content)
        
        return content or "Content not available"
    
    def parse_date(self, entry) -> datetime:
        """Parse publication date from entry"""
        try:
            if hasattr(entry, 'published_parsed') and entry.published_parsed:
                return datetime(*entry.published_parsed[:6], tzinfo=timezone.utc)
            elif hasattr(entry, 'updated_parsed') and entry.updated_parsed:
                return datetime(*entry.updated_parsed[:6], tzinfo=timezone.utc)
            else:
                return datetime.now(timezone.utc)
        except:
            return datetime.now(timezone.utc)
    
    def extract_category(self, entry) -> str:
        """Extract category from entry"""
        if hasattr(entry, 'tags') and entry.tags:
            return entry.tags[0].term
        elif hasattr(entry, 'category'):
            return entry.category
        return "General"
    
    def extract_tags(self, entry) -> List[str]:
        """Extract tags from entry"""
        tags = []
        if hasattr(entry, 'tags'):
            tags = [tag.term for tag in entry.tags[:5]]  # Limit to 5 tags
        return tags
    
    def extract_image(self, entry) -> str:
        """Extract image URL from entry"""
        # Try to find image in various fields
        if hasattr(entry, 'media_content') and entry.media_content:
            return entry.media_content[0].get('url')
        elif hasattr(entry, 'enclosures') and entry.enclosures:
            for enclosure in entry.enclosures:
                if enclosure.type.startswith('image/'):
                    return enclosure.href
        
        # Try to extract from content
        if hasattr(entry, 'content') and entry.content:
            soup = BeautifulSoup(entry.content[0].value, 'html.parser')
            img = soup.find('img')
            if img and img.get('src'):
                return img['src']
        
        return None