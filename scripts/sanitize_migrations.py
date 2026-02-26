import os
import re

dir_path = r'd:\eka-ai-7.0\migrations\versions'
for filename in os.listdir(dir_path):
    if filename.endswith('.py'):
        path = os.path.join(dir_path, filename)
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Replace now() with CURRENT_TIMESTAMP for defaults
        new_content = content.replace("sa.text('now()')", "sa.text('CURRENT_TIMESTAMP')")
        new_content = new_content.replace("server_default='now()'", "server_default='CURRENT_TIMESTAMP'")
        
        if new_content != content:
            with open(path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print(f"Updated {filename}")
