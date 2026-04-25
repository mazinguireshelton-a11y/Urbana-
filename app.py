from flask import Flask, render_template, request, jsonify, send_file, make_response, redirect, url_for, flash, session, g
import secrets
import base64
from supabase import create_client, Client
from werkzeug.security import generate_password_hash, check_password_hash
import json
import csv
import io
import os
import secrets
import base64
from datetime import datetime, timedelta, timezone
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from io import BytesIO
from dotenv import load_dotenv
import httpx
import secrets
import base64
import hashlib

# ========== CARREGAR VARIÁVEIS DE AMBIENTE ==========
load_dotenv()

# ========== CONFIGURAÇÃO FLASK ==========
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'urbana-secure-key-2026')
app.config['SESSION_TYPE'] = 'filesystem'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=30)
app.config['REMEMBER_COOKIE_DURATION'] = timedelta(days=30)

# ========== SUPABASE CLIENT ==========
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_ANON_KEY = os.getenv('SUPABASE_ANON_KEY')
SUPABASE_SERVICE_KEY = os.getenv('SUPABASE_SERVICE_KEY', '')

if not SUPABASE_URL or not SUPABASE_ANON_KEY:
    raise ValueError("SUPABASE_URL e SUPABASE_ANON_KEY devem ser configurados no .env")

# Criar cliente Supabase base
supabase_base_client = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)

# Cliente admin se tiver service key
supabase_admin = None
if SUPABASE_SERVICE_KEY:
    supabase_admin = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)

# ========== USUÁRIO DEMO FIXO (SEM LOGIN) ==========
class DemoUser:
    def __init__(self):
        self.id = "demo_user_001"
        self.email = "demo@urbana.app"
        self.name = "Usuário Demo"
        self.organization = "URBANA System"
        self.is_authenticated = True
        self.is_active = True

CURRENT_USER = DemoUser()

# ========== CONTEXT PROCESSOR ==========
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
    
    # ✅ IMPORTANTE: Retorna o objeto, não uma função
    return {
        'format_date': format_date,
        'format_number': format_number,
        'current_user': CURRENT_USER  # ← Sem lambda, sem função
    }
    
    def format_number(value, decimals=0):
        if value is None:
            return "N/A"
        try:
            if isinstance(value, str):
                try:
                    value = float(value.replace(',', '.'))
                except:
                    return value
            
            if decimals == 0:
                return f"{int(value):,}".replace(",", ".")
            else:
                return f"{float(value):,.{decimals}f}".replace(",", ".")
        except Exception as e:
            print(f"DEBUG: Erro ao formatar número: {e}")
            return str(value)
    
    # Retorna o usuário demo para os templates
    return dict(format_date=format_date, format_number=format_number, current_user=lambda: CURRENT_USER)

# ========== MIDDLEWARE ==========
@app.before_request
def before_request():
    """Configurar cliente Supabase antes de cada request"""
    try:
        g.supabase = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)
        g.current_user = CURRENT_USER
    except Exception as e:
        print(f"⚠️ Erro no before_request: {e}")
        g.supabase = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)
        g.current_user = CURRENT_USER

# ========== FUNÇÕES AUXILIARES ==========

def get_building_type_label(building_type):
    types = {
        'low': 'Baixa Densidade',
        'medium': 'Média Densidade',
        'high': 'Alta Densidade'
    }
    return types.get(building_type, building_type)

def create_consumption_chart(total_water, total_energy, water_per_capita, energy_per_capita):
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4))
    
    resources = ['Água', 'Energia']
    values = [total_water, total_energy]
    colors_bars = ['#1565C0', '#2E7D32']
    
    bars = ax1.bar(resources, values, color=colors_bars)
    ax1.set_title('Consumo Total Diário', fontweight='bold')
    ax1.set_ylabel('Unidades/dia')
    ax1.grid(True, alpha=0.3)
    
    for bar, value in zip(bars, values):
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., height + max(values)*0.02,
                f'{value:,.0f}', ha='center', va='bottom')
    
    per_capita = [water_per_capita, energy_per_capita]
    
    ax2.pie(per_capita, labels=['Água per capita', 'Energia per capita'],
            colors=['#64B5F6', '#A5D6A7'], autopct='%1.1f%%', startangle=90)
    ax2.set_title('Distribuição per Capita', fontweight='bold')
    
    plt.tight_layout()
    return fig

