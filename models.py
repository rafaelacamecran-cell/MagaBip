from extensions import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

# -------------------------------------------------------------------
# MODELO DE USUÁRIO
# -------------------------------------------------------------------
class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False) # Login
    colaborador_id = db.Column(db.String(50), unique=True, nullable=True) # ID do Colaborador
    name = db.Column(db.String(120), nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=True)
    
    role = db.Column(db.String(50), nullable=False, default='colaborador')
    funcao = db.Column(db.String(100), nullable=True)
    turno = db.Column(db.String(50), nullable=True)
    must_change_password = db.Column(db.Boolean, default=False)
    
    # --- FILIAL ---
    filial_id = db.Column(db.Integer, db.ForeignKey('filiais.id'), nullable=True)
    filial = db.relationship('Filial', back_populates='users')

    @property
    def is_privileged(self):
        """ Retorna True se o usuário tem cargo ou função de liderança/gestão. """
        privileged_roles = ['ti', 'lider', 'liderança', 'lideranca', 'sesmt']
        privileged_functions = ['Gerente', 'Coordenador', 'Supervisor', 'Líder', 'T.I', 'Gestor']
        
        roles_match = self.role.lower() in privileged_roles
        functions_match = self.funcao in privileged_functions if self.funcao else False
        
        return roles_match or functions_match


    # --- Relacionamentos ---
    
    # Dispositivos que este utilizador está usando AGORA
    current_devices = db.relationship('Device', back_populates='current_user', lazy=True)
    
    # Histórico de todos os checkouts deste utilizador
    checkout_logs = db.relationship('CheckoutLog', back_populates='user', lazy=True)
    
    # Tickets de suporte que este utilizador ABRIU
    support_tickets_reported = db.relationship(
        'SupportTicket', 
        foreign_keys='SupportTicket.reported_by_user_id', 
        back_populates='reported_by',
        lazy=True
    )
    
    # Tickets de suporte que este utilizador APROVOU (adicionou link Zendesk)
    support_tickets_approved = db.relationship(
        'SupportTicket',
        foreign_keys='SupportTicket.zendesk_added_by_user_id',
        back_populates='zendesk_added_by',
        lazy=True
    )

    # Tickets que este utilizador (TI) RESOLVEU
    support_tickets_resolved = db.relationship(
        'SupportTicket',
        foreign_keys='SupportTicket.resolved_by_user_id',
        back_populates='resolved_by',
        lazy=True
    )

    # --- Métodos de Senha ---
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username} ({self.role})>'

# -------------------------------------------------------------------
# MODELO DE DISPOSITIVO
# -------------------------------------------------------------------
class Device(db.Model):
    """ Representa um dispositivo físico (coletor ou impressora). """
    __tablename__ = 'devices'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    type = db.Column(db.String(50), nullable=False) # 'coletor', 'impressora', 'radio'
    status = db.Column(db.String(50), nullable=False, default='disponivel') # disponivel, em_uso, em_suporte
    
    # --- CAMPOS PARA ESTOQUE VIRTUAL ---
    location = db.Column(db.String(50), default='estoque') # estoque, backup, operacao
    condition = db.Column(db.String(50), default='bom') # bom, com_defeito, manutenção
    serial_number = db.Column(db.String(100), unique=True, nullable=True)
    last_inventory_check = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Quem está usando agora (FK para users.id)
    current_user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)

    # Campo de controle de atualização
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Link zendesk 
    zendesk_url = db.Column(db.String(500), nullable=True) 

    # --- FILIAL ---
    filial_id = db.Column(db.Integer, db.ForeignKey('filiais.id'), nullable=True)
    filial = db.relationship('Filial', back_populates='devices')

    # --- Relacionamentos ---

    current_user = db.relationship('User', back_populates='current_devices')
    
    checkout_logs = db.relationship('CheckoutLog', back_populates='device', lazy=True, cascade="all, delete-orphan")
    support_tickets = db.relationship('SupportTicket', back_populates='device', lazy=True, cascade="all, delete-orphan")
    
    # Relacionamento com a tabela de saúde (Health)
    health_entries = db.relationship('DeviceHealth', back_populates='device', lazy=True, cascade="all, delete-orphan")
    
    def __repr__(self):
        return f'<Device {self.name}>'

