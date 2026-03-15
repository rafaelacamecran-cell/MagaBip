import requests

# --- COLAR LINK ABAIXO ENTRE AS ASPAS ---
WEBHOOK_URL_LIDERANCA = "https://chat.googleapis.com/v1/spaces/AAQASu4ce0Y/messages?key=AIzaSyDdI0hCZtE6vySjMm-WEfRq3CPzqKqqsHI&token=j14d7jZd9CihF6eICynzTQCrOfec1SEGFMnDe96s3yg"

def testar_envio():
    print(f"Tentando enviar para: {WEBHOOK_URL_LIDERANCA[:30]}...")
    
    mensagem = {
        "text": "🔔 Teste de Notificação do Sistema de Ativos! Se você ler isso, funcionou."
    }
    
    try:
        response = requests.post(WEBHOOK_URL_LIDERANCA, json=mensagem)
        
        if response.status_code == 200:
            print("✅ SUCESSO! Mensagem enviada. Verifique o Google Chat.")
        else:
            print(f"❌ ERRO DO GOOGLE: {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"❌ ERRO NO PYTHON: {e}")

if __name__ == "__main__":
    testar_envio()