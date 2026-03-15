from app import create_app
from extensions import db
from models import Device, Filial

app = create_app()
with app.app_context():
    print("--- EQUIPAMENTOS (DEVICES) ---")
    devices = Device.query.all()
    print(f"Total de equipamentos: {len(devices)}")
    
    counts = {}
    for d in devices:
        filial_nome = d.filial.nome if d.filial else "N/A"
        counts[filial_nome] = counts.get(filial_nome, 0) + 1
    
    for filial, count in counts.items():
        print(f"Filial: {filial}, Quantidade: {count}")

    print("\n--- FILIAIS DISPONÍVEIS ---")
    filiais = Filial.query.all()
    for f in filiais:
        print(f"ID: {f.id}, Nome: {f.nome}")
