"""
URBANA - Sistema de Planejamento Urbano
Modo DEMO - Sem autenticação
Arquivo organizado e otimizado
"""

from flask import Flask, render_template, request, jsonify, make_response, redirect, url_for, flash, session, g
from werkzeug.security import generate_password_hash, check_password_hash
from supabase import create_client, Client
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
from functools import wraps

# ============================================================
# CONFIGURAÇÃO INICIAL
# ============================================================

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'urbana-demo-key-2026')
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=30)

# ============================================================
# SUPABASE CLIENT
# ============================================================

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_ANON_KEY = os.getenv('SUPABASE_ANON_KEY')

if not SUPABASE_URL or not SUPABASE_ANON_KEY:
    raise ValueError("SUPABASE_URL e SUPABASE_ANON_KEY devem ser configurados no .env")

supabase_client = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)

# ============================================================
# USUÁRIO DEMO (SEM AUTENTICAÇÃO)
# ============================================================

class DemoUser:
    """Usuário padrão para modo demo"""
    def __init__(self):
        self.id = "demo_user"
        self.email = "demo@urbana.app"
        self.name = "Usuário Demo"
        self.organization = "URBANA System"
        self.is_authenticated = True
        self.is_active = True
    
    def get_id(self):
        return self.id

CURRENT_USER = DemoUser()

# ============================================================
# MIDDLEWARE
# ============================================================

@app.before_request
def before_request():
    """Configura cliente Supabase e usuário antes de cada requisição"""
    g.supabase = supabase_client
    g.current_user = CURRENT_USER

# ============================================================
# FUNÇÕES AUXILIARES
# ============================================================

def get_building_type_label(building_type):
    """Retorna o label formatado do tipo de construção"""
    types = {
        'low': 'Baixa Densidade',
        'medium': 'Média Densidade',
        'high': 'Alta Densidade'
    }
    return types.get(building_type, building_type)

def format_currency(value):
    """Formata valor como moeda"""
    try:
        return f"R$ {float(value):,.2f}".replace(",", "v").replace(".", ",").replace("v", ".")
    except:
        return f"R$ {value}"

# ============================================================
# CONTEXT PROCESSOR (VARIÁVEIS GLOBAIS PARA TEMPLATES)
# ============================================================

@app.context_processor
def utility_processor():
    def format_date(date_value, format_str='%d/%m/%Y'):
        if not date_value:
            return "N/A"
        try:
            if isinstance(date_value, str):
                date_value = date_value.replace('Z', '+00:00')
                if '.' in date_value:
                    date_value = date_value.split('.')[0] + date_value.split('+')[1]
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
        'format_currency': format_currency,
        'current_user': lambda: CURRENT_USER,
        'now': datetime.now()
    }

# ============================================================
# ROTAS PRINCIPAIS
# ============================================================

@app.route("/")
def index():
    """Página inicial - redireciona para dashboard"""
    return redirect(url_for('dashboard'))

