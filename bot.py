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
# 📋 TEXT LISTS (from second script)
# ==========================================

reply_list = [
    "𝐊ʏᴀ 𝐑ᴇ 𝐑ᴀɴᴅɪᴋᴇ 𝐂ᴏᴏʟ 𝐁ᴀɴᴇɢᴀ 𝐓ᴜ 𝐂ʜᴀʟ 𝐀ʙ 𝐂ʜᴜᴅ 𝐀ᴘɴᴇ 𝐁ᴀᴀᴘ 𝗦𝗶𝗱 𝐒ᴇ - 🦢💘",
    "𝐊ɪ 𝐌ᴀᴀ 𝐌ᴀʀʀ 𝐆ᴀʏɪ 𝐘ᴀᴀʀ - 𝐉ᴀɪ 𝗦𝗶𝗱 ! 🌙",
    "acha beta 😂🔥👊🏻 ? coi na me toh HATER codunga 😹💔🔥😆👊🏻💥",
    "chudke bhaga kaise 😂💥🤣🤘🏻",
    "ne toh 𝗦𝗶𝗱 ka lun muh me lelia 😂🙏🏻😂🙏🏻",
    "try maa सूर्य☀ nikalte hi pel du 😹🔥💔",
    "mkl lun te vaj 😂✊🏻💦",
    "𝗧ᴍᴋ𝗕 pe 𝗦𝗶𝗱 ka hamla 😂⚔🔥💥",
    "𝐂ʜʟ 𝐇ᴀʀᴍᴢᴀᴅ𝐈 𝐊ᴇ लड़के 💛🤍🩵",
    "oi 𝐓ᴇʀɪ 𝐌‌ᴀᴀ गुलाम ₰🖤",
    "chl rndyce chud ke dikha 😂💥🤣🔥",
    "𝐊ɪ 𝐌ᴀᴀ 𝐌ᴀʀʀ 𝐆ᴀʏɪ naacho 💃🏻💃🏻🕺🏻🎶😂😆💞🔥 !",
    "tera baap bass 𝗦𝗶𝗱 hai 😂🎀",
    "try maa hagte hue paad mari -#😹🔥🥀",
    "𝐓ᴇʀɪ 𝐌ᴜᴍᴍʏ 𝐂ʜᴏᴅ 𝐃ɪ 𝗦𝗶𝗱 𝐍ᴇ 𝐁ᴡᴀʜᴀʜᴀʜᴀ ⚜",
]

reply_texts = [
    "⋆｡ﾟ☁︎｡𝐂ʏᴜ 𝐑ᴇ मदरचोद 𝗦𝗶𝗱 बाप के सामने 𝐅ʏᴛᴇʀ 𝐁ᴀɴᴇɢᴀ ⋆𓂃 ོ☼𓂃 😂🔥",
    "नहीं नहीं तेरी मां को 𝐒ɪʀғ 𝗦𝗶𝗱 बाप चोद सकता है ִֶָ𓂃 ࣪ ִֶָ👑་༘࿐ sᴀᴍᴊʜᴀ ʀᴀɴᴅɪᴋᴇ ???",
    "तेरी मां का 𝐒ᴛʏʟɪsʜ भोसड़ा 😱",
    "𝑻𝒆𝒓𝒚 𝒎𝒂𝒂 𝒓𝒂𝒏𝒅𝒂𝒍 𝒉 𝒃𝒂𝒔 𝒃𝒂𝒂𝒕 𝒌𝒉𝒂𝒕𝒂𝒎 😡🔥",
    "सोच तेरी बहन को 𝗦𝗶𝗱 बाप का गुलाम चोद रहा 😎🔥",
    "Hello hello?? Oxygen aarahi है? रण्डी पुत्र 🧘🏻",
    "Shut up रंडीके वरना दुनिया यही बोलेगी तेरी बहन 𝗦𝗶𝗱 /~👑 बाप से सही chudi 🥵🔥",
    "ᴛᴜ ᴏʀ ᴛᴇʀɪ ᴍᴀᴀ ᴅᴏɴᴏ 𝗦𝗶𝗱 बाप के ʟɴᴅ sᴇ ᴋᴀʙʜɪ ᴜᴛʜ ɴʜɪ ᴘᴀʏᴇ 😂🔥",
]

fun_texts = [
    "तेरे मां के दूदू के बीच मेरा lund fas gaya oops 🤪（ ͜.🍆 ͜.）",
    "𝐓ᴇʀʏ 𝐁ʜᴇ𝐍 𝐊ᴇ ( ͜. ㅅ ͜. )🥛 ʏᴜᴍᴍʏ ",
    "𓂃☁︎ 𓂃𝐒ɪᴅᴇ 𝐇ᴀᴛ 𝐆ᴜʟᴀᴍ 𝐓ᴇʀʏ 𝐌ᴀᴀ 𝐊ᴏ 𝐂ʜᴏᴅɴᴇ  मेरी रेलगाड़ी आ रही .-'🚂-'.ᯓᡣ𐭩______ 𓂃☁︎ 𓂃",
    "⋆⭒˚.⋆🔭 𝐒ʜᴜᴛ 𝐔ᴘ 𝐑ᴀɴᴅɪᴋᴇ 𝐓ᴇʀɪ 𝐌ᴀᴀ 𝐊ɪ 𝐂ʜᴜᴅᴀɪ 𝐄ɴᴊᴏʏ 𝐊ʀ 𝐑ᴀʜᴀ 𝐓ᴇʟᴇ𝐒ᴄᴏᴘᴇ 𝐒ᴇ⋆⭒˚.⋆🔭",
]

flag_texts = [
    " ོ༘₊⁺🇮🇳 ₊⁺⋆.˚ 𝐓ᴇʀɪ 𝐌ᴀᴀ 𝐊ᴇ 𝐒ᴀᴛʜ 𝗦𝗶𝗱 𝐁ᴀᴀᴘ 𝐀ᴜʀ 𝐈ɴᴅɪᴀ 𝐖ᴀʟᴇ 𝐁ʜɪ 𝐂ʜɪʟʟ 𝐊ᴀʀ 𝐑ʜᴇ ོ༘₊⁺🇮🇳 ₊⁺⋆.˚",
    " ོ༘₊⁺🇯🇵 ₊⁺⋆.˚ 𝐓ᴇʀɪ 𝐌ᴀᴀ 𝐊ᴇ 𝐒ᴀᴛʜ 𝗦𝗶𝗱 𝐁ᴀᴀᴘ 𝐀ᴜʀ 𝐉ᴀᴘᴀɴ 𝐖ᴀʟᴇ 𝐁ʜɪ 𝐂ʜɪʟʟ 𝐊ᴀʀ 𝐑ʜᴇ ོ༘₊⁺🇯🇵 ₊⁺⋆.˚",
    " ₊⁺🇺🇸 ₊⁺⋆.˚ 𝐓ᴇʀɪ 𝐌ᴀᴀ 𝐊ᴇ 𝐒ᴀᴛʜ 𝗦𝗶𝗱 𝐁ᴀᴀᴘ 𝐀ᴜʀ 𝐔𝐒𝐀 𝐖ᴀʟᴇ 𝐁ʜɪ 𝐂ʜɪʟʟ 𝐊ᴀʀ 𝐑ʜᴇ ོ༘₊⁺🇺🇸 ₊⁺⋆.˚",
    " ོ༘₊⁺🇬🇧 ₊⁺⋆.˚ 𝐓ᴇʀɪ 𝐌ᴀᴀ 𝐊ᴇ 𝐒ᴀᴛʜ 𝗦𝗶𝗱 𝐁ᴀᴀᴘ 𝐀ᴜʀ 𝐔𝐊 𝐖ᴀʟᴇ 𝐁ʜɪ 𝐂ʜɪʟʟ 𝐊ᴀʀ 𝐑ʜᴇ ོ༘₊⁺🇬🇧 ₊⁺⋆.˚",
    " ོ༘₊⁺🇰🇷 ₊⁺⋆.˚𝐓ᴇʀɪ 𝐌ᴀᴀ 𝐊ᴇ 𝐒ᴀᴛʜ 𝗦𝗶𝗱 𝐁ᴀᴀᴘ 𝐀ᴜʀ 𝐊ᴏʀᴇᴀ 𝐖ᴀʟᴇ 𝐁ʜɪ 𝐂ʜɪʟʟ 𝐊ᴀʀ 𝐑ʜᴇ ོ༘₊⁺🇰🇷 ₊⁺⋆.˚",
    " ོ༘₊⁺🇩🇪 ₊⁺⋆.˚ 𝐓ᴇʀɪ 𝐌ᴀᴀ 𝐊ᴇ 𝐒ᴀᴛʜ 𝗦𝗶𝗱 𝐁ᴀᴀᴘ 𝐀ᴜʀ 𝐆ᴇʀᴍᴀɴʏ 𝐖ᴀʟᴇ 𝐁ʜɪ 𝐂ʜɪʟʟ 𝐊ᴀʀ 𝐑ʜᴇ ོ༘₊⁺🇩🇪 ₊⁺⋆.˚",
]

heart_replies = [
    "𓂃˖˳·˖ ִֶָ ⋆❤️͙⋆ ִֶָ˖·˳˖𓂃 ִֶָ⁀➴༯ sꪶꪖꪜꫀ ִֶָ. ..𓂃 ࣪ ִֶָ🌈་༘࿐ 𝗟𝗡𝗗 𝗖𝗛𝗢𝗢𝗦 -/- ⋆˚❤️ ݁˖⭑.ᐟ",
    "𓂃˖˳·˖ ִֶָ ⋆🧡͙⋆ ִֶָ˖·˳˖𓂃 ִֶָ⁀➴༯ sꪶꪖꪜꫀ ִֶָ. ..𓂃 ࣪ ִֶָ🌈་༘࿐ 𝗟𝗡𝗗 𝗖𝗛𝗢𝗢𝗦 -/- ⋆˚🧡 ݁˖⭑.ᐟ",
    "𓂃˖˳·˖ ִֶָ ⋆💛͙⋆ ִֶָ˖·˳˖𓂃 ִֶָ⁀➴༯ sꪶꪖꪜꫀ ִֶָ. ..𓂃 ࣪ ִֶָ🌈་༘࿐ 𝗟𝗡𝗗 𝗖𝗛𝗢𝗢𝗦 -/- ⋆˚💛 ݁˖⭑.ᐟ",
    "𓂃˖˳·˖ ִֶָ ⋆💚͙⋆ ִֶָ˖·˳˖𓂃 ִֶָ⁀➴༯ sꪶꪖꪜꫀ ִֶָ. ..𓂃 ࣪ ִֶָ🌈་༘࿐ 𝗟𝗡𝗗 𝗖𝗛𝗢𝗢𝗦 -/- ⋆˚💚 ݁˖⭑.ᐟ",
    "𓂃˖˳·˖ ִֶָ ⋆💙͙⋆ ִֶָ˖·˳˖𓂃 ִֶָ⁀➴༯ sꪶꪖꪜꫀ ִֶָ. ..𓂃 ࣪ ִֶָ🌈་༘࿐ 𝗟𝗡𝗗 𝗖𝗛𝗢𝗢𝗦 -/- ⋆˚💙 ݁˖⭑.ᐟ",
]

