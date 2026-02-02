import argparse
import asyncio
import os
import sys

from jdcrawler.db.client import DatabaseClient
from jdcrawler.services.crawler import CrawlerService


async def main():
    parser = argparse.ArgumentParser(description="JDCrawler CLI")
    parser.add_argument("site", nargs="?", choices=["saramin", "jobkorea", "wanted"], help="Site to crawl (optional)")
    parser.add_argument("--keyword", "-k", help="Search keyword")
    parser.add_argument("--all-keywords", "-a", action="store_true", help="Crawl all active keywords from DB")
    parser.add_argument("--no-headless", action="store_true", help="Run browser in visible mode")
    
    args = parser.parse_args()
    
    # Initialize DB
    os.makedirs("data", exist_ok=True)
    db = DatabaseClient()
    db.create_tables()
    
    service = CrawlerService(db)
    
    headless = not args.no_headless
    
    try:
        if args.all_keywords:
            print("Crawling all active keywords from DB...")
            await service.crawl_all_active_keywords(headless=headless)
        elif args.keyword:
            sites = [args.site] if args.site else None
            await service.crawl_keyword(args.keyword, sites=sites, headless=headless)
        else:
            print("Error: Provide --keyword or --all-keywords")
            parser.print_help()
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(main())
