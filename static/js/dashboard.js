// static/js/dashboard.js
console.log("Dashboard JS carregado");

// Verificar se Chart.js está disponível
if (typeof Chart === 'undefined') {
    console.warn("Chart.js não foi carregado. Carregando...");
    const script = document.createElement('script');
    script.src = 'https://cdn.jsdelivr.net/npm/chart.js';
    script.onload = function() {
        console.log("Chart.js carregado com sucesso");
        initCharts();
    };
    document.head.appendChild(script);
} else {
    initCharts();
}

function initCharts() {
    console.log("Inicializando gráficos...");
    
    // Se houver elementos de gráfico na página, inicializá-los
    const charts = document.querySelectorAll('canvas');
    if (charts.length > 0) {
        console.log(`${charts.length} gráfico(s) encontrado(s)`);
    }
}

// Funções auxiliares
function viewSimulation(id) {
    window.location.href = `/report/${id}`;
}

function deleteSimulation(id) {
    if (confirm('Tem certeza que deseja excluir esta simulação?')) {
        fetch(`/delete/${id}`, { 
            method: 'DELETE',
            headers: {
                'Content-Type': 'application/json'
            }
        })
        .then(response => {
            if (response.ok) {
                alert('Simulação excluída com sucesso!');
                location.reload();
            } else {
                alert('Erro ao excluir simulação.');
            }
        })
        .catch(error => {
            console.error('Erro:', error);
            alert('Erro ao excluir simulação.');
        });
    }
}
