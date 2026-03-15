from flask import Blueprint, render_template, redirect, url_for, abort, request, flash, current_app, jsonify, session
from flask_login import login_required, current_user, login_user
from models import Device, CheckoutLog, SupportTicket, User, DeviceHealth, AlertaTI, TechnicalDoc, Filial
from extensions import db
from datetime import datetime, timezone, timedelta, time
from functools import wraps
import requests 
from sqlalchemy import desc
from sqlalchemy.exc import IntegrityError # <--- ADICIONADO PARA TRATAR ERROS DO BANCO DE DADOS
from werkzeug.security import generate_password_hash
import os

main_bp = Blueprint('main', __name__)

# ========================================================
# AUTO-CORRETOR DE BANCO DE DADOS
# ========================================================
@main_bp.before_app_request
def auto_update_db():
    if not getattr(current_app, '_db_updated', False):
        from sqlalchemy import text
        try:
            # Detect database engine
            engine_name = db.engine.name
            
            # 1. CRIAR TABELA DE FILIAIS SE NÃO EXISTIR
            if engine_name == 'postgresql':
                db.session.execute(text("""
                    CREATE TABLE IF NOT EXISTS filiais (
                        id SERIAL PRIMARY KEY,
                        nome VARCHAR(120) UNIQUE NOT NULL,
                        codigo VARCHAR(50) UNIQUE,
                        cidade VARCHAR(100)
                    );
                """))
            else: # SQLite or others
                db.session.execute(text("""
                    CREATE TABLE IF NOT EXISTS filiais (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        nome VARCHAR(120) UNIQUE NOT NULL,
                        codigo VARCHAR(50) UNIQUE,
                        cidade VARCHAR(100)
                    );
                """))
            
            # 2. ADICIONAR COLUNAS (Tratadas individualmente para compatibilidade)
            columns_to_add = [
                ("users", "filial_id", "INTEGER REFERENCES filiais(id)"),
                ("devices", "filial_id", "INTEGER REFERENCES filiais(id)"),
                ("checkout_logs", "filial_id", "INTEGER REFERENCES filiais(id)"),
                ("support_tickets", "filial_id", "INTEGER REFERENCES filiais(id)"),
                ("alertas_ti", "filial_id", "INTEGER REFERENCES filiais(id)"),
                ("checkout_logs", "setor", "VARCHAR(100)"),
                ("checkout_logs", "nivel_bateria", "VARCHAR(50)"),
                ("checkout_logs", "observacoes", "TEXT"),
                ("devices", "location", "VARCHAR(50) DEFAULT 'estoque'"),
                ("devices", "condition", "VARCHAR(50) DEFAULT 'bom'")
            ]

            for table, col, spec in columns_to_add:
                try:
                    if engine_name == 'postgresql':
                        db.session.execute(text(f"ALTER TABLE {table} ADD COLUMN IF NOT EXISTS {col} {spec};"))
                    else:
                        # SQLite doesn't support IF NOT EXISTS for ADD COLUMN
                        db.session.execute(text(f"ALTER TABLE {table} ADD COLUMN {col} {spec};"))
                except Exception:
                    db.session.rollback() # Ignora erro se a coluna já existir

            db.session.commit()

        except Exception as e:
            print(f"Erro na migração automática: {e}")
            db.session.rollback()
        current_app._db_updated = True

def get_oauth():
    from authlib.integrations.flask_client import OAuth
    if hasattr(current_app, 'extensions') and 'authlib.integrations.flask_client' in current_app.extensions:
        return current_app.extensions['authlib.integrations.flask_client']
    return OAuth(current_app)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "SUA_CHAVE_AQUI")

def check_password_change_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.is_authenticated and hasattr(current_user, 'must_change_password'):
            if current_user.must_change_password and request.endpoint not in ['auth.change_password', 'auth.logout']:
                flash('Por favor, atualize a sua senha provisória.', 'warning')
                return redirect(url_for('auth.change_password'))
        return f(*args, **kwargs)
    return decorated_function

# ========================================================
# REGRAS ESTRITAS DE HORÁRIO
# ========================================================

def check_shift_rules(turno_raw):
    """ Devolve (Boolean, Mensagem) - True se pode retirar, False se bloqueado """
    if not turno_raw or str(turno_raw).strip() == "" or turno_raw == "Selecione":
        return False, "Você precisa selecionar um Turno válido no formulário de retirada."
        
    turno = str(turno_raw).strip().lower()
    agora_dt = datetime.now()
    agora = agora_dt.time()
    hora_atual_str = agora.strftime('%H:%M')
    
    if '1º' in turno or '1o' in turno:
        if time(6, 0) <= agora <= time(14, 0): return True, ""
        return False, f"O 1º Turno só pode retirar equipamentos das 06:00 às 14:00 (Hora atual do sistema: {hora_atual_str})."
        
    elif '2º' in turno or '2o' in turno:
        if time(13, 40) <= agora <= time(22, 0): return True, ""
        return False, f"O 2º Turno só pode retirar equipamentos das 13:40 às 22:00 (Hora atual do sistema: {hora_atual_str})."
        
    elif '3º' in turno or '3o' in turno:
        if agora >= time(22, 0) or agora <= time(5, 45): return True, ""
        return False, f"O 3º Turno só pode retirar equipamentos das 22:00 às 05:45 (Hora atual do sistema: {hora_atual_str})."
        
    elif 'adm' in turno or 'administrativo' in turno:
        if time(8, 0) <= agora <= time(17, 0): return True, ""
        return False, f"O Turno Administrativo só pode retirar equipamentos das 08:00 às 17:00 (Hora atual do sistema: {hora_atual_str})."
        
    return False, f"O turno '{turno_raw}' não é reconhecido pelas regras do sistema."

