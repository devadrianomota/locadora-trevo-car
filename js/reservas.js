// reservas.js - Sistema SIMPLIFICADO de reservas
class ReservasSystem {
    constructor() {
        this.reservas = [];
        this.init();
    }

    init() {
        this.carregarReservasDoStorage();
        this.renderizarReservas();
        this.configurarFiltros();
        this.configurarBotoes();
        console.log('🐞 Sistema de reservas iniciado');
    }

    carregarReservasDoStorage() {
        // Tenta carregar do Local Storage
        const reservasSalvas = localStorage.getItem('trevocar_reservas');
        
        if (reservasSalvas) {
            this.reservas = JSON.parse(reservasSalvas);
        } else {
            // Dados de exemplo INICIAIS - só ativas e concluídas
            this.reservas = [
                {
                    id: 1,
                    codigo: 'TRV12345',
                    veiculo: 'Hyundai HB20 - Essencial',
                    periodo: '27/10/2024 - 30/10/2024 (3 dias)',
                    agencia: 'Aeroporto Guarulhos',
                    valor: 267.00,
                    status: 'active', // ou 'completed'
                    avaliacao: null,
                    dataCriacao: new Date().toISOString()
                },
                {
                    id: 2,
                    codigo: 'TRV12344',
                    veiculo: 'Toyota Corolla - Intermediário',
                    periodo: '15/10/2024 - 18/10/2024 (Concluído)',
                    agencia: 'Aeroporto Congonhas',
                    valor: 387.00,
                    status: 'completed',
                    avaliacao: 4,
                    dataCriacao: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000).toISOString()
                }
            ];
            this.salvarNoStorage();
        }
    }

    salvarNoStorage() {
        localStorage.setItem('trevocar_reservas', JSON.stringify(this.reservas));
    }

    renderizarReservas(filtro = 'todas') {
        const container = document.querySelector('.reservas-list');
        const reservasFiltradas = this.reservas.filter(reserva => {
            if (filtro === 'todas') return true;
            return reserva.status === filtro;
        });

        if (reservasFiltradas.length === 0) {
            container.innerHTML = `
                <div class="sem-reservas">
                    <div class="trevo-icon">🍀</div>
                    <h3>Nenhuma reserva encontrada</h3>
                    <p>Quando você fizer uma reserva, ela aparecerá aqui!</p>
                </div>
            `;
            return;
        }

        container.innerHTML = reservasFiltradas.map(reserva => `
            <div class="reserva-card ${reserva.status}">
                <div class="reserva-status">
                    ${reserva.status === 'active' ? '🟢 ATIVA' : '✅ CONCLUÍDA'}
                </div>
                <div class="reserva-content">
                    <div class="reserva-info">
                        <h3>${reserva.veiculo}</h3>
                        <p class="reserva-codigo">🍀 Código: ${reserva.codigo}</p>
                        <p class="reserva-periodo">📅 ${reserva.periodo}</p>
                        <p class="reserva-local">🏢 ${reserva.agencia}</p>
                        <p class="reserva-valor">💵 Valor: R$ ${reserva.valor.toFixed(2)}</p>
                        ${reserva.avaliacao ? 
                            `<p class="reserva-avaliacao">⭐ ${'⭐'.repeat(reserva.avaliacao)}${'☆'.repeat(5 - reserva.avaliacao)} (${reserva.avaliacao}/5)</p>` : 
                            ''
                        }
                    </div>
                    <div class="reserva-actions">
                        <button class="btn-detalhes" data-id="${reserva.id}">Ver detalhes</button>
                        ${reserva.status === 'active' ? 
                            `<button class="btn-cancelar" data-id="${reserva.id}">Cancelar reserva</button>` : 
                            `<button class="btn-repetir" data-id="${reserva.id}">Alugar novamente</button>`
                        }
                    </div>
                </div>
            </div>
        `).join('');
    }

    configurarFiltros() {
        const filtroSelect = document.querySelector('.filtro-select');
        const searchInput = document.querySelector('.search-input');

        filtroSelect.addEventListener('change', (e) => {
            this.renderizarReservas(e.target.value);
        });

        searchInput.addEventListener('input', (e) => {
            this.buscarReservas(e.target.value);
        });
    }

    configurarBotoes() {
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('btn-detalhes')) {
                this.mostrarDetalhes(parseInt(e.target.dataset.id));
            }
            if (e.target.classList.contains('btn-cancelar')) {
                this.cancelarReserva(parseInt(e.target.dataset.id));
            }
            if (e.target.classList.contains('btn-repetir')) {
                this.repetirReserva(parseInt(e.target.dataset.id));
            }
        });
    }

    buscarReservas(termo) {
        const termoLower = termo.toLowerCase();
        const reservasFiltradas = this.reservas.filter(reserva => 
            reserva.codigo.toLowerCase().includes(termoLower) ||
            reserva.veiculo.toLowerCase().includes(termoLower)
        );
        this.renderizarListaEspecifica(reservasFiltradas);
    }

    renderizarListaEspecifica(reservas) {
        const container = document.querySelector('.reservas-list');
        
        if (reservas.length === 0) {
            container.innerHTML = `
                <div class="sem-reservas">
                    <div class="trevo-icon">🔍</div>
                    <h3>Nenhuma reserva encontrada</h3>
                    <p>Tente buscar com outros termos</p>
                </div>
            `;
            return;
        }

        container.innerHTML = reservas.map(reserva => `
            <div class="reserva-card ${reserva.status}">
                <div class="reserva-status">
                    ${reserva.status === 'active' ? '🟢 ATIVA' : '✅ CONCLUÍDA'}
                </div>
                <div class="reserva-content">
                    <div class="reserva-info">
                        <h3>${reserva.veiculo}</h3>
                        <p class="reserva-codigo">🍀 Código: ${reserva.codigo}</p>
                        <p class="reserva-periodo">📅 ${reserva.periodo}</p>
                        <p class="reserva-local">🏢 ${reserva.agencia}</p>
                        <p class="reserva-valor">💵 Valor: R$ ${reserva.valor.toFixed(2)}</p>
                    </div>
                    <div class="reserva-actions">
                        <button class="btn-detalhes" data-id="${reserva.id}">Ver detalhes</button>
                        ${reserva.status === 'active' ? 
                            `<button class="btn-cancelar" data-id="${reserva.id}">Cancelar reserva</button>` : 
                            `<button class="btn-repetir" data-id="${reserva.id}">Alugar novamente</button>`
                        }
                    </div>
                </div>
            </div>
        `).join('');
    }

    mostrarDetalhes(id) {
        const reserva = this.reservas.find(r => r.id === id);
        if (reserva) {
            alert(`🍀 **Detalhes da Reserva**\n\n` +
                  `Código: ${reserva.codigo}\n` +
                  `Veículo: ${reserva.veiculo}\n` +
                  `Período: ${reserva.periodo}\n` +
                  `Agência: ${reserva.agencia}\n` +
                  `Valor: R$ ${reserva.valor.toFixed(2)}\n` +
                  `Status: ${reserva.status === 'active' ? 'Ativa' : 'Concluída'}`);
        }
    }

    cancelarReserva(id) {
        const reserva = this.reservas.find(r => r.id === id);
        if (reserva && confirm(`Tem certeza que deseja cancelar a reserva ${reserva.codigo}?`)) {
            // Remove a reserva (ou marca como cancelada)
            this.reservas = this.reservas.filter(r => r.id !== id);
            this.salvarNoStorage();
            this.renderizarReservas();
            alert('Reserva cancelada com sucesso! 🍀');
        }
    }

    repetirReserva(id) {
        const reserva = this.reservas.find(r => r.id === id);
        if (reserva) {
            alert(`🍀 Redirecionando para nova reserva do ${reserva.veiculo}...\n\n` +
                  `Em um sistema real, isso abriria a página de reservas com o veículo pré-selecionado!`);
        }
    }

    // MÉTODO PARA ADICIONAR NOVAS RESERVAS (usado pela página de pagamentos)
    adicionarReserva(novaReserva) {
        novaReserva.id = Date.now(); // ID único
        novaReserva.dataCriacao = new Date().toISOString();
        novaReserva.status = 'active'; // Sempre começa como ativa
        
        this.reservas.unshift(novaReserva); // Adiciona no início
        this.salvarNoStorage();
        this.renderizarReservas();
        
        console.log('🐞 Nova reserva adicionada:', novaReserva);
    }
}

// Inicializar sistema
document.addEventListener('DOMContentLoaded', function() {
    window.reservasSystem = new ReservasSystem();
});

// Função global para adicionar reservas de outras páginas
window.adicionarNovaReserva = function(dadosReserva) {
    if (window.reservasSystem) {
        window.reservasSystem.adicionarReserva(dadosReserva);
    } else {
        // Se o sistema não estiver carregado, salva para depois
        let reservasPendentes = JSON.parse(localStorage.getItem('trevocar_reservas_pendentes') || '[]');
        reservasPendentes.push(dadosReserva);
        localStorage.setItem('trevocar_reservas_pendentes', JSON.stringify(reservasPendentes));
    }
};
// Função para abrir páginas do menu
function abrirPagina(pagina) {
    const paginas = {
        'reservas': 'paginas-perfil/reservas.html',
        'perfil': 'paginas-perfil/perfil.html', 
        'veiculos': 'paginas-perfil/veiculos.html',
        'pagamentos': 'paginas-perfil/pagamentos.html',
        'favoritos': 'paginas-perfil/favoritos.html'
    };
    
    if (paginas[pagina]) {
        window.location.href = paginas[pagina];
    }
}