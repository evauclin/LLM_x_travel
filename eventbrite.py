from typing import List, Any

import requests
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright


class EventbriteScraper:
    def __init__(self):
        self.base_url = 'https://www.eventbrite.com/d'

    def get_events_links(self, state: str, city: str, category: str) -> List[str]:
        """
        Récupère les liens des événements à partir de la page principale.
        """
        url = f'{self.base_url}/{state}--{city}/{category}'
        try:
            page = requests.get(url)
            soup = BeautifulSoup(page.content, 'html.parser')

            event_elems = soup.find_all(class_='event-card-details')
            events_links = []

            for event_elem in event_elems:
                link_tag = event_elem.find('a', class_='event-card-link')
                if link_tag and 'href' in link_tag.attrs:
                    events_links.append(link_tag['href'])

            return events_links
        except Exception as e:
            print(f"Erreur lors de la récupération des liens Eventbrite: {e}")
            return []

    async def get_events_infos(self, url: str) -> list[str] | dict[Any, Any]:
        """
        Récupère les détails d'un événement spécifique.
        """
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context()
            page = await context.new_page()

            try:
                await page.goto(url)
                await page.wait_for_timeout(2000)
                event_details = await page.locator('.event-details').all_text_contents()
                await browser.close()
                return event_details
            except Exception as e:
                print(f"Erreur lors de la récupération des détails de l'événement: {e}")
                await browser.close()
                return {}

