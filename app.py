from flask import Flask, render_template, request, jsonify, make_response, redirect, url_for, flash, session, g
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

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'urbana-demo-key-2026')
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=30)

# Supabase
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_ANON_KEY = os.getenv('SUPABASE_ANON_KEY')
supabase = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)

# Usuário Demo
class DemoUser:
    def __init__(self):
        self.id = "demo_user"
        self.email = "demo@urbana.app"
        self.name = "Usuário Demo"
        self.organization = "URBANA System"
        self.is_authenticated = True
        self.is_active = True

CURRENT_USER = DemoUser()

@app.before_request
def before_request():
    g.supabase = supabase
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
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    
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
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    
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

# ========== CONTEXT PROCESSOR ==========
@app.context_processor
def utility_processor():
    def format_date(date_value, format_str='%d/%m/%Y'):
        if not date_value:
            return "N/A"
        try:
            if isinstance(date_value, str):
                date_value = date_value.replace('Z', '+00:00')
                if '.' in date_value and '+' in date_value:
                    date_value = date_value.split('.')[0] + '+' + date_value.split('+')[1]
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
            if isinstance(value, str):
                try:
                    value = float(value.replace(',', '.'))
                except:
                    return value
            
            if decimals == 0:
                return f"{int(value):,}".replace(",", ".")
            else:
                return f"{float(value):,.{decimals}f}".replace(",", ".")
        except:
            return str(value)
    
    return {
        'format_date': format_date,
        'format_number': format_number,
        'current_user': lambda: CURRENT_USER,
        'get_building_type_label': get_building_type_label
    }

# ========== ROTAS PRINCIPAIS ==========
@app.route("/")
def index():
    return redirect(url_for('dashboard'))

@app.route("/dashboard")
def dashboard():
    try:
        response = supabase.table('simulations').select('*').order('created_at', desc=True).execute()
        simulations = response.data if response.data else []
        
        processed_simulations = []
        for sim in simulations:
            sim_copy = sim.copy()
            if sim.get('created_at'):
                try:
                    sim_copy['created_at_obj'] = datetime.fromisoformat(sim['created_at'].replace('Z', '+00:00'))
                except:
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
        
        # Dados por área
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
        
        # Distribuição por tipo
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
        print(f"❌ Erro no dashboard: {e}")
        flash('Erro ao carregar dashboard.', 'danger')
        return render_template("dashboard.html", simulations=[], stats={})

@app.route("/simulate", methods=["GET"])
def simulate_form():
    return render_template("index.html")

@app.route("/calculate", methods=["POST"])
def calculate():
    try:
        area_name = request.form.get("area_name", "Área não nomeada")
        population = int(request.form.get("population", 0))
        area_size = float(request.form.get("area_size", 0))
        building_type = request.form.get("building_type", "medium")

        water_per_person = 120
        energy_per_person = 2.5

        total_water = population * water_per_person
        total_energy = population * energy_per_person
        density = population / area_size if area_size > 0 else 0

        simulation_data = {
            'user_id': CURRENT_USER.id,
            'area_name': area_name,
            'population': population,
            'area_size': area_size,
            'building_type': building_type,
            'total_water': total_water,
            'total_energy': total_energy,
            'density': density,
            'water_per_capita': water_per_person,
            'energy_per_capita': energy_per_person,
            'created_at': datetime.now(timezone.utc).isoformat()
        }
        
        response = supabase.table('simulations').insert(simulation_data).execute()
        
        if response.data:
            flash('✅ Simulação criada com sucesso!', 'success')
            return redirect(url_for('view_report', sim_id=response.data[0]['id']))
        else:
            flash('❌ Erro ao salvar simulação.', 'danger')
            return redirect(url_for('simulate_form'))
    
    except Exception as e:
        print(f"❌ Erro na simulação: {e}")
        flash(f'Erro ao processar simulação: {str(e)[:100]}', 'danger')
        return redirect(url_for('simulate_form'))

@app.route("/report/<int:sim_id>")
def view_report(sim_id):
    try:
        response = supabase.table('simulations').select('*').eq('id', sim_id).execute()
        
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
        print(f"❌ Erro no relatório: {e}")
        flash('Erro ao carregar relatório.', 'danger')
        return redirect(url_for('dashboard'))

