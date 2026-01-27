/**
 * URBANA Translator - Sistema de Tradução PT/EN
 * Versão 2.0 - Tradutor completo e funcional
 */

class UrbanaTranslator {
    constructor() {
        this.currentLang = this.getSavedLanguage() || 'pt';
        this.translations = this.getTranslations();
        this.initialized = false;
    }

    getTranslations() {
        return {
            'pt': {
                // ========== NAVEGAÇÃO ==========
                '🏠 Início': '🏠 Início',
                '📊 Dashboard': '📊 Dashboard',
                '📋 Simulações': '📋 Simulações',
                '👤 Perfil': '👤 Perfil',
                'Sair': 'Sair',
                'Entrar': 'Entrar',
                'Cadastrar': 'Cadastrar',
                
                // ========== TÍTULOS E HEADERS ==========
                'URBANA': 'URBANA',
                'Sistema Inteligente de Planejamento de Infraestrutura Urbana': 'Sistema Inteligente de Planejamento de Infraestrutura Urbana',
                
                // ========== DASHBOARD ==========
                '📊 Dashboard Analítico': '📊 Dashboard Analítico',
                'Visualização completa das suas simulações urbanas': 'Visualização completa das suas simulações urbanas',
                'Total de Simulações': 'Total de Simulações',
                'População Total': 'População Total',
                'Água Média/dia': 'Água Média/dia',
                'Energia Média/dia': 'Energia Média/dia',
                '🏙️ Consumo por Localidade': '🏙️ Consumo por Localidade',
                'Comparativo entre áreas urbanas': 'Comparativo entre áreas urbanas',
                '🏢 Distribuição por Densidade': '🏢 Distribuição por Densidade',
                'Tipos de construção nas simulações': 'Tipos de construção nas simulações',
                '📈 Evolução Temporal': '📈 Evolução Temporal',
                'Tendência dos últimos 7 dias': 'Tendência dos últimos 7 dias',
                '📋 Histórico de Simulações': '📋 Histórico de Simulações',
                '🔍 Buscar local...': '🔍 Buscar local...',
                '📂 Todos os tipos': '📂 Todos os tipos',
                '🏡 Baixa densidade': '🏡 Baixa densidade',
                '🏢 Média densidade': '🏢 Média densidade',
                '🏙️ Alta densidade': '🏙️ Alta densidade',
                '📍 Local': '📍 Local',
                '👥 População': '👥 População',
                '📏 Área (km²)': '📏 Área (km²)',
                '🏢 Tipo': '🏢 Tipo',
                '💧 Água (L/dia)': '💧 Água (L/dia)',
                '⚡ Energia (kWh/dia)': '⚡ Energia (kWh/dia)',
                '📅 Data': '📅 Data',
                '⚙️ Ações': '⚙️ Ações',
                'Nenhuma simulação encontrada': 'Nenhuma simulação encontrada',
                'Crie sua primeira simulação para ver os dados aqui': 'Crie sua primeira simulação para ver os dados aqui',
                '➕ Criar Primeira Simulação': '➕ Criar Primeira Simulação',
                
                // ========== MINHAS SIMULAÇÕES ==========
                'Minhas Simulações': 'Minhas Simulações',
                '+ Nova Simulação': '+ Nova Simulação',
                '📥 Exportar CSV': '📥 Exportar CSV',
                'Total de Simulações': 'Total de Simulações',
                'População Total': 'População Total',
                'Água Média/dia': 'Água Média/dia',
                'Energia Média/dia': 'Energia Média/dia',
                'Histórico de Simulações': 'Histórico de Simulações',
                'Buscar local...': 'Buscar local...',
                'Todos os tipos': 'Todos os tipos',
                'Baixa densidade': 'Baixa densidade',
                'Média densidade': 'Média densidade',
                'Alta densidade': 'Alta densidade',
                'Local': 'Local',
                'Densidade': 'Densidade',
                'Data': 'Data',
                'Exportar CSV': 'Exportar CSV',
                'Exportar PDF': 'Exportar PDF',
                'Ver relatório': 'Ver relatório',
                'Excluir': 'Excluir',
                
                // ========== PERFIL ==========
                'Meu Perfil': 'Meu Perfil',
                '✏️ Editar Perfil': '✏️ Editar Perfil',
                'Status da Conta': 'Status da Conta',
                'Email verificado ✔️': 'Email verificado ✔️',
                'Email não verificado': 'Email não verificado',
                'Sua conta está totalmente verificada e segura.': 'Sua conta está totalmente verificada e segura.',
                'Você precisa confirmar seu email para acessar todas as funcionalidades.': 'Você precisa confirmar seu email para acessar todas as funcionalidades.',
                'Informações da Conta': 'Informações da Conta',
                'Nome Completo': 'Nome Completo',
                'Email': 'Email',
                'Organização': 'Organização',
                'Membro desde': 'Membro desde',
                'Estatísticas': 'Estatísticas',
                'Simulações': 'Simulações',
                'Dias na plataforma': 'Dias na plataforma',
                'Última Simulação': 'Última Simulação',
                'Nenhuma simulação realizada ainda.': 'Nenhuma simulação realizada ainda.',
                'Ações da Conta': 'Ações da Conta',
                'Exportar Meus Dados (CSV)': 'Exportar Meus Dados (CSV)',
                'Minhas Simulações': 'Minhas Simulações',
                'Dashboard Completo': 'Dashboard Completo',
                'Alterar Senha': 'Alterar Senha',
                'Sair da Conta': 'Sair da Conta',
                'Ajuda e Segurança': 'Ajuda e Segurança',
                'Termos de Serviço': 'Termos de Serviço',
                'Política de Privacidade': 'Política de Privacidade',
                'Confirmar Email': 'Confirmar Email',
                'Conta não verificada': 'Conta não verificada',
                'Para acessar todas as funcionalidades do URBANA, você precisa confirmar seu email.': 'Para acessar todas as funcionalidades do URBANA, você precisa confirmar seu email.',
                
                // ========== FOOTER ==========
                '© 2026 • Projeto URBANA • Engenharia & Impacto Social': '© 2026 • Projeto URBANA • Engenharia & Impacto Social',
                'Tema atual:': 'Tema atual:',
                'Claro': 'Claro',
                'Escuro': 'Escuro',
                'Automático': 'Automático',
                
                // ========== TEMAS ==========
                'Tema Claro': 'Tema Claro',
                'Tema Escuro': 'Tema Escuro',
                'Auto (Sistema)': 'Auto (Sistema)',
                
                // ========== FORMULÁRIOS ==========
                'Nome do Bairro / Cidade': 'Nome do Bairro / Cidade',
                'População Total': 'População Total',
                'Área (km²)': 'Área (km²)',
                'Tipo de Construção': 'Tipo de Construção',
                'Baixa densidade': 'Baixa densidade',
                'Média densidade': 'Média densidade',
                'Alta densidade': 'Alta densidade',
                'Calcular Infraestrutura': 'Calcular Infraestrutura',
                
                // ========== MENSAGENS ==========
                'Simulação criada com sucesso!': 'Simulação criada com sucesso!',
                'Erro ao salvar simulação.': 'Erro ao salvar simulação.',
                'Simulação não encontrada ou acesso negado.': 'Simulação não encontrada ou acesso negado.',
                'Erro ao carregar relatório.': 'Erro ao carregar relatório.',
                
                // ========== RELATÓRIO ==========
                'RELATÓRIO DE INFRAESTRUTURA URBANA': 'RELATÓRIO DE INFRAESTRUTURA URBANA',
                'Análise técnica completa para planejamento urbano': 'Análise técnica completa para planejamento urbano',
                'RESUMO EXECUTIVO': 'RESUMO EXECUTIVO',
                'Água Necessária': 'Água Necessária',
                'L/dia': 'L/dia',
                'L por pessoa/dia': 'L por pessoa/dia',
                'Energia Necessária': 'Energia Necessária',
                'kWh/dia': 'kWh/dia',
                'kWh por pessoa/dia': 'kWh por pessoa/dia',
                'Densidade Populacional': 'Densidade Populacional',
                'hab/km²': 'hab/km²',
                'Baixa densidade': 'Baixa densidade',
                'Média densidade': 'Média densidade',
                'Alta densidade': 'Alta densidade',
                'Eficiência Urbana': 'Eficiência Urbana',
                'Alta': 'Alta',
                'Média': 'Média',
                'Baixa': 'Baixa',
                'Índice de eficiência energética': 'Índice de eficiência energética',
                'VISUALIZAÇÃO DE CONSUMO': 'VISUALIZAÇÃO DE CONSUMO',
                'Comparação entre recursos necessários': 'Comparação entre recursos necessários',
                'ANÁLISE DE INFRAESTRUTURA': 'ANÁLISE DE INFRAESTRUTURA',
                'Recomendações de Água': 'Recomendações de Água',
                'Recomendações de Energia': 'Recomendações de Energia',
                'COMPARAÇÃO COM PADRÕES': 'COMPARAÇÃO COM PADRÕES',
                'Consumo per capita (água)': 'Consumo per capita (água)',
                'Consumo per capita (energia)': 'Consumo per capita (energia)',
                'Referência:': 'Referência:',
                'L/dia': 'L/dia',
                'kWh/dia': 'kWh/dia',
                'Eficiência urbana': 'Eficiência urbana',
                'EXPORTAR E COMPARTILHAR': 'EXPORTAR E COMPARTILHAR',
                'Salve este relatório para apresentações ou análises futuras': 'Salve este relatório para apresentações ou análises futuras',
                'Exportar PDF': 'Exportar PDF',
                'Relatório completo': 'Relatório completo',
                'Exportar CSV': 'Exportar CSV',
                'Dados brutos': 'Dados brutos',
                'Ver Dashboard': 'Ver Dashboard',
                'Análise avançada': 'Análise avançada',
                'Nova Simulação': 'Nova Simulação',
                'Criar outro cenário': 'Criar outro cenário'
            },
            'en': {
                // ========== NAVIGATION ==========
                '🏠 Início': '🏠 Home',
                '📊 Dashboard': '📊 Dashboard',
                '📋 Simulações': '📋 My Simulations',
                '👤 Perfil': '👤 Profile',
                'Sair': 'Logout',
                'Entrar': 'Login',
                'Cadastrar': 'Register',
                
                // ========== TITLES AND HEADERS ==========
                'URBANA': 'URBANA',
                'Sistema Inteligente de Planejamento de Infraestrutura Urbana': 'Intelligent Urban Infrastructure Planning System',
                
                // ========== DASHBOARD ==========
                '📊 Dashboard Analítico': '📊 Analytical Dashboard',
                'Visualização completa das suas simulações urbanas': 'Complete visualization of your urban simulations',
                'Total de Simulações': 'Total Simulations',
                'População Total': 'Total Population',
                'Água Média/dia': 'Average Water/day',
                'Energia Média/dia': 'Average Energy/day',
                '🏙️ Consumo por Localidade': '🏙️ Consumption by Location',
                'Comparativo entre áreas urbanas': 'Comparison between urban areas',
                '🏢 Distribuição por Densidade': '🏢 Distribution by Density',
                'Tipos de construção nas simulações': 'Building types in simulations',
                '📈 Evolução Temporal': '📈 Time Evolution',
                'Tendência dos últimos 7 dias': 'Trend of the last 7 days',
                '📋 Histórico de Simulações': '📋 Simulation History',
                '🔍 Buscar local...': '🔍 Search location...',
                '📂 Todos os tipos': '📂 All types',
                '🏡 Baixa densidade': '🏡 Low density',
                '🏢 Média densidade': '🏢 Medium density',
                '🏙️ Alta densidade': '🏙️ High density',
                '📍 Local': '📍 Location',
                '👥 População': '👥 Population',
                '📏 Área (km²)': '📏 Area (km²)',
                '🏢 Tipo': '🏢 Type',
                '💧 Água (L/dia)': '💧 Water (L/day)',
                '⚡ Energia (kWh/dia)': '⚡ Energy (kWh/day)',
                '📅 Data': '📅 Date',
                '⚙️ Ações': '⚙️ Actions',
                'Nenhuma simulação encontrada': 'No simulations found',
                'Crie sua primeira simulação para ver os dados aqui': 'Create your first simulation to see data here',
                '➕ Criar Primeira Simulação': '➕ Create First Simulation',
                
                // ========== MY SIMULATIONS ==========
                'Minhas Simulações': 'My Simulations',
                '+ Nova Simulação': '+ New Simulation',
                '📥 Exportar CSV': '📥 Export CSV',
                'Total de Simulações': 'Total Simulations',
                'População Total': 'Total Population',
                'Água Média/dia': 'Average Water/day',
                'Energia Média/dia': 'Average Energy/day',
                'Histórico de Simulações': 'Simulation History',
                'Buscar local...': 'Search location...',
                'Todos os tipos': 'All types',
                'Baixa densidade': 'Low density',
                'Média densidade': 'Medium density',
                'Alta densidade': 'High density',
                'Local': 'Location',
                'Densidade': 'Density',
                'Data': 'Date',
                'Exportar CSV': 'Export CSV',
                'Exportar PDF': 'Export PDF',
                'Ver relatório': 'View report',
                'Excluir': 'Delete',
                
                // ========== PROFILE ==========
                'Meu Perfil': 'My Profile',
                '✏️ Editar Perfil': '✏️ Edit Profile',
                'Status da Conta': 'Account Status',
                'Email verificado ✔️': 'Email verified ✔️',
                'Email não verificado': 'Email not verified',
                'Sua conta está totalmente verificada e segura.': 'Your account is fully verified and secure.',
                'Você precisa confirmar seu email para acessar todas as funcionalidades.': 'You need to confirm your email to access all features.',
                'Informações da Conta': 'Account Information',
                'Nome Completo': 'Full Name',
                'Email': 'Email',
                'Organização': 'Organization',
                'Membro desde': 'Member since',
                'Estatísticas': 'Statistics',
                'Simulações': 'Simulations',
                'Dias na plataforma': 'Days on platform',
                'Última Simulação': 'Last Simulation',
                'Nenhuma simulação realizada ainda.': 'No simulations performed yet.',
                'Ações da Conta': 'Account Actions',
                'Exportar Meus Dados (CSV)': 'Export My Data (CSV)',
                'Minhas Simulações': 'My Simulations',
                'Dashboard Completo': 'Complete Dashboard',
                'Alterar Senha': 'Change Password',
                'Sair da Conta': 'Logout',
                'Ajuda e Segurança': 'Help & Security',
                'Termos de Serviço': 'Terms of Service',
                'Política de Privacidade': 'Privacy Policy',
                'Confirmar Email': 'Confirm Email',
                'Conta não verificada': 'Account not verified',
                'Para acessar todas as funcionalidades do URBANA, você precisa confirmar seu email.': 'To access all URBANA features, you need to confirm your email.',
                
                // ========== FOOTER ==========
                '© 2026 • Projeto URBANA • Engenharia & Impacto Social': '© 2026 • URBANA Project • Engineering & Social Impact',
                'Tema atual:': 'Current theme:',
                'Claro': 'Light',
                'Escuro': 'Dark',
                'Automático': 'Auto',
                
                // ========== THEMES ==========
                'Tema Claro': 'Light Theme',
                'Tema Escuro': 'Dark Theme',
                'Auto (Sistema)': 'Auto (System)',
                
                // ========== FORMS ==========
                'Nome do Bairro / Cidade': 'Neighborhood / City Name',
                'População Total': 'Total Population',
                'Área (km²)': 'Area (km²)',
                'Tipo de Construção': 'Building Type',
                'Baixa densidade': 'Low density',
                'Média densidade': 'Medium density',
                'Alta densidade': 'High density',
                'Calcular Infraestrutura': 'Calculate Infrastructure',
                
                // ========== MESSAGES ==========
                'Simulação criada com sucesso!': 'Simulation created successfully!',
                'Erro ao salvar simulação.': 'Error saving simulation.',
                'Simulação não encontrada ou acesso negado.': 'Simulation not found or access denied.',
                'Erro ao carregar relatório.': 'Error loading report.',
                
                // ========== REPORT ==========
                'RELATÓRIO DE INFRAESTRUTURA URBANA': 'URBAN INFRASTRUCTURE REPORT',
                'Análise técnica completa para planejamento urbano': 'Complete technical analysis for urban planning',
                'RESUMO EXECUTIVO': 'EXECUTIVE SUMMARY',
                'Água Necessária': 'Water Required',
                'L/dia': 'L/day',
                'L por pessoa/dia': 'L per person/day',
                'Energia Necessária': 'Energy Required',
                'kWh/dia': 'kWh/day',
                'kWh por pessoa/dia': 'kWh per person/day',
                'Densidade Populacional': 'Population Density',
                'hab/km²': 'people/km²',
                'Baixa densidade': 'Low density',
                'Média densidade': 'Medium density',
                'Alta densidade': 'High density',
                'Eficiência Urbana': 'Urban Efficiency',
                'Alta': 'High',
                'Média': 'Medium',
                'Baixa': 'Low',
                'Índice de eficiência energética': 'Energy efficiency index',
                'VISUALIZAÇÃO DE CONSUMO': 'CONSUMPTION VISUALIZATION',
                'Comparação entre recursos necessários': 'Comparison between required resources',
                'ANÁLISE DE INFRAESTRUTURA': 'INFRASTRUCTURE ANALYSIS',
                'Recomendações de Água': 'Water Recommendations',
                'Recomendações de Energia': 'Energy Recommendations',
                'COMPARAÇÃO COM PADRÕES': 'COMPARISON WITH STANDARDS',
                'Consumo per capita (água)': 'Per capita consumption (water)',
                'Consumo per capita (energia)': 'Per capita consumption (energy)',
                'Referência:': 'Reference:',
                'L/dia': 'L/day',
                'kWh/dia': 'kWh/day',
                'Eficiência urbana': 'Urban efficiency',
                'EXPORTAR E COMPARTILHAR': 'EXPORT AND SHARE',
                'Salve este relatório para apresentações ou análises futuras': 'Save this report for presentations or future analysis',
                'Exportar PDF': 'Export PDF',
                'Relatório completo': 'Complete report',
                'Exportar CSV': 'Export CSV',
                'Dados brutos': 'Raw data',
                'Ver Dashboard': 'View Dashboard',
                'Análise avançada': 'Advanced analysis',
                'Nova Simulação': 'New Simulation',
                'Criar outro cenário': 'Create another scenario'
            }
        };
    }

