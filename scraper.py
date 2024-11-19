import pathlib

from bs4 import BeautifulSoup
import requests
'''from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options'''
import time
import asyncio
from playwright.async_api import async_playwright


SCRIPT_DIR = pathlib.Path(__file__).parent.absolute()
EVENTBRITE_URL = 'https://www.eventbrite.com/d'


class EventbriteScraper:
    def get_events_links(self, state, city, category):
        """
        Récupère les liens des événements à partir de la page principale.
        """
        page = requests.get(f'{EVENTBRITE_URL}/{state}--{city}/{category}')
        soup = BeautifulSoup(page.content, 'html.parser')

        event_elems = soup.find_all(class_='event-card-details')
        events_links = []

        for event_elem in event_elems:
            # Récupérer le lien de l'événement
            link_tag = event_elem.find('a', class_='event-card-link')
            if link_tag:
                link = link_tag['href']
                events_links.append(link)

        return events_links

    async def get_events_infos(self, url):
        """
        Récupère les détails d'un événement spécifique en utilisant Playwright.
        """
        async with async_playwright() as p:
            # Lancer le navigateur en mode headless
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context()
            page = await context.new_page()

            # Naviguer vers l'URL
            await page.goto(url)

            # Attendre que la page se charge complètement
            await page.wait_for_timeout(5000)  # Peut être remplacé par un wait_for_selector si besoin

            # Récupérer les détails des événements
            event_details = await page.locator('.Layout-module__layout___1vM08').all_text_contents()

            # Fermer le navigateur
            await browser.close()

            return event_details