def create_comparison_chart(areas, water_values, energy_values):
    if not areas:
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.text(0.5, 0.5, 'Sem dados para exibir', 
                ha='center', va='center', fontsize=14)
        ax.set_title('Consumo Comparativo por Localidade', fontweight='bold')
        return fig
    
    fig, ax = plt.subplots(figsize=(10, 6))
    
    x = range(len(areas))
    width = 0.35
    
    bars1 = ax.bar([i - width/2 for i in x], water_values, width, label='Água (L/dia)', color='#1565C0')
    bars2 = ax.bar([i + width/2 for i in x], energy_values, width, label='Energia (kWh/dia)', color='#2E7D32')
    
    ax.set_xlabel('Localidades')
    ax.set_ylabel('Consumo')
    ax.set_title('Consumo Comparativo por Localidade', fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(areas, rotation=45, ha='right')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    for bars in [bars1, bars2]:
        for bar in bars:
            height = bar.get_height()
            if height > 0:
                ax.text(bar.get_x() + bar.get_width()/2., height,
                       f'{height:,.0f}', ha='center', va='bottom', fontsize=8)
    
    plt.tight_layout()
    return fig

# ========== ROTAS ==========

@app.route("/")
def index():
    """Página inicial - redireciona para dashboard sem login"""
    return redirect(url_for('dashboard'))

@app.route("/login")
def login():
    """Redireciona para dashboard (login desativado)"""
    return redirect(url_for('dashboard'))

@app.route("/register")
def register():
    """Redireciona para dashboard (registro desativado)"""
    return redirect(url_for('dashboard'))

@app.route("/auth/google")
def auth_google():
    """Redireciona para dashboard (Google desativado)"""
    return redirect(url_for('dashboard'))

@app.route("/auth/callback")
def auth_callback():
    """Redireciona para dashboard (callback desativado)"""
    return redirect(url_for('dashboard'))

@app.route("/logout")
def logout():
    """Logout - apenas limpa sessão"""
    session.clear()
    flash('Você saiu do modo demo.', 'info')
    return redirect(url_for('dashboard'))

@app.route("/forgot-password")
def forgot_password():
    return redirect(url_for('dashboard'))

@app.route("/resend-confirmation")
def resend_confirmation():
    return redirect(url_for('dashboard'))

@app.route("/terms")
def terms():
    return render_template("terms.html")

@app.route("/privacy")
def privacy():
    return render_template("privacy.html")

# ========== DASHBOARD ==========
@app.route("/dashboard")
def dashboard():
    try:
        supabase = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)
        
        try:
            response = supabase.table('simulations')\
                .select('*')\
                .order('created_at', desc=True)\
                .execute()
            
            simulations = response.data if response.data else []
        except Exception as e:
            print(f"⚠️ Erro ao buscar simulações: {e}")
            simulations = []
        
        processed_simulations = []
        for sim in simulations:
            sim_copy = sim.copy()
            if 'created_at' in sim_copy and isinstance(sim_copy['created_at'], str):
                try:
                    date_str = sim_copy['created_at']
                    if 'Z' in date_str:
                        date_str = date_str.replace('Z', '+00:00')
                    sim_copy['created_at_obj'] = datetime.fromisoformat(date_str)
                except Exception as e:
                    print(f"⚠️ Erro ao converter data: {e}")
                    sim_copy['created_at_obj'] = None
            processed_simulations.append(sim_copy)
        
        if processed_simulations:
            total_population = sum(s.get('population', 0) for s in processed_simulations)
            avg_water = sum(s.get('total_water', 0) for s in processed_simulations) / len(processed_simulations)
            avg_energy = sum(s.get('total_energy', 0) for s in processed_simulations) / len(processed_simulations)
            avg_area = sum(s.get('area_size', 0) for s in processed_simulations) / len(processed_simulations)
        else:
            total_population = 0
            avg_water = 0
            avg_energy = 0
            avg_area = 0
        
        stats = {
            'total_simulations': len(processed_simulations),
            'total_population': total_population,
            'avg_water': round(avg_water, 2),
            'avg_energy': round(avg_energy, 2),
            'avg_area': round(avg_area, 2)
        }
        
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
        
        trend_data = {}
        seven_days_ago = datetime.now(timezone.utc) - timedelta(days=7)
        
        for sim in processed_simulations:
            if 'created_at_obj' in sim and sim['created_at_obj']:
                created_at = sim['created_at_obj']
                if created_at >= seven_days_ago:
                    date_str = created_at.strftime('%Y-%m-%d')
                    if date_str not in trend_data:
                        trend_data[date_str] = {'count': 0, 'water': 0, 'energy': 0}
                    trend_data[date_str]['count'] += 1
                    trend_data[date_str]['water'] += sim.get('total_water', 0)
                    trend_data[date_str]['energy'] += sim.get('total_energy', 0)
        
        dates = sorted(trend_data.keys())
        sim_counts = [trend_data[date]['count'] for date in dates]
        
        trend_water = []
        trend_energy = []
        for date in dates:
            count = trend_data[date]['count']
            if count > 0:
                trend_water.append(trend_data[date]['water'] / count)
                trend_energy.append(trend_data[date]['energy'] / count)
            else:
                trend_water.append(0)
                trend_energy.append(0)
        
        formatted_dates = []
        for date_str in dates:
            try:
                date_obj = datetime.strptime(date_str, '%Y-%m-%d')
                formatted_dates.append(date_obj.strftime('%d/%m'))
            except:
                formatted_dates.append(date_str)
        
        type_distribution = {}
        for sim in processed_simulations:
            tipo = sim.get('building_type', 'unknown')
            if tipo not in type_distribution:
                type_distribution[tipo] = {'count': 0, 'water': 0, 'energy': 0}
            type_distribution[tipo]['count'] += 1
            type_distribution[tipo]['water'] += sim.get('total_water', 0)
            type_distribution[tipo]['energy'] += sim.get('total_energy', 0)
        
        tipo_labels = []
        tipo_counts = []
        tipo_water = []
        tipo_energy = []
        
        for tipo, data in type_distribution.items():
            tipo_labels.append(get_building_type_label(tipo))
            tipo_counts.append(data['count'])
            if data['count'] > 0:
                tipo_water.append(data['water'] / data['count'])
                tipo_energy.append(data['energy'] / data['count'])
            else:
                tipo_water.append(0)
                tipo_energy.append(0)
        
        return render_template(
            "dashboard.html",
            simulations=processed_simulations,
            stats=stats,
            areas=json.dumps(areas),
            water_values=json.dumps(water_values),
            energy_values=json.dumps(energy_values),
            dates=json.dumps(formatted_dates),
            sim_counts=json.dumps(sim_counts),
            trend_water=json.dumps(trend_water),
            trend_energy=json.dumps(trend_energy),
            tipo_labels=json.dumps(tipo_labels),
            tipo_counts=json.dumps(tipo_counts),
            tipo_water=json.dumps(tipo_water),
            tipo_energy=json.dumps(tipo_energy)
        )
        
    except Exception as e:
        print(f"❌ Erro crítico no dashboard: {e}")
        import traceback
        traceback.print_exc()
        flash('Erro ao carregar dashboard.', 'warning')
        return render_template("dashboard.html", simulations=[], stats={'total_simulations': 0, 'total_population': 0, 'avg_water': 0, 'avg_energy': 0, 'avg_area': 0})