    init() {
        if (this.initialized) return;
        
        this.addStyles();
        this.updateLanguageButtons();
        
        // Aplicar tradução se não for português
        if (this.currentLang !== 'pt') {
            // Pequeno delay para garantir que o DOM está carregado
            setTimeout(() => {
                this.translatePage();
            }, 300);
        }
        
        this.initialized = true;
    }

    getSavedLanguage() {
        return localStorage.getItem('urbana_lang') || 'pt';
    }

    saveLanguage(lang) {
        localStorage.setItem('urbana_lang', lang);
        this.currentLang = lang;
    }

    updateLanguageButtons() {
        const updateButtons = () => {
            document.querySelectorAll('.lang-btn').forEach(btn => {
                let lang = 'pt';
                const onclick = btn.getAttribute('onclick');
                if (onclick) {
                    lang = onclick.includes("'pt'") ? 'pt' : 'en';
                } else {
                    lang = btn.textContent.includes('PT') ? 'pt' : 'en';
                }
                btn.classList.toggle('active', lang === this.currentLang);
            });
        };
        
        // Tentar várias vezes para garantir que os botões existam
        let attempts = 0;
        const tryUpdate = () => {
            if (document.querySelectorAll('.lang-btn').length > 0) {
                updateButtons();
            } else if (attempts < 10) {
                attempts++;
                setTimeout(tryUpdate, 100);
            }
        };
        
        tryUpdate();
    }

