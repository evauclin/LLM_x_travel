from langchain_community.llms import HuggingFacePipeline
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
from huggingface_hub import login
import torch


class FormProcessor:
    def __init__(self):
        self.llm = self.initialize_model()

    def initialize_model(self):
        # Configuration du modèle
        token = "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"
        model_name_or_path = "meta-llama/Llama-3.2-3B-Instruct"

        login(token=token)
        tokenizer = AutoTokenizer.from_pretrained(
            model_name_or_path,
            token=token,
            use_fast=True
        )
        model = AutoModelForCausalLM.from_pretrained(
            model_name_or_path,
            token=token,
            device_map="auto",
            trust_remote_code=True,
            torch_dtype=torch.float16
        )

        pipe = pipeline(
            "text-generation",
            model=model,
            tokenizer=tokenizer,
            max_length=256,  # Réduit car nous avons besoin d'une réponse plus courte
            temperature=0.05  # Réduit pour des réponses plus précises
        )
        return HuggingFacePipeline(pipeline=pipe)

    def process_form(self, user_query):
        prompt = f"""Analyse cette requête utilisateur: "{user_query}"
        et génère uniquement les paramètres de l'URL Ticketmaster correspondants.

        Format de sortie requis:
        

        Ne génère que les paramètres, sans autre texte.
        """

        try:
            with torch.inference_mode():
                response = self.llm(prompt)
            return response
        except Exception as e:
            return f"Erreur lors du traitement: {e}"


def main():
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


if __name__ == "__main__":
    main()