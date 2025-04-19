# scrapers/glassdoor_scraper.py

import asyncio
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
from .base import JobScraper

class GlassdoorScraper(JobScraper):
    def scrape(self, keywords, country, pages=1):
        cache_key = self._make_cache_key("glassdoor", keywords, country, pages)
        cached = self.get_cached(cache_key)
        if cached:
            return cached

        results = asyncio.run(self._scrape_async(keywords, country, pages))
        self.set_cache(cache_key, results)
        return results

    async def _scrape_async(self, keywords, country, pages):
        results = []
        search_term = keywords.replace(" ", "-")
        url_base = f"https://www.glassdoor.com/Job/{country.lower()}-{search_term}-jobs-SRCH_IL.0,2_IN0_KO0,25.htm"
        proxy = self._get_next_proxy()
        proxy_config = {"server": proxy["http"]} if proxy else None

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(proxy=proxy_config)
            page = await context.new_page()

            for i in range(pages):
                self._throttle()
                page_suffix = f"_IP{i+1}.htm" if i > 0 else ""
                await page.goto(url_base.replace(".htm", page_suffix), timeout=60000)
                await page.wait_for_timeout(3000)
                content = await page.content()
                soup = BeautifulSoup(content, "html.parser")

                for card in soup.select("li.react-job-listing"):
                    title_el = card.select_one("a.jobLink")
                    company_el = card.select_one("div.jobHeader")
                    location_el = card.select_one("span.pr-xxsm")
                    if title_el and company_el and location_el:
                        results.append({
                            "portal": "Glassdoor",
                            "title": title_el.get_text(strip=True),
                            "employer": company_el.get_text(strip=True),
                            "location": location_el.get_text(strip=True),
                            "contract": None,
                            "url": "https://www.glassdoor.com" + title_el.get("href")
                        })

            await context.close()
            await browser.close()
        return results
