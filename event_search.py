import json

from eventbrite import *
from ollama_client import *

from ticket_master import *


class EventSearch:
    def __init__(self, api_key: str):
        self.ollama_client = OllamaClient()
        self.ticketmaster_client = TicketmasterClient(api_key)
        self.eventbrite_scraper = EventbriteScraper()
        self.system_message = (
            "Tu es un agent de voyage qui génère une liste d'événements "
            "pour aider à planifier un séjour. À partir d'une liste d'événements, "
            "tu dois donner le top 3 des activité et un top 3 des evenements qui correspondent à la demande de l'utilisateur."
        )

    def generate_params(self, user_query: str) -> Optional[Dict]:
        """Generate search parameters from user query"""
        system_message = """
        Analyse cette requête utilisateur pour un événement et retourne uniquement un dictionnaire JSON avec les paramètres suivants :

        {
            "Ticketmaster": {
                "city": "ville mentionnée",
                "countryCode": "code pays (IT pour Italie, FR pour France, ES pour Espagne, etc.)",
                "locale": "*",
                "classificationName": "type d'événement (Music, Sports, Arts, Theatre, etc.)",
                "sort": "date,asc"
            },
            "EventbriteScraper": {
                "state": "état ou région mentionné(e) Exemple: france, italy, spain"
                "city": "ville mentionnée Exemple: paris, rome, madrid"
                "category": "type d'événement ou mot-clé exemple: "theatre" ou "music""
            }
        }

        le format doit absolument être respecté pour que l'agent puisse analyser correctement la requête.
        """

        response = self.ollama_client.chat(
            model="llava:13b",
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": user_query},
            ],
        )

        if not response:
            return None

        content = response["message"]["content"].strip()
        json_start = content.find("{")
        json_end = content.rfind("}") + 1
        return json.loads(content[json_start:json_end])

    async def search_events(self, params: Dict) -> Dict[str, List[Dict]]:
        """Search events from both Ticketmaster and Eventbrite"""
        ticketmaster_events = self.ticketmaster_client.search_events(
            params.get("Ticketmaster", {})
        )

        eventbrite_params = params.get("EventbriteScraper", {})
        eventbrite_events = []
        if all(key in eventbrite_params for key in ["state", "city", "category"]):
            events_links = self.eventbrite_scraper.get_events_links(
                eventbrite_params["state"],
                eventbrite_params["city"],
                eventbrite_params["category"],
            )
            for link in events_links:
                event_info = {
                    "state": eventbrite_params["state"],
                    "city": eventbrite_params["city"],
                    "category": eventbrite_params["category"],
                    "url": link,
                }
                eventbrite_events.append(event_info)

        return {"ticketmaster": ticketmaster_events, "eventbrite": eventbrite_events}

    def save_events(self, events: Dict[str, List[Dict]], filename: str = "output.txt"):
        """Save events to a file"""

        with open(filename, "w", encoding="utf-8") as file:
            # Ticketmaster events
            file.write("=== Événements Ticketmaster ===\n\n")
            if events["ticketmaster"]:
                for event in events["ticketmaster"]:
                    if event:  # Vérifier que l'événement est valide
                        file.write(f"Nom de l'événement: {event['name']}\n")
                        file.write(f"Date: {event['date']}\n")
                        file.write(f"Lieu: {event['venue']}\n")
                        file.write(f"Description: {event['description']}\n")
                        file.write(f"Prix: {event['price']}\n")
                        file.write(f"URL: {event['url']}\n")
                        file.write("-" * 50 + "\n")
                print(
                    f"{len([e for e in events if e])} événements trouvés et enregistrés dans '{filename}'"
                )
            else:
                file.write("Aucun événement trouvé pour ces critères de recherche.\n")
                print("Aucun événement trouvé.")

            # Eventbrite events
            file.write("\n=== Événements Eventbrite ===\n\n")
            if events["eventbrite"]:
                for event in events["eventbrite"]:
                    if event:
                        for key, value in event.items():
                            file.write(f"{key}: {value}\n")
                        file.write("-" * 50 + "\n")
            else:
                file.write("Aucun événement Eventbrite trouvé.\n")

        print(f"Événements enregistrés dans '{filename}'")

    def generate_response(
        self, user_query: str, content: str, user_message_template: str
    ) -> Optional[str]:
        """Generate a response based on events and user query"""
        formatted_message = user_message_template.format(
            content=content, user_query=user_query
        )

        response = self.ollama_client.chat(
            model="llama3.2-vision:latest",
            messages=[
                {"role": "system", "content": self.system_message},
                {"role": "user", "content": formatted_message},
            ],
            stream=True,
        )

        if response:
            return response["message"]["content"]
        return None
