import pathlib

from bs4 import BeautifulSoup
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time


SCRIPT_DIR = pathlib.Path(__file__).parent.absolute()
EVENTBRITE_URL = 'https://www.eventbrite.com/d'


class EventbriteScraper:

    def __init__(self):
        # Configurer les options pour Selenium
        self.chrome_options = Options()
        self.chrome_options.add_argument(
            "--headless")  # Exécuter Chrome en mode headless (sans interface graphique)
        self.chrome_options.add_argument("--no-sandbox")
        self.chrome_options.add_argument("--disable-dev-shm-usage")

        # Démarrer le driver Selenium
        self.driver = webdriver.Chrome(options=self.chrome_options)

    def get_events_links(self, state, city, category):
        page = requests.get(f'{EVENTBRITE_URL}/{state}--{city}/{category}')

        soup = BeautifulSoup(page.content, 'html.parser')



        event_elems = soup.find_all(
                                    class_='event-card-details')

        events_links = []
        for event_elem in event_elems:
            # Récupérer le lien de l'événement
            link_tag = event_elem.find('a', class_='event-card-link')

            if link_tag:
                link = link_tag['href']
                events_links.append(link)



        return events_links


    def get_events_infos(self, URL):
        

        # Ouvrir la page
        self.driver.get(URL)

        # Attendre que la page se charge (ajustez le temps d'attente si nécessaire)
        time.sleep(5)

        # Récupérer les éléments contenant les détails de l'événement
        event_details = self.driver.find_elements(By.CLASS_NAME,
                                             'Layout-module__layout___1vM08')

        # Extraire le texte de chaque élément pour le rendre JSON-serialisable
        event_details_text = [element.text for element in event_details]

        return event_details_text
    
    def quit_driver(self):
        self.driver.quit()




