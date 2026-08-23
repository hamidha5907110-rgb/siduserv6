import os, sys, threading, time, random, json, logging
from typing import Optional, Dict, Set

# ==========================================
# 🛑 DEPENDENCY CHECKS
# ==========================================
try:
    import telebot
except ImportError:
    print("\n❌ CRITICAL ERROR: pyTelegramBotAPI is not installed!")
    print("👉 Run: pip install pyTelegramBotAPI\n")
    sys.exit(1)

try:
    import pyrogram
except ImportError:
    print("\n❌ CRITICAL ERROR: Pyrogram is not installed!")
    print("👉 Run: pip install pyrogram tgcrypto\n")
    sys.exit(1)

# ==========================================
# 🌸 CONFIGURATION
# ==========================================

OWNER_IDS_RAW = "2119464081"               # comma-separated Telegram IDs
OWNER_IDS = set(int(x.strip()) for x in OWNER_IDS_RAW.split(",") if x.strip().isdigit())

BOT_TOKENS = [
    "8685762136:AAGb2ZJuae4RZg34eUaEJs7fH1BvukZFXTI",
    "8760147668:AAFcextp6TOEmx8AVuMkFqF_sttSEIuU9Zo",
    "8889832400:AAHhsQcyLdFl4IqV2qCJfwlDN_HYPRL6N_4",
    "8961186063:AAEyiW_Gil_jS4CPwrL-kRljOa3CUSwDvY0",
    "8925438420:AAEkH9ifRSQn1JNQSYbw-kaiYVXDUj4MYdo",
    "7858818327:AAExBuyJweHmYm7AgBaWlsEHLV3bPFIKF4E",
    "8799511134:AAGi965XCc-0YlEdpZFPtQz6_cJZL1epQQ4",
    "8556288413:AAGSGSavd1aEGxGxspWlKGv19KYAx0G1fTE",
    "8656976249:AAGsBCnFWMHffu6Ik98XTWCSFtOA3whsKBg"
]

# Pyrogram credentials (replace with your own)
API_ID = 12345          # get from my.telegram.org
API_HASH = "your_api_hash"

# ==========================================

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("SID")

STATE_FILE = "sid_state.json"
CUTE_EMOJIS = ["🌸","💕","✨","🦋","🍓","🌷","🎀","💫","🌺","🍒","🌻","💖","🌈","🫧","🧁","🌙","⭐","🍑","🪷","💗","🐾","🌼","💝","🫶","🍀"]

def cute_emoji():
    return random.choice(CUTE_EMOJIS)

def normalize(text: str) -> str:
    text = text.strip()
    if text.startswith("/"):
        text = text[1:]
    parts = text.split(None, 1)
    if parts and "@" in parts[0]:
        parts[0] = parts[0].split("@")[0]
    return " ".join(parts)

_all_states = {}                     # bot states per bot label
ub_client = None                     # Pyrogram client for userbot
ub_state = None                      # Userbot state object
ub_lock = threading.Lock()           # to safely start/stop userbot

# ==========================================
# 📦 STATE CLASSES
# ==========================================

class BotState:
    def __init__(self):
        self.subadmins = set()
        self.spam_flags = {}
        self.spam_threads = {}
        self.spam_delay = {}
        self.spam_msgs = {}
        self.nc_flags = {}
        self.nc_threads = {}
        self.nc_delay = {}
        self.nc_names = {}
        self.dc_flags = {}
        self.dc_threads = {}
        self.dc_delay = {}
        self.dc_descs = {}
        self.auto_delete = {}
        self.auto_react = {}

    def is_admin(self, user_id):
        return user_id in OWNER_IDS or user_id in self.subadmins

class UserbotState:
    def __init__(self):
        self.spam_flags = {}
        self.spam_threads = {}
        self.spam_delay = {}
        self.spam_msgs = {}
        self.nc_flags = {}
        self.nc_threads = {}
        self.nc_delay = {}
        self.nc_names = {}
        self.dc_flags = {}
        self.dc_threads = {}
        self.dc_delay = {}
        self.dc_descs = {}

# ==========================================
# 💾 PERSISTENCE
# ==========================================

def save_all_states():
    data = {}
    # Bot states
    for label, state in _all_states.items():
        spam = {}
        for cid in set(list(state.spam_flags) + list(state.spam_msgs)):
            spam[str(cid)] = {"active": state.spam_flags.get(cid, False), "msg": state.spam_msgs.get(cid, ""), "delay": state.spam_delay.get(cid, 1.0)}
        nc = {}
        for cid in set(list(state.nc_flags) + list(state.nc_names)):
            nc[str(cid)] = {"active": state.nc_flags.get(cid, False), "name": state.nc_names.get(cid, ""), "delay": state.nc_delay.get(cid, 2.0)}
        dc = {}
        for cid in set(list(state.dc_flags) + list(state.dc_descs)):
            dc[str(cid)] = {"active": state.dc_flags.get(cid, False), "desc": state.dc_descs.get(cid, ""), "delay": state.dc_delay.get(cid, 3.0)}
        data[label] = {
            "spam": spam, "nc": nc, "dc": dc,
            "subadmins": list(state.subadmins),
            "auto_delete": {str(cid): list(uids) for cid, uids in state.auto_delete.items()},
            "auto_react": {str(k): v for k, v in state.auto_react.items()}
        }
    # Userbot state
    if ub_state:
        spam_ub = {}
        for cid in set(list(ub_state.spam_flags) + list(ub_state.spam_msgs)):
            spam_ub[str(cid)] = {"active": ub_state.spam_flags.get(cid, False), "msg": ub_state.spam_msgs.get(cid, ""), "delay": ub_state.spam_delay.get(cid, 1.0)}
        nc_ub = {}
        for cid in set(list(ub_state.nc_flags) + list(ub_state.nc_names)):
            nc_ub[str(cid)] = {"active": ub_state.nc_flags.get(cid, False), "name": ub_state.nc_names.get(cid, ""), "delay": ub_state.nc_delay.get(cid, 2.0)}
        dc_ub = {}
        for cid in set(list(ub_state.dc_flags) + list(ub_state.dc_descs)):
            dc_ub[str(cid)] = {"active": ub_state.dc_flags.get(cid, False), "desc": ub_state.dc_descs.get(cid, ""), "delay": ub_state.dc_delay.get(cid, 3.0)}
        data["__userbot__"] = {"spam": spam_ub, "nc": nc_ub, "dc": dc_ub}
    try:
        with open(STATE_FILE, "w") as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        logger.warning(f"State save error: {e}")

