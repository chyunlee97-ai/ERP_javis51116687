import os

files = ['client/ui/main_window.py', 'client/ui/scifi_avatar.py']

color_map = {
    '#5C4DB1': '#D32F2F',  # Theme -> Red
    '#483A96': '#B71C1C',  # Dark Theme -> Dark Red
    '#C3BCEB': '#FFCDD2',  # Accent / Light -> Light Red
    '#382C80': '#961414',  # Darkest -> Deepest Red
}

for f in files:
    with open(f, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # Replace colors
    for old, new in color_map.items():
        content = content.replace(old, new)
        
    # Replace character image in main_window.py
    if 'main_window.py' in f:
        old_img = '''        self.pixmaps = {
            "idle": QPixmap(os.path.join(PROJECT_ROOT, "character_idle.png")),
            "thinking": QPixmap(os.path.join(PROJECT_ROOT, "character_thinking.png")),
            "talking": QPixmap(os.path.join(PROJECT_ROOT, "character_talking.png")),
        }'''
        new_img = '''        img_path = os.path.join(PROJECT_ROOT, "ERP_javis_transparent.png")
        self.pixmaps = {
            "idle": QPixmap(img_path),
            "thinking": QPixmap(img_path),
            "talking": QPixmap(img_path),
        }'''
        content = content.replace(old_img, new_img)
        
    with open(f, 'w', encoding='utf-8') as file:
        file.write(content)

print("Replacement complete")
