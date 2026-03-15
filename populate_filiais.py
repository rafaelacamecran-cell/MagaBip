from app import create_app
from extensions import db
from models import Filial

app = create_app()
with app.app_context():
    # Lista de CDs comuns
    cds = [
        ("CD001", "001", "Louveira"),
        ("CD002", "002", "Franca"),
        ("CD010", "010", "Recife"),
        ("CD050", "050", "Cajamar"),
        ("CD051", "051", "Cajamar 2"),
        ("CD070", "070", "Extrema"),
        ("CD080", "080", "Gravataí"),
        ("CD090", "090", "Uberlândia"),
    ]
    
    # Criar uma carga automática maior se desejar (opcional)
    # Aqui vamos focar nos principais e nos que o usuário costuma ver
    
    print(">>> Populando Tabela de Filiais...")
    count = 0
    for nome, codigo, cidade in cds:
        if not Filial.query.filter_by(nome=nome).first():
            f = Filial(nome=nome, codigo=codigo, cidade=cidade)
            db.session.add(f)
            count += 1
    
    db.session.commit()
    print(f"Sucesso! {count} novas filiais adicionadas.")
