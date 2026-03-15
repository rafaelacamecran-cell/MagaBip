from app import create_app
from extensions import db
from sqlalchemy import text
import sys

app = create_app()
with app.app_context():
    try:
        print("Testando conexão com o banco...")
        result = db.session.execute(text("SELECT 1")).fetchone()
        print(f"Conexão OK: {result}")
        
        print("\nVerificando colunas da tabela 'users'...")
        # Postgres query to list columns
        query = text("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'users' 
            ORDER BY ordinal_position;
        """)
        cols = db.session.execute(query).fetchall()
        for col in cols:
            print(f"- {col[0]} ({col[1]})")
            
    except Exception as e:
        print(f"\nERRO: {e}")
        sys.exit(1)
