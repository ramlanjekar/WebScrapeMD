import os
import sys
import psutil
import asyncio
import requests
import time  # Add time import
from xml.etree import ElementTree
from anchorl_url_generator import extract_doc_links

__location__ = os.path.dirname(os.path.abspath(__file__))
__output__ = os.path.join(__location__, "output")

# Append parent directory to system path
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

from typing import List
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode

async def crawl_parallel(urls: List[str], max_concurrent: int = 3):
    start_time = time.perf_counter()  # Start timing
    print("\n=== Parallel Crawling with Browser Reuse + Memory Check ===")

    # We'll keep track of peak memory usage across all tasks
    peak_memory = 0
    process = psutil.Process(os.getpid())

    # Prepare a single markdown file for all content
    os.makedirs(__output__, exist_ok=True)
    output_file = os.path.join(__output__, "combined_documentation_base_3.md")
    
    # Initialize the file with a title
    with open(output_file, "w", encoding="utf-8") as f:
        f.write("# Combined Documentation\n\n")
        f.write("*Generated automatically from web crawling*\n\n")
        f.write("## Table of Contents\n\n")

    def log_memory(prefix: str = ""):
        nonlocal peak_memory
        current_mem = process.memory_info().rss  # in bytes
        if current_mem > peak_memory:
            peak_memory = current_mem
        print(f"{prefix} Current Memory: {current_mem // (1024 * 1024)} MB, Peak: {peak_memory // (1024 * 1024)} MB")

    # Define browser configuration
    browser_config = BrowserConfig(
    headless=True,
    verbose=True,   
    extra_args=["--disable-gpu", "--disable-dev-shm-usage", "--no-sandbox"],
      # Remove overlay elements
    )

    # Define crawl configuration without the extraction_config parameter
    # Define crawl configuration with proper settings for navigation menus and code blocks
    crawl_config = CrawlerRunConfig(
        cache_mode=CacheMode.BYPASS,
        # Remove navigation and sidebar elements but preserve code blocks
        excluded_selector="nav, .sidebar, .navigation, .side-nav, .menu, aside",
        excluded_tags=["footer", "header"],
        keep_data_attributes=True,  # Important for preserving code block formatting
    )

    # Create the crawler instance
    crawler = AsyncWebCrawler(config=browser_config)
    await crawler.start()

    try:
        # We'll chunk the URLs in batches of 'max_concurrent'
        success_count = 0
        fail_count = 0
        
        # Dictionary to store all successful crawl results for TOC generation
        successful_pages = []
        
        for i in range(0, len(urls), max_concurrent):
            batch = urls[i : i + max_concurrent]
            tasks = []

            for j, url in enumerate(batch):
                # Unique session_id per concurrent sub-task
                session_id = f"parallel_session_{i + j}"
                task = crawler.arun(url=url, config=crawl_config, session_id=session_id)
                tasks.append(task)

            # Check memory usage prior to launching tasks
            log_memory(prefix=f"Before batch {i//max_concurrent + 1}: ")

            # Gather results
            results = await asyncio.gather(*tasks, return_exceptions=True)

            # Check memory usage after tasks complete
            log_memory(prefix=f"After batch {i//max_concurrent + 1}: ")

            # Evaluate results
            for url, result in zip(batch, results):
                if isinstance(result, Exception):
                    print(f"Error crawling {url}: {result}")
                    fail_count += 1
                elif result.success:
                    success_count += 1
                    
                    try:
                        # Extract title from result
                        title = "Untitled Page"
                        
                        # Try different ways to get the title
                        if hasattr(result, 'metadata') and result.metadata and result.metadata.get('title'):
                            title = result.metadata.get('title')
                        elif hasattr(result, 'html') and result.html:
                            # Basic title extraction from HTML
                            title_start = result.html.find("<title>")
                            title_end = result.html.find("</title>")
                            if title_start != -1 and title_end != -1:
                                title = result.html[title_start + 7:title_end].strip()
                        
                        # Clean the title for use as an anchor
                        anchor = title.lower().replace(" ", "-").replace(".", "").replace(",", "")
                        anchor = ''.join(c for c in anchor if c.isalnum() or c == '-')
                        
                        # Add to successful pages for TOC
                        successful_pages.append({
                            "url": url,
                            "title": title, 
                            "anchor": anchor
                        })
                        
                        # Write the content to the combined file
                        with open(output_file, "a", encoding="utf-8") as f:
                            f.write(f"\n## {title}\n")
                            f.write(f"*Source: [{url}]({url})*\n\n")
                            
                            # Try different ways to get content in markdown format
                            content = "*No content extracted*"
                            
                            # First try fit_markdown (most relevant content)
                            if hasattr(result, 'fit_markdown') and result.fit_markdown:
                                content = result.fit_markdown
                            # Then try regular markdown
                            elif hasattr(result, 'markdown') and result.markdown:
                                content = result.markdown
                            # Then try cleaned_html wrapped in code block
                            elif hasattr(result, 'cleaned_html') and result.cleaned_html:
                                content = f"```html\n{result.cleaned_html}\n```"
                            # Last resort: use raw html
                            elif hasattr(result, 'html') and result.html:
                                content = f"```html\n{result.html}\n```"
                                
                            f.write(content)
                            f.write("\n\n---\n\n")  # Page separator
                    
                    except Exception as e:
                        print(f"Error processing content from {url}: {e}")
                else:
                    fail_count += 1
                    print(f"Failed to crawl {url}, status code: {result.status_code if hasattr(result, 'status_code') else 'unknown'}")

        # After all content is written, go back and update the TOC at the beginning
        if successful_pages:
            with open(output_file, "r", encoding="utf-8") as f:
                content = f.read()
                
            toc_content = "## Table of Contents\n\n"
            for page in successful_pages:
                toc_content += f"- [{page['title']}](#{page['anchor']})\n"
            toc_content += "\n---\n\n"
            
            # Replace placeholder TOC with actual TOC
            content = content.replace("## Table of Contents\n\n", toc_content)
            
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(content)
            
            print(f"\nCombined documentation saved to: {output_file}")

        print(f"\nSummary:")
        print(f"  - Successfully crawled: {success_count}")
        print(f"  - Failed: {fail_count}")

    finally:
        print("\nClosing crawler...")
        await crawler.close()
        # Final memory log
        log_memory(prefix="Final: ")
        
        # Calculate and print timing information
        end_time = time.perf_counter()
        total_time = end_time - start_time
        print(f"\nTotal execution time: {total_time:.2f} seconds ({total_time/60:.2f} minutes)")
        print(f"Peak memory usage (MB): {peak_memory // (1024 * 1024)}")

async def main():
    total_start = time.perf_counter()  # Start timing for everything
    doc_url = input("Enter the URL of the documentation main page: ")
    doc_url=extract_doc_links(doc_url)
    urls = doc_url
    if urls:
        print(f"Found {len(urls)} URLs to crawl")
        await crawl_parallel(urls, max_concurrent=10)  
        
        # Print total time including setup
        total_time = time.perf_counter() - total_start
        print(f"\nTotal process time (including setup): {total_time:.2f} seconds ({total_time/60:.2f} minutes)")
    else:
        print("No URLs found to crawl")    

if __name__ == "__main__":
    asyncio.run(main())