from app import create_app
from extensions import db
from sqlalchemy import text

app = create_app()
with app.app_context():
    try:
        print(">>> INICIANDO CORREÇÃO MANUAL DO BANCO DE DADOS (MagaBip)...")
        
        # 1. CRIAR TABELA DE FILIAIS
        db.session.execute(text("""
            CREATE TABLE IF NOT EXISTS filiais (
                id SERIAL PRIMARY KEY,
                nome VARCHAR(120) UNIQUE NOT NULL,
                codigo VARCHAR(50) UNIQUE,
                cidade VARCHAR(100)
            );
        """))
        print("- Tabela 'filiais' verificada/criada.")

        # 2. ADICIONAR COLUNA FILIAL_ID NAS TABELAS
        tables = ['users', 'devices', 'checkout_logs', 'support_tickets', 'alertas_ti']
        for table in tables:
            try:
                db.session.execute(text(f"ALTER TABLE {table} ADD COLUMN filial_id INTEGER REFERENCES filiais(id);"))
                print(f"- Coluna 'filial_id' adicionada na tabela '{table}'.")
            except Exception as e:
                db.session.rollback()
                if "already exists" in str(e):
                    print(f"- Coluna 'filial_id' já existe na tabela '{table}'.")
                else:
                    print(f"! Erro ao alterar tabela '{table}': {e}")

        # 3. OUTRAS COLUNAS ÚTEIS
        try:
            db.session.execute(text("ALTER TABLE checkout_logs ADD COLUMN IF NOT EXISTS setor VARCHAR(100);"))
            db.session.execute(text("ALTER TABLE checkout_logs ADD COLUMN IF NOT EXISTS nivel_bateria VARCHAR(50);"))
            db.session.execute(text("ALTER TABLE checkout_logs ADD COLUMN IF NOT EXISTS observacoes TEXT;"))
            print("- Colunas extras de log verificadas.")
        except Exception:
            db.session.rollback()

        db.session.commit()
        print("\nBANCO DE DADOS ATUALIZADO COM SUCESSO!")
        print("Agora voce pode rodar o run.py e fazer login.")

    except Exception as e:
        db.session.rollback()
        print(f"\nERRO CRITICO NA MIGRACAO: {e}")

