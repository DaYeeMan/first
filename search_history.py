import re
from pathlib import Path
import requests
from bs4 import BeautifulSoup
import time
import json

def get_video_metadata(url):
    """
    Get metadata (title, description, tags) from a TikTok video URL.
    
    Args:
        url (str): TikTok video URL
    
    Returns:
        dict: Video metadata including title, description, and tags
    """
    try:
        # Add headers to mimic a browser request
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            print(f"Failed to fetch video: {url}")
            return None
            
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extract metadata from the page
        # Note: TikTok's structure might change, so this is a basic implementation
        title = soup.find('title').text if soup.find('title') else ''
        description = soup.find('meta', {'name': 'description'})
        description = description['content'] if description else ''
        
        # Try to find hashtags in the description
        tags = re.findall(r'#(\w+)', description)
        
        return {
            'title': title,
            'description': description,
            'tags': tags,
            'url': url
        }
    except Exception as e:
        print(f"Error processing video {url}: {e}")
        return None

def read_video_entry(file):
    """
    Read a complete video entry (date and link) from the file.
    
    Args:
        file: File object
    
    Returns:
        tuple: (date, url) or (None, None) if end of file
    """
    try:
        # Read date line
        date_line = file.readline().strip()
        if not date_line:  # End of file
            return None, None
            
        # Read link line
        link_line = file.readline().strip()
        if not link_line:  # End of file
            return None, None
            
        # Skip empty line
        file.readline()
        
        # Extract date and URL
        date_match = re.search(r'Date: (.*? UTC)', date_line)
        link_match = re.search(r'Link: (https://.*?)(?:\s|$)', link_line)
        
        if date_match and link_match:
            return date_match.group(1), link_match.group(1)
        return None, None
        
    except Exception as e:
        print(f"Error reading video entry: {e}")
        return None, None

def search_videos(keywords, file_path):
    """
    Search through the watch history file for videos matching any of the given keywords.
    
    Args:
        keywords (list): List of keywords to search for
        file_path (str): Path to the Watch History.txt file
    
    Returns:
        list: List of matching video metadata
    """
    matches = []
    # Convert keywords to lowercase for case-insensitive search
    keywords = [k.lower() for k in keywords]
    
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            print("\nReading first few entries to check format:")
            for i in range(5):  # Process first 5 entries for debugging
                date, url = read_video_entry(file)
                if not url:
                    break
                    
                print(f"\nProcessing video {i+1}:")
                print(f"Date: {date}")
                print(f"URL: {url}")
                
                # Get video metadata
                metadata = get_video_metadata(url)
                if not metadata:
                    continue
                
                # Add the date to the metadata
                metadata['date'] = date
                
                # Check if any keyword matches the title, description, or tags
                text_to_search = f"{metadata['title']} {metadata['description']} {' '.join(metadata['tags'])}".lower()
                if any(keyword in text_to_search for keyword in keywords):
                    matches.append(metadata)
                    print("Found a match!")
                
                # Add a delay to avoid rate limiting
                time.sleep(1)
                    
    except Exception as e:
        print(f"Error reading file: {e}")
        return []
    
    return matches

def main():
    # Path to the Watch History file
    file_path = Path("first/Watch History.txt")
    
    # Keywords to search for
    keywords = [
        "orv",
        "omniscient readers viewpoint",
        "orv animation",
        "orv fan animation"
    ]
    
    print("Starting search... This might take a while as we need to check each video.")
    print("Press Ctrl+C to stop the search at any time.")
    
    # Search for videos
    matches = search_videos(keywords, file_path)
    
    # Print results
    if matches:
        print(f"\nFound {len(matches)} matching videos:")
        for i, match in enumerate(matches, 1):
            print(f"\n{i}. Date: {match['date']}")
            print(f"   URL: {match['url']}")
            print(f"   Title: {match['title']}")
            print(f"   Tags: {', '.join(match['tags'])}")
    else:
        print("No matching videos found.")

if __name__ == "__main__":
    main() 