from model import FormProcessor
from ticket_master import request_ticket_master





if __name__ == "__main__":
    processor = FormProcessor()
    print("Générateur de paramètres URL initialisé! (Tapez 'quit' pour quitter)")
    print("\nExemples de requêtes:")
    print("- 'Je cherche des concerts à Lyon'")
    print("- 'Événements sportifs à Marseille'")
    print("- 'Spectacles de théâtre à Paris'")

    while True:
        query = input("\nQuelle est votre recherche ? ")
        if query.lower() == 'quit':
            break

        print("\nGénération des paramètres...")
        response = processor.process_form(query)
        print("\nParamètres générés:")
        print(response)
        print("\n" + "=" * 50)

    #response
    params = {
        "city": "Paris",
        "countryCode": "FR",
        "locale": "*",
        "classificationName": "music",
        "page": 0
    }

    request_ticket_master(params)