#!/usr/bin/env python3

import os
import sys
import glob

def get_all_modules():
    """Finds all .htm files recursively in the modules/ directory."""
    # Search recursively for all .htm files
    search_pattern = os.path.join("modules", "**", "*.htm")
    files = glob.glob(search_pattern, recursive=True)
    
    # Make paths relative to the 'modules' folder and convert Windows slashes (\\) to (/)
    rel_files = [os.path.relpath(f, "modules").replace('\\', '/') for f in files]
    return sorted(rel_files)

def generate_sample_list():
    """Generates the moduleselection.txt.sample file."""
    modules = get_all_modules()
    sample_file = "moduleselection.txt.sample"
    
    with open(sample_file, "w", encoding="utf-8") as f:
        f.write("# EuroCheats Module Selection\n")
        f.write("# ---------------------------\n")
        f.write("# 1. Copy this file and rename it to 'moduleselection.txt'\n")
        f.write("# 2. Delete modules you don't need.\n")
        f.write("# 3. Change the order to your liking.\n")
        f.write("# 4. Run 'python build.py'.\n\n")
        
        for mod in modules:
            f.write(f"{mod}\n")
            
    print(f"Successfully created: {sample_file}")
    print("Copy it to 'moduleselection.txt' to match your own rack.")

def build_cheat_sheets():
    """Reads the selection file and builds the index.htm with all chosen cheat sheets."""
    selection_file = "moduleselection.txt"
    modules_to_build = []
    
    # 1. Load selection
    if os.path.exists(selection_file):
        print(f"Reading personal selection from: {selection_file} ...")
        with open(selection_file, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                # Ignore empty lines and comments
                if line and not line.startswith("#"):
                    # Rebuild path
                    filepath = os.path.join("modules", line)
                    if os.path.exists(filepath):
                        modules_to_build.append(filepath)
                    else:
                        print(f"Warning: File '{filepath}' not found. Skipping...")
    else:
        print(f"No '{selection_file}' found. Building ALL available modules...")
        modules_to_build = [os.path.join("modules", m) for m in get_all_modules()]

    if not modules_to_build:
        print("No module files found to build!")
        return

    nav_html = ""
    cards_html = ""
    
    # 2. Generate HTML
    for index, filepath in enumerate(modules_to_build):
        # Normalize slashes to safely split the path regardless of the OS
        normalized_path = filepath.replace('\\', '/')
        parts = normalized_path.split('/')
        
        # Check if it follows the deep structure: modules/Manufacturer/Module/Cheat.htm
        if len(parts) >= 4:
            module_name = parts[-2] # e.g. "Milky Way"
            # cheat_name = os.path.splitext(parts[-1])[0] # e.g. "Algorithms"
            # clean_name = f"{module_name} ({cheat_name})"
            clean_name = f"{module_name}"
        else:
            # Fallback for flat or intermediate structure
            filename = os.path.basename(filepath)
            clean_name = os.path.splitext(filename)[0]
        
        card_id = f"module-{index}"
        active_class = "active" if index == 0 else ""
        
        nav_html += f'<button class="{active_class}" onclick="showCard(\'{card_id}\')">{clean_name}</button>\n'
        
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            
        cards_html += f'<div id="{card_id}" class="card-container {active_class}">\n{content}\n</div>\n'

    # 3. Fill template and save
    try:
        with open('template.htm', 'r', encoding='utf-8') as f:
            template = f.read()
    except FileNotFoundError:
        print("Error: 'template.htm' not found in the root directory!")
        return
        
    final_html = template.replace('[[NAVIGATION]]', nav_html)
    final_html = final_html.replace('[[MODULES]]', cards_html)
    
    with open('index.htm', 'w', encoding='utf-8') as f:
        f.write(final_html)
        
    print(f"\nSuccessfully built: index.htm now contains {len(modules_to_build)} modules.")

if __name__ == "__main__":
    # Check if the script was called with the list argument
    if len(sys.argv) > 1 and sys.argv[1] == "-list":
        generate_sample_list()
    else:
        build_cheat_sheets()