def get_overdue_devices(filial_id=None):
    overdue = []
    agora_dt = datetime.now()
    agora_t = agora_dt.time()
    
    query = Device.query.filter_by(status='em_uso')
    if filial_id:
        query = query.filter_by(filial_id=filial_id)
        
    devices_em_uso = query.all()

    for d in devices_em_uso:
        if not d.current_user or not d.current_user.turno: continue
            
        log = CheckoutLog.query.filter_by(device_id=d.id, checkin_time=None).order_by(desc(CheckoutLog.checkout_time)).first()
        if not log: continue
            
        horas_uso = (agora_dt - log.checkout_time).total_seconds() / 3600
        if horas_uso > 12: 
            overdue.append(d)
            continue
            
        turno = d.current_user.turno.strip().lower()
        is_late = False
        
        if '1º' in turno or '1o' in turno:
            if time(14, 30) <= agora_t <= time(23, 59): is_late = True
        elif '2º' in turno or '2o' in turno:
            if time(22, 30) <= agora_t <= time(23, 59) or time(0, 0) <= agora_t <= time(4, 0): is_late = True
        elif '3º' in turno or '3o' in turno:
            if time(6, 15) <= agora_t <= time(20, 0): is_late = True
        elif 'adm' in turno or 'administrativo' in turno:
            if time(17, 30) <= agora_t <= time(23, 59): is_late = True
            
        if is_late and d not in overdue:
            overdue.append(d)
            
    return overdue

# ========================================================
# 1. AUTENTICAÇÃO
# ========================================================

def process_social_login(email, name, provider):
    user = User.query.filter_by(username=email).first()
    if not user:
        try:
            user = User(name=name or email.split('@')[0], username=email, email=email, role='colaborador', must_change_password=False)
            user.password_hash = generate_password_hash("OAUTH_USER_RANDOM_PWD")
            db.session.add(user)
            db.session.commit()
            flash(f"Conta criada via {provider}!", "success")
        except Exception as e:
            db.session.rollback()
            flash(f"Erro ao criar conta: {str(e)}", "danger")
            return redirect(url_for('auth.login'))

    login_user(user)
    flash(f"Bem-vindo(a), {user.name}!", "success")
    
    # Reconhecimento Automático: Se não tem filial, obriga a selecionar uma no perfil
    if not user.filial_id:
        flash("Por favor, selecione sua Filial (CD) para configurar seu ambiente de trabalho.", "warning")
        return redirect(url_for('main.profile_page'))
        
    return redirect(url_for('main.dashboard'))

@main_bp.route('/login_google')
def login_google(): return get_oauth().google.authorize_redirect(url_for('main.auth_google_callback', _external=True))

@main_bp.route('/auth_google_callback')
def auth_google_callback():
    token = get_oauth().google.authorize_access_token()
    user_info = get_oauth().google.parse_id_token(token)
    return process_social_login(user_info['email'], user_info['name'], "Google")

@main_bp.route('/login_humand')
def login_humand(): return get_oauth().humand.authorize_redirect(url_for('main.auth_humand_callback', _external=True))

@main_bp.route('/auth_humand_callback')
def auth_humand_callback():
    token = get_oauth().humand.authorize_access_token()
    user_info = token['userinfo'] if 'userinfo' in token else {}
    return process_social_login(user_info.get('email'), user_info.get('name'), "Humand")

@main_bp.route('/login-corporate', methods=['GET', 'POST'])
def login_corporate():
    if request.method == 'POST':
        email = request.form.get('email')
        if any(domain in email for domain in ['magazineluiza.com.br', 'luizalabs.com']):
            return process_social_login(email, None, "E-mail Corporativo")
        flash('Domínio não autorizado.', 'danger')
    return render_template('login_corporate.html')

# ========================================================
# 2. DASHBOARD E RELATÓRIO DE ATRASOS
# ========================================================

