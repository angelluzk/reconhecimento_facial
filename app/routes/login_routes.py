from flask import (
    Blueprint, render_template, request, redirect, url_for, flash, session
)
from app.services.login_service import (
    login_usuario, cadastrar_usuario, atualizar_senha_usuario
)

login_routes = Blueprint('login_routes', __name__)


@login_routes.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        senha = request.form['senha']
        lembrar_me = 'lembrar-me' in request.form
        usuario = login_usuario(email, senha)

        if usuario:
            session['usuario_email'] = email
            session['usuario_id'] = usuario['id']
            session['is_admin'] = usuario['is_admin']

            if lembrar_me:
                response = redirect(url_for('dashboard_routes.dashboard'))
                response.set_cookie('usuario_email', email,
                                    max_age=60*60*24*30)
                return response

            return redirect(url_for('dashboard_routes.dashboard'))

        else:
            flash("E-mail ou senha inválidos!", 'danger')
            return render_template('login.html')

    return render_template('login.html')


@login_routes.route('/cadastro_admin', methods=['GET', 'POST'])
def cadastro_admin():
    if request.method == 'POST':
        nome = request.form['nome']
        email = request.form['email']
        senha = request.form['senha']
        is_admin = False

        if cadastrar_usuario(nome, email, senha, is_admin):
            flash("Cadastro realizado com sucesso!", 'success')
            return redirect(url_for('login_routes.login'))
        else:
            flash(
                "Erro ao cadastrar usuário. Verifique se o e-mail já está em uso.", 'danger')
            return render_template('login.html')

    return render_template('cadastro_admin.html')


@login_routes.route('/esqueci_senha', methods=['GET', 'POST'])
def esqueci_senha():
    if request.method == 'POST':
        email = request.form['email']
        nova_senha = request.form['nova_senha']

        if atualizar_senha_usuario(email, nova_senha):
            flash('Senha atualizada com sucesso!', 'success')
            return redirect(url_for('login_routes.login'))
        else:
            flash('E-mail não encontrado.', 'danger')

    return render_template('esqueci_senha.html')


@login_routes.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login_routes.login'))