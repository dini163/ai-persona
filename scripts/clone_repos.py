import os
import subprocess

REPOS = {
    "agency-agents": "https://github.com/msitarzewski/agency-agents.git",
    "edict": "https://github.com/cft0808/edict.git",
    "game-studios": "https://github.com/Donchitos/Claude-Code-Game-Studios.git",
    "clawcompany": "https://github.com/Claw-Company/clawcompany.git"
}

def main():
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "repos"))
    os.makedirs(base_dir, exist_ok=True)
    
    for name, url in REPOS.items():
        target = os.path.join(base_dir, name)
        if os.path.exists(target):
            print(f"[{name}] Already exists, pulling latest...")
            subprocess.run(["git", "pull"], cwd=target, check=True)
        else:
            print(f"[{name}] Cloning from {url}...")
            subprocess.run(["git", "clone", "--depth", "1", url, target], check=True)
            
    print("All repositories cloned successfully!")

if __name__ == "__main__":
    main()