# ========== ROTAS DE SIMULAÇÃO ==========
@app.route("/simulate", methods=["GET"])
def simulate_form():
    return render_template("index.html")

@app.route("/calculate", methods=["POST"])
def calculate():
    try:
        supabase = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)
        
        area_name = request.form.get("area_name", "Área não nomeada")
        population = int(request.form.get("population", 0))
        area_size = float(request.form.get("area_size", 0))
        building_type = request.form.get("building_type", "medium")

        water_per_person = 120
        energy_per_person = 2.5

        total_water = population * water_per_person
        total_energy = population * energy_per_person
        
        density = population / area_size if area_size > 0 else 0
        water_per_capita = water_per_person
        energy_per_capita = energy_per_person

        simulation_data = {
            'user_id': CURRENT_USER.id,
            'area_name': area_name,
            'population': population,
            'area_size': area_size,
            'building_type': building_type,
            'total_water': total_water,
            'total_energy': total_energy,
            'density': density,
            'water_per_capita': water_per_capita,
            'energy_per_capita': energy_per_capita,
            'created_at': datetime.now(timezone.utc).isoformat()
        }
        
        response = supabase.table('simulations').insert(simulation_data).execute()
        
        if response.data:
            sim_id = response.data[0]['id']
            flash('Simulação criada com sucesso!', 'success')
            return redirect(url_for('view_report', sim_id=sim_id))
        else:
            flash('Erro ao salvar simulação.', 'danger')
            return redirect(url_for('simulate_form'))
    
    except Exception as e:
        print(f"❌ Erro na simulação: {e}")
        flash(f'Erro ao processar simulação: {str(e)[:100]}', 'danger')
        return redirect(url_for('simulate_form'))

