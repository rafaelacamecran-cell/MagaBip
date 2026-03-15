from app import create_app
from extensions import db
from models import User

app = create_app()

with app.app_context():
    # 1. DIGITE O LOGIN DO USUÁRIO QUE VAI VIRAR LÍDER AQUI:
    login_alvo = "melc_santos"  # Substitua pelo login do usuário alvo
    
    user = User.query.filter_by(username=login_alvo).first()
    
    if user:
        print(f"Usuário encontrado: {user.name} | Cargo atual: {user.role}")
        
        # 2. ALTERA O CARGO
        user.role = 'Liderança' # Use 'lideranca' (sem acento)
        
        db.session.commit()
        print(f"SUCESSO! O cargo de {user.name} foi alterado para LIDERANÇA.")
    else:
        print("ERRO: Usuário não encontrado.")