    translatePage() {
        // Método 1: Traduzir elementos específicos por classe/ID
        this.translateBySelectors();
        
        // Método 2: Traduzir por TreeWalker (mais abrangente)
        this.translateWithWalker();
        
        // Método 3: Traduzir atributos
        this.translateAttributes();
        
        // Atualizar botões
        this.updateLanguageButtons();
        
        // Mostrar notificação
        this.showNotification();
    }

    translateBySelectors() {
        // Lista de seletores para elementos importantes
        const selectors = [
            'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
            'p', 'span', 'a', 'button', 'label',
            'li', 'td', 'th', 'div',
            '.nav-link', '.btn', '.card-title', '.card-subtitle',
            '.page-title', '.page-subtitle', '.metric-label',
            '.form-label', '.alert', '.badge'
        ];

        selectors.forEach(selector => {
            document.querySelectorAll(selector).forEach(element => {
                this.translateElement(element);
            });
        });
    }

    translateElement(element) {
        // Ignorar elementos com filhos que já foram processados
        if (element.hasAttribute('data-translated')) return;
        
        // Traduzir texto direto
        if (element.childNodes.length === 1 && element.childNodes[0].nodeType === 3) {
            const text = element.textContent.trim();
            if (text && this.translations[this.currentLang][text]) {
                element.textContent = this.translations[this.currentLang][text];
                element.setAttribute('data-translated', 'true');
            }
        }
        
        // Traduzir todos os nós de texto dentro do elemento
        const walker = document.createTreeWalker(
            element,
            NodeFilter.SHOW_TEXT,
            null
        );
        
        let node;
        while (node = walker.nextNode()) {
            const text = node.nodeValue.trim();
            if (text && this.translations[this.currentLang][text]) {
                node.nodeValue = node.nodeValue.replace(text, this.translations[this.currentLang][text]);
            }
        }
    }

