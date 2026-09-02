import urllib.request
import json
import re
from typing import List, Dict, Tuple, Any, Optional

def parse_iso_duration(duration_str: str) -> int:
    """Convert ISO 8601 duration (e.g. PT10M, PT1H15M) into minutes."""
    if not duration_str:
        return 0
    match = re.match(r'PT(?:(\d+)H)?(?:(\d+)M)?', duration_str)
    if not match:
        return 0
    hours = int(match.group(1) or 0)
    minutes = int(match.group(2) or 0)
    return hours * 60 + minutes


def parse_servings(yield_str: str) -> int:
    """Extract number of servings from strings like '6 personnes' or '6'."""
    if not yield_str:
        return 5
    match = re.search(r'\d+', str(yield_str))
    if match:
        return max(1, int(match.group(0)))
    return 5


def parse_marmiton_ingredient(raw_text: str) -> Tuple[str, float, str, Optional[str]]:
    """
    Extract ingredient name, amount, unit, and non-critical warning log from Marmiton text.
    """
    text = raw_text.strip()
    warning = None

    # Handle parenthetical notes (e.g., "(type bulgare)")
    text_clean = re.sub(r'\s*\([^)]*\)', '', text).strip()
    if not text_clean:
        text_clean = text

    # Extract quantity at beginning
    amount_match = re.match(r'^(\d+(?:[.,]\d+)?|\d+/\d+)\s*(.*)', text_clean)
    if not amount_match:
        return text_clean.capitalize(), 1.0, "pincée", f"Quantité non spécifiée pour '{text_clean}' -> 1 pincée appliquée par défaut"

    amount_str = amount_match.group(1).replace(',', '.')
    if '/' in amount_str:
        num, den = amount_str.split('/')
        amount = float(num) / float(den)
    else:
        amount = float(amount_str)

    rest = amount_match.group(2).strip()

    # Units matching pattern
    unit_patterns = [
        (r'^(cuillères? à soupe|c\. à soupe|cs)\s+(?:de\s+|d\'\s*)?', 'c. à soupe'),
        (r'^(cuillères? à café|c\. à café|cc)\s+(?:de\s+|d\'\s*)?', 'c. à café'),
        (r'^(gousses?)\s+(?:de\s+|d\'\s*)?', 'gousses'),
        (r'^(pincées?)\s+(?:de\s+|d\'\s*)?', 'pincée'),
        (r'^(tranches?)\s+(?:de\s+|d\'\s*)?', 'tranches'),
        (r'^(pots?)\s+(?:de\s+|d\'\s*)?', 'pots'),
        (r'^(sachets?)\s+(?:de\s+|d\'\s*)?', 'sachets'),
        (r'^(clous?)\s+(?:de\s+|d\'\s*)?', 'clous'),
        (r'^(g|kg|ml|cl|l)\b\s*(?:de\s+|d\'\s*)?', None),
    ]

    unit = "pièces"
    name = rest

    for pattern, normalized_unit in unit_patterns:
        match = re.search(pattern, rest, re.IGNORECASE)
        if match:
            matched_unit = match.group(1).lower()
            unit = normalized_unit if normalized_unit else matched_unit
            name = rest[match.end():].strip()
            break

    # Clean leading 'de ' or 'd\''
    name = re.sub(r'^(?:de\s+|d\'\s*)', '', name, flags=re.IGNORECASE).strip()
    if not name:
        name = rest

    return name.capitalize(), round(amount, 2), unit, warning


def fetch_marmiton_recipe_data(url: str) -> Dict[str, Any]:
    """
    Fetch Marmiton recipe URL and extract structured data + log notes.
    """
    url_clean = url.strip()
    if 'marmiton.org' not in url_clean:
        raise ValueError("L'URL doit provenir du site marmiton.org")

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept-Language': 'fr-FR,fr;q=0.9,en;q=0.8'
    }

    req = urllib.request.Request(url_clean, headers=headers)
    logs: List[str] = []

    try:
        html = urllib.request.urlopen(req, timeout=10).read().decode('utf-8')
    except Exception as e:
        raise RuntimeError(f"Impossible de contacter le serveur Marmiton : {str(e)}")

    # Extract JSON-LD graph
    matches = re.findall(r'<script[^>]*type=["\']application/ld\+json["\'][^>]*>(.*?)</script>', html, re.DOTALL)
    recipe_ld = None

    for m in matches:
        try:
            data = json.loads(m.strip())
            graph = data.get('@graph', [data])
            for item in graph:
                if isinstance(item, dict) and item.get('@type') in ['Recipe', 'http://schema.org/Recipe']:
                    recipe_ld = item
                    break
            if recipe_ld:
                break
        except Exception:
            continue

    if not recipe_ld:
        # Fallback to HTML Title if JSON-LD fails
        title_match = re.search(r'<h1[^>]*>(.*?)</h1>', html, re.DOTALL)
        if not title_match:
            raise ValueError("Impossible d'extraire la recette depuis cette page Marmiton.")
        recipe_name = re.sub(r'<[^>]+>', '', title_match.group(1)).strip()
        raw_ingredients = []
        prep_time = 15
        cook_time = 20
        servings = 5
        logs.append("⚠️ Métadonnées JSON-LD non trouvées : extraction HTML basique effectuée.")
    else:
        # Extract title
        recipe_name = recipe_ld.get('name', 'Recette Marmiton').strip()
        recipe_name = re.sub(r'\s*:.*best of.*', '', recipe_name, flags=re.IGNORECASE)
        recipe_name = re.sub(r'\s*:.*la meilleure recette.*', '', recipe_name, flags=re.IGNORECASE).strip()

        prep_time = parse_iso_duration(recipe_ld.get('prepTime', '')) or 15
        cook_time = parse_iso_duration(recipe_ld.get('cookTime', '')) or 20
        servings = parse_servings(recipe_ld.get('recipeYield', '5'))
        raw_ingredients = recipe_ld.get('recipeIngredient', [])

    parsed_ingredients = []
    for raw in raw_ingredients:
        name, amount, unit, warn = parse_marmiton_ingredient(raw)
        if warn:
            logs.append(f"⚠️ {warn}")
        parsed_ingredients.append({
            "name": name,
            "amount": amount,
            "unit": unit
        })

    logs.insert(0, f"✅ Recette '{recipe_name}' extraite avec succès ({len(parsed_ingredients)} ingrédients) !")

    return {
        "name": recipe_name,
        "prep_time": prep_time,
        "cook_time": cook_time,
        "base_servings": servings,
        "ingredients": parsed_ingredients,
        "logs": logs
    }