def load_all_states():
    if not os.path.exists(STATE_FILE):
        return
    try:
        with open(STATE_FILE) as f:
            data = json.load(f)
    except Exception:
        return
    # Restore userbot state if present
    if "__userbot__" in data:
        ub = data["__userbot__"]
        global ub_state
        if ub_state is None:
            ub_state = UserbotState()
        for cid_str, info in ub.get("spam", {}).items():
            if info.get("active") and info.get("msg"):
                cid = int(cid_str)
                ub_state.spam_delay[cid] = info.get("delay", 1.0)
                ub_state.spam_flags[cid] = True
                ub_state.spam_msgs[cid] = info["msg"]
        for cid_str, info in ub.get("nc", {}).items():
            if info.get("active") and info.get("name"):
                cid = int(cid_str)
                ub_state.nc_delay[cid] = info.get("delay", 2.0)
                ub_state.nc_flags[cid] = True
                ub_state.nc_names[cid] = info["name"]
        for cid_str, info in ub.get("dc", {}).items():
            if info.get("active") and info.get("desc"):
                cid = int(cid_str)
                ub_state.dc_delay[cid] = info.get("delay", 3.0)
                ub_state.dc_flags[cid] = True
                ub_state.dc_descs[cid] = info["desc"]
    # Bot states are restored per bot in start_bot

# ==========================================
# 🧵 WORKER FUNCTIONS (BOT & USERBOT)
# ==========================================

def spam_worker_bot(bot, state, chat_id, text):
    while state.spam_flags.get(chat_id, False):
        try:
            bot.send_message(chat_id, text)
        except Exception:
            pass
        time.sleep(state.spam_delay.get(chat_id, 1.0))

def nc_worker_bot(bot, state, chat_id, base_name):
    while state.nc_flags.get(chat_id, False):
        try:
            bot.set_chat_title(chat_id, f"{base_name} {cute_emoji()}")
        except Exception:
            pass
        time.sleep(state.nc_delay.get(chat_id, 2.0))

def dc_worker_bot(bot, state, chat_id, base_desc):
    while state.dc_flags.get(chat_id, False):
        try:
            bot.set_chat_description(chat_id, f"{base_desc} {cute_emoji()}")
        except Exception:
            pass
        time.sleep(state.dc_delay.get(chat_id, 3.0))

# Userbot workers (use Pyrogram client)
def spam_worker_ub(client, state, chat_id, text):
    while state.spam_flags.get(chat_id, False):
        try:
            client.send_message(chat_id, text)
        except Exception:
            pass
        time.sleep(state.spam_delay.get(chat_id, 1.0))

def nc_worker_ub(client, state, chat_id, base_name):
    while state.nc_flags.get(chat_id, False):
        try:
            client.set_chat_title(chat_id, f"{base_name} {cute_emoji()}")
        except Exception:
            pass
        time.sleep(state.nc_delay.get(chat_id, 2.0))

def dc_worker_ub(client, state, chat_id, base_desc):
    while state.dc_flags.get(chat_id, False):
        try:
            client.set_chat_description(chat_id, f"{base_desc} {cute_emoji()}")
        except Exception:
            pass
        time.sleep(state.dc_delay.get(chat_id, 3.0))

# ==========================================
# 🤖 USERBOT MANAGEMENT (with interactive login)
# ==========================================

# Temporary storage for login sessions
login_sessions = {}  # user_id -> {step, phone, client, message_id}

def start_userbot_login(user_id, bot, message):
    """Initiate login process for userbot."""
    if user_id in login_sessions:
        bot.reply_to(message, "⏳ You already have a login session in progress. Please complete or cancel it.")
        return
    login_sessions[user_id] = {"step": "phone", "phone": None, "client": None, "message_id": None}
    bot.reply_to(message, "📱 Please enter your phone number (with country code, e.g., +1234567890):\n\nType /cancel to abort.")

def cancel_login(user_id, bot, message):
    if user_id in login_sessions:
        del login_sessions[user_id]
        bot.reply_to(message, "❌ Login cancelled.")
    else:
        bot.reply_to(message, "No active login session.")