# Fighting lists (from second script) – added for completeness
attack_list = [
    "⚔️ Teri aukat nahi mujhse ladhne ki randike 😂🔥",
    "💥 Chal bhaag yahan se chutiye warna maar khayega 🤣⚔️",
    "🗡️ Tera baap aaya hai sunta nahi kya 👑😈",
    "⚡ Mere saamne aake dikhao himmat hai toh 😎💪",
    "🔥 Attack mode on — teri khair nahi aaj 😡⚔️",
    "💀 Tujhe itna marunga ke teri maa bhi nahi pehchanegi 😂🔥",
    "⚔️ Randike chal 1v1 kar le dikhata hoon kaun baap hai 👊😤",
    "💥 Beta ye territory meri hai nikal yahan se 🏴‍☠️⚡",
    "🗡️ Aukaat hai toh saamne aa nahi toh chup baith 😈💀",
    "⚡ Tu keyboard warrior hai asli mard nahi 😂👊",
    "🔥 Teri maa ne bhi bola tera baap chahiye 😹💔",
    "💥 Chal hat yahan se chota baccha 🤣👋",
    "⚔️ Mujhe gaali de ke dekh kya hoga teri life mein 😈⚡",
    "💀 Bhai seedha bol de surrender karega ya maar khayega 😎🔥",
    "🗡️ Attack karta hoon toh block nahi hoga tera 😡⚔️",
    "⚡ Yeh game mein nahi real life mein bhi kaatenge tujhe 💪😤",
    "🔥 Tera confidence dekh ke hansi aati hai yaar 😂💥",
    "💥 Andha hai ya dikhta nahi kaun boss hai yahan 👑⚔️",
    "⚔️ Teri har gaali pe 10 gaaliyan waapis aayengi 😈🔥",
    "💀 Beta peeth nahi dikhana mujhe — coward 🏃‍♂️😂",
    "🗡️ Lad le ek baar — guarantee hai rota hoga tu 😹⚡",
    "⚡ Keyboard tod ke aa toh baat karte hain 💥👊",
    "🔥 Teri bhasha se pata chalta hai ghar mein parhe nahi 😂🤣",
    "💥 Chutiye attack se pehle socha nahi kya hoega 😈⚔️",
    "⚔️ Main yahan hoon — tu kahan chhupta hai aaja 😎💀",
    "💀 Teri har move ka jawab taiyaar hai mere paas 🎯🔥",
    "🗡️ Tu sirf darta hai asli attack nahi kar sakta 😂⚡",
    "⚡ Baahubali nahi hai tu yahan — chal nikal 👋💥",
    "🔥 Teri aukaat utni hai jitni do takke ki 😹🗡️",
    "💥 Attack aur reaction — dono mein haar jayega tu ⚔️😎",
    "⚔️ Ek baar aake dekh kya hota hai tere saath 💀🔥",
    "💀 Sher ke saamne bakra nahi ban — phir bhi ban raha 😂⚡",
    "🗡️ Yeh teri territory nahi bhai — haath jod ke ja 🙏😈",
    "⚡ Tu attack karega aur main finish karunga 💥⚔️",
    "🔥 Teri himmat hai toh mujhse seedha baat kar 😤💀",
    "💥 Keyboard pe hero ban raha hai — asli duniya mein zero 😂🗡️",
    "⚔️ Maar kha aur phir rota mat — warning hai 😈⚡",
    "💀 Teri speed se faster hoon main — bhaag nahi sakta 🔥💥",
    "🗡️ Yaar teri life mein koi nahi kya isliye yahan ata hai 😂⚔️",
    "⚡ Hero mat ban — yahan real khiladi baithe hain 👑💀",
    "🔥 Attack kiya — ab lash uthane ki taiyaari kar 😹⚡",
    "💥 Randike tu attack karta hai ya gaana gaata hai 😂⚔️",
    "⚔️ Teri har galti ka hisaab hoga — ruk 😈🔥",
    "💀 Bhai attack se pehle 1% dimag use kar 🧠💥",
    "🗡️ Chal hat nahi toh main khud hataunga isko 😤⚡",
    "⚡ Yeh war hai — aur tu already haar gaya 😎🔥",
    "🔥 Teri maa bhi tera lecture sunke bore ho gayi hogi 😹💥",
    "💥 Main attack mein vishwas nahi karta — main finish mein karta hoon ⚔️😈",
    "⚔️ Chal randike ek baar try kar le — rona mat baad mein 😂💀",
    "💀 Ab samjha kya hua? No? Toh phir ek aur attack 🔥⚡",
]

roast_list = [
    "🔥 Teri zindagi ek bakwas webseries ki tarah hai — 1 season mein flop 😂📺",
    "🤣 Bhai teri personality ek sada hua pyaz jaisi hai — khole toh aansu aaye 🧅💀",
    "😹 Tu itna bura lagta hai ke teri photo dekh ke mosquito bhi bhaag jata hai 🦟😂",
    "🔥 Teri maa ne bhi socha hoga — yaar galti ho gayi 😹👶",
    "🤣 Tujhe dekh ke pata chalta hai — darr darr ke jeena kya hota hai 😂💀",
    "😹 Beta tu Google Maps pe search kare toh bhi worthless aayega 🗺️😈",
    "🔥 Teri iq level negative hai — calculator mein error aata hai 🧮😂",
    "🤣 Tu chhata hua papad hai — touch karte hi toot gaya 😹🔥",
    "😹 Bhai teri aukat itni hai ke mirror bhi muh fer leta hai 🪞😂",
    "🔥 Teri personality dekh ke AI bhi depressed ho gaya hoga 🤖😹",
    "🤣 Tu aisa dost hai jo aaye na aaye — fark nahi padta 😂💀",
    "😹 Bhai teri soch utni hi purani hai jitna tera Nokia phone 📱😂",
    "🔥 Tera existence mere life mein irrelevant hai — bilkul sarkari kaam jaisa 📋😹",
    "🤣 Tu itna boring hai ke neend khud aa jaaye tujhe dekh ke 😴😂",
    "😹 Teri profile pic dekh ke emoji wale bhi sue kar sakte hain 😱🔥",
    "🔥 Bhai tu aisa player hai jo kabhi goal nahi kar sakta apne hi team ke khilaf 😂⚽",
    "🤣 Teri advice sunna waisa hai jaise sade kele se rasta poochna 🍌😹",
    "😹 Tu garib nahi hai — but tujhe dekh ke gareebi ko takleef hoti hai 💰😂",
    "🔥 Teri kismat itni kharab hai ke lottery ticket bhi teri traf nahi dekhti 🎫😹",
    "🤣 Bhai tera sense of humor graveyard se udhaara liya hai kya 🪦😂",
    "😹 Tu itna irrelevant hai ke khud Google bhi nahi jaanta tera naam 🔍🔥",
    "🔥 Teri body language bolta hai — main hara hua insaan hoon 😂💀",
    "🤣 Tu ek hi baar funny tha — jab tune mujhe seriously liya 😹⚡",
    "😹 Bhai teri achievements list mein sirf ek cheez hai — exist karna 😂🔥",
    "🔥 Tujhe dekh ke lagta hai — nature ne mistake ki thi 🌿😹",
    "🤣 Teri skills dekh ke Thanos ne bola hoga — yeh toh automatically wipe ho jaayega 💀😂",
    "😹 Beta tera future itna dark hai ke sunglasses pehenne ki zaroorat nahi 🕶️🔥",
    "🔥 Teri batting dekh ke khud pitch ne sorry bola 🏏😂",
    "🤣 Bhai tu aisa idea hai jo meeting mein sab ignore karte hain 📊😹",
    "😹 Teri zubaan aur dimag mein kabhi meetup nahi hota 🧠💬😂",
    "🔥 Tu aisa hero hai jiska movie 3 minutes mein flop ho gayi 🎬😹",
    "🤣 Teri gaali sunne ke baad dushmano ne mafi maang li 😂⚔️",
    "😹 Bhai tera swag level Excel mein error hai — #NAME? 📊🔥",
    "🔥 Tu itna dheema hai ke kachhua bhi race jeet gaya 🐢😂",
    "🤣 Teri thinking 2G speed pe chal rahi hai duniya 5G mein hai 📡😹",
    "😹 Beta tera ek message dekh ke aasman bhi sharma gaya ☁️😂",
    "🔥 Bhai teri life ek loading screen hai — jo kabhi load nahi hoti ⏳😹",
    "🤣 Tu aisa mirror hai jo galat reflection dikhata hai 🪞😂",
    "😹 Teri maa ne tujhe chhoda nahi chhodni chahiye thi 😂🔥",
    "🔥 Beta tera existence proof hai ke koi bhi internet use kar sakta hai 📶😹",
    "🤣 Tujhe dekh ke lagta hai — maa baap ne education mein invest nahi kiya 📚😂",
    "😹 Teri personality ek blank page hai — aur blank hi rahega 📄🔥",
    "🔥 Tu sirf chat mein hero hai real duniya mein zero 💻😂",
    "🤣 Bhai teri jawab dene ki speed se tortoise bhi impress nahi 🐢😹",
    "😹 Teri soch itni outdated hai ke floppy disk bhi reject kar de 💾😂",
    "🔥 Tu aisa WiFi password hai jo koi yaad nahi rakhta 🔑😹",
    "🤣 Beta teri awaaz sunne ke baad mujhe silence zyada priceless laga 🤫😂",
    "😹 Bhai tera roast karna waisa hai jaise sadi hui vegetable ko season karna 🥦🔥",
    "🔥 Teri social skills dekh ke chatbot bhi impress ho gaya 🤖😂",
    "🤣 Tu aisa chapter hai jise sab skip karte hain 📖😹",
]

diss_list = [
    "🎤 Tera naam sun ke log mute kar dete hain khud ko 🔇😂",
    "💀 Tu diss kar raha hai — khud ko diss kar pehle 🪞😹",
    "🎙️ Teri rap jaisi hai — no flow no bars no future 🎵😂",
    "💥 Bhai tera verse sun ke Eminem ne retire le liya 😹🎤",
    "🔥 Teri diss itni kamzor hai ke whisper bhi zyada loud hai 🤫😂",
    "💀 Tu sirf bolne mein mard hai karne mein? Zero 😈🎙️",
    "🎤 Beta teri bars mein bar hi nahi — sirf khali string 🎸😂",
    "💥 Tera diss track sunne ke baad logon ne earbuds tod diye 🎧😹",
    "🔥 Bhai teri lyric likh ke dekha — autocorrect ne bhi reject kiya ✍️😂",
    "💀 Tu diss karta hai aur log diss ko diss karte hain 😂🎤",
    "🎙️ Teri voice aisi hai ke autotune bhi nahi bach sakta 🎶😹",
    "💥 Beta freestyle kar le — ya phir stop the embarrassment 🛑😂",
    "🔥 Tujhe sun ke DJ ne plug nikal diya 🔌😹",
    "💀 Bhai tera flow aisa hai jaise jaam mein traffic — ruka hua 🚗😂",
    "🎤 Teri soch itni slow hai ke beat ke saath nahi chalti 🥁😹",
    "💥 Tera diss mujhe sula raha hai — better than sleeping pills 😴😂",
    "🔥 Bhai asli diss toh tab hogi jab tu actually kuch achieve kare 🏆😹",
    "💀 Teri lyrics Google Translate se better hain — bas 🌐😂",
    "🎙️ Beta chal hat stage se — pehle walk-on music bana 🎵😹",
    "💥 Tera punchline itna weak hai ke paper bhi survive kar le 📄😂",
    "🔥 Bhai teri diss sun ke crowd ne baat karna shuru kar diya 🙄😹",
    "💀 Tu verse likhta hai ya grocery list — same energy 🛒😂",
    "🎤 Teri bars mein calories zyada hain — totally empty 😹🔥",
    "💥 Bhai teri rhyme sunke chhote bacche bhi sharma jaate hain 😂💀",
    "🔥 Teri diss aisi hai — sirf uski maa samjhi 😹🎙️",
    "💀 Tu diss karta hai mujhe — main khud apni diss sunta hoon for fun 😂💥",
    "🎤 Tera stage naam kya hai — Bakwas ke Raja? 👑😹",
    "💥 Bhai teri microphone bhi teri awaaz se dara hua hai 🎙️😂",
    "🔥 Tu diss mein expert hai — aur expert hone mein loser 😹💀",
    "💀 Teri har line mein cringe hai — Olympic level 🥇😂",
    "🎙️ Beta khud ki diss sun le — ek baar realise hoga 😹🔥",
    "💥 Bhai tera diss itna slow hai ke mujhe neend aa gayi 😴😂",
    "🔥 Teri creativity level: template pe naam likhna 💀😹",
    "💀 Tu diss karne ke liye paida hua tha — aur fail ho gaya 😂🎤",
    "🎙️ Tera rhyme scheme: aab aab aab — boring AF 📝😹",
    "💥 Bhai teri diss response mein Soulja Boy beat use karta hun 😂🔥",
    "🔥 Tu keyboard pe rap karta hai — phone pe nahi kaata 📱💀",
    "💀 Teri diss sun ke mic khud neeche gir gaya 🎙️😂",
    "🎤 Beta teri bars itni weak hain ke paper toh chodh kaagaz bhi nahi chhapega 📰😹",
    "💥 Bhai tera flow paani mein nahi petrol mein hai — ab blast 🔥😂",
    "🔥 Teri diss sunta hoon toh lagta hai sabne kaan band kar rakhe hain 🔇💀",
    "💀 Tu diss mein ghusaa — tu diss tha diss 😹😂",
    "🎙️ Bhai tera verse industry standard se neeche hai — ground floor bhi nahi 🏚️🔥",
    "💥 Teri awaaz mein woh baat nahi jo diss mein chahiye — talent 😂💀",
    "🔥 Beta teri diss itni pathetic hai ke pity vote mil sakta tha 🗳️😹",
    "💀 Bhai teri rap career ek Instagram story jaisi hai — 24 ghante mein khatam 📸😂",
    "🎤 Tu rapper nahi rapper ki copy ki copy ka knock-off hai 😹🔥",
    "💥 Teri diss sun ke auto-generated ho sakti hai — aur better hoti 🤖😂",
    "🔥 Bhai freestyle maar — aur phir sun khud ko — tujhe pata chalega 🎧💀",
    "💀 Teri diss ka reply nahi deta — tujhe dignify karna time waste hai 😂🎙️",
]

