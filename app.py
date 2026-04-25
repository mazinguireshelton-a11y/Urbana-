from flask import Flask, render_template, request, jsonify, make_response, redirect, url_for, flash, session
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from supabase import create_client
from datetime import datetime, timedelta, timezone
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from io import BytesIO, StringIO
from dotenv import load_dotenv
import json
import csv
import os
import secrets
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

load_dotenv()

# ============================================================
# CONFIGURAÇÃO INICIAL
# ============================================================

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', secrets.token_hex(32))
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=30)

# ============================================================
# SUPABASE
# ============================================================

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_ANON_KEY = os.getenv('SUPABASE_ANON_KEY')

if not SUPABASE_URL or not SUPABASE_ANON_KEY:
    raise ValueError("SUPABASE_URL e SUPABASE_ANON_KEY são obrigatórios!")

supabase = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)

# ============================================================
# FLASK-LOGIN
# ============================================================

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Por favor, faça login para continuar'
login_manager.login_message_category = 'warning'

class User(UserMixin):
    def __init__(self, user_data):
        self.id = user_data.get('id')
        self.email = user_data.get('email')
        self.name = user_data.get('name', 'Usuário')
        self.organization = user_data.get('organization', '')
    
    @staticmethod
    def get(user_id):
        try:
            response = supabase.table('users').select('*').eq('id', user_id).execute()
            if response.data:
                return User(response.data[0])
            return None
        except Exception as e:
            print(f"Erro ao buscar usuário: {e}")
            return None

@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)

# ============================================================
# FUNÇÕES AUXILIARES
# ============================================================

def get_building_type_label(building_type):
    types = {
        'low': 'Baixa Densidade',
        'medium': 'Média Densidade',
        'high': 'Alta Densidade'
    }
    return types.get(building_type, building_type)

# ============================================================
# CONTEXT PROCESSOR
# ============================================================

@app.context_processor
def utility_processor():
    def format_date(date_value, format_str='%d/%m/%Y'):
        if not date_value:
            return "N/A"
        try:
            if isinstance(date_value, str):
                date_value = date_value.replace('Z', '+00:00')
                date_obj = datetime.fromisoformat(date_value)
            elif isinstance(date_value, datetime):
                date_obj = date_value
            else:
                return str(date_value)
            return date_obj.strftime(format_str)
        except:
            return "N/A"
    
    def format_number(value, decimals=0):
        if value is None:
            return "N/A"
        try:
            num = float(str(value).replace(',', '.'))
            if decimals == 0:
                return f"{int(num):,}".replace(",", ".")
            return f"{num:,.{decimals}f}".replace(",", ".")
        except:
            return str(value)
    
    return {
        'format_date': format_date,
        'format_number': format_number,
        'get_building_type_label': get_building_type_label
    }

# ============================================================
# ROTAS DE AUTENTICAÇÃO
# ============================================================

@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    if request.method == "POST":
        email = request.form.get('email')
        password = request.form.get('password')
        remember = request.form.get('remember', False)
        
        try:
            auth_response = supabase.auth.sign_in_with_password({
                "email": email,
                "password": password
            })
            
            if auth_response.user:
                session['access_token'] = auth_response.session.access_token
                session['refresh_token'] = auth_response.session.refresh_token
                
                user = User.get(auth_response.user.id)
                login_user(user, remember=remember)
                
                flash(f'Bem-vindo, {user.name}!', 'success')
                return redirect(url_for('dashboard'))
                
        except Exception as e:
            error = str(e)
            if "Invalid login" in error:
                flash('Email ou senha incorretos', 'danger')
            else:
                flash('Erro ao fazer login', 'danger')
    
    return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    if request.method == "POST":
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        name = request.form.get('name')
        organization = request.form.get('organization', '')
        
        if password != confirm_password:
            flash('As senhas não coincidem', 'danger')
        elif len(password) < 6:
            flash('A senha deve ter pelo menos 6 caracteres', 'danger')
        else:
            try:
                auth_response = supabase.auth.sign_up({
                    "email": email,
                    "password": password,
                    "options": {
                        "data": {
                            "name": name,
                            "organization": organization
                        }
                    }
                })
                
                if auth_response.user:
                    flash('Conta criada com sucesso! Faça login.', 'success')
                    return redirect(url_for('login'))
                    
            except Exception as e:
                error = str(e)
                if "already registered" in error:
                    flash('Este email já está cadastrado', 'warning')
                else:
                    flash('Erro ao criar conta', 'danger')
    
    return render_template("register.html")

