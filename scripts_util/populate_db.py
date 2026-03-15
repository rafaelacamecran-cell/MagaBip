import sys
from app import create_app
from extensions import db
from models import Device, CheckoutLog, SupportTicket

def populate_devices():
    """
    Limpa e recria a lista padrão de dispositivos.
    Novos padrões:
    - Coletores: Coletor 001 a Coletor 114
    - Impressoras: Impressora 01 a Impressora 50
    - Rádios: Rádio 01 a Rádio 20
    """
    print("Iniciando a população do banco de dados...")
    
    try:
        # 1. Limpa tabelas dependentes primeiro (Logs e Tickets)
        # Isso evita erros de chave estrangeira ao apagar os devices
        print("Limpando tabelas antigas (logs, tickets)...")
        db.session.query(CheckoutLog).delete()
        db.session.query(SupportTicket).delete()
        
        # 2. Limpa a tabela principal (Devices)
        print("Limpando tabela (devices)...")
        db.session.query(Device).delete()
        
        # Confirma a limpeza antes de adicionar novos dados
        db.session.commit()
        
        # 3. Prepara os novos dispositivos em memória
        print("Preparando novos dispositivos...")

        # --- COLETORES (114 unidades) ---
        coletores = [
            Device(name=f"Coletor {i:03d}", type='coletor', status='disponivel')
            for i in range(1, 115) 
        ]
        
        # --- IMPRESSORAS (50 unidades) ---
        impressoras = [
            Device(name=f"Impressora {i:02d}", type='impressora', status='disponivel')
            for i in range(1, 51)
        ]
        
        # --- RÁDIOS (20 unidades) --- [NOVO]
        radios = [
            # O type='radio' deve ser minúsculo para bater com os filtros do backend
            Device(name=f"Rádio {i:02d}", type='radio', status='disponivel')
            for i in range(1, 21)
        ]
        # ----------------------

        # Junta todas as listas
        devices_to_add = coletores + impressoras + radios
        
        # 4. Adiciona todos os dispositivos ao banco de uma só vez
        print(f"Adicionando {len(devices_to_add)} dispositivos ao banco de dados...")
        db.session.add_all(devices_to_add)
        db.session.commit()
        
        print(f"✅ Banco de dados populado com sucesso!")
        print(f"Resumo: {len(coletores)} Coletores, {len(impressoras)} Impressoras e {len(radios)} Rádios.")

    except Exception as e:
        db.session.rollback()
        print(f"[ERRO] Falha ao popular o banco de dados: {e}", file=sys.stderr)
    finally:
        # Garante que a sessão seja fechada corretamente
        db.session.remove()

# --- Bloco de Execução ---
if __name__ == '__main__':
    # Cria a aplicação Flask para obter o contexto do banco de dados
    app = create_app()
    with app.app_context():
        populate_devices()