@main_bp.route('/dashboard')
@login_required 
@check_password_change_required
def dashboard():
    if current_user.is_privileged:
        aparelhos_atrasados = get_overdue_devices(current_user.filial_id)
        if aparelhos_atrasados:
            nomes = " | ".join([f"{d.name} (c/ {d.current_user.name})" for d in aparelhos_atrasados])
            flash(f'🚨 ALERTA DE ATRASO: Equipamentos não devolvidos no fim do turno: {nomes}', 'danger')

    page = request.args.get('page', 1, type=int)
    search_term = request.args.get('search', '')
    query = Device.query
    
    # SEPARAÇÃO POR FILIAL: Todos veem apenas o que é da sua filial
    if current_user.filial_id:
        query = query.filter_by(filial_id=current_user.filial_id)
        
    if search_term: query = query.filter(Device.name.ilike(f"%{search_term}%"))

    coletores = query.filter_by(type='coletor').order_by(Device.name).paginate(page=page, per_page=1000, error_out=False)
    impressoras = query.filter_by(type='impressora').order_by(Device.name).paginate(page=page, per_page=1000, error_out=False)
    radios = query.filter_by(type='radio').order_by(Device.name).paginate(page=page, per_page=1000, error_out=False)
    transpaleteiras = query.filter_by(type='transpaleteira').order_by(Device.name).paginate(page=page, per_page=1000, error_out=False)
    empilhadeiras = query.filter_by(type='empilhadeira').order_by(Device.name).paginate(page=page, per_page=1000, error_out=False)

    my_devices = Device.query.filter_by(current_user_id=current_user.id).all()

    render_data = {
        "user": current_user, "coletores_pagination": coletores, "impressoras_pagination": impressoras,
        "radios_pagination": radios, "transpaleteiras_pagination": transpaleteiras,
        "empilhadeiras_pagination": empilhadeiras, "search_term": search_term, "my_devices": my_devices
    }

    template_map = {
        'ti': 'dashboard_ti.html', 
        'liderança': 'dashboard_lideranca.html', 'lideranca': 'dashboard_lideranca.html', 'lider': 'dashboard_lideranca.html',
        'sesmt': 'dashboard_sesmt.html'
    }
    template = template_map.get(current_user.role.lower(), 'dashboard_colaborador.html')
    return render_template(template, **render_data)

@main_bp.route('/relatorio_atrasos')
@login_required
def relatorio_atrasos():
    if not current_user.is_privileged: abort(403)

    lista_atrasados = get_overdue_devices(current_user.filial_id)

    dados_atraso = []
    for device in lista_atrasados:
        log = CheckoutLog.query.filter_by(device_id=device.id, checkin_time=None).order_by(desc(CheckoutLog.checkout_time)).first()
        if log:
            dados_atraso.append({
                'equipamento': device.name, 'tipo': device.type, 'colaborador': device.current_user.name,
                'colaborador_id': device.current_user.colaborador_id, 'turno': device.current_user.turno,
                'retirada': log.checkout_time.strftime('%d/%m/%Y %H:%M')
            })
    return render_template('relatorio_atrasos.html', atrasados=dados_atraso)

# ========================================================
# 3. GESTÃO DE DISPOSITIVOS E RETIRADAS
# ========================================================

@main_bp.route('/device/pickup/<int:device_id>', methods=['POST'])
@login_required
@check_password_change_required
def device_pickup(device_id):
    device = Device.query.get_or_404(device_id)
    if device.status != 'disponivel':
        flash('Dispositivo indisponível.', 'danger')
        return redirect(url_for('main.dashboard'))

    turno_selecionado = request.form.get('turno', '')
    permitido, msg_erro = check_shift_rules(turno_selecionado)
    
    if not permitido:
        doze_horas_atras = datetime.now() - timedelta(hours=12)
        ticket_recente = SupportTicket.query.filter_by(reported_by_user_id=current_user.id).filter(SupportTicket.created_at >= doze_horas_atras).first()
        
        if not ticket_recente:
            flash(f'⚠️ RETIRADA BLOQUEADA: {msg_erro} Se for uma troca, reporte o problema do equipamento anterior primeiro!', 'danger')
            return redirect(url_for('main.dashboard'))
        else:
            flash('ℹ️ Retirada fora de hora autorizada (Troca de equipamento com defeito detectada).', 'info')
        
    setor = request.form.get('setor')
    nivel_bateria = request.form.get('nivel_bateria')
    observacoes = request.form.get('observacoes', '')

    device.status = 'em_uso'
    device.current_user_id = current_user.id
    
    novo_log = CheckoutLog(
        device_id=device.id, user_id=current_user.id, checkout_time=datetime.now(),
        colaborador_name=current_user.name, colaborador_id=current_user.colaborador_id,
        setor=setor, nivel_bateria=nivel_bateria, filial_id=current_user.filial_id,
        observacoes=f"[Turno: {turno_selecionado}] {observacoes}" if turno_selecionado else observacoes
    )
    db.session.add(novo_log)
    db.session.commit()
    flash(f'{device.name} retirado com sucesso!', 'success')
    return redirect(url_for('main.dashboard'))

@main_bp.route('/device/return/<int:device_id>', methods=['POST'])
@login_required
def device_return(device_id):
    device = Device.query.get_or_404(device_id)
    if device.current_user_id != current_user.id:
        flash('Este dispositivo não está com você.', 'danger')
        return redirect(url_for('main.dashboard'))
        
    device.status = 'disponivel'
    device.current_user_id = None
    log = CheckoutLog.query.filter_by(device_id=device.id, user_id=current_user.id, checkin_time=None).first()
    if log: log.checkin_time = datetime.now()
    db.session.commit()
    flash(f'{device.name} devolvido.', 'success')
    return redirect(url_for('main.dashboard'))

