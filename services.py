import requests
import threading
from datetime import datetime, timedelta

# ==============================================================================
# CONFIGURAÇÃO DOS LINKS DO GOOGLE CHAT
# ==============================================================================

WEBHOOK_TI = "https://chat.googleapis.com/v1/spaces/AAQAi5WtQdk/messages?key=AIzaSyDdI0hCZtE6vySjMm-WEfRq3CPzqKqqsHI&token=lls_g6s1rcKvapWMkE9SrlNqtOPsXL3UqkSUcs9dQ-U"
WEBHOOK_LIDERANCA = "https://chat.googleapis.com/v1/spaces/AAQASu4ce0Y/messages?key=AIzaSyDdI0hCZtE6vySjMm-WEfRq3CPzqKqqsHI&token=j14d7jZd9CihF6eICynzTQCrOfec1SEGFMnDe96s3yg" 

# ==============================================================================

def get_device_label(device):
    """Retorna o ícone e nome correto baseado no tipo."""
    if device.type == 'impressora':
        return "🖨️ Impressora"
    elif device.type == 'radio':
        return "📻 Rádio"
    else:
        return "📱 Coletor"

def send_message_to_chat(webhook_url, text):
    """ Função genérica para enviar mensagem ao Google Chat """
    if "COLE_O_LINK" in webhook_url:
        print(f"⚠️ AVISO: Webhook não configurado. Mensagem não enviada: {text}")
        return

    try:
        message_headers = {'Content-Type': 'application/json; charset=UTF-8'}
        message_body = {'text': text}
        
        response = requests.post(webhook_url, headers=message_headers, json=message_body)
        
        if response.status_code != 200:
            print(f"Erro ao enviar para o Chat: {response.text}")
    except Exception as e:
        print(f"Erro de conexão com o Chat: {e}")

# --- FUNÇÕES ESPECÍFICAS CHAMADAS PELO ROUTES_MAIN.PY ---

def send_problem_report_alert(app_context, device, user, ticket):
    """
    Disparado quando o COLABORADOR reporta um defeito.
    """
    # 1. Ajusta o Horário (UTC-3 Brasil)
    hora_formatada = (datetime.utcnow() - timedelta(hours=3)).strftime('%d-%m-%Y %H:%M:%S')
    
    # 2. Garante o Turno
    turno_user = user.turno if user.turno else "Não informado"

    # 3. Identifica o equipamento
    tipo_equipamento = get_device_label(device)

    # 4. Monta a mensagem dinâmica
    msg_formatada = (
        f"🔔 *CHAMADO ABERTO (Reportado pelo Colaborador)* 🔔\n\n"
        f"📅 *Data/Hora:* {hora_formatada}\n"
        f"📦 *{tipo_equipamento}:* {device.name}\n"
        f"👤 *Aberto por:* {user.name} (ID: {user.username})\n"
        f"🕒 *Turno:* {turno_user}\n"
        f"📝 *Problema:* {ticket.problem_description}\n\n"
        f"👉 *AÇÃO NECESSÁRIA (LÍDER):*\n"
        f"Por favor Liderança, acesse o sistema para criar o chamado e gerar o link do Zendesk."
    )
    
    # Envia para TI e Liderança em threads separadas para não travar o site
    threading.Thread(target=send_message_to_chat, args=(WEBHOOK_TI, msg_formatada)).start()
    threading.Thread(target=send_message_to_chat, args=(WEBHOOK_LIDERANCA, msg_formatada)).start()

def send_leader_to_support_alert(app_context, device, user, ticket):
    """
    Disparado quando o LÍDER coloca o link do Zendesk.
    Notifica: TI (Agora eles podem agir).
    """
    tipo_equipamento = get_device_label(device)

    msg = (
        f"✅ *ALERTA DE SUPORTE (LIDERANÇA)*\n"
        f"📦 *{tipo_equipamento}:* {device.name}\n"
        f"👤 *Líder:* {user.name}\n"
        f"🔗 *Link Zendesk:* {ticket.zendesk_link}\n"
        f"🛠️ *TI:* O equipamento está liberado para manutenção."
    )
    
    threading.Thread(target=send_message_to_chat, args=(WEBHOOK_TI, msg)).start()


