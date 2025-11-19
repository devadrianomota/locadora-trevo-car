/*
================================================================
ARQUIVO: script2.js
USO: secaoCarros2.html e pagamento.html
================================================================
*/

/*
================================================================
ARQUIVO: script2.js
USO: secaoCarros2.html, pagamentoCarro.html
================================================================
*/

// Aguarda o documento carregar
document.addEventListener('DOMContentLoaded', () => {
    
    // --- 1. CONTROLE DO MODAL DE MENSAGEM (Usado para a confirmação de Pagamento) ---
    const messageOverlay = document.getElementById('message-box-overlay');
    const messageText = document.getElementById('message-box-text');
    const closeButton = document.getElementById('message-box-close');

    window.mostrarMensagem = (texto) => {
        if (messageText && messageOverlay) {
            messageText.innerText = texto;
            messageOverlay.style.display = 'flex';
        }
    };

    if (closeButton && messageOverlay) {
        closeButton.addEventListener('click', () => {
            messageOverlay.style.display = 'none';
        });
    }

    // --- 2. LÓGICA DA PÁGINA DE FILTROS (secaoCarros2.html) ---
    
    // 2.1. Lógica do Filtro (Botão "Filtrar")
    const filterButton = document.getElementById('filter-button');
    const vehicleCards = document.querySelectorAll('.vehicle-card');
    
    if (filterButton) {
        filterButton.addEventListener('click', () => {
            const marca = document.getElementById('marca').value;
            const modelo = document.getElementById('modelo').value;
            const cor = document.getElementById('cor').value;
            const categoria = document.getElementById('categoria').value;

            vehicleCards.forEach(card => {
                const cardMarca = card.getAttribute('data-marca');
                const cardModelo = card.getAttribute('data-modelo');
                const cardCor = card.getAttribute('data-cor');
                const cardCategoria = card.getAttribute('data-categoria');

                const matchesMarca = marca === 'Todas' || cardMarca === marca;
                const matchesModelo = modelo === 'Todos' || cardModelo === modelo;
                const matchesCor = cor === 'Todas' || cardCor === cor;
                const matchesCategoria = categoria === 'Todas' || cardCategoria === categoria;

                if (matchesMarca && matchesModelo && matchesCor && matchesCategoria) {
                    // Se o card corresponder, exibe-o (usando 'flex' pois é o padrão de display do card)
                    card.style.display = 'flex'; 
                } else {
                    card.style.display = 'none';
                }
            });
        });
    }


    // 2.2. Funcionalidade do botão "Reservar" (Redirecionamento)
    // Alvo: <button class="alugar-btn"> do seu HTML
    const botoesReservar = document.querySelectorAll('.alugar-btn'); 
    
    botoesReservar.forEach(botao => {
        botao.addEventListener('click', () => {
            
            const pricePerDay = parseFloat(botao.getAttribute('data-car-price'));
            
            // Assume 2 dias de aluguel. No detalhesCarro.html, ajustaremos as diárias.
            const rentalDays = 2; 
            const basePriceForTwoDays = (pricePerDay * rentalDays).toFixed(2); 

            // Salva o preço da locação BASE (2 dias) no localStorage
            // O nome da chave é 'carBasePrice'
            localStorage.setItem('carBasePrice', basePriceForTwoDays); 
            
            // Redireciona para a página de detalhes
            window.location.href = 'detalhesCarro.html';
        });
    });
});