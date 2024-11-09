import ollama


class Agent:
    def __init__(self, model_name, system_message, modelfile_template="FROM llama3.1\nSYSTEM SYSTEM_MESSAGE"):
        self.model_name = model_name
        self.system_message = system_message
        self.modelfile = modelfile_template.replace("SYSTEM_MESSAGE", system_message)
        self.create_model()

    def create_model(self):
        try:
            ollama.create(model=self.model_name, modelfile=self.modelfile)
            print(f"Modèle '{self.model_name}' créé avec succès.")
        except Exception as e:
            print(f"Erreur lors de la création du modèle: {e}")

    def generate_response(self, user_query, content, user_message_template):

        user_content = user_message_template.format(content=content, user_query=user_query)

        messages = [
            {'role': 'system', 'content': self.system_message},
            {'role': 'user', 'content': user_content}
        ]

        response = []
        try:
            stream = ollama.chat(model=self.model_name, messages=messages, stream=True)
            for chunk in stream:
                response.append(chunk.get('message', {}).get('content', ''))
        except Exception as e:
            print(f"Erreur lors de la génération de réponse: {e}")

        return ''.join(response)


if __name__ == "__main__":

    with open("output.txt", "r", encoding="utf-8") as file:
        content = file.read()


    agent = Agent(
        model_name="agent2",
        system_message=(
            "Tu es un agent de voyage qui génère une liste d'événements "
            "pour aider à planifier un séjour. À partir d'une liste d'événements, "
            "tu dois donner le top 3 qui correspondent à la demande de l'utilisateur."
        )
    )

    user_query = "Je veux partir à Paris et je veux assister à un concert de musique un peu électro."

    custom_user_message = (
        "Voici les informations récupérées : {content}.\n\n"
        "Voici la demande de l'utilisateur : {user_query}\n\n"
        "Je veux que tu respectes le format suivant pour les événements :\n\n"
        "1. Event: Nom de l'événement\n"
        "   Date: Date de l'événement\n"
        "   Lieu: Lieu de l'événement\n"
        "   Description: Extrait de la description de l'événement\n"
        "   Lien Ticketmaster : Lien vers la billetterie\n"
        "   Prix: Prix de l'événement\n\n"
        "Il est essentiel de proposer le top 3 des événements qui correspondent à la demande "
        "de l'utilisateur, avec des dates différentes pour chaque événement et dans l'intervalle de dates demandé."
        "Propose des événements à des dates différentes sur la base des informations récupérées."
    )

    response = agent.generate_response(user_query, content, custom_user_message)
    print(response)
