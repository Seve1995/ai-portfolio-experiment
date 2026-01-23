"""
AI Portfolio Dashboard - Flask Web App
Remote access to generate prompts and execute trades
"""
import os
from pathlib import Path
from functools import wraps
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from dotenv import load_dotenv

# Load environment variables from parent directory (root .env)
root_dir = Path(__file__).parent.parent
load_dotenv(root_dir / ".env")

from core.prompt_generator import generate_prompt, MODELS
from core.trade_executor import execute_trades

app = Flask(__name__)
app.secret_key = os.getenv("APP_SECRET_KEY", os.urandom(24))

# Simple password protection
APP_PASSWORD = os.getenv("APP_PASSWORD", "changeme")


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get("logged_in"):
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated_function


@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        if request.form.get("password") == APP_PASSWORD:
            session["logged_in"] = True
            return redirect(url_for("index"))
        error = "Invalid password"
    return render_template("login.html", error=error)


@app.route("/logout")
def logout():
    session.pop("logged_in", None)
    return redirect(url_for("login"))


@app.route("/")
@login_required
def index():
    return render_template("index.html", models=MODELS)


@app.route("/generate", methods=["POST"])
@login_required
def generate():
    """Generate AI prompt for selected model."""
    model_key = request.form.get("model", "1")
    
    try:
        prompt_text, status = generate_prompt(model_key)
        return jsonify({
            "success": True,
            "prompt": prompt_text,
            "status": status
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        })


@app.route("/execute", methods=["POST"])
@login_required
def execute():
    """Execute trades from AI response."""
    model_key = request.form.get("model", "1")
    trade_table = request.form.get("trade_table", "")
    dry_run = request.form.get("dry_run", "false") == "true"
    
    if not trade_table.strip():
        return jsonify({
            "success": False,
            "error": "No trade table provided"
        })
    
    try:
        logs = execute_trades(model_key, trade_table, dry_run=dry_run)
        return jsonify({
            "success": True,
            "logs": logs
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        })


if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
