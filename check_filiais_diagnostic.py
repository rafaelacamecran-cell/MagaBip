from app import create_app
from extensions import db
from models import Filial, User

app = create_app()
with app.app_context():
    print("--- FILIAIS ---")
    filiais = Filial.query.all()
    for f in filiais:
        print(f"ID: {f.id}, Nome: {f.nome}, Codigo: {f.codigo or 'N/A'}")
    
    print("\n--- USERS ---")
    users = User.query.all()
    for u in users:
        filial_nome = u.filial.nome if u.filial else "N/A"
        print(f"User: {u.username}, Filial: {filial_nome}")
