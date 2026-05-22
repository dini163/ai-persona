import os
import json
import urllib.request
import urllib.parse
import time
import sys
import re

def get_translation(text, target_lang):
    if not text:
        return ""
    
    url = "https://translate.googleapis.com/translate_a/single"
    params = {
        "client": "gtx",
        "sl": "en",
        "tl": target_lang,
        "dt": "t",
        "q": text
    }
    query_string = urllib.parse.urlencode(params)
    req = urllib.request.Request(f"{url}?{query_string}", headers={'User-Agent': 'Mozilla/5.0'})
    
    retries = 3
    backoff = 2.0
    while retries > 0:
        try:
            with urllib.request.urlopen(req) as response:
                res = json.loads(response.read().decode('utf-8'))
                translated = "".join([sentence[0] for sentence in res[0]])
                return translated
        except urllib.error.HTTPError as e:
            if e.code == 429:
                print(f"Rate limited (429) for {target_lang}. Retrying in {backoff}s...")
                time.sleep(backoff)
                backoff *= 2
                retries -= 1
            else:
                print(f"HTTP Error: {e.code} for {target_lang}")
                return None
        except Exception as e:
            print(f"Connection error: {e}")
            time.sleep(1)
            retries -= 1
    return None

def translate_batch(texts, target_lang):
    """
    Translates a list of strings in a single batch using a numbered list structure.
    Returns a list of translated strings, or None if validation/length mismatch occurs.
    """
    if not texts:
        return []
    
    # We join with numbered lists: "1. text1\n2. text2"
    joined_text = "\n".join(f"{i}. {t}" for i, t in enumerate(texts, 1))
    translated_raw = get_translation(joined_text, target_lang)
    
    if not translated_raw:
        return None
        
    # Split back into lines
    lines = [line.strip() for line in translated_raw.split("\n") if line.strip()]
    
    # Clean the numbers (e.g. "1. Text" or "1 .Text" or "1 - Text" -> "Text")
    parsed_results = []
    for line in lines:
        clean = re.sub(r"^\d+[\s\.\-\:]+", "", line).strip()
        if clean:
            parsed_results.append(clean)
            
    if len(parsed_results) == len(texts):
        return parsed_results
    else:
        # Sometimes translations combine lists, print warning and fall back
        print(f"  [Warning] Batch length mismatch in {target_lang}: expected {len(texts)}, got {len(parsed_results)}.")
        return None

def main():
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    json_path = os.path.join(base_dir, "data", "characters.json")
    
    if not os.path.exists(json_path):
        print(f"Error: Database not found at {json_path}")
        sys.exit(1)
        
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    characters = data.get("characters", [])
    total_chars = len(characters)
    print(f"Loaded {total_chars} characters from database.")
    
    languages = ["zh-CN", "zh-TW", "fr", "es", "pt", "ru", "ja", "ko", "ar"]
    
    batch_size = 25
    
    # Process each language
    for lang in languages:
        print(f"\n>>> Starting translations for language: {lang} <<<")
        
        # 1. Gather all names and descriptions that need translation for this language
        names_to_translate = []
        descs_to_translate = []
        indices_to_update = []
        
        for idx, c in enumerate(characters):
            if "translations" not in c:
                c["translations"] = {}
            if lang not in c["translations"]:
                c["translations"][lang] = {}
                
            needs_name = "name" not in c["translations"][lang] or not c["translations"][lang]["name"]
            needs_desc = "description" not in c["translations"][lang] or not c["translations"][lang]["description"]
            
            if needs_name or needs_desc:
                names_to_translate.append(c["name"])
                descs_to_translate.append(c["description"])
                indices_to_update.append(idx)
                
        to_translate_count = len(indices_to_update)
        print(f"Found {to_translate_count} characters that need translation to {lang}.")
        
        if to_translate_count == 0:
            continue
            
        # Translate in batches
        for i in range(0, to_translate_count, batch_size):
            batch_indices = indices_to_update[i:i+batch_size]
            batch_names = names_to_translate[i:i+batch_size]
            batch_descs = descs_to_translate[i:i+batch_size]
            
            print(f"  Translating batch {i//batch_size + 1}/{(to_translate_count-1)//batch_size + 1} (size {len(batch_indices)})...")
            
            # --- Translate names ---
            t_names = translate_batch(batch_names, lang)
            if not t_names:
                # Fall back to sequential for names in this batch
                t_names = []
                for idx_in_batch, name in enumerate(batch_names):
                    print(f"    Fallback sequential name translation: {name[:20]}")
                    res = get_translation(name, lang)
                    t_names.append(res or name)
                    time.sleep(0.1)
                    
            # --- Translate descriptions ---
            t_descs = translate_batch(batch_descs, lang)
            if not t_descs:
                # Fall back to sequential for descs in this batch
                t_descs = []
                for idx_in_batch, desc in enumerate(batch_descs):
                    print(f"    Fallback sequential desc translation: {desc[:20]}...")
                    res = get_translation(desc, lang)
                    t_descs.append(res or desc)
                    time.sleep(0.1)
            
            # Apply to database in memory
            for item_idx, orig_char_idx in enumerate(batch_indices):
                characters[orig_char_idx]["translations"][lang]["name"] = t_names[item_idx]
                characters[orig_char_idx]["translations"][lang]["description"] = t_descs[item_idx]
                
            # Intermittent save
            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
                
            time.sleep(0.3)  # Small cool-down to prevent rate limit
            
        print(f"Finished translations for {lang}.")
        
    print("\nAll database translations complete!")

if __name__ == "__main__":
    main()
