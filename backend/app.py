from flask import Flask, jsonify, request, send_from_directory, render_template, session, redirect, url_for
from flask_cors import CORS
import mysql.connector
from mysql.connector import Error
import os
import hashlib
import re
import bcrypt
import time
from functools import wraps
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'sua_chave_secreta_existente'  # Mantenha a mesma chave
CORS(app)

class Database:
    def __init__(self):
        self.host = 'localhost'
        self.database = 'trevocar'
        self.user = 'root'
        self.password = 'mota1413@'
        
    def get_connection(self):
        try:
            connection = mysql.connector.connect(
                host=self.host,
                database=self.database,
                user=self.user,
                password=self.password
            )
            if connection.is_connected():
                print("✅ Conectado ao MySQL!")
                return connection
        except Error as e:
            print(f"❌ Erro ao conectar com MySQL: {e}")
            return None

db = Database()

# Função para hash de senha
def hash_senha(senha):
    return hashlib.sha256(senha.encode()).hexdigest()

# ========== ROTAS DO FRONTEND ==========
@app.route('/')
def serve_index():
    return send_from_directory('../', 'index.html')

@app.route('/<path:filename>')
def serve_static(filename):
    return send_from_directory('../', filename)

@app.route('/css/<path:filename>')
def serve_css(filename):
    return send_from_directory('../css', filename)

@app.route('/js/<path:filename>')
def serve_js(filename):
    return send_from_directory('../js', filename)

@app.route('/templates/paginas-perfil/<path:filename>')
def serve_profile_pages(filename):
    return send_from_directory('../templates/paginas-perfil', filename)

# ========== ROTAS DA API (CLIENTES) ==========
@app.route('/api/test')
def test():
    return jsonify({'message': '✅ Backend TrevoCar funcionando!'})

