from app import create_app
from extensions import db
from models import User
from werkzeug.security import generate_password_hash

# Inicializa a aplicação
app = create_app()

with app.app_context():
    # Defina aqui o usuário que deu erro e a nova senha que você quer
    alvo_usuario = "ra_camecran"
    nova_senha = "R@f@08049226*#"

    print(f"--> Procurando usuário: {alvo_usuario}...")
    
    # Busca o usuário no banco
    user = User.query.filter_by(username=alvo_usuario).first()
    
    if user:
        print("--> Usuário encontrado!")
        
        # Gera o hash seguro da nova senha
        # Nota: Se o seu model usa um método 'set_password', o ideal seria usá-lo,
        # mas vamos tentar atualizar o campo de hash diretamente para garantir.
        novo_hash = generate_password_hash(nova_senha)
        
        # Tenta identificar o nome do campo de senha (geralmente password_hash ou password)
        if hasattr(user, 'password_hash'):
            user.password_hash = novo_hash
            print("--> Atualizando campo 'password_hash'...")
        elif hasattr(user, 'password'):
            # Se for property, atribuir o texto plano aciona o setter
            # Se for coluna, atribuímos o hash. Vamos tentar o setter primeiro.
            try:
                user.password = nova_senha
            except:
                user.password = novo_hash
            print("--> Atualizando campo 'password'...")
            
        db.session.commit()
        print("----------------------------------------------------")
        print(f"SUCESSO! A senha de '{alvo_usuario}' foi alterada para: {nova_senha}")
        print("----------------------------------------------------")
    else:
        print(f"ERRO: Usuário '{alvo_usuario}' não encontrado no banco.")