    translateWithWalker() {
        const walker = document.createTreeWalker(
            document.body,
            NodeFilter.SHOW_TEXT,
            {
                acceptNode: function(node) {
                    // Ignorar nós vazios
                    if (!node.nodeValue || !node.nodeValue.trim()) {
                        return NodeFilter.FILTER_REJECT;
                    }
                    
                    // Ignorar elementos técnicos
                    const parent = node.parentElement;
                    if (parent) {
                        const tagName = parent.tagName.toLowerCase();
                        const ignoreTags = ['script', 'style', 'code', 'pre', 'textarea', 'input', 'select', 'option'];
                        
                        if (ignoreTags.includes(tagName)) {
                            return NodeFilter.FILTER_REJECT;
                        }
                        
                        // Ignorar seletor de idioma
                        if (parent.classList.contains('lang-btn') || 
                            parent.classList.contains('language-toggle')) {
                            return NodeFilter.FILTER_REJECT;
                        }
                    }
                    
                    return NodeFilter.FILTER_ACCEPT;
                }
            }
        );

        let node;
        const nodes = [];
        while (node = walker.nextNode()) {
            nodes.push(node);
        }

        // Traduzir em lote
        nodes.forEach(node => {
            const text = node.nodeValue.trim();
            if (text && this.translations[this.currentLang][text]) {
                node.nodeValue = node.nodeValue.replace(text, this.translations[this.currentLang][text]);
            }
        });
    }

