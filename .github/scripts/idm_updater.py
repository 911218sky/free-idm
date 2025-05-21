import requests
from bs4 import BeautifulSoup
import re
import os
import sys
from typing import Tuple, Optional

def get_current_version() -> str:
    """Read current version from file or return default"""
    try:
        with open('current_version.txt', 'r') as f:
            return f.read().strip()
    except:
        return "0.0.0"

def check_latest_version() -> Tuple[str, str, str, Optional[str]]:
    """Fetch and parse the latest version from IDM website"""
    url = "https://www.internetdownloadmanager.com/news.html"
    try:
        response = requests.get(url)
        response.raise_for_status()
    except Exception as e:
        print(f"Failed to connect to IDM website: {e}")
        sys.exit(1)
        
    # Parse HTML to find latest version
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Pattern to match version information like "6.42 Build 37"
    version_pattern = re.compile(r'What\'s new in version (\d+\.\d+) Build (\d+)')
    
    try:
        # Find the latest version info (first occurrence is the latest)
        version_headers = soup.find_all('h3')
        for header in version_headers:
            match = version_pattern.search(header.text)
            if match:
                version = match.group(1)
                build = match.group(2)
                latest_version = f"{version}.{build}"
                
                # Check release date to confirm this is the latest version
                release_info = header.find_next('p')
                release_date = None
                if release_info and 'Released' in release_info.text:
                    release_date = release_info.text
                
                return latest_version, version, build, release_date
                
        if not match:
            raise ValueError("Could not find version information")
    except Exception as e:
        print(f"Error processing version information: {e}")
        sys.exit(1)

def handle_version_update(
    current_version: str, 
    latest_version: str, 
    version: str, 
    build: str, 
    release_date: Optional[str]
  ) -> Tuple[bool, Optional[str], Optional[str]]:
    """Handle actions when checking for version updates"""
    print(f"Current version: {current_version}")
    print(f"Latest version: {latest_version}")
    
    if release_date:
        print(f"Release date: {release_date}")
    
    # Compare versions
    if latest_version > current_version:
        print("New version found!")
        
        # Build download URL
        # Format version number for IDM download filename (e.g., 6.42 Build 37 -> idman642build37.exe)
        version_no_dot = version.replace('.', '')
        download_filename = f"idman{version_no_dot}build{build}.exe"
        download_url = f"https://mirror2.internetdownloadmanager.com/{download_filename}"
        print(f"Download URL: {download_url}")
        
        # Output results for GitHub Actions
        with open(os.environ.get('GITHUB_OUTPUT', 'output.txt'), 'a') as f:
            f.write(f"new_version=true\n")
            f.write(f"version={latest_version}\n")
            f.write(f"download_url={download_url}\n")
        
        # Save the new version number
        with open('current_version.txt', 'w') as f:
            f.write(latest_version)
            
        return True, latest_version, download_url
    else:
        print("No new version available")
        with open(os.environ.get('GITHUB_OUTPUT', 'output.txt'), 'a') as f:
            f.write("new_version=false\n")
        return False, None, None

def check_idm_update():
    """Main function to check for IDM updates"""
    # Get current version
    current_version = get_current_version()
    
    # Get latest version information
    latest_version, version, build, release_date = check_latest_version()
    
    # Handle version update check
    return handle_version_update(current_version, latest_version, version, build, release_date)

if __name__ == "__main__":
    check_idm_update()