@app.route("/dashboard")
def dashboard():
    """Dashboard principal com estatísticas e gráficos"""
    try:
        # Buscar todas as simulações
        response = supabase_client.table('simulations')\
            .select('*')\
            .order('created_at', desc=True)\
            .execute()
        
        simulations = response.data if response.data else []
        
        # Processar simulações para formato amigável
        processed = []
        for sim in simulations:
            sim_copy = sim.copy()
            if sim.get('created_at'):
                try:
                    sim_copy['created_at_obj'] = datetime.fromisoformat(
                        sim['created_at'].replace('Z', '+00:00')
                    )
                except:
                    sim_copy['created_at_obj'] = None
            processed.append(sim_copy)
        
        # Estatísticas gerais
        if processed:
            total_pop = sum(s.get('population', 0) for s in processed)
            stats = {
                'total_simulations': len(processed),
                'total_population': total_pop,
                'avg_water': round(sum(s.get('total_water', 0) for s in processed) / len(processed), 2),
                'avg_energy': round(sum(s.get('total_energy', 0) for s in processed) / len(processed), 2),
                'avg_area': round(sum(s.get('area_size', 0) for s in processed) / len(processed), 2)
            }
        else:
            stats = {'total_simulations': 0, 'total_population': 0, 'avg_water': 0, 'avg_energy': 0, 'avg_area': 0}
        
        # Dados por área (top 10)
        areas_data = {}
        for sim in processed:
            area = sim.get('area_name', 'Sem nome')
            if area not in areas_data:
                areas_data[area] = {'water': 0, 'energy': 0}
            areas_data[area]['water'] += sim.get('total_water', 0)
            areas_data[area]['energy'] += sim.get('total_energy', 0)
        
        areas = list(areas_data.keys())[:10]
        water_values = [areas_data[a]['water'] for a in areas]
        energy_values = [areas_data[a]['energy'] for a in areas]
        
        # Tendência dos últimos 7 dias
        trend_data = {}
        seven_days_ago = datetime.now(timezone.utc) - timedelta(days=7)
        
        for sim in processed:
            if sim.get('created_at_obj') and sim['created_at_obj'] >= seven_days_ago:
                date_str = sim['created_at_obj'].strftime('%Y-%m-%d')
                if date_str not in trend_data:
                    trend_data[date_str] = {'count': 0, 'water': 0, 'energy': 0}
                trend_data[date_str]['count'] += 1
                trend_data[date_str]['water'] += sim.get('total_water', 0)
                trend_data[date_str]['energy'] += sim.get('total_energy', 0)
        
        dates = sorted(trend_data.keys())
        sim_counts = [trend_data[d]['count'] for d in dates]
        trend_water = [trend_data[d]['water'] / trend_data[d]['count'] if trend_data[d]['count'] > 0 else 0 for d in dates]
        trend_energy = [trend_data[d]['energy'] / trend_data[d]['count'] if trend_data[d]['count'] > 0 else 0 for d in dates]
        
        # Distribuição por tipo de construção
        type_dist = {}
        for sim in processed:
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
            simulations=processed,
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
        print(f"❌ Erro no dashboard: {e}")
        flash('Erro ao carregar dashboard.', 'danger')
        return render_template("dashboard.html", simulations=[], stats={})

# ============================================================
# SIMULAÇÕES
# ============================================================

@app.route("/simulate", methods=["GET"])
def simulate_form():
    """Formulário de simulação"""
    return render_template("index.html")

@app.route("/calculate", methods=["POST"])
def calculate():
    """Calcula e salva nova simulação"""
    try:
        area_name = request.form.get("area_name", "Área não nomeada")
        population = int(request.form.get("population", 0))
        area_size = float(request.form.get("area_size", 0))
        building_type = request.form.get("building_type", "medium")
        
        # Constantes de consumo
        WATER_PER_PERSON = 120  # litros/dia
        ENERGY_PER_PERSON = 2.5  # kWh/dia
        
        total_water = population * WATER_PER_PERSON
        total_energy = population * ENERGY_PER_PERSON
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
            'water_per_capita': WATER_PER_PERSON,
            'energy_per_capita': ENERGY_PER_PERSON,
            'created_at': datetime.now(timezone.utc).isoformat()
        }
        
        response = supabase_client.table('simulations').insert(simulation_data).execute()
        
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
    """Visualiza relatório de uma simulação"""
    try:
        response = supabase_client.table('simulations')\
            .select('*')\
            .eq('id', sim_id)\
            .execute()
        
        if not response.data:
            flash('Simulação não encontrada.', 'danger')
            return redirect(url_for('dashboard'))
        
        sim = response.data[0]
        
        return render_template(
            "report.html",
            sim_id=sim['id'],
            area_name=sim.get('area_name', 'N/A'),
            population=sim.get('population', 0),
            area_size=sim.get('area_size', 0),
            building_type=sim.get('building_type', 'medium'),
            total_water=sim.get('total_water', 0),
            total_energy=sim.get('total_energy', 0),
            density=sim.get('density', 0),
            water_per_capita=sim.get('water_per_capita', 0),
            energy_per_capita=sim.get('energy_per_capita', 0),
            current_date=datetime.now().strftime("%d/%m/%Y %H:%M")
        )
        
    except Exception as e:
        print(f"❌ Erro ao carregar relatório: {e}")
        flash('Erro ao carregar relatório.', 'danger')
        return redirect(url_for('dashboard'))

@app.route("/my-simulations")
def my_simulations():
    """Lista todas as simulações"""
    try:
        response = supabase_client.table('simulations')\
            .select('*')\
            .order('created_at', desc=True)\
            .execute()
        
        simulations = response.data if response.data else []
        return render_template("my_simulations.html", simulations=simulations)
        
    except Exception as e:
        print(f"❌ Erro ao listar simulações: {e}")
        flash('Erro ao carregar simulações.', 'danger')
        return redirect(url_for('dashboard'))