war_list = [
    "⚔️ War shuru ho gayi — aur tu pehle hi haar gaya 😂🔥",
    "💣 Bhai main war mein nahi aata — main war khatam karne aata hoon 😈⚡",
    "🏴‍☠️ Tera jhanda uraya — apna wala lehraya 😎💀",
    "⚔️ Tu lad raha hai mujhse — yeh teri sabse badi galti hai 🔥😂",
    "💣 Main war nahi khelta — main result deliver karta hoon 👑⚡",
    "🏴‍☠️ Battlefield pe aake to dekh — tera rank kya hai 😈⚔️",
    "⚔️ Randike war declare kiya toh surrender ka option bhi rakh 😂💣",
    "💣 Tu soldier nahi hai — tu sirf noise hai 🔊😂",
    "🏴‍☠️ War mein strategy chahiye — tu sirf emotion se ladhta hai 😹⚔️",
    "⚔️ Beta yeh teri territory nahi — nikalja 👋💣",
    "💣 Tera war cry sunke mujhe neend aati hai 😴😂",
    "🏴‍☠️ Main akela kaafi hoon — teri poori army ke liye ⚔️😈",
    "⚔️ War ghoshit kiya — white flag kahan hai tera 🏳️😂",
    "💣 Bhai tu pehle khud ko toh jeet — phir mujhse lad 😎💀",
    "🏴‍☠️ Tera war tactic: bolna aur bhaagna 😹⚔️",
    "⚔️ Main chhoda nahi — tu chhoda baad mein roega 😂💣",
    "💣 Battle field pe aate waqt socha — main jeet sakta hoon? Nahi 😈🏴‍☠️",
    "⚔️ Tu ek round bhi nahi jeeta — aur war ki baat karta hai 😂💀",
    "💣 Bhai surrender kar le — dignity bachegi thodi 🙏😹",
    "🏴‍☠️ War mein aaye — aur pehli line mein fail ho gaye ⚔️😂",
    "⚔️ Tera morale zero hai — teri army teri khud ki dushman hai 😂💣",
    "💣 Main war expert hoon — tu war ka victim hai 😎🏴‍☠️",
    "🏴‍☠️ Beta teri strategy ek broken compass jaisi hai ⚔️😂",
    "⚔️ War mein seena taan ke aa — peeth dikha ke nahi 😹💣",
    "💣 Bhai teri army mein sirf tu hai — aur tu kaafi nahi 😈🏴‍☠️",
    "🏴‍☠️ Teri war cry sun ke dushman khud aa gaye — rescue karne ⚔️😂",
    "⚔️ Beta teri territory war se pehle hi haari thi 💣😹",
    "💣 Main war mein nahi — main tujhe personally destroy karne mein hoon 😈🏴‍☠️",
    "🏴‍☠️ Tera war plan sunke GPS bhi confused hai ⚔️😂",
    "⚔️ Tu war mein aaya — par weapons lana bhool gaya 💣😹",
    "💣 Bhai yeh war nahi tujhe sirf reality check tha 😂🏴‍☠️",
    "🏴‍☠️ Teri army tujhse zyada samajhdaar hai — unhone bandh kiya ⚔️😈",
    "⚔️ War mein bhi excuse karta hai — aur life mein bhi 😂💣",
    "💣 Tu jo war soch raha hai — woh meri morning routine hai 😎🏴‍☠️",
    "🏴‍☠️ Bhai teri war itni slow hai ke climate change pehle ho jaayega ⚔️😹",
    "⚔️ Main tujhse war karta hoon — aur tujhe pata bhi nahi chalta 💣😂",
    "💣 War ghoshit kar ke tu pehla tha — haar ke bhi pehla hai 😹🏴‍☠️",
    "🏴‍☠️ Teri war mein consistency hai — consistently losing ⚔️😂",
    "⚔️ Bhai war mein bhagna galat hai — tu phir bhi karta hai 💣😈",
    "💣 Tu war mein aaya — main pehle se tere base par tha 🏴‍☠️😂",
    "🏴‍☠️ Teri war strategy mein sirf ek problem hai — sab kuch ⚔️😹",
    "⚔️ Beta war ka matalab samjha nahi tujhe — sikhaunga abhi 💣😂",
    "💣 War mein hero nahi bante — survivors bante hain — aur tu nahi banega 🏴‍☠️😈",
    "🏴‍☠️ Teri war mein dum nahi — sirf dhool hai ⚔️😂",
    "⚔️ Bhai war declare karna alag baat hai — jeetan alag 💣😹",
    "💣 Tu war mein aaya sirf lose karne ke liye — congratulations 🏴‍☠️😂",
    "🏴‍☠️ Main akele teri sab pe bhaari hoon — aur tujhe pata hai ⚔️😈",
    "⚔️ Teri war ka sabse bura part — tu khud tha 💣😂",
    "💣 War mein aaye — teri team ne hi tujhe chhod diya 🏴‍☠️😹",
    "🏴‍☠️ Beta war khatam — teri taraf se surrender accepted ⚔️😎",
]

savage_list = [
    "😈 Main savage hoon — tujhe explanation nahi deta 🔥💀",
    "💀 Teri feelings mere liye statistics hain — irrelevant 😂😈",
    "🔥 Main woh nahi hoon jo tujhe comfortable feel karaaye 😎💀",
    "😈 Beta teri baatein mujhe bore karti hain — next 😂🔥",
    "💀 Teri opinion meri life mein footnote bhi nahi hai 😈😹",
    "🔥 Main tujhe explain nahi karta — tujhse better logon ke paas time deta hoon 😎💀",
    "😈 Tera attitude dekh ke mujhe apni nails file karni chahiye 💅😂",
    "💀 Bhai tujhe reject karna meri hobby hai 🔥😈",
    "🔥 Teri presence mujhe remind karaati hai — kuch logon ko mute karna chahiye 🔇😂",
    "😈 Main bad vibes nahi leta — teri taraf bhi nahi 💀🔥",
    "💀 Tu mere standard se neeche hai — elevator laga le 🛗😂",
    "🔥 Teri baat sunna — option nahi habit nahi aur interest bhi nahi 😈💀",
    "😈 Main ghanta samjhata hoon — samajh nahi aaya toh teri problem 😂🔥",
    "💀 Teri ego itni badi hai — uske liye alag zip code chahiye 📮😂",
    "🔥 Beta mujhe tujhse jealousy feel nahi hoti — pity hoti hai 😈💀",
    "😈 Main woh insaan nahi hoon jis par tu waqt barbad kare — ya main karta hoon 😂🔥",
    "💀 Teri life choices dekh ke main grateful hoon main tujhsa nahi hoon 😹😈",
    "🔥 Bhai teri smartness ka level: WiFi password ignore karna 📶😂",
    "😈 Teri mastiyan mujhe entertain nahi karti — bore karti hain 💀🔥",
    "💀 Main savage nahi — main simply tujhse better hoon 😎😂",
    "🔥 Teri personality ek blank meme format jaisi hai — kuch nahi 😈💀",
    "😈 Beta apni journey pe focus kar — meri disturb mat kar 😂🔥",
    "💀 Teri hard work ka result tera hi face hai — kaafi bura 😹😈",
    "🔥 Main tujhe miss nahi karta — mujhe tujhse better cheezein miss hoti hain 😂💀",
    "😈 Teri baatein sun ke laga — yeh real person hai ya chatbot glitch 🤖😂",
    "💀 Bhai teri intelligence ke liye sorry feel hoti hai 🔥😈",
    "🔥 Main tujhe block isliye nahi karta — kyunki tujhe exist karna pata hai 😂💀",
    "😈 Teri struggles dekh ke mujhe motivation milti hai — teri tarah mat banna 😹🔥",
    "💀 Tu jo effort lagate ho mujhpe — woh apni growth mein lagao 😎😂",
    "🔥 Teri vibes mujhe 2G network se bhi slow lagti hain 📡😈",
    "😈 Main tujhe pehle judge nahi karta — par tujhe pehle judge hota hoon 💀😂",
    "💀 Bhai tera shadow bhi tujhse zyada interesting hai 🔥😂",
    "🔥 Teri logic sun ke Albert Einstein ne resign kar diya hoga 🧪😈",
    "😈 Tu mere jaisa ban sakta hai — agar try karta 10 saal toh bhi nahi 💀😂",
    "💀 Teri taraf se koi bhi reaction — mujhe bored karta hai 🔥😹",
    "🔥 Main respectful hoon — tere sath nahi 😈💀",
    "😈 Beta teri vibe check: FAILED 😂🔥",
    "💀 Teri har move predicted thi — boring player 😹😈",
    "🔥 Main tujhe second chance nahi deta — teri pehli impression kafi thi 😂💀",
    "😈 Teri friendship ke offer ko professionally decline karta hoon 😎😂",
    "💀 Beta tu mujhe feel nahi karaata — tu sirf annoy karta hai 🔥😈",
    "🔥 Teri dimagi capacity dekh ke solar calculator bhi sorry bol de 🔋😂",
    "😈 Main uun logon mein nahi hoon jo tere liye time waste karein 💀🔥",
    "💀 Teri life ka GPS tujhe wrong direction mein le ja raha hai 🗺️😂",
    "🔥 Bhai teri alag identity bana — copier mat ban 😈💀",
    "😈 Tu mere radar par bhi nahi aata — itna irrelevant hai 😂🔥",
    "💀 Teri maa ne bhi socha hoga — yaar isko kuch aur karna chahiye tha 😹😈",
    "🔥 Main woh hoon jo teri nightmares mein aata hai — as a reminder 😎💀",
    "😈 Beta teri bakaiti mujhe filter nahi karti — automatically skip ho jaati hai 😂🔥",
    "💀 Tu savage hone ki koshish karta hai — mujhe dekh savage ka example 😈😹",
]

ultra_list = [
    "🌪️ ULTRA MODE ACTIVATED — teri poori existence question mein hai 😈🔥",
    "⚡ Ultra attack — pehle gaali sunna phir rona — sequence yaad kar 😂💀",
    "🌪️ Beta ultra level pe aake dekh — yahan teri category nahi hai 👑🔥",
    "⚡ ULTRA BLOW — teri soch se lekar attitude tak sab destroy 💥😈",
    "🌪️ Yeh ultra mode hai — blocking nahi help karega 😂⚡",
    "⚡ Ultra raid engaged — ab teri poori chat history history hai 📜😹",
    "🌪️ Beta ultra speed mein aa — par seedha home le jaata hoon 💀🔥",
    "⚡ Ultra fire — teri har defensive move kaam nahi karegi 😈🌪️",
    "🌪️ Yeh ultra level fight hai — tu still bronze mein hai 😂⚡",
    "⚡ ULTRA DAMAGE — teri reputation, teri aukaat, teri everything 💥😹",
    "🌪️ Ultra mode mein poori teri army bhi kaafi nahi 😈🔥",
    "⚡ Beta ultra attack sunne ke baad sun raha hai kya? Normal hai 😂🌪️",
    "🌪️ ULTRA RANT incoming — tune jo kiya uska hisaab hoga 💀⚡",
    "⚡ Yeh ultra version hai — tujhe pata bhi nahi kya aaya 😹🔥",
    "🌪️ Ultra mode ON — timer chal raha hai teri destruction ka 😈⚡",
    "⚡ Beta ultra strike pe tujhe sirf ek option hai — disappear 😂💀",
    "🌪️ ULTRA COMBO — reply + react + roast + raid all at once 🔥⚡",
    "⚡ Yeh ultra level rage hai — aur tujhe taste hoga 😈🌪️",
    "🌪️ Ultra activated — pehle bol sorry phir ja 😹😂",
    "⚡ Beta ULTRA message ka matlab — tu mere liye mission ban gaya 💀🔥",
    "🌪️ ULTRA STORM — har cheez destroy ho rahi hai teri side pe 😈⚡",
    "⚡ Yeh ultra nahi — tujhe sirf samjhane ki koshish thi 😂🌪️",
    "🌪️ Ultra mode finish — teri team ne tera saath chhoda 💀🔥",
    "⚡ Beta ULTRA = mera minimum effort on you 😈😂",
    "🌪️ ULTRA RAIN — tune invite kiya tha — enjoy karna tha na? 😹⚡",
    "⚡ Ultra mode mein ek hi rule — no mercy 💀🔥",
    "🌪️ Beta ULTRA sabse pehle yeh — teri galti ka hisaab 😈⚡",
    "⚡ Yeh ultra speed se aaya — aur teri samajh mein ultra slow aayega 😹🌪️",
    "🌪️ ULTRA LOCK — ab yahan se nahi jayega tu 💀🔥",
    "⚡ Beta ultra strike mein teri saari strategy fail hai 😂😈",
    "🌪️ Ultra level pe chal — toh teri duniya hi badal jaayegi 🔥⚡",
    "⚡ ULTRA — yeh word hi teri aukat se bada hai 😹💀",
    "🌪️ Beta ultra mein main hoon — tujhe pata nahi tha kya 😈🔥",
    "⚡ Yeh ultra raid hai — har message teri ek problem hai 😂🌪️",
    "🌪️ ULTRA DONE — tu done kar le pehle 💀⚡",
    "⚡ Beta ultra mein welcome — pehle bol kya karna hai 😹🔥",
    "🌪️ Ultra mode — ab seedha point pe aata hoon — tu fail hai 😂😈",
    "⚡ ULTRA BLAST — teri timeline pe aaya — nahi ruk sakta 💥🌪️",
    "🌪️ Beta ultra mein aake teri baat karo — nahi aata toh seedha ja 💀🔥",
    "⚡ Yeh ultra war hai — aur teri taraf se koi nahi 😂😈",
    "🌪️ ULTRA FINAL — bas yahi hoga — accept kar 💀⚡",
    "⚡ Beta ultra strike complete — check teri status 😹🔥",
    "🌪️ Ultra mode mein log surrender karte hain — tujhe bhi karna hoga 😈⚡",
    "⚡ Yeh ultra punishment nahi — tutorial hai teri life ka 😂💀",
    "🌪️ ULTRA JUDGEMENT — teri har move judged ho rahi hai 🔥⚡",
    "⚡ Beta ultra mein ek cheez — main hoon aur tu nahi rahe 😈🌪️",
    "🌪️ Ultra mode completed — teri side destroyed 💀😂",
    "⚡ Yeh ultra attack ka last wave hai — teri koi repair nahi 😹🔥",
    "🌪️ ULTRA END — teri war khatam teri taraf se flag gira 😈⚡",
    "⚡ Beta ultra mein aana tha — rona nahi tha — par dono kiye 😂💀",
]