@app.route("/report/<int:sim_id>")
def view_report(sim_id):
    try:
        supabase = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)
            
        response = supabase.table('simulations')\
            .select('*')\
            .eq('id', sim_id)\
            .execute()
        
        if not response.data:
            flash('Simulação não encontrada.', 'danger')
            return redirect(url_for('dashboard'))
        
        simulation = response.data[0]
        
        return render_template(
            "report.html",
            sim_id=simulation['id'],
            area_name=simulation.get('area_name', 'N/A'),
            population=simulation.get('population', 0),
            area_size=simulation.get('area_size', 0),
            building_type=simulation.get('building_type', 'medium'),
            total_water=simulation.get('total_water', 0),
            total_energy=simulation.get('total_energy', 0),
            density=simulation.get('density', 0),
            water_per_capita=simulation.get('water_per_capita', 0),
            energy_per_capita=simulation.get('energy_per_capita', 0),
            current_date=datetime.now().strftime("%d/%m/%Y %H:%M")
        )
        
    except Exception as e:
        print(f"⚠️ Erro ao buscar simulação: {e}")
        flash('Erro ao carregar relatório.', 'danger')
        return redirect(url_for('dashboard'))

# ========== ROTAS DE VISUALIZAÇÃO ==========
@app.route("/my-simulations")
def my_simulations():
    try:
        supabase = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)
            
        response = supabase.table('simulations')\
            .select('*')\
            .order('created_at', desc=True)\
            .execute()
        
        simulations = response.data if response.data else []
        return render_template("my_simulations.html", simulations=simulations)
        
    except Exception as e:
        print(f"⚠️ Erro ao buscar simulações: {e}")
        flash('Erro ao carregar simulações.', 'danger')
        return redirect(url_for('dashboard'))

# ========== ROTAS DE API ==========
@app.route("/api/simulation/<int:sim_id>")
def get_simulation_detail(sim_id):
    try:
        supabase = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)
            
        response = supabase.table('simulations')\
            .select('*')\
            .eq('id', sim_id)\
            .execute()
        
        if not response.data:
            return jsonify({"error": "Simulação não encontrada"}), 404
        
        simulation = response.data[0]
        
        return jsonify({
            'id': simulation['id'],
            'area_name': simulation.get('area_name', ''),
            'population': simulation.get('population', 0),
            'area_size': simulation.get('area_size', 0),
            'building_type': simulation.get('building_type', ''),
            'total_water': simulation.get('total_water', 0),
            'total_energy': simulation.get('total_energy', 0),
            'density': simulation.get('density', 0),
            'water_per_capita': simulation.get('water_per_capita', 0),
            'energy_per_capita': simulation.get('energy_per_capita', 0),
            'created_at': simulation.get('created_at', '')
        })
        
    except Exception as e:
        print(f"⚠️ Erro na API: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/delete/<int:sim_id>", methods=["DELETE"])
def delete_simulation(sim_id):
    try:
        supabase = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)
        
        delete_response = supabase.table('simulations')\
            .delete()\
            .eq('id', sim_id)\
            .execute()
        
        return '', 204
        
    except Exception as e:
        print(f"⚠️ Erro ao deletar: {e}")
        return jsonify({"error": str(e)}), 500

