import os
import re
import json
from datetime import datetime

# Helper to parse YAML-like frontmatter without external dependency
def parse_frontmatter(content):
    if content.startswith('---'):
        parts = content.split('---', 2)
        if len(parts) >= 3:
            fm_text = parts[1]
            body = parts[2].strip()
            
            fm_data = {}
            for line in fm_text.split('\n'):
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                if ':' in line:
                    k, v = line.split(':', 1)
                    k = k.strip()
                    v = v.strip()
                    if (v.startswith('"') and v.endswith('"')) or (v.startswith("'") and v.endswith("'")):
                        v = v[1:-1]
                    if v.startswith('[') and v.endswith(']'):
                        v = [x.strip().strip("'\"") for x in v[1:-1].split(',')]
                    fm_data[k] = v
            return fm_data, body
    return {}, content

# Keyword-based emoji and tags mapper for game-studios and edict if needed
def get_game_emoji(name):
    name_l = name.lower()
    if 'programmer' in name_l or 'engineer' in name_l or 'developer' in name_l:
        return "💻"
    elif 'designer' in name_l or 'director' in name_l or 'lead' in name_l:
        return "🎮"
    elif 'art' in name_l or 'animator' in name_l or 'technical-artist' in name_l or 'artist' in name_l or 'builder' in name_l:
        return "🎨"
    elif 'audio' in name_l or 'sound' in name_l or 'music' in name_l:
        return "🔊"
    elif 'writer' in name_l or 'narrative' in name_l or 'localization' in name_l:
        return "✍️"
    elif 'qa' in name_l or 'tester' in name_l or 'analyst' in name_l or 'performance' in name_l:
        return "🧪"
    elif 'accessibility' in name_l:
        return "♿"
    elif 'community' in name_l or 'producer' in name_l or 'manager' in name_l:
        return "👥"
    else:
        return "👾"

def get_game_tags(name):
    name_l = name.lower()
    tags = ["Game Dev"]
    if 'programmer' in name_l or 'engineer' in name_l or 'developer' in name_l:
        tags.extend(["Programming", "Coding"])
    if 'designer' in name_l:
        tags.extend(["Design", "Systems"])
    if 'director' in name_l or 'lead' in name_l or 'manager' in name_l or 'producer' in name_l:
        tags.extend(["Leadership", "Management"])
    if 'art' in name_l or 'artist' in name_l or 'builder' in name_l:
        tags.extend(["Art", "Visuals"])
    if 'audio' in name_l or 'sound' in name_l:
        tags.extend(["Audio", "SFX"])
    if 'unity' in name_l:
        tags.append("Unity")
    if 'unreal' in name_l or 'ue-' in name_l:
        tags.append("Unreal Engine")
    if 'godot' in name_l:
        tags.append("Godot")
    if 'qa' in name_l or 'tester' in name_l:
        tags.append("Testing")
    return list(set(tags))

def get_claw_emoji(role_id):
    mapping = {
        'ceo': "🦁", 'cto': "💻", 'cfo': "💰", 'cmo': "📣",
        'researcher': "🔍", 'analyst': "📊", 'engineer': "🛠️",
        'secretary': "📅", 'worker': "🐝", 'founder_coach': "🚀",
        'product_manager': "📋", 'tech_lead': "👨‍💻", 'designer': "🎨",
        'qa': "🧪", 'growth_hacker': "📈", 'fund_manager': "💼",
        'bull_analyst': "🐂", 'bear_analyst': "🐻", 'technical_analyst': "📈",
        'risk_manager': "🛡️", 'sentiment_analyst': "🗣️", 'trader': "⚡",
        'principal_researcher': "🔬", 'experimenter': "🧪", 'evaluator': "📐",
        'reviewer': "👁️", 'logger': "📝", 'architect': "🏗️",
        'project_manager': "📅", 'dev_engineer': "💻", 'qa_engineer': "🛡️",
        'tech_writer': "✍️", 'planner': "🗺️", 'generator': "⚙️",
        'fallback_a': "🤖", 'fallback_b': "🔌"
    }
    return mapping.get(role_id, "🤖")