@app.route("/my-simulations")
def my_simulations():
    try:
        response = supabase.table('simulations').select('*').order('created_at', desc=True).execute()
        simulations = response.data if response.data else []
        return render_template("my_simulations.html", simulations=simulations)
    except Exception as e:
        print(f"❌ Erro: {e}")
        flash('Erro ao carregar simulações.', 'danger')
        return redirect(url_for('dashboard'))

@app.route("/delete/<int:sim_id>", methods=["POST"])
def delete_simulation(sim_id):
    try:
        supabase.table('simulations').delete().eq('id', sim_id).execute()
        flash('Simulação deletada com sucesso!', 'success')
    except Exception as e:
        flash('Erro ao deletar simulação.', 'danger')
    return redirect(url_for('my_simulations'))

@app.route("/profile")
def profile():
    try:
        response = supabase.table('simulations').select('id', count='exact').execute()
        total_sims = len(response.data) if response.data else 0
        
        user_stats = {
            'total_simulations': total_sims,
            'account_age': 0,
            'last_simulation': None,
            'user_data': {
                'email': CURRENT_USER.email,
                'name': CURRENT_USER.name,
                'organization': CURRENT_USER.organization
            }
        }
        return render_template("profile.html", user_stats=user_stats)
    except Exception as e:
        return render_template("profile.html", user_stats={'total_simulations': 0})

@app.route("/terms")
def terms():
    return render_template("terms.html")

@app.route("/privacy")
def privacy():
    return render_template("privacy.html")

# ========== EXPORTAÇÕES ==========
@app.route("/export/csv")
def export_csv():
    try:
        response = supabase.table('simulations').select('*').order('created_at', desc=True).execute()
        simulations = response.data if response.data else []
        
        output = StringIO()
        output.write('\ufeff')
        writer = csv.writer(output, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        
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
                sim.get('created_at', '')[:10] if sim.get('created_at') else ""
            ])
        
        output.seek(0)
        response = make_response(output.getvalue())
        response.headers['Content-Disposition'] = f'attachment; filename=urbana_simulacoes_{datetime.now().strftime("%Y%m%d_%H%M")}.csv'
        response.headers['Content-Type'] = 'text/csv; charset=utf-8'
        return response
    except Exception as e:
        flash('Erro ao exportar CSV.', 'danger')
        return redirect(url_for('dashboard'))

@app.route("/export/csv/<int:sim_id>")
def export_csv_single(sim_id):
    try:
        response = supabase.table('simulations').select('*').eq('id', sim_id).execute()
        
        if not response.data:
            flash('Simulação não encontrada.', 'danger')
            return redirect(url_for('dashboard'))
        
        sim = response.data[0]
        
        output = StringIO()
        output.write('\ufeff')
        writer = csv.writer(output, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        
        writer.writerow(['Campo', 'Valor'])
        writer.writerow(['ID da Simulação', sim['id']])
        writer.writerow(['Local', sim.get('area_name', '')])
        writer.writerow(['População', f"{sim.get('population', 0):,} habitantes"])
        writer.writerow(['Área', f"{sim.get('area_size', 0):.2f} km²"])
        writer.writerow(['Tipo de Construção', get_building_type_label(sim.get('building_type', ''))])
        writer.writerow(['Data da Simulação', sim.get('created_at', '')[:10] if sim.get('created_at') else "N/A"])
        
        output.seek(0)
        response = make_response(output.getvalue())
        response.headers['Content-Disposition'] = f'attachment; filename=simulacao_{sim_id}_{datetime.now().strftime("%Y%m%d")}.csv'
        response.headers['Content-Type'] = 'text/csv; charset=utf-8'
        return response
    except Exception as e:
        flash('Erro ao exportar CSV.', 'danger')
        return redirect(url_for('view_report', sim_id=sim_id))

if __name__ == "__main__":
    print("=" * 60)
    print("🚀 URBANA - Sistema de Planejamento Urbano (Modo DEMO)")
    print("=" * 60)
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=False, host='0.0.0.0', port=port)