@main_bp.route('/device-history/<int:device_id>')
@login_required
def device_history(device_id):
    dev = Device.query.get_or_404(device_id)
    logs = CheckoutLog.query.filter_by(device_id=device_id).order_by(desc(CheckoutLog.checkout_time)).all()
    tickets = SupportTicket.query.filter_by(device_id=device_id).order_by(desc(SupportTicket.created_at)).all()
    return render_template('device_history.html', device=dev, checkout_logs=logs, support_tickets=tickets)

@main_bp.route('/devices', methods=['GET'])
@login_required
def manage_devices_page():
    if current_user.role.lower() != 'ti': abort(403)
    page = request.args.get('page', 1, type=int)
    search_term = request.args.get('search', '')
    
    coletores_query = Device.query.filter_by(type='coletor')
    impressoras_query = Device.query.filter_by(type='impressora')
    radios_query = Device.query.filter_by(type='radio')

    if current_user.filial_id:
        coletores_query = coletores_query.filter_by(filial_id=current_user.filial_id)
        impressoras_query = impressoras_query.filter_by(filial_id=current_user.filial_id)
        radios_query = radios_query.filter_by(filial_id=current_user.filial_id)

    if search_term:
        term = f"%{search_term}%"
        coletores_query = coletores_query.filter(Device.name.ilike(term))
        impressoras_query = impressoras_query.filter(Device.name.ilike(term))
        radios_query = radios_query.filter(Device.name.ilike(term))
    
    coletores_pagination = coletores_query.order_by(Device.name).paginate(page=page, per_page=50, error_out=False)
    impressoras_pagination = impressoras_query.order_by(Device.name).paginate(page=page, per_page=50, error_out=False)
    radios_pagination = radios_query.order_by(Device.name).paginate(page=page, per_page=50, error_out=False)
    
    return render_template('manage_devices_list.html', coletores_pagination=coletores_pagination, impressoras_pagination=impressoras_pagination, radios_pagination=radios_pagination, search_term=search_term)

@main_bp.route('/devices/new', methods=['GET', 'POST'])
@login_required
def create_device():
    if current_user.role.lower() != 'ti': abort(403)
    if request.method == 'POST':
        new_device = Device(name=request.form.get('name'), type=request.form.get('device_type'), status='disponivel', filial_id=current_user.filial_id)
        db.session.add(new_device)
        db.session.commit()
        flash('Equipamento cadastrado!', 'success')
        return redirect(url_for('main.manage_devices_page'))
    return render_template('manage_device_form.html')

