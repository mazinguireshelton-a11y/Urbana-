// static/js/main.js
document.addEventListener('DOMContentLoaded', function() {
    // Animações de entrada
    const cards = document.querySelectorAll('.card, .metric-card');
    cards.forEach((card, index) => {
        card.style.animationDelay = `${index * 0.1}s`;
        card.classList.add('fade-in-up');
    });
    
    // Contador animado para métricas
    const metricValues = document.querySelectorAll('.metric-value');
    metricValues.forEach(value => {
        const target = parseInt(value.textContent.replace(/\./g, ''));
        if (!isNaN(target) && target > 0) {
            animateCounter(value, target);
        }
    });
});

function animateCounter(element, target) {
    let current = 0;
    const increment = target / 50;
    const timer = setInterval(() => {
        current += increment;
        if (current >= target) {
            element.textContent = target.toLocaleString('pt-BR');
            clearInterval(timer);
        } else {
            element.textContent = Math.floor(current).toLocaleString('pt-BR');
        }
    }, 30);
}

// ========== FUNÇÕES DE IDIOMA ==========

// Função para mudar idioma
function changeLanguage(lang) {
    if (window.urbanaTranslator) {
        window.urbanaTranslator.switchLanguage(lang);
    } else {
        // Fallback simples
        localStorage.setItem('urbana_lang', lang);
        location.reload();
    }
}

// Carregar idioma salvo ao iniciar
document.addEventListener('DOMContentLoaded', function() {
    const savedLang = localStorage.getItem('urbana_lang') || 'pt';
    const select = document.getElementById('language-select');
    if (select) {
        select.value = savedLang;
    }
});