godwar_list = [
    "👑 GOD MODE — tu mortal hai mujhse ladhne ki aukat nahi 😈🔥",
    "🌟 Main GOD WAR mein hoon — teri poori bloodline haari 💀⚡",
    "👑 Beta God level pe welcome — nahi samjha toh nahi samjha 😂😈",
    "🌟 GOD FURY — sun raha hai na? Yeh teri calling hai 🔥💀",
    "👑 Main woh hoon jis se God bhi seekhta hai war 😎⚡",
    "🌟 Beta God war mein aaja — tujhe enlightenment milega 😂🔥",
    "👑 GOD LEVEL ATTACK — teri sari defenses dust hain 💀😈",
    "🌟 Main tujhe war mein nahi involve karta — tujhe demo dikhata hoon 😎⚡",
    "👑 Beta GOD mode — yeh teri life pe trailer tha 🔥😂",
    "🌟 GOD WAR declaration — teri surrender automatically process hogi 💀😈",
    "👑 Mujhse God war karta hai — bhai apni aukat dekh pehle 😹🌟",
    "🌟 Beta yeh God ki territory hai — tujhe clearance nahi 😈🔥",
    "👑 GOD RAID — tune invite nahi kiya tha — main khud aaya 💀⚡",
    "🌟 God level pe destruction toh ek ritual hai — tu shikaar hai 😂😈",
    "👑 Beta GOD WAR mein mercy nahi hoti — yaad rakhna 🔥💀",
    "🌟 Main GOD hoon — tujhse sirf proof nahi — demonstration 😎⚡",
    "👑 GOD FURY — teri poori defence grid fail ho gayi 😂🌟",
    "🌟 Beta tu GOD war ke eligible nahi — neeche jaake pehle seedh ho 💀😈",
    "👑 GOD LEVEL ROAST — teri existence ko judge kar raha hoon 🔥😂",
    "🌟 Main GOD mein aaya — teri poori team disqualified 😈⚡",
    "👑 Beta GOD war ka ek hi rule — mera wins 💀🌟",
    "🌟 GOD MODE FINAL — teri sab pray kar rahi hai — tere liye 😂🔥",
    "👑 Main GOD war mein sirf ek baar aata hoon — yeh tha 😈💀",
    "🌟 Beta GOD ki bhasha — tu nahi samjhega 🔥⚡",
    "👑 GOD WRATH — teri aankh mein aansu aayenge meri victory pe 😂😈",
    "🌟 Main GOD hoon yahan — tujhe bhagwan bhi nahi bachayega 💀🔥",
    "👑 Beta GOD war mein aake cry mat karna 😹🌟",
    "🌟 GOD LEVEL — teri poori history erase — new game 😈⚡",
    "👑 Main GOD war mein tab aata hoon jab dushman deserve karta hai 🔥💀",
    "🌟 Beta GOD mode mein teri soch bhi haari 😂😈",
    "👑 GOD RAID COMPLETE — check teri position 💀🔥",
    "🌟 Main GOD hoon — isliye tujhe seriously le raha hoon briefly 😎⚡",
    "👑 Beta GOD war mein rules nahi hote — sirf results 😂🌟",
    "🌟 GOD FURY UNLEASHED — ab teri timeline pe aa raha hoon 💀😈",
    "👑 Main GOD level pe operate karta hoon — tu tutorial mein hai 🔥⚡",
    "🌟 Beta GOD war ka last chapter — teri story yahan khatam 😂💀",
    "👑 GOD MODE — tujhe itna marunga ke tujhe khud samajh aayega 😈🌟",
    "🌟 Main GOD war mein hoon — tu still login attempt mein 🔥😂",
    "👑 Beta GOD level destroy — teri poori team silent hai 💀⚡",
    "🌟 GOD WAR — yeh nahi tha teri plan mein — par mera tha 😈😂",
    "👑 Main GOD hoon — mercy nahi hai yahan — documentation nahi meri 🔥💀",
    "🌟 Beta GOD level baat — teri aukat sun lene ki nahi ⚡😈",
    "👑 GOD WAR OVER — teri side: zero GOD side: everything 😂🌟",
    "🌟 Main GOD mode mein hoon — tujhe pata bhi nahi 💀🔥",
    "👑 Beta GOD war mein aake tujhe pehle proof karna hoga — nahi kar sakta 😈⚡",
    "🌟 GOD FINAL BLOW — yeh tha — enjoy kar teri haari 😂💀",
    "👑 Main GOD hoon — teri war meri relaxation thi 🔥😎",
    "🌟 Beta GOD mode ACTIVATED — teri poori chat screenshot ho rahi hai 😹💀",
    "👑 GOD WAR — sirf GOD jeette hain — aur GOD main hoon 😈⚡",
    "🌟 Beta GOD war ka tutorial yaad rakho — yeh tha 😂👑",
]

combo_list = [
    "💥⚔️🔥 COMBO HIT — reply + roast + flag + react sab ek saath 😈💀",
    "🌪️💣👑 TRIPLE COMBO — teri sab kuch ek hi shot mein 😂⚡",
    "💥🔥😈 COMBO ATTACK — nahi rokna kisi ke liye bhi 💀🌪️",
    "⚔️💣🌟 Yeh combo hai — tu already down hai teri counting shuru 😂🔥",
    "🌪️😈💀 MEGA COMBO — tera sara defense ek message mein finish 😹⚡",
    "💥⚡👑 Combo level ULTRA — teri koi move kaam nahi ayegi 🔥😂",
    "⚔️🔥😹 COMBO RAIN — jab bhi message karega — combo activate 💀🌪️",
    "🌪️💣😈 Beta yeh combo nahi — yeh tujhe samjhaane ka tarika hai 😂⚡",
    "💥👑🔥 GRAND COMBO — teri poori squad aaj haari 😈💀",
    "⚔️🌪️😂 Combo attack engage — ab teri duniya theek nahi hogi 🔥💣",
    "💀⚡💥 COMBO BLAST — every message ek naya problem tera 😹😈",
    "🔥🌪️⚔️ Beta COMBO mein teri sochi bhi counted hai 😂💀",
    "😈💣👑 COMBO FINISHER — teri team tujhe chhod ke bhaag gayi ⚡🔥",
    "💥🔥😹 Yeh combo teri life ka worst decision yaad karayega 😈🌪️",
    "⚔️💀🌟 COMBO CHECK — teri reply ka wait nahi — next combo ready 😂⚡",
    "🌪️😈💣 Beta combo mein teri sab cheez shaamil hai — teri galti bhi 🔥💀",
    "💥⚡🔥 ULTIMATE COMBO — teri existence challenged hai 😹😂",
    "⚔️👑😈 Combo attack — ek aaya aur sab le gaya 💀🌪️",
    "🌪️💥😂 Beta COMBO FURY — tujhe recover karne ki zaroorat nahi rahi 🔥⚡",
    "💣🔥👑 COMBO FINALE — teri story ka end likha ja raha hai 😈💀",
    "⚔️💀😹 Yeh combo tujhpe dedicated hai — enjoy kar 🌪️⚡",
    "🌪️😈🔥 COMBO STORM — har cheez teri toot rahi hai 💥😂",
    "💀⚡💣 Beta COMBO mein koi block kaam nahi aata 😹🔥",
    "🔥👑🌪️ COMBO TRIGGER — teri sab mute hone chahiye 😈💀",
    "💥😂⚔️ COMBO RAID — pehli baar nahi — par yaadgaar hai 🌪️⚡",
    "😈💣🔥 Beta COMBO kar ke dekh — apni taraf se 😂💀",
    "⚡🌪️😹 COMBO OVERDRIVE — tujhe pause bhi nahi milega 🔥😈",
    "💀💥👑 Yeh COMBO tera time waste hai — mera fun 😂⚔️",
    "🌪️⚔️😈 COMBO LAUNCH — teri trajectory down hai 🔥💣",
    "💥😹🌟 Beta COMBO mein aake sab kuch kaata — kuch nahi bachega 💀😂",
    "🔥😈💣 COMBO PUNISHMENT — teri har galti ka charge add ho raha hai ⚡🌪️",
    "⚔️💀😂 Yeh COMBO tera tutorial tha — fail ho gaya 🔥💥",
    "🌪️⚡😈 COMBO FINISH — teri team ki condolences le aata hoon 😹💀",
    "💥👑🔥 Beta COMBO LOADED — sab teri taraf aim hai 😂😈",
    "⚔️💣🌪️ COMBO EXPLOSION — teri har cheez gone 💀⚡",
    "😈🔥💀 Beta yeh COMBO teri poori chat ka summary hai 😹🌪️",
    "💥⚡😂 GRAND COMBO RELEASE — tujhe mera response nahi chahiye — aata hai 🔥😈",
    "🌪️💣👑 COMBO RAIN — teri timeline pe aa raha hoon 💀⚔️",
    "⚡🔥😹 Beta COMBO engage — teri soch ke pehle message aa gaya 😈🌪️",
    "💥😈⚔️ MEGA COMBO — tujhe pehle bola tha — nahi maana 💀🔥",
    "🌪️💀😂 COMBO LOCKED — teri taraf se no escape 😈⚡",
    "🔥⚔️💣 Beta COMBO mein sab kuch plan tha — tujhe nahi pata tha 😹💀",
    "💥🌪️😈 COMBO BURST — teri poori squad silent ho gayi 🔥⚡",
    "⚡💀🔥 Yeh COMBO teri poori history ka audit tha 😂😈",
    "🌪️💥👑 COMBO COMPLETE — teri side: nothing ours: everything 💀🔥",
    "😈⚔️😹 Beta COMBO mein aake pata chala — tujhe try mat karna chahiye tha 🌪️⚡",
    "💀🔥💥 COMBO FINAL WAVE — last chance surrender kar le 😂😈",
    "⚡🌪️👑 Yeh COMBO nahi tha — practice session tha tera against 😹💀",
    "💥😈🔥 COMBO OVER — teri wahi condition jo socha tha 🌪️⚡",
    "⚔️💀😂 MEGA COMBO DONE — shukriya tera — itna fun kabhi nahi tha 😈🔥",
]

