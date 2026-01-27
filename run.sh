#!/bin/bash
echo "Iniciando URBANA..."
echo "Instalando dependências..."
pip install -r requirements.txt 2>/dev/null || echo "✓ Dependências já instaladas"

echo "Criando banco de dados..."
python -c "
from app import app, db, User
with app.app_context():
    db.create_all()
    if not User.query.filter_by(email='admin@urbana.com').first():
        from werkzeug.security import generate_password_hash
        admin = User(name='Administrador', email='admin@urbana.com', organization='URBANA')
        admin.password_hash = generate_password_hash('admin123')
        db.session.add(admin)
        db.session.commit()
        print('✓ Usuário admin criado: admin@urbana.com / admin123')
    print('✓ Banco de dados inicializado')
"

echo "Iniciando servidor..."
python app.py