# ============================================================
# API
# ============================================================

@app.route("/api/simulation/<int:sim_id>")
def get_simulation_api(sim_id):
    """API para buscar detalhes de uma simulação"""
    try:
        response = supabase_client.table('simulations')\
            .select('*')\
            .eq('id', sim_id)\
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
            'density': sim.get('density', 0),
            'created_at': sim.get('created_at', '')
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/delete/<int:sim_id>", methods=["DELETE"])
def delete_simulation(sim_id):
    """Deleta uma simulação"""
    try:
        supabase_client.table('simulations').delete().eq('id', sim_id).execute()
        return '', 204
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ============================================================
# EXPORTAÇÕES
# ============================================================

@app.route("/export/csv")
def export_all_csv():
    """Exporta todas as simulações em CSV"""
    try:
        response = supabase_client.table('simulations')\
            .select('*')\
            .order('created_at', desc=True)\
            .execute()
        
        simulations = response.data if response.data else []
        
        if not simulations:
            flash('Nenhuma simulação para exportar.', 'warning')
            return redirect(url_for('dashboard'))
        
        output = StringIO()
        output.write('\ufeff')
        writer = csv.writer(output, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        
        writer.writerow(['ID', 'Local', 'População', 'Área (km²)', 'Tipo', 'Densidade', 'Água (L/dia)', 'Energia (kWh/dia)', 'Data'])
        
        for sim in simulations:
            writer.writerow([
                sim['id'],
                sim.get('area_name', ''),
                sim.get('population', 0),
                f"{sim.get('area_size', 0):.2f}",
                get_building_type_label(sim.get('building_type', '')),
                f"{sim.get('density', 0):.2f}",
                f"{sim.get('total_water', 0):,.0f}",
                f"{sim.get('total_energy', 0):.2f}",
                sim.get('created_at', '')[:10] if sim.get('created_at') else ''
            ])
        
        output.seek(0)
        response = make_response(output.getvalue())
        response.headers['Content-Disposition'] = f'attachment; filename=urbana_simulacoes_{datetime.now().strftime("%Y%m%d_%H%M")}.csv'
        response.headers['Content-Type'] = 'text/csv; charset=utf-8'
        
        return response
        
    except Exception as e:
        print(f"❌ Erro ao exportar CSV: {e}")
        flash('Erro ao exportar dados.', 'danger')
        return redirect(url_for('dashboard'))

@app.route("/export/csv/<int:sim_id>")
def export_single_csv(sim_id):
    """Exporta uma simulação específica em CSV"""
    try:
        response = supabase_client.table('simulations').select('*').eq('id', sim_id).execute()
        
        if not response.data:
            flash('Simulação não encontrada.', 'danger')
            return redirect(url_for('dashboard'))
        
        sim = response.data[0]
        
        output = StringIO()
        output.write('\ufeff')
        writer = csv.writer(output, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        
        writer.writerow(['Campo', 'Valor'])
        writer.writerow(['ID', sim['id']])
        writer.writerow(['Local', sim.get('area_name', '')])
        writer.writerow(['População', sim.get('population', 0)])
        writer.writerow(['Área', f"{sim.get('area_size', 0):.2f} km²"])
        writer.writerow(['Tipo', get_building_type_label(sim.get('building_type', ''))])
        writer.writerow(['Densidade', f"{sim.get('density', 0):.2f} hab/km²"])
        writer.writerow(['Água', f"{sim.get('total_water', 0):,.0f} L/dia"])
        writer.writerow(['Energia', f"{sim.get('total_energy', 0):.2f} kWh/dia"])
        writer.writerow(['Data', sim.get('created_at', '')[:10] if sim.get('created_at') else ''])
        
        output.seek(0)
        response = make_response(output.getvalue())
        response.headers['Content-Disposition'] = f'attachment; filename=simulacao_{sim_id}_{datetime.now().strftime("%Y%m%d")}.csv'
        response.headers['Content-Type'] = 'text/csv; charset=utf-8'
        
        return response
        
    except Exception as e:
        print(f"❌ Erro ao exportar CSV: {e}")
        flash('Erro ao exportar dados.', 'danger')
        return redirect(url_for('view_report', sim_id=sim_id))

@app.route("/export/pdf/<int:sim_id>")
def export_pdf(sim_id):
    """Exporta relatório em PDF"""
    try:
        response = supabase_client.table('simulations').select('*').eq('id', sim_id).execute()
        
        if not response.data:
            flash('Simulação não encontrada.', 'danger')
            return redirect(url_for('dashboard'))
        
        sim = response.data[0]
        
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
        styles = getSampleStyleSheet()
        
        story = []
        
        # Título
        title_style = ParagraphStyle('CustomTitle', parent=styles['Heading1'], fontSize=16, textColor=colors.HexColor('#1565C0'), spaceAfter=20)
        story.append(Paragraph("Relatório URBANA", title_style))
        story.append(Paragraph(f"Simulação #{sim['id']} - {datetime.now().strftime('%d/%m/%Y')}", styles['Normal']))
        story.append(Spacer(1, 20))
        
        # Dados da simulação
        story.append(Paragraph("Dados da Simulação", styles['Heading2']))
        sim_data = [
            ['Local:', sim.get('area_name', 'N/A')],
            ['População:', f"{sim.get('population', 0):,} habitantes"],
            ['Área:', f"{sim.get('area_size', 0):.2f} km²"],
            ['Tipo:', get_building_type_label(sim.get('building_type', ''))],
            ['Densidade:', f"{sim.get('density', 0):.2f} hab/km²"]
        ]
        
        table = Table(sim_data, colWidths=[100, 350])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#E3F2FD')),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('PADDING', (0, 0), (-1, -1), 6),
        ]))
        story.append(table)
        story.append(Spacer(1, 20))
        
        # Consumo
        story.append(Paragraph("Consumo Estimado", styles['Heading2']))
        consumo_data = [
            ['Recurso', 'Total/dia', 'Per capita'],
            ['Água', f"{sim.get('total_water', 0):,.0f} L", f"{sim.get('water_per_capita', 0):.1f} L"],
            ['Energia', f"{sim.get('total_energy', 0):.2f} kWh", f"{sim.get('energy_per_capita', 0):.2f} kWh"]
        ]
        
        table2 = Table(consumo_data, colWidths=[100, 150, 150])
        table2.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1565C0')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('PADDING', (0, 0), (-1, -1), 6),
        ]))
        story.append(table2)
        
        # Rodapé
        story.append(Spacer(1, 30))
        footer = Paragraph(f"<i>Gerado por URBANA em {datetime.now().strftime('%d/%m/%Y %H:%M')}</i>", styles['Italic'])
        story.append(footer)
        
        doc.build(story)
        
        buffer.seek(0)
        response = make_response(buffer.getvalue())
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = f'inline; filename=relatorio_{sim_id}_{datetime.now().strftime("%Y%m%d")}.pdf'
        
        return response
        
    except Exception as e:
        print(f"❌ Erro ao gerar PDF: {e}")
        flash('Erro ao gerar PDF.', 'danger')
        return redirect(url_for('view_report', sim_id=sim_id))

