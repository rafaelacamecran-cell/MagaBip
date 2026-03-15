from app import create_app
from extensions import db
from models import Device, CheckoutLog, SupportTicket, DeviceHealth, BehaviorLog

def seed_devices(filial_id=None):
    app = create_app()
    with app.app_context():
        # Se for passado um filial_id, vamos apenas adicionar para essa filial sem limpar tudo
        if filial_id:
             print(f"🚀 Semeando dispositivos para Filial ID: {filial_id}...")
        else:
            print("⏳ Limpando históricos, tickets e dispositivos...")
            try:
                # 1. Limpa TODOS os relacionamentos primeiro para evitar erros de Foreign Key no PostgreSQL
                db.session.query(CheckoutLog).delete()
                db.session.query(SupportTicket).delete()
                db.session.query(DeviceHealth).delete()
                db.session.query(BehaviorLog).delete()
                
                # 2. Agora sim, podemos limpar os dispositivos com segurança
                db.session.query(Device).delete()
                
                db.session.commit()
                print("✅ Banco de dados limpo com sucesso!")
            except Exception as e:
                db.session.rollback()
                print(f"❌ Erro ao limpar banco de dados: {e}")
                return

            print("🚀 Semeando 464 dispositivos globais...")
        
        # Dicionário com a configuração: 'tipo_no_banco': ('Prefixo do Nome', Quantidade)
        categorias = {
            'coletor': ('Coletor', 114),
            'impressora': ('Impressora', 100),
            'radio': ('Rádio', 50),
            'transpaleteira': ('Transpaleteira', 100),
            'empilhadeira': ('Empilhadeira', 100)
        }

        # Loop inteligente que cria todas as categorias automaticamente
        for tipo, (prefixo, quantidade) in categorias.items():
            for i in range(1, quantidade + 1):
                # Formata o nome para ter sempre 3 dígitos (ex: Coletor 001, Rádio 015)
                nome = f"{prefixo}_{i:03d}"
                device_exists = Device.query.filter_by(name=nome, filial_id=filial_id).first()
                if not device_exists:
                    novo_device = Device(name=nome, type=tipo, status='disponivel', filial_id=filial_id)
                    db.session.add(novo_device)
        
        try:
            db.session.commit()
            print(f"🎉 Sucesso! Dispositivos cadastrados.")
        except Exception as e:
            db.session.rollback()
            print(f"❌ Erro ao semear equipamentos: {e}")

if __name__ == "__main__":
    import sys
    f_id = int(sys.argv[1]) if len(sys.argv) > 1 else None
    seed_devices(f_id)