def process_login_step(user_id, text, bot, message):
    if user_id not in login_sessions:
        return
    session = login_sessions[user_id]
    step = session["step"]

    if step == "phone":
        phone = text.strip()
        if not phone.startswith("+") or not phone[1:].isdigit():
            bot.reply_to(message, "❌ Invalid phone number. Please include country code, e.g., +1234567890")
            return
        session["phone"] = phone
        # Create pyrogram client
        try:
            client = pyrogram.Client(
                f"userbot_{user_id}",
                api_id=API_ID,
                api_hash=API_HASH,
                in_memory=True
            )
            session["client"] = client
            # Send code request
            client.start()
            sent_code = client.send_code(phone)
            session["sent_code"] = sent_code
            client.stop()  # temporarily stop
            session["step"] = "otp"
            bot.reply_to(message, f"✅ OTP sent to {phone}. Please enter the code you received:")
        except Exception as e:
            bot.reply_to(message, f"❌ Error sending OTP: {e}")
            del login_sessions[user_id]
            return

    elif step == "otp":
        otp = text.strip()
        if not otp.isdigit():
            bot.reply_to(message, "❌ OTP must be numeric. Try again or /cancel")
            return
        client = session["client"]
        try:
            client.start()
            # Sign in with OTP
            signed_in = client.sign_in(session["phone"], session["sent_code"].phone_code_hash, otp)
            if hasattr(signed_in, 'is_password_required') and signed_in.is_password_required:
                session["step"] = "2fa"
                bot.reply_to(message, "🔐 Two‑factor authentication is enabled. Please enter your 2FA password:")
                client.stop()
            else:
                # Login successful
                session["step"] = "done"
                # Get session string
                session_string = client.export_session_string()
                client.stop()
                # Now start the userbot with the session string
                success = start_userbot(session_string, user_id)
                if success:
                    bot.reply_to(message, "✅ Userbot deployed successfully! You can now use /ubspam, /ubnc, /ubdc.")
                else:
                    bot.reply_to(message, "❌ Failed to start userbot. Check logs.")
                del login_sessions[user_id]
        except Exception as e:
            bot.reply_to(message, f"❌ Login error: {e}")
            client.stop()
            del login_sessions[user_id]

    elif step == "2fa":
        password = text.strip()
        client = session["client"]
        try:
            client.start()
            client.check_password(password)
            # Success
            session["step"] = "done"
            session_string = client.export_session_string()
            client.stop()
            success = start_userbot(session_string, user_id)
            if success:
                bot.reply_to(message, "✅ Userbot deployed successfully!")
            else:
                bot.reply_to(message, "❌ Failed to start userbot.")
            del login_sessions[user_id]
        except Exception as e:
            bot.reply_to(message, f"❌ 2FA error: {e}")
            client.stop()
            del login_sessions[user_id]

def start_userbot(session_string: str, user_id: int):
    global ub_client, ub_state
    with ub_lock:
        if ub_client is not None:
            logger.warning("Userbot already running. Stopping old one first.")
            stop_userbot()
        try:
            app = pyrogram.Client(
                f"userbot_{user_id}",
                api_id=API_ID,
                api_hash=API_HASH,
                session_string=session_string,
                in_memory=True
            )
            app.start()
            ub_client = app
            if ub_state is None:
                ub_state = UserbotState()
            # Resume workers from saved state
            for cid, text in list(ub_state.spam_msgs.items()):
                if ub_state.spam_flags.get(cid, False):
                    t = threading.Thread(target=spam_worker_ub, args=(app, ub_state, cid, text), daemon=True)
                    ub_state.spam_threads[cid] = t
                    t.start()
            for cid, name in list(ub_state.nc_names.items()):
                if ub_state.nc_flags.get(cid, False):
                    t = threading.Thread(target=nc_worker_ub, args=(app, ub_state, cid, name), daemon=True)
                    ub_state.nc_threads[cid] = t
                    t.start()
            for cid, desc in list(ub_state.dc_descs.items()):
                if ub_state.dc_flags.get(cid, False):
                    t = threading.Thread(target=dc_worker_ub, args=(app, ub_state, cid, desc), daemon=True)
                    ub_state.dc_threads[cid] = t
                    t.start()
            logger.info("✅ Userbot started successfully.")
            save_all_states()
            return True
        except Exception as e:
            logger.error(f"❌ Failed to start userbot: {e}")
            ub_client = None
            return False

def stop_userbot():
    global ub_client, ub_state
    with ub_lock:
        if ub_client is None:
            return False
        try:
            # Stop all workers
            for cid in list(ub_state.spam_flags.keys()):
                ub_state.spam_flags[cid] = False
            for cid in list(ub_state.nc_flags.keys()):
                ub_state.nc_flags[cid] = False
            for cid in list(ub_state.dc_flags.keys()):
                ub_state.dc_flags[cid] = False
            ub_client.stop()
            ub_client = None
            save_all_states()
            logger.info("✅ Userbot stopped.")
            return True
        except Exception as e:
            logger.error(f"❌ Error stopping userbot: {e}")
            return False

def get_ub_status():
    if ub_client is None:
        return "⛔ Not deployed"
    try:
        me = ub_client.get_me()
        return f"✅ Active as @{me.username or me.first_name}"
    except:
        return "⚠️ Deployed but disconnected"

# ==========================================
# 🎨 ATTRACTIVE MENU & HELP
# ==========================================

def build_menu_text(label: str, state: BotState, chat_id: int) -> str:
    def yn(v):
        return "🟢 ON" if v else "🔴 OFF"
    spam_on = state.spam_flags.get(chat_id, False)
    spam_delay = state.spam_delay.get(chat_id, 1.0) * 1000
    nc_on = state.nc_flags.get(chat_id, False)
    nc_delay = state.nc_delay.get(chat_id, 2.0) * 1000
    dc_on = state.dc_flags.get(chat_id, False)
    dc_delay = state.dc_delay.get(chat_id, 3.0) * 1000
    ad = state.auto_delete.get(chat_id, set())
    react = state.auto_react.get(chat_id, "OFF")
    subadmins = len(state.subadmins)
    ub_stat = get_ub_status()

    lines = [
        "╔════════════════════════════════╗",
        f"║   ✨·˚ SID Bot [{label}] ˚·✨   ║",
        "║   💕 your premium assistant 💕  ║",
        "╠════════════════════════════════╣",
        f"║ 🌸 Spam        : {yn(spam_on)}  ║",
        f"║    Delay       : {spam_delay:.0f} ms   ║",
        f"║ 🌷 NC          : {yn(nc_on)}  ║",
        f"║    Delay       : {nc_delay:.0f} ms   ║",
        f"║ 🦋 DC          : {yn(dc_on)}  ║",
        f"║    Delay       : {dc_delay:.0f} ms   ║",
        f"║ 🍓 AutoDelete  : {len(ad)} user(s)   ║",
        f"║ 💖 AutoReact   : {react}  ║",
        f"║ 👥 Subadmins   : {subadmins}   ║",
        "╠════════════════════════════════╣",
        f"║ 🚀 Userbot     : {ub_stat}   ║",
        "╚════════════════════════════════╝",
        "",
        "📌 Quick commands:",
        "  /spam <text>  /nc <name>  /dc <desc>",
        "  /spamoff  /ncoff  /dcoff",
        "  /auto_delete <id>  /react <emoji>",
        "  /addsubadmin @user  /removesubadmin",
        "  /host_ub  (deploy userbot)",
        "  /stop_ub  (stop userbot)",
        "  /ubspam /ubnc /ubdc  (userbot version)",
        "",
        "📋 Additional menus:",
        "  /menu1  → 👑 Admin & Mute controls",
        "  /menu2  → ⚔️ Raid Engine (original)",
        "  /menu3  → 💣 Spam Engine & Text Manager",
    ]
    return "\n".join(lines)

