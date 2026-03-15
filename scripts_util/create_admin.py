from werkzeug.security import generate_password_hash
from extensions import db
from app import create_app
from models import User
    
# --- CONFIGURE AQUI ---
ADMIN_USERNAME = 'ra_camecran' # O login que você vai usar
ADMIN_PASSWORD = 'R@f@08049226*#' # A senha que você vai usar
ADMIN_NAME = 'TI'
# -----------------------
    
print("Iniciando script para criar admin...")
    
# Gera o hash da senha
password_hash = generate_password_hash(ADMIN_PASSWORD)
print(f"Hash da senha gerado.")
    
# Cria a aplicação Flask para ter o contexto do banco de dados
app = create_app()
    
with app.app_context():
        # Verifica se o usuário já existe
        user_exists = User.query.filter_by(username=ADMIN_USERNAME).first()
        if user_exists:
            print(f"Erro: Usuário '{ADMIN_USERNAME}' já existe no banco.")
        else:
            # Cria o novo usuário
            admin_user = User(
                username=ADMIN_USERNAME,
                name=ADMIN_NAME,
                password_hash=password_hash,
                role='ti', # Define como TI
                must_change_password=False # Admin não precisa trocar a senha
            )
            
            db.session.add(admin_user)
            db.session.commit()
            print(f"Sucesso! Usuário '{ADMIN_USERNAME}' (role=ti) foi criado.")
            print("Você já pode logar com ele.")

            # Fechar a sessão do banco de dados
            db.session.remove()

            # Finaliza a aplicação Flask
            app = None

            