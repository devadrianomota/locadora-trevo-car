// perfil.js - Sistema de perfil CONECTADO COM MYSQL
class PerfilSystem {
    constructor() {
        this.init();
    }

    init() {
        this.carregarDadosUsuario();
        this.configurarEventos();
        console.log('🐞 Sistema de perfil inicializado');
    }

    // FUNÇÃO PARA BUSCAR USUÁRIO DO BACKEND
    async carregarUsuarioDoBackend(email) {
        try {
            const response = await fetch(`http://localhost:5000/api/usuario/${email}`);
            const data = await response.json();
            
            if (data.success) {
                return data.usuario;
            } else {
                throw new Error(data.message);
            }
        } catch (error) {
            console.error('Erro ao carregar usuário:', error);
            throw error;
        }
    }

    // FUNÇÃO PARA ATUALIZAR USUÁRIO NO BACKEND
    async atualizarUsuarioNoBackend(email, dados) {
        try {
            const response = await fetch(`http://localhost:5000/api/usuario/${email}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(dados)
            });
            
            const data = await response.json();
            
            if (data.success) {
                return data;
            } else {
                throw new Error(data.error);
            }
        } catch (error) {
            console.error('Erro ao atualizar usuário:', error);
            throw error;
        }
    }

    async carregarDadosUsuario() {
        // Pega o usuário do localStorage (que veio do login)
        const usuarioStorage = localStorage.getItem('trevocar_usuario');
        
        if (usuarioStorage) {
            const usuario = JSON.parse(usuarioStorage);
            const email = usuario.email;
            
            console.log('📧 Carregando dados para:', email);
            
            try {
                // Busca dados COMPLETOS do backend
                const usuarioCompleto = await this.carregarUsuarioDoBackend(email);
                this.preencherFormulario(usuarioCompleto);
                console.log('✅ Dados carregados do MySQL:', usuarioCompleto);
            } catch (error) {
                console.error('❌ Erro ao carregar do backend:', error);
                // Fallback: usa dados do localStorage
                this.preencherFormulario(usuario);
            }
        } else {
            console.log('❌ Nenhum usuário logado');
            this.mostrarMensagem('Faça login para acessar seu perfil', 'error');
        }
    }

   preencherFormulario(usuario) {
    console.log('📝 Preenchendo formulário com:', usuario);
    console.log('🔍 DETALHES DO USUÁRIO:', {
        nome: usuario.nome,
        email: usuario.email, 
        telefone: usuario.telefone,
        cpf: usuario.cpf,
        data_nascimento: usuario.data_nascimento,
        cep: usuario.cep,
        rua: usuario.rua,
        numero: usuario.numero
    });
    
    // ... resto do código continua igual
        // Dados Pessoais
        document.getElementById('nome').value = usuario.nome || '';
        document.getElementById('email').value = usuario.email || '';
        document.getElementById('telefone').value = usuario.telefone || '';
        document.getElementById('cpf').value = usuario.cpf || '';
        document.getElementById('nascimento').value = usuario.data_nascimento || '';

        // Endereço
        document.getElementById('cep').value = usuario.cep || '';
        document.getElementById('rua').value = usuario.rua || '';
        document.getElementById('numero').value = usuario.numero || '';
        document.getElementById('complemento').value = usuario.complemento || '';
        document.getElementById('bairro').value = usuario.bairro || '';
        document.getElementById('cidade').value = usuario.cidade || '';
        document.getElementById('estado').value = usuario.estado || 'SP';

        // Preferências
        document.getElementById('notificacao-email').checked = usuario.notificacao_email !== false;
        document.getElementById('notificacao-sms').checked = usuario.notificacao_sms || false;
        document.getElementById('categoria-preferida').value = usuario.categoria_preferida || 'intermediario';

        // Avatar com iniciais
        const avatar = document.querySelector('.avatar');
        const iniciais = usuario.nome ? usuario.nome.split(' ').map(n => n[0]).join('').toUpperCase().substring(0, 2) : 'US';
        avatar.textContent = iniciais;
    }

    configurarEventos() {
        // Botão Salvar
        document.querySelector('.btn-salvar').addEventListener('click', (e) => {
            e.preventDefault();
            this.salvarPerfil();
        });

        // Botão Cancelar
        document.querySelector('.btn-cancelar').addEventListener('click', (e) => {
            e.preventDefault();
            if (confirm('Descartar todas as alterações?')) {
                this.carregarDadosUsuario();
            }
        });

        // Botão Alterar Senha
        document.querySelector('.btn-alterar-senha').addEventListener('click', (e) => {
            e.preventDefault();
            this.alterarSenha();
        });

        // Botão Alterar Foto
        document.querySelector('.btn-alterar-foto').addEventListener('click', (e) => {
            e.preventDefault();
            this.alterarFoto();
        });

        // Buscar CEP automático
        document.getElementById('cep').addEventListener('blur', (e) => {
            this.buscarCEP(e.target.value);
        });
    }

   coletarDadosFormulario() {
    const dados = {
        nome: document.getElementById('nome').value,
        telefone: document.getElementById('telefone').value,
        cpf: document.getElementById('cpf').value,
        nascimento: document.getElementById('nascimento').value,
        cep: document.getElementById('cep').value,
        rua: document.getElementById('rua').value,
        numero: document.getElementById('numero').value,
        complemento: document.getElementById('complemento').value,
        bairro: document.getElementById('bairro').value,
        cidade: document.getElementById('cidade').value,
        estado: document.getElementById('estado').value,
        notificacaoEmail: document.getElementById('notificacao-email').checked,
        notificacaoSMS: document.getElementById('notificacao-sms').checked,
        categoriaPreferida: document.getElementById('categoria-preferida').value
    };
    
    console.log('📋 Dados coletados do formulário:', dados);
    return dados;
}

   validarDados(dados) {
    console.log('🔍 Validando dados:', dados);
    
    // Só valida campos realmente obrigatórios
    if (!dados.nome || dados.nome.trim() === '') {
        this.mostrarMensagem('O campo Nome é obrigatório!', 'error');
        return false;
    }

    // Remove a validação de email (não editável no perfil)
    // if (!dados.email) {
    //     this.mostrarMensagem('E-mail é obrigatório!', 'error');
    //     return false;
    // }

    // if (!this.validarEmail(dados.email)) {
    //     this.mostrarMensagem('E-mail inválido!', 'error');
    //     return false;
    // }

    console.log('✅ Dados validados com sucesso');
    return true;
}

    validarEmail(email) {
        const regex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return regex.test(email);
    }

    async salvarPerfil() {
        const dados = this.coletarDadosFormulario();
        
        if (!this.validarDados(dados)) {
            return;
        }

        try {
            // Mostrar loading
            const btnSalvar = document.querySelector('.btn-salvar');
            const originalText = btnSalvar.textContent;
            btnSalvar.textContent = 'Salvando...';
            btnSalvar.disabled = true;
            
            // Pega o email do usuário logado
            const usuarioStorage = localStorage.getItem('trevocar_usuario');
            if (!usuarioStorage) {
                throw new Error('Usuário não está logado');
            }
            
            const usuario = JSON.parse(usuarioStorage);
            const email = usuario.email;
            
            console.log('💾 Salvando perfil para:', email, dados);
            
            // ✅ SALVA NO MYSQL
            const resultado = await this.atualizarUsuarioNoBackend(email, dados);
            
            // Atualiza localStorage com novos dados
            const usuarioAtualizado = { ...usuario, ...dados };
            localStorage.setItem('trevocar_usuario', JSON.stringify(usuarioAtualizado));
            
            this.mostrarMensagem('Perfil atualizado com sucesso! 🍀', 'success');
            console.log('💾 Perfil salvo no MySQL:', resultado);
            
        } catch (error) {
            this.mostrarMensagem('Erro ao salvar: ' + error.message, 'error');
            console.error('❌ Erro ao salvar perfil:', error);
        } finally {
            // Restaurar botão
            const btnSalvar = document.querySelector('.btn-salvar');
            btnSalvar.textContent = '💾 Salvar Alterações';
            btnSalvar.disabled = false;
        }
    }

    alterarSenha() {
        const novaSenha = prompt('Digite sua nova senha:');
        if (novaSenha && novaSenha.length >= 6) {
            this.mostrarMensagem('Senha alterada com sucesso! 🍀', 'success');
        } else if (novaSenha) {
            this.mostrarMensagem('A senha deve ter pelo menos 6 caracteres!', 'error');
        }
    }

    alterarFoto() {
        alert('Em uma versão real, isso abriria um seletor de arquivos para upload de foto!');
    }

    buscarCEP(cep) {
        if (cep.length === 8) {
            console.log(`🔍 Buscando endereço para CEP: ${cep}`);
            // Aqui integraria com uma API de CEP
        }
    }

    mostrarMensagem(mensagem, tipo = 'info') {
        // Remove mensagens anteriores
        const mensagensAntigas = document.querySelectorAll('.mensagem-flutuante');
        mensagensAntigas.forEach(msg => msg.remove());
        
        const messageElement = document.createElement('div');
        messageElement.textContent = mensagem;
        messageElement.className = 'mensagem-flutuante';
        messageElement.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 15px 20px;
            border-radius: 5px;
            color: white;
            font-weight: bold;
            z-index: 10000;
            transition: opacity 0.3s;
            background-color: ${tipo === 'success' ? '#27ae60' : tipo === 'error' ? '#e74c3c' : '#3498db'};
        `;
        
        document.body.appendChild(messageElement);
        
        setTimeout(() => {
            messageElement.style.opacity = '0';
            setTimeout(() => {
                if (messageElement.parentNode) {
                    document.body.removeChild(messageElement);
                }
            }, 300);
        }, 3000);
    }
}

// Inicializar sistema quando a página carregar
document.addEventListener('DOMContentLoaded', function() {
    console.log('🚀 Iniciando sistema de perfil...');
    window.perfilSystem = new PerfilSystem();
});