@main_bp.route('/manage-devices/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_device(id):
    if current_user.role.lower() != 'ti': abort(403)
    dev = Device.query.get_or_404(id)
    if request.method == 'POST':
        dev.name = request.form.get('name')
        dev.type = request.form.get('type')
        if request.form.get('status'): dev.status = request.form.get('status')
        db.session.commit()
        flash('Atualizado.', 'success')
        return redirect(url_for('main.manage_devices_page'))
    return render_template('manage_device_form.html', device=dev)

@main_bp.route('/manage-devices/delete/<int:id>', methods=['POST'])
@login_required
def delete_device(id):
    if current_user.role.lower() != 'ti': abort(403)
    dev = Device.query.get_or_404(id)
    if dev.status != 'disponivel':
        flash('Não é possível remover. Dispositivo não está disponível.', 'warning')
        return redirect(url_for('main.manage_devices_page'))
    try:
        SupportTicket.query.filter_by(device_id=id).delete()
        CheckoutLog.query.filter_by(device_id=id).delete()
        db.session.delete(dev)
        db.session.commit()
        flash('Removido.', 'success')
    except Exception as e:
        db.session.rollback()
    return redirect(url_for('main.manage_devices_page'))


# ========================================================
# ROTA DEFINITIVA PARA CRIAR E VINCULAR APARELHOS
# ========================================================
@main_bp.route('/populate_all_devices')
@login_required
def populate_all_devices():
    if current_user.role.lower() != 'ti': abort(403) 
    
    if not current_user.filial_id:
        flash("Precisas de ter uma filial selecionada no perfil primeiro antes de gerar aparelhos!", "warning")
        return redirect(url_for('main.dashboard'))
        
    configs = [('coletor', 'Coletor', 114), ('impressora', 'Impressora', 100), ('radio', 'Rádio', 50), ('transpaleteira', 'Transpaleteira', 100), ('empilhadeira', 'Empilhadeira', 100)]
    criados = 0
    atualizados = 0
    
    for tipo, prefixo, total in configs:
        for i in range(1, total + 1):
            name = f"{prefixo}_{i:03d}"
            device = Device.query.filter_by(name=name).first()
            
            # Se o aparelho não existe, cria-o já na tua filial
            if not device:
                db.session.add(Device(name=name, type=tipo, status='disponivel', filial_id=current_user.filial_id))
                criados += 1
            # Se já existe (seja sem filial ou em outra filial), move para a tua filial atual
            else:
                device.filial_id = current_user.filial_id
                atualizados += 1
                
    db.session.commit()
    flash(f'Sucesso! {criados} aparelhos criados e {atualizados} vinculados ao CD {current_user.filial.nome}!', 'success')
    return redirect(url_for('main.dashboard'))


# ========================================================
# 4. GESTÃO DE USUÁRIOS E PERFIL
# ========================================================

@main_bp.route('/manage_users')
@login_required
def manage_users():
    if not current_user.is_privileged: abort(403)

    search = request.args.get('search', '')
    query = User.query
    
    # SEPARAÇÃO POR FILIAL: Lideranças veem apenas usuários do seu CD
    if current_user.role.lower() != 'ti' and current_user.filial_id:
        query = query.filter_by(filial_id=current_user.filial_id)

    if search: query = query.filter((User.name.ilike(f'%{search}%')) | (User.username.ilike(f'%{search}%')) | (User.colaborador_id.ilike(f'%{search}%')))
    users_pagination = query.order_by(User.name).paginate(page=request.args.get('page', 1, type=int), per_page=10)
    
    filiais = Filial.query.order_by(Filial.nome).all()
    return render_template('manage_users.html', users_pagination=users_pagination, search_term=search, filiais=filiais)

@main_bp.route('/create_user', methods=['POST'])
@login_required
def create_user():
    my_role = current_user.role.lower()
    role_final = 'colaborador' if 'lider' in my_role else request.form.get('role')
    username = request.form.get('username')
    colaborador_id = request.form.get('colaborador_id')

    if User.query.filter_by(username=username).first() or User.query.filter_by(colaborador_id=colaborador_id).first():
        flash('Erro: Login ou ID já existe.', 'danger')
        return redirect(url_for('main.manage_users'))

    new_user = User(
        name=request.form.get('name'), 
        username=username, 
        colaborador_id=colaborador_id,
        role=role_final, 
        password_hash=generate_password_hash(request.form.get('password')), 
        must_change_password=True, 
        turno=request.form.get('turno'), 
        funcao=request.form.get('funcao')
    )
    
    # Lógica de Filial via ID
    filial_id_form = request.form.get('filial_id')
    if filial_id_form:
        new_user.filial_id = int(filial_id_form)

    db.session.add(new_user)
    try:
        db.session.commit()
        flash(f'Usuário criado ({role_final})!', 'success')
    except IntegrityError:
        db.session.rollback()
        flash('Erro no banco de dados. Este usuário ou filial já existe.', 'danger')
        
    return redirect(url_for('main.manage_users'))

@main_bp.route('/reset_password/<int:user_id>', methods=['POST'])
@login_required
def reset_password(user_id):
    target_user = User.query.get_or_404(user_id)
    target_user.password_hash = generate_password_hash("maga1234")
    target_user.must_change_password = True
    db.session.commit()
    flash(f'Senha resetada para "maga1234".', 'success')
    return redirect(url_for('main.manage_users'))

@main_bp.route('/delete_user/<int:user_id>', methods=['POST'])
@login_required
def delete_user(user_id):
    if current_user.role.lower() != 'ti': abort(403)
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    flash(f"Usuário {user.name} excluído.", 'info')
    return redirect(url_for('main.manage_users'))

# ========================================================
# GESTÃO DE FILIAIS (CDs)
# ========================================================

@main_bp.route('/manage_filiais')
@login_required
def manage_filiais():
    if current_user.role.lower() != 'ti': abort(403)
    filiais = Filial.query.order_by(Filial.nome).all()
    return render_template('manage_filiais.html', filiais=filiais)

@main_bp.route('/create_filial', methods=['POST'])
@login_required
def create_filial():
    if current_user.role.lower() != 'ti': abort(403)
    nome = request.form.get('nome')
    codigo = request.form.get('codigo')
    
    if Filial.query.filter_by(nome=nome).first():
        flash('Erro: Já existe uma filial com este nome.', 'danger')
        return redirect(url_for('main.manage_filiais'))
        
    if codigo and Filial.query.filter_by(codigo=codigo).first():
        flash(f'Erro: Já existe uma filial com o código {codigo}.', 'danger')
        return redirect(url_for('main.manage_filiais'))
        
    new_filial = Filial(nome=nome, codigo=codigo, cidade=request.form.get('cidade'))
    db.session.add(new_filial)
    
    try:
        db.session.commit()
        flash(f'Filial {nome} cadastrada com sucesso!', 'success')
    except IntegrityError:
        db.session.rollback() 
        flash('Erro no banco de dados. Este código ou nome já existe.', 'danger')
        
    return redirect(url_for('main.manage_filiais'))

@main_bp.route('/edit_filial/<int:id>', methods=['POST'])
@login_required
def edit_filial(id):
    if current_user.role.lower() != 'ti': abort(403)
    
    filial = Filial.query.get_or_404(id)
    
    novo_nome = request.form.get('nome')
    novo_codigo = request.form.get('codigo')
    nova_cidade = request.form.get('cidade')
    
    if novo_nome != filial.nome and Filial.query.filter_by(nome=novo_nome).first():
        flash('Erro: Já existe outra filial com este nome.', 'danger')
        return redirect(url_for('main.manage_filiais'))
        
    if novo_codigo and novo_codigo != filial.codigo and Filial.query.filter_by(codigo=novo_codigo).first():
        flash(f'Erro: Já existe outra filial com o código {novo_codigo}.', 'danger')
        return redirect(url_for('main.manage_filiais'))
        
    filial.nome = novo_nome
    filial.codigo = novo_codigo
    filial.cidade = nova_cidade
    
    try:
        db.session.commit()
        flash(f'Filial {novo_nome} atualizada com sucesso!', 'success')
    except IntegrityError:
        db.session.rollback()
        flash('Erro no banco de dados. Informação duplicada.', 'danger')
        
    return redirect(url_for('main.manage_filiais'))

@main_bp.route('/delete_filial/<int:id>', methods=['POST'])
@login_required
def delete_filial(id):
    if current_user.role.lower() != 'ti': abort(403)
    filial = Filial.query.get_or_404(id)
    db.session.delete(filial)
    db.session.commit()
    flash(f'Filial {filial.nome} removida.', 'info')
    return redirect(url_for('main.manage_filiais'))

@main_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile_page():
    filiais = Filial.query.order_by(Filial.nome).all()
    if request.method == 'POST':

        novo_nome = request.form.get('name')
        if novo_nome: current_user.name = novo_nome
        current_user.turno = request.form.get('turno')
        current_user.funcao = request.form.get('funcao')
        
        # Permitir mudar filial apenas se não tiver uma ou for TI
        if not current_user.filial_id or current_user.role.lower() == 'ti':
            filial_id_form = request.form.get('filial_id')
            if filial_id_form:
                current_user.filial_id = int(filial_id_form)

        if current_user.is_privileged:
            new_pw = request.form.get('new_password')
            if new_pw: current_user.password_hash = generate_password_hash(new_pw)
        
        try:
            db.session.commit()
            flash('Perfil atualizado. O seu Turno agora é considerado nas regras do sistema.', 'success')
        except IntegrityError:
            db.session.rollback()
            flash('Erro ao atualizar o perfil. Alguma informação pode estar duplicada.', 'danger')
            
        return redirect(url_for('main.profile_page'))
    return render_template('profile.html', user=current_user, filiais=filiais)

# ========================================================
# 5. SISTEMA DE SUPORTE E TICKETS
# ========================================================

@main_bp.route('/device/<int:device_id>/report_problem', methods=['GET', 'POST'])
@login_required
def report_problem(device_id):
    device = Device.query.get_or_404(device_id)
    if request.method == 'POST':
        ticket = SupportTicket(device_id=device.id, reported_by_user_id=current_user.id, problem_description=request.form.get('problem_description'), status='aberto')
        db.session.add(ticket)
        device.status = 'aguardando_lider'
        device.current_user_id = None 
        db.session.commit()
        flash('Problema reportado! Você agora tem autorização para levantar um aparelho de substituição.', 'success')
        return redirect(url_for('main.dashboard'))
    return render_template('report_problem_page.html', device=device)

@main_bp.route('/device/<int:device_id>/add_zendesk', methods=['POST'])
@login_required
def add_zendesk_link(device_id):
    if current_user.role.lower() not in ['lideranca', 'liderança', 'lider', 'ti']: abort(403)
    device = Device.query.get_or_404(device_id)
    ticket = SupportTicket.query.filter_by(device_id=device.id, status='aberto').order_by(desc(SupportTicket.created_at)).first()
    if ticket:
        ticket.zendesk_link = request.form.get('zendesk_link')
        ticket.zendesk_added_by_user_id = current_user.id
        device.status = 'em_suporte'
        db.session.commit()
        flash('Liberado para o TI!', 'success')
    return redirect(url_for('main.dashboard'))

@main_bp.route('/device/<int:device_id>/resolve_support', methods=['POST'])
@login_required
def device_resolve_support(device_id):
    if current_user.role.lower() != 'ti': abort(403)
    device = Device.query.get_or_404(device_id)
    ticket = SupportTicket.query.filter_by(device_id=device.id, status='aberto').order_by(desc(SupportTicket.created_at)).first()
    if ticket:
        ticket.status = 'fechado'
        ticket.solution = request.form.get('solution', 'Solução aplicada pelo TI.')
        ticket.resolved_by_user_id = current_user.id
        ticket.resolved_at = datetime.utcnow()
    device.status = 'disponivel'
    db.session.commit()
    flash('Suporte finalizado!', 'success')
    return redirect(url_for('main.dashboard'))

# ========================================================
# 6. ESTOQUE, ANÁLISES E RELATÓRIOS (NOVO)
# ========================================================

@main_bp.route('/relatorio_manutencao')
@login_required
def relatorio_manutencao():
    if not current_user.is_privileged: abort(403)
        
    query_ranking = db.session.query(
        Device, db.func.count(SupportTicket.id).label('total_tickets')
    ).join(SupportTicket).group_by(Device.id)

    query_historico = SupportTicket.query

    if current_user.filial_id:
        query_ranking = query_ranking.filter(Device.filial_id == current_user.filial_id)
        query_historico = query_historico.filter_by(filial_id=current_user.filial_id)

    ranking_defeitos = query_ranking.order_by(desc('total_tickets')).all()
    historico_completo = query_historico.order_by(desc(SupportTicket.created_at)).all()

    return render_template('relatorio_manutencao.html', 
                           ranking=ranking_defeitos, 
                           historico=historico_completo)


@main_bp.route('/relatorio_sesmt')
@login_required
def relatorio_sesmt():
    if not current_user.is_privileged: abort(403)
    
    q_bateria = CheckoutLog.query.filter(CheckoutLog.nivel_bateria == 'Critica')
    q_devices = Device.query.filter(Device.type.in_(['transpaleteira', 'empilhadeira']))
    q_checkout = CheckoutLog.query.filter(CheckoutLog.checkin_time != None)

    if current_user.filial_id:
        q_bateria = q_bateria.filter_by(filial_id=current_user.filial_id)
        q_devices = q_devices.filter_by(filial_id=current_user.filial_id)
        q_checkout = q_checkout.filter_by(filial_id=current_user.filial_id)

    alertas_bateria = q_bateria.order_by(desc(CheckoutLog.checkout_time)).limit(50).all()
    
    heavy_machinery_ids = [d.id for d in q_devices.all()]
    q_riscos = SupportTicket.query.filter(SupportTicket.device_id.in_(heavy_machinery_ids))
    if current_user.filial_id:
        q_riscos = q_riscos.filter_by(filial_id=current_user.filial_id)
    
    riscos_maquinas = q_riscos.order_by(desc(SupportTicket.created_at)).limit(50).all()
    
    uso_total = {}
    logs_concluidos = q_checkout.all()
    for log in logs_concluidos:
        duration = (log.checkin_time - log.checkout_time).total_seconds() / 3600
        uso_total[log.device.name] = uso_total.get(log.device.name, 0) + duration
    
    ranking_uso = sorted(uso_total.items(), key=lambda x: x[1], reverse=True)[:10]

    return render_template('relatorio_sesmt.html', 
                           alertas_bateria=alertas_bateria, 
                           riscos_maquinas=riscos_maquinas,
                           ranking_uso=ranking_uso)


@main_bp.route('/global-history')
@login_required
def global_history():
    if not current_user.is_privileged: abort(403)
    
    q_logs = CheckoutLog.query
    q_tickets = SupportTicket.query

    if current_user.filial_id:
        q_logs = q_logs.filter_by(filial_id=current_user.filial_id)
        q_tickets = q_tickets.filter_by(filial_id=current_user.filial_id)

    logs = q_logs.order_by(desc(CheckoutLog.checkout_time)).paginate(page=request.args.get('page_usage', 1, type=int), per_page=20)
    tickets = q_tickets.order_by(desc(SupportTicket.created_at)).paginate(page=request.args.get('page_support', 1, type=int), per_page=20)
    return render_template('global_history.html', logs=logs, tickets=tickets)


@main_bp.route('/estoque_virtual')
@login_required
def estoque_virtual():
    if current_user.role.lower() != 'ti': abort(403)
    
    query = Device.query
    if current_user.filial_id:
        query = query.filter_by(filial_id=current_user.filial_id)
        
    devices = query.all()
    estoque = [d for d in devices if d.location == 'estoque']
    backup = [d for d in devices if d.location == 'backup']
    operacao = [d for d in devices if d.location == 'operacao']
    com_defeito = [d for d in devices if d.condition == 'com_defeito']
    return render_template('estoque_virtual.html', devices=devices, estoque=estoque, backup=backup, operacao=operacao, com_defeito=com_defeito, total_operacao=len(operacao), total_estoque=len(estoque), total_defeito=len(com_defeito), total_backup=len(backup))


@main_bp.route('/estoque/update/<int:device_id>', methods=['POST'])
@login_required
def update_estoque_device(device_id):
    if current_user.role.lower() != 'ti': return jsonify({'success': False}), 403
    device = Device.query.get_or_404(device_id)
    data = request.get_json(force=True, silent=True) or {}
    if 'location' in data: device.location = data['location']
    if 'condition' in data: device.condition = data['condition']
    try:
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False}), 500