def main():
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    repos_dir = os.path.join(base_dir, "data", "repos")
    
    print(f"Base Directory: {base_dir}")
    print(f"Repos Directory: {repos_dir}")
    
    characters = []
    
    # ----------------------------------------------------
    # 1. Parse agency-agents
    # ----------------------------------------------------
    agency_dir = os.path.join(repos_dir, "agency-agents")
    if os.path.exists(agency_dir):
        print("[agency-agents] Processing...")
        excluded_dirs = {".git", ".github", "scripts", "examples"}
        count = 0
        for root, dirs, files in os.walk(agency_dir):
            # Exclude non-division folders
            dirs[:] = [d for d in dirs if d not in excluded_dirs]
            
            category = os.path.basename(root)
            if category == "agency-agents" or not category:
                continue
            
            # Format category name (e.g. game-development -> Game Development)
            category_formatted = category.replace("-", " ").title()
            
            for file in files:
                if file.endswith(".md") and file.lower() not in {"readme.md", "contributing.md", "contributing_zh-cn.md", "security.md", "license.md"}:
                    file_path = os.path.join(root, file)
                    with open(file_path, "r", encoding="utf-8") as f:
                        content = f.read()
                    
                    fm_data, body = parse_frontmatter(content)
                    
                    role_id = os.path.splitext(file)[0]
                    name = fm_data.get("name") or role_id.replace("-", " ").title()
                    description = fm_data.get("description") or "Professional division specialist."
                    emoji = fm_data.get("emoji") or "🤖"
                    tags = fm_data.get("tags") or [category_formatted]
                    if isinstance(tags, str):
                        tags = [tags]
                    
                    characters.append({
                        "id": f"agency-{role_id}",
                        "name": name,
                        "emoji": emoji,
                        "category": category_formatted,
                        "source": "agency-agents",
                        "tags": tags,
                        "description": description,
                        "prompt": body,
                        "compatible": ["openclaw", "hermes", "claude", "chatgpt", "manual"]
                    })
                    count += 1
        print(f"[agency-agents] Extracted {count} agents.")
    else:
        print("[agency-agents] Repository folder not found.")

    # ----------------------------------------------------
    # 2. Parse game-studios
    # ----------------------------------------------------
    game_dir = os.path.join(repos_dir, "game-studios")
    agents_subdir = os.path.join(game_dir, ".claude", "agents")
    if os.path.exists(agents_subdir):
        print("[game-studios] Processing...")
        count = 0
        for file in os.listdir(agents_subdir):
            if file.endswith(".md"):
                file_path = os.path.join(agents_subdir, file)
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                
                fm_data, body = parse_frontmatter(content)
                
                role_id = os.path.splitext(file)[0]
                name = fm_data.get("name") or role_id.replace("-", " ").title()
                description = fm_data.get("description") or "Game development studio specialist."
                
                emoji = get_game_emoji(name)
                tags = get_game_tags(name)
                
                characters.append({
                    "id": f"gamestudios-{role_id}",
                    "name": name,
                    "emoji": emoji,
                    "category": "Game Development",
                    "source": "game-studios",
                    "tags": tags,
                    "description": description,
                    "prompt": body,
                    "compatible": ["openclaw", "hermes", "claude", "chatgpt", "manual"]
                })
                count += 1
        print(f"[game-studios] Extracted {count} agents.")
    else:
        print("[game-studios] Repository folder `.claude/agents` not found.")

    # ----------------------------------------------------
    # 3. Parse edict
    # ----------------------------------------------------
    edict_dir = os.path.join(repos_dir, "edict")
    edict_agents_dir = os.path.join(edict_dir, "agents")
    if os.path.exists(edict_agents_dir):
        print("[edict] Processing...")
        count = 0
        
        emoji_map = {
            "bingbu": "🛡️", "gongbu": "🛠️", "hubu": "💰", "libu": "📜",
            "libu_hr": "👥", "menxia": "👁️", "qintianjian": "🔭",
            "shangshu": "🏛️", "taizi": "👑", "xingbu": "⛓️",
            "zaochao": "🏛️", "zhongshu": "✍️"
        }
        
        for folder in os.listdir(edict_agents_dir):
            folder_path = os.path.join(edict_agents_dir, folder)
            if os.path.isdir(folder_path) and folder != "groups":
                soul_path = os.path.join(folder_path, "SOUL.md")
                if os.path.exists(soul_path):
                    with open(soul_path, "r", encoding="utf-8") as f:
                        prompt_content = f.read()
                    
                    # Extract name from the first H1 header
                    name = folder.replace("_", " ").title()
                    h1_match = re.search(r"^#\s+(.+)$", prompt_content, re.MULTILINE)
                    if h1_match:
                        name = h1_match.group(1).strip()
                    
                    # Extract description from the first normal text paragraph under H1
                    description = "Imperial administrative subagent."
                    # Split by paragraph and search for a normal sentence
                    lines = prompt_content.split("\n")
                    for line in lines:
                        line_stripped = line.strip()
                        if line_stripped and not line_stripped.startswith("#") and not line_stripped.startswith(">") and not line_stripped.startswith("-") and not line_stripped.startswith("*"):
                            description = line_stripped
                            break
                    
                    emoji = emoji_map.get(folder.lower(), "🏛️")
                    tags = ["Edict", "Governance", "Imperial Administration"]
                    
                    characters.append({
                        "id": f"edict-{folder.lower()}",
                        "name": name,
                        "emoji": emoji,
                        "category": "Governance",
                        "source": "edict",
                        "tags": tags,
                        "description": description,
                        "prompt": prompt_content,
                        "compatible": ["openclaw", "hermes", "claude", "chatgpt", "manual"]
                    })
                    count += 1
        print(f"[edict] Extracted {count} agents.")
    else:
        print("[edict] Repository folder `agents` not found.")

    # ----------------------------------------------------
    # 4. Parse clawcompany
    # ----------------------------------------------------
    claw_file = os.path.join(repos_dir, "clawcompany", "packages", "shared", "src", "defaults.ts")
    if os.path.exists(claw_file):
        print("[clawcompany] Processing...")
        with open(claw_file, "r", encoding="utf-8") as f:
            claw_content = f.read()
        
        # Define array sections to parse
        sections = {
            "default": "BUILTIN_ROLES",
            "yc_startup": "YC_STARTUP_ROLES",
            "trading": "TRADING_ROLES",
            "research_lab": "RESEARCH_LAB_ROLES",
            "software_dev": "SOFTWARE_DEV_ROLES",
            "harness_builder": "HARNESS_BUILDER_ROLES"
        }
        
        count = 0
        for template_id, array_name in sections.items():
            # Find array content block in file
            # e.g., export const YC_STARTUP_ROLES: Role[] = [ ... ];
            start_marker = f"const {array_name}"
            if f"export const {array_name}" in claw_content:
                start_marker = f"export const {array_name}"
                
            start_idx = claw_content.find(start_marker)
            if start_idx == -1:
                continue
                
            # Find ending of array by searching for the matching ]; or next export
            end_idx = claw_content.find("];", start_idx)
            if end_idx == -1:
                end_idx = len(claw_content)
                
            array_block = claw_content[start_idx:end_idx]
            
            # Find all roles inside this block
            # Each role has:
            # id: '...', name: '...', description: '...', systemPrompt: `...`
            pattern = re.compile(
                r"id:\s*['\"]([^'\"]+)['\"]\s*,\s*"
                r"name:\s*['\"]([^'\"]+)['\"]\s*,\s*"
                r"description:\s*['\"]([^'\"]+)['\"]\s*,\s*"
                r"systemPrompt:\s*`([\s\S]*?)`",
                re.MULTILINE
            )
            
            matches = pattern.findall(array_block)
            
            template_name = template_id.replace("_", " ").title()
            
            for m_id, m_name, m_desc, m_prompt in matches:
                # E.g. clawcompany-yc_startup-founder_coach
                unique_id = f"clawcompany-{template_id}-{m_id}"
                emoji = get_claw_emoji(m_id)
                
                tags = ["ClawCompany", template_name]
                if template_id == "trading":
                    tags.append("Finance")
                elif template_id == "software_dev" or template_id == "harness_builder":
                    tags.append("Engineering")
                elif template_id == "yc_startup":
                    tags.append("Startup")
                elif template_id == "research_lab":
                    tags.append("Research")
                
                characters.append({
                    "id": unique_id,
                    "name": f"{m_name} ({template_name})",
                    "emoji": emoji,
                    "category": "Management" if template_id in ["default", "yc_startup"] else "Specialized",
                    "source": "clawcompany",
                    "tags": tags,
                    "description": m_desc,
                    "prompt": m_prompt.strip(),
                    "compatible": ["openclaw", "hermes", "claude", "chatgpt", "manual"]
                })
                count += 1
                
        print(f"[clawcompany] Extracted {count} agents.")
    else:
        print("[clawcompany] File `defaults.ts` not found.")

    # ----------------------------------------------------
    # 5. Output to characters.json
    # ----------------------------------------------------
    output_path = os.path.join(base_dir, "data", "characters.json")
    
    data = {
        "meta": {
            "version": "1.1.0",
            "lastUpdated": datetime.now().strftime("%Y-%m-%d"),
            "totalCharacters": len(characters),
            "sources": [
                { "id": "agency-agents", "name": "The Agency", "url": "https://github.com/msitarzewski/agency-agents", "color": "#6366f1" },
                { "id": "edict", "name": "三省六部 Edict", "url": "https://github.com/cft0808/edict", "color": "#ef4444" },
                { "id": "game-studios", "name": "Game Studios", "url": "https://github.com/Donchitos/Claude-Code-Game-Studios", "color": "#8b5cf6" },
                { "id": "clawcompany", "name": "ClawCompany", "url": "https://github.com/Claw-Company/clawcompany", "color": "#f59e0b" }
            ]
        },
        "characters": characters
    }
    
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        
    print(f"\nSuccessfully wrote {len(characters)} characters to {output_path}!")

    # ----------------------------------------------------
    # 6. Cleanup temporary cloned repositories
    # ----------------------------------------------------
    if os.path.exists(repos_dir):
        print(f"Cleaning up temporary repositories folder: {repos_dir}...")
        import shutil
        import stat
        
        def remove_readonly(func, path, excinfo):
            try:
                os.chmod(path, stat.S_IWRITE)
                func(path)
            except Exception:
                pass
                
        try:
            shutil.rmtree(repos_dir, onerror=remove_readonly)
            print("Successfully removed temporary files, project structure is clean!")
        except Exception as e:
            print(f"Warning: Failed to remove temporary files: {e}")

if __name__ == "__main__":
    main()
