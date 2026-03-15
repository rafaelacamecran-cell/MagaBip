import os
import sys
from werkzeug.security import generate_password_hash
from psycopg2.extras import execute_values
from app import create_app
from extensions import db

def bulk_import_users(usuarios_lista):
    """
    Importa usuários em massa no banco de dados.
    usuarios_lista: lista de tuplas (nome, login, id_colaborador, senha_plana, cargo, turno, funcao)
    """
    app = create_app()
    
    with app.app_context():
        # Obtém a conexão bruta do psycopg2 através do engine do SQLAlchemy
        connection = db.engine.raw_connection()
        try:
            cursor = connection.cursor()
            
            # Preparamos os dados (hasheando as senhas e garantindo os campos corretos)
            dados_preparados = []
            for nome, login, id_col, senha, cargo, turno, funcao in usuarios_lista:
                senha_hash = generate_password_hash(senha)
                dados_preparados.append((
                    nome, 
                    login, 
                    id_col, 
                    senha_hash, 
                    cargo.lower(), # Normaliza para o padrão do sistema
                    turno, 
                    funcao,
                    True # must_change_password = True por segurança
                ))
            
            query = """
                INSERT INTO users (name, username, colaborador_id, password_hash, role, turno, funcao, must_change_password)
                VALUES %s
                ON CONFLICT (username) DO NOTHING
            """
            
            print(f"Iniciando inserção de {len(dados_preparados)} usuários...")
            execute_values(cursor, query, dados_preparados)
            connection.commit()
            print("Importação concluída com sucesso!")
            
        except Exception as e:
            connection.rollback()
            print(f"Erro durante a importação: {e}")
        finally:
            cursor.close()
            connection.close()

if __name__ == "__main__":
    # Exemplo de uso baseado no seu snippet
    # Adicionando o campo 'turno' e 'funcao' que também são necessários no sistema
    exemplo_usuarios = [
        ('João Silva', 'joao.silva', '123456', 'maga1234', 'colaborador', '1º Turno', 'Conferente'),
        ('Maria Souza', 'maria.souza', '654321', 'maga1234', 'lider', 'Administrativo', 'Gerente'),
    ]
    
    bulk_import_users(exemplo_usuarios)
