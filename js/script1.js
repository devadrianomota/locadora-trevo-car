

/*
================================================================
ARQUIVO: script1.js
USO: Apenas na página detalhesCarro.html
================================================================
*/

// Funções utilitárias
const RENTAL_DAYS = 2; // Duração fixa para cálculo dos extras
const parsePrice = (priceString) => parseFloat(priceString.replace('R$', '').replace(/\./g, '').replace(',', '.').trim()) || 0;
const formatPrice = (priceNumber) => new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(priceNumber);

document.addEventListener('DOMContentLoaded', () => {
    
    // Elementos de Preço
    const baseRentalElement = document.getElementById('base-rental-price');
    const taxesElement = document.getElementById('taxes-price');
    const finalTotalElement = document.getElementById('final-total');
    const extrasSummaryContainer = document.getElementById('extras-summary');
    
    // Checkboxes dos Extras
    const extraCheckboxes = document.querySelectorAll('input[type="checkbox"][data-extra-price]');
    
    // Preços Iniciais (lidos do HTML)
    // O valor base é lido do HTML. Se precisasse do preço vindo do secaoCarros2.html, 
    // usaríamos: parsePrice(localStorage.getItem('carBasePrice') || baseRentalElement.innerText)
    let baseRental = parsePrice(baseRentalElement ? baseRentalElement.innerText : '0');
    let taxes = parsePrice(taxesElement ? taxesElement.innerText : '0');
    
    let currentTotal = baseRental + taxes;
    
    // Função principal para calcular e atualizar a tela
    const updateSummaryAndTotal = () => {
        let extrasTotal = 0;
        let htmlExtras = '';

        extraCheckboxes.forEach(checkbox => {
            if (checkbox.checked) {
                const pricePerDay = parseFloat(checkbox.getAttribute('data-extra-price'));
                const days = parseFloat(checkbox.getAttribute('data-extra-days')) || RENTAL_DAYS;
                const extraName = checkbox.getAttribute('data-extra-name');
                
                const extraPriceTotal = pricePerDay * days;
                extrasTotal += extraPriceTotal;
                
                // Cria a linha HTML para o resumo do pedido
                htmlExtras += `
                    <div class="price-line extra-line">
                        <span style="color: var(--brand-green-dark); font-weight: 500;">+ ${extraName} (${days} dias)</span>
                        <span style="color: var(--brand-green-dark);">${formatPrice(extraPriceTotal)}</span>
                    </div>
                `;
            }
        });

        // Atualiza a seção de extras no resumo
        if (extrasSummaryContainer) {
            extrasSummaryContainer.innerHTML = htmlExtras;
        }

        // Calcula e exibe o novo Total Final
        currentTotal = baseRental + taxes + extrasTotal;
        if (finalTotalElement) {
            finalTotalElement.innerText = formatPrice(currentTotal);
        }
    };

    // Adiciona listener para recalcular o total a cada mudança de checkbox
    extraCheckboxes.forEach(checkbox => {
        checkbox.addEventListener('change', updateSummaryAndTotal);
    });

    // Inicia a atualização (garante que o total inicial está correto)
    updateSummaryAndTotal();


    // --- LÓGICA DE REDIRECIONAMENTO PARA PAGAMENTO ---
    const btnReservar = document.querySelector('.reserve-btn'); 

    if (btnReservar) {
        btnReservar.addEventListener('click', () => {
            // Salva o valor TOTAL final calculado (com extras) no localStorage
            localStorage.setItem('reservaTotal', currentTotal.toFixed(2));
            
            // Redireciona para a página de pagamento
            window.location.href = 'pagamentoCarro.html';
        });
    }
});