# -------------------------------------------------------------------
# MODELO DE LOGS (HISTÓRICO)
# -------------------------------------------------------------------
class CheckoutLog(db.Model):
    """ Regista o histórico de retiradas e devoluções. """
    __tablename__ = 'checkout_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    checkout_time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    checkin_time = db.Column(db.DateTime, nullable=True) 

    device_id = db.Column(db.Integer, db.ForeignKey('devices.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Campos para registro detalhado
    colaborador_name = db.Column(db.String(120))
    colaborador_id = db.Column(db.Integer)
    lider_name = db.Column(db.String(120))
    lider_id = db.Column(db.Integer)
    ti_name = db.Column(db.String(120))
    ti_id = db.Column(db.Integer)
    action_time = db.Column(db.DateTime, default=datetime.utcnow)

    # --- CAMPOS DO CHECKLIST ---
    setor = db.Column(db.String(100), nullable=True)
    nivel_bateria = db.Column(db.String(50), nullable=True)
    observacoes = db.Column(db.Text, nullable=True)

    # --- FILIAL ---
    filial_id = db.Column(db.Integer, db.ForeignKey('filiais.id'), nullable=True)

    # --- Relacionamentos ---

    device = db.relationship('Device', back_populates='checkout_logs')
    user = db.relationship('User', back_populates='checkout_logs')

# -------------------------------------------------------------------
# MODELO DE TICKETS (SUPORTE)
# -------------------------------------------------------------------
class SupportTicket(db.Model):
    """ Regista chamados de manutenção. """
    __tablename__ = 'support_tickets'

    id = db.Column(db.Integer, primary_key=True)
    
    # Campos de Dados
    device_id = db.Column(db.Integer, db.ForeignKey('devices.id'), nullable=False)
    problem_description = db.Column(db.String(255))
    solution = db.Column(db.String(500)) 
    status = db.Column(db.String(20), default='aberto') # aberto, fechado/resolvido
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    resolved_at = db.Column(db.DateTime)
    
    # Link do Zendesk (Histórico do ticket)
    zendesk_link = db.Column(db.String(255))

    # Campos de Relacionamento de Usuários
    reported_by_user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    zendesk_added_by_user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    resolved_by_user_id = db.Column(db.Integer, db.ForeignKey('users.id')) 

    # Campos para registro detalhado
    colaborador_name = db.Column(db.String(120))
    colaborador_id = db.Column(db.Integer)
    lider_name = db.Column(db.String(120))
    lider_id = db.Column(db.Integer)
    ti_name = db.Column(db.String(120))
    ti_id = db.Column(db.Integer)
    action_time = db.Column(db.DateTime, default=datetime.utcnow)

    # --- FILIAL ---
    filial_id = db.Column(db.Integer, db.ForeignKey('filiais.id'), nullable=True)

    # --- Relacionamentos ---

    device = db.relationship('Device', back_populates='support_tickets')
    reported_by = db.relationship('User', foreign_keys=[reported_by_user_id], back_populates='support_tickets_reported')
    zendesk_added_by = db.relationship('User', foreign_keys=[zendesk_added_by_user_id], back_populates='support_tickets_approved')
    resolved_by = db.relationship('User', foreign_keys=[resolved_by_user_id], back_populates='support_tickets_resolved')

# -------------------------------------------------------------------
# MODELO DE SAÚDE DO DISPOSITIVO (IOT/BATTERY)
# -------------------------------------------------------------------
class DeviceHealth(db.Model):
    """ Registra dados de saúde dos dispositivos (bateria, sinal, etc). """
    __tablename__ = 'device_health'

    id = db.Column(db.Integer, primary_key=True)
    device_id = db.Column(db.Integer, db.ForeignKey('devices.id'), nullable=False)
    
    battery_level = db.Column(db.Float, nullable=True)
    battery_voltage = db.Column(db.Float, nullable=True)
    rssi = db.Column(db.Integer, nullable=True)
    uptime_seconds = db.Column(db.Integer, nullable=True)
    reset_reason = db.Column(db.String(100), nullable=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relacionamento inverso
    device = db.relationship('Device', back_populates='health_entries')

# -------------------------------------------------------------------
# MODELO PARA DOCUMENTAÇÃO TÉCNICA
# -------------------------------------------------------------------
class TechnicalDoc(db.Model):
    __tablename__ = 'technical_docs'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50)) 
    tags = db.Column(db.String(200)) 
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# -------------------------------------------------------------------
# MODELO PARA FAQ INTELIGENTE
# -------------------------------------------------------------------
class FAQ(db.Model):
    __tablename__ = 'faqs'
    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.String(500), nullable=False)
    answer = db.Column(db.Text, nullable=False)
    relevance_count = db.Column(db.Integer, default=0)

# -------------------------------------------------------------------
# MODELO PARA ANÁLISE DE COMPORTAMENTO E FRAUDE
# -------------------------------------------------------------------
class BehaviorLog(db.Model):
    __tablename__ = 'behavior_logs'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    device_id = db.Column(db.Integer, db.ForeignKey('devices.id'))
    event_type = db.Column(db.String(100)) 
    description = db.Column(db.Text)
    severity = db.Column(db.String(20)) 
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', backref='behavior_logs')
    device = db.relationship('Device', backref='behavior_logs')

# -------------------------------------------------------------------
# MODELO PARA ALERTAS TI
# -------------------------------------------------------------------
class AlertaTI(db.Model):
    __tablename__ = 'alertas_ti'  # Adicionado para padronizar
    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.DateTime, default=datetime.utcnow)
    tipo = db.Column(db.String(50))
    colaborador = db.Column(db.String(120))
    equipamento = db.Column(db.String(120))
    mensagem = db.Column(db.Text)

    # --- FILIAL ---
    filial_id = db.Column(db.Integer, db.ForeignKey('filiais.id'), nullable=True)

# -------------------------------------------------------------------
# MODELO DE FILIAL (CENTRO DE DISTRIBUIÇÃO)
# -------------------------------------------------------------------
class Filial(db.Model):
    __tablename__ = 'filiais'

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(120), unique=True, nullable=False) # Ex: CD050
    codigo = db.Column(db.String(50), unique=True, nullable=True) # Código da filial
    cidade = db.Column(db.String(100), nullable=True)
    
    # --- Relacionamentos ---
    users = db.relationship('User', back_populates='filial', lazy=True)
    devices = db.relationship('Device', back_populates='filial', lazy=True)

    def __repr__(self):
        return f'<Filial {self.nome}>'
