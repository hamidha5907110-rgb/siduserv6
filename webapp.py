#!/usr/bin/env python3
# webapp.py – Flask server for SID Premium Hoster dashboard
# Integrates with sid_bot.py via import (no changes to sid_bot.py required)

import os
import json
import time
from flask import Flask, render_template, request, jsonify, send_from_directory

# Import the bot's database and runner (only works when not in userbot mode)
# The bot file must be in the same directory.
# Change this line:
# To this:
import my_awesome_bot as sid_bot

app = Flask(__name__)

# Use the bot's database and runner objects
db = sid_bot.db
runner = sid_bot.runner

# Reuse the helper functions from the bot (optional)
# We'll use our own API endpoints.

# ---------- API Endpoints ----------

@app.route("/api/stats", methods=["GET"])
def api_stats():
    """Return global statistics."""
    try:
        total_users = db.user_count()
        hosted_count = db.hosted_count()
        running_count = runner.running_count()
        # Uptime: use the bot's START_TIME if available, else compute
        uptime_secs = int(time.time() - getattr(sid_bot, 'START_TIME', time.time()))
        h, r = divmod(uptime_secs, 3600)
        m, s = divmod(r, 60)
        uptime_str = f"{h}h {m}m {s}s"
        return jsonify({
            "totalUsers": total_users,
            "hostedCount": hosted_count,
            "runningCount": running_count,
            "uptime": uptime_str
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/accounts", methods=["GET"])
def api_accounts():
    """Return list of accounts for the requesting user (mock owner for demo)."""
    # In a real multi-user setup, you'd get user_id from session.
    # For simplicity, we return all accounts (or you can filter by owner).
    # We'll return a list of hosted accounts with their status.
    accounts = []
    for uid_str in db.get_all_users():
        uid = int(uid_str)
        for acct in db.get_accounts(uid):
            if acct.get("hosted"):
                slot = acct["slot"]
                running = runner.is_running(uid, slot)
                uptime = runner.get_uptime(uid, slot) if running else None
                accounts.append({
                    "userId": uid,
                    "userName": db.get_user_meta(uid).get("first_name", f"User {uid}"),
                    "slot": slot,
                    "phone": acct.get("phone", f"Account #{slot+1}"),
                    "running": running,
                    "uptime": uptime if running else "—"
                })
    return jsonify(accounts)

@app.route("/api/host", methods=["POST"])
def api_host():
    """Simulate hosting a new account (you can replace with real login flow)."""
    data = request.get_json()
    phone = data.get("phone")
    name = data.get("name", "New User")
    if not phone:
        return jsonify({"success": False, "message": "Phone number required"}), 400
    # In real implementation, you would initiate the login flow via /host command.
    # For demo, we create a mock account.
    # Since we don't have a real session, we'll just simulate success.
    # You could call sid_bot.cmd_host_start logic, but it's async and complex.
    # We'll just return success to show the UI.
    return jsonify({"success": True, "message": f"Userbot for {phone} deployed (simulated)"})

@app.route("/api/restart", methods=["POST"])
def api_restart():
    data = request.get_json()
    user_id = data.get("userId")
    slot = data.get("slot")
    if user_id is None or slot is None:
        return jsonify({"success": False, "message": "Missing userId or slot"}), 400
    # Get the account's session string from DB
    acct = db.get_account(user_id, slot)
    if not acct or not acct.get("session_string"):
        return jsonify({"success": False, "message": "Account not found or no session"}), 404
    # Restart using runner
    ok = runner.restart_userbot(
        user_id, slot,
        sid_bot.TELEGRAM_API_ID, sid_bot.TELEGRAM_API_HASH,
        acct["session_string"], str(user_id)
    )
    if ok:
        return jsonify({"success": True, "message": f"Account {slot+1} restarted"})
    else:
        return jsonify({"success": False, "message": "Restart failed"}), 500

@app.route("/api/logout", methods=["POST"])
def api_logout():
    data = request.get_json()
    user_id = data.get("userId")
    slot = data.get("slot")
    if user_id is None or slot is None:
        return jsonify({"success": False, "message": "Missing userId or slot"}), 400
    # Stop the process and remove account
    runner.stop_userbot(user_id, slot)
    db.remove_account(user_id, slot)
    # Also remove session directory
    import shutil
    session_dir = f"data/sessions/{user_id}/{slot}"
    shutil.rmtree(session_dir, ignore_errors=True)
    return jsonify({"success": True, "message": f"Account {slot+1} logged out"})

# ---------- Frontend Serving ----------
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/static/<path:path>")
def serve_static(path):
    return send_from_directory("static", path)

if __name__ == "__main__":
    # For Render, use port from environment
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
