# Travliaq-Translate - Service de Traduction

## 🐛 Bug Fix - AttributeError NLLB Tokenizer

### Problème Identifié

```
AttributeError: NllbTokenizerFast has no attribute lang_code_to_id
```

### Cause

L'API du tokenizer NLLB a changé dans les versions récentes de `transformers`. L'attribut `lang_code_to_id` n'existe plus dans `NllbTokenizerFast`.

### Solution Appliquée

#### Avant (❌ Non fonctionnel)

```python
# Ligne 38
if clean_code in self.tokenizer.lang_code_to_id:
    return clean_code

# Ligne 55
forced_bos_token_id = self.tokenizer.lang_code_to_id.get(target_lang_code)
```

#### Après (✅ Corrigé)

```python
# Validation de langue
token_id = self.tokenizer.convert_tokens_to_ids(clean_code)
if token_id != self.tokenizer.unk_token_id:
    return clean_code

# Obtention du BOS token ID
forced_bos_token_id = self.tokenizer.convert_tokens_to_ids(target_lang_code)
if forced_bos_token_id == self.tokenizer.unk_token_id:
    raise ValueError(f"Unsupported target language code: {target_language}")
```

### Changements dans `service.py`

1. **`_resolve_language()` (lignes 31-40)**

   - Remplacé `self.tokenizer.lang_code_to_id` par `convert_tokens_to_ids()`
   - Ajout de validation avec `unk_token_id`
   - Gestion d'exceptions pour codes invalides

2. **`translate()` (lignes 46-64)**
   - Utilisation de `convert_tokens_to_ids()` pour obtenir `forced_bos_token_id`
   - Validation que le token n'est pas le token "unknown"
   - Messages d'erreur plus clairs

### Test de Validation

Pour tester en production:

```bash
curl -X POST "http://your-service/translate" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Hello world",
    "source_language": "EN",
    "target_language": "FR"
  }'
```

Réponse attendue:

```json
{
  "translated_text": "Bonjour le monde",
  "target_language": "fra_Latn"
}
```

### Langues Supportées

- EN → eng_Latn (Anglais)
- FR → fra_Latn (Français)
- ES → spa_Latn (Espagnol)
- DE → deu_Latn (Allemand)
- PT → por_Latn (Portugais)
- IT → ita_Latn (Italien)
- NL → nld_Latn (Néerlandais)
- RU → rus_Cyrl (Russe)
- AR → arb_Arab (Arabe)
- ZH → zho_Hans (Chinois simplifié)

### Production Ready ✅

Le service est maintenant:

- ✅ Compatible avec les versions récentes de `transformers`
- ✅ Gestion robuste des erreurs
- ✅ Validation stricte des codes de langue
- ✅ Messages d'erreur clairs pour le débogage