# ========== ROTAS DE EXPORTAÇÃO ==========
@app.route("/export/csv")
def export_csv():
    """Exportar simulações como CSV"""
    try:
        supabase = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)
            
        response = supabase.table('simulations')\
            .select('*')\
            .order('created_at', desc=True)\
            .execute()
        
        simulations = response.data if response.data else []
        
        if not simulations:
            flash('Nenhuma simulação encontrada para exportar.', 'warning')
            return redirect(url_for('dashboard'))
        
        output = io.StringIO()
        writer = csv.writer(output, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        
        output.write('\ufeff')
        
        writer.writerow(['ID', 'Local', 'População', 'Área (km²)', 'Tipo de Construção', 
                         'Densidade (hab/km²)', 'Água (L/dia)', 'Energia (kWh/dia)',
                         'Água per capita (L/dia)', 'Energia per capita (kWh/dia)', 'Data de Criação'])
        
        for sim in simulations:
            writer.writerow([
                sim['id'],
                sim.get('area_name', ''),
                sim.get('population', 0),
                f"{sim.get('area_size', 0):.2f}",
                get_building_type_label(sim.get('building_type', '')),
                f"{sim.get('density', 0):.2f}" if sim.get('density') else "0.00",
                f"{sim.get('total_water', 0):,.0f}",
                f"{sim.get('total_energy', 0):.2f}",
                f"{sim.get('water_per_capita', 0):.1f}",
                f"{sim.get('energy_per_capita', 0):.2f}",
                datetime.fromisoformat(sim['created_at'].replace('Z', '+00:00')).strftime('%d/%m/%Y %H:%M') 
                if sim.get('created_at') else ""
            ])
        
        output.seek(0)
        response = make_response(output.getvalue())
        response.headers['Content-Disposition'] = \
            f'attachment; filename=urbana_simulacoes_{datetime.now().strftime("%Y%m%d_%H%M")}.csv'
        response.headers['Content-Type'] = 'text/csv; charset=utf-8'
        
        return response
        
    except Exception as e:
        print(f"⚠️ Erro ao exportar CSV: {e}")
        flash(f'Erro ao exportar CSV: {str(e)[:100]}', 'danger')
        return redirect(url_for('dashboard'))

@app.route("/export/csv/<int:sim_id>")
def export_csv_single(sim_id):
    """Exportar uma simulação específica como CSV"""
    try:
        supabase = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)
            
        response = supabase.table('simulations')\
            .select('*')\
            .eq('id', sim_id)\
            .execute()
        
        if not response.data:
            flash('Simulação não encontrada.', 'danger')
            return redirect(url_for('dashboard'))
        
        simulation = response.data[0]
        
        output = io.StringIO()
        writer = csv.writer(output, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        
        output.write('\ufeff')
        
        writer.writerow(['Campo', 'Valor'])
        
        writer.writerow(['ID da Simulação', simulation['id']])
        writer.writerow(['Local', simulation.get('area_name', '')])
        writer.writerow(['População', f"{simulation.get('population', 0):,} habitantes"])
        writer.writerow(['Área', f"{simulation.get('area_size', 0):.2f} km²"])
        writer.writerow(['Tipo de Construção', get_building_type_label(simulation.get('building_type', ''))])
        writer.writerow(['Densidade', f"{simulation.get('density', 0):.2f} hab/km²" if simulation.get('density') else "N/A"])
        writer.writerow(['Consumo Diário de Água', f"{simulation.get('total_water', 0):,.0f} litros"])
        writer.writerow(['Consumo Diário de Energia', f"{simulation.get('total_energy', 0):,.2f} kWh"])
        writer.writerow(['Água per Capita', f"{simulation.get('water_per_capita', 0):.1f} L/dia/pessoa"])
        writer.writerow(['Energia per Capita', f"{simulation.get('energy_per_capita', 0):.2f} kWh/dia/pessoa"])
        writer.writerow(['Data da Simulação', 
                         datetime.fromisoformat(simulation['created_at'].replace('Z', '+00:00')).strftime('%d/%m/%Y %H:%M') 
                         if simulation.get('created_at') else "N/A"])
        writer.writerow(['Data de Exportação', datetime.now().strftime('%d/%m/%Y %H:%M')])
        
        output.seek(0)
        response = make_response(output.getvalue())
        response.headers['Content-Disposition'] = \
            f'attachment; filename=urbana_simulacao_{simulation.get("area_name", "simulacao").replace(" ", "_")}_{datetime.now().strftime("%Y%m%d")}.csv'
        response.headers['Content-Type'] = 'text/csv; charset=utf-8'
        
        return response
        
    except Exception as e:
        print(f"⚠️ Erro ao exportar CSV: {e}")
        flash(f'Erro ao exportar CSV: {str(e)[:100]}', 'danger')
        return redirect(url_for('view_report', sim_id=sim_id))

@app.route("/export/pdf/<int:sim_id>")
def export_pdf(sim_id):
    """Exportar relatório de simulação como PDF"""
    try:
        supabase = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)
            
        response = supabase.table('simulations')\
            .select('*')\
            .eq('id', sim_id)\
            .execute()
        
        if not response.data:
            flash('Simulação não encontrada.', 'danger')
            return redirect(url_for('dashboard'))
        
        simulation = response.data[0]
        
        buffer = BytesIO()
        
        doc = SimpleDocTemplate(
            buffer, 
            pagesize=A4,
            rightMargin=40, 
            leftMargin=40, 
            topMargin=40, 
            bottomMargin=40
        )
        
        styles = getSampleStyleSheet()
        
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=16,
            textColor=colors.HexColor('#1565C0'),
            spaceAfter=20
        )
        
        subtitle_style = ParagraphStyle(
            'CustomSubtitle',
            parent=styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#2E7D32'),
            spaceAfter=10
        )
        
        normal_style = styles['Normal']
        
        story = []
        
        story.append(Paragraph("Relatório de Simulação URBANA", title_style))
        story.append(Paragraph(f"Simulação ID: {simulation['id']} • Data: {datetime.now().strftime('%d/%m/%Y')}", styles['Normal']))
        story.append(Spacer(1, 20))
        
        story.append(Paragraph("1. Informações da Simulação", subtitle_style))
        
        sim_data = [
            ['Local:', simulation.get('area_name', 'N/A')],
            ['População:', f"{simulation.get('population', 0):,} habitantes"],
            ['Área:', f"{simulation.get('area_size', 0):.2f} km²"],
            ['Tipo de Construção:', get_building_type_label(simulation.get('building_type', ''))],
            ['Densidade:', f"{simulation.get('density', 0):.2f} hab/km²" if simulation.get('density') else "N/A"],
            ['Data da Simulação:', 
             datetime.fromisoformat(simulation['created_at'].replace('Z', '+00:00')).strftime('%d/%m/%Y %H:%M') 
             if simulation.get('created_at') else "N/A"]
        ]
        
        sim_table = Table(sim_data, colWidths=[150, 300])
        sim_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#E3F2FD')),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#1565C0')),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('PADDING', (0, 0), (-1, -1), 6),
        ]))
        
        story.append(sim_table)
        story.append(Spacer(1, 20))
        
        story.append(Paragraph("2. Métricas de Consumo", subtitle_style))
        
        consumption_data = [
            ['Recurso', 'Consumo Total Diário', 'Consumo per Capita'],
            ['Água', f"{simulation.get('total_water', 0):,.0f} litros/dia", f"{simulation.get('water_per_capita', 0):.1f} litros/dia/pessoa"],
            ['Energia', f"{simulation.get('total_energy', 0):,.0f} kWh/dia", f"{simulation.get('energy_per_capita', 0):.2f} kWh/dia/pessoa"]
        ]
        
        consumption_table = Table(consumption_data, colWidths=[100, 150, 200])
        consumption_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1565C0')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('PADDING', (0, 0), (-1, -1), 6),
            ('BACKGROUND', (0, 1), (0, -1), colors.HexColor('#E8F5E8')),
            ('BACKGROUND', (1, 1), (1, -1), colors.HexColor('#E3F2FD')),
            ('BACKGROUND', (2, 1), (2, -1), colors.HexColor('#FFF3E0')),
        ]))
        
        story.append(consumption_table)
        story.append(Spacer(1, 20))
        
        story.append(Paragraph("3. Análise e Recomendações", subtitle_style))
        
        density_val = simulation.get('density', 0)
        density_class = "Baixa" if density_val < 50 else "Média" if density_val < 150 else "Alta"
        
        recommendations = {
            'low': [
                "Considerar incentivos para aumento de densidade",
                "Otimizar redes de distribuição",
                "Implementar sistemas de reuso de água"
            ],
            'medium': [
                "Manter planejamento de crescimento ordenado",
                "Expandir infraestrutura de forma proporcional",
                "Implementar sistemas de energia renovável"
            ],
            'high': [
                "Otimizar sistemas existentes",
                "Considerar soluções verticais de infraestrutura",
                "Implementar tecnologias de eficiência energética"
            ]
        }
        
        rec_list = recommendations.get(simulation.get('building_type', 'medium'), [])
        
        analysis_text = f"""
        <b>Classificação de Densidade:</b> {density_class}<br/>
        <b>Consumo total estimado:</b> {simulation.get('total_water', 0):,.0f} litros de água e {simulation.get('total_energy', 0):,.0f} kWh de energia por dia.<br/>
        <br/>
        <b>Recomendações para planejamento urbano:</b>
        """
        
        story.append(Paragraph(analysis_text, normal_style))
        
        for i, rec in enumerate(rec_list, 1):
            story.append(Paragraph(f"{i}. {rec}", normal_style))
        
        story.append(Spacer(1, 20))
        
        footer_text = f"""
        <i>Relatório gerado por: {CURRENT_USER.name} ({CURRENT_USER.organization})<br/>
        Data de geração: {datetime.now().strftime('%d/%m/%Y %H:%M')}<br/>
        Sistema URBANA - Planejamento Urbano Inteligente</i>
        """
        story.append(Paragraph(footer_text, styles['Italic']))
        
        doc.build(story)
        
        buffer.seek(0)
        response = make_response(buffer.getvalue())
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = \
            f'inline; filename=urbana_relatorio_{simulation.get("area_name", "simulacao").replace(" ", "_")}_{datetime.now().strftime("%Y%m%d_%H%M")}.pdf'
        
        return response
        
    except Exception as e:
        print(f"❌ Erro ao gerar PDF: {e}")
        flash(f'Erro ao gerar PDF: {str(e)[:100]}', 'danger')
        return redirect(url_for('view_report', sim_id=sim_id))

