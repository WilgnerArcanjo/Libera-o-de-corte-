from functools import wraps

from flask import flash, redirect, session, url_for


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if "user_id" not in session:
            flash("Faça login para acessar esta página.")
            return redirect(url_for("main.login"))
        return view(*args, **kwargs)

    return wrapped
