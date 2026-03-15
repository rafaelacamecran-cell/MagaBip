from app import create_app
from extensions import db
from models import Filial, User

app = create_app()
with app.app_context():
    # ID 14 is CD 2650 based on previous diagnostic
    target_filial = Filial.query.get(14)
    if not target_filial:
        print("Erro: Filial CD 2650 (ID 14) não encontrada.")
    else:
        users_to_update = User.query.filter(User.filial_id == None).all()
        print(f"Atualizando {len(users_to_update)} usuários para {target_filial.nome}...")
        for u in users_to_update:
            u.filial_id = target_filial.id
        db.session.commit()
        print("Sucesso! Todos os usuários agora possuem filial.")