@app.route("/export/pdf")
def export_all_pdf():
    """Exportar todas as simulações como PDF"""
    try:
        supabase = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)
            
        response = supabase.table('simulations')\
            .select('*')\
            .order('created_at', desc=True)\
            .execute()
        
        simulations = response.data if response.data else []
        
        if not simulations:
            flash('Nenhuma simulação encontrada para exportar.', 'warning')
            return redirect(url_for('my_simulations'))
        
        buffer = BytesIO()
        
        doc = SimpleDocTemplate(
            buffer, 
            pagesize=A4,
            rightMargin=40, 
            leftMargin=40, 
            topMargin=40, 
            bottomMargin=40
        )
        
        styles = getSampleStyleSheet()
        
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=16,
            textColor=colors.HexColor('#1565C0'),
            spaceAfter=20
        )
        
        story = []
        
        story.append(Paragraph("Relatório Consolidado de Simulações URBANA", title_style))
        story.append(Paragraph(f"Usuário: {CURRENT_USER.name} • Data: {datetime.now().strftime('%d/%m/%Y')}", styles['Normal']))
        story.append(Spacer(1, 20))
        
        total_pop = sum(s.get('population', 0) for s in simulations)
        total_water = sum(s.get('total_water', 0) for s in simulations)
        total_energy = sum(s.get('total_energy', 0) for s in simulations)
        total_area = sum(s.get('area_size', 0) for s in simulations)
        
        summary_data = [
            ['Total de Simulações:', str(len(simulations))],
            ['População Total:', f"{total_pop:,} habitantes"],
            ['Área Total:', f"{total_area:.2f} km²"],
            ['Consumo Total Diário de Água:', f"{total_water:,.0f} litros"],
            ['Consumo Total Diário de Energia:', f"{total_energy:,.0f} kWh"],
            ['Data de Geração:', datetime.now().strftime('%d/%m/%Y %H:%M')]
        ]
        
        summary_table = Table(summary_data, colWidths=[200, 250])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#E3F2FD')),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('PADDING', (0, 0), (-1, -1), 6),
        ]))
        
        story.append(summary_table)
        story.append(Spacer(1, 20))
        
        story.append(Paragraph("Simulações Detalhadas", styles['Heading2']))
        
        sims_data = [['ID', 'Local', 'População', 'Área (km²)', 'Água (L/dia)', 'Energia (kWh/dia)', 'Data']]
        
        for sim in simulations:
            sims_data.append([
                str(sim['id']),
                sim.get('area_name', '')[:20] + '...' if len(sim.get('area_name', '')) > 20 else sim.get('area_name', ''),
                str(sim.get('population', 0)),
                f"{sim.get('area_size', 0):.2f}",
                f"{sim.get('total_water', 0):,.0f}",
                f"{sim.get('total_energy', 0):,.0f}",
                datetime.fromisoformat(sim['created_at'].replace('Z', '+00:00')).strftime('%d/%m/%y') 
                if sim.get('created_at') else ''
            ])
        
        sims_table = Table(sims_data, repeatRows=1, colWidths=[40, 100, 60, 60, 80, 80, 60])
        sims_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1565C0')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('PADDING', (0, 0), (-1, -1), 4),
            ('ALIGN', (2, 1), (5, -1), 'RIGHT'),
            ('ALIGN', (0, 1), (0, -1), 'CENTER'),
        ]))
        
        story.append(sims_table)
        
        story.append(Spacer(1, 30))
        footer = Paragraph(f"<i>Relatório consolidado gerado por {CURRENT_USER.name} • Sistema URBANA</i>", styles['Italic'])
        story.append(footer)
        
        doc.build(story)
        
        buffer.seek(0)
        response = make_response(buffer.getvalue())
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = \
            f'inline; filename=urbana_consolidado_{datetime.now().strftime("%Y%m%d")}.pdf'
        
        return response
        
    except Exception as e:
        print(f"❌ Erro ao gerar PDF consolidado: {e}")
        flash(f'Erro ao gerar PDF: {str(e)[:100]}', 'danger')
        return redirect(url_for('my_simulations'))