@app.route("/logout")
@login_required
def logout():
    try:
        supabase.auth.sign_out()
    except:
        pass
    session.clear()
    logout_user()
    flash('Você saiu da sua conta', 'info')
    return redirect(url_for('login'))

# ============================================================
# ROTAS PRINCIPAIS
# ============================================================

@app.route("/")
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route("/dashboard")
@login_required
def dashboard():
    try:
        response = supabase.table('simulations')\
            .select('*')\
            .eq('user_id', current_user.id)\
            .order('created_at', desc=True)\
            .execute()
        
        simulations = response.data if response.data else []
        
        # Processar simulações para formato amigável
        processed_simulations = []
        for sim in simulations:
            sim_copy = sim.copy()
            if sim.get('created_at'):
                try:
                    sim_copy['created_at_obj'] = datetime.fromisoformat(sim['created_at'].replace('Z', '+00:00'))
                except:
                    sim_copy['created_at_obj'] = None
            processed_simulations.append(sim_copy)
        
        # Estatísticas
        if processed_simulations:
            total_population = sum(s.get('population', 0) for s in processed_simulations)
            avg_water = sum(s.get('total_water', 0) for s in processed_simulations) / len(processed_simulations)
            avg_energy = sum(s.get('total_energy', 0) for s in processed_simulations) / len(processed_simulations)
            avg_area = sum(s.get('area_size', 0) for s in processed_simulations) / len(processed_simulations)
        else:
            total_population = avg_water = avg_energy = avg_area = 0
        
        stats = {
            'total_simulations': len(processed_simulations),
            'total_population': total_population,
            'avg_water': round(avg_water, 2),
            'avg_energy': round(avg_energy, 2),
            'avg_area': round(avg_area, 2)
        }
        
        # Dados por área para gráficos
        areas_data = {}
        for sim in processed_simulations:
            area = sim.get('area_name', 'Sem nome')
            if area not in areas_data:
                areas_data[area] = {'water': 0, 'energy': 0}
            areas_data[area]['water'] += sim.get('total_water', 0)
            areas_data[area]['energy'] += sim.get('total_energy', 0)
        
        areas = list(areas_data.keys())[:10]
        water_values = [areas_data[area]['water'] for area in areas]
        energy_values = [areas_data[area]['energy'] for area in areas]
        
        # Tendência últimos 7 dias
        trend_data = {}
        seven_days_ago = datetime.now(timezone.utc) - timedelta(days=7)
        
        for sim in processed_simulations:
            if sim.get('created_at_obj') and sim['created_at_obj'] >= seven_days_ago:
                date_str = sim['created_at_obj'].strftime('%Y-%m-%d')
                if date_str not in trend_data:
                    trend_data[date_str] = {'count': 0, 'water': 0, 'energy': 0}
                trend_data[date_str]['count'] += 1
                trend_data[date_str]['water'] += sim.get('total_water', 0)
                trend_data[date_str]['energy'] += sim.get('total_energy', 0)
        
        dates = sorted(trend_data.keys())
        sim_counts = [trend_data[date]['count'] for date in dates]
        trend_water = [trend_data[date]['water'] / trend_data[date]['count'] if trend_data[date]['count'] > 0 else 0 for date in dates]
        trend_energy = [trend_data[date]['energy'] / trend_data[date]['count'] if trend_data[date]['count'] > 0 else 0 for date in dates]
        
        # Distribuição por tipo
        type_dist = {}
        for sim in processed_simulations:
            tipo = sim.get('building_type', 'unknown')
            if tipo not in type_dist:
                type_dist[tipo] = {'count': 0, 'water': 0, 'energy': 0}
            type_dist[tipo]['count'] += 1
            type_dist[tipo]['water'] += sim.get('total_water', 0)
            type_dist[tipo]['energy'] += sim.get('total_energy', 0)
        
        tipo_labels = [get_building_type_label(t) for t in type_dist.keys()]
        tipo_counts = [type_dist[t]['count'] for t in type_dist.keys()]
        tipo_water = [type_dist[t]['water'] / type_dist[t]['count'] if type_dist[t]['count'] > 0 else 0 for t in type_dist.keys()]
        tipo_energy = [type_dist[t]['energy'] / type_dist[t]['count'] if type_dist[t]['count'] > 0 else 0 for t in type_dist.keys()]
        
        return render_template(
            "dashboard.html",
            simulations=processed_simulations,
            stats=stats,
            areas=json.dumps(areas),
            water_values=json.dumps(water_values),
            energy_values=json.dumps(energy_values),
            dates=json.dumps(dates),
            sim_counts=json.dumps(sim_counts),
            trend_water=json.dumps(trend_water),
            trend_energy=json.dumps(trend_energy),
            tipo_labels=json.dumps(tipo_labels),
            tipo_counts=json.dumps(tipo_counts),
            tipo_water=json.dumps(tipo_water),
            tipo_energy=json.dumps(tipo_energy)
        )
        
    except Exception as e:
        print(f"Erro no dashboard: {e}")
        flash('Erro ao carregar dashboard', 'danger')
        return render_template("dashboard.html", simulations=[], stats={'total_simulations': 0})

