#!/bin/python3
# Script para corrigir o app.py

import re

with open('app.py', 'r') as f:
    content = f.read()

# Encontrar a função resend_confirmation problemática
pattern = r'(@app\.route\("/resend-confirmation".*?def resend_confirmation\(\):.*?)(?=@app\.route|\Z)'
match = re.search(pattern, content, re.DOTALL)

if match:
    print("Encontrei a função problemática")
    
    # Substituir por versão corrigida
    fixed_function = '''@app.route("/resend-confirmation", methods=["GET", "POST"])
def resend_confirmation():
    """Reenviar email de confirmação"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    if request.method == "POST":
        email = request.form.get('email')
        
        if not email:
            flash('Por favor, informe seu email.', 'danger')
        else:
            try:
                if hasattr(g, 'supabase'):
                    supabase = g.supabase
                else:
                    supabase = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)
                
                # Método simples: tentar reenviar confirmação
                supabase.auth.resend({
                    "type": "signup",
                    "email": email
                })
                
                flash(f'📩 Enviamos novamente o email de confirmação para {email}. Verifique sua caixa de entrada.', 'success')
                return redirect(url_for('login'))
                
            except Exception as e:
                error_msg = str(e)
                if "already confirmed" in error_msg.lower():
                    flash('Este email já foi confirmado. Faça login normalmente.', 'info')
                    return redirect(url_for('login'))
                elif "not found" in error_msg.lower():
                    flash('Este email não está cadastrado no sistema.', 'warning')
                else:
                    flash(f'Erro ao reenviar confirmação: {error_msg}', 'danger')
    
    return render_template("resend_confirmation.html")
'''
    
    # Substituir no conteúdo
    content = content[:match.start()] + fixed_function + content[match.end():]
    
    # Salvar arquivo corrigido
    with open('app.py', 'w') as f:
        f.write(content)
    
    print("✅ Arquivo corrigido com sucesso!")
else:
    print("❌ Não encontrei a função problemática")
