#!/usr/bin/env python3
import os
import re

def fix_strftime_in_templates():
    template_dir = "."
    
    for filename in os.listdir(template_dir):
        if filename.endswith(".html"):
            filepath = os.path.join(template_dir, filename)
            print(f"Processando: {filename}")
            
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Substituir .strftime('%...') por format_date(..., '...')
            # Padrão: {{ variavel.strftime('%d/%m/%Y') }}
            pattern1 = r'\{\{\s*([^}]+?)\.strftime\(([^)]+)\)\s*\}\}'
            replacement1 = r'{{ format_date(\1, \2) }}'
            content = re.sub(pattern1, replacement1, content)
            
            # Padrão: {{ variavel.strftime("%d/%m/%Y") }}
            pattern2 = r'\{\{\s*([^}]+?)\.strftime\(([^)]+)\)\s*\}\}'
            content = re.sub(pattern2, replacement1, content)
            
            # Padrão: {{ variavel.created_at.strftime('%d/%m/%Y') }}
            pattern3 = r'\{\{\s*([^}]+?)\.created_at\.strftime\(([^)]+)\)\s*\}\}'
            replacement3 = r'{{ format_date(\1.created_at, \2) }}'
            content = re.sub(pattern3, replacement3, content)
            
            # Padrão: {{ sim.created_at.strftime('%d/%m/%Y') }}
            pattern4 = r'\{\{\s*sim\.created_at\.strftime\(([^)]+)\)\s*\}\}'
            replacement4 = r'{{ format_date(sim.created_at, \1) }}'
            content = re.sub(pattern4, replacement4, content)
            
            # Padrão: {{ user.created_at.strftime('%d/%m/%Y') }}
            pattern5 = r'\{\{\s*user_stats\.user_data\.created_at\.strftime\(([^)]+)\)\s*\}\}'
            replacement5 = r'{{ format_date(user_stats.user_data.created_at, \1) }}'
            content = re.sub(pattern5, replacement5, content)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f"✓ {filename} atualizado")

if __name__ == "__main__":
    fix_strftime_in_templates()
    print("✅ Todos os templates foram atualizados!")