@main_bp.route('/ia_analise')
@login_required
def ai_analise_page():
    if current_user.role.lower() not in ['ti', 'lideranca', 'liderança', 'lider', 'sesmt']: abort(403)
    return render_template('ai_analise.html')

@main_bp.route('/api/generate_report', methods=['POST'])
@login_required
def generate_report():
    if current_user.role.lower() not in ['ti', 'lideranca', 'liderança', 'lider', 'sesmt']: return jsonify({"error": "Acesso negado"}), 403
    try:
        data = request.get_json(silent=True) or {}
        prompt_usuario = data.get('prompt', 'Diagnóstico resumido.')
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent?key={GEMINI_API_KEY}"
        resp = requests.post(url, json={"contents": [{"parts": [{"text": prompt_usuario}]}]})
        if resp.status_code == 200: return jsonify({"response": resp.json()['candidates'][0]['content']['parts'][0]['text']})
        return jsonify({"response": f"Erro API: {resp.status_code}"}), 500
    except Exception as e: return jsonify({"response": str(e)}), 500

@main_bp.route('/alertas_ti')
@login_required
def alertas_ti():
    if current_user.role.lower() != 'ti': abort(403)
    
    query = AlertaTI.query
    if current_user.filial_id:
        query = query.filter_by(filial_id=current_user.filial_id)
        
    alertas = query.order_by(AlertaTI.data.desc()).limit(100).all()
    return render_template('alertas_ti.html', alertas=alertas)