@app.route("/simulate")
@login_required
def simulate_form():
    return render_template("index.html")

@app.route("/calculate", methods=["POST"])
@login_required
def calculate():
    try:
        area_name = request.form.get('area_name')
        population = int(request.form.get('population', 0))
        area_size = float(request.form.get('area_size', 0))
        building_type = request.form.get('building_type', 'medium')
        
        simulation_data = {
            'user_id': current_user.id,
            'area_name': area_name,
            'population': population,
            'area_size': area_size,
            'building_type': building_type,
            'total_water': population * 120,
            'total_energy': population * 2.5,
            'density': population / area_size if area_size > 0 else 0,
            'water_per_capita': 120,
            'energy_per_capita': 2.5,
            'created_at': datetime.now(timezone.utc).isoformat()
        }
        
        response = supabase.table('simulations').insert(simulation_data).execute()
        
        if response.data:
            flash('✅ Simulação criada com sucesso!', 'success')
            return redirect(url_for('view_report', sim_id=response.data[0]['id']))
        else:
            flash('Erro ao salvar simulação', 'danger')
            return redirect(url_for('simulate_form'))
            
    except Exception as e:
        flash(f'Erro: {str(e)[:100]}', 'danger')
        return redirect(url_for('simulate_form'))

@app.route("/report/<int:sim_id>")
@login_required
def view_report(sim_id):
    try:
        response = supabase.table('simulations')\
            .select('*')\
            .eq('id', sim_id)\
            .eq('user_id', current_user.id)\
            .execute()
        
        if not response.data:
            flash('Simulação não encontrada', 'danger')
            return redirect(url_for('dashboard'))
        
        return render_template("report.html", simulation=response.data[0])
        
    except Exception as e:
        flash('Erro ao carregar relatório', 'danger')
        return redirect(url_for('dashboard'))

@app.route("/my-simulations")
@login_required
def my_simulations():
    try:
        response = supabase.table('simulations')\
            .select('*')\
            .eq('user_id', current_user.id)\
            .order('created_at', desc=True)\
            .execute()
        
        simulations = response.data if response.data else []
        return render_template("my_simulations.html", simulations=simulations)
        
    except Exception as e:
        flash('Erro ao carregar simulações', 'danger')
        return redirect(url_for('dashboard'))

@app.route("/delete/<int:sim_id>", methods=["POST"])
@login_required
def delete_simulation(sim_id):
    try:
        supabase.table('simulations').delete().eq('id', sim_id).eq('user_id', current_user.id).execute()
        flash('Simulação deletada!', 'success')
    except Exception as e:
        flash('Erro ao deletar', 'danger')
    return redirect(url_for('my_simulations'))