# ROTA DE CADASTRO (CLIENTES)
@app.route('/api/cadastro', methods=['POST'])
def cadastro():
    try:
        data = request.json
        nome = data.get('nome')
        email = data.get('email')
        senha = data.get('senha')
        telefone = data.get('telefone', '')
        
        print(f"📝 Tentativa de cadastro: {email}")
        
        # Validações
        if not nome or not email or not senha:
            return jsonify({'success': False, 'message': 'Preencha todos os campos obrigatórios'}), 400
        
        if len(senha) < 6:
            return jsonify({'success': False, 'message': 'Senha deve ter pelo menos 6 caracteres'}), 400
        
        # Validar email
        if not re.match(r'^[^\s@]+@[^\s@]+\.[^\s@]+$', email):
            return jsonify({'success': False, 'message': 'Email inválido'}), 400
        
        conn = db.get_connection()
        if conn:
            cursor = conn.cursor(dictionary=True)
            
            # Verificar se email já existe
            cursor.execute("SELECT id FROM usuarios WHERE email = %s", (email,))
            if cursor.fetchone():
                return jsonify({'success': False, 'message': 'Email já cadastrado'}), 400
            
            # Hash da senha
            senha_hash = hash_senha(senha)
            
            # Inserir novo usuário - APENAS CAMPOS OBRIGATÓRIOS
            cursor.execute("""
                INSERT INTO usuarios (nome, email, telefone, senha_hash, tipo) 
                VALUES (%s, %s, %s, %s, 'cliente')
            """, (nome, email, telefone, senha_hash))
            
            conn.commit()
            
            # Buscar usuário criado (apenas campos básicos)
            cursor.execute("""
                SELECT id, nome, email, telefone, tipo, data_criacao 
                FROM usuarios WHERE email = %s
            """, (email,))
            novo_usuario = cursor.fetchone()
            
            cursor.close()
            conn.close()
            
            print(f"✅ Usuário cadastrado: {email}")
            return jsonify({
                'success': True, 
                'message': 'Cadastro realizado com sucesso!',
                'usuario': novo_usuario
            })
                
    except Error as e:
        print(f"❌ Erro no MySQL: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500
    except Exception as e:
        print(f"❌ Erro geral: {e}")
        return jsonify({'success': False, 'error': 'Erro interno do servidor'}), 500
    
    return jsonify({'success': False, 'error': 'Erro de conexão'}), 500

# ROTA DE LOGIN (CLIENTES) - FUNÇÃO ORIGINAL MANTIDA
@app.route('/api/login', methods=['POST'])
def login_cliente():
    try:
        data = request.json
        email = data.get('email')
        senha = data.get('senha')
        
        print(f"🔐 Tentativa de login CLIENTE: {email}")
        
        if not email or not senha:
            return jsonify({'success': False, 'message': 'Email e senha são obrigatórios'}), 400
        
        conn = db.get_connection()
        if conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM usuarios WHERE email = %s", (email,))
            usuario = cursor.fetchone()
            
            if usuario:
                # Verificar senha com hash
                senha_hash = hash_senha(senha)
                if usuario['senha_hash'] == senha_hash:
                    # Criar resposta sem dados sensíveis
                    usuario_response = {
                        'id': usuario['id'],
                        'nome': usuario['nome'],
                        'email': usuario['email'],
                        'telefone': usuario.get('telefone', ''),
                        'tipo': usuario.get('tipo', 'cliente')
                    }
                    
                    print(f"✅ Login CLIENTE bem-sucedido: {email}")
                    return jsonify({
                        'success': True,
                        'usuario': usuario_response,
                        'message': 'Login realizado com sucesso!'
                    })
                else:
                    print(f"❌ Senha incorreta: {email}")
                    return jsonify({'success': False, 'message': 'Email ou senha incorretos'}), 401
            else:
                print(f"❌ Usuário não encontrado: {email}")
                return jsonify({'success': False, 'message': 'Email ou senha incorretos'}), 401
                
            cursor.close()
            conn.close()
                
    except Error as e:
        print(f"❌ Erro no MySQL: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500
    except Exception as e:
        print(f"❌ Erro geral: {e}")
        return jsonify({'success': False, 'error': 'Erro interno do servidor'}), 500
    
    return jsonify({'success': False, 'error': 'Erro de conexão'}), 500

# ROTA PARA BUSCAR USUÁRIO (COMPLETO) - FUNÇÃO ORIGINAL MANTIDA
@app.route('/api/usuario/<email>', methods=['GET'])
def get_usuario_completo(email):
    print(f"📥 Buscando usuário COMPLETO: {email}")
    
    conn = db.get_connection()
    if conn:
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("""
                SELECT id, nome, email, telefone, cpf, data_nascimento,
                       cep, rua, numero, complemento, bairro, cidade, estado,
                       notificacao_email, notificacao_sms, categoria_preferida,
                       tipo, data_criacao
                FROM usuarios WHERE email = %s
            """, (email,))
            usuario = cursor.fetchone()
            
            if usuario:
                print(f"✅ Usuário encontrado: {usuario['nome']}")
                return jsonify({'success': True, 'usuario': usuario})
            else:
                print(f"❌ Usuário não encontrado: {email}")
                return jsonify({'success': False, 'message': 'Usuário não encontrado'}), 404
                
        except Error as e:
            print(f"❌ Erro no MySQL: {e}")
            return jsonify({'success': False, 'error': str(e)}), 500
        finally:
            cursor.close()
            conn.close()
    return jsonify({'success': False, 'error': 'Erro de conexão'}), 500

# ROTA PARA ATUALIZAR USUÁRIO - FUNÇÃO ORIGINAL MANTIDA
@app.route('/api/usuario/<email>', methods=['PUT'])
def update_usuario(email):
    print(f"🔄 Recebendo atualização para: {email}")
    print(f"📦 Dados recebidos: {request.json}")
    
    data = request.json
    conn = db.get_connection()
    
    if conn:
        try:
            cursor = conn.cursor()
            
            # Função para converter strings vazias em None
            def clean_value(value):
                if value == '' or value is None:
                    return None
                return value
            
            # Função ESPECIAL para data - trata datas vazias
            def clean_date(value):
                if value == '' or value is None:
                    return None
                # Se for uma data válida no formato YYYY-MM-DD
                if isinstance(value, str) and re.match(r'^\d{4}-\d{2}-\d{2}$', value):
                    return value
                return None
            
            # Limpar os valores antes de enviar para o MySQL
            nome = clean_value(data.get('nome'))
            telefone = clean_value(data.get('telefone'))
            cpf = clean_value(data.get('cpf'))
            nascimento = clean_date(data.get('nascimento'))
            cep = clean_value(data.get('cep'))
            rua = clean_value(data.get('rua'))
            numero = clean_value(data.get('numero'))
            complemento = clean_value(data.get('complemento'))
            bairro = clean_value(data.get('bairro'))
            cidade = clean_value(data.get('cidade'))
            estado = clean_value(data.get('estado'))
            notificacao_email = 1 if data.get('notificacaoEmail') else 0
            notificacao_sms = 1 if data.get('notificacaoSMS') else 0
            categoria_preferida = clean_value(data.get('categoriaPreferida'))
            
            query = """
                UPDATE usuarios SET 
                nome = %s, telefone = %s, cpf = %s, data_nascimento = %s,
                cep = %s, rua = %s, numero = %s, complemento = %s,
                bairro = %s, cidade = %s, estado = %s,
                notificacao_email = %s, notificacao_sms = %s, categoria_preferida = %s
                WHERE email = %s
            """
            values = (
                nome, telefone, cpf, nascimento,
                cep, rua, numero, complemento,
                bairro, cidade, estado,
                notificacao_email, notificacao_sms, categoria_preferida,
                email
            )
            
            print(f"🎯 Executando query com valores: {values}")
            print(f"📅 Data de nascimento processada: '{nascimento}' (tipo: {type(nascimento)})")
            
            cursor.execute(query, values)
            conn.commit()
            
            print("✅ Perfil atualizado no MySQL!")
            return jsonify({'success': True, 'message': 'Perfil atualizado com sucesso!'})
            
        except Error as e:
            print(f"❌ Erro no MySQL: {e}")
            return jsonify({'success': False, 'error': str(e)}), 500
        finally:
            cursor.close()
            conn.close()
    return jsonify({'success': False, 'error': 'Erro de conexão'}), 500

# ========== SISTEMA DE FUNCIONÁRIOS (NOVAS ROTAS) ==========

# Decorator para verificar login de funcionários
def login_funcionario_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'funcionario_id' not in session:
            return redirect(url_for('login_funcionarios_page'))
        return f(*args, **kwargs)
    return decorated_function

# Decorator para verificar se é administrador
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'cargo' not in session or session['cargo'] != 'administrador':
            return jsonify({'error': 'Acesso não autorizado'}), 403
        return f(*args, **kwargs)
    return decorated_function

# Página de login para funcionários
@app.route('/login-funcionarios')
def login_funcionarios_page():
   return send_from_directory('templates/funcionario', 'loginfuncionario.html')

@app.route('/dashboard-funcionarios')
def dashboard_funcionarios():
    cargo = session.get('cargo', '')
    funcionario_nome = session.get('funcionario_nome', 'Administrador')
    
    print(f"🎯 Dashboard acessado - Cargo: {cargo}, Nome: {funcionario_nome}")
    
    if cargo == 'administrador':
        return redirect(f'/dashboard-admin?nome={funcionario_nome}&cargo={cargo}')
    elif cargo == 'manutencionista':
        return redirect(f'/dashboard-manutencionista?nome={funcionario_nome}&cargo={cargo}')
    elif cargo == 'motorista':
        return redirect(f'/dashboard-motorista?nome={funcionario_nome}&cargo={cargo}')
    elif cargo == 'agenciador':
        return redirect(f'/dashboard-agenciador?nome={funcionario_nome}&cargo={cargo}')
    else:
        return redirect('/login-funcionarios')

# Rotas específicas para cada dashboard
@app.route('/dashboard-admin')
def dashboard_admin():
    nome = request.args.get('nome', 'Administrador')
    cargo = request.args.get('cargo', 'administrador')
    return send_from_directory('../templates/funcionario', 'dashboard_admin.html')

@app.route('/dashboard-manutencionista')
def dashboard_manutencionista():
    nome = request.args.get('nome', 'Manutencionista')
    return send_from_directory('../templates/funcionario', 'dashboard_manutencionista.html')

@app.route('/dashboard-motorista')
def dashboard_motorista():
    nome = request.args.get('nome', 'Motorista')
    return send_from_directory('../templates/funcionario', 'dashboard_motorista.html')

@app.route('/dashboard-agenciador')
def dashboard_agenciador():
    nome = request.args.get('nome', 'Agenciador')
    return send_from_directory('../templates/funcionario', 'dashboard_agenciador.html')
       
# Login para funcionários (ROTA DIFERENTE DA DOS CLIENTES)
@app.route('/api/login-funcionarios', methods=['POST'])
def login_funcionario():
    try:
        print("🎯 ROTA LOGIN FUNCIONARIOS ACIONADA")
        print("📦 Headers:", dict(request.headers))
        print("🔍 Content-Type:", request.content_type)
        
        # Verifica se tem dados JSON
        if not request.is_json:
            print("❌ Content-Type não é JSON")
            return jsonify({'success': False, 'error': 'Content-Type deve ser application/json'}), 400
        
        data = request.get_json()
        print("📥 Dados JSON recebidos:", data)
        
        # Extrai e valida campos
        id_funcionario = data.get('id')
        senha = data.get('senha')
        
        print(f"🔐 ID extraído: '{id_funcionario}' (tipo: {type(id_funcionario)})")
        print(f"🔐 Senha extraída: '{senha}' (tipo: {type(senha)})")
        
        # Validação rigorosa
        if id_funcionario is None or senha is None:
            print("❌ Campos faltando no JSON")
            return jsonify({'success': False, 'error': 'Campos "id" e "senha" são obrigatórios'}), 400
        
        if id_funcionario == '' or senha == '':
            print("❌ Campos vazios")
            return jsonify({'success': False, 'error': 'ID e senha não podem estar vazios'}), 400
        
        print(f"🚀 Buscando funcionário ID: {id_funcionario} no banco...")
        
        conn = db.get_connection()
        if not conn:
            print("❌ Falha na conexão com o banco")
            return jsonify({'success': False, 'error': 'Erro de conexão com o banco'}), 500
        
        cursor = conn.cursor(dictionary=True)
        
        # Busca funcionário
        cursor.execute("""
            SELECT id, nome, email, cargo, senha_hash 
            FROM funcionarios 
            WHERE id = %s AND ativo = TRUE
        """, (id_funcionario,))
        
        funcionario = cursor.fetchone()
        cursor.close()
        conn.close()
        
        print(f"🔍 Resultado da busca: {funcionario}")
        
        if not funcionario:
            print("❌ Nenhum funcionário encontrado com este ID ou inativo")
            return jsonify({'success': False, 'error': 'Credenciais inválidas'}), 401
        
        print(f"✅ Funcionário encontrado: {funcionario['nome']} ({funcionario['cargo']})")
        print(f"🔑 Hash no banco: {funcionario['senha_hash'][:20]}...")
        
        # Verifica senha
        try:
            senha_valida = bcrypt.checkpw(
                senha.encode('utf-8'), 
                funcionario['senha_hash'].encode('utf-8')
            )
            print(f"🔑 Senha válida: {senha_valida}")
        except Exception as bcrypt_error:
            print(f"❌ Erro ao verificar senha: {bcrypt_error}")
            return jsonify({'success': False, 'error': 'Erro na verificação de senha'}), 500
        
        if not senha_valida:
            print("❌ Senha incorreta")
            return jsonify({'success': False, 'error': 'Credenciais inválidas'}), 401
        
        # Cria sessão
        session['funcionario_id'] = funcionario['id']
        session['funcionario_nome'] = funcionario['nome']
        session['cargo'] = funcionario['cargo']
        
        print(f"✅ Login bem-sucedido! Sessão criada:")
        print(f"   - ID: {session['funcionario_id']}")
        print(f"   - Nome: {session['funcionario_nome']}")
        print(f"   - Cargo: {session['cargo']}")
        
        return jsonify({
            'success': True,
            'funcionario': {
                'id': funcionario['id'],
                'nome': funcionario['nome'],
                'cargo': funcionario['cargo']
            },
            'message': 'Login realizado com sucesso!'
        })
        
    except Exception as e:
        print(f"💥 ERRO GERAL no login: {str(e)}")
        print(f"💥 Tipo do erro: {type(e).__name__}")
        import traceback
        print(f"💥 Traceback: {traceback.format_exc()}")
        
        return jsonify({
            'success': False, 
            'error': 'Erro interno do servidor'
        }), 500

@app.route('/api/funcionarios', methods=['POST'])
def cadastrar_funcionario():
    try:
        print("📝 Tentativa de cadastro de funcionário recebida")
        data = request.get_json()
        print(f"📦 Dados recebidos: {data}")
        
        # Validar dados
        campos_obrigatorios = ['nome', 'email', 'telefone', 'cpf', 'endereco', 'cargo', 'senha']
        for campo in campos_obrigatorios:
            if not data.get(campo):
                print(f"❌ Campo obrigatório faltando: {campo}")
                return jsonify({'success': False, 'error': f'Campo {campo} é obrigatório'}), 400

        conn = db.get_connection()
        if not conn:
            print("❌ Erro de conexão com o banco")
            return jsonify({'success': False, 'error': 'Erro de conexão com o banco'}), 500
            
        cursor = conn.cursor(dictionary=True)
        
        # Verificar se email ou CPF já existem
        cursor.execute("SELECT id FROM funcionarios WHERE email = %s OR cpf = %s", 
                    (data['email'], data['cpf']))
        
        if cursor.fetchone():
            cursor.close()
            conn.close()
            print("❌ Email ou CPF já cadastrado")
            return jsonify({'success': False, 'error': 'Email ou CPF já cadastrado'}), 400

        # Hash da senha
        senha_hash = bcrypt.hashpw(data['senha'].encode('utf-8'), bcrypt.gensalt())
        print("✅ Senha hash criada")

        # Inserir no banco
        cursor.execute("""
            INSERT INTO funcionarios 
            (nome, email, telefone, cpf, endereco, cargo, senha_hash) 
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (data['nome'], data['email'], data['telefone'], data['cpf'], 
            data['endereco'], data['cargo'], senha_hash.decode('utf-8')))

        conn.commit()
        novo_id = cursor.lastrowid
        cursor.close()
        conn.close()

        print(f"✅ Funcionário cadastrado com ID: {novo_id}")
        return jsonify({
            'success': True,
            'message': 'Funcionário cadastrado com sucesso',
            'id': novo_id
        }), 201

    except Exception as e:
        print(f"❌ Erro no cadastro de funcionário: {e}")
        return jsonify({'success': False, 'error': 'Erro interno do servidor'}), 500

# Redefinir senha de funcionários
@app.route('/api/redefinir-senha-funcionario', methods=['POST'])
def redefinir_senha_funcionario():
    return jsonify({'success': True, 'message': 'Funcionalidade em desenvolvimento'})

# Logout de funcionários
@app.route('/logout-funcionarios')
def logout_funcionarios():
    session.clear()
    return redirect(url_for('serve_index'))

# ========== APIS PARA DASHBOARD ADMINISTRATIVO ==========

# API para listar veículos
@app.route('/api/veiculos', methods=['GET'])
def get_veiculos():
    try:
        print("🚗 Buscando lista de veículos...")
        
        conn = db.get_connection()
        if conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("""
                SELECT v.id_veiculo, v.placa, v.modelo, v.ano, v.cor, 
                       v.quilometragem, v.status, v.data_criacao,
                       c.nome as categoria_nome, c.preco_diaria,
                       f.nome as filial_nome
                FROM veiculo v
                LEFT JOIN categoria_veiculo c ON v.id_categoria = c.id_categoria
                LEFT JOIN filial f ON v.id_filial = f.id_filial
                ORDER BY v.data_criacao DESC
                LIMIT 50
            """)
            
            veiculos = cursor.fetchall()
            cursor.close()
            conn.close()
            
            print(f"✅ {len(veiculos)} veículos encontrados")
            
            # Converter Decimal para float para JSON
            for veiculo in veiculos:
                if veiculo['quilometragem']:
                    veiculo['quilometragem'] = float(veiculo['quilometragem'])
                if veiculo['preco_diaria']:
                    veiculo['preco_diaria'] = float(veiculo['preco_diaria'])
                if veiculo['data_criacao']:
                    veiculo['data_criacao'] = veiculo['data_criacao'].isoformat()
            
            return jsonify({
                'success': True,
                'veiculos': veiculos,
                'total': len(veiculos)
            })
            
    except Error as e:
        print(f"❌ Erro ao buscar veículos: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500
    except Exception as e:
        print(f"❌ Erro geral: {e}")
        return jsonify({'success': False, 'error': 'Erro interno do servidor'}), 500
    
    return jsonify({'success': False, 'error': 'Erro de conexão'}), 500

# API para listar funcionários
@app.route('/api/funcionarios', methods=['GET'])
def get_funcionarios():
    try:
        print("👥 Buscando lista de funcionários...")
        
        conn = db.get_connection()
        if conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("""
                SELECT id, nome, email, telefone, cpf, cargo, 
                       data_cadastro, ativo
                FROM funcionarios 
                ORDER BY data_cadastro DESC
            """)
            
            funcionarios = cursor.fetchall()
            cursor.close()
            conn.close()
            
            print(f"✅ {len(funcionarios)} funcionários encontrados")
            
            # Converter dados para JSON
            for func in funcionarios:
                if func['data_cadastro']:
                    func['data_cadastro'] = func['data_cadastro'].isoformat()
                func['ativo'] = bool(func['ativo'])
            
            return jsonify({
                'success': True,
                'funcionarios': funcionarios,
                'total': len(funcionarios)
            })
            
    except Error as e:
        print(f"❌ Erro ao buscar funcionários: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500
    except Exception as e:
        print(f"❌ Erro geral: {e}")
        return jsonify({'success': False, 'error': 'Erro interno do servidor'}), 500
    
    return jsonify({'success': False, 'error': 'Erro de conexão'}), 500

# API para listar filiais
@app.route('/api/filiais', methods=['GET'])
def get_filiais():
    try:
        print("🏢 Buscando lista de filiais...")
        
        conn = db.get_connection()
        if conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("""
                SELECT id_filial, nome, endereco
                FROM filial 
                ORDER BY nome
            """)
            
            filiais = cursor.fetchall()
            cursor.close()
            conn.close()
            
            print(f"✅ {len(filiais)} filiais encontradas")
            
            return jsonify({
                'success': True,
                'filiais': filiais,
                'total': len(filiais)
            })
            
    except Error as e:
        print(f"❌ Erro ao buscar filiais: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500
    except Exception as e:
        print(f"❌ Erro geral: {e}")
        return jsonify({'success': False, 'error': 'Erro interno do servidor'}), 500
    
    return jsonify({'success': False, 'error': 'Erro de conexão'}), 500

# API para listar categorias de veículos
@app.route('/api/categorias', methods=['GET'])
def get_categorias():
    try:
        print("📋 Buscando lista de categorias...")
        
        conn = db.get_connection()
        if conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("""
                SELECT id_categoria, nome, preco_diaria
                FROM categoria_veiculo 
                ORDER BY preco_diaria DESC
            """)
            
            categorias = cursor.fetchall()
            cursor.close()
            conn.close()
            
            print(f"✅ {len(categorias)} categorias encontradas")
            
            # Converter Decimal para float
            for categoria in categorias:
                if categoria['preco_diaria']:
                    categoria['preco_diaria'] = float(categoria['preco_diaria'])
            
            return jsonify({
                'success': True,
                'categorias': categorias,
                'total': len(categorias)
            })
            
    except Error as e:
        print(f"❌ Erro ao buscar categorias: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500
    except Exception as e:
        print(f"❌ Erro geral: {e}")
        return jsonify({'success': False, 'error': 'Erro interno do servidor'}), 500
    
    return jsonify({'success': False, 'error': 'Erro de conexão'}), 500

# API para estatísticas do dashboard
@app.route('/api/estatisticas', methods=['GET'])
def get_estatisticas():
    try:
        print("📊 Buscando estatísticas do dashboard...")
        
        conn = db.get_connection()
        if conn:
            cursor = conn.cursor(dictionary=True)
            
            # Total de veículos
            cursor.execute("SELECT COUNT(*) as total FROM veiculo")
            total_veiculos = cursor.fetchone()['total']
            
            # Veículos por status
            cursor.execute("""
                SELECT status, COUNT(*) as quantidade 
                FROM veiculo 
                GROUP BY status
            """)
            status_veiculos = cursor.fetchall()
            
            # Total de funcionários
            cursor.execute("SELECT COUNT(*) as total FROM funcionarios WHERE ativo = TRUE")
            total_funcionarios = cursor.fetchone()['total']
            
            # Funcionários por cargo
            cursor.execute("""
                SELECT cargo, COUNT(*) as quantidade 
                FROM funcionarios 
                WHERE ativo = TRUE
                GROUP BY cargo
            """)
            funcionarios_cargo = cursor.fetchall()
            
            # Total de filiais
            cursor.execute("SELECT COUNT(*) as total FROM filial")
            total_filiais = cursor.fetchone()['total']
            
            # Total de categorias
            cursor.execute("SELECT COUNT(*) as total FROM categoria_veiculo")
            total_categorias = cursor.fetchone()['total']
            
            cursor.close()
            conn.close()
            
            estatisticas = {
                'total_veiculos': total_veiculos,
                'status_veiculos': status_veiculos,
                'total_funcionarios': total_funcionarios,
                'funcionarios_cargo': funcionarios_cargo,
                'total_filiais': total_filiais,
                'total_categorias': total_categorias
            }
            
            print(f"✅ Estatísticas carregadas: {estatisticas}")
            
            return jsonify({
                'success': True,
                'estatisticas': estatisticas
            })
            
    except Error as e:
        print(f"❌ Erro ao buscar estatísticas: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500
    except Exception as e:
        print(f"❌ Erro geral: {e}")
        return jsonify({'success': False, 'error': 'Erro interno do servidor'}), 500
    
    return jsonify({'success': False, 'error': 'Erro de conexão'}), 500

# API para criar novo veículo
@app.route('/api/veiculos', methods=['POST'])
def criar_veiculo():
    try:
        print("🚗 Criando novo veículo...")
        data = request.get_json()
        
        # Validação dos campos obrigatórios
        campos_obrigatorios = ['placa', 'modelo', 'ano', 'cor', 'id_categoria', 'id_filial']
        for campo in campos_obrigatorios:
            if not data.get(campo):
                return jsonify({'success': False, 'error': f'Campo {campo} é obrigatório'}), 400
        
        conn = db.get_connection()
        if conn:
            cursor = conn.cursor()
            
            # Verificar se placa já existe
            cursor.execute("SELECT id_veiculo FROM veiculo WHERE placa = %s", (data['placa'],))
            if cursor.fetchone():
                cursor.close()
                conn.close()
                return jsonify({'success': False, 'error': 'Placa já cadastrada'}), 400
            
            # Inserir novo veículo
            cursor.execute("""
                INSERT INTO veiculo 
                (placa, modelo, ano, cor, quilometragem, status, id_categoria, id_filial) 
                VALUES (%s, %s, %s, %s, %s, 'disponível', %s, %s)
            """, (
                data['placa'], data['modelo'], data['ano'], data['cor'],
                data.get('quilometragem', 0), data['id_categoria'], data['id_filial']
            ))
            
            conn.commit()
            novo_id = cursor.lastrowid
            cursor.close()
            conn.close()
            
            print(f"✅ Veículo criado com ID: {novo_id}")
            
            return jsonify({
                'success': True,
                'message': 'Veículo cadastrado com sucesso',
                'id_veiculo': novo_id
            }), 201
            
    except Error as e:
        print(f"❌ Erro ao criar veículo: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500
    except Exception as e:
        print(f"❌ Erro geral: {e}")
        return jsonify({'success': False, 'error': 'Erro interno do servidor'}), 500
    
    return jsonify({'success': False, 'error': 'Erro de conexão'}), 500

# API para criar nova filial
@app.route('/api/filiais', methods=['POST'])
def criar_filial():
    try:
        print("🏢 Criando nova filial...")
        data = request.get_json()
        
        # Validação
        if not data.get('nome') or not data.get('endereco'):
            return jsonify({'success': False, 'error': 'Nome e endereço são obrigatórios'}), 400
        
        conn = db.get_connection()
        if conn:
            cursor = conn.cursor()
            
            # Inserir nova filial
            cursor.execute("""
                INSERT INTO filial (nome, endereco) 
                VALUES (%s, %s)
            """, (data['nome'], data['endereco']))
            
            conn.commit()
            novo_id = cursor.lastrowid
            cursor.close()
            conn.close()
            
            print(f"✅ Filial criada com ID: {novo_id}")
            
            return jsonify({
                'success': True,
                'message': 'Filial cadastrada com sucesso',
                'id_filial': novo_id
            }), 201
            
    except Error as e:
        print(f"❌ Erro ao criar filial: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500
    except Exception as e:
        print(f"❌ Erro geral: {e}")
        return jsonify({'success': False, 'error': 'Erro interno do servidor'}), 500
    
    return jsonify({'success': False, 'error': 'Erro de conexão'}), 500

# API para criar nova categoria
@app.route('/api/categorias', methods=['POST'])
def criar_categoria():
    try:
        print("📋 Criando nova categoria...")
        data = request.get_json()
        
        # Validação
        if not data.get('nome') or not data.get('preco_diaria'):
            return jsonify({'success': False, 'error': 'Nome e preço diária são obrigatórios'}), 400
        
        conn = db.get_connection()
        if conn:
            cursor = conn.cursor()
            
            # Inserir nova categoria
            cursor.execute("""
                INSERT INTO categoria_veiculo (nome, preco_diaria) 
                VALUES (%s, %s)
            """, (data['nome'], float(data['preco_diaria'])))
            
            conn.commit()
            novo_id = cursor.lastrowid
            cursor.close()
            conn.close()
            
            print(f"✅ Categoria criada com ID: {novo_id}")
            
            return jsonify({
                'success': True,
                'message': 'Categoria cadastrada com sucesso',
                'id_categoria': novo_id
            }), 201
            
    except Error as e:
        print(f"❌ Erro ao criar categoria: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500
    except Exception as e:
        print(f"❌ Erro geral: {e}")
        return jsonify({'success': False, 'error': 'Erro interno do servidor'}), 500
    
    return jsonify({'success': False, 'error': 'Erro de conexão'}), 500

# API para listar reservas
@app.route('/api/reservas', methods=['GET'])
def get_reservas():
    try:
        print("📋 Buscando lista de reservas...")
        
        conn = db.get_connection()
        if conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("""
                SELECT r.*, u.nome as usuario_nome, v.modelo as veiculo_modelo
                FROM reservas r
                LEFT JOIN usuarios u ON r.usuario_id = u.id
                LEFT JOIN veiculo v ON r.id_veiculo = v.id_veiculo
                ORDER BY r.data_criacao DESC
            """)
            
            reservas = cursor.fetchall()
            cursor.close()
            conn.close()
            
            print(f"✅ {len(reservas)} reservas encontradas")
            
            # Converter dados para JSON
            for reserva in reservas:
                if reserva['data_retirada']:
                    reserva['data_retirada'] = reserva['data_retirada'].isoformat()
                if reserva['data_devolucao']:
                    reserva['data_devolucao'] = reserva['data_devolucao'].isoformat()
                if reserva['data_criacao']:
                    reserva['data_criacao'] = reserva['data_criacao'].isoformat()
                if reserva['valor']:
                    reserva['valor'] = float(reserva['valor'])
            
            return jsonify({
                'success': True,
                'reservas': reservas,
                'total': len(reservas)
            })
            
    except Error as e:
        print(f"❌ Erro ao buscar reservas: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500
    except Exception as e:
        print(f"❌ Erro geral: {e}")
        return jsonify({'success': False, 'error': 'Erro interno do servidor'}), 500
    
    return jsonify({'success': False, 'error': 'Erro de conexão'}), 500

# API para atualizar status da reserva
@app.route('/api/reservas/status', methods=['PUT'])
def atualizar_status_reserva():
    try:
        print("🔄 Atualizando status da reserva...")
        data = request.get_json()
        
        reserva_id = data.get('reserva_id')
        novo_status = data.get('novo_status')
        motivo_cancelamento = data.get('motivo_cancelamento', '')
        
        if not reserva_id or not novo_status:
            return jsonify({'success': False, 'error': 'ID da reserva e novo status são obrigatórios'}), 400
        
        conn = db.get_connection()
        if conn:
            cursor = conn.cursor()
            
            if novo_status == 'cancelled' and not motivo_cancelamento:
                return jsonify({'success': False, 'error': 'Motivo do cancelamento é obrigatório'}), 400
            
            # Atualizar reserva
            if novo_status == 'cancelled':
                cursor.execute("""
                    UPDATE reservas 
                    SET status = %s, motivo_cancelamento = %s 
                    WHERE id = %s
                """, (novo_status, motivo_cancelamento, reserva_id))
            else:
                cursor.execute("""
                    UPDATE reservas 
                    SET status = %s, motivo_cancelamento = NULL 
                    WHERE id = %s
                """, (novo_status, reserva_id))
            
            # Se a reserva foi concluída, liberar o veículo
            if novo_status == 'completed':
                cursor.execute("""
                    UPDATE veiculo v
                    JOIN reservas r ON v.id_veiculo = r.id_veiculo
                    SET v.status = 'disponível'
                    WHERE r.id = %s
                """, (reserva_id,))
            
            conn.commit()
            cursor.close()
            conn.close()
            
            print(f"✅ Status da reserva {reserva_id} atualizado para {novo_status}")
            
            return jsonify({
                'success': True,
                'message': 'Status da reserva atualizado com sucesso'
            })
            
    except Error as e:
        print(f"❌ Erro ao atualizar status: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500
    except Exception as e:
        print(f"❌ Erro geral: {e}")
        return jsonify({'success': False, 'error': 'Erro interno do servidor'}), 500
    
    return jsonify({'success': False, 'error': 'Erro de conexão'}), 500   

# API para listar clientes
@app.route('/api/clientes', methods=['GET'])
def get_clientes():
    try:
        print("👥 Buscando lista de clientes...")
        
        conn = db.get_connection()
        if conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("""
                SELECT id, nome, email, telefone, cpf
                FROM usuarios 
                WHERE tipo = 'cliente'
                ORDER BY nome
            """)
            
            clientes = cursor.fetchall()
            cursor.close()
            conn.close()
            
            print(f"✅ {len(clientes)} clientes encontrados")
            
            return jsonify({
                'success': True,
                'clientes': clientes,
                'total': len(clientes)
            })
            
    except Exception as e:
        print(f"❌ Erro ao buscar clientes: {e}")
        return jsonify({'success': False, 'error': 'Erro interno do servidor'}), 500
    
    return jsonify({'success': False, 'error': 'Erro de conexão'}), 500

# API para listar veículos disponíveis
@app.route('/api/veiculos-disponiveis', methods=['GET'])
def get_veiculos_disponiveis():
    try:
        print("🚗 Buscando veículos disponíveis...")
        
        conn = db.get_connection()
        if conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("""
                SELECT v.*, c.nome as categoria_nome, c.preco_diaria
                FROM veiculo v
                LEFT JOIN categoria_veiculo c ON v.id_categoria = c.id_categoria
                WHERE v.status = 'disponível'
                ORDER BY v.modelo
            """)
            
            veiculos = cursor.fetchall()
            cursor.close()
            conn.close()
            
            print(f"✅ {len(veiculos)} veículos disponíveis encontrados")
            
            # Converter Decimal para float
            for veiculo in veiculos:
                if veiculo['preco_diaria']:
                    veiculo['preco_diaria'] = float(veiculo['preco_diaria'])
                if veiculo['quilometragem']:
                    veiculo['quilometragem'] = float(veiculo['quilometragem'])
            
            return jsonify({
                'success': True,
                'veiculos': veiculos,
                'total': len(veiculos)
            })
            
    except Exception as e:
        print(f"❌ Erro ao buscar veículos disponíveis: {e}")
        return jsonify({'success': False, 'error': 'Erro interno do servidor'}), 500
    
    return jsonify({'success': False, 'error': 'Erro de conexão'}), 500

# API para criar nova reserva (VERSÃO CORRIGIDA)
@app.route('/api/reservas', methods=['POST'])
def criar_reserva():
    try:
        print("🎯 CRIANDO RESERVA...")
        data = request.get_json()
        print("📦 Dados recebidos:", data)
        
        # Validação básica
        if not data.get('usuario_id') or not data.get('id_veiculo'):
            return jsonify({'success': False, 'error': 'Dados incompletos'}), 400
        
        conn = db.get_connection()
        if not conn:
            return jsonify({'success': False, 'error': 'Sem conexão com banco'}), 500
            
        cursor = conn.cursor()
        
        # INSERÇÃO COM CAMPO AGENCIA
        cursor.execute("""
            INSERT INTO reservas 
            (usuario_id, id_veiculo, codigo, veiculo, data_retirada, data_devolucao, 
             local_retirada, local_devolucao, valor, agencia, status) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 'active')
        """, (
            data['usuario_id'], 
            data['id_veiculo'], 
            data.get('codigo', 'RES' + str(int(time.time()))[-6:]),
            data.get('veiculo', 'Veículo Teste'),
            data.get('data_retirada'),
            data.get('data_devolucao'),
            data.get('local_retirada'),
            data.get('local_devolucao'),
            data.get('valor', 100.00),
            'Trevocar Agenciador'  # ← VALOR FIXO PARA AGENCIA
        ))
        
        conn.commit()
        novo_id = cursor.lastrowid
        cursor.close()
        conn.close()
        
        print(f"✅ RESERVA CRIADA COM SUCESSO! ID: {novo_id}")
        
        return jsonify({
            'success': True,
            'message': 'Reserva criada com sucesso!',
            'id_reserva': novo_id
        }), 201
        
    except Exception as e:
        print(f"💥 ERRO: {str(e)}")
        import traceback
        print(f"💥 TRACEBACK: {traceback.format_exc()}")
        return jsonify({'success': False, 'error': f'Erro: {str(e)}'}), 500

# API para buscar dados de um veículo específico
@app.route('/api/veiculo/<int:veiculo_id>', methods=['GET'])
def get_veiculo(veiculo_id):
    try:
        conn = db.get_connection()
        if conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("""
                SELECT v.*, c.preco_diaria, c.nome as categoria_nome
                FROM veiculo v
                LEFT JOIN categoria_veiculo c ON v.id_categoria = c.id_categoria
                WHERE v.id_veiculo = %s
            """, (veiculo_id,))
            
            veiculo = cursor.fetchone()
            cursor.close()
            conn.close()
            
            if veiculo:
                # Converter Decimal para float
                if veiculo.get('preco_diaria'):
                    veiculo['preco_diaria'] = float(veiculo['preco_diaria'])
                if veiculo.get('quilometragem'):
                    veiculo['quilometragem'] = float(veiculo['quilometragem'])
                
                return jsonify({
                    'success': True,
                    'veiculo': veiculo
                })
            else:
                return jsonify({'success': False, 'error': 'Veículo não encontrado'}), 404
                
    except Exception as e:
        print(f"❌ Erro ao buscar veículo: {e}")
        return jsonify({'success': False, 'error': 'Erro interno do servidor'}), 500
    
    return jsonify({'success': False, 'error': 'Erro de conexão'}), 500

# ========== ROTAS DE MANUTENÇÃO ==========

@app.route('/api/manutencao/veiculos', methods=['GET'])
def get_veiculos_manutencao():
    """Buscar veículos para manutenção"""
    try:
        conn = db.get_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("""
            SELECT v.*, c.nome as categoria_nome 
            FROM veiculo v 
            LEFT JOIN categoria_veiculo c ON v.id_categoria = c.id_categoria
            ORDER BY v.placa
        """)
        veiculos = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return jsonify(veiculos)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/manutencao/veiculos-em-manutencao', methods=['GET'])
def get_veiculos_em_manutencao():
    """Buscar veículos em manutenção"""
    try:
        conn = db.get_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("""
            SELECT v.*, c.nome as categoria_nome 
            FROM veiculo v 
            LEFT JOIN categoria_veiculo c ON v.id_categoria = c.id_categoria
            WHERE v.status = 'em manutenção'
            ORDER BY v.placa
        """)
        veiculos = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return jsonify(veiculos)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/manutencao/registrar', methods=['POST'])
def registrar_manutencao():
    """Registrar nova manutenção"""
    try:
        data = request.json
        conn = db.get_connection()
        cursor = conn.cursor()
        
        # Atualizar status do veículo
        cursor.execute(
            "UPDATE veiculo SET status = 'em manutenção' WHERE id_veiculo = %s",
            (data['id_veiculo'],)
        )
        
        # Criar tabela de manutenções se não existir
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS manutencao (
                id_manutencao INT AUTO_INCREMENT PRIMARY KEY,
                id_veiculo INT,
                motivo TEXT,
                data_inicio DATETIME,
                data_fim DATETIME,
                status ENUM('em_andamento', 'concluida'),
                FOREIGN KEY (id_veiculo) REFERENCES veiculo(id_veiculo)
            )
        """)
        
        # Registrar manutenção
        cursor.execute("""
            INSERT INTO manutencao (id_veiculo, motivo, data_inicio, status)
            VALUES (%s, %s, %s, 'em_andamento')
        """, (data['id_veiculo'], data['motivo'], datetime.now()))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({'success': True, 'message': 'Manutenção registrada com sucesso!'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/manutencao/concluir', methods=['POST'])
def concluir_manutencao():
    """Concluir manutenção"""
    try:
        data = request.json
        conn = db.get_connection()
        cursor = conn.cursor()
        
        # Atualizar status do veículo para disponível
        cursor.execute(
            "UPDATE veiculo SET status = 'disponível' WHERE id_veiculo = %s",
            (data['id_veiculo'],)
        )
        
        # Atualizar registro de manutenção
        cursor.execute("""
            UPDATE manutencao 
            SET data_fim = %s, status = 'concluida'
            WHERE id_veiculo = %s AND status = 'em_andamento'
        """, (datetime.now(), data['id_veiculo']))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({'success': True, 'message': 'Manutenção concluída com sucesso!'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/manutencao/historico', methods=['GET'])
def get_historico_manutencao():
    """Buscar histórico de manutenções"""
    try:
        conn = db.get_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("""
            SELECT m.*, v.placa, v.modelo 
            FROM manutencao m
            JOIN veiculo v ON m.id_veiculo = v.id_veiculo
            ORDER BY m.data_inicio DESC
        """)
        historico = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return jsonify(historico)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ========== SUBSTITUA O CONTEÚDO DESTAS APIS ==========

@app.route('/api/motorista/perfil', methods=['GET'])
def get_motorista_perfil():
    print("🎯 API /api/motorista/perfil ACESSADA!")
    return jsonify({
        'success': True,
        'motorista': {
            'id_motorista': 1,
            'nome': 'Manuel Batista',
            'cnh': '12345678901', 
            'disponibilidade': 'sim',
            'id_usuario': 1,
            'funcionario_nome': 'Manuel Batista'
        }
    })

@app.route('/api/motorista/disponibilidade', methods=['PUT'])
def atualizar_disponibilidade_motorista():
    print("🎯 API /api/motorista/disponibilidade ACESSADA!")
    data = request.json
    return jsonify({
        'success': True,
        'message': f'Disponibilidade {data.get("disponibilidade")} atualizada!'
    })

@app.route('/api/motorista/estatisticas', methods=['GET'])
def get_estatisticas_motorista():
    print("🎯 API /api/motorista/estatisticas ACESSADA!")
    return jsonify({
        'success': True,
        'estatisticas': {
            'total_viagens': 15,
            'viagens_pendentes': 2,
            'viagens_agendadas': 3, 
            'viagens_concluidas': 10
        }
    })

@app.route('/api/motorista/viagens/pendentes', methods=['GET'])
def get_viagens_pendentes():
    print("🎯 API /api/motorista/viagens/pendentes ACESSADA!")
    return jsonify({
        'success': True,
        'viagens': [
            {
                'id_viagem': 1,
                'cliente_nome': 'Maria Silva',
                'origem': 'Aeroporto Internacional',
                'destino': 'Hotel Central', 
                'data_viagem': '2024-01-20T14:30:00',
                'veiculo_solicitado': 'Toyota Corolla',
                'valor': 45.00,
                'passageiros': 2,
                'observacoes': 'Voo atrasado'
            }
        ]
    })

@app.route('/api/motorista/viagens/agendadas', methods=['GET'])
def get_viagens_agendadas():
    print("🎯 API /api/motorista/viagens/agendadas ACESSADA!")
    return jsonify({
        'success': True,
        'viagens': [
            {
                'id_viagem': 2,
                'cliente_nome': 'Carlos Santos',
                'origem': 'Shopping Center',
                'destino': 'Aeroporto',
                'data_viagem': '2024-01-21T08:00:00',
                'veiculo_solicitado': 'Honda Civic', 
                'valor': 60.00
            }
        ]
    })

@app.route('/api/motorista/viagens/historico', methods=['GET'])
def get_historico_viagens():
    print("🎯 API /api/motorista/viagens/historico ACESSADA!")
    return jsonify({
        'success': True,
        'viagens': [
            {
                'id_viagem': 3,
                'cliente_nome': 'Ana Costa',
                'origem': 'Estação Central',
                'destino': 'Universidade',
                'data_viagem': '2024-01-18T09:15:00',
                'veiculo_solicitado': 'Toyota Corolla',
                'valor': 20.00,
                'status': 'concluida'
            }
        ]
    })

@app.route('/api/motorista/viagens/<int:viagem_id>/aceitar', methods=['POST'])
def aceitar_viagem(viagem_id):
    print(f"🎯 API /api/motorista/viagens/{viagem_id}/aceitar ACESSADA!")
    return jsonify({'success': True, 'message': 'Viagem aceita!'})

@app.route('/api/motorista/viagens/<int:viagem_id>/recusar', methods=['POST'])
def recusar_viagem(viagem_id):
    print(f"🎯 API /api/motorista/viagens/{viagem_id}/recusar ACESSADA!")
    return jsonify({'success': True, 'message': 'Viagem recusada'})

@app.route('/api/motorista/viagens/<int:viagem_id>/iniciar', methods=['POST'])
def iniciar_viagem(viagem_id):
    print(f"🎯 API /api/motorista/viagens/{viagem_id}/iniciar ACESSADA!")
    return jsonify({'success': True, 'message': 'Viagem iniciada!'})

# ========== APIS PARA VIAGENS (COM NOMES ÚNICOS) ==========

@app.route('/api/viagens', methods=['POST'])
def criar_viagem_admin():
    try:
        print("🎯 CRIANDO NOVA VIAGEM...")
        data = request.get_json()
        print("📦 Dados recebidos:", data)
        
        # Validação básica
        if not data.get('id_cliente') or not data.get('origem') or not data.get('destino'):
            return jsonify({'success': False, 'error': 'Dados incompletos'}), 400
        
        conn = db.get_connection()
        if not conn:
            return jsonify({'success': False, 'error': 'Sem conexão com banco'}), 500
            
        cursor = conn.cursor()
        
        # Inserir viagem
        cursor.execute("""
            INSERT INTO viagens 
            (id_cliente, origem, destino, data_viagem, veiculo_solicitado, valor, passageiros, observacoes, status) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, 'pendente')
        """, (
            data['id_cliente'],
            data['origem'],
            data['destino'],
            data.get('data_viagem'),
            data.get('veiculo_solicitado'),
            data.get('valor', 0),
            data.get('passageiros', 1),
            data.get('observacoes', '')
        ))
        
        conn.commit()
        novo_id = cursor.lastrowid
        cursor.close()
        conn.close()
        
        print(f"✅ VIAGEM CRIADA COM SUCESSO! ID: {novo_id}")
        
        return jsonify({
            'success': True,
            'message': 'Viagem criada com sucesso!',
            'id_viagem': novo_id
        }), 201
        
    except Exception as e:
        print(f"💥 ERRO: {str(e)}")
        import traceback
        print(f"💥 TRACEBACK: {traceback.format_exc()}")
        return jsonify({'success': False, 'error': f'Erro: {str(e)}'}), 500

@app.route('/api/admin/clientes', methods=['GET'])
def get_clientes_admin():
    try:
        print("👥 Buscando lista de clientes...")
        
        conn = db.get_connection()
        if conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("""
                SELECT id, nome, email, telefone
                FROM usuarios 
                WHERE tipo = 'cliente'
                ORDER BY nome
            """)
            
            clientes = cursor.fetchall()
            cursor.close()
            conn.close()
            
            print(f"✅ {len(clientes)} clientes encontrados")
            
            return jsonify({
                'success': True,
                'clientes': clientes
            })
            
    except Exception as e:
        print(f"❌ Erro ao buscar clientes: {e}")
        return jsonify({'success': False, 'error': 'Erro interno do servidor'}), 500
    
    return jsonify({'success': False, 'error': 'Erro de conexão'}), 500

@app.route('/api/admin/funcionarios', methods=['GET'])
def get_funcionarios_admin():
    try:
        cargo = request.args.get('cargo')
        print(f"👥 Buscando funcionários - Cargo: {cargo}")
        
        conn = db.get_connection()
        if conn:
            cursor = conn.cursor(dictionary=True)
            
            if cargo:
                cursor.execute("""
                    SELECT id, nome, email, telefone, cargo
                    FROM funcionarios 
                    WHERE cargo = %s AND ativo = TRUE
                    ORDER BY nome
                """, (cargo,))
            else:
                cursor.execute("""
                    SELECT id, nome, email, telefone, cargo, ativo
                    FROM funcionarios 
                    ORDER BY data_cadastro DESC
                """)
            
            funcionarios = cursor.fetchall()
            cursor.close()
            conn.close()
            
            print(f"✅ {len(funcionarios)} funcionários encontrados")
            
            return jsonify({
                'success': True,
                'funcionarios': funcionarios
            })
            
    except Exception as e:
        print(f"❌ Erro ao buscar funcionários: {e}")
        return jsonify({'success': False, 'error': 'Erro interno do servidor'}), 500
    return jsonify({'success': False, 'error': 'Erro de conexão'}), 500
    
# ========== APIS PARA VIAGENS (ADMIN) ==========

@app.route('/api/admin/viagens', methods=['GET'])
def get_viagens_admin():
    try:
        print("🚗 Buscando lista de viagens para admin...")
        
        conn = db.get_connection()
        if conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("""
                SELECT 
                    v.id_viagem,
                    v.id_cliente,
                    v.id_motorista,
                    v.origem,
                    v.destino,
                    v.data_viagem,
                    v.veiculo_solicitado,
                    v.valor,
                    v.passageiros,
                    v.observacoes,
                    v.status,
                    v.data_criacao,
                    v.data_aceitacao,
                    v.data_inicio,
                    v.data_conclusao,
                    u.nome as nome_cliente,
                    f.nome as nome_motorista
                FROM viagens v
                LEFT JOIN usuarios u ON v.id_cliente = u.id
                LEFT JOIN funcionarios f ON v.id_motorista = f.id
                ORDER BY v.data_criacao DESC
            """)
            
            viagens = cursor.fetchall()
            cursor.close()
            conn.close()
            
            print(f"✅ {len(viagens)} viagens encontradas")
            
            # Converter dados para JSON
            for viagem in viagens:
                if viagem['data_viagem']:
                    viagem['data_viagem'] = viagem['data_viagem'].isoformat()
                if viagem['data_criacao']:
                    viagem['data_criacao'] = viagem['data_criacao'].isoformat()
                if viagem['data_aceitacao']:
                    viagem['data_aceitacao'] = viagem['data_aceitacao'].isoformat()
                if viagem['data_inicio']:
                    viagem['data_inicio'] = viagem['data_inicio'].isoformat()
                if viagem['data_conclusao']:
                    viagem['data_conclusao'] = viagem['data_conclusao'].isoformat()
                if viagem['valor']:
                    viagem['valor'] = float(viagem['valor'])
            
            return jsonify({
                'success': True,
                'viagens': viagens,
                'total': len(viagens)
            })
            
    except Exception as e:
        print(f"❌ Erro ao buscar viagens: {e}")
        return jsonify({'success': False, 'error': 'Erro interno do servidor'}), 500
    
    return jsonify({'success': False, 'error': 'Erro de conexão'}), 500

@app.route('/api/viagens', methods=['GET'])
def get_viagens():
    try:
        print("🚗 Buscando lista de viagens...")
        
        conn = db.get_connection()
        if conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("""
                SELECT 
                    v.id_viagem,
                    v.id_cliente,
                    v.id_motorista,
                    v.origem,
                    v.destino,
                    v.data_viagem,
                    v.veiculo_solicitado,
                    v.valor,
                    v.passageiros,
                    v.observacoes,
                    v.status,
                    v.data_criacao,
                    u.nome as nome_cliente,
                    f.nome as nome_motorista
                FROM viagens v
                LEFT JOIN usuarios u ON v.id_cliente = u.id
                LEFT JOIN funcionarios f ON v.id_motorista = f.id
                ORDER BY v.data_criacao DESC
            """)
            
            viagens = cursor.fetchall()
            cursor.close()
            conn.close()
            
            print(f"✅ {len(viagens)} viagens encontradas")
            
            # Converter dados para JSON
            for viagem in viagens:
                if viagem['data_viagem']:
                    viagem['data_viagem'] = viagem['data_viagem'].isoformat()
                if viagem['data_criacao']:
                    viagem['data_criacao'] = viagem['data_criacao'].isoformat()
                if viagem['valor']:
                    viagem['valor'] = float(viagem['valor'])
            
            return jsonify({
                'success': True,
                'viagens': viagens
            })
            
    except Exception as e:
        print(f"❌ Erro ao buscar viagens: {e}")
        return jsonify({'success': False, 'error': 'Erro interno do servidor'}), 500
    
    return jsonify({'success': False, 'error': 'Erro de conexão'}), 500

@app.route('/api/admin/motoristas', methods=['GET'])
def get_motoristas_admin():
    try:
        print("👨‍✈️ Buscando lista de motoristas...")
        
        conn = db.get_connection()
        if conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("""
                SELECT id, nome, email, telefone, cargo
                FROM funcionarios 
                WHERE cargo LIKE '%motorista%' AND ativo = TRUE
                ORDER BY nome
            """)
            
            motoristas = cursor.fetchall()
            cursor.close()
            conn.close()
            
            print(f"✅ {len(motoristas)} motoristas encontrados")
            
            return jsonify({
                'success': True,
                'motoristas': motoristas
            })
            
    except Exception as e:
        print(f"❌ Erro ao buscar motoristas: {e}")
        return jsonify({'success': False, 'error': 'Erro interno do servidor'}), 500
    
    return jsonify({'success': False, 'error': 'Erro de conexão'}), 500

# Ações para viagens
@app.route('/api/admin/viagens/<int:viagem_id>/aceitar', methods=['PUT'])
def aceitar_viagem_admin(viagem_id):
    try:
        print(f"✅ Aceitando viagem {viagem_id}...")
        
        conn = db.get_connection()
        if conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE viagens 
                SET status = 'aceita', data_aceitacao = NOW() 
                WHERE id_viagem = %s
            """, (viagem_id,))
            
            conn.commit()
            cursor.close()
            conn.close()
            
            print(f"✅ Viagem {viagem_id} aceita com sucesso")
            
            return jsonify({
                'success': True,
                'message': 'Viagem aceita com sucesso!'
            })
            
    except Exception as e:
        print(f"❌ Erro ao aceitar viagem: {e}")
        return jsonify({'success': False, 'error': 'Erro interno do servidor'}), 500
    
    return jsonify({'success': False, 'error': 'Erro de conexão'}), 500

@app.route('/api/admin/viagens/<int:viagem_id>/recusar', methods=['PUT'])
def recusar_viagem_admin(viagem_id):
    try:
        data = request.get_json()
        motivo = data.get('motivo', 'Motivo não informado')
        
        print(f"❌ Recusando viagem {viagem_id}...")
        
        conn = db.get_connection()
        if conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE viagens 
                SET status = 'recusada', observacoes = CONCAT(COALESCE(observacoes, ''), ' Motivo recusa: ', %s)
                WHERE id_viagem = %s
            """, (motivo, viagem_id))
            
            conn.commit()
            cursor.close()
            conn.close()
            
            print(f"✅ Viagem {viagem_id} recusada com sucesso")
            
            return jsonify({
                'success': True,
                'message': 'Viagem recusada com sucesso!'
            })
            
    except Exception as e:
        print(f"❌ Erro ao recusar viagem: {e}")
        return jsonify({'success': False, 'error': 'Erro interno do servidor'}), 500
    
    return jsonify({'success': False, 'error': 'Erro de conexão'}), 500

@app.route('/api/admin/viagens/<int:viagem_id>/iniciar', methods=['PUT'])
def iniciar_viagem_admin(viagem_id):
    try:
        print(f"🚀 Iniciando viagem {viagem_id}...")
        
        conn = db.get_connection()
        if conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE viagens 
                SET status = 'em_andamento', data_inicio = NOW() 
                WHERE id_viagem = %s
            """, (viagem_id,))
            
            conn.commit()
            cursor.close()
            conn.close()
            
            print(f"✅ Viagem {viagem_id} iniciada com sucesso")
            
            return jsonify({
                'success': True,
                'message': 'Viagem iniciada com sucesso!'
            })
            
    except Exception as e:
        print(f"❌ Erro ao iniciar viagem: {e}")
        return jsonify({'success': False, 'error': 'Erro interno do servidor'}), 500
    
    return jsonify({'success': False, 'error': 'Erro de conexão'}), 500

@app.route('/api/admin/viagens/<int:viagem_id>/concluir', methods=['PUT'])
def concluir_viagem_admin(viagem_id):
    try:
        print(f"🏁 Concluindo viagem {viagem_id}...")
        
        conn = db.get_connection()
        if conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE viagens 
                SET status = 'concluida', data_conclusao = NOW() 
                WHERE id_viagem = %s
            """, (viagem_id,))
            
            conn.commit()
            cursor.close()
            conn.close()
            
            print(f"✅ Viagem {viagem_id} concluída com sucesso")
            
            return jsonify({
                'success': True,
                'message': 'Viagem concluída com sucesso!'
            })
            
    except Exception as e:
        print(f"❌ Erro ao concluir viagem: {e}")
        return jsonify({'success': False, 'error': 'Erro interno do servidor'}), 500
    
    return jsonify({'success': False, 'error': 'Erro de conexão'}), 500

@app.route('/api/admin/viagens/<int:viagem_id>/cancelar', methods=['PUT'])
def cancelar_viagem_admin(viagem_id):
    try:
        print(f"❌ Cancelando viagem {viagem_id}...")
        
        conn = db.get_connection()
        if conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE viagens 
                SET status = 'cancelada' 
                WHERE id_viagem = %s
            """, (viagem_id,))
            
            conn.commit()
            cursor.close()
            conn.close()
            
            print(f"✅ Viagem {viagem_id} cancelada com sucesso")
            
            return jsonify({
                'success': True,
                'message': 'Viagem cancelada com sucesso!'
            })
            
    except Exception as e:
        print(f"❌ Erro ao cancelar viagem: {e}")
        return jsonify({'success': False, 'error': 'Erro interno do servidor'}), 500
    
    return jsonify({'success': False, 'error': 'Erro de conexão'}), 500

# API para editar veículo
@app.route('/api/veiculos/<int:veiculo_id>', methods=['PUT'])
def atualizar_veiculo(veiculo_id):
    try:
        print(f"✏️ Atualizando veículo {veiculo_id}...")
        data = request.get_json()
        
        conn = db.get_connection()
        if conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE veiculo 
                SET placa = %s, modelo = %s, ano = %s, cor = %s, 
                    quilometragem = %s, status = %s, id_categoria = %s, id_filial = %s
                WHERE id_veiculo = %s
            """, (
                data['placa'], data['modelo'], data['ano'], data['cor'],
                data.get('quilometragem', 0), data['status'], 
                data['id_categoria'], data['id_filial'], veiculo_id
            ))
            
            conn.commit()
            cursor.close()
            conn.close()
            
            print(f"✅ Veículo {veiculo_id} atualizado com sucesso")
            
            return jsonify({
                'success': True,
                'message': 'Veículo atualizado com sucesso!'
            })
            
    except Exception as e:
        print(f"❌ Erro ao atualizar veículo: {e}")
        return jsonify({'success': False, 'error': 'Erro interno do servidor'}), 500
    
    return jsonify({'success': False, 'error': 'Erro de conexão'}), 500

# API para excluir veículo
@app.route('/api/veiculos/<int:veiculo_id>', methods=['DELETE'])
def excluir_veiculo(veiculo_id):
    try:
        print(f"🗑️ Excluindo veículo {veiculo_id}...")
        
        conn = db.get_connection()
        if conn:
            cursor = conn.cursor()
            
            cursor.execute("DELETE FROM veiculo WHERE id_veiculo = %s", (veiculo_id,))
            
            conn.commit()
            cursor.close()
            conn.close()
            
            print(f"✅ Veículo {veiculo_id} excluído com sucesso")
            
            return jsonify({
                'success': True,
                'message': 'Veículo excluído com sucesso!'
            })
            
    except Exception as e:
        print(f"❌ Erro ao excluir veículo: {e}")
        return jsonify({'success': False, 'error': 'Erro interno do servidor'}), 500
    
    return jsonify({'success': False, 'error': 'Erro de conexão'}), 500


# ========== INICIAR SERVIDOR ==========
if __name__ == '__main__':
    print("TREVOCAR - SISTEMA DE LOCADORA")
    print("=====================================")
    print(" Servidor iniciado!")
    print(" Sistema de login/cadastro ativo!")
    print(" Sistema de funcionários ativo!")
    print(" Sistema de manutenção ativo!")
    print("Acesse: http://localhost:5000")
    print("=====================================")
    
    app.run(debug=True, host='0.0.0.0', port=5000)