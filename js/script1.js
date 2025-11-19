

/*
================================================================
ARQUIVO: script1.js
USO: Apenas na página detalhesCarro.html (Carrega os dados via ID)
================================================================
*/

// Funções utilitárias
const RENTAL_DAYS = 2; 
const parsePrice = (priceString) => parseFloat(String(priceString).replace('R$', '').replace(/\./g, '').replace(',', '.').trim()) || 0;
const formatPrice = (priceNumber) => new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(priceNumber);


// ===================================================================
// BANCO DE DADOS DE CARROS (CAR_DETAILS_DB)
// Aqui você define todas as informações ÚNICAS de cada carro
// ===================================================================

const CAR_DETAILS_DB = [
    {
        id: 1,
        title: "JEEP COMPASS 1.3 TURBO",
        group: "Grupo LD - Star Especial",
        pricePerDay: 218.95,
        basePriceTotal: (218.95 * RENTAL_DAYS).toFixed(2),
        imgSrc: "imagens/jeep_compass.png",
        description: "Um SUV sofisticado e potente com motor 1.3 Turbo. Ideal para quem busca luxo, espaço e performance, tanto na cidade quanto em viagens longas.",
        specs: [
            { icon: '⚙️', detail: 'Câmbio Automático' },
            { icon: '❄️', detail: 'Ar Condicionado' },
            { icon: '👥', detail: '5 Ocupantes' },
            { icon: '🚪', detail: '4 Portas' },
            { icon: '⛽', detail: 'Flex' },
            { icon: '🛅', detail: '410L Porta-malas' }
        ]
    },
    {
        id: 2,
        title: "BYD Dolphin (OU SIMILAR)",
        group: "Grupo CE - Econômico Especial C/Ar",
        pricePerDay: 93.95,
        basePriceTotal: (93.95 * RENTAL_DAYS).toFixed(2),
        imgSrc: "imagens/byd_dolphin.png",
        description: "O carro perfeito para o dia a dia. Econômico, ágil e fácil de estacionar. Uma opção inteligente para locações curtas e uso urbano.",
        specs: [
            { icon: '⚙️', detail: 'Câmbio Manual' },
            { icon: '❄️', detail: 'Ar Condicionado' },
            { icon: '👥', detail: '5 Ocupantes' },
            { icon: '🚪', detail: '4 Portas' },
            { icon: '⚡', detail: 'Elétrico' },
            { icon: '🛅', detail: '345L Porta-malas' }
        ]
    },
    {
        id: 3,
        title: "BMW X1 (OU SIMILAR)",
        group: "Grupo SX - Suv Automático",
        pricePerDay: 161.95,
        basePriceTotal: (161.95 * RENTAL_DAYS).toFixed(2),
        imgSrc: "imagens/bmw_x1.png",
        description: "Luxo e performance em um SUV compacto e elegante. Experimente o conforto e a dirigibilidade premium da BMW.",
        specs: [
            { icon: '⚙️', detail: 'Câmbio Automático' },
            { icon: '❄️', detail: 'Ar Condicionado Dual Zone' },
            { icon: '👥', detail: '5 Ocupantes' },
            { icon: '🚪', detail: '4 Portas' },
            { icon: '⛽', detail: 'Gasolina' },
            { icon: '🛅', detail: '500L Porta-malas' }
        ]
    }
];

// ===================================================================
// LÓGICA PRINCIPAL
// ===================================================================

document.addEventListener('DOMContentLoaded', () => {

    // 1. OBTÉM O ID DO CARRO E SEUS DADOS COMPLETOS
    const selectedCarId = parseInt(localStorage.getItem('selectedCarId'));
    const carData = CAR_DETAILS_DB.find(car => car.id === selectedCarId);

    // Variáveis de Elementos (Ids)
    const baseRentalElement = document.getElementById('base-rental-price');
    const taxesElement = document.getElementById('taxes-price');
    const finalTotalElement = document.getElementById('final-total');
    const extrasSummaryContainer = document.getElementById('extras-summary');
    const extraCheckboxes = document.querySelectorAll('input[type="checkbox"][data-extra-price]');
    
    // Elementos da Visão Geral (para o novo conteúdo)
    const nameEl = document.getElementById('overview-car-name');
    const imgEl = document.getElementById('overview-car-img');
    const groupEl = document.getElementById('overview-car-group');
    const basePriceDisplayEl = document.getElementById('overview-base-price-display');
    const descriptionEl = document.getElementById('car-description-text');
    const specsListEl = document.getElementById('car-specs-list');

    let baseRental = 0;
    let taxes = parsePrice(taxesElement ? taxesElement.innerText : '0'); 

    if (carData) {
        // 2. POPULA O HTML COM OS DADOS DO CARRO ENCONTRADO
        baseRental = parsePrice(carData.basePriceTotal);
        
        // Visão Geral
        if (nameEl) nameEl.innerText = carData.title;
        if (groupEl) groupEl.innerText = carData.group;
        if (imgEl) imgEl.src = carData.imgSrc;
        if (basePriceDisplayEl) basePriceDisplayEl.innerText = formatPrice(baseRental);

        // Descrição e Especificações
        if (descriptionEl) descriptionEl.innerText = carData.description;
        if (specsListEl) {
            specsListEl.innerHTML = carData.specs.map(spec => 
                `<li><span class="icon">${spec.icon}</span>${spec.detail}</li>`
            ).join('');
        }

    } else {
        // Se não encontrar o ID, usa os valores padrão (hardcoded) do HTML
        baseRental = parsePrice(baseRentalElement ? baseRentalElement.innerText : '0');
        console.warn("Carro não encontrado. Verifique se o ID foi passado corretamente.");
    }
    
    // Atualiza o preço base no Resumo (Resumo)
    if (baseRentalElement) baseRentalElement.innerText = formatPrice(baseRental);


    // --- 3. LÓGICA DE CÁLCULO DE EXTRAS (MANTIDA) ---
    let currentTotal = baseRental + taxes;
    
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
                
                htmlExtras += `
                    <div class="price-line extra-line">
                        <span style="color: var(--brand-green-dark); font-weight: 500;">+ ${extraName} (${days} dias)</span>
                        <span style="color: var(--brand-green-dark);">${formatPrice(extraPriceTotal)}</span>
                    </div>
                `;
            }
        });

        if (extrasSummaryContainer) extrasSummaryContainer.innerHTML = htmlExtras;

        currentTotal = baseRental + taxes + extrasTotal;
        if (finalTotalElement) finalTotalElement.innerText = formatPrice(currentTotal);
    };

    extraCheckboxes.forEach(checkbox => {
        checkbox.addEventListener('change', updateSummaryAndTotal);
    });

    updateSummaryAndTotal(); // Chamada inicial


    // --- 4. LÓGICA DE REDIRECIONAMENTO PARA PAGAMENTO (MANTIDA) ---
    const btnReservar = document.querySelector('.reserve-btn');

    if (btnReservar) {
        btnReservar.addEventListener('click', () => {
            localStorage.setItem('reservaTotal', currentTotal.toFixed(2));
            window.location.href = 'pagamentoCarro.html';
        });
    }
});