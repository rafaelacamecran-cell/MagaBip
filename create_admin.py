from app import create_app
from extensions import db
from models import User
from werkzeug.security import generate_password_hash
import sys

def create_or_promote_admin(username, password, name, colaborador_id):
    app = create_app()
    with app.app_context():
        user = User.query.filter_by(username=username).first()
        if user:
            print(f"Usuário {username} já existe. Atualizando dados e promovendo a 'ti'...")
            user.role = 'ti'
            user.name = name
            user.colaborador_id = colaborador_id
            user.must_change_password = False
            db.session.commit()
            print("Dados atualizados e promovido com sucesso!")
        else:
            print(f"Criando novo usuário admin {username}...")
            new_user = User(
                username=username,
                name=name,
                colaborador_id=colaborador_id,
                role='ti',
                password_hash=generate_password_hash(password),
                must_change_password=False
            )
            db.session.add(new_user)
            db.session.commit()
            print("Usuário admin criado com sucesso!")

if __name__ == "__main__":
    if len(sys.argv) < 5:
        print("Uso: python create_admin.py <usuario> <senha> <nome> <id_colaborador>")
    else:
        create_or_promote_admin(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])