# ==========================================
# 📨 BOT HANDLERS
# ==========================================

def register_handlers(bot: telebot.TeleBot, state: BotState, label: str):
    def admin_only(message):
        uid = message.from_user.id if message.from_user else None
        return uid is not None and state.is_admin(uid)

    def owner_only(message):
        uid = message.from_user.id if message.from_user else None
        return uid is not None and uid in OWNER_IDS

    def save():
        save_all_states()

    # --------------------------------------
    # 🏠 MAIN MENU (no inline buttons)
    # --------------------------------------
    @bot.message_handler(commands=["start", "menu"])
    def send_menu(message):
        if not admin_only(message):
            return
        chat_id = message.chat.id
        text = build_menu_text(label, state, chat_id)
        bot.send_message(chat_id, text, parse_mode=None)

    # --------------------------------------
    # 📋 EXTRA MENUS (from second script)
    # --------------------------------------
    @bot.message_handler(commands=["menu1"])
    def cmd_menu1(message):
        if not admin_only(message):
            return
        menu = (
    "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
    "   👑  𝗔𝗗𝗠𝗜𝗡  •  🔇  𝗠𝗨𝗧𝗘  •  🧹  𝗚𝗥𝗢𝗨𝗣\n"
    "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
    "\n"
    "【 👑 𝗔𝗗𝗠𝗜𝗡 𝗖𝗢𝗡𝗧𝗥𝗢𝗟 】\n"
    "  ✦ .admins      → Admin list dekhna\n"
    "  ✦ .addadmin    → Admin add karo\n"
    "  ✦ .deladmin    → Admin hatao\n"
    "\n"
    "【 🔇 𝗠𝗨𝗧𝗘 𝗦𝗬𝗦𝗧𝗘𝗠 】\n"
    "  ✦ .mute        → User mute karo\n"
    "  ✦ .unmute      → User unmute karo\n"
    "  ✦ .gmute       → Global mute\n"
    "  ✦ .gunmute     → Global unmute\n"
    "  ✦ .mutelist    → Muted list\n"
    "\n"
    "【 🧹 𝗚𝗥𝗢𝗨𝗣 𝗠𝗢𝗗 】\n"
    "  ✦ .lock / .unlock   → Group lock\n"
    "  ✦ .purge             → Messages saaf\n"
    "  ✦ .throw             → User throw\n"
    "  ✦ .addbots           → Bots add karo\n"
    "\n"
    "【 ⚖️ 𝗗𝗜𝗦𝗖𝗜𝗣𝗟𝗜𝗡𝗘 】\n"
    "  ✦ .ban / .unban      → Ban system\n"
    "  ✦ .kick              → Kick user\n"
    "  ✦ .promote / .demote → Admin rights\n"
    "  ✦ .warn              → User warn karo\n"
    "  ✦ .warnlist          → Warn list\n"
    "  ✦ .clearwarn         → Warn clear\n"
    "  ✦ .pin / .unpin      → Pin message\n"
    "  ✦ .groupinfo         → Group info\n"
    "  ✦ .membercount       → Members count\n"
    "  ✦ .invitelink        → Invite link\n"
    "\n"
    "📌  .menu → Main menu wapas"
        )
        bot.reply_to(message, menu)

    @bot.message_handler(commands=["menu2"])
    def cmd_menu2(message):
        if not admin_only(message):
            return
        menu = (
    "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
    "      ⚔️  𝗥𝗔𝗜𝗗  𝗘𝗡𝗚𝗜𝗡𝗘  (𝗢𝗥𝗜𝗚𝗜𝗡𝗔𝗟)\n"
    "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
    "\n"
    "  💡 𝗨𝘀𝗲: .cmdname @username\n"
    "  🛑 𝗦𝘁𝗼𝗽: .s + cmdname\n"
    "\n"
    "┌────────────────────────────────┐\n"
    "│  𝗥𝗔𝗜𝗗   │  𝗦𝗧𝗔𝗥𝗧      │  𝗦𝗧𝗢𝗣   │\n"
    "├────────────────────────────────┤\n"
    "│  💬 Reply │  .reply     │  .sreply │\n"
    "│  🤣 RR    │  .rr        │  .srr    │\n"
    "│  🚩 Flag  │  .flag      │  .sflag  │\n"
    "│  💗 Heart │  .hrr       │  .shrr   │\n"
    "│  😈 God   │  .replygod  │  .sgod   │\n"
    "└────────────────────────────────┘\n"
    "\n"
    "【 🎯 𝗟𝗜𝗠𝗜𝗧𝗘𝗗 𝗥𝗔𝗜𝗗 】\n"
    "  ✦ .replysid <text> <count>\n"
    "  ✦ .sstop  → Limited raid stop\n"
    "\n"
    "📌  .menu6 → 🔥 NEW 1000+ Fighting Raids"
        )
        bot.reply_to(message, menu)

    @bot.message_handler(commands=["menu3"])
    def cmd_menu3(message):
        if not admin_only(message):
            return
        menu = (
    "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
    "      💣  𝗦𝗣𝗔𝗠  𝗘𝗡𝗚𝗜𝗡𝗘  &  📝  𝗧𝗘𝗫𝗧\n"
    "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
    "\n"
    "【 💣 𝗦𝗣𝗔𝗠 𝗦𝗬𝗦𝗧𝗘𝗠 】\n"
    "  ✦ .spray          → Spam karo\n"
    "  ✦ .dspray         → Delete & spam\n"
    "  ✦ .tspray <n> <t> → Timed spray\n"
    "  ✦ .rspray         → Random text spam\n"
    "  ✦ .multispray     → Multi line spam\n"
    "  ✦ .countspray <n> → N baar spray\n"
    "  ✦ .spraydelay <s> → Speed set karo\n"
    "\n"
    "【 📝 𝗧𝗘𝗫𝗧 𝗠𝗔𝗡𝗔𝗚𝗘𝗥 】\n"
    "  ✦ .addtext  <text>  → Text save karo\n"
    "  ✦ .listtexts        → Saved texts\n"
    "  ✦ .edittext <n> <t> → Text edit karo\n"
    "  ✦ .deltext  <n>     → Text delete\n"
    "  ✦ .cleartext        → Sab clear\n"
    "\n"
    "【 ⚡ 𝗙𝗔𝗦𝗧 𝗚𝗖 𝗘𝗡𝗚𝗜𝗡𝗘 】\n"
    "  ✦ .fastgc set {emoji} <template>\n"
    "  ✦ .fastgc stop  → FastGC band karo\n"
    "\n"
    "📌  .menu → Main menu wapas"
        )
        bot.reply_to(message, menu)

    # --------------------------------------
    # 📢 SPAM (bot version)
    # --------------------------------------
    @bot.message_handler(commands=["spam"])
    def handle_spam_cmd(message):
        if not admin_only(message): return
        chat_id = message.chat.id
        text = normalize(message.text)
        if text.lower() == "spam off":
            state.spam_flags[chat_id] = False
            state.spam_msgs.pop(chat_id, None)
            save()
            bot.reply_to(message, "🌸 Spam stopped! 💤")
            return
        if text.lower().startswith("spam delay"):
            parts = text.split()
            if len(parts) >= 3 and parts[2].isdigit():
                state.spam_delay[chat_id] = int(parts[2]) / 1000.0
                save()
                bot.reply_to(message, f"✨ Spam delay: {parts[2]}ms")
            else:
                bot.reply_to(message, "Usage: /spam delay <ms>")
            return
        parts = text.split(" ", 1)
        if len(parts) < 2 or not parts[1].strip():
            bot.reply_to(message, "Usage: /spam <message>")
            return
        spam_msg = parts[1].strip()
        state.spam_flags[chat_id] = False
        time.sleep(0.1)
        state.spam_flags[chat_id] = True
        state.spam_msgs[chat_id] = spam_msg
        save()
        t = threading.Thread(target=spam_worker_bot, args=(bot, state, chat_id, spam_msg), daemon=True)
        state.spam_threads[chat_id] = t
        t.start()
        bot.reply_to(message, f"💕 Spamming: \"{spam_msg}\" | /spamoff to stop")

    @bot.message_handler(commands=["spamoff"])
    def spam_off_cmd(message):
        if not admin_only(message): return
        state.spam_flags[message.chat.id] = False
        state.spam_msgs.pop(message.chat.id, None)
        save()
        bot.reply_to(message, "🌸 Spam stopped! 💤")

    # --------------------------------------
    # 🏷️ NC (bot version)
    # --------------------------------------
    @bot.message_handler(commands=["nc"])
    def handle_nc_cmd(message):
        if not admin_only(message): return
        if message.chat.type == "private":
            bot.reply_to(message, "NC only works in groups!")
            return
        chat_id = message.chat.id
        text = normalize(message.text)
        if text.lower() == "nc off":
            state.nc_flags[chat_id] = False
            state.nc_names.pop(chat_id, None)
            save()
            bot.reply_to(message, "🌸 NC stopped! 💤")
            return
        if text.lower().startswith("nc delay"):
            parts = text.split()
            if len(parts) >= 3 and parts[2].isdigit():
                state.nc_delay[chat_id] = int(parts[2]) / 1000.0
                save()
                bot.reply_to(message, f"✨ NC delay: {parts[2]}ms")
            else:
                bot.reply_to(message, "Usage: /nc delay <ms>")
            return
        parts = text.split(" ", 1)
        if len(parts) < 2 or not parts[1].strip():
            bot.reply_to(message, "Usage: /nc <name>")
            return
        base_name = parts[1].strip()
        state.nc_flags[chat_id] = False
        time.sleep(0.1)
        state.nc_flags[chat_id] = True
        state.nc_names[chat_id] = base_name
        save()
        t = threading.Thread(target=nc_worker_bot, args=(bot, state, chat_id, base_name), daemon=True)
        state.nc_threads[chat_id] = t
        t.start()
        bot.reply_to(message, f"💖 NC started: '{base_name}' | /ncoff to stop")

    @bot.message_handler(commands=["ncoff"])
    def nc_off_cmd(message):
        if not admin_only(message): return
        state.nc_flags[message.chat.id] = False
        state.nc_names.pop(message.chat.id, None)
        save()
        bot.reply_to(message, "🌸 NC stopped! 💤")

    # --------------------------------------
    # 📝 DC (bot version)
    # --------------------------------------
    @bot.message_handler(commands=["dc"])
    def handle_dc_cmd(message):
        if not admin_only(message): return
        if message.chat.type == "private":
            bot.reply_to(message, "DC only works in groups!")
            return
        chat_id = message.chat.id
        text = normalize(message.text)
        if text.lower() == "dc off":
            state.dc_flags[chat_id] = False
            state.dc_descs.pop(chat_id, None)
            save()
            bot.reply_to(message, "🌸 DC stopped! 💤")
            return
        if text.lower().startswith("dc delay"):
            parts = text.split()
            if len(parts) >= 3 and parts[2].isdigit():
                state.dc_delay[chat_id] = int(parts[2]) / 1000.0
                save()
                bot.reply_to(message, f"✨ DC delay: {parts[2]}ms")
            else:
                bot.reply_to(message, "Usage: /dc delay <ms>")
            return
        parts = text.split(" ", 1)
        if len(parts) < 2 or not parts[1].strip():
            bot.reply_to(message, "Usage: /dc <description>")
            return
        base_desc = parts[1].strip()
        state.dc_flags[chat_id] = False
        time.sleep(0.1)
        state.dc_flags[chat_id] = True
        state.dc_descs[chat_id] = base_desc
        save()
        t = threading.Thread(target=dc_worker_bot, args=(bot, state, chat_id, base_desc), daemon=True)
        state.dc_threads[chat_id] = t
        t.start()
        bot.reply_to(message, "💖 DC started | /dcoff to stop")

    @bot.message_handler(commands=["dcoff"])
    def dc_off_cmd(message):
        if not admin_only(message): return
        state.dc_flags[message.chat.id] = False
        state.dc_descs.pop(message.chat.id, None)
        save()
        bot.reply_to(message, "🌸 DC stopped! 💤")

    # --------------------------------------
    # 🗑️ AUTO DELETE
    # --------------------------------------
    @bot.message_handler(commands=["auto_delete", "autodelete"])
    def handle_auto_delete(message):
        if not admin_only(message): return
        if message.chat.type == "private":
            bot.reply_to(message, "Auto delete only works in groups!")
            return
        chat_id = message.chat.id
        parts = message.text.strip().split(None, 1)
        arg = parts[1].strip() if len(parts) > 1 else ""
        if arg.lower() == "off" or arg == "":
            state.auto_delete.pop(chat_id, None)
            save()
            bot.reply_to(message, "🌸 Auto delete disabled! 💤")
            return
        try:
            target_id = int(arg)
            state.auto_delete.setdefault(chat_id, set()).add(target_id)
            save()
            bot.reply_to(message, f"✨ Auto delete ON for {target_id}")
        except ValueError:
            bot.reply_to(message, "Usage: /auto_delete <user_id>")

    # --------------------------------------
    # ❤️ AUTO REACT
    # --------------------------------------
    @bot.message_handler(commands=["react"])
    def handle_react(message):
        if not admin_only(message): return
        parts = message.text.strip().split(None, 1)
        if len(parts) < 2 or not parts[1].strip():
            bot.reply_to(message, "Usage: /react <emoji>")
            return
        state.auto_react[message.chat.id] = parts[1].strip()
        save()
        bot.reply_to(message, f"✨ Auto react: {parts[1].strip()}")

    @bot.message_handler(commands=["stopreact"])
    def stop_react(message):
        if not admin_only(message): return
        state.auto_react.pop(message.chat.id, None)
        save()
        bot.reply_to(message, "🌷 Auto react off 💤")

    # --------------------------------------
    # 👥 SUBADMIN MANAGEMENT
    # --------------------------------------
    @bot.message_handler(commands=["addsubadmin"])
    def add_subadmin(message):
        if message.from_user.id not in OWNER_IDS: return
        parts = message.text.split(None, 1)
        if len(parts) < 2:
            bot.reply_to(message, "Usage: /addsubadmin @username or <user_id>")
            return
        target = parts[1].strip().lstrip("@")
        try:
            uid = int(target)
            state.subadmins.add(uid)
            save()
            bot.reply_to(message, f"✨ {uid} added as subadmin")
        except ValueError:
            try:
                member = bot.get_chat_member(message.chat.id, target)
                state.subadmins.add(member.user.id)
                save()
                bot.reply_to(message, f"✨ @{target} added as subadmin")
            except Exception:
                bot.reply_to(message, f"Could not find '{target}'. Use numeric ID.")

    @bot.message_handler(commands=["removesubadmin"])
    def remove_subadmin(message):
        if message.from_user.id not in OWNER_IDS: return
        parts = message.text.split(None, 1)
        if len(parts) < 2:
            bot.reply_to(message, "Usage: /removesubadmin @username or <user_id>")
            return
        target = parts[1].strip().lstrip("@")
        try:
            uid = int(target)
            state.subadmins.discard(uid)
            save()
            bot.reply_to(message, f"🌷 {uid} removed")
        except ValueError:
            try:
                member = bot.get_chat_member(message.chat.id, target)
                state.subadmins.discard(member.user.id)
                save()
                bot.reply_to(message, f"🌷 @{target} removed")
            except Exception:
                bot.reply_to(message, f"Could not find '{target}'.")

    @bot.message_handler(commands=["listsubadmin"])
    def list_subadmins(message):
        if not admin_only(message): return
        if not state.subadmins:
            bot.reply_to(message, "No subadmins yet.")
            return
        bot.reply_to(message, "✨ Subadmins:\n" + "\n".join(f"  ✦ {uid}" for uid in state.subadmins))

    # --------------------------------------
    # 🚀 USERBOT DEPLOY / UNDEPLOY (via commands)
    # --------------------------------------
    @bot.message_handler(commands=["host_ub", "deploy_ub"])
    def host_ub_command(message):
        if not admin_only(message): return
        start_userbot_login(message.from_user.id, bot, message)

    @bot.message_handler(commands=["stop_ub"])
    def stop_ub_command(message):
        if not admin_only(message): return
        if ub_client is None:
            bot.reply_to(message, "⛔ Userbot is not running.")
            return
        bot.reply_to(message, "⏳ Stopping userbot...")
        success = stop_userbot()
        if success:
            bot.reply_to(message, "✅ Userbot stopped.")
        else:
            bot.reply_to(message, "❌ Error stopping userbot.")

    @bot.message_handler(commands=["ubstatus"])
    def ub_status_cmd(message):
        if not admin_only(message): return
        stat = get_ub_status()
        bot.reply_to(message, f"🚀 Userbot status: {stat}")

    # --------------------------------------
    # 📢 USERBOT SPAM / NC / DC
    # --------------------------------------
    @bot.message_handler(commands=["ubspam"])
    def handle_ubspam(message):
        if not admin_only(message): return
        if ub_client is None:
            bot.reply_to(message, "⛔ Userbot not deployed. Use /host_ub first.")
            return
        chat_id = message.chat.id
        text = normalize(message.text)
        if text.lower() == "ubspam off":
            ub_state.spam_flags[chat_id] = False
            ub_state.spam_msgs.pop(chat_id, None)
            save_all_states()
            bot.reply_to(message, "🌸 Userbot spam stopped! 💤")
            return
        if text.lower().startswith("ubspam delay"):
            parts = text.split()
            if len(parts) >= 3 and parts[2].isdigit():
                ub_state.spam_delay[chat_id] = int(parts[2]) / 1000.0
                save_all_states()
                bot.reply_to(message, f"✨ Userbot spam delay: {parts[2]}ms")
            else:
                bot.reply_to(message, "Usage: /ubspam delay <ms>")
            return
        parts = text.split(" ", 1)
        if len(parts) < 2 or not parts[1].strip():
            bot.reply_to(message, "Usage: /ubspam <message>")
            return
        spam_msg = parts[1].strip()
        ub_state.spam_flags[chat_id] = False
        time.sleep(0.1)
        ub_state.spam_flags[chat_id] = True
        ub_state.spam_msgs[chat_id] = spam_msg
        save_all_states()
        t = threading.Thread(target=spam_worker_ub, args=(ub_client, ub_state, chat_id, spam_msg), daemon=True)
        ub_state.spam_threads[chat_id] = t
        t.start()
        bot.reply_to(message, f"💕 Userbot spamming: \"{spam_msg}\" | /ubspam off to stop")

    @bot.message_handler(commands=["ubnc"])
    def handle_ubnc(message):
        if not admin_only(message): return
        if ub_client is None:
            bot.reply_to(message, "⛔ Userbot not deployed.")
            return
        if message.chat.type == "private":
            bot.reply_to(message, "NC only works in groups!")
            return
        chat_id = message.chat.id
        text = normalize(message.text)
        if text.lower() == "ubnc off":
            ub_state.nc_flags[chat_id] = False
            ub_state.nc_names.pop(chat_id, None)
            save_all_states()
            bot.reply_to(message, "🌸 Userbot NC stopped! 💤")
            return
        if text.lower().startswith("ubnc delay"):
            parts = text.split()
            if len(parts) >= 3 and parts[2].isdigit():
                ub_state.nc_delay[chat_id] = int(parts[2]) / 1000.0
                save_all_states()
                bot.reply_to(message, f"✨ Userbot NC delay: {parts[2]}ms")
            else:
                bot.reply_to(message, "Usage: /ubnc delay <ms>")
            return
        parts = text.split(" ", 1)
        if len(parts) < 2 or not parts[1].strip():
            bot.reply_to(message, "Usage: /ubnc <name>")
            return
        base_name = parts[1].strip()
        ub_state.nc_flags[chat_id] = False
        time.sleep(0.1)
        ub_state.nc_flags[chat_id] = True
        ub_state.nc_names[chat_id] = base_name
        save_all_states()
        t = threading.Thread(target=nc_worker_ub, args=(ub_client, ub_state, chat_id, base_name), daemon=True)
        ub_state.nc_threads[chat_id] = t
        t.start()
        bot.reply_to(message, f"💖 Userbot NC started: '{base_name}' | /ubnc off to stop")

    @bot.message_handler(commands=["ubdc"])
    def handle_ubdc(message):
        if not admin_only(message): return
        if ub_client is None:
            bot.reply_to(message, "⛔ Userbot not deployed.")
            return
        if message.chat.type == "private":
            bot.reply_to(message, "DC only works in groups!")
            return
        chat_id = message.chat.id
        text = normalize(message.text)
        if text.lower() == "ubdc off":
            ub_state.dc_flags[chat_id] = False
            ub_state.dc_descs.pop(chat_id, None)
            save_all_states()
            bot.reply_to(message, "🌸 Userbot DC stopped! 💤")
            return
        if text.lower().startswith("ubdc delay"):
            parts = text.split()
            if len(parts) >= 3 and parts[2].isdigit():
                ub_state.dc_delay[chat_id] = int(parts[2]) / 1000.0
                save_all_states()
                bot.reply_to(message, f"✨ Userbot DC delay: {parts[2]}ms")
            else:
                bot.reply_to(message, "Usage: /ubdc delay <ms>")
            return
        parts = text.split(" ", 1)
        if len(parts) < 2 or not parts[1].strip():
            bot.reply_to(message, "Usage: /ubdc <description>")
            return
        base_desc = parts[1].strip()
        ub_state.dc_flags[chat_id] = False
        time.sleep(0.1)
        ub_state.dc_flags[chat_id] = True
        ub_state.dc_descs[chat_id] = base_desc
        save_all_states()
        t = threading.Thread(target=dc_worker_ub, args=(ub_client, ub_state, chat_id, base_desc), daemon=True)
        ub_state.dc_threads[chat_id] = t
        t.start()
        bot.reply_to(message, "💖 Userbot DC started | /ubdc off to stop")

    # --------------------------------------
    # 🔄 STATUS COMMAND (legacy) - no parse_mode
    # --------------------------------------
    @bot.message_handler(commands=["status"])
    def show_status(message):
        if not admin_only(message): return
        chat_id = message.chat.id
        def yn(v): return "ON" if v else "OFF"
        ad = state.auto_delete.get(chat_id, set())
        react = state.auto_react.get(chat_id)
        ub_stat = get_ub_status()
        bot.reply_to(message,
            f"🌸 [{label}] Status\n"
            "━━━━━━━━━━━━━━━\n"
            f"Spam       : {yn(state.spam_flags.get(chat_id))} | {state.spam_delay.get(chat_id,1.0)*1000:.0f}ms\n"
            f"NC         : {yn(state.nc_flags.get(chat_id))} | {state.nc_delay.get(chat_id,2.0)*1000:.0f}ms\n"
            f"DC         : {yn(state.dc_flags.get(chat_id))} | {state.dc_delay.get(chat_id,3.0)*1000:.0f}ms\n"
            f"AutoDelete : {str(len(ad))+' user(s)' if ad else 'OFF'}\n"
            f"AutoReact  : {react if react else 'OFF'}\n"
            f"Subadmins  : {len(state.subadmins)}\n"
            f"Userbot    : {ub_stat}"
        )

    # --------------------------------------
    # 📨 MESSAGE HANDLER (auto delete & react)
    # --------------------------------------
    @bot.message_handler(func=lambda m: True, content_types=["text","photo","sticker","video","audio","document","voice","animation"])
    def on_any_message(message):
        chat_id = message.chat.id
        user_id = message.from_user.id if message.from_user else None
        if user_id and chat_id in state.auto_delete and user_id in state.auto_delete[chat_id]:
            try: bot.delete_message(chat_id, message.message_id)
            except Exception: pass
            return
        emoji = state.auto_react.get(chat_id)
        if emoji:
            try: bot.set_message_reaction(chat_id, message.message_id, [telebot.types.ReactionTypeEmoji(emoji)])
            except Exception: pass

    # --------------------------------------
    # 🚫 Cancel login
    # --------------------------------------
    @bot.message_handler(commands=["cancel"])
    def cancel_login_cmd(message):
        if not admin_only(message): return
        cancel_login(message.from_user.id, bot, message)

    # Handle text messages for login steps (only if in login session)
    @bot.message_handler(func=lambda m: m.from_user.id in login_sessions and m.text and not m.text.startswith("/"))
    def login_text_handler(message):
        user_id = message.from_user.id
        if user_id in login_sessions:
            process_login_step(user_id, message.text, bot, message)