# ========== ROTAS DE PERFIL ==========
@app.route("/profile")
def profile():
    try:
        supabase = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)
            
        user_response = supabase.table('users')\
            .select('*')\
            .eq('id', CURRENT_USER.id)\
            .execute()
        
        user_data = user_response.data[0] if user_response.data else {}
        
        sim_response = supabase.table('simulations')\
            .select('id, area_name, population, total_water, total_energy, created_at')\
            .order('created_at', desc=True)\
            .limit(1)\
            .execute()
        
        simulations = sim_response.data
        
        total_sim_response = supabase.table('simulations')\
            .select('id', count='exact')\
            .execute()
        
        total_simulations = total_sim_response.count if hasattr(total_sim_response, 'count') else 0
        
        user_stats = {
            'total_simulations': total_simulations,
            'account_age': 0,
            'last_simulation': simulations[0] if simulations else None,
            'user_data': {
                'email': CURRENT_USER.email,
                'name': CURRENT_USER.name,
                'organization': CURRENT_USER.organization
            }
        }
        return render_template("profile.html", user_stats=user_stats)
        
    except Exception as e:
        print(f"⚠️ Erro no perfil: {e}")
        flash('Erro ao carregar perfil.', 'danger')
        return redirect(url_for('dashboard'))

@app.route("/profile/edit", methods=["GET", "POST"])
def edit_profile():
    if request.method == "POST":
        flash('Edição de perfil desativada no modo demo.', 'info')
        return redirect(url_for('profile'))
    
    return render_template("edit_profile.html")

