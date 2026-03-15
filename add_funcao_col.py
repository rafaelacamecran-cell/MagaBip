from app import create_app
from extensions import db
from sqlalchemy import text

app = create_app()

with app.app_context():
    try:
        # Tenta adicionar a coluna funcao
        db.session.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS funcao VARCHAR(100)"))
        db.session.commit()
        print("Coluna 'funcao' adicionada com sucesso ou já existente.")
    except Exception as e:
        db.session.rollback()
        print(f"Erro ao adicionar coluna: {e}")
