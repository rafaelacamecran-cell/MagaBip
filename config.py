import os

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    """Configurações base comuns a todos os ambientes."""
    
    # --- 1. SEGURANÇA BÁSICA ---
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'maga-bip-secret-key-2026'
    
    # --- 2. BANCO DE DADOS (SQLALCHEMY) ---
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {"pool_pre_ping": True}

    # Lógica para URL do Postgres (SQLAlchemy exige postgresql://)
    database_url = os.environ.get('DATABASE_URL')
    if database_url and database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql://", 1)
    
    # Prioriza banco externo, senão usa SQLite local
    SQLALCHEMY_DATABASE_URI = database_url or 'sqlite:///' + os.path.join(basedir, 'app.db')

    # --- 3. AUTENTICAÇÃO OAUTH ---
    # Google
    GOOGLE_CLIENT_ID = os.environ.get('GOOGLE_CLIENT_ID')
    GOOGLE_CLIENT_SECRET = os.environ.get('GOOGLE_CLIENT_SECRET')
    
    # Humand (Adicionado)
    HUMAND_CLIENT_ID = os.environ.get('HUMAND_CLIENT_ID')
    HUMAND_CLIENT_SECRET = os.environ.get('HUMAND_CLIENT_SECRET')
    
    # IA Gemini (Adicionado)
    GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')

    # Lógica do Interruptor: Verifica se tem chaves mínimas para OAuth
    USE_OAUTH = bool(GOOGLE_CLIENT_ID or HUMAND_CLIENT_ID)

    # --- 4. E-MAIL (SMTP) ---
    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.googlemail.com')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', '587'))
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'true').lower() in ['true', 'on', '1']
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    
    # E-mail padrão de envio do sistema
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER', MAIL_USERNAME)

    # --- 5. SEGURANÇA DE COOKIES ---
    SESSION_COOKIE_SECURE = False 
    SESSION_COOKIE_HTTPONLY = True

    # --- 6. CONFIGURAÇÕES DE VPN ---
    # Define se o sistema deve exigir conexão via VPN (IP filtrado)
    ENFORCE_VPN = os.environ.get('ENFORCE_VPN', 'false').lower() in ['true', 'on', '1']
    # Lista de prefixos de IP permitidos (pode ser configurado via string separada por vírgula no .env)
    vpn_prefixes_raw = os.environ.get('VPN_IP_PREFIXES', '10., 127.0.0.1, 192.168.')
    VPN_IP_PREFIXES = [p.strip() for p in vpn_prefixes_raw.split(',')]

class DevelopmentConfig(Config):
    """Configurações para desenvolvimento local."""
    DEBUG = True
    # Imprime status no terminal para ajudar no seu trabalho
    print(f"\nSTATUS MAGABIP: {'OAuth Ativado' if Config.USE_OAUTH else 'Modo Local'}")
    print(f"IA GEMINI: {'Configurada' if Config.GEMINI_API_KEY else 'Sem Chave'}\n")


class ProductionConfig(Config):
    """Configurações para produção (Deploy)."""
    DEBUG = False
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_SAMESITE = 'Lax'

config_map = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}