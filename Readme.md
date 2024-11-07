# Générateur de Paramètres Ticketmaster

## Description
Ce projet est un générateur intelligent de paramètres d'URL pour l'API Ticketmaster. Il utilise un modèle de langage (LLM) pour analyser des requêtes en langage naturel et générer les paramètres correspondants pour l'API Ticketmaster.

## Prérequis
- Python 3.8+
- PyTorch
- CUDA (recommandé pour de meilleures performances)

## Installation

1. Clonez le dépôt :
```bash
git clone [votre-repo]
cd [votre-repo]
```

2. Installez les dépendances requises :
```bash
pip install langchain-community
pip install transformers
pip install torch
pip install huggingface-hub
```

3. Configurez votre token Hugging Face :
- Créez un compte sur [Hugging Face](https://huggingface.co/)
- Générez un token d'accès
- Remplacez `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` dans le code par votre token

## Utilisation

1. Exécutez le script :
```bash
python form_processor.py
```

2. Entrez votre requête quand demandé. Par exemple :
- "Je cherche des concerts à Lyon"
- "Événements sportifs à Marseille"
- "Spectacles de théâtre à Paris"

3. Le script générera les paramètres d'URL correspondants au format :
```python
params = {
    "city": "ville",
    "countryCode": "code pays",
    "locale": "*",
    "classificationName": "type d'événement",
    "page": numéro de page
}
```

## Configuration du Modèle

Le script utilise :
- Modèle : Llama-3.2-3B-Instruct
- Longueur maximale : 256 tokens
- Température : 0.05 (pour des réponses précises)
- Format float16 pour optimisation mémoire

## Structure du Code

```
form_processor.py
├── class FormProcessor
│   ├── __init__()
│   ├── initialize_model()
│   └── process_form()
└── main()
```

## Paramètres Personnalisables

Dans `initialize_model()` :
- `max_length` : Longueur maximale de la réponse (défaut : 256)
- `temperature` : Créativité du modèle (défaut : 0.05)
- `model_name_or_path` : Choix du modèle

## Optimisations

Le code inclut plusieurs optimisations :
- Utilisation de `torch.float16` pour réduire l'utilisation mémoire
- `device_map="auto"` pour la gestion automatique GPU/CPU
- `use_fast=True` pour le tokenizer rapide
- Mode d'inférence optimisé avec `torch.inference_mode()`

## Dépannage

1. Erreur de mémoire GPU :
   - Réduisez `max_length`
   - Utilisez un modèle plus petit
   - Passez en mode CPU

2. Requêtes lentes :
   - Vérifiez la disponibilité du GPU
   - Réduisez la taille du modèle
   - Ajustez les paramètres de génération

## Contribution

Les contributions sont les bienvenues ! N'hésitez pas à :
1. Fork le projet
2. Créer une branche (`git checkout -b feature/AmazingFeature`)
3. Commit vos changements (`git commit -m 'Add AmazingFeature'`)
4. Push vers la branche (`git push origin feature/AmazingFeature`)
5. Ouvrir une Pull Request

## Licence

Distribué sous la licence MIT. Voir `LICENSE` pour plus d'informations.

