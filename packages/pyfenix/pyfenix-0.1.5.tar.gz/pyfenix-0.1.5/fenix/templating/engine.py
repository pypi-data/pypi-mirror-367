# fenix/templating/engine.py
import re
import os

def load_templates(template_path):
    if not os.path.exists(template_path):
        print(f"{template_path} not found!")
        return {}

    with open(template_path, "r", encoding="utf-8") as f:
        content = f.read()

    matches = re.findall(r"\{\% template \"(.*?)\" \%\}(.*?)(?=\{\% template|$)", content, re.S)
    return {name.strip(): html.strip() for name, html in matches}