troll_list = [
    "🤡 Bhai tujhe dekh ke lagta hai troll ka mascot tu hai 😂🔥",
    "😹 Tu itna troll hai ke khud ko pata nahi 💀🤡",
    "🤡 Teri baatein sun ke log seriously nahi lete — aur le bhi nahi chahiye 😂😹",
    "😹 Beta tu internet ka troll #1 candidate hai 💀🤡",
    "🤡 Tujhe real life mein bhi ignore karte honge log 😂🔥",
    "😹 Bhai teri comments section mein sabne dislike diya 👎🤡",
    "🤡 Tu troll karne ki koshish karta hai — khud troll bana rehta hai 😂💀",
    "😹 Teri troll game weak hai — aur weak troll game bhi troll hai 🤡🔥",
    "🤡 Beta jo tu sochta hai funny hai woh boring hai 😂😹",
    "😹 Bhai tera troll skill level: tutorial mode pe stuck 🤡💀",
    "🤡 Tu troll hai par original nahi — copy-paste troll 😂🔥",
    "😹 Teri trolling se logon ko secondhand embarrassment hoti hai 🤡😂",
    "🤡 Beta tujhe seriously lena — woh troll hoga apne aap pe 😹💀",
    "😹 Bhai tera meme quality — delete worthy 🤡😂",
    "🤡 Tu troll karta hai online — real duniya mein kaanta nahi milta 😹🔥",
    "😹 Beta teri har post pe raat ko cry karta hai 🤡💀",
    "🤡 Tujhe dekh ke pata chalta hai — internet access free nahi honi chahiye 😂😹",
    "😹 Bhai teri troll attempt genuine cringe hai 🤡🔥",
    "🤡 Tu troll ka wannabe version hai 😂💀",
    "😹 Beta asli troll woh hota hai jise pata nahi woh troll hai — tu wahi hai 🤡😂",
    "🤡 Bhai teri comments log copy karke dusron ko dikhate hain — example ke liye kya nahi karna chahiye 😹🔥",
    "😹 Tu troll karta hai par khud hi jal jaata hai 🤡💀",
    "🤡 Beta teri troll attempts fail hoti hain kyunki tujhe original hona chahiye 😂😹",
    "😹 Bhai seriously — apni energy sahi jagah lagao 🤡🔥",
    "🤡 Teri trolling mein timing nahi content nahi creativity nahi 😂💀",
    "😹 Beta tu woh insaan hai jo khud ko troll king samjhta hai — aur paida hota hai troll ke neeche 🤡😂",
    "🤡 Bhai tera troll fail isliye hota hai — genuine nahi hai 😹🔥",
    "😹 Tu troll karta hai aur end mein rota hai — classic 🤡💀",
    "🤡 Beta tujhe sun ke logon ko stress nahi hoti — pity hoti hai 😂😹",
    "😹 Bhai teri troll quality inspect hua — returned as defective 🤡🔥",
    "🤡 Tu original troll nahi — fan-made version hai 😂💀",
    "😹 Beta teri trolling attempt mein best cheez — mujhe engage nahi karta 🤡😂",
    "🤡 Bhai teri presence troll community ke liye embarrassment hai 😹🔥",
    "😹 Tu troll karta hai aur log silent ho jaate hain — cringe se 🤡💀",
    "🤡 Beta teri troll ka response — ignore — kyunki deserve nahi karta 😂😹",
    "😹 Bhai tera troll skill tree mein sirf ek node hai — aur woh bhi locked hai 🤡🔥",
    "🤡 Tu troll ka demo version hai — full version nahi aaya 😂💀",
    "😹 Beta trolling seekh pehle phir aa — abhi tu syllabus mein nahi hai 🤡😂",
    "🤡 Bhai teri baatein sun ke log empathy feel karte hain — tere liye 😹🔥",
    "😹 Tu troll nahi — annoying hai — alag concept hai 🤡💀",
    "🤡 Beta tera troll game 0/10 — ek baar apni chat history padh 😂😹",
    "😹 Bhai tu sirf apna time barbad kar raha hai — mera nahi 🤡🔥",
    "🤡 Teri troll attempt ek baar bhi hit nahi hui — streak: 0 😂💀",
    "😹 Beta tera troll unprovoked aur uninspired tha 🤡😂",
    "🤡 Bhai tu troll ke bhi standards neeche hai 😹🔥",
    "😹 Teri trolling see aur feel karna — dono experience kharab hain 🤡💀",
    "🤡 Beta teri troll ne sirf yeh prove kiya — tujhe better kaam dhundhna chahiye 😂😹",
    "😹 Bhai troll mein skill hoti hai — teri mein nahi 🤡🔥",
    "🤡 Tu troll hai aur tera troll bhi troll hai — recursion 😂💀",
    "😹 Beta ek advice — yeh mat kar — seriously apni life mein focus kar 🤡😎",
]

shame_list = [
    "😤 Sharam kar — itna gira hua kaam karte kaise hain tum log 🔥💀",
    "🙅 Bhai teri harkat dekh ke pura group sharam se doob gaya 😂😤",
    "😤 Yeh sab karke tujhe pride feel hoti hai? Really? 💀🔥",
    "🙅 Beta teri harkaten dekh ke maa baap sharmayenge 😂😤",
    "😤 Sharam nahi hai tujhe bilkul — clearly 💀😹",
    "🙅 Bhai itna gira hua kaam dekh ke log muh fer lete hain 😤🔥",
    "😤 Tu itna neeche gira — zameen bhi neeche ho gayi 💀😂",
    "🙅 Beta sharam bhi nahi aata aisa karte hue 😤😹",
    "😤 Yeh harkat dekh ke lagta hai — tujhe value kisi ne nahi sikhayi 💀🔥",
    "🙅 Bhai log tujhe dekh ke aankhein pher lete hain — soch kya kar raha hai 😤😂",
    "😤 Teri galti nahi — environment ki galti — par ab waqt hai change ka 💀😹",
    "🙅 Beta sharam isliye nahi aati kyunki sharam feel karna seekha nahi 😤🔥",
    "😤 Yeh kaam karke tujhe khushi mili? Toh mujhe tujhse zyada chinta hai 💀😂",
    "🙅 Bhai teri harkat pura record hai — aur yeh record kharab hai 😤😹",
    "😤 Tu sochta hai koi dekh nahi raha — sab dekh rahe hain 💀🔥",
    "🙅 Beta aisa behave karta hai — khud se bhi embarrassing lagta hai tu 😤😂",
    "😤 Yeh sab dekh ke lagta hai — teri parwarish kahan gayi 💀😹",
    "🙅 Bhai teri harkaton ka hisaab hoga — aaj nahi toh kal 😤🔥",
    "😤 Tu sharminda nahi hai — woh most shameful cheez hai 💀😂",
    "🙅 Beta logo ne tujhe judge kiya — kyunki tune judge hone wala kaam kiya 😤😹",
    "😤 Yeh bura kaam karke tujhe kya mila — kuch nahi — bas naam barbad 💀🔥",
    "🙅 Bhai sharam karo — itna toh haq hai tumhara 😤😂",
    "😤 Tu yahan cool lagne ki koshish mein sharminda ho gaya 💀😹",
    "🙅 Beta ghalat rasta chhod — vapas aa 😤🔥",
    "😤 Yeh sab karke teri image bani hai — worst category mein 💀😂",
    "🙅 Bhai teri harkat ka review — 0 stars — do not recommend 😤😹",
    "😤 Tu itna neeche gira — recovery mushkil lagti hai 💀🔥",
    "🙅 Beta tujhe samjhana waqt waste hai — par try kar raha hoon 😤😂",
    "😤 Yeh sab dekh ke mujhe tujhse zyada tujhpe gussa nahi — hairaani hai 💀😹",
    "🙅 Bhai sharam se doob — par us mein bhi tujhe help chahiye shayad 😤🔥",
    "😤 Teri harkat ek lesson hai — dusron ke liye kya nahi karna chahiye 💀😂",
    "🙅 Beta teri yeh sab dekh ke khud bhi tujhse door rehna chahta hoon 😤😹",
    "😤 Yeh gaaliyaan nahi — sirf reality check hai 💀🔥",
    "🙅 Bhai sharam tab aati hai jab insaan mein insaniyat hoti hai 😤😂",
    "😤 Tu ek example bana diya khud ko — negative example 💀😹",
    "🙅 Beta tujhe ek baar ruk ke soochna chahiye tha — nahi soocha 😤🔥",
    "😤 Yeh sab karke tu yahan hai — aur sochta hai main galat hoon? 💀😂",
    "🙅 Bhai itna toh bata — tujhe kaisa feel hota hai yeh sab karne ke baad 😤😹",
    "😤 Tu sharminda nahi — tujhe sharminda feel karna chahiye 💀🔥",
    "🙅 Beta yeh rasta galat hai — abhi bhi change ho sakta hai 😤😂",
    "😤 Yeh sab khud se bura nahi tha — tu tha 💀😹",
    "🙅 Bhai teri harkaton ka real world impact sun — sab tujhse dur hain 😤🔥",
    "😤 Tu soch raha hai main overreact kar raha hoon — par tujhe hisaab hoga 💀😂",
    "🙅 Beta tujhe pata hai tu kya kar raha hai — aur phir bhi kar raha hai 😤😹",
    "😤 Yeh sharm ki baat hai — aur tujhe realize karna chahiye 💀🔥",
    "🙅 Bhai tujhe mirror mein dekhna chahiye — ek baar 😤😂",
    "😤 Tu itna bura nahi hai — par yeh kaam bura tha 💀😹",
    "🙅 Beta sharam isliye nahi aati — kyunki tu sochta nahi consequences ke baare mein 😤🔥",
    "😤 Yeh moment tera lowest point hai — aur abhi bhi jaag sakta hai 💀😂",
    "🙅 Bhai aaj ek kaam kar — sharminda ho aur badal — bas itna chahiye 😤😎",
]

fire_list = [
    "🔥 FIRE MODE — teri sab cheez jal rahi hai 😈⚡",
    "🔥🔥 Double fire — tujhe bachaane ka option nahi 💀😂",
    "🔥 Teri har baat pe fire respond karenge — ready? 😈⚡",
    "🔥 Bhai FIRE unleashed — tujhe pata bhi nahi kya aaya 💀😂",
    "🔥 Fire level 10 — teri poori existence threatened 😈🌪️",
    "🔥 Beta teri baatein fire se nahi — mere se jali 💀😂",
    "🔥 FIRE STORM — teri location traced — figuratively 😈⚡",
    "🔥 Bhai mere fire pe paani mat daal — gasoline hai 💀🔥",
    "🔥 Teri baat pe FIRE response — tu ready tha? 😂😈",
    "🔥 Beta ek cheez tujhe batata hoon — yeh fire hai — bhaag ja 💀⚡",
    "🔥 FIRE DROP — teri sab baatein ash ho gayi 😈😂",
    "🔥 Bhai fire mein kaun jata hai? Tu gaya — khud 💀🔥",
    "🔥 Tera attitude fire pe throw kiya — zyada jala 😈⚡",
    "🔥 Beta fire mode mein teri har line ka jawab ek blaze 💀😂",
    "🔥 FIRE BURST — teri defense melt ho gayi 😈🌪️",
    "🔥 Bhai jab fire aata hai toh sab hatate hain — tujhe bhi hatna chahiye 💀😂",
    "🔥 Fire aaya — teri side pe — enjoy karo 😈⚡",
    "🔥 Beta fire nahi karunga — already ka gaya 💀😂",
    "🔥 BLAZING RESPONSE — teri cheez pe aag — already 😈🔥",
    "🔥 Bhai teri poori chat fire ke baad debris hai 💀⚡",
    "🔥 Fire level MAXIMUM — teri area evacuated 😈😂",
    "🔥 Beta fire se darr — yeh meri territory hai 💀🔥",
    "🔥 FIRE ATTACK RESPONSE — yeh tera last message tha? Nahi? Theek hai 😈⚡",
    "🔥 Bhai fire mein koi nahi bachta — sab jal jaate hain 💀😂",
    "🔥 Teri ego fire pe rakh di — gone in seconds 😈🔥",
    "🔥 Beta fire drop — tujhe rona mat — khud aaya tha 💀⚡",
    "🔥 FIRE FINISHER — teri poori team aag mein 😈😂",
    "🔥 Bhai mere fire ke saamne tera ice melts instantly 💀🔥",
    "🔥 Fire mode — tera surrender nahi aaya? Interesting 😈⚡",
    "🔥 Beta fire se mujhe dar nahi — main fire hoon 💀😂",
    "🔥 BLAZING FURY — teri existence burning 😈🌪️",
    "🔥 Bhai teri shikayat fire pe rakh di — dissolve ho gayi 💀😂",
    "🔥 Fire response — tujhe ek hi chahiye tha — yeh lo 😈⚡",
    "🔥 Beta mere fire se bach ke gaya toh winner — nahi gaya toh obvious 💀🔥",
    "🔥 FIRE FINALE — teri poori side: ashes 😈😂",
    "🔥 Bhai fire mein aake cool lagta hai — tujhe pata nahi 💀⚡",
    "🔥 Teri har weakness fire pe react karti hai — too many reactions 😈😂",
    "🔥 Beta fire mein aana galat tha — par aaya toh hai 💀🔥",
    "🔥 MEGA FIRE RAID — teri timeline pe aaya — stay 😈⚡",
    "🔥 Bhai fire aur tu — bad combination 💀😂",
    "🔥 Fire mode COMPLETE — teri side nothing remaining 😈🌪️",
    "🔥 Beta fire se pehle socha nahi — ab sochta hai par late hai 💀😂",
    "🔥 FIRE STORM COMPLETE — tujhe mujhse distance rakhni chahiye thi 😈⚡",
    "🔥 Bhai fire mein kabhi koi jeet nahi sakta — tu jeetha? Nahi 💀🔥",
    "🔥 Beta teri baat fire pe: ash 😈😂",
    "🔥 FIRE LEVEL OVER 9000 — teri side zero se bhi neeche 💀⚡",
    "🔥 Bhai fire mein aake puchha kya tha? Bhool gaya — fire ne bhula diya 😈😂",
    "🔥 Fire drop FINAL — teri poori team scattered 💀🔥",
    "🔥 Beta fire se bacha nahi — fire ne tujhe dhundha 😈⚡",
    "🔥 🔥 FIRE OVER — teri side: lesson learned? Hope so 💀😂",
]