@app.route("/api/simulation/<int:sim_id>")
@login_required
def get_simulation_api(sim_id):
    try:
        response = supabase.table('simulations')\
            .select('*')\
            .eq('id', sim_id)\
            .eq('user_id', current_user.id)\
            .execute()
        
        if not response.data:
            return jsonify({"error": "Simulação não encontrada"}), 404
        
        sim = response.data[0]
        return jsonify({
            'id': sim['id'],
            'area_name': sim.get('area_name', ''),
            'population': sim.get('population', 0),
            'area_size': sim.get('area_size', 0),
            'building_type': sim.get('building_type', ''),
            'total_water': sim.get('total_water', 0),
            'total_energy': sim.get('total_energy', 0),
            'created_at': sim.get('created_at', '')
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/profile")
@login_required
def profile():
    try:
        response = supabase.table('simulations').select('id', count='exact').eq('user_id', current_user.id).execute()
        total_sims = response.count if hasattr(response, 'count') else 0
        
        user_stats = {
            'total_simulations': total_sims,
            'user_data': {
                'name': current_user.name,
                'email': current_user.email,
                'organization': current_user.organization
            }
        }
        return render_template("profile.html", user_stats=user_stats)
        
    except Exception as e:
        return render_template("profile.html", user_stats={'total_simulations': 0})

# ============================================================
# EXPORTAÇÕES
# ============================================================

@app.route("/export/csv")
@login_required
def export_csv():
    try:
        response = supabase.table('simulations')\
            .select('*')\
            .eq('user_id', current_user.id)\
            .order('created_at', desc=True)\
            .execute()
        
        simulations = response.data if response.data else []
        
        output = StringIO()
        output.write('\ufeff')
        writer = csv.writer(output)
        writer.writerow(['ID', 'Local', 'População', 'Área (km²)', 'Tipo', 'Água (L/dia)', 'Energia (kWh/dia)', 'Data'])
        
        for sim in simulations:
            writer.writerow([
                sim['id'], sim.get('area_name', ''), sim.get('population', 0),
                sim.get('area_size', 0), get_building_type_label(sim.get('building_type', '')),
                sim.get('total_water', 0), sim.get('total_energy', 0),
                sim.get('created_at', '')[:10] if sim.get('created_at') else ''
            ])
        
        output.seek(0)
        response = make_response(output.getvalue())
        response.headers['Content-Disposition'] = f'attachment; filename=simulacoes_{datetime.now().strftime("%Y%m%d")}.csv'
        response.headers['Content-Type'] = 'text/csv; charset=utf-8'
        return response
        
    except Exception as e:
        flash('Erro ao exportar CSV', 'danger')
        return redirect(url_for('dashboard'))

@app.route("/export/pdf/<int:sim_id>")
@login_required
def export_pdf(sim_id):
    try:
        response = supabase.table('simulations')\
            .select('*')\
            .eq('id', sim_id)\
            .eq('user_id', current_user.id)\
            .execute()
        
        if not response.data:
            flash('Simulação não encontrada', 'danger')
            return redirect(url_for('dashboard'))
        
        sim = response.data[0]
        
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        styles = getSampleStyleSheet()
        
        story = []
        story.append(Paragraph(f"Relatório de Simulação - {sim.get('area_name', 'URBANA')}", styles['Title']))
        story.append(Spacer(1, 20))
        
        data = [
            ['Local', sim.get('area_name', 'N/A')],
            ['População', f"{sim.get('population', 0):,}"],
            ['Área', f"{sim.get('area_size', 0):.2f} km²"],
            ['Tipo', get_building_type_label(sim.get('building_type', ''))],
            ['Água', f"{sim.get('total_water', 0):,.0f} L/dia"],
            ['Energia', f"{sim.get('total_energy', 0):,.2f} kWh/dia"],
        ]
        
        table = Table(data, colWidths=[100, 300])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.grey),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.whitesmoke),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('PADDING', (0, 0), (-1, -1), 6),
        ]))
        story.append(table)
        
        doc.build(story)
        buffer.seek(0)
        
        response = make_response(buffer.getvalue())
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = f'inline; filename=relatorio_{sim_id}.pdf'
        return response
        
    except Exception as e:
        flash('Erro ao gerar PDF', 'danger')
        return redirect(url_for('view_report', sim_id=sim_id))

# ============================================================
# PÁGINAS ESTÁTICAS
# ============================================================

@app.route("/terms")
def terms():
    return render_template("terms.html")

@app.route("/privacy")
def privacy():
    return render_template("privacy.html")

# ============================================================
# EXECUÇÃO
# ============================================================

if __name__ == "__main__":
    print("=" * 60)
    print("🚀 URBANA - Sistema de Planejamento Urbano")
    print(f"✅ Supabase: {SUPABASE_URL}")
    print("=" * 60)
    
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=False, host='0.0.0.0', port=port)
