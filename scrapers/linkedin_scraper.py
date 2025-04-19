# scrapers/linkedin_scraper.py

import asyncio
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
from .base import JobScraper

class LinkedInScraper(JobScraper):
    def scrape(self, keywords, country, pages=1):
        cache_key = self._make_cache_key("linkedin", keywords, country, pages)
        cached = self.get_cached(cache_key)
        if cached:
            return cached

        results = asyncio.run(self._scrape_async(keywords, country, pages))
        self.set_cache(cache_key, results)
        return results

    async def _scrape_async(self, keywords, country, pages):
        results = []
        url_base = (
            f"https://www.linkedin.com/jobs/search?keywords={keywords.replace(' ', '%20')}"
            f"&location={country.replace(' ', '%20')}"
        )

        proxy = self._get_next_proxy()
        proxy_config = {"server": proxy["http"]} if proxy else None

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(proxy=proxy_config)
            page = await context.new_page()

            for i in range(pages):
                self._throttle()
                start = i * 25
                await page.goto(url_base + f"&start={start}", timeout=60000)
                await page.wait_for_timeout(3000)
                content = await page.content()
                soup = BeautifulSoup(content, "html.parser")
                for card in soup.select("ul.jobs-search__results-list li"):
                    title_el = card.select_one("h3")
                    company_el = card.select_one("h4")
                    location_el = card.select_one("div.job-search-card__location")
                    link_el = card.select_one("a")
                    if title_el and company_el and location_el and link_el:
                        results.append({
                            "portal": "LinkedIn",
                            "title": title_el.get_text(strip=True),
                            "employer": company_el.get_text(strip=True),
                            "location": location_el.get_text(strip=True),
                            "url": link_el["href"],
                            "contract": None
                        })

            await context.close()
            await browser.close()
        return results