devil_list = [
    "😈 DEVIL MODE — yahan woh aaya hai jo tujhe deserve karta hai 🔥💀",
    "😈 Beta main devil nahi — main tera worst nightmare hoon 🔥⚡",
    "😈 Devil raid activate — teri poori timeline disturbed 💀😂",
    "😈 Bhai devil pe hath lagaya — ab bhog 🔥💥",
    "😈 DEVIL FURY — teri sab cheez ek baar mein 💀⚡",
    "😈 Beta devil ke saamne hum sab khiladi hain — tu beginner 🔥😂",
    "😈 DEVIL ATTACK — teri defense devil ke touch se fail 💀😈",
    "😈 Bhai devil mode mein koi safe nahi — tu bhi nahi 🔥⚡",
    "😈 Teri galti — devil ko challenge karna 💀😂",
    "😈 Beta devil ki bhasha — punishment aur reward — tu punishment mein hai 🔥😈",
    "😈 DEVIL LEVEL RAGE — teri poori life on line 💀⚡",
    "😈 Bhai devil se lad ke koi nahi jeeta — tu bhi nahi jeetega 🔥😂",
    "😈 Devil mode — tera sab kuch noted — sab 💀😈",
    "😈 Beta DEVIL FIRE — teri poori duniya burn 🔥⚡",
    "😈 DEVIL RAID COMPLETE — tujhe koi nahi bachayega 💀😂",
    "😈 Bhai devil teri har move pe already plan bana chuka 🔥😈",
    "😈 Devil mode — tera future bleak — teri choice thi 💀⚡",
    "😈 Beta devil ne tujhe select kiya — koi bada reason hoga 🔥😂",
    "😈 DEVIL STORM — teri poori squad disbanded 💀😈",
    "😈 Bhai devil ke game mein tera turn tha — abhi mera 🔥⚡",
    "😈 Devil raid engage — now teri responsibility 💀😂",
    "😈 Beta devil level punishment — tujhse tune karaya tha 🔥😈",
    "😈 DEVIL ZONE — nikal ja nahi toh devil ka guest ban 💀⚡",
    "😈 Bhai devil hamesha sunta hai — teri bhi sun li 🔥😂",
    "😈 Devil mode ACTIVATED — teri poori timeline hijacked 💀😈",
    "😈 Beta devil ke saamne sirf ek option — respect ya suffer 🔥⚡",
    "😈 DEVIL FINAL BLOW — teri defense completely gone 💀😂",
    "😈 Bhai devil ne decide kiya — teri loss is inevitable 🔥😈",
    "😈 Devil mein aake dekha — tu deserving nahi tha challenge ka 💀⚡",
    "😈 Beta DEVIL RAIN — teri har cheez soaked in fire 🔥😂",
    "😈 DEVIL vs YOU — spoiler: devil wins 💀😈",
    "😈 Bhai devil ke saamne teri prayers bhi kaam nahi aate 🔥⚡",
    "😈 Devil mode — teri weak spots identified — attack 💀😂",
    "😈 Beta devil ki nazar se tu nahi chhupta 🔥😈",
    "😈 DEVIL JUDGMENT — teri poori history reviewed — verdict: guilty 💀⚡",
    "😈 Bhai devil ki duniya mein tu tourist tha — time up 🔥😂",
    "😈 Devil fury — tere steps already tracked hain 💀😈",
    "😈 Beta DEVIL COUNTER — teri har move ka counter ready tha 🔥⚡",
    "😈 DEVIL FINISH — teri game over — my game continues 💀😂",
    "😈 Bhai devil mode se nikalna — tujhe option nahi 🔥😈",
    "😈 Devil attack — teri soul targeted — figuratively 💀⚡",
    "😈 Beta devil ne kaha — teri aukat nahi — aur devil galat nahi hota 🔥😂",
    "😈 DEVIL STORM OVER — teri side: scorched earth 💀😈",
    "😈 Bhai devil ke rules simple hain — tu follow nahi kiya 🔥⚡",
    "😈 Devil raid — teri position compromised — retreat 💀😂",
    "😈 Beta DEVIL mein aake rota mat — khud aaya tha 🔥😈",
    "😈 DEVIL WAVE — teri har defence erased 💀⚡",
    "😈 Bhai devil ka favorite — log jo khud ko smart samjhte hain — tu 🔥😂",
    "😈 Devil mode DONE — check teri condition 💀😈",
    "😈 Beta devil ne aaj tujhe yaadgaar bana diya — wrong reasons se 🔥⚡",
]

karma_list = [
    "☯️ Karma aaya — teri sab harkat ka hisaab ho raha hai 🔥💀",
    "☯️ Beta karma kisi ki nahi sunta — teri bhi nahi 😂⚡",
    "☯️ KARMA STRIKE — tune jo kiya woh teri taraf wapas aaya 🔥😈",
    "☯️ Bhai karma judge nahi karta — deliver karta hai 💀😂",
    "☯️ Karma mode activate — teri sab galtiyan wapas aa rahi hain 🔥⚡",
    "☯️ Beta karma tujhe bhool nahi gaya — yaad rakha tha 😂💀",
    "☯️ KARMA DELIVERY — teri harkat ka package arrive ho gaya 🔥😈",
    "☯️ Bhai karma se koi nahi bachta — tu bhi nahi bachega 💀⚡",
    "☯️ Karma tujhe dhundh raha tha — dhundh liya 🔥😂",
    "☯️ Beta karma aata hai jab expect nahi karte — sun le 😂💀",
    "☯️ KARMA HITS DIFFERENT — teri sab cheez wapas 🔥⚡",
    "☯️ Bhai karma teri priority nahi thi — karma mein tu priority hai 😂💀",
    "☯️ Karma cycle complete — tune jo kiya tune hi bhoga 🔥😈",
    "☯️ Beta karma slow hota hai par sure hota hai — yeh sure tha 💀⚡",
    "☯️ KARMA CALL — teri line pe aa gaya 🔥😂",
    "☯️ Bhai karma mein koi error nahi — teri galti recorded thi 😂💀",
    "☯️ Karma teri taraf waapis — enjoy 🔥⚡",
    "☯️ Beta karma tera address jaanta tha 😂💀",
    "☯️ KARMA FINAL — teri poori account balance zero 🔥😈",
    "☯️ Bhai karma se lad nahi sakte — tu chhupa nahi karma se 💀⚡",
    "☯️ Karma strike — tune deserve kiya — mila 🔥😂",
    "☯️ Beta karma ko excuse nahi deta — sirf result deta hai 😂💀",
    "☯️ KARMA STORM — teri sab beizzati aaj ekatha aayi 🔥⚡",
    "☯️ Bhai karma tujhse behtar account maintain karta hai 😂💀",
    "☯️ Karma mein tera account — overdraft mein hai 🔥😈",
    "☯️ Beta karma ki speed teri speed se faster hai 💀⚡",
    "☯️ KARMA BLAST — teri sab cheezon ka hisaab 🔥😂",
    "☯️ Bhai karma ko pata tha tune kya kiya — sab record mein hai 😂💀",
    "☯️ Karma kisi pe bhi nahi rulta — teri bhi nahi 🔥⚡",
    "☯️ Beta karma tera future nahi — karma tera present hai 😂💀",
    "☯️ KARMA INVOICE — teri sab galtiyon ka bill aa gaya 🔥😈",
    "☯️ Bhai karma mein koi discount nahi milta — full price pay 💀⚡",
    "☯️ Karma delivered — tune jo bheja wahi mila 🔥😂",
    "☯️ Beta karma tujhse kisi ki nahi sunta — seedha deliver karta hai 😂💀",
    "☯️ KARMA FULL CIRCLE — teri sab harkat ghumke teri hi taraf aayi 🔥⚡",
    "☯️ Bhai karma teri taraf — aur tu prepared nahi tha 😂💀",
    "☯️ Karma hit kiya — tujhe pata tha aayega — aaya 🔥😈",
    "☯️ Beta karma mein interest bhi hota hai — tera compound ho gaya 💀⚡",
    "☯️ KARMA COMPLETE — lesson mila? 🔥😂",
    "☯️ Bhai karma ne tujhe select kiya — deservingly 😂💀",
    "☯️ Karma tujhe yaad dila raha hai — tune kya kiya tha 🔥⚡",
    "☯️ Beta karma ki awaaz nahi hoti — par result loud hota hai 😂💀",
    "☯️ KARMA RESPONSE — teri har cheez ka seedha jawab 🔥😈",
    "☯️ Bhai karma ki list mein tu first position pe tha 💀⚡",
    "☯️ Karma tujhe bhool nahi gaya — teri galti note thi 🔥😂",
    "☯️ Beta karma aur tu — aaj inka meetup schedule tha 😂💀",
    "☯️ KARMA WRAP UP — teri life lesson: yeh tha 🔥⚡",
    "☯️ Bhai karma ne apna kaam kiya — efficient tha 😂💀",
    "☯️ Karma strike final — teri sab cheez balanced ho gayi — zero pe 🔥😈",
    "☯️ Beta karma yaad rakhna — abhi bhi teri account open hai ☯️😂",
]

ghost_list = [
    "👻 GHOST MODE — tujhe pata bhi nahi kab aaya 😂💀",
    "👻 Beta ghost ki tarah silently teri sab cheez note kar liya 🔥😈",
    "👻 GHOST RAID — teri timeline pe tha tu socha nahi 💀⚡",
    "👻 Bhai ghost mode mein sab kuch possible hai — teri nazar se baahar 😂🔥",
    "👻 Ghost strike — teri sab cheez read — tujhe pata nahi 💀😈",
    "👻 Beta ghost se koi nahi chhupta — teri history meri hai 😂⚡",
    "👻 GHOST ATTACK — teri weaknesses identified without you knowing 🔥💀",
    "👻 Bhai ghost mein aaya — teri sab dekha — wapas aaya 😈😂",
    "👻 Ghost mode — tu sooye hua tha main active tha 💀⚡",
    "👻 Beta ghost ki tarah aa aur ja — par lesson chhod 🔥😂",
    "👻 GHOST OBSERVATION — teri sab cheez monitored 💀😈",
    "👻 Bhai ghost ne sab dekha — teri harkaten recorded 😂⚡",
    "👻 Ghost strike final — teri poori plan exposed 🔥💀",
    "👻 Beta ghost mode mein tera koi secret nahi raha 😈😂",
    "👻 GHOST RAID COMPLETE — teri sab cheez ghost ke paas 💀⚡",
    "👻 Bhai ghost tujhse zyada mobile tha 🔥😂",
    "👻 Ghost ne teri sab sun li — seedha sun li 💀😈",
    "👻 Beta ghost se koi hidden nahi — tera bhi nahi 😂⚡",
    "👻 GHOST FINAL — teri sab expose ho gayi silently 🔥💀",
    "👻 Bhai ghost mein ek power hai — invisibility — jo tujhpe use ki 😈😂",
    "👻 Ghost mode — teri baat sun ke ghost ne judge kiya 💀⚡",
    "👻 Beta ghost aaya aur teri sab cheez log kar ke gaya 🔥😂",
    "👻 GHOST PRESENCE — tu feel kar sakta hai par dekh nahi sakta 💀😈",
    "👻 Bhai ghost ne tujhe 24/7 observe kiya — teri knowledge ke bina 😂⚡",
    "👻 Ghost strike — teri poori defense bypass ho gayi 🔥💀",
    "👻 Beta ghost report taiyaar hai — teri life ka full audit 😈😂",
    "👻 GHOST RETURN — wapas aaya — aur tujhe leke ja raha hoon 💀⚡",
    "👻 Bhai ghost ki tarah — nazar nahi aaya par haraaya zaroor 🔥😂",
    "👻 Ghost mode — teri conversations screenshotted 💀😈",
    "👻 Beta ghost ke saamne teri poori timeline open book 😂⚡",
    "👻 GHOST DAMAGE — tujhe pata bhi nahi kya hua 🔥💀",
    "👻 Bhai ghost ki speed mein teri poori history read 😈😂",
    "👻 Ghost raid — teri sab log ki gayi 💀⚡",
    "👻 Beta ghost tujhse pehle arrive kiya — always 🔥😂",
    "👻 GHOST NETWORK — teri sab moves already anticipated 💀😈",
    "👻 Bhai ghost ne tujhe dost banaya — tujhe pata hi nahi chala 😂⚡",
    "👻 Ghost mode complete — teri sab information gathered 🔥💀",
    "👻 Beta ghost tera shadow tha — teri knowledge ke bina 😈😂",
    "👻 GHOST INTEL — teri ek bhi move safe nahi thi 💀⚡",
    "👻 Bhai ghost ke saamne tera defense transparent tha 🔥😂",
    "👻 Ghost final message — sun le — yeh tha 💀😈",
    "👻 Beta ghost raid done — teri sab cheez: compromised 😂⚡",
    "👻 GHOST VANISH — gaya aur teri legacy chhod gaya — for the wrong reasons 🔥💀",
    "👻 Bhai ghost teri poori situation samajh gaya — tu abhi samjha 😈😂",
    "👻 Ghost mode — tera sab kuch pehle se predict tha 💀⚡",
    "👻 Beta ghost ki tarah observe kiya — teri sab weakness note 🔥😂",
    "👻 GHOST COMPLETE — teri poori profile analyzed — done 💀😈",
    "👻 Bhai ghost ne tujhe deliver kiya — message: tu predictable hai 😂⚡",
    "👻 Ghost raid FINAL — enjoy the lesson 🔥💀",
    "👻 Beta ghost ne sun liya — ab teri galti public domain mein hai 😈😂",
]

