from app import create_app
from waitress import serve
import socket
import os
from dotenv import load_dotenv
load_dotenv()

# --- CONFIGURAÇÃO ---
# Mude para True para ver os erros detalhados (Desenvolvimento)
# Mude para False para usar o servidor rápido e seguro (Produção/Waitress)
# MODO_DEBUG: True para desenvolvimento, False para produção
MODO_DEBUG = os.getenv('MODO_DEBUG', 'False').lower() in ('true', '1', 't')
# --------------------

app = create_app()

def get_internal_ip():
    """ Tenta encontrar o endereço IP interno do computador. """
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"

if __name__ == '__main__':
    host = '0.0.0.0'
    port = 80
    internal_ip = get_internal_ip()

    print("===============================================================")
    if MODO_DEBUG:
        print(f"MODO DEBUG ATIVADO (Use apenas para corrigir erros)")
        print(f"Os erros aparecerão aqui no terminal.")
    else:
        print(f"SERVIDOR DE PRODUÇÃO (WAITRESS) INICIADO")
    
    print(f"Acesse em: http://{internal_ip}:{port}")
    print("===============================================================")

    if MODO_DEBUG:
        # Modo Debug: Mostra o erro na tela e no terminal
        app.run(debug=True, host=host, port=port)
    else:
        # Modo Produção: Rápido, aguenta muitos usuários, mas esconde erros
        serve(app, host=host, port=port, threads=6)