from flask import Blueprint, flash, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash

from auth import login_required
from models import (
    add_user,
    create_order,
    delete_order,
    get_order,
    get_orders,
    get_user_by_username,
    update_order,
)

main = Blueprint("main", __name__)

# Limites de tamanho para validação
MAX_USERNAME_LENGTH = 50
MAX_PASSWORD_LENGTH = 100
MAX_TITLE_LENGTH = 100
MAX_CLIENT_LENGTH = 100
MAX_DESCRIPTION_LENGTH = 1000


def validate_username(username):
    """Valida o nome de usuário."""
    if not username or len(username) < 3:
        return "Usuário deve ter no mínimo 3 caracteres."
    if len(username) > MAX_USERNAME_LENGTH:
        return f"Usuário não pode ter mais de {MAX_USERNAME_LENGTH} caracteres."
    if not username.replace("_", "").replace("-", "").isalnum():
        return "Usuário deve conter apenas letras, números, hífens e underscores."
    return None


def validate_password(password):
    """Valida a senha."""
    if not password or len(password) < 6:
        return "Senha deve ter no mínimo 6 caracteres."
    if len(password) > MAX_PASSWORD_LENGTH:
        return f"Senha não pode ter mais de {MAX_PASSWORD_LENGTH} caracteres."
    return None


def validate_order(title, client, description):
    """Valida os dados de uma ordem."""
    if not title or len(title) < 3:
        return "Título deve ter no mínimo 3 caracteres."
    if len(title) > MAX_TITLE_LENGTH:
        return f"Título não pode ter mais de {MAX_TITLE_LENGTH} caracteres."
    if not client or len(client) < 2:
        return "Cliente deve ter no mínimo 2 caracteres."
    if len(client) > MAX_CLIENT_LENGTH:
        return f"Cliente não pode ter mais de {MAX_CLIENT_LENGTH} caracteres."
    if not description or len(description) < 5:
        return "Descrição deve ter no mínimo 5 caracteres."
    if len(description) > MAX_DESCRIPTION_LENGTH:
        return f"Descrição não pode ter mais de {MAX_DESCRIPTION_LENGTH} caracteres."
    return None


@main.route("/")
@login_required
def index():
    selected_status = request.args.get("status", "").strip()
    all_orders = get_orders(session["user_id"])

    if selected_status:
        orders = [order for order in all_orders if order["status"] == selected_status]
    else:
        orders = all_orders

    status_names = ["Aberta", "Em andamento", "Concluída"]
    status_report = {}
    total_orders = len(all_orders)

    for status in status_names:
        count = sum(1 for order in all_orders if order["status"] == status)
        percentage = round((count / total_orders) * 100, 1) if total_orders else 0
        status_report[status] = {"count": count, "percentage": percentage}

    return render_template(
        "index.html",
        orders=orders,
        selected_status=selected_status,
        status_report=status_report,
        total_orders=total_orders,
    )


@main.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        if not username or not password:
            flash("Preencha usuário e senha.")
            return render_template("login.html")

        user = get_user_by_username(username)
        if user and check_password_hash(user["password_hash"], password):
            session.clear()
            session["user_id"] = user["id"]
            session["username"] = user["username"]
            flash("Login realizado com sucesso.")
            return redirect(url_for("main.index"))

        flash("Credenciais inválidas.")

    return render_template("login.html")


@main.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")

        # Validação de username
        username_error = validate_username(username)
        if username_error:
            flash(username_error)
            return render_template("register.html")

        # Validação de senha
        password_error = validate_password(password)
        if password_error:
            flash(password_error)
            return render_template("register.html")

        if password != confirm_password:
            flash("As senhas não conferem.")
            return render_template("register.html")

        if get_user_by_username(username):
            flash("Este usuário já existe.")
            return render_template("register.html")

        add_user(username, generate_password_hash(password))
        flash("Usuário cadastrado com sucesso.")
        return redirect(url_for("main.login"))

    return render_template("register.html")


@main.route("/logout")
def logout():
    session.clear()
    flash("Você saiu da sessão.")
    return redirect(url_for("main.login"))


@main.route("/ordens/nova", methods=["GET", "POST"])
@login_required
def new_order():
    if request.method == "POST":
        title = request.form.get("title", "").strip()
        client = request.form.get("client", "").strip()
        description = request.form.get("description", "").strip()
        status = request.form.get("status", "Aberta")

        # Validação de dados
        order_error = validate_order(title, client, description)
        if order_error:
            flash(order_error)
            return render_template("order_form.html", order=None)

        create_order(title, client, description, status, session["user_id"])
        flash("Ordem de serviço criada com sucesso.")
        return redirect(url_for("main.index"))

    return render_template("order_form.html", order=None)


@main.route("/ordens/<int:order_id>/editar", methods=["GET", "POST"])
@login_required
def edit_order(order_id):
    order = get_order(order_id, session["user_id"])
    if not order:
        flash("Ordem não encontrada.")
        return redirect(url_for("main.index"))

    if request.method == "POST":
        title = request.form.get("title", "").strip()
        client = request.form.get("client", "").strip()
        description = request.form.get("description", "").strip()
        status = request.form.get("status", "Aberta")

        # Validação de dados
        order_error = validate_order(title, client, description)
        if order_error:
            flash(order_error)
            return render_template("order_form.html", order=order)

        update_order(order_id, title, client, description, status, session["user_id"])
        flash("Ordem atualizada com sucesso.")
        return redirect(url_for("main.index"))

    return render_template("order_form.html", order=order)


@main.route("/ordens/<int:order_id>/excluir", methods=["POST"])
@login_required
def delete_order_route(order_id):
    order = get_order(order_id, session["user_id"])
    if not order:
        flash("Ordem não encontrada.")
        return redirect(url_for("main.index"))
    delete_order(order_id, session["user_id"])
    flash("Ordem removida.")
    return redirect(url_for("main.index"))
