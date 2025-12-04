# Travliaq-Translate

Service de traduction multilingue basé sur le modèle NLLB (No Language Left Behind) de Meta, conçu pour l'intégration avec le serveur MCP Travliaq.

## 📋 Table des Matières

- [Vue d'ensemble](#-vue-densemble)
- [Fonctionnalités](#-fonctionnalités)
- [Architecture Technique](#-architecture-technique)
- [Installation & Configuration](#-installation--configuration)
- [Utilisation](#-utilisation)
- [Intégration MCP](#-intégration-mcp)
- [API Reference](#-api-reference)
- [Langues Supportées](#-langues-supportées)
- [Déploiement](#-déploiement)
- [Troubleshooting](#-troubleshooting)

---

## 🎯 Vue d'ensemble

**Travliaq-Translate** est un microservice de traduction haute performance destiné à traduire les contenus de voyage générés par les agents Travliaq. Il utilise le modèle **NLLB-200** de Meta, optimisé pour 200 langues avec une qualité professionnelle.

### Cas d'usage principal

Traduire automatiquement les itinéraires de voyage (titres, descriptions, activités) dans la langue cible de l'utilisateur tout en préservant le contexte culturel et touristique.

### Pourquoi NLLB ?

- ✅ **200 langues** supportées (vs ~100 pour Google Translate API)
- ✅ **Open-source** et auto-hébergeable (pas de coûts API)
- ✅ **Spécialisé multilingue** : meilleure qualité pour les paires de langues rares
- ✅ **Pas de limite de requêtes** (contrairement aux APIs cloud)
- ✅ **Confidentialité** : données de voyage sensibles non envoyées à des tiers

---

## 🚀 Fonctionnalités

### Traduction de Texte

- Translation bidirectionnelle entre 200 langues
- Préservation du contexte et du ton
- Gestion automatique des codes de langue (ISO-639 ou codes NLLB)

### Normalisation de Codes Langue

- Conversion automatique des codes ISO courts (EN, FR, ES) vers codes NLLB (eng_Latn, fra_Latn, spa_Latn)
- Validation stricte des langues supportées
- Messages d'erreur explicites pour codes invalides

### Performance

- Traitement batch optimisé
- Cache de modèle persistant
- Réponses < 2s pour textes courts (< 100 mots)

---

## 🏗️ Architecture Technique

### Stack

```
┌─────────────────────────────────────┐
│         FastAPI Service             │
│  (Python 3.9 + Uvicorn)             │
├─────────────────────────────────────┤
│   Transformers 4.x (Hugging Face)   │
├─────────────────────────────────────┤
│   NLLB-200 Model (3.3B params)      │
│   facebook/nllb-200-distilled-600M  │
└─────────────────────────────────────┘
```

### Composants

- **FastAPI** : Framework web asynchrone
- **Transformers** : Bibliothèque Hugging Face pour modèles NLP
- **NLLB Tokenizer** : Tokenizer multilingue spécialisé
- **PyTorch** : Backend pour inférence du modèle

### Dépendances principales

```txt
fastapi==0.115.6
transformers==4.46.3
torch==2.5.1
uvicorn==0.34.0
pydantic-settings==2.6.1
```

---

## 🛠️ Installation & Configuration

### Prérequis

- Python 3.9+
- 4 GB RAM minimum (8 GB recommandé)
- 2 GB espace disque (pour le modèle)
- Docker (optionnel mais recommandé)

### Installation Locale

#### 1. Cloner le projet

```bash
git clone https://github.com/your-org/Travliaq-Translate.git
cd Travliaq-Translate
```

#### 2. Créer l'environnement virtuel

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

#### 3. Installer les dépendances

```bash
pip install -r requirements.txt
```

#### 4. Configuration

Créer un fichier `.env` à la racine :

```env
# Modèle NLLB à utiliser
MODEL_NAME=facebook/nllb-200-distilled-600M

# Cache pour le modèle (économise temps de téléchargement)
TRANSFORMERS_CACHE=/path/to/model_cache

# Configuration serveur
API_HOST=0.0.0.0
API_PORT=8000
DEBUG_MODE=false
```

#### 5. Lancer le service

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Le service sera accessible sur `http://localhost:8000`

### Installation Docker (Recommandé)

```bash
# Build l'image
docker build -t travliaq-translate .

# Lancer le container
docker run -d \
  --name travliaq-translate \
  -p 8000:8000 \
  -e MODEL_NAME=facebook/nllb-200-distilled-600M \
  -v $(pwd)/model_cache:/app/model_cache \
  travliaq-translate
```

Ou avec docker-compose :

```bash
docker-compose up -d
```

---

## 📖 Utilisation

### API Endpoint

#### `POST /translate`

Traduit un texte d'une langue source vers une langue cible.

**Request Body:**

```json
{
  "text": "Welcome to Paris! Discover the Eiffel Tower.",
  "source_language": "EN",
  "target_language": "FR"
}
```

**Response:**

```json
{
  "translated_text": "Bienvenue à Paris ! Découvrez la Tour Eiffel.",
  "target_language": "fra_Latn"
}
```

**Codes HTTP:**

- `200 OK` : Traduction réussie
- `400 Bad Request` : Code de langue invalide ou texte vide
- `500 Internal Server Error` : Erreur du modèle
- `503 Service Unavailable` : Service non initialisé

### Exemples cURL

#### Traduction Anglais → Français

```bash
curl -X POST "http://localhost:8000/translate" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "The best time to visit is during spring",
    "source_language": "EN",
    "target_language": "FR"
  }'
```

#### Traduction Français → Espagnol

```bash
curl -X POST "http://localhost:8000/translate" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Ce monument historique date du XIIe siècle",
    "source_language": "FR",
    "target_language": "ES"
  }'
```

#### Utilisation de codes NLLB complets

```bash
curl -X POST "http://localhost:8000/translate" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Hello world",
    "source_language": "eng_Latn",
    "target_language": "zho_Hans"
  }'
```

### Exemples Python

```python
import requests

def translate_text(text: str, source: str, target: str) -> str:
    response = requests.post(
        "http://localhost:8000/translate",
        json={
            "text": text,
            "source_language": source,
            "target_language": target
        }
    )
    response.raise_for_status()
    return response.json()["translated_text"]

# Usage
result = translate_text(
    "Visit the ancient temples at sunrise",
    source="EN",
    target="FR"
)
print(result)  # "Visitez les temples anciens au lever du soleil"
```

### Exemples JavaScript/Node.js

```javascript
async function translateText(text, sourceLang, targetLang) {
  const response = await fetch("http://localhost:8000/translate", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      text: text,
      source_language: sourceLang,
      target_language: targetLang,
    }),
  });

  if (!response.ok) {
    throw new Error(`Translation failed: ${response.statusText}`);
  }

  const data = await response.json();
  return data.translated_text;
}

// Usage
const translated = await translateText(
  "Book your tickets in advance",
  "EN",
  "DE"
);
console.log(translated); // "Buchen Sie Ihre Tickets im Voraus"
```

---

## 🔌 Intégration MCP

### Ajouter l'outil au serveur MCP

#### 1. Créer le fichier `tools/translation.py`

```python
"""
Translation tool for Travliaq MCP Server
"""
from typing import Dict, Any
import httpx
from app.config import settings

TRANSLATE_SERVICE_URL = settings.translate_service_url  # http://travliaq-translate:8000


async def translate_text(
    text: str,
    source_language: str = "EN",
    target_language: str = "FR"
) -> Dict[str, Any]:
    """
    Translate text using Travliaq-Translate service.

    Args:
        text: Text to translate
        source_language: Source language code (EN, FR, ES, etc.)
        target_language: Target language code

    Returns:
        Dict containing translated_text and target_language

    Raises:
        RuntimeError: If translation service is unavailable or returns error
    """
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.post(
                f"{TRANSLATE_SERVICE_URL}/translate",
                json={
                    "text": text,
                    "source_language": source_language,
                    "target_language": target_language
                }
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            raise RuntimeError(f"Translation failed: {e.response.text}")
        except httpx.RequestError as e:
            raise RuntimeError(f"Translation service unavailable: {str(e)}")
```

#### 2. Enregistrer l'outil dans `server.py`

```python
from mcp import Context
from typing import Dict, Any
from .tools import translation as t

@mcp.tool(name="text.translate")
async def text_translate(
    text: str,
    source_language: str = "EN",
    target_language: str = "FR",
    ctx: Context = None
) -> Dict[str, Any]:
    """
    Traduit un texte d'une langue source vers une langue cible.

    Utilise le service Travliaq-Translate basé sur NLLB-200.
    Supporte 200 langues avec haute qualité.

    Args:
        text: Texte à traduire (max 512 tokens)
        source_language: Code de langue source (EN, FR, ES, DE, IT, PT, etc.)
        target_language: Code de langue cible

    Returns:
        Dict avec `translated_text` et `target_language` normalisé

    Examples:
        text.translate(text="Hello world", source_language="EN", target_language="FR")
        → {"translated_text": "Bonjour le monde", "target_language": "fra_Latn"}
    """
    try:
        if ctx:
            await ctx.info(f"Translating {source_language} → {target_language}")

        result = await t.translate_text(text, source_language, target_language)

        if ctx:
            await ctx.info(f"Translation successful")

        return result
    except Exception as e:
        if ctx:
            await ctx.error(f"Translation failed: {str(e)}")
        raise
```

#### 3. Configuration Docker Compose

Ajouter le service dans `docker-compose.yml` du projet MCP :

```yaml
services:
  mcp-server:
    # ... config existante
    environment:
      - TRANSLATE_SERVICE_URL=http://travliaq-translate:8000
    depends_on:
      - travliaq-translate

  travliaq-translate:
    image: travliaq-translate:latest
    container_name: travliaq-translate
    environment:
      - MODEL_NAME=facebook/nllb-200-distilled-600M
      - TRANSFORMERS_CACHE=/app/model_cache
    volumes:
      - translate-cache:/app/model_cache
    ports:
      - "8001:8000" # Exposé en 8001 sur l'hôte
    restart: unless-stopped

volumes:
  translate-cache:
```

#### 4. Utilisation depuis les agents

```python
# Dans un agent CrewAI
from crewai import Agent, Task

translation_agent = Agent(
    role="Traducteur",
    goal="Traduire les itinéraires dans la langue de l'utilisateur",
    tools=["text.translate"],  # MCP tool
    # ...
)

translate_task = Task(
    description="""
    Traduire tous les titres et descriptions de l'itinéraire
    du français vers {target_language}.

    Itinéraire: {itinerary_json}
    Langue cible: {target_language}
    """,
    agent=translation_agent,
    expected_output="JSON de l'itinéraire traduit"
)
```

---

## 📚 API Reference

### Schemas Pydantic

#### TranslationRequest

```python
class TranslationRequest(BaseModel):
    text: str  # Texte à traduire (1-10000 caractères)
    source_language: str  # Code langue source
    target_language: str  # Code langue cible
```

#### TranslationResponse

```python
class TranslationResponse(BaseModel):
    translated_text: str  # Texte traduit
    target_language: str  # Code NLLB normalisé (ex: "fra_Latn")
```

### Endpoints

| Endpoint        | Méthode | Description              |
| --------------- | ------- | ------------------------ |
| `/translate`    | POST    | Traduit un texte         |
| `/docs`         | GET     | Documentation Swagger UI |
| `/openapi.json` | GET     | Schéma OpenAPI           |

---

## 🌍 Langues Supportées

### Mapping de Codes Courts

Le service accepte les codes ISO courts et les convertit automatiquement :

| Code Court | Code NLLB  | Langue      | Script     |
| ---------- | ---------- | ----------- | ---------- |
| `EN`       | `eng_Latn` | Anglais     | Latin      |
| `FR`       | `fra_Latn` | Français    | Latin      |
| `ES`       | `spa_Latn` | Espagnol    | Latin      |
| `DE`       | `deu_Latn` | Allemand    | Latin      |
| `IT`       | `ita_Latn` | Italien     | Latin      |
| `PT`       | `por_Latn` | Portugais   | Latin      |
| `NL`       | `nld_Latn` | Néerlandais | Latin      |
| `RU`       | `rus_Cyrl` | Russe       | Cyrillique |
| `AR`       | `arb_Arab` | Arabe       | Arabe      |
| `ZH`       | `zho_Hans` | Chinois     | Simplifié  |

### Langues NLLB Complètes

Le modèle NLLB-200 supporte **200 langues**. Exemples :

- **Européennes** : eng, fra, deu, ita, spa, por, nld, pol, ces, ron, etc.
- **Asiatiques** : zho, jpn, kor, tha, vie, hin, ben, etc.
- **Africaines** : swa, amh, hau, yor, etc.
- **Autres** : tur, fas, heb, ukr, ell, etc.

Pour la liste complète, consultez : [NLLB Languages](https://github.com/facebookresearch/fairseq/tree/nllb#languages-in-nllb-200)

---

## 🚢 Déploiement

### Déploiement Railway

1. Connecter le repo GitHub à Railway
2. Configurer les variables d'environnement :
   ```
   MODEL_NAME=facebook/nllb-200-distilled-600M
   TRANSFORMERS_CACHE=/app/model_cache
   ```
3. Railway détectera automatiquement le `Dockerfile`
4. Le service sera déployé avec HTTPS automatique

### Déploiement Docker Swarm

```bash
docker stack deploy -c docker-compose.yml travliaq-translate
```

### Déploiement Kubernetes

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: travliaq-translate
spec:
  replicas: 2
  selector:
    matchLabels:
      app: travliaq-translate
  template:
    metadata:
      labels:
        app: travliaq-translate
    spec:
      containers:
        - name: translate
          image: travliaq-translate:latest
          ports:
            - containerPort: 8000
          env:
            - name: MODEL_NAME
              value: facebook/nllb-200-distilled-600M
          resources:
            requests:
              memory: "4Gi"
              cpu: "1000m"
            limits:
              memory: "8Gi"
              cpu: "2000m"
          volumeMounts:
            - name: model-cache
              mountPath: /app/model_cache
      volumes:
        - name: model-cache
          persistentVolumeClaim:
            claimName: translate-cache-pvc
```

---

## 🐛 Troubleshooting

### Erreur: `AttributeError: NllbTokenizerFast has no attribute lang_code_to_id`

**Cause** : Version ancienne du code utilisant l'API obsolète du tokenizer.

**Solution** :

```bash
cd Travliaq-Translate
git pull origin main
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

### Erreur: `ValueError: Unsupported language code: XX`

**Cause** : Code de langue non reconnu.

**Solution** : Vérifier que le code est soit :

- Un code court mappé : EN, FR, ES, DE, IT, PT, NL, RU, AR, ZH
- Un code NLLB complet : `eng_Latn`, `fra_Latn`, etc.

### Erreur: `503 Service Unavailable`

**Cause** : Le modèle n'est pas encore chargé en mémoire.

**Solution** : Attendre 30-60 secondes après le démarrage du container pour que le modèle NLLB se charge.

### Performance lente (>10s par traduction)

**Causes possibles** :

1. CPU insuffisant (recommandé : 2+ cores)
2. RAM insuffisante (recommandé : 8 GB)
3. Texte très long (>500 mots)

**Solutions** :

- Augmenter les ressources Docker
- Utiliser un modèle plus petit : `facebook/nllb-200-distilled-600M` (600M params)
- Découper les textes longs en chunks

### Le modèle se télécharge à chaque redémarrage

**Cause** : Cache non persisté.

**Solution** : Monter un volume pour `/app/model_cache` :

```bash
docker run -v $(pwd)/model_cache:/app/model_cache travliaq-translate
```

---

## 📝 Changelog

### v1.1.0 (2024-12-04)

- ✅ Fix: Remplacement de `lang_code_to_id` par `convert_tokens_to_ids`
- ✅ Compatibilité avec Transformers 4.46+
- ✅ Gestion robuste des erreurs de tokenization
- 📚 Documentation complète pour intégration MCP

### v1.0.0

- 🎉 Version initiale
- ✅ Support NLLB-200 avec 10 langues principales
- ✅ API FastAPI
- ✅ Docker support

---

## 🤝 Contribution

Les contributions sont les bienvenues ! Pour contribuer :

1. Fork le projet
2. Créer une branche (`git checkout -b feature/amazing-feature`)
3. Commit les changements (`git commit -m 'Add amazing feature'`)
4. Push vers la branche (`git push origin feature/amazing-feature`)
5. Ouvrir une Pull Request

---

## 📄 License

Ce projet est sous licence MIT. Voir le fichier `LICENSE` pour plus de détails.

---

## 📞 Support

- **Issues** : [GitHub Issues](https://github.com/your-org/Travliaq-Translate/issues)
- **Documentation MCP** : Voir le README du projet `Travliaq-MCP`
- **Email** : support@travliaq.com

---

## 🙏 Remerciements

- **Meta AI** pour le modèle NLLB-200
- **Hugging Face** pour la bibliothèque Transformers
- **FastAPI** pour le framework web

---

**Made with ❤️ for Travliaq Platform**