legend_list = [
    "👑 LEGEND MODE — tujhse baat karna mera time nahi — par exception 😎🔥",
    "👑 Beta legend ne tujhe notice kiya — galat kaam ke liye 😂💀",
    "👑 LEGEND STRIKE — teri poori position legend ne handle ki 😎⚡",
    "👑 Bhai legend ke saamne teri sab bakwaas — sirf noise 🔥😂",
    "👑 Legend mode — main aaya — tu already haara 😎💀",
    "👑 Beta LEGEND level pe tu exist nahi karta — par exception de raha hoon 😂⚡",
    "👑 LEGEND RAID — teri timeline pe aaya — yaad rahega 🔥😎",
    "👑 Bhai legend se lad ke jeeta kaun? Koi nahi — tu bhi nahi 💀😂",
    "👑 Legend status — tujhe challenge accept nahi karna tha 😎⚡",
    "👑 Beta legend aaya — teri poori squad bhaag gayi 🔥💀",
    "👑 LEGEND BLOW — teri defense — gone 😎😂",
    "👑 Bhai legend ki speed se teri situation analyze ho gayi 🔥⚡",
    "👑 Legend mode on — teri har move already countered 😎💀",
    "👑 Beta LEGEND ka ek rule — woh kabhi lose nahi karta 😂⚡",
    "👑 LEGEND FINISH — teri poori war — legend ki morning exercise thi 🔥😎",
    "👑 Bhai legend ko insult karna — teri worst idea thi 💀😂",
    "👑 Legend ne tujhe acknowledge kiya — that's it — teri privilege khatam 😎⚡",
    "👑 Beta legend ki taraf se — teri sab cheez ka answer: nahi 🔥💀",
    "👑 LEGEND STRIKE FINAL — teri poori side — taken care of 😎😂",
    "👑 Bhai legend se panga — teri bravery ya foolishness? 💀⚡",
    "👑 Legend mode — teri sab galtiyan noted — teri 🔥😎",
    "👑 Beta LEGEND ki baat sun — yeh advice nahi — judgment hai 😂💀",
    "👑 LEGEND RAID COMPLETE — tu ek example ban gaya — negative wala 😎⚡",
    "👑 Bhai legend ke saamne baat karte waqt soch lena tha 🔥😂",
    "👑 Legend status confirm — teri side: unconfirmed 💀😎",
    "👑 Beta LEGEND ne tujhpe ek second spend kiya — teri lucky day thi 😂⚡",
    "👑 LEGEND FURY — teri har defense melt 🔥😎",
    "👑 Bhai legend ka level dekh — aur apna dekh — gap samjha? 💀😂",
    "👑 Legend mode final — teri sab cheez — reviewed — rejected 😎⚡",
    "👑 Beta LEGEND mein sirf ek rule — excellence — teri cheez nahi 🔥💀",
    "👑 LEGEND FINAL MESSAGE — yahi tha — good luck 😎😂",
    "👑 Bhai legend se lad ke teri position — worse than before 💀⚡",
    "👑 Legend raid final wave — teri sab gone 🔥😎",
    "👑 Beta LEGEND ki mercy — tujhe yahan tak aane diya — bas 😂💀",
    "👑 LEGEND COMPLETE — teri story: cautionary tale ban gayi 😎⚡",
    "👑 Bhai legend ne tujhe ek lesson diya — free of charge 🔥😂",
    "👑 Legend mode — tu ek footnote hai meri history mein 💀😎",
    "👑 Beta LEGEND ka visit — teri timeline ka highlight — wrong reasons se 😂⚡",
    "👑 LEGEND OVER — teri war: history — meri war: ongoing 🔥😎",
    "👑 Bhai legend ke saamne tera struggle cute lagta hai 💀😂",
    "👑 Legend mode engaged — tujhe pata bhi nahi kab hua 😎⚡",
    "👑 Beta LEGEND ne tujhe prove kiya — teri theory wrong thi 🔥💀",
    "👑 LEGEND VERDICT — teri poori existence: could do better 😎😂",
    "👑 Bhai legend se seekh — agar seekh sakta hai 💀⚡",
    "👑 Legend raid — teri poori team acknowledged defeat 🔥😎",
    "👑 Beta LEGEND tujhe seriously leta nahi — par professionally handle karta hai 😂💀",
    "👑 LEGEND STAMP — teri chat: closed — meri: continuing 😎⚡",
    "👑 Bhai legend ne tujhe ek cheez diya — perspective — use kar 🔥😂",
    "👑 Legend mode OVER — teri loss: recorded — teri lesson: pending 💀😎",
    "👑 Beta LEGEND ki baat seedhi — tu meri league mein nahi — abhi 😂⚡",
]

doom_list = [
    "💀 DOOM activated — teri poori existence on countdown 🔥😈",
    "💀 Beta doom aaya — tera timer start ho gaya 😂⚡",
    "💀 DOOM STRIKE — teri poori defense wiped 🔥😈",
    "💀 Bhai doom se koi nahi bachta — teri bhi date aane wali thi 😂💀",
    "💀 Doom mode — teri sab cheez: scheduled for deletion 🔥⚡",
    "💀 Beta doom tera waqt dekh ke aaya — perfect timing 😂😈",
    "💀 DOOM RAID — teri poori squad: doomed 🔥💀",
    "💀 Bhai doom pe haath lagaya — yeh result expect karna chahiye tha 😂⚡",
    "💀 Doom finale — teri poori story: ended 🔥😈",
    "💀 Beta doom ki awaaz sunna nahi chahte log — teri aa gayi 😂💀",
    "💀 DOOM COMPLETE — teri sab cheez: finished 🔥⚡",
    "💀 Bhai doom tujhse pehle plan kar ke aaya tha 😂😈",
    "💀 Doom level CRITICAL — teri situation: hopeless 🔥💀",
    "💀 Beta doom ne tujhe select kiya — teri achievement nahi 😂⚡",
    "💀 DOOM COUNTDOWN — teri sab cheez: 3... 2... 1... done 🔥😈",
    "💀 Bhai doom mein rasta ek hi hota hai — neeche 😂💀",
    "💀 Doom activated — teri poori future: uncertain 🔥⚡",
    "💀 Beta doom ki language — teri samajh nahi aati — result aata hai 😂😈",
    "💀 DOOM FINAL — teri poori team: gone 🔥💀",
    "💀 Bhai doom aur tu — aaj ka meetup tera worst tha 😂⚡",
    "💀 Doom mode — tera har step: tracked 🔥😈",
    "💀 Beta doom ne teri position: permanent zero confirm ki 😂💀",
    "💀 DOOM RAIN — teri har cheez: destroyed 🔥⚡",
    "💀 Bhai doom mein mercy nahi hoti — teri request: denied 😂😈",
    "💀 Doom strike — teri sab galtiyan: collected 🔥💀",
    "💀 Beta doom clock — teri ticking: started 😂⚡",
    "💀 DOOM WAVE — teri poori defense: overwhelmed 🔥😈",
    "💀 Bhai doom ki speed mein teri situation resolve ho gayi — badly 😂💀",
    "💀 Doom verdict — teri case: closed — against you 🔥⚡",
    "💀 Beta doom se pehle sun: teri galti — doom aaya 😂😈",
    "💀 DOOM ARRIVAL — teri poori day ruined 🔥💀",
    "💀 Bhai doom ne tujhe apna project bana liya 😂⚡",
    "💀 Doom mode final — teri sab cheez: ash 🔥😈",
    "💀 Beta doom ki ek khasiyat — woh aata zaroor hai 😂💀",
    "💀 DOOM EXECUTION — teri poori plan: failed 🔥⚡",
    "💀 Bhai doom tera number leke aaya tha — mila 😂😈",
    "💀 Doom level MAX — teri recovery: impossible 🔥💀",
    "💀 Beta doom ki taraf se ek gift — teri haari 😂⚡",
    "💀 DOOM COMPLETE CYCLE — teri poori existence reset 🔥😈",
    "💀 Bhai doom tujhse better hai — wait nahi karta 😂💀",
    "💀 Doom mode — teri sab cheez: compromised 🔥⚡",
    "💀 Beta DOOM aur tu — tujhe jeetna tha par doom ka hi naam hai 😂😈",
    "💀 DOOM FINAL WAVE — teri sab: erased 🔥💀",
    "💀 Bhai doom ne tujhe memorable bana diya — galat reasons se 😂⚡",
    "💀 Doom activated final time — teri countdown: zero 🔥😈",
    "💀 Beta DOOM se seekhna tha — tujhe nahi tha pata ab hai 😂💀",
    "💀 DOOM OVER — teri side: collapsed — mine: standing 🔥⚡",
    "💀 Bhai doom ne tera chapter likh diya — R.I.P. chapter 😂😈",
    "💀 Doom final message — tujhe yaad rahega — sahi reasons se nahi 🔥💀",
    "💀 Beta DOOM complete — check teri condition — yahi tha 😂⚡",
]

nuke_list = [
    "☢️ NUKE LAUNCHED — teri poori existence vapas nahi aayegi 💀🔥",
    "💥 Nuke strike — teri sab cheez radiated hai 😈⚡",
    "☢️ Beta nuke aaya — tera timer ab 0 pe hai 😂💀",
    "💥 NUKE FURY — teri poori timeline erased 🔥😈",
    "☢️ Nuke mode — teri har move fail hogi 💀⚡",
    "💥 Beta nuke se koi nahi bachta — tu bhi nahi 😂😈",
    "☢️ NUKE IMPACT — teri sab cheez dust 💀🔥",
    "💥 Bhai nuke ka effect — teri maa bhi nahi pehchanegi 😂⚡",
    "☢️ Nuke activated — teri har reply waste hai 💀😈",
    "💥 Beta nuke ki speed — tu soch bhi nahi sakta 😂🔥",
    "☢️ NUKE RAIN — teri chat mein sab khatam 💀⚡",
    "💥 Bhai nuke mein ek hi rule — teri haari 😈😂",
    "☢️ Nuke over — teri side zero pe 💀🔥",
    "💥 Beta nuke ka proof — tu ab yahan nahi 😂⚡",
    "☢️ NUKE STRIKE — teri poori squad vaporized 💀😈",
    "💥 Bhai nuke pe haath lagaya — ab koi nahi bachega 😂🔥",
    "☢️ Nuke mode — teri sab expectations destroyed 💀⚡",
    "💥 Beta nuke aur tu — dono mein farak hai 😈😂",
    "☢️ NUKE FINAL — teri war khatam 💀🔥",
    "💥 Bhai nuke ne tujhe lesson diya — permanent 😂⚡",
    "☢️ Nuke complete — teri koi baat nahi 💀😈",
    "💥 Beta nuke ki awaaz — teri baaton se louder 😂🔥",
    "☢️ NUKE BLAST — teri har cheez wiped 💀⚡",
    "💥 Bhai nuke ne tujhe reset kiya — version 0 😈😂",
    "☢️ Nuke attack — teri koi strategy kaam nahi 💀🔥",
    "💥 Beta nuke se pehle bolna tha — ab nahi 😂⚡",
    "☢️ NUKE OVERDRIVE — teri poori timeline corrupted 💀😈",
    "💥 Bhai nuke ka result — teri side gone 😂🔥",
    "☢️ Nuke strike final — teri maa bhi roegi 💀⚡",
    "💥 Beta nuke aur main — dono same nahi 😈😂",
    "☢️ NUKE MODE ON — teri sab cheez 0 pe 💀🔥",
    "💥 Bhai nuke se darr — par ab der hai 😂⚡",
    "☢️ Nuke rain complete — teri koi recovery nahi 💀😈",
    "💥 Beta nuke ki guarantee — teri haari 😂🔥",
    "☢️ NUKE POWER — teri poori squad silent 💀⚡",
    "💥 Bhai nuke ne tujhe target kiya — reason nahi 😈😂",
    "☢️ Nuke verdict — teri case closed 💀🔥",
    "💥 Beta nuke aaya aur gaya — tu nahi gaya 😂⚡",
    "☢️ NUKE DAMAGE — teri profile 0 pe 💀😈",
    "💥 Bhai nuke ka impact — teri soch se bada 😂🔥",
    "☢️ Nuke finish — teri side: nothing 💀⚡",
    "💥 Beta nuke ne tujhe replace kiya — khud 😈😂",
    "☢️ NUKE END — teri war khatam teri taraf se 💀🔥",
    "💥 Bhai nuke ka ek rule — tu nahi bachega 😂⚡",
    "☢️ Nuke final wave — teri har defense fail 💀😈",
    "💥 Beta nuke ne sab khatam kiya — tera bhi 😂🔥",
    "☢️ NUKE COMPLETE — teri existence erased 💀⚡",
    "💥 Bhai nuke se seekh — tu abhi bhi nahi 😈😂",
    "☢️ Nuke over — teri side gone forever 💀🔥",
    "💥 Beta nuke ki taraf se — bye bye 😂⚡",
]

