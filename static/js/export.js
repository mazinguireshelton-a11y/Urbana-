// export.js - Funcionalidades de exportação

document.addEventListener('DOMContentLoaded', function() {
    // Adicionar indicador de carregamento para exportações
    setupExportLoading();
    
    // Configurar prévia de PDF
    setupPDFPreview();
});

function setupExportLoading() {
    // Criar indicador de carregamento
    const loadingHTML = `
        <div id="exportLoading" class="loading-indicator">
            <div class="spinner"></div>
            <p>Gerando relatório...</p>
            <small>Isso pode levar alguns segundos</small>
        </div>
    `;
    
    document.body.insertAdjacentHTML('beforeend', loadingHTML);
    
    // Adicionar listeners para links de exportação
    document.querySelectorAll('a[href*="/export/"]').forEach(link => {
        link.addEventListener('click', function(e) {
            if (this.href.includes('/export/pdf') || this.href.includes('/export/csv')) {
                showLoading();
                
                // Esconder loading após 30s (timeout de segurança)
                setTimeout(() => {
                    hideLoading();
                }, 30000);
            }
        });
    });
}

function showLoading() {
    const loading = document.getElementById('exportLoading');
    if (loading) {
        loading.classList.add('active');
        document.body.style.overflow = 'hidden';
    }
}

function hideLoading() {
    const loading = document.getElementById('exportLoading');
    if (loading) {
        loading.classList.remove('active');
        document.body.style.overflow = '';
    }
}

// Ocultar loading quando a página for carregada (para downloads)
window.addEventListener('load', hideLoading);

function setupPDFPreview() {
    // Botão para prévia de PDF (opcional)
    const previewBtn = document.getElementById('pdfPreviewBtn');
    if (previewBtn) {
        previewBtn.addEventListener('click', showPDFPreview);
    }
}

function showPDFPreview() {
    // Coletar dados atuais para prévia
    const simulationData = {
        area_name: document.querySelector('[name="area_name"]')?.value || 'Local de Exemplo',
        population: document.querySelector('[name="population"]')?.value || 10000,
        area_size: document.querySelector('[name="area_size"]')?.value || 10,
        building_type: document.querySelector('[name="building_type"]')?.value || 'medium',
        total_water: (document.querySelector('[name="population"]')?.value || 10000) * 120,
        total_energy: (document.querySelector('[name="population"]')?.value || 10000) * 2.5
    };
    
    // Criar modal de prévia
    const modalHTML = `
        <div id="pdfPreviewModal" class="modal">
            <div class="modal-content export-preview">
                <div class="preview-header">
                    <h3>📄 Prévia do Relatório PDF</h3>
                    <p>Visualize como ficará seu relatório antes de exportar</p>
                </div>
                <div class="preview-body">
                    <div class="preview-section">
                        <h4>Informações da Simulação</h4>
                        <table class="preview-table">
                            <tr>
                                <th>Local:</th>
                                <td>${simulationData.area_name}</td>
                            </tr>
                            <tr>
                                <th>População:</th>
                                <td>${parseInt(simulationData.population).toLocaleString('pt-BR')} habitantes</td>
                            </tr>
                            <tr>
                                <th>Área:</th>
                                <td>${parseFloat(simulationData.area_size).toFixed(2)} km²</td>
                            </tr>
                            <tr>
                                <th>Tipo de Construção:</th>
                                <td>${getBuildingTypeLabel(simulationData.building_type)}</td>
                            </tr>
                        </table>
                    </div>
                    
                    <div class="preview-section">
                        <h4>Métricas de Consumo</h4>
                        <div class="preview-graph">
                            📊 Gráfico de Consumo (visualização no PDF)
                        </div>
                        <table class="preview-table">
                            <tr>
                                <th>Recurso</th>
                                <th>Consumo Total</th>
                                <th>Consumo per Capita</th>
                            </tr>
                            <tr>
                                <td>Água</td>
                                <td>${parseInt(simulationData.total_water).toLocaleString('pt-BR')} L/dia</td>
                                <td>${(simulationData.total_water / simulationData.population).toFixed(1)} L/dia/pessoa</td>
                            </tr>
                            <tr>
                                <td>Energia</td>
                                <td>${parseInt(simulationData.total_energy).toLocaleString('pt-BR')} kWh/dia</td>
                                <td>${(simulationData.total_energy / simulationData.population).toFixed(2)} kWh/dia/pessoa</td>
                            </tr>
                        </table>
                    </div>
                    
                    <div class="preview-section">
                        <h4>Análise e Recomendações</h4>
                        <p>O relatório incluirá uma análise detalhada baseada nos dados fornecidos, com recomendações específicas para planejamento urbano.</p>
                    </div>
                    
                    <div style="text-align: center; margin-top: 30px;">
                        <button onclick="closePreview()" class="btn" style="margin-right: 10px;">Fechar</button>
                        <a href="/export/pdf/${getCurrentSimulationId()}" class="btn export-pdf-btn" onclick="showLoading()">
                            📄 Gerar PDF Completo
                        </a>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    document.body.insertAdjacentHTML('beforeend', modalHTML);
    document.getElementById('pdfPreviewModal').style.display = 'block';
}

function closePreview() {
    const modal = document.getElementById('pdfPreviewModal');
    if (modal) {
        modal.remove();
    }
}

function getBuildingTypeLabel(type) {
    const types = {
        'low': 'Baixa Densidade',
        'medium': 'Média Densidade',
        'high': 'Alta Densidade'
    };
    return types[type] || type;
}

function getCurrentSimulationId() {
    // Tentar obter ID da URL ou dos dados da página
    const urlParams = new URLSearchParams(window.location.search);
    return urlParams.get('id') || '1';
}

// Fechar modal ao clicar fora
window.addEventListener('click', function(event) {
    const modal = document.getElementById('pdfPreviewModal');
    if (modal && event.target === modal) {
        closePreview();
    }
    
    const loading = document.getElementById('exportLoading');
    if (loading && event.target === loading) {
        hideLoading();
    }
});

// Adicionar este script ao base.html
function addExportScript() {
    const script = document.createElement('script');
    script.src = "{{ url_for('static', filename='js/export.js') }}";
    document.head.appendChild(script);
}

// Adicionar botão de prévia opcional
function addPreviewButton() {
    const exportSection = document.querySelector('.btn-group');
    if (exportSection && !document.getElementById('pdfPreviewBtn')) {
        const previewBtn = document.createElement('button');
        previewBtn.id = 'pdfPreviewBtn';
        previewBtn.className = 'btn';
        previewBtn.innerHTML = '👁️ Prévia do PDF';
        previewBtn.style.background = 'linear-gradient(135deg, #8b5cf6, #7c3aed)';
        exportSection.insertBefore(previewBtn, exportSection.firstChild);
    }
}

// Inicializar quando a página carregar
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', addPreviewButton);
} else {
    addPreviewButton();
}