# ==========================================
# 🚀 BOT LAUNCHER
# ==========================================

def start_bot(token: str, label: str):
    logger.info(f"Checking credentials for [{label}] ...")
    bot = telebot.TeleBot(token, parse_mode=None)
    
    try:
        me = bot.get_me()
        logger.info(f"✅ [{label}] SUCCESS: Connected as @{me.username}")
    except telebot.apihelper.ApiTelegramException as e:
        logger.error(f"❌ [{label}] FAILED: Token invalid! {e}")
        return
    except Exception as e:
        logger.error(f"❌ [{label}] FAILED: Connection error! {e}")
        return

    state = BotState()
    _all_states[label] = state
    register_handlers(bot, state, label)
    
    # Resume bot state from file (separate from userbot)
    load_all_states()  # loads userbot too
    # Resume bot workers
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE) as f:
                data = json.load(f)
            if label in data:
                d = data[label]
                state.subadmins = set(d.get("subadmins", []))
                state.auto_delete = {int(cid): set(uids) for cid, uids in d.get("auto_delete", {}).items()}
                state.auto_react = {int(k): v for k, v in d.get("auto_react", {}).items() if k.lstrip("-").isdigit()}
                # Spam
                for cid_str, info in d.get("spam", {}).items():
                    if info.get("active") and info.get("msg"):
                        cid = int(cid_str)
                        state.spam_delay[cid] = info.get("delay", 1.0)
                        state.spam_flags[cid] = True
                        state.spam_msgs[cid] = info["msg"]
                        t = threading.Thread(target=spam_worker_bot, args=(bot, state, cid, info["msg"]), daemon=True)
                        state.spam_threads[cid] = t
                        t.start()
                # NC
                for cid_str, info in d.get("nc", {}).items():
                    if info.get("active") and info.get("name"):
                        cid = int(cid_str)
                        state.nc_delay[cid] = info.get("delay", 2.0)
                        state.nc_flags[cid] = True
                        state.nc_names[cid] = info["name"]
                        t = threading.Thread(target=nc_worker_bot, args=(bot, state, cid, info["name"]), daemon=True)
                        state.nc_threads[cid] = t
                        t.start()
                # DC
                for cid_str, info in d.get("dc", {}).items():
                    if info.get("active") and info.get("desc"):
                        cid = int(cid_str)
                        state.dc_delay[cid] = info.get("delay", 3.0)
                        state.dc_flags[cid] = True
                        state.dc_descs[cid] = info["desc"]
                        t = threading.Thread(target=dc_worker_bot, args=(bot, state, cid, info["desc"]), daemon=True)
                        state.dc_threads[cid] = t
                        t.start()
        except Exception as e:
            logger.warning(f"Could not resume state for {label}: {e}")

    while True:
        try:
            bot.infinity_polling(timeout=15, long_polling_timeout=10)
        except Exception as e:
            logger.warning(f"⚠️ [{label}] disconnected: {e} — retrying in 5s")
            time.sleep(5)

# ==========================================
# 🏁 MAIN
# ==========================================

if __name__ == "__main__":
    print(f"🌸 SID Premium Multi‑Bot with Userbot Hosting | Owners: {', '.join(str(x) for x in OWNER_IDS)} | Bots: {len(BOT_TOKENS)}")

    # Load existing state (userbot will be restored if it was running)
    load_all_states()
    # If userbot state exists, we don't auto-start because we need session string.
    # User must host again.

    for idx, token in enumerate(BOT_TOKENS, start=1):
        t = threading.Thread(target=start_bot, args=(token, f"Bot{idx}"), daemon=True)
        t.start()
        time.sleep(0.5)

    print("\n✨ SID Bot is alive! Send /menu to any bot to see the premium dashboard.\n")
    try:
        while True:
            time.sleep(60)
    except KeyboardInterrupt:
        print("\n🌸 Goodbye~")
        if ub_client:
            ub_client.stop()