storm_list = [
    "🌪️ STORM MODE — teri poori chat mein andhi 😈🔥",
    "⚡ Storm attack — teri har baat blown away 💀😂",
    "🌪️ Beta storm aaya — tera sab kuch scattered 😈⚡",
    "⚡ STORM FURY — teri poori timeline broken 🔥💀",
    "🌪️ Storm mode — teri koi move nahi chalegi 😂😈",
    "⚡ Beta storm se koi nahi bachta — teri bhi nahi 💀🔥",
    "🌪️ STORM IMPACT — teri sab cheez air mein 😈⚡",
    "⚡ Bhai storm ka effect — teri maa bhi shock mein 😂💀",
    "🌪️ Storm activated — teri har reply waste 🔥😈",
    "⚡ Beta storm ki speed — tu soch bhi nahi sakta 💀😂",
    "🌪️ STORM RAIN — teri chat mein sab kuch flying 😈⚡",
    "⚡ Bhai storm mein ek hi rule — teri haari 🔥😂",
    "🌪️ Storm over — teri side zero pe 💀😈",
    "⚡ Beta storm ka proof — tu ab yahan nahi 😂🔥",
    "🌪️ STORM STRIKE — teri poori squad blown 😈⚡",
    "⚡ Bhai storm pe haath lagaya — ab koi nahi bachega 💀😂",
    "🌪️ Storm mode — teri sab expectations destroyed 🔥😈",
    "⚡ Beta storm aur tu — dono mein farak hai 💀😂",
    "🌪️ STORM FINAL — teri war khatam 😈🔥",
    "⚡ Bhai storm ne tujhe lesson diya — permanent 💀😂",
    "🌪️ Storm complete — teri koi baat nahi 🔥😈",
    "⚡ Beta storm ki awaaz — teri baaton se louder 💀😂",
    "🌪️ STORM BLAST — teri har cheez wiped 😈🔥",
    "⚡ Bhai storm ne tujhe reset kiya — version 0 💀😂",
    "🌪️ Storm attack — teri koi strategy kaam nahi 🔥😈",
    "⚡ Beta storm se pehle bolna tha — ab nahi 💀😂",
    "🌪️ STORM OVERDRIVE — teri poori timeline corrupted 😈🔥",
    "⚡ Bhai storm ka result — teri side gone 💀😂",
    "🌪️ Storm strike final — teri maa bhi roegi 🔥😈",
    "⚡ Beta storm aur main — dono same nahi 💀😂",
    "🌪️ STORM MODE ON — teri sab cheez 0 pe 😈🔥",
    "⚡ Bhai storm se darr — par ab der hai 💀😂",
    "🌪️ Storm rain complete — teri koi recovery nahi 🔥😈",
    "⚡ Beta storm ki guarantee — teri haari 💀😂",
    "🌪️ STORM POWER — teri poori squad silent 😈🔥",
    "⚡ Bhai storm ne tujhe target kiya — reason nahi 💀😂",
    "🌪️ Storm verdict — teri case closed 🔥😈",
    "⚡ Beta storm aaya aur gaya — tu nahi gaya 💀😂",
    "🌪️ STORM DAMAGE — teri profile 0 pe 😈🔥",
    "⚡ Bhai storm ka impact — teri soch se bada 💀😂",
    "🌪️ Storm finish — teri side: nothing 🔥😈",
    "⚡ Beta storm ne tujhe replace kiya — khud 💀😂",
    "🌪️ STORM END — teri war khatam teri taraf se 😈🔥",
    "⚡ Bhai storm ka ek rule — tu nahi bachega 💀😂",
    "🌪️ Storm final wave — teri har defense fail 🔥😈",
    "⚡ Beta storm ne sab khatam kiya — tera bhi 💀😂",
    "🌪️ STORM COMPLETE — teri existence erased 😈🔥",
    "⚡ Bhai storm se seekh — tu abhi bhi nahi 💀😂",
    "🌪️ Storm over — teri side gone forever 🔥😈",
    "⚡ Beta storm ki taraf se — bye bye 💀😂",
]

blizzard_list = [
    "❄️ BLIZZARD MODE — teri poori chat frozen 😈🔥",
    "🧊 Blizzard attack — teri har baat ice mein 💀😂",
    "❄️ Beta blizzard aaya — tera sab kuch jam 😈⚡",
    "🧊 BLIZZARD FURY — teri poori timeline blocked 🔥💀",
    "❄️ Blizzard mode — teri koi move nahi chalegi 😂😈",
    "🧊 Beta blizzard se koi nahi bachta — teri bhi nahi 💀🔥",
    "❄️ BLIZZARD IMPACT — teri sab cheez frozen 😈⚡",
    "🧊 Bhai blizzard ka effect — teri maa bhi thandi 💀😂",
    "❄️ Blizzard activated — teri har reply waste 🔥😈",
    "🧊 Beta blizzard ki speed — tu soch bhi nahi sakta 💀😂",
    "❄️ BLIZZARD RAIN — teri chat mein sab kuch jam 😈⚡",
    "🧊 Bhai blizzard mein ek hi rule — teri haari 🔥😂",
    "❄️ Blizzard over — teri side zero pe 💀😈",
    "🧊 Beta blizzard ka proof — tu ab yahan nahi 😂🔥",
    "❄️ BLIZZARD STRIKE — teri poori squad frozen 😈⚡",
    "🧊 Bhai blizzard pe haath lagaya — ab koi nahi bachega 💀😂",
    "❄️ Blizzard mode — teri sab expectations destroyed 🔥😈",
    "🧊 Beta blizzard aur tu — dono mein farak hai 💀😂",
    "❄️ BLIZZARD FINAL — teri war khatam 😈🔥",
    "🧊 Bhai blizzard ne tujhe lesson diya — permanent 💀😂",
    "❄️ Blizzard complete — teri koi baat nahi 🔥😈",
    "🧊 Beta blizzard ki awaaz — teri baaton se louder 💀😂",
    "❄️ BLIZZARD BLAST — teri har cheez wiped 😈🔥",
    "🧊 Bhai blizzard ne tujhe reset kiya — version 0 💀😂",
    "❄️ Blizzard attack — teri koi strategy kaam nahi 🔥😈",
    "🧊 Beta blizzard se pehle bolna tha — ab nahi 💀😂",
    "❄️ BLIZZARD OVERDRIVE — teri poori timeline corrupted 😈🔥",
    "🧊 Bhai blizzard ka result — teri side gone 💀😂",
    "❄️ Blizzard strike final — teri maa bhi roegi 🔥😈",
    "🧊 Beta blizzard aur main — dono same nahi 💀😂",
    "❄️ BLIZZARD MODE ON — teri sab cheez 0 pe 😈🔥",
    "🧊 Bhai blizzard se darr — par ab der hai 💀😂",
    "❄️ Blizzard rain complete — teri koi recovery nahi 🔥😈",
    "🧊 Beta blizzard ki guarantee — teri haari 💀😂",
    "❄️ BLIZZARD POWER — teri poori squad silent 😈🔥",
    "🧊 Bhai blizzard ne tujhe target kiya — reason nahi 💀😂",
    "❄️ Blizzard verdict — teri case closed 🔥😈",
    "🧊 Beta blizzard aaya aur gaya — tu nahi gaya 💀😂",
    "❄️ BLIZZARD DAMAGE — teri profile 0 pe 😈🔥",
    "🧊 Bhai blizzard ka impact — teri soch se bada 💀😂",
    "❄️ Blizzard finish — teri side: nothing 🔥😈",
    "🧊 Beta blizzard ne tujhe replace kiya — khud 💀😂",
    "❄️ BLIZZARD END — teri war khatam teri taraf se 😈🔥",
    "🧊 Bhai blizzard ka ek rule — tu nahi bachega 💀😂",
    "❄️ Blizzard final wave — teri har defense fail 🔥😈",
    "🧊 Beta blizzard ne sab khatam kiya — tera bhi 💀😂",
    "❄️ BLIZZARD COMPLETE — teri existence erased 😈🔥",
    "🧊 Bhai blizzard se seekh — tu abhi bhi nahi 💀😂",
    "❄️ Blizzard over — teri side gone forever 🔥😈",
    "🧊 Beta blizzard ki taraf se — bye bye 💀😂",
]

venom_list = [
    "☠️ VENOM MODE — teri poori chat poisonous 😈🔥",
    "🐍 Venom attack — teri har baat toxic 💀😂",
    "☠️ Beta venom aaya — tera sab kuch infected 😈⚡",
    "🐍 VENOM FURY — teri poori timeline corrupted 🔥💀",
    "☠️ Venom mode — teri koi move nahi chalegi 😂😈",
    "🐍 Beta venom se koi nahi bachta — teri bhi nahi 💀🔥",
    "☠️ VENOM IMPACT — teri sab cheez poison 😈⚡",
    "🐍 Bhai venom ka effect — teri maa bhi sick 💀😂",
    "☠️ Venom activated — teri har reply waste 🔥😈",
    "🐍 Beta venom ki speed — tu soch bhi nahi sakta 💀😂",
    "☠️ VENOM RAIN — teri chat mein sab kuch toxic 😈⚡",
    "🐍 Bhai venom mein ek hi rule — teri haari 🔥😂",
    "☠️ Venom over — teri side zero pe 💀😈",
    "🐍 Beta venom ka proof — tu ab yahan nahi 😂🔥",
    "☠️ VENOM STRIKE — teri poori squad poisoned 😈⚡",
    "🐍 Bhai venom pe haath lagaya — ab koi nahi bachega 💀😂",
    "☠️ Venom mode — teri sab expectations destroyed 🔥😈",
    "🐍 Beta venom aur tu — dono mein farak hai 💀😂",
    "☠️ VENOM FINAL — teri war khatam 😈🔥",
    "🐍 Bhai venom ne tujhe lesson diya — permanent 💀😂",
    "☠️ Venom complete — teri koi baat nahi 🔥😈",
    "🐍 Beta venom ki awaaz — teri baaton se louder 💀😂",
    "☠️ VENOM BLAST — teri har cheez wiped 😈🔥",
    "🐍 Bhai venom ne tujhe reset kiya — version 0 💀😂",
    "☠️ Venom attack — teri koi strategy kaam nahi 🔥😈",
    "🐍 Beta venom se pehle bolna tha — ab nahi 💀😂",
    "☠️ VENOM OVERDRIVE — teri poori timeline corrupted 😈🔥",
    "🐍 Bhai venom ka result — teri side gone 💀😂",
    "☠️ Venom strike final — teri maa bhi roegi 🔥😈",
    "🐍 Beta venom aur main — dono same nahi 💀😂",
    "☠️ VENOM MODE ON — teri sab cheez 0 pe 😈🔥",
    "🐍 Bhai venom se darr — par ab der hai 💀😂",
    "☠️ Venom rain complete — teri koi recovery nahi 🔥😈",
    "🐍 Beta venom ki guarantee — teri haari 💀😂",
    "☠️ VENOM POWER — teri poori squad silent 😈🔥",
    "🐍 Bhai venom ne tujhe target kiya — reason nahi 💀😂",
    "☠️ Venom verdict — teri case closed 🔥😈",
    "🐍 Beta venom aaya aur gaya — tu nahi gaya 💀😂",
    "☠️ VENOM DAMAGE — teri profile 0 pe 😈🔥",
    "🐍 Bhai venom ka impact — teri soch se bada 💀😂",
    "☠️ Venom finish — teri side: nothing 🔥😈",
    "🐍 Beta venom ne tujhe replace kiya — khud 💀😂",
    "☠️ VENOM END — teri war khatam teri taraf se 😈🔥",
    "🐍 Bhai venom ka ek rule — tu nahi bachega 💀😂",
    "☠️ Venom final wave — teri har defense fail 🔥😈",
    "🐍 Beta venom ne sab khatam kiya — tera bhi 💀😂",
    "☠️ VENOM COMPLETE — teri existence erased 😈🔥",
    "🐍 Bhai venom se seekh — tu abhi bhi nahi 💀😂",
    "☠️ Venom over — teri side gone forever 🔥😈",
    "🐍 Beta venom ki taraf se — bye bye 💀😂",
]

# (End of text lists)

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