# ========================================================
# 7. DOCUMENTAÇÃO TÉCNICA E APIS COMPLEMENTARES
# ========================================================

@main_bp.route('/documentacao_tecnica')
@login_required
def documentacao_tecnica(): return render_template('documentacao_tecnica.html', docs=TechnicalDoc.query.order_by(TechnicalDoc.category).all())

@main_bp.route('/documentacao_tecnica/novo', methods=['POST'])
@login_required
def create_documentacao():
    if current_user.role.lower() != 'ti': abort(403)
    db.session.add(TechnicalDoc(title=request.form.get('title'), category=request.form.get('category'), tags=request.form.get('tags'), content=request.form.get('content')))
    db.session.commit()
    flash('Manual técnico cadastrado!', 'success')
    return redirect(url_for('main.documentacao_tecnica'))

@main_bp.route('/documentacao_tecnica/deletar/<int:doc_id>', methods=['POST'])
@login_required
def delete_documentacao(doc_id):
    if current_user.role.lower() != 'ti': abort(403)
    db.session.delete(TechnicalDoc.query.get_or_404(doc_id))
    db.session.commit()
    flash('Manual removido.', 'success')
    return redirect(url_for('main.documentacao_tecnica'))

@main_bp.route('/api/chatbot', methods=['POST'])
@login_required
def chatbot_endpoint():
    try:
        data = request.get_json(silent=True) or {}
        user_message = data.get('message') or data.get('prompt')
        if not user_message: return jsonify({"response": "Como posso ajudar?"})
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
        resp = requests.post(url, json={"contents": [{"parts": [{"text": f"Responda ao suporte: {user_message}"}]}]})
        if resp.status_code == 200: return jsonify({"response": resp.json()['candidates'][0]['content']['parts'][0]['text']})
        return jsonify({"response": "Erro na IA."}), 500
    except Exception as e: return jsonify({"response": str(e)}), 500