    translateAttributes() {
        // Placeholders
        document.querySelectorAll('[placeholder]').forEach(el => {
            const text = el.getAttribute('placeholder');
            if (text && this.translations[this.currentLang][text]) {
                el.setAttribute('placeholder', this.translations[this.currentLang][text]);
            }
        });

        // Titles
        document.querySelectorAll('[title]').forEach(el => {
            const text = el.getAttribute('title');
            if (text && this.translations[this.currentLang][text]) {
                el.setAttribute('title', this.translations[this.currentLang][text]);
            }
        });

        // Alt text
        document.querySelectorAll('[alt]').forEach(el => {
            const text = el.getAttribute('alt');
            if (text && this.translations[this.currentLang][text]) {
                el.setAttribute('alt', this.translations[this.currentLang][text]);
            }
        });
    }

    addStyles() {
        // Remover estilos antigos
        const oldStyle = document.getElementById('urbana-translator-styles');
        if (oldStyle) oldStyle.remove();

        const style = document.createElement('style');
        style.id = 'urbana-translator-styles';
        style.textContent = `
            .language-toggle {
                display: flex;
                gap: 5px;
                margin-right: 10px;
            }
            
            .lang-btn {
                background: var(--gray-light, #f5f5f5);
                border: 1px solid var(--border-color, #ddd);
                border-radius: 4px;
                padding: 4px 10px;
                cursor: pointer;
                font-size: 0.85rem;
                transition: all 0.2s;
                font-family: inherit;
                min-width: 40px;
                text-align: center;
            }
            
            .lang-btn:hover {
                background: var(--gray, #e0e0e0);
                transform: translateY(-1px);
            }
            
            .lang-btn.active {
                background: var(--color-primary, #1565C0);
                color: white !important;
                border-color: var(--color-primary, #1565C0);
                font-weight: 500;
                box-shadow: 0 2px 5px rgba(21, 101, 192, 0.3);
            }
            
            .lang-notification {
                position: fixed;
                bottom: 20px;
                right: 20px;
                background: var(--color-primary, #1565C0);
                color: white;
                padding: 12px 20px;
                border-radius: 8px;
                z-index: 10000;
                animation: langFadeInOut 3s ease;
                box-shadow: 0 4px 15px rgba(0,0,0,0.2);
                font-family: 'Inter', sans-serif;
                font-weight: 500;
                pointer-events: none;
            }
            
            @keyframes langFadeInOut {
                0% { opacity: 0; transform: translateX(100px); }
                10% { opacity: 1; transform: translateX(0); }
                90% { opacity: 1; transform: translateX(0); }
                100% { opacity: 0; transform: translateX(100px); }
            }
        `;
        document.head.appendChild(style);
    }

    showNotification() {
        // Remover notificação existente
        const existing = document.querySelector('.lang-notification');
        if (existing) existing.remove();

        const messages = {
            'pt': 'Idioma alterado para Português 🇧🇷',
            'en': 'Language changed to English 🇺🇸'
        };

        const notification = document.createElement('div');
        notification.className = 'lang-notification';
        notification.textContent = messages[this.currentLang];
        
        document.body.appendChild(notification);

        setTimeout(() => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        }, 3000);
    }
}

// Inicialização segura
document.addEventListener('DOMContentLoaded', () => {
    // Garantir que só há uma instância
    if (!window.urbanaTranslator) {
        window.urbanaTranslator = new UrbanaTranslator();
    }
    
    // Pequeno delay para garantir que tudo está carregado
    setTimeout(() => {
        if (window.urbanaTranslator && !window.urbanaTranslator.initialized) {
            window.urbanaTranslator.init();
        }
    }, 500);
});

// Função global para mudança de idioma
window.changeLanguage = function(lang) {
    if (window.urbanaTranslator) {
        window.urbanaTranslator.saveLanguage(lang);
        window.urbanaTranslator.currentLang = lang;
        window.urbanaTranslator.translatePage();
    }
};