def send_ti_resolved_alert(app_context, device, user, ticket, solution_text):
    """
    Envia notificação formatada de conclusão de chamado.
    """
    # 1. Ajusta o Horário
    hora_atual = (datetime.utcnow() - timedelta(hours=3)).strftime('%d-%m-%Y %H:%M:%S')
    
    # 2. Identifica o equipamento
    tipo_equipamento = get_device_label(device)
    
    # 3. Formata a mensagem
    msg = (
        f"✅ *MANUTENÇÃO FINALIZADA*\n"
        f"📅 *Data/Hora Liberação:* {hora_atual}\n"
        f"📦 *{tipo_equipamento}:* {device.name}\n"
        f"🔓 *Status:* Disponível (liberado)\n"
        f"👤 *Fechado por (Analista TI):* {user.name}\n\n"
        f"🔗 *Link do Chamado:*\n{ticket.zendesk_link}\n\n"
        f"🛠️ *Solução Aplicada:*\n{solution_text}"
    )
    
    # Envia para o chat da Liderança
    threading.Thread(target=send_message_to_chat, args=(WEBHOOK_LIDERANCA, msg)).start()
    
    # Opcional: Mandar no grupo de TI também para log
    threading.Thread(target=send_message_to_chat, args=(WEBHOOK_TI, msg)).start()

def predict_maintenance(device):
    """
    Heurística simples de manutenção preditiva baseada em saúde.
    Em um cenário real, isso poderia usar um modelo de ML mais complexo.
    """
    from models import DeviceHealth
    health_logs = DeviceHealth.query.filter_by(device_id=device.id).order_by(DeviceHealth.created_at.desc()).limit(10).all()
    
    if not health_logs:
        return {"status": "ok", "message": "Sem dados suficientes."}
    
    # Exemplo: Se a bateria cai muito rápido ou o RSSI está muito baixo constantemente
    battery_levels = [h.battery_level for h in health_logs if h.battery_level is not None]
    if len(battery_levels) > 5:
        # Se a média da bateria nos últimos 10 logs é < 20% e o device está em uso
        avg_battery = sum(battery_levels) / len(battery_levels)
        if avg_battery < 20:
            return {"status": "warning", "message": "Bateria com baixa autonomia detectada."}
    
    return {"status": "ok", "message": "Equipamento em bom estado."}

from models import AlertaTI, db
from datetime import datetime

def analyze_behavior(user, device, event):
    # Análise de comportamento e fraude
    colaborador = user.name if user else 'Desconhecido'
    equipamento = device.name if device else 'Desconhecido'
    if event == 'nao_devolveu':
        mensagem = f'O colaborador {colaborador} não devolveu o equipamento {equipamento}.'
        tipo = 'Não Devolveu'
    elif event == 'nao_retirou':
        mensagem = f'O colaborador {colaborador} não retirou o equipamento {equipamento}.'
        tipo = 'Não Retirou'
    elif event == 'uso_sem_retirada':
        mensagem = f'O equipamento {equipamento} foi usado sem retirada registrada.'
        tipo = 'Uso Indevido'
    else:
        mensagem = f'Evento: {event} - Equipamento: {equipamento}.'
        tipo = event
    alerta = AlertaTI(data=datetime.utcnow(), tipo=tipo, colaborador=colaborador, equipamento=equipamento, mensagem=mensagem)
    db.session.add(alerta)
    db.session.commit()
    # Envia alerta para TI e liderança
    from notifications import send_alert
    send_alert('TI', mensagem)
    send_alert('Liderança', mensagem)