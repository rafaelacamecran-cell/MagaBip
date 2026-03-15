from flask import Blueprint, render_template, redirect, url_for, request, flash, session, current_app
from flask_login import login_user, logout_user, current_user, login_required
from forms import LoginForm
from models import User
from extensions import db
from datetime import datetime, timezone 
from authlib.integrations.flask_client import OAuth
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from routes_main import process_social_login
from auth_helpers import is_corporate_email

def get_oauth():
    # Garante que o OAuth está sempre disponível via current_app
    if hasattr(current_app, 'extensions') and 'authlib.integrations.flask_client' in current_app.extensions:
        return current_app.extensions['authlib.integrations.flask_client']
    return OAuth(current_app)

auth_bp = Blueprint('auth', __name__)

# --- ROTA DE BOAS-VINDAS (SPLASH SCREEN) ---
@auth_bp.route('/')
def welcome():
    # Se o utilizador já estiver logado, manda-o para o painel
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    # Incrementa métrica Prometheus
    if hasattr(current_app, 'metrics'):
        current_app.metrics['HOME_PAGE_ACCESSES'].inc()
    
    # Se não, mostra a tela de boas-vindas
    return render_template('welcome.html')

# --- ROTA DE LOGIN PRINCIPAL ---
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    # Tenta instanciar o formulário se a classe existir
    form = LoginForm() if LoginForm else None

    # 1. Se o usuário já estiver autenticado, redireciona
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))

    # 2. Processa a requisição POST (tentativa de login)
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = User.query.filter((User.username == username) | (User.email == username) | (User.colaborador_id == username)).first()

        if not user or not user.check_password(password):
            flash('ID de Colaborador ou senha inválidos.', 'danger')
            return render_template('login.html', form=form) 

        login_user(user)
        
        # ==================================
        #  Lógica de Sessão e Atividade
        # ==================================
        session.permanent = True 
        session['last_activity'] = datetime.now(timezone.utc)
        
        # Se for o primeiro login, força a troca de senha
        if user.must_change_password:
            flash('Este é o seu primeiro acesso. Por favor, crie uma nova senha.', 'info')
            return redirect(url_for('auth.change_password'))

        # Se não, vai para o dashboard normal
        return redirect(url_for('main.dashboard'))

    # 3. Para requisições GET
    return render_template('login.html', form=form)

# --- ROTA DE LOGIN CORPORATIVO ---
@auth_bp.route('/login_corporativo')
def login_corporativo():
    # Redireciona para o login Google, mas só permite domínios corporativos
    redirect_uri = url_for('auth.auth_google_corporativo_callback', _external=True)
    return get_oauth().google.authorize_redirect(redirect_uri)

@auth_bp.route('/auth_google_corporativo_callback')
def auth_google_corporativo_callback():
    token = get_oauth().google.authorize_access_token()
    user_info = get_oauth().google.parse_id_token(token)
    email = user_info['email']
    name = user_info['name']
    if not is_corporate_email(email):
        flash('Apenas e-mails corporativos são permitidos para este login.', 'danger')
        return redirect(url_for('auth.login'))
    return process_social_login(email, name, "E-mail Corporativo")

# --- ROTAS SSOCORP (Portal Luiza / Portal do Colaborador) ---
@auth_bp.route('/login_ssocorp')
def login_ssocorp():
    redirect_uri = url_for('auth.auth_ssocorp_callback', _external=True)
    return get_oauth().ssocorp.authorize_redirect(redirect_uri)

@auth_bp.route('/auth_ssocorp_callback')
def auth_ssocorp_callback():
    token = get_oauth().ssocorp.authorize_access_token()
    # Tenta obter userinfo do token ou via endpoint se configurado
    user_info = token.get('userinfo')
    if not user_info:
        # Se não vier no token, tenta buscar no endpoint da API
        resp = get_oauth().ssocorp.get('userinfo')
        user_info = resp.json() if resp.status_code == 200 else {}

    email = user_info.get('email')
    name = user_info.get('name') or user_info.get('preferred_username')

    if not email:
        flash('Não foi possível obter seu e-mail do Portal Corporativo.', 'danger')
        return redirect(url_for('auth.login'))

    return process_social_login(email, name, "Portal Corporativo (SSOCorp)")

# --- ROTA DE LOGOUT ---
@auth_bp.route('/logout')
def logout():
    logout_user()
    # flash('Você saiu do sistema.') # Removido conforme solicitado
    return redirect(url_for('auth.login'))

# --- ROTA PARA TROCAR A SENHA ---
@auth_bp.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    if request.method == 'POST':
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')

        if not new_password or new_password != confirm_password:
            flash('As senhas não conferem. Tente novamente.', 'danger')
            return redirect(url_for('auth.change_password'))

        # Atualiza o utilizador
        user = current_user
        user.set_password(new_password)
        user.must_change_password = False 
        db.session.commit()

        flash('Senha atualizada com sucesso! Você já pode usar o sistema.', 'success')
        session['last_activity'] = datetime.now(timezone.utc)
        return redirect(url_for('main.dashboard'))

    return render_template('change_password.html')

# --- ROTA "ESQUECI MINHA SENHA" ---
@auth_bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form.get('email')
        
        # AQUI entraria a lógica real de envio de e-mail.
        # Por enquanto, apenas simulamos que deu certo para não travar o usuário.
        flash(f'Se o e-mail {email} estiver cadastrado, enviaremos um link de recuperação.', 'info')
        
        return redirect(url_for('auth.login'))

    return render_template('forgot_password.html')