# ========== CONFIGURAÇÃO ==========
def setup_supabase():
    """Configurar Supabase"""
    try:
        print("🔧 Testando conexão com Supabase...")
        supabase_test = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)
        response = supabase_test.table('users').select('count', count='exact').limit(1).execute()
        print(f"✅ Conexão com Supabase estabelecida")
        print(f"📊 Tabela 'users' tem {response.count or 0} registros")
        return True
    except Exception as e:
        print(f"❌ Erro ao conectar com Supabase: {e}")
        return False

# ========== EXECUÇÃO ==========
if __name__ == "__main__":
    print("=" * 60)
    print("🚀 URBANA - Sistema de Planejamento Urbano (Modo DEMO - Sem Login)")
    print("=" * 60)

    if not os.getenv('SUPABASE_URL') or not os.getenv('SUPABASE_ANON_KEY'):
        print("❌ ERRO: Variáveis de ambiente não configuradas")
        print("Configure as variáveis no Render:")
        print("SUPABASE_URL, SUPABASE_ANON_KEY, SECRET_KEY")
        exit(1)

    if setup_supabase():
        print("✅ Sistema pronto para uso - Sem necessidade de login")
        print("📍 Acesse diretamente: /dashboard")
        print("=" * 60)

        port = int(os.environ.get('PORT', 5000))
        app.run(debug=False, host='0.0.0.0', port=port)
    else:
        print("❌ Falha ao conectar com Supabase")