@main_bp.route('/api/device_history', methods=['GET'])
@login_required
def device_history_api():
    device_id = request.args.get('device_id')
    logs = CheckoutLog.query.filter_by(device_id=device_id).order_by(desc(CheckoutLog.checkout_time)).all()
    history = [
        {
            'colaborador': log.user_id,
            'acao': 'Retirada',
            'data': log.checkout_time.strftime('%d/%m/%Y %H:%M') if log.checkout_time else ''
        }
        for log in logs
    ]
    return {'history': history}

@main_bp.route('/forgot_password')
def forgot_password(): return render_template('forgot_password.html')

@main_bp.route('/export/<report_type>')
@login_required
def export_csv(report_type):
    if not current_user.is_privileged: abort(403)
    
    import io
    import csv
    from flask import make_response

    output = io.StringIO()
    # Adicionar BOM para Excel reconhecer UTF-8 corretamente
    output.write('\ufeff')
    writer = csv.writer(output, delimiter=';', quoting=csv.QUOTE_MINIMAL)

    filename = f"relatorio_{report_type}_{datetime.now().strftime('%Y%m%d_%H%M')}.csv"

    if report_type == 'historico':
        writer.writerow(['Equipamento', 'Tipo', 'Colaborador', 'ID', 'Retirada', 'Devolução', 'Setor', 'Filial'])
        query = CheckoutLog.query
        if current_user.filial_id:
            query = query.filter_by(filial_id=current_user.filial_id)
        
        logs = query.order_by(CheckoutLog.checkout_time.desc()).all()
        for log in logs:
            writer.writerow([
                log.device.name, log.device.type, log.user.name if log.user else '---', 
                log.user.colaborador_id if log.user else '---',
                log.checkout_time.strftime('%d/%m/%Y %H:%M') if log.checkout_time else '---',
                log.checkin_time.strftime('%d/%m/%Y %H:%M') if log.checkin_time else 'EM USO',
                log.setor or '---',
                log.filial.nome if log.filial else 'GLOBAL'
            ])

    elif report_type == 'suporte':
        writer.writerow(['Equipamento', 'Problema', 'Status', 'Relatado por', 'Data Abertura', 'Solução', 'Resolvido em', 'Filial'])
        query = SupportTicket.query
        if current_user.filial_id:
            query = query.filter_by(filial_id=current_user.filial_id)
            
        tickets = query.order_by(SupportTicket.created_at.desc()).all()
        for t in tickets:
            writer.writerow([
                t.device.name, t.problem_description, t.status, t.reported_by.name if t.reported_by else '---',
                t.created_at.strftime('%d/%m/%Y %H:%M') if t.created_at else '---',
                t.solution or '---',
                t.resolved_at.strftime('%d/%m/%Y %H:%M') if t.resolved_at else 'ABERTO',
                t.filial.nome if t.filial else 'GLOBAL'
            ])

    response = make_response(output.getvalue())
    response.headers["Content-Disposition"] = f"attachment; filename={filename}"
    response.headers["Content-type"] = "text/csv; charset=utf-8"
    return response

