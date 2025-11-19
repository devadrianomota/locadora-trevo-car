/*
================================================================
ARQUIVO: pagamentoCarro.js
USO: Apenas na página pagamento.html
================================================================
*/

// Função para formatar números como moeda BRL
function formatCurrency(value) {
    return value.toLocaleString('pt-BR', {
        style: 'currency',
        currency: 'BRL'
    });
}

// Aguarda o documento carregar
document.addEventListener('DOMContentLoaded', () => {

    // --- 1. CARREGAR DADOS DA PÁGINA DE DETALHES ---
    const subtotalSalvo = parseFloat(localStorage.getItem('reservaSubtotal'));
    const taxasSalvo = parseFloat(localStorage.getItem('reservaTaxas'));
    const totalSalvo = parseFloat(localStorage.getItem('reservaTotal'));

    // Seleciona os elementos no Resumo da Compra
    const subtotalEl = document.getElementById('resume-subtotal');
    const taxasEl = document.getElementById('resume-taxas');
    const totalEl = document.getElementById('resume-total');
    const installmentsSelect = document.getElementById('card-installments');

    if (totalSalvo) {
        // Atualiza os valores na tela
        subtotalEl.innerText = formatCurrency(subtotalSalvo);
        taxasEl.innerText = formatCurrency(taxasSalvo);
        totalEl.innerText = formatCurrency(totalSalvo);

        // --- PREENCHER PARCELAS DINAMICAMENTE ---
        installmentsSelect.innerHTML = ''; // Limpa o "Carregando..."
        for (let i = 1; i <= 3; i++) {
            const parcelValue = totalSalvo / i;
            const optionText = `${i}x de ${formatCurrency(parcelValue)} (sem juros)`;
            const option = new Option(optionText, i); // (text, value)
            installmentsSelect.add(option);
        }

    } else {
        subtotalEl.innerText = formatCurrency(0);
        taxasEl.innerText = formatCurrency(0);
        totalEl.innerText = formatCurrency(0);
        installmentsSelect.innerHTML = '<option>Valor não encontrado</option>';
    }

    // --- 2. FUNCIONALIDADE DAS ABAS (PIX, Cartão) ---
    const tabs = document.querySelectorAll('.tab-link');
    const contents = document.querySelectorAll('.payment-tab-content');

    tabs.forEach(tab => {
        tab.addEventListener('click', () => {
            const targetId = tab.getAttribute('data-tab');
            const targetContent = document.getElementById(`tab-${targetId}`);

            tabs.forEach(t => t.classList.remove('active'));
            contents.forEach(c => c.classList.remove('active'));

            tab.classList.add('active');
            targetContent.classList.add('active');
        });
    });

    // --- 3. MENSAGEM DE "RESERVA CONCLUÍDA" ---
    const btnFinalizar = document.getElementById('btn-finalizar-pedido');

    btnFinalizar.addEventListener('click', (e) => {
        e.preventDefault(); // Impede o envio do formulário
        const numeroPedido = Math.floor(Math.random() * 900000) + 100000;

        // Chama a função global do 'script2.js'
        if (window.mostrarMensagem) {
            window.mostrarMensagem(
                `Reserva concluída com sucesso!\n\nNúmero do Pedido: #${numeroPedido}`
            );
        } else {
            alert('Reserva concluída! (Erro ao carregar modal)');
        }
    });
});