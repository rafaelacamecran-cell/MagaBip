from functools import wraps
from flask import redirect, url_for, session
from flask_login import current_user, login_user
from config import Config
from models import User
from extensions import db
from werkzeug.security import generate_password_hash

def smart_auth(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # CENÁRIO A: OAuth está ativado (Produção)
        if Config.USE_OAUTH:
            if not current_user.is_authenticated:
                return redirect(url_for('auth.login')) # Manda para o login do Google
            return f(*args, **kwargs)

        # CENÁRIO B: OAuth está desligado (Dev/Local)
        # Precisamos garantir que existe um usuário logado para não quebrar o código
        else:
            if not current_user.is_authenticated:
                # 1. Tenta achar o usuário "Dev" no banco
                dev_user = User.query.filter_by(username='dev_admin').first()
                
                # 2. Se não existe, cria ele agora (Auto-Setup)
                if not dev_user:
                    dev_user = User(
                        username='dev_admin',
                        name='Desenvolvedor (Modo Local)',
                        role='ti', # Damos acesso total para não travar nada
                        turno='Integral',
                        password_hash=generate_password_hash('dev')
                    )
                    db.session.add(dev_user)
                    db.session.commit()
                
                # 3. Força o login desse usuário automaticamente
                login_user(dev_user)
            
            # Executa a rota normalmente
            return f(*args, **kwargs)

    return decorated_function