// theme.js - Sistema de controle de tema

document.addEventListener('DOMContentLoaded', function() {
    // Carregar tema salvo
    loadTheme();
    
    // Atualizar indicador de tema
    updateThemeIndicator();
});

// Função para definir o tema
function setTheme(theme) {
    // Remover classes anteriores
    document.body.classList.remove('light-theme', 'dark-theme', 'auto-theme');
    document.body.removeAttribute('data-theme');
    
    // Definir novo tema
    if (theme === 'dark') {
        document.body.classList.add('dark-theme');
        document.body.setAttribute('data-theme', 'dark');
        localStorage.setItem('urbana-theme', 'dark');
    } else if (theme === 'light') {
        document.body.classList.add('light-theme');
        localStorage.setItem('urbana-theme', 'light');
    } else {
        // Auto - seguir preferência do sistema
        document.body.classList.add('auto-theme');
        localStorage.setItem('urbana-theme', 'auto');
        applySystemTheme();
    }
    
    // Atualizar botões ativos
    updateThemeButtons(theme);
    
    // Atualizar indicador
    updateThemeIndicator();
    
    // Adicionar classe de transição
    document.body.classList.add('theme-transition');
    setTimeout(() => {
        document.body.classList.remove('theme-transition');
    }, 300);
    
    console.log(`Tema alterado para: ${theme}`);
}

// Aplicar tema do sistema
function applySystemTheme() {
    if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
        document.body.setAttribute('data-theme', 'dark');
    } else {
        document.body.removeAttribute('data-theme');
    }
}

// Carregar tema salvo
function loadTheme() {
    const savedTheme = localStorage.getItem('urbana-theme') || 'light';
    
    // Verificar se há preferência salva
    if (savedTheme) {
        setTheme(savedTheme);
    } else {
        // Tentar detectar preferência do sistema
        if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
            setTheme('auto');
        }
    }
    
    // Ouvir mudanças no tema do sistema
    if (window.matchMedia) {
        window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', e => {
            if (localStorage.getItem('urbana-theme') === 'auto') {
                applySystemTheme();
                updateThemeIndicator();
            }
        });
    }
}

// Atualizar botões ativos
function updateThemeButtons(theme) {
    // Remover classe active de todos
    document.querySelectorAll('.theme-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    
    // Adicionar classe active ao botão correspondente
    if (theme === 'light') {
        document.querySelector('.light-btn').classList.add('active');
    } else if (theme === 'dark') {
        document.querySelector('.dark-btn').classList.add('active');
    } else {
        document.querySelector('.auto-btn').classList.add('active');
    }
}

// Atualizar indicador de tema no footer
function updateThemeIndicator() {
    const theme = localStorage.getItem('urbana-theme') || 'light';
    const indicator = document.getElementById('current-theme');
    
    if (indicator) {
        let themeName = '';
        switch(theme) {
            case 'light': themeName = 'Claro'; break;
            case 'dark': themeName = 'Escuro'; break;
            case 'auto': themeName = 'Automático'; break;
            default: themeName = 'Claro';
        }
        
        indicator.textContent = themeName;
    }
}

// Detector de tema do sistema
function detectSystemTheme() {
    return window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
}

// Alternar entre claro/escuro
function toggleTheme() {
    const current = localStorage.getItem('urbana-theme') || 'light';
    
    if (current === 'light') {
        setTheme('dark');
    } else if (current === 'dark') {
        setTheme('auto');
    } else {
        setTheme('light');
    }
}

// Atalho de teclado (Ctrl+Shift+T)
document.addEventListener('keydown', function(e) {
    if (e.ctrlKey && e.shiftKey && e.key === 'T') {
        e.preventDefault();
        toggleTheme();
    }
});

// Exportar funções para uso global
window.URBANA_THEME = {
    setTheme,
    toggleTheme,
    getCurrentTheme: () => localStorage.getItem('urbana-theme') || 'light',
    isDarkMode: () => document.body.getAttribute('data-theme') === 'dark'
};
