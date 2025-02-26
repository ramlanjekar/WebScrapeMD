import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from typing import List, Dict

def extract_doc_links(url: str) -> List[Dict[str, str]]:
    """
    Extract unique navigation links from the main page of a documentation website.
    
    Args:
        url (str): The URL of the documentation main page
        
    Returns:
        List of dictionaries containing unique links with their text
    """
    try:
        # Fetch the main page
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Store unique links
        unique_links = {}  # Using dict to maintain uniqueness
        
        # Find all <a> tags
        for a_tag in soup.find_all('a', href=True):
            href = a_tag.get('href')
            text = a_tag.get_text(strip=True)
            
            # Skip empty links or links without text
            if not href or not text:
                continue
                
            # Convert relative URLs to absolute
            if not href.startswith(('http://', 'https://')):
                href = urljoin(url, href)
            
            # Store in dictionary with URL as key to ensure uniqueness
            unique_links[href] = {
                'url': href,
                'text': text
            }
        
        result=list(unique_links.values())

        # Convert the dictionary values to a list of URLs only
        return [link['url'] for link in result]

    except requests.RequestException as e:
        print(f"Error fetching the page: {str(e)}")
        return []

# Example usage
if __name__ == "__main__":
    # Example with a documentation website
    doc_url = "https://docs.dask.org/en/stable/"
    links = extract_doc_links(doc_url)
    print(type(links))
    
    # # Print results in a readable format
    # print(f"\nFound Links:,{len(links)}")
    # for link in links:
    #     # print(f"• {link['text']}")
    #     print(f"{link}\n")