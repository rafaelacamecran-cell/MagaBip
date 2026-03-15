import requests
import threading
from datetime import datetime, timedelta
from flask import current_app

# LINKS DO GOOGLE CHAT (Seus webhooks)
WEBHOOK_TI = "https://chat.googleapis.com/v1/spaces/AAQAi5WtQdk/messages?key=AIzaSyDdI0hCZtE6vySjMm-WEfRq3CPzqKqqsHI&token=lls_g6s1rcKvapWMkE9SrlNqtOPsXL3UqkSUcs9dQ-U"
WEBHOOK_LIDERANCA = "https://chat.googleapis.com/v1/spaces/AAQASu4ce0Y/messages?key=AIzaSyDdI0hCZtE6vySjMm-WEfRq3CPzqKqqsHI&token=j14d7jZd9CihF6eICynzTQCrOfec1SEGFMnDe96s3yg" 

def get_device_label(device):
    if device.type == 'impressora': return "🖨️ Impressora"
    elif device.type == 'radio': return "📻 Rádio"
    else: return "📱 Coletor"

def send_message_to_chat(webhook_url, text):
    try:
        requests.post(webhook_url, headers={'Content-Type': 'application/json; charset=UTF-8'}, json={'text': text})
    except Exception as e:
        print(f"Erro Chat: {e}")

def send_alert(destinatario, mensagem):
    # Envia alerta para Google Chat ou e-mail
    if destinatario == 'TI':
        webhook = current_app.config.get('GCHAT_WEBHOOK_URL_TI')
    elif destinatario == 'Liderança':
        webhook = current_app.config.get('GCHAT_WEBHOOK_URL_LIDERANCA')
    else:
        webhook = None
    if webhook:
        import requests
        requests.post(webhook, json={"text": mensagem})
    # Pode expandir para e-mail

def send_problem_report_alert(app_context, device, user, ticket):
    now = (datetime.utcnow() - timedelta(hours=3))
    date_time = now.strftime('%d-%m-%Y %H:%M:%S')
    device_label = get_device_label(device)
    
    # Mensagem 1: Alerta Rápido
    msg1 = (f"📢 *ATENÇÃO LIDERANÇA*\n"
            f"O colaborador *{user.name}* reportou um defeito no *{device.name}*.\n"
            f"📝 *Motivo:* [Colaborador {user.name}]: {ticket.problem_description}\n"
            f"👉 Por favor, acesse o painel e anexe o link do chamado Zendesk.")
    
    # Mensagem 2: Relatório Detalhado
    msg2 = (f"🔔 *CHAMADO ABERTO (Aberto por Colaborador)* 🔔\n\n"
            f"📅 *Data/Hora:* {date_time}\n"
            f"📦 *{device_label}:* {device.name}\n"
            f"👤 *Aberto por (Colab.):* {user.name} (ID: {user.username})\n"
            f"🕒 *Turno:* {user.turno or '---'}\n"
            f"📝 *Problema:* [Colaborador {user.name}]: {ticket.problem_description}\n\n"
            f"👉 *AÇÃO NECESSÁRIA (LÍDER):*\n"
            f"Por favor, use o 'Acesso Liderança' para abrir o chamado e anexar o link para enviar o equipamento ao suporte.")
    
    # Envia em threads separadas para não travar o app
    def send_both():
        send_message_to_chat(WEBHOOK_TI, msg1)
        send_message_to_chat(WEBHOOK_LIDERANCA, msg1)
        send_message_to_chat(WEBHOOK_TI, msg2)
        send_message_to_chat(WEBHOOK_LIDERANCA, msg2)

    threading.Thread(target=send_both).start()

def send_non_return_alert(device, user):
    msg = (f"⚠️ *ALERTA DE DEVOLUÇÃO*\n"
           f"🚫 O colaborador *{user.name}* não devolveu o equipamento: *{device.name}*.\n"
           f"Favor verificar com o colaborador.")
    threading.Thread(target=send_message_to_chat, args=(WEBHOOK_TI, msg)).start()
    threading.Thread(target=send_message_to_chat, args=(WEBHOOK_LIDERANCA, msg)).start()

def send_fraud_alert(event_type, description, user=None):
    user_name = user.name if user else "Desconhecido"
    msg = (f"🚨 *ALERTA DE SEGURANÇA/FRAUDE*\n"
           f"🚩 Tipo: {event_type}\n"
           f"👤 Colaborador: {user_name}\n"
           f"📝 Detalhes: {description}")
    threading.Thread(target=send_message_to_chat, args=(WEBHOOK_TI, msg)).start()
    threading.Thread(target=send_message_to_chat, args=(WEBHOOK_LIDERANCA, msg)).start()

def send_leader_to_support_alert(app_context, device, user, ticket):
    msg = (f"✅ *AUTORIZADO P/ TI*\n"
           f"📦 *Equipamento:* {device.name}\n"
           f"👤 *Líder:* {user.name}\n"
           f"🔗 *Chamado:* {ticket.zendesk_link}\n"
           f"👉 *Próximo passo:* TI já pode iniciar a manutenção.")
    threading.Thread(target=send_message_to_chat, args=(WEBHOOK_TI, msg)).start()

def send_ti_resolved_alert(app_context, device, user, ticket, solution_text):
    now = (datetime.utcnow() - timedelta(hours=3))
    date_time = now.strftime('%d-%m-%Y %H:%M:%S')
    device_label = get_device_label(device)

    # Mensagem 1: Conclusão
    msg1 = (f"🟢 *MANUTENÇÃO CONCLUÍDA (TI)*\n"
            f"📦 *Equipamento:* {device.name}\n"
            f"👤 *Técnico:* {user.name}\n"
            f"✨ O dispositivo foi consertado/trocado e está *DISPONÍVEL* novamente no painel.")

    # Mensagem 2: Relatório Final
    msg2 = (f"✅ *MANUTENÇÃO FINALIZADA*\n"
            f"📅 *Data/Hora Liberação:* {date_time}\n"
            f"📦 *{device_label}:* {device.name}\n"
            f"🔓 *Status:* Disponível (liberado)\n"
            f"👤 *Fechado por (Analista TI):* {user.name} ({user.username})\n\n"
            f"🔗 *Link do Chamado:*\n{ticket.zendesk_link}\n\n"
            f"🛠️ *Solução Aplicada:*\n{solution_text}")

    def send_both():
        send_message_to_chat(WEBHOOK_LIDERANCA, msg1)
        send_message_to_chat(WEBHOOK_LIDERANCA, msg2)
        send_message_to_chat(WEBHOOK_TI, msg1)
        send_message_to_chat(WEBHOOK_TI, msg2)

    threading.Thread(target=send_both).start()
