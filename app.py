from dotenv import load_dotenv
load_dotenv()

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from flask import Flask, session, flash, redirect, url_for, jsonify, render_template, Response, request
from flask_login import current_user, logout_user, login_required
from sqlalchemy import text 
from datetime import datetime, timezone, timedelta
from authlib.integrations.flask_client import OAuth
import logging
from pythonjsonlogger import jsonlogger
from prometheus_client import Counter, Gauge, generate_latest, CONTENT_TYPE_LATEST

# Importações do Projeto
import config
import extensions
import models
import auth_helpers
import routes_auth
import routes_main

def create_app():
    app = Flask(__name__)

    # --- CONFIGURAÇÕES DE LOGS (JSON) ---
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    if logger.hasHandlers():
        logger.handlers.clear()
    logHandler = logging.StreamHandler()
    formatter = jsonlogger.JsonFormatter('%(asctime)s %(levelname)s %(name)s %(message)s')
    logHandler.setFormatter(formatter)
    logger.addHandler(logHandler)
    app.logger.info("MagaBip: Logs configurados em JSON")

    # --- CONFIGURAÇÕES DE MÉTRICAS (PROMETHEUS) ---
    app.metrics = {
        'HOME_PAGE_ACCESSES': Counter('magabip_home_page_accesses_total', 'Total de acessos a pagina inicial'),
        'TOTAL_ASSET_COUNT': Gauge('magabip_total_assets', 'Total de dispositivos cadastrados')
    }

    def update_asset_metrics():
        from models import Device
        try:
            with app.app_context():
                return Device.query.count()
        except:
            return 0
    app.metrics['TOTAL_ASSET_COUNT'].set_function(update_asset_metrics)
    
    # --- 1. Carrega Configurações ---
    config_class = config.config_map.get('default', config.config_map['default'])
    app.config.from_object(config_class)
    
    # =================================================================
    # DEBUG: IMPRIMIR STRING DE CONEXÃO NO TERMINAL
    # Isso vai te mostrar se o Python está olhando para o Localhost 
    # ou para o servidor 10.60.xxx.xxx
    # =================================================================
    print("\n" + "="*60)
    print(">>> PYTHON ESTÁ CONECTANDO NESTE BANCO DE DADOS:")
    print(app.config.get('SQLALCHEMY_DATABASE_URI'))
    print("="*60 + "\n")
    # =================================================================

    # --- 2. Inicializa Extensões ---
    extensions.db.init_app(app)
    extensions.login_manager.init_app(app)
    extensions.mail.init_app(app)
    
    # --- Configuração do OAuth2 ---
    oauth = OAuth(app)
    oauth.register(
        name='google',
        client_id=os.getenv('GOOGLE_CLIENT_ID'),
        client_secret=os.getenv('GOOGLE_CLIENT_SECRET'),
        access_token_url='https://accounts.google.com/o/oauth2/token',
        authorize_url='https://accounts.google.com/o/oauth2/auth',
        api_base_url='https://www.googleapis.com/oauth2/v1/',
        userinfo_endpoint='https://openidconnect.googleapis.com/v1/userinfo',
        client_kwargs={'scope': 'openid email profile'},
    )
    # Exemplo para Humand (ajuste endpoints conforme documentação Humand)
    oauth.register(
        name='humand',
        client_id=os.getenv('HUMAND_CLIENT_ID'),
        client_secret=os.getenv('HUMAND_CLIENT_SECRET'),
        access_token_url='https://auth.humand.com/oauth/token',
        authorize_url='https://auth.humand.com/oauth/authorize',
        api_base_url='https://api.humand.com/',
        client_kwargs={'scope': 'openid email profile'},
    )

    # --- Configuração do SSOCorp (Portal Luiza/Colaborador) ---
    oauth.register(
        name='ssocorp',
        client_id=os.getenv('SSOCORP_CLIENT_ID'),
        client_secret=os.getenv('SSOCORP_CLIENT_SECRET'),
        access_token_url=os.getenv('SSOCORP_TOKEN_URL', 'https://ssocorp.magazineluiza.com.br/oauth/token'),
        authorize_url=os.getenv('SSOCORP_AUTHORIZE_URL', 'https://ssocorp.magazineluiza.com.br/oauth/authorize'),
        api_base_url=os.getenv('SSOCORP_API_BASE_URL', 'https://ssocorp.magazineluiza.com.br/api/v1/'),
        client_kwargs={'scope': 'openid email profile'},
    )
    
    # --- 3. Configuração do Flask-Login ---
    extensions.login_manager.login_view = 'auth.login' 
    extensions.login_manager.login_message = "Por favor, faça login para acessar esta página."
    extensions.login_manager.login_message_category = 'info'

    @extensions.login_manager.user_loader
    def load_user(user_id):
        # Importação local para evitar ciclo
        return extensions.db.session.get(models.User, int(user_id))

    # --- 4. Configuração de Rotas e Banco de Dados ---
    with app.app_context():
        # Importa as rotas (Blueprints)
        from routes_auth import auth_bp
        from routes_main import main_bp
        
        # Registra Blueprints
        app.register_blueprint(auth_bp, url_prefix='/')
        app.register_blueprint(main_bp, url_prefix='/')

        # Importa os modelos para garantir que o SQLAlchemy os conheça
        from models import User, Device, CheckoutLog, SupportTicket, Filial
        
        # Cria tabelas se não existirem (OBS: Isso NÃO cria colunas novas em tabelas velhas)
        extensions.db.create_all()

    # --- 5. Restrição de Acesso VPN ---
    @app.before_request
    def restrict_by_ip():
        # Se a restrição de VPN estiver ativada nas configurações
        if app.config.get('ENFORCE_VPN', False):
            client_ip = request.remote_addr
            # Obtém ranges permitidos (ex: "10., 192.168.100.")
            allowed_prefixes = app.config.get('VPN_IP_PREFIXES', ['10.', '127.0.0.1', '192.168.'])
            
            is_allowed = any(client_ip.startswith(prefix) for prefix in allowed_prefixes)
            
            if not is_allowed:
                return f"Acesso negado. Este sistema é acessível apenas através da VPN corporativa. (Seu IP: {client_ip})", 403

    # --- 6. Função de Tempo Limite de Sessão ---
    @app.before_request
    def check_session_timeout():
        if current_user.is_authenticated:
            # Define o tempo de expiração baseado no cargo
            if current_user.role == 'colaborador':
                timeout_duration = timedelta(minutes=2) 
            else:
                timeout_duration = timedelta(minutes=15) 

            now_utc = datetime.now(timezone.utc)

            # Se for a primeira atividade, marca o tempo
            if 'last_activity' not in session:
                session['last_activity'] = now_utc
                return 

            last_activity_time = session['last_activity']

            # Garante que o tempo tenha fuso horário (UTC)
            if last_activity_time.tzinfo is None:
                last_activity_time = last_activity_time.replace(tzinfo=timezone.utc)

            time_since_last_activity = now_utc - last_activity_time

            # Se passou do tempo limite, faz logout
            if time_since_last_activity > timeout_duration:
                logout_user()
                session.pop('last_activity', None) 
                flash('Sua sessão expirou por inatividade.', 'info')
                return redirect(url_for('auth.login'))
            
            # Atualiza o tempo da última atividade
            session['last_activity'] = now_utc

    # --- 6. ROTA DE API GERA RELATÓRIO ---
    @app.route('/api/generate_report', methods=['GET'])
    @login_required 
    def get_dashboard_data():
        try:
            # Query otimizada para pegar o último registro de saúde de cada device
            query = text("""
                SELECT DISTINCT ON (device_id) 
                    device_id, 
                    battery_level, 
                    rssi, 
                    created_at 
                FROM device_health 
                ORDER BY device_id, created_at DESC;
            """)
            
            result = extensions.db.session.execute(query)
            devices = []
            
            for row in result:
                devices.append({
                    'device_id': row.device_id,
                    'battery': row.battery_level,
                    'rssi': row.rssi,
                    'last_seen': row.created_at.isoformat() 
                })
            
            return jsonify(devices), 200

        except Exception as e:
            print(f"Erro no dashboard: {e}")
            # Retorna lista vazia em caso de erro para não quebrar o front
            return jsonify([]), 200

    # --- 7. ROTAS DAS ABAS (COLETORES, IMPRESSORAS, RÁDIOS) ---
    
    @app.route('/coletores')
    @login_required 
    def coletores():
        return render_template('index.html', aba_ativa='coletores')

    @app.route('/impressoras')
    @login_required
    def impressoras():
        return render_template('index.html', aba_ativa='impressoras')

    @app.route('/radios')
    @login_required
    def radios():
        return render_template('index.html', aba_ativa='radios')

    @app.route('/metrics')
    def metrics():
        return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)

    return app

# --- BLOCO PRINCIPAL DE EXECUÇÃO ---
if __name__ == '__main__':
    app = create_app()
    # Debug=True ajuda a ver os erros detalhados no navegador
    # Rodar na porta 80 permite acesso via IP direto sem digitar :5000
    # OBS: No Windows, pode exigir rodar o VS Code ou Terminal como Administrador.
    app.run(debug=True, host='0.0.0.0', port=5000)

# Lista de domínios permitidos para liberação automática
ALLOWED_DOMAINS = ['magazineluiza.com.br', 'luizalabs.com']