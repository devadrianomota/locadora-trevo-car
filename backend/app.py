from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import mysql.connector
from mysql.connector import Error
import os
import hashlib
import re

app = Flask(__name__)
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

# ========== ROTAS DA API ==========
@app.route('/api/test')
def test():
    return jsonify({'message': '✅ Backend TrevoCar funcionando!'})

# ROTA DE CADASTRO
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

# ROTA DE LOGIN
@app.route('/api/login', methods=['POST'])
def login():
    try:
        data = request.json
        email = data.get('email')
        senha = data.get('senha')
        
        print(f"🔐 Tentativa de login: {email}")
        
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
                    
                    print(f"✅ Login bem-sucedido: {email}")
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

# ROTA PARA BUSCAR USUÁRIO
@app.route('/api/usuario/<email>', methods=['GET'])
def get_usuario(email):
    print(f"📥 Buscando usuário: {email}")
    
    conn = db.get_connection()
    if conn:
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT id, nome, email, telefone, tipo FROM usuarios WHERE email = %s", (email,))
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

# ROTA PARA ATUALIZAR USUÁRIO
@app.route('/api/usuario/<email>', methods=['PUT'])
def update_usuario(email):
    print(f"🔄 Recebendo atualização para: {email}")
    print(f"📦 Dados recebidos: {request.json}")
    
    data = request.json
    conn = db.get_connection()
    
    if conn:
        try:
            cursor = conn.cursor()
            query = """
                UPDATE usuarios SET 
                nome = %s, telefone = %s, cpf = %s, data_nascimento = %s,
                cep = %s, rua = %s, numero = %s, complemento = %s,
                bairro = %s, cidade = %s, estado = %s,
                notificacao_email = %s, notificacao_sms = %s, categoria_preferida = %s
                WHERE email = %s
            """
            values = (
                data.get('nome'), data.get('telefone'), data.get('cpf'), data.get('nascimento'),
                data.get('cep'), data.get('rua'), data.get('numero'), data.get('complemento'),
                data.get('bairro'), data.get('cidade'), data.get('estado'),
                data.get('notificacaoEmail'), data.get('notificacaoSMS'), data.get('categoriaPreferida'),
                email
            )
            
            print(f"🎯 Executando query com valores: {values}")
            
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

# ========== INICIAR SERVIDOR ==========
if __name__ == '__main__':
    print("🎓 TREVOCAR - SISTEMA DE LOCADORA")
    print("=====================================")
    print("🚀 Servidor iniciado!")
    print("📧 Sistema de login/cadastro ativo!")
    print("👤 Usuário teste: joao@email.com / 123456")
    print("🌐 Acesse: http://localhost:5000")
    print("=====================================")
    
    app.run(debug=True, host='0.0.0.0', port=5000)