# ============================================================
# PERFIL (VERSÃO DEMO)
# ============================================================

@app.route("/profile")
def profile():
    """Perfil do usuário - versão demo"""
    try:
        # Contar simulações
        response = supabase_client.table('simulations').select('id', count='exact').execute()
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
        print(f"❌ Erro no perfil: {e}")
        flash('Erro ao carregar perfil.', 'danger')
        return redirect(url_for('dashboard'))

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
# INICIALIZAÇÃO
# ============================================================

def setup_supabase():
    """Verifica conexão com Supabase"""
    try:
        print("🔧 Testando conexão com Supabase...")
        supabase_client.table('users').select('count', count='exact').limit(1).execute()
        print("✅ Conexão com Supabase estabelecida")
        return True
    except Exception as e:
        print(f"❌ Erro ao conectar com Supabase: {e}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("🚀 URBANA - Sistema de Planejamento Urbano (Modo DEMO)")
    print("=" * 60)
    
    if setup_supabase():
        print("✅ Sistema pronto para uso")
        print("📍 Acesse: http://localhost:5000/dashboard")
        print("=" * 60)
        
        port = int(os.environ.get('PORT', 5000))
        app.run(debug=False, host='0.0.0.0', port=port)
    else:
        print("❌ Falha ao conectar com Supabase")
