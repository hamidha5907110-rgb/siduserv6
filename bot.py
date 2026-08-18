#!/usr/bin/env python3
# ════════════════════════════════════════════════════════════════════
#   SID PREMIUM HOSTER + USERBOT CORE V3 — MERGED SINGLE FILE
#   By SIDxBOT — All rights reserved
# ════════════════════════════════════════════════════════════════════
#
#  HOW TO RUN:
#    Hoster bot  →  python sid_bot.py
#    Userbot     →  python sid_bot.py --userbot   (called by hoster)
#
#  REQUIRED ENV VARS (hoster mode):
#    BOT_TOKEN, OWNER_ID, TELEGRAM_API_ID, TELEGRAM_API_HASH
#    SUPPORT_USERNAME  (e.g. @YourUsername)
#    MAX_USERBOTS      (optional, default 50)
#
#  The hoster spawns userbot subprocesses of this same file automatically.
#  No manual --userbot flag needed — just set env vars and run.
# ════════════════════════════════════════════════════════════════════

import sys as _sys
import os as _os

_IS_USERBOT = "--userbot" in _sys.argv or _os.environ.get("USERBOT_MODE") == "1"

if _IS_USERBOT:
    #BY SIDxBOT — ADVANCED V3 (500+ COMMANDS)
    # Modified for SID Premium Hoster — reads credentials from ENV

    # ────────────────────────────────────────────────
    #                 STANDARD LIB
    # ────────────────────────────────────────────────
    import asyncio
    import os
    import time
    import json
    import random
    import logging
    import traceback
    import re
    import hashlib
    import base64
    import uuid
    import string
    import math
    from typing import Dict, Set, Optional
    from io import BytesIO
    from datetime import datetime

    # ────────────────────────────────────────────────
    #                 THIRD PARTY
    # ────────────────────────────────────────────────
    import requests
    import qrcode
    from gtts import gTTS
    import yt_dlp

    # ────────────────────────────────────────────────
    #                 TELETHON
    # ────────────────────────────────────────────────
    from telethon import TelegramClient, events, functions, types
    from telethon.sessions import StringSession
    from telethon.errors import FloodWaitError, RPCError

    # ────────────────────────────────────────────────
    #                 BASIC PATH SETUP
    # ────────────────────────────────────────────────
    BASE_DIR = os.getcwd()
    DOWNLOAD_PATH = os.path.join(BASE_DIR, "downloads")
    os.makedirs(DOWNLOAD_PATH, exist_ok=True)
    TEMP_PATH = os.path.join(BASE_DIR, "temp")
    os.makedirs(TEMP_PATH, exist_ok=True)

    # ────────────────────────────────────────────────
    #        USERBOT CONFIG — read from environment
    # ────────────────────────────────────────────────
    _api_id_raw = os.environ.get("API_ID", "")
    _api_hash_raw = os.environ.get("API_HASH", "")
    _session_str = os.environ.get("SESSION_STRING", "")

    if not _api_id_raw or not _api_hash_raw or not _session_str:
        raise RuntimeError(
            "Missing required env vars: API_ID, API_HASH, SESSION_STRING"
        )

    API_ID = int(_api_id_raw)
    API_HASH = _api_hash_raw
    # OWNER_ID is set at startup to me.id (the actual logged-in account)
    # so ONLY that Telegram account can use commands — no one else
    OWNER_ID: int = 0

    # ── SELF PROTECTION ──────────────────────────────────────────────────
    # PROTECTED_IDS = IDs that can NEVER be muted/raided/targeted by this
    # userbot, even if another user running the same script tries to do so.
    # Includes the hoster-bot owner's Telegram ID (USERBOT_OWNER_ID env var).
    _protected_raw = os.environ.get("USERBOT_OWNER_ID", "")
    PROTECTED_IDS: Set[int] = set()
    for _pid in _protected_raw.replace(",", " ").split():
        try: PROTECTED_IDS.add(int(_pid))
        except: pass
    # Also add any extra IDs from EXTRA_PROTECTED env var (comma/space separated)
    for _pid in os.environ.get("EXTRA_PROTECTED", "").replace(",", " ").split():
        try: PROTECTED_IDS.add(int(_pid))
        except: pass

    bot = TelegramClient(
        StringSession(_session_str), API_ID, API_HASH,
        auto_reconnect=True, connection_retries=10, retry_delay=3
    )

    # ────────────────────────────────────────────────
    #                 STORAGE FILES
    # ────────────────────────────────────────────────
    ADMINS_FILE = "admins.json"
    NOTES_FILE = "notes.json"
    BANNER_FILE = "banner_msg_id.txt"
    SPAM_TEXTS_FILE = "spam_texts.json"
    WARNS_FILE = "warns.json"

    # ────────────────────────────────────────────────
    #                 CLONE ENGINE STATE
    # ────────────────────────────────────────────────
    CLONE_ACTIVE: bool = False
    LAST_CLONE_ID: Optional[int] = None
    CLONE_DATA: Dict[str, Optional[object]] = {
        "name": None, "username": None, "bio": None, "photo_bytes": None,
    }

    # ────────────────────────────────────────────────
    #                 RUNTIME STATE
    # ────────────────────────────────────────────────
    admins: Set[int] = set()
    notes: Dict[int, str] = {}
    warns: Dict[int, int] = {}

    menu_banner_msg: Optional[tuple] = None
    auto_react_emoji: Optional[str] = None

    muted_users: Set[int] = set()
    global_muted: Set[int] = set()

    reply_users: Set[int] = set()
    rr_users: Set[int] = set()
    flag_users: Set[int] = set()
    hrr_users: Set[int] = set()
    replygod_users: Set[int] = set()
    replysid_users: Dict[int, Dict[str, object]] = {}
    rspam_users: Dict[int, Dict[str, object]] = {}   # reply+spam mode

    # ─── NEW RAID STATE ───
    attack_users: Set[int] = set()
    roast_users: Set[int] = set()
    diss_users: Set[int] = set()
    war_users: Set[int] = set()
    savage_users: Set[int] = set()
    ultra_users: Set[int] = set()
    godwar_users: Set[int] = set()
    combo_users: Set[int] = set()
    troll_users: Set[int] = set()
    shame_users: Set[int] = set()
    fire_users: Set[int] = set()
    devil_users: Set[int] = set()
    karma_users: Set[int] = set()
    ghost_users: Set[int] = set()
    legend_users: Set[int] = set()
    doom_users: Set[int] = set()
    # ─── ADDED 4 MORE RAID TYPES ───
    nuke_users: Set[int] = set()
    storm_users: Set[int] = set()
    blizzard_users: Set[int] = set()
    venom_users: Set[int] = set()

    spray_tasks: Dict[int, asyncio.Task] = {}
    spam_texts: list = []
    watch_spam: Dict[tuple, Dict] = {}

    antidel_enabled: bool = False
    antidel_cache: Dict[int, Dict] = {}

    group_locks: Set[int] = set()
    START_TIME = time.time()
    SPRAY_DELAY = 0.1

    # ────────────────────────────────────────────────
    #                 BOT ADD ENGINE
    # ────────────────────────────────────────────────
    ADD_BOTS_LIST = [ "",]

    # ────────────────────────────────────────────────
    #                 FASTGC ENGINE STATE
    # ────────────────────────────────────────────────
    FASTGC_STATE: Dict[str, Optional[object]] = {
        "active": False, "template": None, "task": None, "chat_id": None,
    }
    GC_FAST_INTERVAL = 1
    GC_FAST_EMOJIS = [
        "❤️","🧡","💛","💚","💙","💜","🖤","🤍","🤎","🩷","🩵","🩶",
        "💖","💘","💝","💗","💓","💞","💕","💟","❣️","❤️‍🔥","❤️‍🩹"
    ]

    # ────────────────────────────────────────────────
    #                   HELPERS
    # ────────────────────────────────────────────────
    def load_admins():
        global admins
        try:
            if not os.path.isfile(ADMINS_FILE):
                admins = set(); return
            with open(ADMINS_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            clean = set()
            if isinstance(data, list):
                for x in data:
                    try: clean.add(int(x))
                    except: continue
            admins = clean
        except Exception as e:
            print(f"[LOAD ADMINS ERROR] {str(e)[:80]}")
            admins = set()

    def save_admins():
        try:
            tmp = sorted(set(int(x) for x in admins))
            with open(ADMINS_FILE, "w", encoding="utf-8") as f:
                json.dump(tmp, f, indent=2)
        except Exception as e:
            print(f"[SAVE ADMINS ERROR] {str(e)[:80]}")

    def is_admin(uid: int) -> bool:
        if not uid: return False
        return uid == OWNER_ID or uid in admins

    async def safe_edit(event, text: str):
        if not text: return
        try: return await event.edit(text)
        except Exception:
            try:
                msg = await event.reply(text)
            except: return
            try:
                if event.out: await event.delete()
            except: pass
            return msg

    def load_notes():
        global notes
        try:
            if not os.path.isfile(NOTES_FILE):
                notes = {}; return
            with open(NOTES_FILE, "r", encoding="utf-8") as f:
                raw = json.load(f)
            clean = {}
            if isinstance(raw, dict):
                for k, v in raw.items():
                    try: clean[int(k)] = str(v)
                    except: continue
            notes = clean
        except Exception as e:
            print(f"[LOAD NOTES ERROR] {str(e)[:80]}")
            notes = {}

    def save_notes():
        try:
            with open(NOTES_FILE, "w", encoding="utf-8") as f:
                json.dump(notes, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"[SAVE NOTES ERROR] {str(e)[:80]}")

    def load_banner():
        global menu_banner_msg
        try:
            if not os.path.isfile(BANNER_FILE):
                menu_banner_msg = None; return
            with open(BANNER_FILE, "r", encoding="utf-8") as f:
                raw = f.read().strip()
            if ":" not in raw:
                menu_banner_msg = None; return
            chat, msg = raw.split(":", 1)
            menu_banner_msg = (int(chat), int(msg))
        except Exception as e:
            print(f"[LOAD BANNER ERROR] {str(e)[:80]}")
            menu_banner_msg = None

    def save_banner():
        try:
            if not menu_banner_msg:
                if os.path.isfile(BANNER_FILE): os.remove(BANNER_FILE)
                return
            with open(BANNER_FILE, "w", encoding="utf-8") as f:
                f.write(f"{menu_banner_msg[0]}:{menu_banner_msg[1]}")
        except Exception as e:
            print(f"[SAVE BANNER ERROR] {str(e)[:80]}")

    def load_spam_texts():
        global spam_texts
        try:
            if not os.path.isfile(SPAM_TEXTS_FILE):
                spam_texts = []; return
            with open(SPAM_TEXTS_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            spam_texts = [str(x) for x in data] if isinstance(data, list) else []
        except Exception as e:
            print(f"[LOAD SPAM TEXTS ERROR] {str(e)[:80]}")
            spam_texts = []

    def save_spam_texts():
        try:
            with open(SPAM_TEXTS_FILE, "w", encoding="utf-8") as f:
                json.dump(spam_texts, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"[SAVE SPAM TEXTS ERROR] {str(e)[:80]}")

    def load_warns():
        global warns
        try:
            if not os.path.isfile(WARNS_FILE):
                warns = {}; return
            with open(WARNS_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            warns = {int(k): int(v) for k, v in data.items()} if isinstance(data, dict) else {}
        except:
            warns = {}

    def save_warns():
        try:
            with open(WARNS_FILE, "w", encoding="utf-8") as f:
                json.dump(warns, f, indent=2)
        except: pass

    async def get_targets(event, arg: str = "") -> Set[int]:
        targets: Set[int] = set()
        if event.is_reply:
            try:
                reply = await event.get_reply_message()
                if reply and reply.sender_id:
                    targets.add(int(reply.sender_id))
            except: pass
        if arg:
            for part in arg.strip().split():
                if not part: continue
                if part.isdigit():
                    try: targets.add(int(part)); continue
                    except: pass
                try:
                    ent = await bot.get_entity(part)
                    if ent and getattr(ent, "id", None):
                        targets.add(int(ent.id))
                except: pass
        try:
            me = await bot.get_me()
            targets.discard(me.id)
        except: pass
        # Remove all protected IDs — they can NEVER be targeted
        targets -= PROTECTED_IDS
        return targets

    load_admins()
    load_notes()
    load_banner()
    load_spam_texts()
    load_warns()

    # ────────────────────────────────────────────────
    #          ORIGINAL TEXT LISTS (Unchanged)
    # ────────────────────────────────────────────────
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

    # ────────────────────────────────────────────────
    #          NEW FIGHTING TEXT LISTS — 400 TEXTS (existing) + 4 new (200 texts)
    # ────────────────────────────────────────────────

    # ─── ATTACK LIST (50 texts) ───
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

    # ─── ROAST LIST (50 texts) ───
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
        "🤣 Teri skills dekh ke Thanos bhi bola hoga — yeh toh automatically wipe ho jaayega 💀😂",
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

    # ─── DISS LIST (50 texts) ───
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

    # ─── WAR LIST (50 texts) ───
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

    # ─── SAVAGE LIST (50 texts) ───
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

    # ─── ULTRA RAID LIST (50 texts) ───
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

    # ─── GOD WAR LIST (50 texts) ───
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

    # ─── COMBO RAID LIST (50 texts) ───
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

    # ─── TROLL LIST (50 texts) ───
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

    # ─── SHAME LIST (50 texts) ───
    shame_list = [
        "😤 Sharam kar — itna gira hua kaam karte kaise hain tum log 🔥💀",
        "🙅 Bhai teri harkat dekh ke pura group sharam se doob gaya 😂😤",
        "😤 Yeh sab karke tujhe pride feel hoti hai? Really? 💀🔥",
        "🙅 Beta teri harkaten dekh ke maa baap sharmayenge 😂😤",
        "😤 Sharam nahi hai tujhe bilkul — clearly 💀😹",
        "🙅 Bhai itna gira hua kaam dekh ke log muh fer lete hain 😤🔥",
        "😤 Tu itna neeche gira — zameen bhi neeche ho gayi 💀😂",
        "🙅 Beta sharam bhi nahi aata aisa karte hue 😤😹",
        "😤 Yeh harkat dekh ke lagta hai — tujhe value kisi ne nahi sikhaya 💀🔥",
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

    # ─── FIRE LIST (50 texts) ───
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

    # ─── DEVIL LIST (50 texts) ───
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

    # ─── KARMA LIST (50 texts) ───
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

    # ─── GHOST LIST (50 texts) ───
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

    # ─── LEGEND LIST (50 texts) ───
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

    # ─── DOOM LIST (50 texts) ───
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

    # ─── 4 NEW RAID LISTS (NUKE, STORM, BLIZZARD, VENOM) ───────────────────────────
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

    # ────────────────────────────────────────────────
    #                   JOKE / FUN CONTENT
    # ────────────────────────────────────────────────
    joke_list = [
        "Main apni life mein itna positive hoon... ki blood group bhi B+ hai! 😂",
        "Teacher: Kal absent kyun the? Student: Sir, mujhe bukhar tha. Teacher: Proof? Student: Aaj aa gaya na! 😹",
        "Santa: Main ghar ke bahar khada hun. Banta: Andar aa jao. Santa: Andar wala bhi main hoon! 🤣",
        "Meri girlfriend ne kaha — tujhse better koi nahi. Phir chali gayi. Better koi mila hoga shayad 😂",
        "Doctor: Patient ko hawa ki zaroorat hai. Nurse: Kya karein? Doctor: Fan on karo. Nurse: Ceiling se pakad ke? 😹",
        "Ghar mein sabse zyada kaam mera — internet chalaana! 😂",
        "Padhai karo beta future bright hoga. Maine padhi — future gaya andhera mein. Lying wasn't their first language 🤣",
        "Wo bolti hai 'I need space' — main bola ठीक है, NASA se contact karo! 😂",
    ]

    riddle_list = [
        "Kya cheez hai jo khata hai par pet nahi hota? — Aag (Fire) 🔥",
        "Woh kaunsi cheez hai jo bolta hai 'Main aaya' par nahi aata? — Kal (Tomorrow) ⏰",
        "Jitna zyada liya jaaye utna chhota hota hai — kya? — Ek gaddha (hole in the ground) 🕳️",
        "Mere paas aankhein hain par dekh nahi sakta — kya hoon main? — Sooee (needle) 🧵",
        "Vo kya cheez hai jo haath se chhoone pe bhi nahi lagti? — Khoobsoorti! 😄",
    ]

    fact_list = [
        "🧠 Insaan ka dimag 75% paani se bana hai!",
        "🐙 Octopus ke teen dil hote hain!",
        "🌙 Chand par mobile signal nahi hai — par WiFi aata hai ek satellite se! (Future plan 😂)",
        "🍯 Sahi tarike se rakha hua honey kabhi kharab nahi hota!",
        "⚡ Bijli ka ek bolt 5 times zyada garam hota hai sun ki surface se!",
        "🦈 Shark insaan se zyada purana hai — dinasors se bhi pehle!",
        "👁️ Insaan ki aankh 10 million rangon ko differentiate kar sakti hai!",
        "🐝 Ek machhar ek second mein 600 baar apne pankh hilata hai!",
    ]

    truth_list = [
        "Sach bolo — last baar kab jhooth bola tha? 🤥",
        "Teri life ka sabse bada secret kya hai jo kisi ko nahi pata? 🤫",
        "Kisi pe crush tha jo ab dost hai? 😳",
        "Kabhi kisi ki baat repeat ki thi jo confidence mein batai gayi thi? 😬",
        "Woh kaun hai jis par sabse zyada trust karte ho? ❤️",
        "Life mein sabse bada regret kya hai? 💭",
        "Kabhi class ya office se bina bataye bhaage ho? 😂",
    ]

    dare_list = [
        "Abhi apni maa ko call kar ke bol — 'Main tujhse pyaar karta hoon' 📞❤️",
        "Apni sabse embarrassing photo share kar group mein 📸😹",
        "Kisi bhi friend ko abhi message kar — 'Bhai mujhe pata chal gaya' — aur reaction dekho 😈",
        "10 seconds ke liye khud se hi baat karo — loud 🗣️",
        "Abhi ek push-up kar aur photo bhejo 💪",
        "Apne crush ko 'Hi' bol — screenshot bhejo 😳",
        "Khud ki roast karo ek paragraph mein — seriously 😂",
    ]

    pickup_list = [
        "Kya tum WiFi ho? Kyunki main teri taraf khinchat chala aa raha hoon 📶😂",
        "Tujhe dekh ke soch raha tha — yeh image real nahi ho sakti 🖼️❤️",
        "Kya tum dictionary ho? Kyunki tujhme meaning hai 📖✨",
        "Tu itna sweet hai ke mujhe diabetes ka darr ho gaya 🍭😹",
        "Teri eyes mein stars hain ya stars tujhe dekh ke sharminde ho gaye? ⭐❤️",
    ]

    compliment_list = [
        "Bhai tu bahut positive energy rakhta hai — seriously 🌟",
        "Teri thinking bahut alag hai — creative hai tu 🧠✨",
        "Tu jo bhi karta hai dil se karta hai — yeh rare hai ❤️",
        "Teri sense of humor? Top tier 😂👑",
        "Tujhse baat karna genuinely enjoyable hota hai 🗣️✨",
    ]

    quote_list = [
        "💭 'Sapne woh nahi jo sote waqt aate hain, sapne woh hain jo sone nahi dete.' — APJ Abdul Kalam",
        "💭 'Mehnat karo itna ki luck ko bhi mauka mile tujhe dhundhne ka.' — Unknown",
        "💭 'Duniya ka sabse bada teacher: failure hai.' — Unknown",
        "💭 'Ek accha dost aur ek accha kitaab — dono hi tujhe better banate hain.' — Unknown",
        "💭 'Zindagi ek echo hai — jo bejhoge woh wapas aayega.' — Unknown",
    ]

    # ────────────────────────────────────────────────
    #                   DECORATOR
    # ────────────────────────────────────────────────
    commands = {}

    def register_cmd(name: str, needs_reply: bool = False, group_only: bool = False):
        def decorator(func):
            key = (name or "").lower().strip()
            if not key:
                raise ValueError("Command name cannot be empty")
            if key in commands:
                raise ValueError(f"Duplicate command registered: {key}")
            commands[key] = {
                "func": func, "needs_reply": bool(needs_reply), "group_only": bool(group_only),
            }
            return func
        return decorator

    # ────────────────────────────────────────────────
    #                 FASTGC ENGINE
    # ────────────────────────────────────────────────
    async def fast_title_edit(chat_id, title):
        safe_title = (title or "").strip()[:255]
        if not safe_title: return False
        try:
            await bot(functions.channels.EditTitleRequest(channel=chat_id, title=safe_title))
            return True
        except Exception:
            try:
                await bot(functions.messages.EditChatTitleRequest(chat_id=chat_id, title=safe_title))
                return True
            except Exception as e:
                print(f"[FastGC] Title edit failed → {str(e)[:80]}")
                return False

    async def gc_fast_loop(chat_id):
        try:
            while True:
                if not FASTGC_STATE.get("active"): break
                template = FASTGC_STATE.get("template")
                if not template: break
                try: emoji = random.choice(GC_FAST_EMOJIS)
                except: emoji = "⚡"
                try: new_title = template.replace("{emoji}", emoji)
                except: await asyncio.sleep(2); continue
                ok = await fast_title_edit(chat_id, new_title)
                try:
                    if ok: await asyncio.sleep(max(1, GC_FAST_INTERVAL))
                    else: await asyncio.sleep(5)
                except: await asyncio.sleep(3)
        except asyncio.CancelledError: return
        except Exception as e: print(f"[FastGC Loop Crash] → {str(e)[:80]}")

    # ────────────────────────────────────────────────
    #                   MENU COMMANDS
    # ────────────────────────────────────────────────
    @register_cmd("menu")
    async def cmd_menu(event, _):
        global menu_banner_msg
        menu = (
    "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
    "  ⚡️  𝗦𝗜𝗗𝘅𝗕𝗢𝗧  𝗨𝗦𝗘𝗥𝗕𝗢𝗧  𝗩𝟯  ⚡️\n"
    "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
    "\n"
    "  👑  𝗢𝘄𝗻𝗲𝗿   ›  𝗦𝗜𝗗𝘅𝗕𝗢𝗧\n"
    "  📦  𝗖𝗺𝗱𝘀    ›  𝟱𝟬𝟬+ 𝗖𝗼𝗺𝗺𝗮𝗻𝗱𝘀\n"
    "  🔥  𝗣𝗿𝗲𝗳𝗶𝗽  ›  .  (𝗗𝗼𝘁)\n"
    "  ⚔️  𝗥𝗮𝗶𝗱𝘀   ›  𝟮𝟬 𝗧𝘆𝗽𝗲𝘀  (𝟰 𝗡𝗘𝗪)\n"
    "\n"
    "┌──────────────────────────────────┐\n"
    "│         📋  𝗠𝗘𝗡𝗨  𝗣𝗔𝗚𝗘𝗦          │\n"
    "├──────────────────────────────────┤\n"
    "│  .𝗺𝗲𝗻𝘂𝟭  →  👑 𝗔𝗱𝗺𝗶𝗻 & 🔇 𝗠𝘂𝘁𝗲       │\n"
    "│  .𝗺𝗲𝗻𝘂𝟮  →  ⚔️ 𝗥𝗮𝗶𝗱 𝗘𝗻𝗴𝗶𝗻𝗲 (𝗢𝗿𝗶𝗴)   │\n"
    "│  .𝗺𝗲𝗻𝘂𝟯  →  💣 𝗦𝗽𝗮𝗺 & 📝 𝗧𝗲𝘅𝘁 𝗠𝗴𝗿   │\n"
    "│  .𝗺𝗲𝗻𝘂𝟰  →  🛡️ 𝗣𝗿𝗼𝘁𝗲𝗰𝘁𝗶𝗼𝗻          │\n"
    "│  .𝗺𝗲𝗻𝘂𝟱  →  🛠️ 𝗧𝗼𝗼𝗹𝘀 & 🎵 𝗠𝘂𝘀𝗶𝗰     │\n"
    "│  .𝗺𝗲𝗻𝘂𝟲  →  🔥 𝗙𝗶𝗴𝗵𝘁𝗶𝗻𝗴 𝗥𝗮𝗶𝗱𝘀       │\n"
    "│  .𝗺𝗲𝗻𝘂𝟳  →  ⚙️ 𝗨𝘁𝗶𝗹𝗶𝘁𝘆 𝗧𝗼𝗼𝗹𝘀        │\n"
    "│  .𝗺𝗲𝗻𝘂𝟴  →  🎮 𝗙𝘂𝗻 & 𝗚𝗮𝗺𝗲𝘀          │\n"
    "│  .𝗰𝗺𝗱𝘀   →  📜 𝗔𝗹𝗹 𝗖𝗼𝗺𝗺𝗮𝗻𝗱𝘀         │\n"
    "└──────────────────────────────────┘\n"
    "\n"
    "🔥  𝗣𝗼𝘄𝗲𝗿𝗲𝗱 𝗯𝘆 𝗦𝗜𝗗𝘅𝗕𝗢𝗧  🔥"
        )
        await safe_edit(event, menu)
        if menu_banner_msg:
            chat_id, msg_id = menu_banner_msg
            try:
                msg = await bot.get_messages(chat_id, ids=msg_id)
                await bot.send_file(event.chat_id, file=msg.media, caption="⚡ 𝗦𝗜𝗗𝘅𝗕𝗢𝗧 𝗘𝗻𝘁𝗲𝗿𝘀 ❤️‍🔥")
            except: pass


    @register_cmd("menu1")
    async def cmd_menu1(event, _):
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
        await safe_edit(event, menu)


    @register_cmd("menu2")
    async def cmd_menu2(event, _):
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
        await safe_edit(event, menu)


    @register_cmd("menu3")
    async def cmd_menu3(event, _):
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
        await safe_edit(event, menu)


    @register_cmd("menu4")
    async def cmd_menu4(event, _):
        menu = (
    "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
    "   🛡️  𝗣𝗥𝗢𝗧𝗘𝗖𝗧𝗜𝗢𝗡  &  🖼️  𝗣𝗙𝗣  &  ❤️  𝗔𝗨𝗧𝗢\n"
    "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
    "\n"
    "【 🛡️ 𝗔𝗡𝗧𝗜-𝗗𝗘𝗟𝗘𝗧𝗘 】\n"
    "  ✦ .antidel on     → Anti-delete on\n"
    "  ✦ .antidel off    → Anti-delete off\n"
    "  ✦ .antidel status → Status check\n"
    "\n"
    "【 👁️ 𝗦𝗣𝗔𝗠 𝗪𝗔𝗧𝗖𝗛 】\n"
    "  ✦ .watchspam @user <limit> <sec>\n"
    "  ✦ .unwatchspam @user\n"
    "  ✦ .watchlist → Watch list dekho\n"
    "\n"
    "【 🖼️ 𝗚𝗥𝗢𝗨𝗣 𝗣𝗙𝗣 】\n"
    "  ✦ .setgpfp    → Group PFP set\n"
    "  ✦ .addgpfp    → PFP add karo\n"
    "  ✦ .listgpfp   → PFP list\n"
    "  ✦ .autogpfp   → Auto rotate\n"
    "  ✦ .stopgpfp   → Auto PFP band\n"
    "\n"
    "【 ❤️ 𝗔𝗨𝗧𝗢 𝗥𝗘𝗔𝗖𝗧 】\n"
    "  ✦ .ar <emoji>  → Auto react on\n"
    "  ✦ .sar         → Auto react off\n"
    "\n"
    "📌  .menu → Main menu wapas"
        )
        await safe_edit(event, menu)


    @register_cmd("menu5")
    async def cmd_menu5(event, _):
        menu = (
    "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
    "    🛠️  𝗧𝗢𝗢𝗟𝗦  •  🎵  𝗠𝗨𝗦𝗜𝗖  •  👤  𝗣𝗥𝗢𝗙\n"
    "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
    "\n"
    "【 🛠️ 𝗠𝗔𝗜𝗡 𝗧𝗢𝗢𝗟𝗦 】\n"
    "  ✦ .tts <text>    → Text to voice\n"
    "  ✦ .qrcode <text> → QR code banao\n"
    "  ✦ .fancy <text>  → Fancy text\n"
    "  ✦ .style <text>  → Style text\n"
    "  ✦ .calc <expr>   → Calculator\n"
    "  ✦ .weather <city>→ Mausam check\n"
    "  ✦ .ip <ip>       → IP info\n"
    "  ✦ .short <url>   → URL short karo\n"
    "  ✦ .crypto <coin> → Crypto price\n"
    "  ✦ .translate <text>→ Translate\n"
    "  ✦ .imdb <movie>  → Movie info\n"
    "\n"
    "【 🎵 𝗠𝗨𝗦𝗜𝗖 】\n"
    "  ✦ .music <song>  → Song download\n"
    "  ✦ .dmusic <song> → Direct download\n"
    "\n"
    "【 🧠 𝗡𝗢𝗧𝗘𝗦 𝗦𝗬𝗦𝗧𝗘𝗠 】\n"
    "  ✦ .notesadd   → Note save karo\n"
    "  ✦ .noteslist  → Notes dekho\n"
    "  ✦ .notesdelete→ Note delete\n"
    "\n"
    "【 👤 𝗣𝗥𝗢𝗙𝗜𝗟𝗘 】\n"
    "  ✦ .setname <name>   → Name badlo\n"
    "  ✦ .setbio <text>    → Bio set karo\n"
    "  ✦ .setpp (reply)    → Profile pic\n"
    "  ✦ .getpp (reply)    → Get user pic\n"
    "  ✦ .copy / .normal   → Clone/Restore\n"
    "\n"
    "【 🖼️ 𝗕𝗔𝗡𝗡𝗘𝗥 】\n"
    "  ✦ .banner   → Banner set karo\n"
    "  ✦ .rembanner→ Banner hatao\n"
    "\n"
    "📌  .menu7 & .menu8 → Aur tools"
        )
        await safe_edit(event, menu)


    @register_cmd("menu6")
    async def cmd_menu6(event, _):
        menu = (
    "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
    "   🔥  𝗙𝗜𝗚𝗛𝗧𝗜𝗡𝗚  𝗥𝗔𝗜𝗗𝗦  —  𝟭𝟬𝟬𝟬+ 𝗧𝗘𝗫𝗧𝗦\n"
    "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
    "\n"
    "  💡 𝗨𝘀𝗲: .cmdname @username\n"
    "  🛑 𝗦𝘁𝗼𝗽: .s + cmdname\n"
    "\n"
    "┌──────────────────────────────────┐\n"
    "│  𝗥𝗔𝗜𝗗 𝗧𝗬𝗣𝗘  │    𝗦𝗧𝗔𝗥𝗧    │   𝗦𝗧𝗢𝗣   │\n"
    "├──────────────────────────────────┤\n"
    "│  ⚔️ Attack  │  .attack  │ .sattack │\n"
    "│  🎤 Roast   │  .roast   │ .sroast  │\n"
    "│  💀 Diss    │  .diss    │ .sdiss   │\n"
    "│  💣 War     │  .war     │ .swar    │\n"
    "│  😈 Savage  │  .savage  │ .ssavage │\n"
    "│  🌪️ Ultra   │  .ultra   │ .sultra  │\n"
    "│  👑 GodWar  │  .godwar  │ .sgodwar │\n"
    "│  💥 Combo   │  .combo   │ .scombo  │\n"
    "│  🤡 Troll   │  .troll   │ .stroll  │\n"
    "│  😤 Shame   │  .shame   │ .sshame  │\n"
    "│  🔥 Fire    │  .fire    │ .sfire   │\n"
    "│  😈 Devil   │  .devil   │ .sdevil  │\n"
    "│  ☯️ Karma   │  .karma   │ .skarma  │\n"
    "│  👻 Ghost   │  .ghost   │ .sghost  │\n"
    "│  👑 Legend  │  .legend  │ .slegend │\n"
    "│  💀 Doom    │  .doom    │ .sdoom   │\n"
    "│  ☢️ NUKE    │  .nuke    │ .snuke   │  ★ NEW\n"
    "│  🌪️ STORM   │  .storm   │ .sstorm  │  ★ NEW\n"
    "│  ❄️ BLIZZARD│  .blizzard│ .sblizzard│ ★ NEW\n"
    "│  ☠️ VENOM   │  .venom   │ .svenom  │  ★ NEW\n"
    "└──────────────────────────────────┘\n"
    "\n"
    "  🛑 .stopall  → 𝗦𝗮𝗮𝗿𝗲 raids ek saath band\n"
    "  📊 .raidstatus → Active raids check\n"
    "\n"
    "⚡ 𝟮𝟬 𝗥𝗮𝗶𝗱 𝗧𝘆𝗽𝗲𝘀 × 𝟱𝟬 𝗧𝗲𝘅𝘁𝘀 = 𝟭𝟬𝟬𝟬+ 𝗙𝗶𝗴𝗵𝘁𝗶𝗻𝗴 𝗧𝗲𝘅𝘁𝘀 🔥"
        )
        await safe_edit(event, menu)


    @register_cmd("menu7")
    async def cmd_menu7(event, _):
        menu = (
    "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
    "         ⚙️  𝗨𝗧𝗜𝗟𝗜𝗧𝗬  𝗧𝗢𝗢𝗟𝗦\n"
    "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
    "\n"
    "【 📝 𝗧𝗘𝗫𝗧 𝗧𝗢𝗢𝗟𝗦 】\n"
    "  ✦ .upper <text>   → CAPITAL letters\n"
    "  ✦ .lower <text>   → small letters\n"
    "  ✦ .reverse <text> → txet esreveR\n"
    "  ✦ .len <text>     → Character count\n"
    "  ✦ .wcount <text>  → Word count\n"
    "  ✦ .bold <text>    → **Bold** text\n"
    "  ✦ .italic <text>  → __Italic__ text\n"
    "  ✦ .mono <text>    → `Mono` text\n"
    "  ✦ .camel <text>   → camelCase\n"
    "  ✦ .repeat <n> <t> → N baar repeat\n"
    "\n"
    "【 🎨 𝗦𝗧𝗬𝗟𝗘 𝗧𝗢𝗢𝗟𝗦 】\n"
    "  ✦ .big <text>     → 𝗕𝗜𝗚 text\n"
    "  ✦ .small <text>   → ꜱᴍᴀʟʟ text\n"
    "  ✦ .shadow <text>  → ░▒▓ Shadow ▓▒░\n"
    "  ✦ .zalgo <text>   → Z̷̴̵a̴l̷g̵o text\n"
    "  ✦ .leet <text>    → L33T text\n"
    "\n"
    "【 🔐 𝗖𝗥𝗬𝗣𝗧𝗢 & 𝗘𝗡𝗖𝗢𝗗𝗘 】\n"
    "  ✦ .encode <text>  → Base64 encode\n"
    "  ✦ .decode <b64>   → Base64 decode\n"
    "  ✦ .rot13 <text>   → ROT13 cipher\n"
    "  ✦ .morse <text>   → .- Morse code\n"
    "  ✦ .binary <text>  → 01010 Binary\n"
    "  ✦ .md5 <text>     → MD5 hash\n"
    "  ✦ .sha256 <text>  → SHA256 hash\n"
    "  ✦ .b64 <text>     → Base64\n"
    "  ✦ .b64d <text>    → Base64 decode\n"
    "  ✦ .uuid           → UUID generate\n"
    "  ✦ .password <len> → Strong password\n"
    "\n"
    "【 ⏰ 𝗧𝗜𝗠𝗘 & 𝗦𝗬𝗦𝗧𝗘𝗠 】\n"
    "  ✦ .time    → Current IST time\n"
    "  ✦ .date    → Aaj ki date\n"
    "  ✦ .uptime  → Bot ka uptime\n"
    "  ✦ .myip    → Server IP\n"
    "  ✦ .ping    → Latency check\n"
    "\n"
    "【 🔢 𝗠𝗔𝗧𝗛 】\n"
    "  ✦ .random <min> <max> → Random number\n"
    "  ✦ .calc <expression>  → Calculator\n"
    "  ✦ .tempconv <C/F> <n> → Temp convert\n"
    "\n"
    "【 👤 𝗨𝗦𝗘𝗥 𝗜𝗡𝗙𝗢 】\n"
    "  ✦ .id       → Apna ID dekho\n"
    "  ✦ .chatid   → Chat ID\n"
    "  ✦ .whois    → User info\n"
    "  ✦ .mention  → User mention\n"
    "\n"
    "【 🆕 𝗘𝗫𝗧𝗥𝗔 𝗧𝗢𝗢𝗟𝗦 】\n"
    "  ✦ .hex / .octal / .ascii / .nato\n"
    "  ✦ .palindrome / .vowels / .wordfreq\n"
    "  ✦ .charcount / .lettercount / .charinfo\n"
    "  ✦ .bmi / .age / .prime / .factorial\n"
    "  ✦ .fibonacci / .square / .roman / .table\n"
    "  ✦ .percentage / .number / .countdown\n"
    "  ✦ .titlecase / .snake / .shout / .mock\n"
    "  ✦ .alternating / .spaceit / .removespaces\n"
    "  ✦ .clap / .mirror / .flip_text / .tinytext\n"
    "  ✦ .bubble / .square_text / .boxtext\n"
    "  ✦ .encrypt / .decrypt / .sha1 / .sha512\n"
    "  ✦ .strike / .spoiler / .typetest\n"
    "  ✦ .coin / .lucky / .roll / .timer\n"
    "  ✦ .sysinfo / .randname / .randcolor\n"
    "  ✦ .truncate / .wordgame / .emoji2text\n"
    "\n"
    "📌  .menu → Main menu wapas"
        )
        await safe_edit(event, menu)


    @register_cmd("menu8")
    async def cmd_menu8(event, _):
        menu = (
    "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
    "      🎮  𝗙𝗨𝗡  •  𝗚𝗔𝗠𝗘𝗦  •  𝗠𝗔𝗦𝗧𝗜\n"
    "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
    "\n"
    "【 🎲 𝗚𝗔𝗠𝗘𝗦 】\n"
    "  ✦ .flip          → Coin flip 🪙\n"
    "  ✦ .dice          → Roll dice 🎲\n"
    "  ✦ .rps <r/p/s>   → Rock Paper Scissors ✊\n"
    "  ✦ .8ball <ques>  → Magic 8-Ball 🎱\n"
    "  ✦ .choose <a|b>  → Random pick 🎯\n"
    "\n"
    "【 😄 𝗙𝗨𝗡 𝗖𝗢𝗠𝗠𝗔𝗡𝗗𝗦 】\n"
    "  ✦ .joke          → Random joke 😂\n"
    "  ✦ .riddle        → Paheli 🧩\n"
    "  ✦ .fact          → Interesting fact 🤯\n"
    "  ✦ .quote         → Quote 💭\n"
    "  ✦ .truth         → Truth question 😳\n"
    "  ✦ .dare          → Dare challenge 😈\n"
    "  ✦ .pickup        → Pickup line 😏\n"
    "  ✦ .compliment    → Compliment 🌹\n"
    "  ✦ .roastme       → Khud ko roast 🔥\n"
    "\n"
    "【 💬 𝗠𝗘𝗦𝗦𝗔𝗚𝗘 𝗧𝗢𝗢𝗟𝗦 】\n"
    "  ✦ .del           → Message delete\n"
    "  ✦ .echo <text>   → Echo karo\n"
    "  ✦ .react <emoji> → React lagao\n"
    "  ✦ .read          → Read mark\n"
    "  ✦ .typing <sec>  → Typing show\n"
    "  ✦ .online        → Online set\n"
    "\n"
    "【 📊 𝗦𝗧𝗔𝗧𝗦 】\n"
    "  ✦ .status     → Bot stats 📈\n"
    "  ✦ .raidstatus → Active raids 🔥\n"
    "  ✦ .ping       → Latency check ⚡\n"
    "\n"
    "📌  .menu → Main menu wapas"
        )
        await safe_edit(event, menu)


    @register_cmd("cmds")
    async def cmd_cmds(event, _):
        cmds = (
    "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
    "   📜  𝗦𝗜𝗗𝗫𝗕𝗢𝗧  𝗩𝟯  —  𝗙𝗨𝗟𝗟  𝗖𝗠𝗗𝗦\n"
    "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
    "\n"
    "👑 𝗔𝗗𝗠𝗜𝗡:\n"
    "  .admins .addadmin .deladmin\n"
    "\n"
    "🔇 𝗠𝗨𝗧𝗘:\n"
    "  .mute .unmute .gmute .gunmute .mutelist\n"
    "\n"
    "🧹 𝗚𝗥𝗢𝗨𝗣 𝗠𝗢𝗗:\n"
    "  .lock .unlock .purge .throw .addbots\n"
    "  .ban .unban .kick .promote .demote\n"
    "  .warn .warnlist .clearwarn\n"
    "  .pin .unpin .groupinfo .membercount .invitelink\n"
    "\n"
    "⚔️ 𝗥𝗔𝗜𝗗𝗦 (𝗢𝗥𝗜𝗚):\n"
    "  .reply .rr .flag .hrr .replygod .replysid\n"
    "  stop: .sreply .srr .sflag .shrr .sgod .sstop\n"
    "\n"
    "🔥 𝗥𝗔𝗜𝗗𝗦 (𝗡𝗘𝗪 𝟭𝟬𝟬𝟬+ 𝗧𝗘𝗫𝗧𝗦):\n"
    "  .attack .roast .diss .war .savage\n"
    "  .ultra .godwar .combo .troll .shame\n"
    "  .fire .devil .karma .ghost .legend .doom\n"
    "  .nuke .storm .blizzard .venom   ★ 4 NEW\n"
    "  stop: .s<name>  |  all: .stopall\n"
    "\n"
    "💣 𝗦𝗣𝗔𝗠:\n"
    "  .spray .dspray .tspray .rspray\n"
    "  .multispray .countspray .spraydelay\n"
    "\n"
    "📝 𝗧𝗘𝗫𝗧 𝗠𝗚𝗥:\n"
    "  .addtext .listtexts .edittext .deltext .cleartext\n"
    "\n"
    "🛡️ 𝗣𝗥𝗢𝗧𝗘𝗖𝗧𝗜𝗢𝗡:\n"
    "  .antidel .watchspam .unwatchspam .watchlist\n"
    "\n"
    "🖼️ 𝗣𝗙𝗣:\n"
    "  .setgpfp .addgpfp .listgpfp .autogpfp .stopgpfp\n"
    "\n"
    "❤️ 𝗔𝗨𝗧𝗢:\n"
    "  .ar .sar .fastgc\n"
    "\n"
    "🛠️ 𝗧𝗢𝗢𝗟𝗦 (𝗢𝗥𝗜𝗚):\n"
    "  .tts .qrcode .fancy .style .emoji .calc\n"
    "  .weather .ip .short .crypto .translate .imdb\n"
    "\n"
    "📝 𝗧𝗘𝗫𝗧 𝗧𝗢𝗢𝗟𝗦:\n"
    "  .upper .lower .reverse .len .wcount\n"
    "  .bold .italic .mono .camel .repeat\n"
    "  .big .small .shadow .zalgo .leet\n"
    "\n"
    "🔐 𝗖𝗥𝗬𝗣𝗧𝗢:\n"
    "  .encode .decode .rot13 .morse .binary\n"
    "  .md5 .sha256 .b64 .b64d .uuid .password\n"
    "\n"
    "⏰ 𝗦𝗬𝗦𝗧𝗘𝗠:\n"
    "  .time .date .uptime .myip .ping\n"
    "\n"
    "🔢 𝗠𝗔𝗧𝗛:\n"
    "  .random .calc .tempconv\n"
    "\n"
    "👤 𝗨𝗦𝗘𝗥:\n"
    "  .id .chatid .whois .mention\n"
    "  .getpp .setname .setbio .setpp\n"
    "\n"
    "🎵 𝗠𝗨𝗦𝗜𝗖:\n"
    "  .music .dmusic\n"
    "\n"
    "🧠 𝗡𝗢𝗧𝗘𝗦:\n"
    "  .notesadd .noteslist .notesdelete\n"
    "\n"
    "🎮 𝗙𝗨𝗡:\n"
    "  .flip .dice .rps .8ball .choose\n"
    "  .joke .riddle .fact .quote\n"
    "  .truth .dare .pickup .compliment .roastme\n"
    "\n"
    "💬 𝗠𝗦𝗚 𝗧𝗢𝗢𝗟𝗦:\n"
    "  .del .echo .react .read .typing .online\n"
    "\n"
    "👤 𝗣𝗥𝗢𝗙𝗜𝗟𝗘:\n"
    "  .copy .normal .banner .rembanner\n"
    "\n"
    "📊 𝗦𝗧𝗔𝗧𝗦:\n"
    "  .status .raidstatus .ping\n"
    "\n"
    "📖 𝗠𝗘𝗡𝗨:\n"
    "  .menu .menu1 .menu2 .menu3 .menu4\n"
    "  .menu5 .menu6 .menu7 .menu8 .cmds\n"
    "\n"
    "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
    "⚡ 𝟱𝟬𝟬+ 𝗖𝗺𝗱𝘀  |  🔥 𝗣𝗿𝗲𝗳𝗶𝘅: .  |  𝗩𝟯"
        )
        await safe_edit(event, cmds)

    # ────────────────────────────────────────────────
    #              ORIGINAL COMMANDS (Unchanged)
    # ────────────────────────────────────────────────

    @register_cmd("banner", needs_reply=True)
    async def cmd_banner(event, _):
        global menu_banner_msg
        reply = await event.get_reply_message()
        if not reply:
            return await safe_edit(event, "❌ 𝐍ᴏ 𝐑ᴇᴘʟʏ\n👉 𝐑ᴇᴘʟʏ 𝐓ᴏ 𝐏ʜᴏᴛᴏ / 𝐕ɪᴅᴇᴏ")
        if not reply.media:
            return await safe_edit(event, "❌ 𝐈ɴᴠᴀʟɪᴅ 𝐌ᴇᴅɪᴀ\n👉 𝐎ɴʟʏ 𝐏ʜᴏᴛᴏ / 𝐕ɪᴅᴇᴏ")
        await safe_edit(event, "⚡ 𝐏ʀᴏᴄᴇssɪɴɢ 𝐁ᴀɴɴᴇʀ...\n━━━━━━━━━━━━━━━")
        try:
            try: saved = await reply.forward_to("me")
            except Exception:
                file = await reply.download_media(file=bytes)
                if not file: return await safe_edit(event, "❌ 𝐌ᴇᴅɪᴀ 𝐃ᴏᴡɴʟᴏᴀᴅ 𝐅ᴀɪʟ")
                bio = BytesIO(file); bio.name = "banner"
                saved = await bot.send_file("me", bio)
            menu_banner_msg = (saved.chat_id, saved.id)
            save_banner()
            text = f"🖼️ 𝐁ᴀɴɴᴇʀ 𝐒ᴇᴛ\n━━━━━━━━━━━━━━━\n📌 𝐒ᴀᴠᴇᴅ 𝐈ᴅ → `{saved.id}`"
            if event.out: await safe_edit(event, text)
            else: await event.reply(text)
        except Exception as e:
            await safe_edit(event, f"❌ 𝐁ᴀɴɴᴇʀ 𝐄ʀʀ → `{str(e)[:50]}`")


    @register_cmd("rembanner")
    async def cmd_rembanner(event, _):
        global menu_banner_msg
        if not menu_banner_msg:
            return await safe_edit(event, "⚠️ 𝐍ᴏ 𝐁ᴀɴɴᴇʀ 𝐒ᴇᴛ")
        await safe_edit(event, "⚡ 𝐑ᴇᴍᴏᴠɪɴɢ 𝐁ᴀɴɴᴇʀ...\n━━━━━━━━━━━━━━━")
        try:
            chat_id, msg_id = menu_banner_msg
            try: await bot.delete_messages(chat_id, [msg_id])
            except: pass
            menu_banner_msg = None; save_banner()
            text = "🗑️ 𝐁ᴀɴɴᴇʀ 𝐑ᴇᴍᴏᴠᴇᴅ\n━━━━━━━━━━━━━━━"
            if event.out: await safe_edit(event, text)
            else: await event.reply(text)
        except Exception as e:
            await safe_edit(event, f"❌ 𝐑ᴇᴍᴏᴠᴇ 𝐄ʀʀ → `{str(e)[:50]}`")


    @register_cmd("addadmin", needs_reply=True)
    async def cmd_addadmin(event, arg):
        try:
            targets = await get_targets(event, arg)
            if not targets:
                return await safe_edit(event, "❌ 𝐍ᴏ 𝐕ᴀʟɪᴅ 𝐓ᴀʀɢᴇᴛ\n👉 𝐑ᴇᴘʟʏ / @username / ID")
            await safe_edit(event, "⚡ 𝐏ʀᴏᴄᴇssɪɴɢ 𝐀ᴅᴍɪɴ 𝐀ᴅᴅ...\n━━━━━━━━━━━━━━━")
            added, already, skipped_owner = [], [], []
            for uid in targets:
                try: uid = int(uid)
                except: continue
                if uid == OWNER_ID: skipped_owner.append(str(uid)); continue
                if uid in admins: already.append(str(uid))
                else: admins.add(uid); added.append(str(uid))
            try: save_admins()
            except: pass
            parts = []
            if added: parts.append(f"✅ 𝐀ᴅᴍɪɴ 𝐀ᴅᴅᴇᴅ → `{', '.join(added)}`")
            if already: parts.append(f"⚠️ 𝐀ʟʀᴇᴀᴅʏ 𝐀ᴅᴍɪɴ → `{', '.join(already)}`")
            if skipped_owner: parts.append(f"👑 𝐎ᴡɴᴇʀ 𝐒ᴋɪᴘᴘᴇᴅ → `{', '.join(skipped_owner)}`")
            if not parts: parts.append("❌ 𝐍ᴏ 𝐂ʜᴀɴɢᴇs 𝐌ᴀᴅᴇ")
            text = "\n".join(parts)
            if event.out: await safe_edit(event, text)
            else: await event.reply(text)
        except Exception as e:
            await safe_edit(event, f"❌ 𝐀ᴅᴍɪɴ 𝐀ᴅᴅ 𝐄ʀʀ → `{str(e)[:50]}`")


    @register_cmd("deladmin", needs_reply=True)
    async def cmd_deladmin(event, arg):
        try:
            targets = await get_targets(event, arg)
            if not targets:
                return await safe_edit(event, "❌ 𝐍ᴏ 𝐕ᴀʟɪᴅ 𝐓ᴀʀɢᴇᴛ\n👉 𝐑ᴇᴘʟʏ / @username / ID")
            await safe_edit(event, "⚡ 𝐏ʀᴏᴄᴇssɪɴɢ 𝐀ᴅᴍɪɴ 𝐑ᴇᴍᴏᴠᴇ...\n━━━━━━━━━━━━━━━")
            removed, not_admin, skipped_owner = [], [], []
            for uid in targets:
                try: uid = int(uid)
                except: continue
                if uid == OWNER_ID: skipped_owner.append(str(uid)); continue
                if uid in admins: admins.remove(uid); removed.append(str(uid))
                else: not_admin.append(str(uid))
            try: save_admins()
            except: pass
            parts = []
            if removed: parts.append(f"🗑️ 𝐀ᴅᴍɪɴ 𝐑ᴇᴍᴏᴠᴇᴅ → `{', '.join(removed)}`")
            if not_admin: parts.append(f"⚠️ 𝐍ᴏᴛ 𝐀ᴅᴍɪɴ → `{', '.join(not_admin)}`")
            if skipped_owner: parts.append(f"👑 𝐎ᴡɴᴇʀ 𝐏ʀᴏᴛᴇᴄᴛᴇᴅ → `{', '.join(skipped_owner)}`")
            if not parts: parts.append("❌ 𝐍ᴏ 𝐂ʜᴀɴɢᴇs 𝐌ᴀᴅᴇ")
            text = "\n".join(parts)
            if event.out: await safe_edit(event, text)
            else: await event.reply(text)
        except Exception as e:
            await safe_edit(event, f"❌ 𝐀ᴅᴍɪɴ 𝐑ᴇᴍᴏᴠᴇ 𝐄ʀʀ → `{str(e)[:50]}`")


    @register_cmd("admins")
    async def cmd_admins(event, _):
        try:
            await safe_edit(event, "⚡ 𝐅ᴇᴛᴄʜɪɴɢ 𝐀ᴅᴍɪɴ 𝐋ɪsᴛ...\n━━━━━━━━━━━━━━━")
            admin_list = "\n".join(f"• `{a}`" for a in sorted(admins)) if admins else "⚠️ 𝐍ᴏ 𝐄xᴛʀᴀ 𝐀ᴅᴍɪɴs"
            txt = f"👑 𝐀ᴅᴍɪɴ 𝐋ɪsᴛ\n━━━━━━━━━━━━━━━\n👑 𝐎ᴡɴᴇʀ → `{OWNER_ID}`\n\n{admin_list}\n\n📊 𝐓ᴏᴛᴀʟ → `{len(admins)}`"
            await safe_edit(event, txt)
        except Exception as e:
            await safe_edit(event, f"❌ 𝐀ᴅᴍɪɴ 𝐋ɪsᴛ 𝐄ʀʀ → `{str(e)[:50]}`")


    @register_cmd("fighthelp")
    async def cmd_fighthelp(event, _):
        try:
            txt = (
                "╔══════════════════════════════════╗\n"
                "║  ⚔️  𝗕𝗘𝗦𝗧 𝗙𝗜𝗚𝗛𝗧𝗜𝗡𝗚 𝗖𝗢𝗠𝗠𝗔𝗡𝗗𝗦  ⚔️  ║\n"
                "╚══════════════════════════════════╝\n\n"

                "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                "🔥 𝗥𝗔𝗜𝗗 𝗔𝗧𝗧𝗔𝗖𝗞𝗦  (reply karke use karo)\n"
                "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                "`.attack`     💥 Direct attack — seedha maaro\n"
                "`.roast`      🔥 Roast bomb — izzat utaaro\n"
                "`.diss`       😤 Heavy diss — insult level MAX\n"
                "`.savage`     😈 Savage mode — brutal replies\n"
                "`.war`        ⚔️ War mode — continuous attack\n"
                "`.ultra`      ⚡ Ultra power — 3x damage\n"
                "`.doom`       💀 Doom attack — hardest hit\n"
                "`.legend`     👑 Legend mode — GOD level raid\n"
                "`.nuke`       ☢️ Nuclear strike — total annihilation\n"
                "`.storm`      🌪️ Storm mode — relentless assault\n"
                "`.blizzard`   ❄️ Blizzard — freeze and destroy\n"
                "`.venom`      ☠️ Venom — toxic takedown\n\n"

                "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                "🔁 𝗔𝗨𝗧𝗢-𝗥𝗘𝗣𝗟𝗬 𝗥𝗔𝗜𝗗𝗦  (chhod do, khud chalega)\n"
                "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                "`.reply`      🗡️ Auto reply — har msg pe reply\n"
                "`.rr`         🤣 Random reply — alag alag jawab\n"
                "`.hrr`        💗 Heart reply — emoji se chido\n"
                "`.flag`       🚩 Flag raid — flag se bhardo\n"
                "`.replygod`   😈 GOD reply — 3x power, brutal\n"
                "`.replysid <text> <count>`\n"
                "              🎯 Limit raid — X baar reply\n\n"

                "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                "💥 𝗦𝗣𝗔𝗠 / 𝗦𝗣𝗥𝗔𝗬  (chat bhar do)\n"
                "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                "`.spray <text>`        🌊 Spray — ruko mat, bhejo\n"
                "`.spam <n> <text>`     📨 N baar same msg bhejo\n"
                "`.rspam <n> <text>`    💀 Reply + Spam combo (BEAST)\n\n"

                "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                "🔇 𝗠𝗨𝗧𝗘 / 𝗦𝗜𝗟𝗘𝗡𝗖𝗘\n"
                "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                "`.mute`       🔇 Local mute — is chat mein\n"
                "`.gmute`      🔕 Global mute — har jagah\n"
                "`.purge <n>`  🧹 N msgs delete karo\n"
                "`.kick`      👞 Group se bahar nikalo\n\n"

                "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                "🛑 𝗦𝗧𝗢𝗣 𝗖𝗢𝗠𝗠𝗔𝗡𝗗𝗦\n"
                "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                "`.stop`  /  `.stopattack`  — Sab band karo\n"
                "`.sreply` — Auto reply band\n"
                "`.stopspray` — Spray band\n\n"

                "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                "💡 𝗧𝗜𝗣𝗦:\n"
                "• Pehle reply karo target pe, phir command\n"
                "• `.stop` se sab instantly band hoga\n"
                "• `.replygod` + `.spray` combo = 💀 MAX POWER\n"
                "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                "🌟 𝗦𝗜𝗗 𝗔𝗗𝗩𝗔𝗡𝗖𝗘 𝗩𝟯 — 500+ Commands"
            )
            if event.out:
                await safe_edit(event, txt)
            else:
                await event.reply(txt)
        except Exception as e:
            await safe_edit(event, f"❌ Err → `{str(e)[:40]}`")


    @register_cmd("protect")
    async def cmd_protect(event, arg):
        try:
            targets = await get_targets(event, arg)
            if not targets:
                return await safe_edit(event,
                    "🛡️ **PROTECT**\n━━━━━━━━━━━━━━━\n"
                    f"Protected IDs: `{', '.join(str(x) for x in sorted(PROTECTED_IDS)) or 'None'}`\n\n"
                    "Usage: `.protect` (reply) or `.protect <id>`\n"
                    "Remove: `.unprotect` (reply) or `.unprotect <id>`"
                )
            added = []
            for uid in targets:
                PROTECTED_IDS.add(uid)
                added.append(str(uid))
            await safe_edit(event,
                f"🛡️ **Protected** → `{', '.join(added)}`\n"
                "These IDs are now immune to all commands from this userbot."
            )
        except Exception as e:
            await safe_edit(event, f"❌ Protect Err → `{str(e)[:40]}`")


    @register_cmd("unprotect")
    async def cmd_unprotect(event, arg):
        try:
            targets = await get_targets(event, arg)
            if not targets:
                return await safe_edit(event, "❌ No target. Reply or pass ID.")
            removed = []
            for uid in targets:
                if uid in PROTECTED_IDS:
                    PROTECTED_IDS.discard(uid)
                    removed.append(str(uid))
            if removed:
                await safe_edit(event, f"🔓 **Unprotected** → `{', '.join(removed)}`")
            else:
                await safe_edit(event, "⚠️ Those IDs were not protected.")
        except Exception as e:
            await safe_edit(event, f"❌ Unprotect Err → `{str(e)[:40]}`")


    @register_cmd("protectlist")
    async def cmd_protectlist(event, _):
        try:
            if not PROTECTED_IDS:
                return await safe_edit(event, "🛡️ No protected IDs set.")
            lines = "\n".join(f"• `{uid}`" for uid in sorted(PROTECTED_IDS))
            await safe_edit(event,
                f"🛡️ **Protected IDs** ({len(PROTECTED_IDS)})\n━━━━━━━━━━━━━━━\n{lines}"
            )
        except Exception as e:
            await safe_edit(event, f"❌ Err → `{str(e)[:40]}`")


    @register_cmd("ping")
    async def cmd_ping(event, _):
        try:
            t0 = time.perf_counter()
            try:
                if event.out: msg = await event.edit("🏓 𝐏ɪɴɢ...")
                else: msg = await event.reply("🏓 𝐏ɪɴɢ...")
            except: msg = None
            t1 = time.perf_counter()
            ms = round((t1 - t0) * 1000)
            try:
                if msg: await msg.edit(f"🏓 𝐏ᴏɴɢ → `{ms} ms`")
                else: await event.reply(f"🏓 𝐏ᴏɴɢ → `{ms} ms`")
            except: pass
        except Exception as e:
            await safe_edit(event, f"❌ 𝐏ɪɴɢ 𝐄ʀʀ → `{str(e)[:40]}`")


    @register_cmd("alive")
    async def cmd_alive(event, _):
        try:
            elapsed = int(time.time() - START_TIME)
            h, r = divmod(elapsed, 3600)
            m, s = divmod(r, 60)
            uptime_str = f"{h}h {m}m {s}s"
            try:
                me = await bot.get_me()
                uname = f"@{me.username}" if me.username else me.first_name
            except:
                uname = "Unknown"
            txt = (
                "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                "  ⚡️  𝗦𝗜𝗗 𝗔𝗗𝗩𝗔𝗡𝗖𝗘 𝗩𝟯  ⚡️\n"
                "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"🟢  𝐒𝐭𝐚𝐭𝐮𝐬    →  `ALIVE ✅`\n"
                f"👤  𝐀𝐜𝐜𝐨𝐮𝐧𝐭   →  `{uname}`\n"
                f"⏱️  𝐔𝐩𝐭𝐢𝐦𝐞    →  `{uptime_str}`\n"
                f"📦  𝐂𝐨𝐦𝐦𝐚𝐧𝐝𝐬  →  `500+`\n"
                f"⚔️  𝐑𝐚𝐢𝐝𝐬     →  `20 Types`\n"
                f"🔥  𝐕𝐞𝐫𝐬𝐢𝐨𝐧   →  `SIDxBOT✨❤️`\n"
                "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                "💡  𝐐𝐮𝐢𝐜𝐤 𝐒𝐭𝐚𝐫𝐭:\n"
                "    `.ping`   — Speed test karo\n"
                "    `.attack` — Kisi ko attack karo (reply)\n"
                "    `.roast`  — Roast karo (reply)\n"
                "    `.spray`  — Spam spray shuru\n"
                "    `.help`   — Poori commands list\n"
                "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                "🌟  𝐏𝐨𝐰𝐞𝐫𝐞𝐝 𝐛𝐲  𝗦𝗜𝗗𝘅𝗕𝗢𝗧"
            )
            if event.out:
                await safe_edit(event, txt)
            else:
                await event.reply(txt)
        except Exception as e:
            await safe_edit(event, f"❌ 𝐀𝐥𝐢𝐯𝐞 𝐄𝐫𝐫 → `{str(e)[:40]}`")


    @register_cmd("help")
    async def cmd_help_userbot(event, _):
        try:
            txt = (
                "╔══════════════════════════════╗\n"
                "║  📖  𝗖𝗢𝗠𝗠𝗔𝗡𝗗 𝗚𝗨𝗜𝗗𝗘  📖  ║\n"
                "╚══════════════════════════════╝\n\n"
                "💡 𝐏𝐫𝐞𝐟𝐢𝐱: `.`  (𝐝𝐨𝐭)\n"
                "💡 𝐔𝐬𝐞: 𝐀𝐩𝐧𝐚 𝐦𝐞𝐬𝐬𝐚𝐠𝐞 𝐛𝐡𝐞𝐣𝐨 𝐲𝐚 𝐫𝐞𝐩𝐥𝐲 𝐤𝐚𝐫𝐨\n\n"
                "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                "⚡ 𝗕𝗔𝗦𝗜𝗖 (𝐤𝐚𝐡𝐢 𝐛𝐡𝐢 𝐛𝐡𝐞𝐣𝐨)\n"
                "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                "`.alive`  — Bot alive hai ya nahi check karo\n"
                "`.ping`   — Speed test (ms mein)\n"
                "`.status` — Uptime aur info dekho\n"
                "`.id`     — Apna / kisi ka Telegram ID lo\n\n"
                "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                "⚔️ 𝗥𝗔𝗜𝗗 (𝐤𝐢𝐬𝐢 𝐤𝐨 𝐫𝐞𝐩𝐥𝐲 𝐤𝐚𝐫𝐤𝐞)\n"
                "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                "`.attack` — Attack shuru karo\n"
                "`.roast`  — Roast karo\n"
                "`.diss`   — Diss maaro\n"
                "`.war`    — War mode on\n"
                "`.savage` — Savage reply\n"
                "`.ultra`  — Ultra power raid\n"
                "`.doom`   — Doom level attack\n"
                "`.legend` — Legend mode\n"
                "`.nuke`   — ☢️ Nuclear strike\n"
                "`.storm`  — 🌪️ Storm assault\n"
                "`.blizzard`— ❄️ Freeze attack\n"
                "`.venom`  — ☠️ Toxic takedown\n\n"
                "📌 𝐒𝐭𝐨𝐩: `.stop` 𝐲𝐚 `.stopattack`\n\n"
                "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                "💥 𝗦𝗣𝗥𝗔𝗬 / 𝗦𝗣𝗔𝗠\n"
                "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                "`.spray <text>`    — Spray shuru\n"
                "`.stopspray`       — Spray band karo\n"
                "`.spam <n> <text>` — N baar bhejo\n\n"
                "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                "🔁 𝗔𝗨𝗧𝗢-𝗥𝗘𝗣𝗟𝗬 (𝐤𝐢𝐬𝐢 𝐤𝐨 𝐫𝐞𝐩𝐥𝐲 𝐤𝐚𝐫𝐤𝐞)\n"
                "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                "`.reply`    — Auto reply on\n"
                "`.rreply`   — Fun auto reply\n"
                "`.replygod` — Triple power reply\n\n"
                "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                "🛠️ 𝗨𝗧𝗜𝗟𝗜𝗧𝗬\n"
                "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                "`.tts <text>`  — Text to voice\n"
                "`.qr <text>`   — QR code banao\n"
                "`.ytdl <url>`  — YouTube download\n"
                "`.setname <n>` — Naam badlo\n"
                "`.setbio <b>`  — Bio badlo\n\n"
                "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                "📋 𝐏𝐨𝐨𝐫𝐢 𝐥𝐢𝐬𝐭: `.cmds`\n"
                "🌟  𝗦𝗜𝗗𝘅𝗕𝗢𝗧"
            )
            if event.out:
                await safe_edit(event, txt)
            else:
                await event.reply(txt)
        except Exception as e:
            await safe_edit(event, f"❌ Help Err → `{str(e)[:40]}`")


    @register_cmd("cmdlist")
    async def cmd_cmdlist(event, _):
        try:
            txt = (
                "╔══════════════════════════════════╗\n"
                "║  ⚡  𝗦𝗜𝗗 𝗔𝗗𝗩𝗔𝗡𝗖𝗘 𝗩𝟯 — 𝗖𝗠𝗗𝗦  ⚡  ║\n"
                "╚══════════════════════════════════╝\n\n"

                "🔰 ━━━━  𝗕𝗔𝗦𝗜𝗖  ━━━━ 🔰\n"
                "`.alive` `.ping` `.status` `.uptime`\n"
                "`.id` `.info` `.whois` `.chatid`\n\n"

                "⚔️ ━━━━  𝗥𝗔𝗜𝗗 / 𝗙𝗜𝗚𝗛𝗧  ━━━━ ⚔️\n"
                "`.attack` `.roast` `.diss` `.war`\n"
                "`.savage` `.ultra` `.godwar` `.troll`\n"
                "`.shame` `.fire` `.devil` `.karma`\n"
                "`.ghost` `.legend` `.doom` `.combo`\n"
                "`.nuke` `.storm` `.blizzard` `.venom`  ★ NEW\n"
                "🛑 Stop: `.stopall` | Status: `.raidstatus`\n\n"

                "🔁 ━━━━  𝗔𝗨𝗧𝗢-𝗥𝗘𝗣𝗟𝗬  ━━━━ 🔁\n"
                "`.reply` `.rr` `.flag` `.hrr`\n"
                "`.replygod` `.replysid` `.rspam`\n"
                "🛑 Stop: `.sreply` `.srr` `.sflag`\n"
                "        `.shrr` `.sgod` `.sstop`\n\n"

                "💥 ━━━━  𝗦𝗣𝗥𝗔𝗬 / 𝗦𝗣𝗔𝗠  ━━━━ 💥\n"
                "`.spray` `.dspray` `.tspray` `.rspray`\n"
                "`.multispray` `.countspray` `.spraydelay`\n"
                "`.addtext` `.listtexts` `.edittext`\n"
                "`.deltext` `.cleartext`\n\n"

                "🛡️ ━━━━  𝗣𝗥𝗢𝗧𝗘𝗖𝗧𝗜𝗢𝗡  ━━━━ 🛡️\n"
                "`.protect` — Apne aap ko protect karo\n"
                "`.unprotect` — Protection hatao\n"
                "`.protectlist` — Protected list dekho\n"
                "`.antidel` — Deleted messages dekho\n"
                "`.watchspam` — Spam monitor on\n"
                "`.unwatchspam` — Spam monitor off\n"
                "`.watchlist` — Watch list dekho\n"
                "`.lock` `.unlock` — Group lock/unlock\n"
                "`.mute` `.unmute` — User mute karo\n"
                "`.gmute` `.gunmute` — Global mute\n\n"

                "👑 ━━━━  𝗚𝗥𝗢𝗨𝗣 𝗔𝗗𝗠𝗜𝗡  ━━━━ 👑\n"
                "`.ban` `.unban` `.kick` `.promote`\n"
                "`.demote` `.pin` `.unpin` `.purge`\n"
                "`.warn` `.warnlist` `.clearwarn`\n"
                "`.groupinfo` `.membercount` `.invitelink`\n\n"

                "🎭 ━━━━  𝗖𝗟𝗢𝗡𝗘 / 𝗣𝗥𝗢𝗙𝗜𝗟𝗘  ━━━━ 🎭\n"
                "`.copy` — Kisi ka profile clone karo\n"
                "`.normal` — Normal profile restore karo\n"
                "`.setname` `.setbio` `.setpp`\n"
                "`.getpp` `.mention`\n\n"

                "🛠️ ━━━━  𝗨𝗧𝗜𝗟𝗜𝗧𝗬  ━━━━ 🛠️\n"
                "`.tts` `.qr` `.fancy` `.style`\n"
                "`.calc` `.weather` `.ip` `.short`\n"
                "`.crypto` `.translate` `.imdb`\n"
                "`.music` `.dmusic` `.ytdl`\n"
                "`.encode` `.decode` `.b64` `.b64d`\n"
                "`.md5` `.sha256` `.binary` `.morse`\n\n"

                "🎮 ━━━━  𝗙𝗨𝗡  ━━━━ 🎮\n"
                "`.joke` `.fact` `.quote` `.riddle`\n"
                "`.truth` `.dare` `.pickup` `.roastme`\n"
                "`.8ball` `.rps` `.choose` `.flip`\n"
                "`.dice` `.react` `.echo`\n\n"

                "📝 ━━━━  𝗧𝗘𝗫𝗧 𝗧𝗢𝗢𝗟𝗦  ━━━━ 📝\n"
                "`.upper` `.lower` `.reverse` `.bold`\n"
                "`.italic` `.mono` `.zalgo` `.leet`\n"
                "`.camel` `.snake` `.shout` `.shadow`\n"
                "`.rot13` `.big` `.small` `.spaceit`\n\n"

                "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                "⚡ 𝗣𝗼𝘄𝗲𝗿𝗲𝗱 𝗯𝘆 𝗦𝗜𝗗𝘅𝗕𝗢𝗧 | 500+ 𝗖𝗺𝗱𝘀"
            )
            await safe_edit(event, txt)
        except Exception as e:
            await safe_edit(event, f"❌ CmdList Err → `{str(e)[:40]}`")


    @register_cmd("protection")
    async def cmd_protection_info(event, _):
        try:
            txt = (
                "╔══════════════════════════════════╗\n"
                "║  🛡️  𝗦𝗜𝗗 𝗣𝗥𝗢𝗧𝗘𝗖𝗧𝗜𝗢𝗡 𝗦𝗬𝗦𝗧𝗘𝗠  🛡️  ║\n"
                "╚══════════════════════════════════╝\n\n"

                "🔰 ━━━━  𝗦𝗘𝗟𝗙 𝗣𝗥𝗢𝗧𝗘𝗖𝗧𝗜𝗢𝗡  ━━━━ 🔰\n"
                "`.protect` — Reply karke kisi se khud ko protect karo\n"
                "   ↳ Woh tumhe target nahi kar sakta raid mein\n"
                "`.unprotect` — Kisi ki protection hatao\n"
                "`.protectlist` — Kaun protect hai dekho\n\n"

                "👁️ ━━━━  𝗔𝗡𝗧𝗜-𝗗𝗘𝗟𝗘𝗧𝗘  ━━━━ 👁️\n"
                "`.antidel` — ON/OFF karo\n"
                "   ↳ Jab koi message delete kare — tum dekh sakte ho\n\n"

                "🔍 ━━━━  𝗦𝗣𝗔𝗠 𝗪𝗔𝗧𝗖𝗛  ━━━━ 🔍\n"
                "`.watchspam` — Reply karke spam monitor on karo\n"
                "   ↳ Woh X baar message bheje toh auto action\n"
                "`.unwatchspam` — Monitor band karo\n"
                "`.watchlist` — Active monitors dekho\n\n"

                "🔒 ━━━━  𝗚𝗥𝗢𝗨𝗣 𝗟𝗢𝗖𝗞  ━━━━ 🔒\n"
                "`.lock` — Group mein koi action nahi kar sakta\n"
                "`.unlock` — Group unlock karo\n\n"

                "🤫 ━━━━  𝗠𝗨𝗧𝗘 𝗦𝗬𝗦𝗧𝗘𝗠  ━━━━ 🤫\n"
                "`.mute` — Is chat mein mute karo\n"
                "`.unmute` — Unmute karo\n"
                "`.gmute` — Global mute (har jagah)\n"
                "`.gunmute` — Global unmute\n"
                "`.mutelist` — Muted users dekho\n\n"

                "⚠️ ━━━━  𝗪𝗔𝗥𝗡𝗜𝗡𝗚 𝗦𝗬𝗦𝗧𝗘𝗠  ━━━━ ⚠️\n"
                "`.warn` — Warning do\n"
                "`.warnlist` — Warnings dekho\n"
                "`.clearwarn` — Warnings clear karo\n\n"

                "🚫 ━━━━  𝗕𝗔𝗡 / 𝗞𝗜𝗖𝗞  ━━━━ 🚫\n"
                "`.ban` `.unban` — Group se ban/unban\n"
                "`.kick` — Group se nikalo\n\n"

                "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                "💡 𝐓𝐢𝐩: `.protect` + `.antidel` + `.watchspam`\n"
                "   𝐭𝐢𝐧𝐨𝐧 𝐨𝐧 𝐫𝐚𝐤𝐡𝐨 — 𝐟𝐮𝐥𝐥 𝐩𝐫𝐨𝐭𝐞𝐜𝐭𝐢𝐨𝐧 𝐦𝐢𝐥𝐞𝐠𝐢 🛡️\n"
                "⚡ 𝗦𝗜𝗗𝘅𝗕𝗢𝗧"
            )
            await safe_edit(event, txt)
        except Exception as e:
            await safe_edit(event, f"❌ Protection Err → `{str(e)[:40]}`")


    @register_cmd("status")
    async def cmd_status(event, _):
        try:
            now = time.time()
            try: uptime = int(now - START_TIME)
            except: uptime = 0
            if uptime < 0: uptime = 0
            try: admin_count = len(admins)
            except: admin_count = 0
            txt = (
                "✅ 𝐔sᴇʀʙᴏᴛ 𝐒ᴛᴀᴛᴜs 𝐕𝟯\n"
                "━━━━━━━━━━━━━━━\n"
                f"⏱️ 𝐔ᴘᴛɪᴍᴇ → `{uptime}s`\n"
                f"👑 𝐀ᴅᴍɪɴs → `{admin_count}`\n"
                f"⚔️ 𝐑𝐚𝐢𝐝 𝐒𝐞𝐭𝐬 → `20 types`\n"
                f"📦 𝐂𝐨𝐦𝐦𝐚𝐧𝐝𝐬 → `500+`\n"
                f"⚙️ 𝐌ᴏᴅᴇ → `Operational`"
            )
            if event.out: await safe_edit(event, txt)
            else: await event.reply(txt)
        except Exception as e:
            await safe_edit(event, f"❌ 𝐒ᴛᴀᴛᴜs 𝐄ʀʀ → `{str(e)[:40]}`")


    @register_cmd("flip")
    async def cmd_flip(event, _):
        try:
            result = random.choice(["🪙 𝐇ᴇᴀᴅs", "🪙 𝐓ᴀɪʟs"])
            text = f"🎲 𝐂ᴏɪɴ 𝐅ʟɪᴘ\n━━━━━━━━━━━━━━━\n👉 𝐑ᴇsᴜʟᴛ → {result}"
            if event.out: await safe_edit(event, text)
            else: await event.reply(text)
        except Exception as e:
            await safe_edit(event, f"❌ 𝐅ʟɪᴘ 𝐄ʀʀ → `{str(e)[:40]}`")


    @register_cmd("dice")
    async def cmd_dice(event, _):
        try:
            num = random.randint(1, 6)
            faces = {1:"⚀",2:"⚁",3:"⚂",4:"⚃",5:"⚄",6:"⚅"}
            text = f"🎲 𝐃ɪᴄᴇ 𝐑ᴏʟʟ\n━━━━━━━━━━━━━━━\n👉 {faces.get(num, str(num))} → `{num}`"
            if event.out: await safe_edit(event, text)
            else: await event.reply(text)
        except Exception as e:
            await safe_edit(event, f"❌ 𝐃ɪᴄᴇ 𝐄ʀʀ → `{str(e)[:40]}`")


    @register_cmd("mute", needs_reply=True)
    async def cmd_mute(event, arg):
        try:
            targets = await get_targets(event, arg)
            if not targets:
                return await safe_edit(event, "❌ 𝐍ᴏ 𝐓ᴀʀɢᴇᴛ\n👉 `.mute` (reply / @username / id)")
            await safe_edit(event, "⚡ 𝐏ʀᴏᴄᴇssɪɴɢ 𝐌ᴜᴛᴇ...\n━━━━━━━━━━━━━━━")
            added, already = [], []
            for uid in targets:
                try: uid = int(uid)
                except: continue
                if uid in muted_users: already.append(str(uid))
                else: muted_users.add(uid); added.append(str(uid))
            parts = []
            if added: parts.append(f"🔇 𝐌ᴜᴛᴇᴅ → `{', '.join(added)}`")
            if already: parts.append(f"⚠️ 𝐀ʟʀᴇᴀᴅʏ → `{', '.join(already)}`")
            if not parts: parts.append("❌ 𝐍ᴏ 𝐂ʜᴀɴɢᴇ")
            msg = "\n".join(parts)
            if event.out: await safe_edit(event, msg)
            else: await event.reply(msg)
        except Exception as e:
            await safe_edit(event, f"❌ 𝐌ᴜᴛᴇ 𝐄ʀʀ → `{str(e)[:40]}`")


    @register_cmd("unmute", needs_reply=True)
    async def cmd_unmute(event, arg):
        try:
            targets = await get_targets(event, arg)
            if not targets:
                return await safe_edit(event, "❌ 𝐍ᴏ 𝐓ᴀʀɢᴇᴛ\n👉 `.unmute` (reply / @username / id)")
            await safe_edit(event, "⚡ 𝐏ʀᴏᴄᴇssɪɴɢ 𝐔ɴᴍᴜᴛᴇ...\n━━━━━━━━━━━━━━━")
            removed, not_muted = [], []
            for uid in targets:
                try: uid = int(uid)
                except: continue
                if uid in muted_users: muted_users.remove(uid); removed.append(str(uid))
                else: not_muted.append(str(uid))
            parts = []
            if removed: parts.append(f"🗣️ 𝐔ɴᴍᴜᴛᴇ → `{', '.join(removed)}`")
            if not_muted: parts.append(f"⚠️ 𝐍ᴏᴛ 𝐌ᴜᴛᴇᴅ → `{', '.join(not_muted)}`")
            if not parts: parts.append("❌ 𝐍ᴏ 𝐂ʜᴀɴɢᴇ")
            msg = "\n".join(parts)
            if event.out: await safe_edit(event, msg)
            else: await event.reply(msg)
        except Exception as e:
            await safe_edit(event, f"❌ 𝐔ɴᴍᴜᴛᴇ 𝐄ʀʀ → `{str(e)[:40]}`")


    @register_cmd("gmute", needs_reply=True)
    async def cmd_gmute(event, arg):
        try:
            targets = await get_targets(event, arg)
            if not targets:
                return await safe_edit(event, "❌ 𝐍ᴏ 𝐓ᴀʀɢᴇᴛ")
            await safe_edit(event, "⚡ 𝐏ʀᴏᴄᴇssɪɴɢ 𝐆ᴍᴜᴛᴇ...\n━━━━━━━━━━━━━━━")
            added, already = [], []
            for uid in targets:
                try: uid = int(uid)
                except: continue
                if uid in global_muted: already.append(str(uid))
                else: global_muted.add(uid); added.append(str(uid))
            parts = []
            if added: parts.append(f"🔕 𝐆ᴍᴜᴛᴇ → `{', '.join(added)}`")
            if already: parts.append(f"⚠️ 𝐀ʟʀᴇᴀᴅʏ → `{', '.join(already)}`")
            if not parts: parts.append("❌ 𝐍ᴏ 𝐂ʜᴀɴɢᴇ")
            msg = "\n".join(parts)
            if event.out: await safe_edit(event, msg)
            else: await event.reply(msg)
        except Exception as e:
            await safe_edit(event, f"❌ 𝐆ᴍᴜᴛᴇ 𝐄ʀʀ → `{str(e)[:40]}`")


    @register_cmd("gunmute", needs_reply=True)
    async def cmd_gunmute(event, arg):
        try:
            targets = await get_targets(event, arg)
            if not targets:
                return await safe_edit(event, "❌ 𝐍ᴏ 𝐓ᴀʀɢᴇᴛ")
            await safe_edit(event, "⚡ 𝐏ʀᴏᴄᴇssɪɴɢ 𝐆ᴜɴᴍᴜᴛᴇ...\n━━━━━━━━━━━━━━━")
            removed, not_muted = [], []
            for uid in targets:
                try: uid = int(uid)
                except: continue
                if uid in global_muted: global_muted.remove(uid); removed.append(str(uid))
                else: not_muted.append(str(uid))
            parts = []
            if removed: parts.append(f"🔊 𝐆ᴜɴᴍᴜᴛᴇ → `{', '.join(removed)}`")
            if not_muted: parts.append(f"⚠️ 𝐍ᴏᴛ 𝐆ᴍᴜᴛᴇᴅ → `{', '.join(not_muted)}`")
            if not parts: parts.append("❌ 𝐍ᴏ 𝐂ʜᴀɴɢᴇ")
            msg = "\n".join(parts)
            if event.out: await safe_edit(event, msg)
            else: await event.reply(msg)
        except Exception as e:
            await safe_edit(event, f"❌ 𝐆𝐔𝐍𝐌𝐔𝐓𝐄 𝐄ʀʀ → `{str(e)[:40]}`")


    @register_cmd("mutelist")
    async def cmd_mutelist(event, _):
        try:
            local_list = "\n".join(f"• `{x}`" for x in sorted(muted_users)) if muted_users else "None"
            global_list = "\n".join(f"• `{x}`" for x in sorted(global_muted)) if global_muted else "None"
            text = (
                "🔇 𝐌𝐔𝐓𝐄 𝐋𝐈𝐒𝐓\n"
                "━━━━━━━━━━━━━━━\n"
                f"🔇 𝐋𝐨𝐜𝐚𝐥:\n{local_list}\n\n"
                f"🔕 𝐆𝐥𝐨𝐛𝐚𝐥:\n{global_list}"
            )
            await safe_edit(event, text)
        except Exception as e:
            await safe_edit(event, f"❌ 𝐌𝐔𝐓𝐄𝐋𝐈𝐒𝐓 𝐄ʀʀ → `{str(e)[:40]}`")


    @register_cmd("purge")
    async def cmd_purge(event, arg):
        try:
            try: count = int(arg) if arg else 50
            except: count = 50
            if count < 1: count = 1
            if count > 200: count = 200
            await safe_edit(event, "⚡ 𝐏ᴜʀɢɪɴɢ 𝐌ᴇssᴀɢᴇs...\n━━━━━━━━━━━━━━━")
            msgs = []
            async for m in bot.iter_messages(event.chat_id, limit=count + 1):
                msgs.append(m.id)
            if not msgs:
                return await safe_edit(event, "⚠️ 𝐍ᴏ 𝐌ᴇssᴀɢᴇs 𝐅ᴏᴜɴᴅ")
            try: await bot.delete_messages(event.chat_id, msgs)
            except FloodWaitError as fw:
                await asyncio.sleep(fw.seconds)
                await bot.delete_messages(event.chat_id, msgs)
            except RPCError: pass
            text = f"🧹 𝐏ᴜʀɢᴇ 𝐂ᴏᴍᴘʟᴇᴛᴇ\n━━━━━━━━━━━━━━━\n🗑️ 𝐃ᴇʟᴇᴛᴇᴅ → `{max(len(msgs)-1,0)}`"
            if event.out: await safe_edit(event, text)
            else: await event.reply(text)
        except Exception as e:
            await safe_edit(event, f"❌ 𝐏ᴜʀɢᴇ 𝐄ʀʀ → `{str(e)[:40]}`")


    @register_cmd("throw", needs_reply=True, group_only=True)
    async def cmd_throw(event, arg):
        try:
            targets = await get_targets(event, arg)
            if not targets:
                return await safe_edit(event, "❌ 𝐍ᴏ 𝐓ᴀʀɢᴇᴛ")
            try:
                perms = await bot.get_permissions(event.chat_id, 'me')
                if not perms.is_admin:
                    return await safe_edit(event, "❌ 𝐍ᴏ 𝐀ᴅᴍɪɴ 𝐑ɪɢʜᴛs")
            except:
                return await safe_edit(event, "❌ 𝐏ᴇʀᴍɪssɪᴏɴ 𝐂ʜᴇᴄᴋ 𝐅ᴀɪʟ")
            await safe_edit(event, "⚡ 𝐊ɪᴄᴋɪɴɢ 𝐓ᴀʀɢᴇᴛs...\n━━━━━━━━━━━━━━━")
            kicked, failed, skipped = [], [], []
            me = await bot.get_me()
            for uid in targets:
                try: uid = int(uid)
                except: continue
                if uid == me.id: skipped.append(str(uid)); continue
                try: await bot.kick_participant(event.chat_id, uid); kicked.append(str(uid))
                except: failed.append(str(uid))
            parts = []
            if kicked: parts.append(f"👞 𝐊ɪᴄᴋᴇᴅ → `{', '.join(kicked)}`")
            if failed: parts.append(f"⚠️ 𝐅ᴀɪʟᴇᴅ → `{', '.join(failed)}`")
            if skipped: parts.append(f"👑 𝐒ᴇʟғ 𝐒ᴋɪᴘ → `{', '.join(skipped)}`")
            if not parts: parts.append("❌ 𝐍ᴏ 𝐀ᴄᴛɪᴏɴ")
            msg = "\n".join(parts)
            if event.out: await safe_edit(event, msg)
            else: await event.reply(msg)
        except Exception as e:
            await safe_edit(event, f"❌ 𝐓ʜʀᴏᴡ 𝐄ʀʀ → `{str(e)[:40]}`")


    # ─── LOCK / UNLOCK ───
    @register_cmd("lock", group_only=True)
    async def cmd_lock(event, _):
        try:
            group_locks.add(event.chat_id)
            await safe_edit(event, "🔒 𝐆ʀᴏᴜᴘ 𝐋ᴏᴄᴋᴇᴅ — 𝐎ɴʟʏ 𝐀ᴅᴍɪɴs 𝐂ᴀɴ 𝐌ᴇssᴀɢᴇ")
        except Exception as e:
            await safe_edit(event, f"❌ 𝐋ᴏᴄᴋ 𝐄ʀʀ → `{str(e)[:40]}`")


    @register_cmd("unlock", group_only=True)
    async def cmd_unlock(event, _):
        try:
            group_locks.discard(event.chat_id)
            await safe_edit(event, "🔓 𝐆ʀᴏᴜᴘ 𝐔ɴʟᴏᴄᴋᴇᴅ — 𝐄𝐯𝐞𝐫𝐲𝐨𝐧𝐞 𝐂𝐚𝐧 𝐌ᴇssᴀɢᴇ")
        except Exception as e:
            await safe_edit(event, f"❌ 𝐔ɴʟᴏᴄᴋ 𝐄ʀʀ → `{str(e)[:40]}`")


    # ─── ADDBOTS ───
    @register_cmd("addbots")
    async def cmd_addbots(event, arg):
        try:
            try: count = max(1, min(int(arg), len(ADD_BOTS_LIST))) if arg else len(ADD_BOTS_LIST)
            except: count = len(ADD_BOTS_LIST)
            await safe_edit(event, f"⚡ 𝐀ᴅᴅɪɴɢ {count} 𝐁ᴏᴛs...\n━━━━━━━━━━━━━━━")
            added, failed = [], []
            for b in ADD_BOTS_LIST[:count]:
                try:
                    await bot(functions.messages.AddChatUserRequest(chat_id=event.chat_id, user_id=b, fwd_limit=10))
                    added.append(b)
                except:
                    try:
                        await bot(functions.channels.InviteToChannelRequest(channel=event.chat_id, users=[b]))
                        added.append(b)
                    except: failed.append(b)
                await asyncio.sleep(1)
            parts = []
            if added: parts.append(f"✅ 𝐀ᴅᴅᴇᴅ → `{len(added)}`")
            if failed: parts.append(f"⚠️ 𝐅ᴀɪʟᴇᴅ → `{len(failed)}`")
            await safe_edit(event, "\n".join(parts) or "❌ 𝐍𝐨 𝐑𝐞𝐬𝐮𝐥𝐭")
        except Exception as e:
            await safe_edit(event, f"❌ 𝐀𝐃𝐃𝐁𝐎𝐓𝐒 𝐄ʀʀ → `{str(e)[:40]}`")


    # ─── ORIGINAL RAID COMMANDS ───
    @register_cmd("reply", needs_reply=True)
    async def cmd_reply(event, arg):
        try:
            targets = await get_targets(event, arg)
            if not targets:
                return await safe_edit(event, "❌ 𝐍ᴏ 𝐓ᴀʀɢᴇᴛ")
            for uid in targets: reply_users.add(uid)
            await safe_edit(event, f"⚔️ 𝐑ᴇᴘʟʏ 𝐑𝐚𝐢𝐝 𝐎𝐧 → `{len(targets)}` ᴛᴀʀɢᴇᴛs")
        except Exception as e:
            await safe_edit(event, f"❌ 𝐑𝐞𝐩𝐥𝐲 𝐄ʀʀ → `{str(e)[:40]}`")


    @register_cmd("sreply")
    async def cmd_sreply(event, arg):
        try:
            targets = await get_targets(event, arg)
            if targets:
                stopped = [str(uid) for uid in targets if uid in reply_users]
                for uid in targets: reply_users.discard(uid)
                await safe_edit(event, f"🛑 𝐑ᴇᴘʟʏ 𝐎ғғ → `{', '.join(stopped)}`" if stopped else "⚠️ 𝐍ᴏᴛ 𝐀ᴄᴛɪᴠᴇ")
            else:
                reply_users.clear()
                await safe_edit(event, "🛑 𝐑ᴇᴘʟʏ 𝐎ғғ — 𝐀ʟʟ 𝐔sᴇʀs")
        except Exception as e:
            await safe_edit(event, f"❌ 𝐒𝐑𝐄𝐏𝐋𝐘 𝐄ʀʀ → `{str(e)[:40]}`")


    @register_cmd("rr", needs_reply=True)
    async def cmd_rr(event, arg):
        try:
            targets = await get_targets(event, arg)
            if not targets: return await safe_edit(event, "❌ 𝐍ᴏ 𝐓ᴀʀɢᴇᴛ")
            for uid in targets: rr_users.add(uid)
            await safe_edit(event, f"🤣 𝐑𝐑 𝐑𝐚𝐢𝐝 𝐎𝐧 → `{len(targets)}` ᴛᴀʀɢᴇᴛs")
        except Exception as e:
            await safe_edit(event, f"❌ 𝐑𝐑 𝐄ʀʀ → `{str(e)[:40]}`")


    @register_cmd("srr")
    async def cmd_srr(event, arg):
        try:
            targets = await get_targets(event, arg)
            if targets:
                for uid in targets: rr_users.discard(uid)
                await safe_edit(event, "🛑 𝐑𝐑 𝐎ғғ")
            else:
                rr_users.clear()
                await safe_edit(event, "🛑 𝐑𝐑 𝐎ғғ — 𝐀ʟʟ 𝐔sᴇʀs")
        except Exception as e:
            await safe_edit(event, f"❌ 𝐒𝐑𝐑 𝐄ʀʀ → `{str(e)[:40]}`")


    @register_cmd("flag", needs_reply=True)
    async def cmd_flag(event, arg):
        try:
            targets = await get_targets(event, arg)
            if not targets: return await safe_edit(event, "❌ 𝐍ᴏ 𝐓ᴀʀɢᴇᴛ")
            for uid in targets: flag_users.add(uid)
            await safe_edit(event, f"🚩 𝐅ʟᴀɢ 𝐑𝐚𝐢𝐝 𝐎𝐧 → `{len(targets)}` ᴛᴀʀɢᴇᴛs")
        except Exception as e:
            await safe_edit(event, f"❌ 𝐅ʟᴀɢ 𝐄ʀʀ → `{str(e)[:40]}`")


    @register_cmd("sflag")
    async def cmd_sflag(event, arg):
        try:
            targets = await get_targets(event, arg)
            if targets:
                for uid in targets: flag_users.discard(uid)
                await safe_edit(event, "🛑 𝐅ʟᴀɢ 𝐎ғғ")
            else:
                flag_users.clear()
                await safe_edit(event, "🛑 𝐅ʟᴀɢ 𝐎ғғ — 𝐀ʟʟ")
        except Exception as e:
            await safe_edit(event, f"❌ 𝐒𝐅𝐋𝐀𝐆 𝐄ʀʀ → `{str(e)[:40]}`")


    @register_cmd("hrr", needs_reply=True)
    async def cmd_hrr(event, arg):
        try:
            targets = await get_targets(event, arg)
            if not targets: return await safe_edit(event, "❌ 𝐍ᴏ 𝐓ᴀʀɢᴇᴛ")
            for uid in targets: hrr_users.add(uid)
            await safe_edit(event, f"💗 𝐇𝐞𝐚𝐫𝐭 𝐑𝐚𝐢𝐝 𝐎𝐧 → `{len(targets)}` ᴛᴀʀɢᴇᴛs")
        except Exception as e:
            await safe_edit(event, f"❌ 𝐇𝐑𝐑 𝐄ʀʀ → `{str(e)[:40]}`")


    @register_cmd("shrr")
    async def cmd_shrr(event, arg):
        try:
            targets = await get_targets(event, arg)
            if targets:
                for uid in targets: hrr_users.discard(uid)
                await safe_edit(event, "🛑 𝐇𝐞𝐚𝐫𝐭 𝐎ғғ")
            else:
                hrr_users.clear()
                await safe_edit(event, "🛑 𝐇𝐑𝐑 𝐎ғғ — 𝐀ʟʟ")
        except Exception as e:
            await safe_edit(event, f"❌ 𝐒𝐇𝐑𝐑 𝐄ʀʀ → `{str(e)[:40]}`")


    @register_cmd("replygod", needs_reply=True)
    async def cmd_replygod(event, arg):
        try:
            targets = await get_targets(event, arg)
            if not targets: return await safe_edit(event, "❌ 𝐍ᴏ 𝐓ᴀʀɢᴇᴛ")
            for uid in targets: replygod_users.add(uid)
            await safe_edit(event, f"😈 𝐆𝐨𝐝 𝐑𝐚𝐢𝐝 𝐎𝐧 → `{len(targets)}` ᴛᴀʀɢᴇᴛs")
        except Exception as e:
            await safe_edit(event, f"❌ 𝐑𝐄𝐏𝐋𝐘𝐆𝐎𝐃 𝐄ʀʀ → `{str(e)[:40]}`")


    @register_cmd("sgod")
    async def cmd_sgod(event, arg):
        try:
            targets = await get_targets(event, arg)
            if targets:
                for uid in targets: replygod_users.discard(uid)
                await safe_edit(event, "🛑 𝐆𝐨𝐝 𝐎ғғ")
            else:
                replygod_users.clear()
                await safe_edit(event, "🛑 𝐆𝐨𝐝 𝐎ғғ — 𝐀ʟʟ")
        except Exception as e:
            await safe_edit(event, f"❌ 𝐒𝐆𝐎𝐃 𝐄ʀʀ → `{str(e)[:40]}`")


    @register_cmd("replysid", needs_reply=True)
    async def cmd_replysid(event, arg):
        try:
            targets = await get_targets(event, "")
            parts = arg.strip().rsplit(None, 1) if arg else []
            if len(parts) < 2:
                return await safe_edit(event, "❌ 𝐔𝐬𝐞 → `.replysid <text> <count>`")
            text_part = parts[0].strip()
            try: count = int(parts[1].strip())
            except: return await safe_edit(event, "❌ 𝐈𝐧𝐯𝐚𝐥𝐢𝐝 𝐜𝐨𝐮𝐧𝐭")
            count = max(1, min(count, 500))
            if not targets: return await safe_edit(event, "❌ 𝐍𝐨 𝐭𝐚𝐫𝐠𝐞𝐭")
            for uid in targets:
                replysid_users[uid] = {"text": text_part, "count": count}
            await safe_edit(event, f"🎯 𝐋𝐢𝐦𝐢𝐭 𝐑𝐚𝐢𝐝 𝐎𝐧 → `{count}` 𝐫𝐞𝐩𝐥𝐢𝐞𝐬")
        except Exception as e:
            await safe_edit(event, f"❌ 𝐑𝐘 𝐄ʀʀ → `{str(e)[:40]}`")


    @register_cmd("sstop")
    async def cmd_sstop(event, arg):
        try:
            targets = await get_targets(event, arg)
            if targets:
                for uid in targets: replysid_users.pop(uid, None)
                await safe_edit(event, "🛑 𝐋𝐢𝐦𝐢𝐭 𝐑𝐚𝐢𝐝 𝐎ғғ")
            else:
                replysid_users.clear()
                await safe_edit(event, "🛑 𝐀𝐥𝐥 𝐋𝐢𝐦𝐢𝐭 𝐑𝐚𝐢𝐝𝐬 𝐒𝐭𝐨𝐩𝐩𝐞𝐝")
        except Exception as e:
            await safe_edit(event, f"❌ 𝐒𝐒𝐓𝐎𝐏 𝐄ʀʀ → `{str(e)[:40]}`")


    # ─── MEGA COMBO ──────────────────────────────────────────────────────────────
    @register_cmd("combo", needs_reply=True)
    async def cmd_combo(event, arg):
        try:
            targets = await get_targets(event, arg)
            if not targets:
                return await safe_edit(event,
                    "⚡ **COMBO**\n━━━━━━━━━━━━━━━\n"
                    "Usage: reply karke `.combo` bhejo\n"
                    "Optional: `.combo <spray_text>`\n\n"
                    "Kya karta hai:\n"
                    "🗡️ Auto reply ON\n"
                    "🤣 Random reply ON\n"
                    "💗 Heart reply ON\n"
                    "😈 God reply ON\n"
                    "🚩 Flag raid ON\n"
                    "🌊 Spray shuru (text optional)\n\n"
                    "Sab band karne ke liye → `.stopcombo`"
                )

            spray_text = arg.strip() if arg.strip() else "😂💀🔥"

            # Activate all raid sets on targets
            for uid in targets:
                reply_users.add(uid)
                rr_users.add(uid)
                hrr_users.add(uid)
                replygod_users.add(uid)
                flag_users.add(uid)

            # Also start spray in background
            async def _spray_loop():
                for _ in range(500):
                    try:
                        await event.respond(spray_text)
                        await asyncio.sleep(SPRAY_DELAY)
                    except FloodWaitError as fw:
                        await asyncio.sleep(fw.seconds)
                    except asyncio.CancelledError:
                        break
                    except:
                        break

            task = asyncio.ensure_future(_spray_loop())
            spray_tasks[event.chat_id] = task

            uid_list = ", ".join(f"`{u}`" for u in targets)
            await safe_edit(event,
                "╔══════════════════════════════╗\n"
                "║  💀  𝗠𝗘𝗚𝗔 𝗖𝗢𝗠𝗕𝗢 𝗔𝗖𝗧𝗜𝗩𝗔𝗧𝗘𝗗  💀  ║\n"
                "╚══════════════════════════════╝\n\n"
                f"🎯 𝗧𝗮𝗿𝗴𝗲𝘁𝘀 → {uid_list}\n\n"
                "🗡️ Auto Reply     → ✅ ON\n"
                "🤣 Random Reply   → ✅ ON\n"
                "💗 Heart Reply    → ✅ ON\n"
                "😈 God Reply      → ✅ ON\n"
                "🚩 Flag Raid      → ✅ ON\n"
                f"🌊 Spray          → ✅ ON (`{spray_text}`)\n\n"
                "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                "🛑 Band karne ke liye → `.stopcombo`\n"
                "🌟 𝗦𝗜𝗗 𝗔𝗗𝗩𝗔𝗡𝗖𝗘 — MAX POWER 💀"
            )
        except Exception as e:
            await safe_edit(event, f"❌ Combo Err → `{str(e)[:40]}`")


    @register_cmd("stopcombo")
    async def cmd_stopcombo(event, arg):
        try:
            targets = await get_targets(event, arg)

            # Stop all raid sets for targets (or all if no target)
            if targets:
                for uid in targets:
                    reply_users.discard(uid)
                    rr_users.discard(uid)
                    hrr_users.discard(uid)
                    replygod_users.discard(uid)
                    flag_users.discard(uid)
                    replysid_users.pop(uid, None)
            else:
                reply_users.clear()
                rr_users.clear()
                hrr_users.clear()
                replygod_users.clear()
                flag_users.clear()
                replysid_users.clear()

            # Stop spray
            task = spray_tasks.pop(event.chat_id, None)
            if task:
                task.cancel()

            await safe_edit(event,
                "🛑 **COMBO STOPPED**\n"
                "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                "✅ Auto Reply    → OFF\n"
                "✅ Random Reply  → OFF\n"
                "✅ Heart Reply   → OFF\n"
                "✅ God Reply     → OFF\n"
                "✅ Flag Raid     → OFF\n"
                "✅ Spray         → OFF\n"
                "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                "Sab kuch band ho gaya ✌️"
            )
        except Exception as e:
            await safe_edit(event, f"❌ StopCombo Err → `{str(e)[:40]}`")


    # ─── REPLY + SPAM COMBO ─────────────────────────────────────────────────────
    @register_cmd("rspam", needs_reply=True)
    async def cmd_rspam(event, arg):
        try:
            targets = await get_targets(event, "")
            if not targets:
                return await safe_edit(event, "❌ 𝐊𝐢𝐬𝐢 𝐤𝐨 𝐫𝐞𝐩𝐥𝐲 𝐤𝐚𝐫𝐤𝐞 𝐛𝐡𝐞𝐣𝐨")
            parts = arg.strip().split(None, 1) if arg else []
            if len(parts) < 2:
                return await safe_edit(event,
                    "❌ 𝐔𝐬𝐞 → `.rspam <count> <text>`\n"
                    "📌 𝐄𝐱𝐚𝐦𝐩𝐥𝐞 → `.rspam 5 Randi 😂`\n"
                    "🛑 𝐒𝐭𝐨𝐩 → `.stoprspam`"
                )
            try: count = max(1, min(int(parts[0].strip()), 50))
            except: return await safe_edit(event, "❌ 𝐈𝐧𝐯𝐚𝐥𝐢𝐝 𝐜𝐨𝐮𝐧𝐭 — 𝐧𝐮𝐦𝐛𝐞𝐫 𝐝𝐚𝐥𝐨")
            text = parts[1].strip()
            for uid in targets:
                rspam_users[uid] = {"text": text, "count": count}
            names = ", ".join(f"`{u}`" for u in targets)
            await safe_edit(event,
                f"💥 **Reply+Spam MODE ON**\n"
                f"━━━━━━━━━━━━━━━━━━━━\n"
                f"🎯 𝐓𝐚𝐫𝐠𝐞𝐭  → {names}\n"
                f"🔁 𝐑𝐞𝐩𝐥𝐢𝐞𝐬 → `{count}x` per message\n"
                f"📝 𝐓𝐞𝐱𝐭   → `{text[:40]}`\n"
                f"━━━━━━━━━━━━━━━━━━━━\n"
                f"🛑 𝐒𝐭𝐨𝐩 → `.stoprspam`"
            )
        except Exception as e:
            await safe_edit(event, f"❌ 𝐑𝐒𝐩𝐚𝐦 𝐄ʀʀ → `{str(e)[:40]}`")


    @register_cmd("stoprspam")
    async def cmd_stoprspam(event, arg):
        try:
            targets = await get_targets(event, arg)
            if targets:
                stopped = []
                for uid in targets:
                    if uid in rspam_users:
                        rspam_users.pop(uid)
                        stopped.append(uid)
                if stopped:
                    await safe_edit(event, f"🛑 𝐑𝐞𝐩𝐥𝐲+𝐒𝐩𝐚𝐦 𝐎ғғ → {len(stopped)} user(s)")
                else:
                    await safe_edit(event, "⚠️ 𝐔𝐬𝐞𝐫 𝐦𝐞𝐢𝐧 𝐑𝐒𝐩𝐚𝐦 𝐧𝐚𝐡𝐢 𝐭𝐡𝐚")
            else:
                count = len(rspam_users)
                rspam_users.clear()
                await safe_edit(event, f"🛑 𝐀𝐥𝐥 𝐑𝐞𝐩𝐥𝐲+𝐒𝐩𝐚𝐦 𝐒𝐭𝐨𝐩𝐩𝐞𝐝 ({count} users)")
        except Exception as e:
            await safe_edit(event, f"❌ 𝐒𝐭𝐨𝐩𝐑𝐒𝐩𝐚𝐦 𝐄ʀʀ → `{str(e)[:40]}`")


    # ─── SPRAY ENGINE ───
    @register_cmd("spray")
    async def cmd_spray(event, arg):
        try:
            chat = event.chat_id
            if not arg:
                return await safe_edit(event, "❌ 𝐔𝐬𝐞 → `.spray <text>`")
            if chat in spray_tasks:
                spray_tasks[chat].cancel()
                del spray_tasks[chat]
            async def do_spray():
                while True:
                    try:
                        await bot.send_message(chat, arg)
                        await asyncio.sleep(SPRAY_DELAY)
                    except FloodWaitError as fw:
                        await asyncio.sleep(fw.seconds)
                    except asyncio.CancelledError: break
                    except: break
            spray_tasks[chat] = asyncio.create_task(do_spray())
            await safe_edit(event, f"💣 𝐒𝐩𝐫𝐚𝐲 𝐒𝐭𝐚𝐫𝐭𝐞𝐝\n📝 `{arg[:50]}`")
        except Exception as e:
            await safe_edit(event, f"❌ 𝐒𝐩𝐫𝐚𝐲 𝐄ʀʀ → `{str(e)[:40]}`")


    @register_cmd("dspray")
    async def cmd_dspray(event, _):
        try:
            chat = event.chat_id
            if chat in spray_tasks:
                spray_tasks[chat].cancel()
                del spray_tasks[chat]
                await safe_edit(event, "🛑 𝐒𝐩𝐫𝐚𝐲 𝐒𝐭𝐨𝐩𝐩𝐞𝐝")
            else:
                await safe_edit(event, "⚠️ 𝐍𝐨 𝐀𝐜𝐭𝐢𝐯𝐞 𝐒𝐩𝐫𝐚𝐲")
        except Exception as e:
            await safe_edit(event, f"❌ 𝐃𝐒𝐩𝐫𝐚𝐲 𝐄ʀʀ → `{str(e)[:40]}`")


    @register_cmd("spraydelay")
    async def cmd_spraydelay(event, arg):
        global SPRAY_DELAY
        try:
            if not arg:
                return await safe_edit(event, f"⚡ 𝐂𝐮𝐫𝐫𝐞𝐧𝐭 𝐃𝐞𝐥𝐚𝐲 → `{SPRAY_DELAY}s`")
            SPRAY_DELAY = max(0.05, float(arg))
            await safe_edit(event, f"⚡ 𝐃𝐞𝐥𝐚𝐲 → `{SPRAY_DELAY}s`")
        except Exception as e:
            await safe_edit(event, f"❌ 𝐒𝐃𝐞𝐥𝐚𝐲 𝐄ʀʀ → `{str(e)[:40]}`")


    @register_cmd("tspray")
    async def cmd_tspray(event, arg):
        try:
            chat = event.chat_id
            if not arg or not arg.strip().isdigit():
                return await safe_edit(event, "❌ 𝐔𝐬𝐞 → `.tspray <slot_number>`")
            idx = int(arg.strip()) - 1
            if not spam_texts or idx < 0 or idx >= len(spam_texts):
                return await safe_edit(event, "❌ 𝐈𝐧𝐯𝐚𝐥𝐢𝐝 𝐬𝐥𝐨𝐭")
            text = spam_texts[idx]
            if chat in spray_tasks: spray_tasks[chat].cancel(); del spray_tasks[chat]
            async def do_tspray():
                while True:
                    try:
                        await bot.send_message(chat, text)
                        await asyncio.sleep(SPRAY_DELAY)
                    except FloodWaitError as fw: await asyncio.sleep(fw.seconds)
                    except asyncio.CancelledError: break
                    except: break
            spray_tasks[chat] = asyncio.create_task(do_tspray())
            await safe_edit(event, f"💣 𝐓𝐬𝐩𝐫𝐚𝐲 𝐒𝐥𝐨𝐭 `{idx+1}`")
        except Exception as e:
            await safe_edit(event, f"❌ 𝐓𝐒𝐩𝐫𝐚𝐲 𝐄ʀʀ → `{str(e)[:40]}`")


    @register_cmd("rspray")
    async def cmd_rspray(event, _):
        try:
            chat = event.chat_id
            if not spam_texts:
                return await safe_edit(event, "❌ 𝐍𝐨 𝐬𝐚𝐯𝐞𝐝 𝐭𝐞𝐱𝐭𝐬")
            if chat in spray_tasks: spray_tasks[chat].cancel(); del spray_tasks[chat]
            async def do_rspray():
                while True:
                    try:
                        await bot.send_message(chat, random.choice(spam_texts))
                        await asyncio.sleep(SPRAY_DELAY)
                    except FloodWaitError as fw: await asyncio.sleep(fw.seconds)
                    except asyncio.CancelledError: break
                    except: break
            spray_tasks[chat] = asyncio.create_task(do_rspray())
            await safe_edit(event, "💣 𝐑𝐚𝐧𝐝𝐨𝐦 𝐒𝐩𝐫𝐚𝐲 𝐒𝐭𝐚𝐫𝐭𝐞𝐝")
        except Exception as e:
            await safe_edit(event, f"❌ 𝐑𝐒𝐩𝐫𝐚𝐲 𝐄ʀʀ → `{str(e)[:40]}`")


    @register_cmd("multispray")
    async def cmd_multispray(event, _):
        try:
            chat = event.chat_id
            if not spam_texts:
                return await safe_edit(event, "❌ 𝐍𝐨 𝐬𝐚𝐯𝐞𝐝 𝐭𝐞𝐱𝐭𝐬")
            if chat in spray_tasks: spray_tasks[chat].cancel(); del spray_tasks[chat]
            idx = [0]
            async def do_multi():
                while True:
                    try:
                        await bot.send_message(chat, spam_texts[idx[0] % len(spam_texts)])
                        idx[0] += 1
                        await asyncio.sleep(SPRAY_DELAY)
                    except FloodWaitError as fw: await asyncio.sleep(fw.seconds)
                    except asyncio.CancelledError: break
                    except: break
            spray_tasks[chat] = asyncio.create_task(do_multi())
            await safe_edit(event, "💣 𝐌𝐮𝐥𝐭𝐢𝐬𝐩𝐫𝐚𝐲 𝐒𝐭𝐚𝐫𝐭𝐞𝐝")
        except Exception as e:
            await safe_edit(event, f"❌ 𝐌𝐮𝐥𝐭𝐢𝐬𝐩𝐫𝐚𝐲 𝐄ʀʀ → `{str(e)[:40]}`")


    @register_cmd("countspray")
    async def cmd_countspray(event, arg):
        try:
            chat = event.chat_id
            parts = arg.strip().split(None, 1) if arg else []
            if len(parts) < 2:
                return await safe_edit(event, "❌ 𝐔𝐬𝐞 → `.countspray <n> <text>`")
            try: n = int(parts[0])
            except: return await safe_edit(event, "❌ 𝐈𝐧𝐯𝐚𝐥𝐢𝐝 𝐜𝐨𝐮𝐧𝐭")
            text = parts[1]
            if chat in spray_tasks: spray_tasks[chat].cancel(); del spray_tasks[chat]
            async def do_count():
                for _ in range(n):
                    try:
                        await bot.send_message(chat, text)
                        await asyncio.sleep(SPRAY_DELAY)
                    except FloodWaitError as fw: await asyncio.sleep(fw.seconds)
                    except asyncio.CancelledError: break
                    except: break
                spray_tasks.pop(chat, None)
            spray_tasks[chat] = asyncio.create_task(do_count())
            await safe_edit(event, f"💣 𝐂𝐨𝐮𝐧𝐭𝐬𝐩𝐫𝐚𝐲 `{n}x` 𝐒𝐭𝐚𝐫𝐭𝐞𝐝")
        except Exception as e:
            await safe_edit(event, f"❌ 𝐂𝐒𝐩𝐫𝐚𝐲 𝐄ʀʀ → `{str(e)[:40]}`")


    # ─── TEXT MANAGER ───
    @register_cmd("addtext")
    async def cmd_addtext(event, arg):
        try:
            if not arg:
                return await safe_edit(event, "❌ 𝐔𝐬𝐞 → `.addtext <text>`")
            spam_texts.append(arg)
            save_spam_texts()
            await safe_edit(event, f"✅ 𝐓𝐞𝐱𝐭 𝐒𝐚𝐯𝐞𝐝 → 𝐒𝐥𝐨𝐭 `{len(spam_texts)}`")
        except Exception as e:
            await safe_edit(event, f"❌ 𝐀𝐝𝐝𝐓𝐞𝐱𝐭 𝐄ʀʀ → `{str(e)[:40]}`")


    @register_cmd("listtexts")
    async def cmd_listtexts(event, _):
        try:
            if not spam_texts:
                return await safe_edit(event, "⚠️ 𝐍𝐨 𝐒𝐚𝐯𝐞𝐝 𝐓𝐞𝐱𝐭𝐬")
            lines = [f"`{i+1}`. {t[:80]}" for i, t in enumerate(spam_texts)]
            await safe_edit(event, "📝 𝐒𝐚𝐯𝐞𝐝 𝐓𝐞𝐱𝐭𝐬\n━━━━━━━━━━━━━━━\n" + "\n".join(lines))
        except Exception as e:
            await safe_edit(event, f"❌ 𝐋𝐢𝐬𝐭𝐓𝐞𝐱𝐭𝐬 𝐄ʀʀ → `{str(e)[:40]}`")


    @register_cmd("edittext")
    async def cmd_edittext(event, arg):
        try:
            parts = arg.strip().split(None, 1) if arg else []
            if len(parts) < 2:
                return await safe_edit(event, "❌ 𝐔𝐬𝐞 → `.edittext <slot> <new_text>`")
            try: idx = int(parts[0]) - 1
            except: return await safe_edit(event, "❌ 𝐈𝐧𝐯𝐚𝐥𝐢𝐝 𝐬𝐥𝐨𝐭")
            if idx < 0 or idx >= len(spam_texts):
                return await safe_edit(event, "❌ 𝐒𝐥𝐨𝐭 𝐍𝐨𝐭 𝐅𝐨𝐮𝐧𝐝")
            spam_texts[idx] = parts[1]
            save_spam_texts()
            await safe_edit(event, f"✅ 𝐒𝐥𝐨𝐭 `{idx+1}` 𝐔𝐩𝐝𝐚𝐭𝐞𝐝")
        except Exception as e:
            await safe_edit(event, f"❌ 𝐄𝐝𝐢𝐭𝐓𝐞𝐱𝐭 𝐄ʀʀ → `{str(e)[:40]}`")


    @register_cmd("deltext")
    async def cmd_deltext(event, arg):
        try:
            if not arg or not arg.strip().isdigit():
                return await safe_edit(event, "❌ 𝐔𝐬𝐞 → `.deltext <slot>`")
            idx = int(arg.strip()) - 1
            if idx < 0 or idx >= len(spam_texts):
                return await safe_edit(event, "❌ 𝐒𝐥𝐨𝐭 𝐍𝐨𝐭 𝐅𝐨𝐮𝐧𝐝")
            spam_texts.pop(idx)
            save_spam_texts()
            await safe_edit(event, f"🗑️ 𝐒𝐥𝐨𝐭 `{idx+1}` 𝐃𝐞𝐥𝐞𝐭𝐞𝐝")
        except Exception as e:
            await safe_edit(event, f"❌ 𝐃𝐞𝐥𝐓𝐞𝐱𝐭 𝐄ʀʀ → `{str(e)[:40]}`")


    @register_cmd("cleartext")
    async def cmd_cleartext(event, arg):
        try:
            if arg.strip().lower() != "confirm":
                return await safe_edit(event, "⚠️ 𝐔𝐬𝐞 → `.cleartext confirm`")
            spam_texts.clear()
            save_spam_texts()
            await safe_edit(event, "🗑️ 𝐀𝐥𝐥 𝐓𝐞𝐱𝐭𝐬 𝐂𝐥𝐞𝐚𝐫𝐞𝐝")
        except Exception as e:
            await safe_edit(event, f"❌ 𝐂𝐥𝐞𝐚𝐫𝐓𝐞𝐱𝐭 𝐄ʀʀ → `{str(e)[:40]}`")


    # ─── FASTGC ───
    @register_cmd("fastgc")
    async def cmd_fastgc(event, arg):
        try:
            parts = arg.strip().split(None, 1) if arg else []
            subcmd = parts[0].lower() if parts else ""
            if subcmd == "stop":
                if FASTGC_STATE.get("task"):
                    try: FASTGC_STATE["task"].cancel()
                    except: pass
                FASTGC_STATE.update({"active": False, "template": None, "task": None, "chat_id": None})
                return await safe_edit(event, "🛑 𝐅𝐚𝐬𝐭𝐆𝐂 𝐒𝐭𝐨𝐩𝐩𝐞𝐝")
            if subcmd == "set" and len(parts) > 1:
                template = parts[1].strip()
                if not template or "{emoji}" not in template:
                    return await safe_edit(event, "❌ 𝐓𝐞𝐦𝐩𝐥𝐚𝐭𝐞 𝐦𝐮𝐬𝐭 𝐡𝐚𝐯𝐞 `{emoji}`")
                if FASTGC_STATE.get("task"):
                    try: FASTGC_STATE["task"].cancel()
                    except: pass
                FASTGC_STATE.update({"active": True, "template": template, "chat_id": event.chat_id})
                task = asyncio.create_task(gc_fast_loop(event.chat_id))
                FASTGC_STATE["task"] = task
                return await safe_edit(event, f"⚡ 𝐅𝐚𝐬𝐭𝐆𝐂 𝐒𝐭𝐚𝐫𝐭𝐞𝐝\n📝 `{template}`")
            await safe_edit(event, "❌ 𝐔𝐬𝐞 → `.fastgc set {emoji} <template>` or `.fastgc stop`")
        except Exception as e:
            await safe_edit(event, f"❌ 𝐅𝐚𝐬𝐭𝐆𝐂 𝐄ʀʀ → `{str(e)[:40]}`")


    # ─── ANTIDEL ───
    @register_cmd("antidel")
    async def cmd_antidel(event, arg):
        global antidel_enabled
        try:
            sub = (arg or "").strip().lower()
            if sub == "on":
                antidel_enabled = True
                await safe_edit(event, "🛡️ 𝐀𝐧𝐭𝐢𝐃𝐞𝐥 𝐎𝐍")
            elif sub == "off":
                antidel_enabled = False
                antidel_cache.clear()
                await safe_edit(event, "🛡️ 𝐀𝐧𝐭𝐢𝐃𝐞𝐥 𝐎𝐅𝐅")
            else:
                status = "ON" if antidel_enabled else "OFF"
                await safe_edit(event, f"🛡️ 𝐀𝐧𝐭𝐢𝐃𝐞𝐥 → `{status}`\n📦 𝐂𝐚𝐜𝐡𝐞 → `{len(antidel_cache)}`")
        except Exception as e:
            await safe_edit(event, f"❌ 𝐀𝐧𝐭𝐢𝐃𝐞𝐥 𝐄ʀʀ → `{str(e)[:40]}`")


    # ─── WATCHSPAM ───
    @register_cmd("watchspam", needs_reply=True)
    async def cmd_watchspam(event, arg):
        try:
            targets = await get_targets(event, "")
            if not targets:
                return await safe_edit(event, "❌ 𝐍𝐨 𝐓𝐚𝐫𝐠𝐞𝐭")
            parts = (arg or "").strip().split()
            try:
                limit = int(parts[0]) if len(parts) > 0 else 3
                seconds = float(parts[1]) if len(parts) > 1 else 5.0
            except:
                limit, seconds = 3, 5.0
            for uid in targets:
                watch_spam[(event.chat_id, uid)] = {"limit": limit, "seconds": seconds, "times": []}
            await safe_edit(event, f"👁️ 𝐖𝐚𝐭𝐜𝐡𝐒𝐩𝐚𝐦 𝐒𝐞𝐭 → `{limit}` 𝐦𝐬𝐠𝐬 / `{seconds}s`")
        except Exception as e:
            await safe_edit(event, f"❌ 𝐖𝐚𝐭𝐜𝐡𝐒𝐩𝐚𝐦 𝐄ʀʀ → `{str(e)[:40]}`")


    @register_cmd("unwatchspam")
    async def cmd_unwatchspam(event, arg):
        try:
            targets = await get_targets(event, arg)
            if targets:
                for uid in targets:
                    watch_spam.pop((event.chat_id, uid), None)
                await safe_edit(event, f"🗑️ 𝐔𝐧𝐰𝐚𝐭𝐜𝐡𝐒𝐩𝐚𝐦 → `{len(targets)}`")
            else:
                removed = [k for k in watch_spam if k[0] == event.chat_id]
                for k in removed: del watch_spam[k]
                await safe_edit(event, "🗑️ 𝐀𝐥𝐥 𝐖𝐚𝐭𝐜𝐡𝐞𝐬 𝐑𝐞𝐦𝐨𝐯𝐞𝐝")
        except Exception as e:
            await safe_edit(event, f"❌ 𝐔𝐧𝐰𝐚𝐭𝐜𝐡 𝐄ʀʀ → `{str(e)[:40]}`")


    @register_cmd("watchlist")
    async def cmd_watchlist(event, _):
        try:
            chat_watches = [(k, v) for k, v in watch_spam.items() if k[0] == event.chat_id]
            if not chat_watches:
                return await safe_edit(event, "⚠️ 𝐍𝐨 𝐖𝐚𝐭𝐜𝐡𝐞𝐬")
            lines = [f"• `{uid}` → `{v['limit']}` / `{v['seconds']}s`" for (_, uid), v in chat_watches]
            await safe_edit(event, "👁️ 𝐖𝐚𝐭𝐜𝐡𝐥𝐢𝐬𝐭\n━━━━━━━━━━━━━━━\n" + "\n".join(lines))
        except Exception as e:
            await safe_edit(event, f"❌ 𝐖𝐚𝐭𝐜𝐡𝐋𝐢𝐬𝐭 𝐄ʀʀ → `{str(e)[:40]}`")


    # ─── GROUP PFP ───
    gpfp_pool = []
    gpfp_task = None

    @register_cmd("setgpfp", needs_reply=True, group_only=True)
    async def cmd_setgpfp(event, _):
        try:
            reply = await event.get_reply_message()
            if not reply or not reply.media:
                return await safe_edit(event, "❌ 𝐑𝐞𝐩𝐥𝐲 𝐭𝐨 𝐚𝐧 𝐢𝐦𝐚𝐠𝐞")
            file = await reply.download_media(file=bytes)
            if not file: return await safe_edit(event, "❌ 𝐃𝐨𝐰𝐧𝐥𝐨𝐚𝐝 𝐅𝐚𝐢𝐥")
            await bot(functions.channels.EditPhotoRequest(channel=event.chat_id, photo=await bot.upload_file(BytesIO(file))))
            await safe_edit(event, "🖼️ 𝐆𝐫𝐨𝐮𝐩 𝐏𝐅𝐏 𝐔𝐩𝐝𝐚𝐭𝐞𝐝")
        except Exception as e:
            await safe_edit(event, f"❌ 𝐒𝐞𝐭𝐆𝐏𝐅𝐏 𝐄ʀʀ → `{str(e)[:40]}`")


    @register_cmd("addgpfp", needs_reply=True)
    async def cmd_addgpfp(event, _):
        try:
            reply = await event.get_reply_message()
            if not reply or not reply.media:
                return await safe_edit(event, "❌ 𝐑𝐞𝐩𝐥𝐲 𝐭𝐨 𝐚𝐧 𝐢𝐦𝐚𝐠𝐞")
            file = await reply.download_media(file=bytes)
            if file: gpfp_pool.append(file)
            await safe_edit(event, f"✅ 𝐀𝐝𝐝𝐞𝐝 𝐭𝐨 𝐏𝐨𝐨𝐥 → `{len(gpfp_pool)}`")
        except Exception as e:
            await safe_edit(event, f"❌ 𝐀𝐝𝐝𝐆𝐏𝐅𝐏 𝐄ʀʀ → `{str(e)[:40]}`")


    @register_cmd("listgpfp")
    async def cmd_listgpfp(event, _):
        await safe_edit(event, f"🖼️ 𝐆𝐏𝐅𝐏 𝐏𝐨𝐨𝐥 → `{len(gpfp_pool)}` 𝐢𝐦𝐚𝐠𝐞𝐬")


    @register_cmd("stopgpfp")
    async def cmd_stopgpfp(event, _):
        global gpfp_task
        try:
            if gpfp_task: gpfp_task.cancel(); gpfp_task = None
            await safe_edit(event, "🛑 𝐀𝐮𝐭𝐨 𝐆𝐏𝐅𝐏 𝐒𝐭𝐨𝐩𝐩𝐞𝐝")
        except Exception as e:
            await safe_edit(event, f"❌ 𝐒𝐭𝐨𝐩𝐆𝐏𝐅𝐏 𝐄ʀʀ → `{str(e)[:40]}`")


    @register_cmd("autogpfp", group_only=True)
    async def cmd_autogpfp(event, arg):
        global gpfp_task
        try:
            if not gpfp_pool:
                return await safe_edit(event, "❌ 𝐍𝐨 𝐈𝐦𝐚𝐠𝐞𝐬 𝐢𝐧 𝐏𝐨𝐨𝐥")
            try: interval = max(10, int(arg)) if arg else 30
            except: interval = 30
            if gpfp_task: gpfp_task.cancel()
            async def do_auto():
                while True:
                    try:
                        img = random.choice(gpfp_pool)
                        await bot(functions.channels.EditPhotoRequest(
                            channel=event.chat_id,
                            photo=await bot.upload_file(BytesIO(img))
                        ))
                        await asyncio.sleep(interval)
                    except asyncio.CancelledError: break
                    except: await asyncio.sleep(interval)
            gpfp_task = asyncio.create_task(do_auto())
            await safe_edit(event, f"🖼️ 𝐀𝐮𝐭𝐨 𝐆𝐏𝐅𝐏 𝐒𝐭𝐚𝐫𝐭𝐞𝐝 → `{interval}s`")
        except Exception as e:
            await safe_edit(event, f"❌ 𝐀𝐮𝐭𝐨𝐆𝐏𝐅𝐏 𝐄ʀʀ → `{str(e)[:40]}`")


    # ─── AUTO REACT ───
    @register_cmd("ar")
    async def cmd_ar(event, arg):
        global auto_react_emoji
        try:
            if not arg:
                return await safe_edit(event, "❌ 𝐔𝐬𝐞 → `.ar <emoji>`")
            auto_react_emoji = arg.strip()
            await safe_edit(event, f"❤️ 𝐀𝐮𝐭𝐨 𝐑𝐞𝐚𝐜𝐭 → `{auto_react_emoji}`")
        except Exception as e:
            await safe_edit(event, f"❌ 𝐀𝐑 𝐄ʀʀ → `{str(e)[:40]}`")


    @register_cmd("sar")
    async def cmd_sar(event, _):
        global auto_react_emoji
        auto_react_emoji = None
        await safe_edit(event, "❤️ 𝐀𝐮𝐭𝐨 𝐑𝐞𝐚𝐜𝐭 𝐎𝐅𝐅")


    # ─── NOTES ───
    @register_cmd("notesadd")
    async def cmd_notesadd(event, arg):
        try:
            if not arg:
                return await safe_edit(event, "❌ 𝐔𝐬𝐞 → `.notesadd <text>`")
            nid = max(notes.keys(), default=0) + 1
            notes[nid] = arg
            save_notes()
            await safe_edit(event, f"📝 𝐍𝐨𝐭𝐞 𝐒𝐚𝐯𝐞𝐝 → 𝐈𝐃 `{nid}`")
        except Exception as e:
            await safe_edit(event, f"❌ 𝐍𝐨𝐭𝐞𝐬𝐀𝐝𝐝 𝐄ʀʀ → `{str(e)[:40]}`")


    @register_cmd("noteslist")
    async def cmd_noteslist(event, _):
        try:
            if not notes:
                return await safe_edit(event, "⚠️ 𝐍𝐨 𝐍𝐨𝐭𝐞𝐬")
            lines = [f"`{k}`. {v[:60]}" for k, v in sorted(notes.items())]
            await safe_edit(event, "🧠 𝐍𝐨𝐭𝐞𝐬 𝐋𝐢𝐬𝐭\n━━━━━━━━━━━━━━━\n" + "\n".join(lines))
        except Exception as e:
            await safe_edit(event, f"❌ 𝐍𝐨𝐭𝐞𝐬𝐋𝐢𝐬𝐭 𝐄ʀʀ → `{str(e)[:40]}`")


    @register_cmd("notesdelete")
    async def cmd_notesdelete(event, arg):
        try:
            if not arg or not arg.strip().isdigit():
                return await safe_edit(event, "❌ 𝐔𝐬𝐞 → `.notesdelete <id>`")
            nid = int(arg.strip())
            if nid not in notes:
                return await safe_edit(event, "❌ 𝐍𝐨𝐭𝐞 𝐍𝐨𝐭 𝐅𝐨𝐮𝐧𝐝")
            del notes[nid]; save_notes()
            await safe_edit(event, f"🗑️ 𝐍𝐨𝐭𝐞 `{nid}` 𝐃𝐞𝐥𝐞𝐭𝐞𝐝")
        except Exception as e:
            await safe_edit(event, f"❌ 𝐍𝐨𝐭𝐞𝐬𝐃𝐞𝐥 𝐄ʀʀ → `{str(e)[:40]}`")


    # ─── ORIGINAL TOOLS ───
    @register_cmd("tts")
    async def cmd_tts(event, arg):
        try:
            if not arg:
                return await safe_edit(event, "❌ 𝐔𝐬𝐞 → `.tts <text>`")
            await safe_edit(event, "⚡ 𝐆𝐞𝐧𝐞𝐫𝐚𝐭𝐢𝐧𝐠 𝐓𝐓𝐒...\n━━━━━━━━━━━━━━━")
            fname = f"tts_{int(time.time())}.mp3"
            try: gTTS(text=arg[:5000], lang="hi", slow=False).save(fname)
            except: return await safe_edit(event, "❌ 𝐓𝐓𝐒 𝐍𝐞𝐭𝐰𝐨𝐫𝐤 𝐅𝐚𝐢𝐥")
            try:
                if event.out:
                    await event.delete()
                    await bot.send_file(event.chat_id, fname, caption="🎙️ 𝐓𝐓𝐒")
                else: await event.reply(file=fname, message="🎙️ 𝐓𝐓𝐒")
            finally:
                try: os.remove(fname)
                except: pass
        except Exception as e:
            await safe_edit(event, f"❌ 𝐓𝐓𝐒 𝐄ʀʀ → `{str(e)[:50]}`")


    @register_cmd("qrcode")
    async def cmd_qrcode(event, arg):
        try:
            if not arg:
                return await safe_edit(event, "❌ 𝐔𝐬𝐞 → `.qrcode <text>`")
            await safe_edit(event, "⚡ 𝐆𝐞𝐧𝐞𝐫𝐚𝐭𝐢𝐧𝐠 𝐐𝐑...\n━━━━━━━━━━━━━━━")
            file = f"qr_{int(time.time())}.png"
            qrcode.make(arg[:3000]).save(file)
            try:
                if event.out:
                    await event.delete()
                    await bot.send_file(event.chat_id, file, caption="🔳 𝐐𝐑 𝐂𝐨𝐝𝐞")
                else: await event.reply(file=file, message="🔳 𝐐𝐑 𝐂𝐨𝐝𝐞")
            finally:
                try: os.remove(file)
                except: pass
        except Exception as e:
            await safe_edit(event, f"❌ 𝐐𝐑 𝐄ʀʀ → `{str(e)[:50]}`")


    @register_cmd("fancy")
    async def cmd_fancy(event, arg):
        try:
            if not arg:
                return await safe_edit(event, "❌ 𝐔𝐬𝐞 → `.fancy <text>`")
            t = arg[:500]
            styles = [f"★彡 {t} 彡★", f"『 {t} 』", f"✦ {t} ✦", f"☾ {t} ☽", f"➳ {t} ➳",
                      f"⚡ {t} ⚡", f"❖ {t} ❖", f"♛ {t} ♛", f"꧁ {t} ꧂", f"░▒▓ {t} ▓▒░"]
            text = "✨ 𝐅𝐚𝐧𝐜𝐲 𝐒𝐭𝐲𝐥𝐞𝐬\n━━━━━━━━━━━━━━━\n" + "\n".join(styles)
            if event.out: await safe_edit(event, text)
            else: await event.reply(text)
        except Exception as e:
            await safe_edit(event, f"❌ 𝐅𝐚𝐧𝐜𝐲 𝐄ʀʀ → `{str(e)[:40]}`")


    @register_cmd("style")
    async def cmd_style(event, arg):
        try:
            if not arg:
                return await safe_edit(event, "❌ 𝐔𝐬𝐞 → `.style <text>`")
            t = arg[:500]
            fancy = (t.replace('a','𝒶').replace('b','𝒷').replace('c','𝒸').replace('d','𝒹')
                      .replace('e','𝑒').replace('f','𝒻').replace('g','𝑔').replace('h','𝒽'))
            text = f"🎨 𝐒𝐭𝐲𝐥𝐞\n━━━━━━━━━━━━━━━\n𝒇𝒂𝒏𝒄𝒚 → {fancy}\n**Bold** → **{t}**\n__Italic__ → __{t}__\n`Mono` → `{t}`"
            if event.out: await safe_edit(event, text)
            else: await event.reply(text)
        except Exception as e:
            await safe_edit(event, f"❌ 𝐒𝐭𝐲𝐥𝐞 𝐄ʀʀ → `{str(e)[:40]}`")


    @register_cmd("emoji")
    async def cmd_emoji(event, arg):
        try:
            if not arg:
                return await safe_edit(event, "❌ 𝐔𝐬𝐞 → `.emoji <text>`")
            pool = ["🔥","❤️","✨","⚡","💥","🌟","💫","🎯","💎","🦋","🌈","🧨","🎆","👑","🌸","🪄"]
            emojis = "".join(random.choice(pool) for _ in range(8))
            text = f"😀 𝐄𝐦𝐨𝐣𝐢 𝐒𝐭𝐲𝐥𝐞\n━━━━━━━━━━━━━━━\n{arg[:500]} {emojis}"
            if event.out: await safe_edit(event, text)
            else: await event.reply(text)
        except Exception as e:
            await safe_edit(event, f"❌ 𝐄𝐦𝐨𝐣𝐢 𝐄ʀʀ → `{str(e)[:40]}`")


    @register_cmd("calc")
    async def cmd_calc(event, arg):
        try:
            if not arg:
                return await safe_edit(event, "❌ 𝐔𝐬𝐞 → `.calc <expr>`")
            expr = arg.replace(" ", "")
            allowed = set("0123456789+-*/().%")
            if any(c not in allowed for c in expr):
                return await safe_edit(event, "❌ 𝐈𝐧𝐯𝐚𝐥𝐢𝐝 𝐂𝐡𝐚𝐫")
            res = eval(expr, {"__builtins__": None}, {})
            text = f"🧮 𝐂𝐚𝐥𝐜\n━━━━━━━━━━━━━━━\n📥 `{expr}`\n📤 `{res}`"
            if event.out: await safe_edit(event, text)
            else: await event.reply(text)
        except Exception:
            await safe_edit(event, "❌ 𝐈𝐧𝐯𝐚𝐥𝐢𝐝 𝐄𝐱𝐩𝐫𝐞𝐬𝐬𝐢𝐨𝐧")


    @register_cmd("weather")
    async def cmd_weather(event, arg):
        try:
            if not arg:
                return await safe_edit(event, "❌ 𝐔𝐬𝐞 → `.weather <city>`")
            await safe_edit(event, "⚡ 𝐅𝐞𝐭𝐜𝐡𝐢𝐧𝐠 𝐖𝐞𝐚𝐭𝐡𝐞𝐫...\n━━━━━━━━━━━━━━━")
            try:
                geo = requests.get(f"https://geocoding-api.open-meteo.com/v1/search?name={arg}&count=1", timeout=8).json()
            except: return await safe_edit(event, "❌ 𝐆𝐞𝐨 𝐍𝐞𝐭𝐰𝐨𝐫𝐤 𝐅𝐚𝐢𝐥")
            if not geo.get("results"):
                return await safe_edit(event, "❌ 𝐂𝐢𝐭𝐲 𝐍𝐨𝐭 𝐅𝐨𝐮𝐧𝐝")
            res = geo["results"][0]
            lat, lon, name = res.get("latitude"), res.get("longitude"), res.get("name")
            try:
                w = requests.get(f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true", timeout=8).json()
            except: return await safe_edit(event, "❌ 𝐖𝐞𝐚𝐭𝐡𝐞𝐫 𝐅𝐚𝐢𝐥")
            cw = w.get("current_weather")
            if not cw: return await safe_edit(event, "❌ 𝐍𝐨 𝐖𝐞𝐚𝐭𝐡𝐞𝐫 𝐃𝐚𝐭𝐚")
            msg = f"🌦️ 𝐖𝐞𝐚𝐭𝐡𝐞𝐫\n━━━━━━━━━━━━━━━\n📍 `{name}`\n🌡️ `{cw.get('temperature')}°C`\n💨 `{cw.get('windspeed')} km/h`"
            await safe_edit(event, msg)
        except Exception as e:
            await safe_edit(event, f"❌ 𝐖𝐞𝐚𝐭𝐡𝐞𝐫 → `{str(e)[:40]}`")


    @register_cmd("ip")
    async def cmd_ip(event, arg):
        try:
            if not arg:
                return await safe_edit(event, "❌ 𝐔𝐬𝐞 → `.ip <ip>`")
            await safe_edit(event, "⚡ 𝐋𝐨𝐨𝐤𝐢𝐧𝐠 𝐈𝐏...\n━━━━━━━━━━━━━━━")
            try:
                data = requests.get(f"http://ip-api.com/json/{arg}", timeout=8).json()
            except: return await safe_edit(event, "❌ 𝐈𝐏 𝐍𝐞𝐭𝐰𝐨𝐫𝐤 𝐅𝐚𝐢𝐥")
            if data.get("status") != "success":
                return await safe_edit(event, "❌ 𝐈𝐧𝐯𝐚𝐥𝐢𝐝 𝐈𝐏")
            text = f"🌍 𝐈𝐏 𝐈𝐍𝐅𝐎\n━━━━━━━━━━━━━━━\n📡 `{data.get('query')}`\n🌐 `{data.get('country')}`\n🏙️ `{data.get('city')}`\n📍 `{data.get('isp')}`"
            if event.out: await safe_edit(event, text)
            else: await event.reply(text)
        except Exception as e:
            await safe_edit(event, f"❌ 𝐈𝐏 → `{str(e)[:40]}`")


    @register_cmd("short")
    async def cmd_short(event, arg):
        try:
            if not arg:
                return await safe_edit(event, "❌ 𝐔𝐬𝐞 → `.short <url>`")
            if not arg.startswith(("http://", "https://")):
                arg = "http://" + arg
            await safe_edit(event, "⚡ 𝐒𝐡𝐨𝐫𝐭𝐞𝐧𝐢𝐧𝐠...\n━━━━━━━━━━━━━━━")
            try:
                short_url = requests.get(f"http://tinyurl.com/api-create.php?url={requests.utils.requote_uri(arg)}", timeout=8).text.strip()
            except: return await safe_edit(event, "❌ 𝐒𝐡𝐨𝐫𝐭 𝐅𝐚𝐢𝐥")
            text = f"🔗 𝐒𝐡𝐨𝐫𝐭 𝐔𝐑𝐋\n━━━━━━━━━━━━━━━\n`{short_url}`"
            if event.out: await safe_edit(event, text)
            else: await event.reply(text)
        except Exception as e:
            await safe_edit(event, f"❌ 𝐒𝐡𝐨𝐫𝐭 → `{str(e)[:40]}`")


    @register_cmd("info")
    async def cmd_info(event, arg):
        try:
            target = None
            if event.is_reply:
                r = await event.get_reply_message()
                if r and r.sender_id: target = r.sender_id
            elif arg:
                try:
                    ent = await bot.get_entity(arg)
                    target = ent.id
                except: return await safe_edit(event, "❌ 𝐈𝐧𝐯𝐚𝐥𝐢𝐝 𝐔𝐬𝐞𝐫")
            if not target:
                return await safe_edit(event, "⚠️ `.info` (reply / @user / id)")
            await safe_edit(event, "⚡ 𝐅𝐞𝐭𝐜𝐡𝐢𝐧𝐠 𝐔𝐬𝐞𝐫...\n━━━━━━━━━━━━━━━")
            user = await bot.get_entity(target)
            if getattr(user, "deleted", False):
                return await safe_edit(event, "❌ 𝐃𝐞𝐥𝐞𝐭𝐞𝐝 𝐔𝐬𝐞𝐫")
            full = await bot(functions.users.GetFullUserRequest(user.id))
            bio = full.full_user.about or "𝐍𝐨 𝐁𝐢𝐨"
            uname = f"@{user.username}" if user.username else "𝐍𝐨 𝐔𝐬𝐞𝐫"
            text = (
                "👤 𝐔𝐒𝐄𝐑 𝐈𝐍𝐅𝐎\n━━━━━━━━━━━━━━━\n"
                f"🆔 𝐈𝐃 → `{user.id}`\n"
                f"📛 𝐍𝐚𝐦𝐞 → {user.first_name or ''} {user.last_name or ''}\n"
                f"🔗 𝐔𝐬𝐞𝐫 → {uname}\n"
                f"📝 𝐁𝐢𝐨 → {bio}"
            )
            await safe_edit(event, text)
        except Exception as e:
            await safe_edit(event, f"❌ 𝐈𝐍𝐅𝐎 → `{str(e)[:50]}`")


    @register_cmd("copy")
    async def cmd_copy(event, args):
        global CLONE_DATA, CLONE_ACTIVE, LAST_CLONE_ID
        try:
            reply = await event.get_reply_message()
            target = None
            if reply:
                try:
                    if reply.sender_id: target = await bot.get_entity(reply.sender_id)
                except: pass
            if not target and args:
                try: target = await bot.get_entity(args.strip())
                except: pass
            if not target:
                return await safe_edit(event, "❌ 𝐑𝐞𝐩𝐥𝐲 / 𝐔𝐬𝐞𝐫 / 𝐈𝐃")
            me = await bot.get_me()
            if target.id == me.id:
                return await safe_edit(event, "⚠️ 𝐒𝐞𝐥𝐟 𝐂𝐥𝐨𝐧𝐞 𝐁𝐥𝐨𝐜𝐤")
            if CLONE_ACTIVE and LAST_CLONE_ID == target.id:
                return await safe_edit(event, "⚠️ 𝐀𝐥𝐫𝐞𝐚𝐝𝐲 𝐂𝐥𝐨𝐧𝐞𝐝")
            await safe_edit(event, "⚡ 𝐂𝐥𝐨𝐧𝐢𝐧𝐠...\n━━━━━━━━━━━━━━━")
            if not CLONE_ACTIVE:
                full_me = await bot(functions.users.GetFullUserRequest(me.id))
                CLONE_DATA["name"] = me.first_name
                CLONE_DATA["username"] = me.username
                CLONE_DATA["bio"] = full_me.full_user.about or ""
            full = await bot(functions.users.GetFullUserRequest(target.id))
            fname = getattr(target, "first_name", "") or ""
            await bot(functions.account.UpdateProfileRequest(first_name=fname[:64]))
            if full.full_user.about is not None:
                try: await bot(functions.account.UpdateProfileRequest(about=full.full_user.about[:70]))
                except: pass
            try:
                photo = await bot.download_profile_photo(target.id, file=bytes)
                if photo: await bot(functions.photos.UploadProfilePhotoRequest(file=await bot.upload_file(BytesIO(photo))))
            except: pass
            CLONE_ACTIVE = True
            LAST_CLONE_ID = target.id
            await safe_edit(event, f"🎭 𝐂𝐥𝐨𝐧𝐞𝐝 → `{fname}`")
        except Exception as e:
            await safe_edit(event, f"❌ 𝐂𝐨𝐩𝐲 𝐄ʀʀ → `{str(e)[:50]}`")


    @register_cmd("normal")
    async def cmd_normal(event, _):
        global CLONE_ACTIVE, LAST_CLONE_ID
        try:
            if not CLONE_ACTIVE:
                return await safe_edit(event, "⚠️ 𝐍𝐨𝐭 𝐂𝐥𝐨𝐧𝐢𝐧𝐠")
            await bot(functions.account.UpdateProfileRequest(
                first_name=(CLONE_DATA.get("name") or "")[:64],
                about=(CLONE_DATA.get("bio") or "")[:70]
            ))
            if CLONE_DATA.get("photo_bytes"):
                try:
                    await bot(functions.photos.UploadProfilePhotoRequest(
                        file=await bot.upload_file(BytesIO(CLONE_DATA["photo_bytes"]))
                    ))
                except: pass
            CLONE_ACTIVE = False
            LAST_CLONE_ID = None
            await safe_edit(event, "✅ 𝐏𝐫𝐨𝐟𝐢𝐥𝐞 𝐑𝐞𝐬𝐭𝐨𝐫𝐞𝐝")
        except Exception as e:
            await safe_edit(event, f"❌ 𝐍𝐨𝐫𝐦𝐚𝐥 𝐄ʀʀ → `{str(e)[:50]}`")


    # ─── MUSIC ───
    @register_cmd("music")
    async def cmd_music(event, arg):
        if not arg:
            return await safe_edit(event, "❌ 𝐔𝐬𝐞 → `.music <song name>`")
        async def download_and_send():
            try:
                await safe_edit(event, f"🎵 𝐒𝐞𝐚𝐫𝐜𝐡𝐢𝐧𝐠: `{arg}`\n━━━━━━━━━━━━━━━")
                ydl_opts = {
                    'format': 'bestaudio/best',
                    'outtmpl': os.path.join(DOWNLOAD_PATH, '%(title)s.%(ext)s'),
                    'default_search': 'ytsearch1',
                    'noplaylist': True,
                    'quiet': True,
                    'postprocessors': [{'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3', 'preferredquality': '128'}],
                }
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(arg, download=True)
                    if 'entries' in info: info = info['entries'][0]
                    title = info.get('title', 'Unknown')
                    dur = info.get('duration', 0)
                new = os.path.join(DOWNLOAD_PATH, f"{title}.mp3")
                if not os.path.exists(new):
                    for f in os.listdir(DOWNLOAD_PATH):
                        if f.endswith('.mp3'): new = os.path.join(DOWNLOAD_PATH, f); break
                await bot.send_file(event.chat_id, new, voice_note=True, caption=f"🎵 `{title[:60]}`")
                try: os.remove(new)
                except: pass
                await event.delete()
            except Exception as e:
                await safe_edit(event, f"❌ 𝐌𝐮𝐬𝐢𝐜 → `{str(e)[:60]}`")
        asyncio.create_task(download_and_send())


    @register_cmd("dmusic")
    async def cmd_dmusic(event, arg):
        if not arg:
            return await safe_edit(event, "❌ 𝐔𝐬𝐞 → `.dmusic <song name>`")
        async def download_music():
            try:
                await safe_edit(event, f"🎵 𝐃𝐨𝐰𝐧𝐥𝐨𝐚𝐝𝐢𝐧𝐠: `{arg}`\n━━━━━━━━━━━━━━━")
                ydl_opts = {
                    'format': 'bestaudio/best',
                    'outtmpl': os.path.join(DOWNLOAD_PATH, '%(title)s.%(ext)s'),
                    'default_search': 'ytsearch1',
                    'noplaylist': True,
                    'quiet': True,
                    'postprocessors': [{'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3', 'preferredquality': '320'}],
                }
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(arg, download=True)
                    if 'entries' in info: info = info['entries'][0]
                    title = info.get('title', 'Unknown')
                    dur = info.get('duration', 0)
                new = os.path.join(DOWNLOAD_PATH, f"{title}.mp3")
                if not os.path.exists(new):
                    for f in os.listdir(DOWNLOAD_PATH):
                        if f.endswith('.mp3'): new = os.path.join(DOWNLOAD_PATH, f); break
                await bot.send_file(event.chat_id, new, caption=f"🎵 `{title[:60]}`\n🎧 `320kbps MP3`",
                                    attributes=[types.DocumentAttributeAudio(duration=dur, title=title)])
                try: os.remove(new)
                except: pass
                await event.delete()
            except Exception as e:
                await safe_edit(event, f"❌ 𝐃𝐌𝐮𝐬𝐢𝐜 → `{str(e)[:60]}`")
        asyncio.create_task(download_music())


    # ────────────────────────────────────────────────
    #         NEW FIGHTING RAID COMMANDS (16 + 4 = 20 types)
    # ────────────────────────────────────────────────

    def make_raid_cmds(name, start_set, text_list):
        """Factory to create start/stop raid commands"""
        @register_cmd(name, needs_reply=True)
        async def cmd_start(event, arg):
            try:
                targets = await get_targets(event, arg)
                if not targets: return await safe_edit(event, "❌ 𝐍𝐨 𝐓𝐚𝐫𝐠𝐞𝐭")
                for uid in targets: start_set.add(uid)
                await safe_edit(event, f"🔥 **{name.upper()} RAID ON** → `{len(targets)}` targets")
            except Exception as e:
                await safe_edit(event, f"❌ {name} 𝐄ʀʀ → `{str(e)[:40]}`")
        @register_cmd(f"s{name}")
        async def cmd_stop(event, arg):
            try:
                targets = await get_targets(event, arg)
                if targets:
                    for uid in targets: start_set.discard(uid)
                    await safe_edit(event, f"🛑 **{name.upper()} RAID OFF** → targets removed")
                else:
                    start_set.clear()
                    await safe_edit(event, f"🛑 **{name.upper()} RAID OFF** → all cleared")
            except Exception as e:
                await safe_edit(event, f"❌ s{name} 𝐄ʀʀ → `{str(e)[:40]}`")

    make_raid_cmds("attack", attack_users, attack_list)
    make_raid_cmds("roast", roast_users, roast_list)
    make_raid_cmds("diss", diss_users, diss_list)
    make_raid_cmds("war", war_users, war_list)
    make_raid_cmds("savage", savage_users, savage_list)
    make_raid_cmds("ultra", ultra_users, ultra_list)
    make_raid_cmds("godwar", godwar_users, godwar_list)
    make_raid_cmds("troll", troll_users, troll_list)
    make_raid_cmds("shame", shame_users, shame_list)
    make_raid_cmds("fire", fire_users, fire_list)
    make_raid_cmds("devil", devil_users, devil_list)
    make_raid_cmds("karma", karma_users, karma_list)
    make_raid_cmds("ghost", ghost_users, ghost_list)
    make_raid_cmds("legend", legend_users, legend_list)
    make_raid_cmds("doom", doom_users, doom_list)
    # ─── NEW 4 ───
    make_raid_cmds("nuke", nuke_users, nuke_list)
    make_raid_cmds("storm", storm_users, storm_list)
    make_raid_cmds("blizzard", blizzard_users, blizzard_list)
    make_raid_cmds("venom", venom_users, venom_list)


    @register_cmd("stopall")
    async def cmd_stopall(event, _):
        try:
            all_sets = [attack_users, roast_users, diss_users, war_users, savage_users,
                        ultra_users, godwar_users, combo_users, troll_users, shame_users,
                        fire_users, devil_users, karma_users, ghost_users, legend_users, doom_users,
                        nuke_users, storm_users, blizzard_users, venom_users,
                        reply_users, rr_users, flag_users, hrr_users, replygod_users]
            for s in all_sets: s.clear()
            replysid_users.clear()
            rspam_users.clear()
            for task in spray_tasks.values():
                try: task.cancel()
                except: pass
            spray_tasks.clear()
            await safe_edit(event, "🛑 **ALL RAIDS STOPPED** — All sets cleared!")
        except Exception as e:
            await safe_edit(event, f"❌ 𝐒𝐭𝐨𝐩𝐀𝐥𝐥 𝐄ʀʀ → `{str(e)[:40]}`")


    @register_cmd("raidstatus")
    async def cmd_raidstatus(event, _):
        try:
            raids = {
                "reply": len(reply_users), "rr": len(rr_users), "flag": len(flag_users),
                "hrr": len(hrr_users), "replygod": len(replygod_users),
                "attack": len(attack_users), "roast": len(roast_users), "diss": len(diss_users),
                "war": len(war_users), "savage": len(savage_users), "ultra": len(ultra_users),
                "godwar": len(godwar_users), "combo": len(combo_users), "troll": len(troll_users),
                "shame": len(shame_users), "fire": len(fire_users), "devil": len(devil_users),
                "karma": len(karma_users), "ghost": len(ghost_users), "legend": len(legend_users),
                "doom": len(doom_users), "nuke": len(nuke_users), "storm": len(storm_users),
                "blizzard": len(blizzard_users), "venom": len(venom_users),
            }
            active = {k: v for k, v in raids.items() if v > 0}
            if not active:
                return await safe_edit(event, "⚠️ 𝐍𝐨 𝐀𝐜𝐭𝐢𝐯𝐞 𝐑𝐚𝐢𝐝𝐬")
            lines = [f"• **{k}** → `{v}` targets" for k, v in active.items()]
            text = "⚔️ **ACTIVE RAIDS**\n━━━━━━━━━━━━━━━\n" + "\n".join(lines)
            await safe_edit(event, text)
        except Exception as e:
            await safe_edit(event, f"❌ 𝐑𝐚𝐢𝐝𝐒𝐭𝐚𝐭𝐮𝐬 𝐄ʀʀ → `{str(e)[:40]}`")


    # ────────────────────────────────────────────────
    #         NEW 100 UTILITY TOOL COMMANDS
    # ────────────────────────────────────────────────

    # ─── TEXT TOOLS ───
    @register_cmd("upper")
    async def cmd_upper(event, arg):
        try:
            if not arg: return await safe_edit(event, "❌ 𝐔𝐬𝐞 → `.upper <text>`")
            await safe_edit(event, f"🔠 `{arg.upper()}`")
        except Exception as e:
            await safe_edit(event, f"❌ → `{str(e)[:40]}`")


    @register_cmd("lower")
    async def cmd_lower(event, arg):
        try:
            if not arg: return await safe_edit(event, "❌ 𝐔𝐬𝐞 → `.lower <text>`")
            await safe_edit(event, f"🔡 `{arg.lower()}`")
        except Exception as e:
            await safe_edit(event, f"❌ → `{str(e)[:40]}`")


    @register_cmd("reverse")
    async def cmd_reverse(event, arg):
        try:
            if not arg: return await safe_edit(event, "❌ 𝐔𝐬𝐞 → `.reverse <text>`")
            await safe_edit(event, f"↩️ `{arg[::-1]}`")
        except Exception as e:
            await safe_edit(event, f"❌ → `{str(e)[:40]}`")


    @register_cmd("len")
    async def cmd_len(event, arg):
        try:
            if not arg: return await safe_edit(event, "❌ 𝐔𝐬𝐞 → `.len <text>`")
            await safe_edit(event, f"📏 𝐋𝐞𝐧𝐠𝐭𝐡 → `{len(arg)}` chars")
        except Exception as e:
            await safe_edit(event, f"❌ → `{str(e)[:40]}`")


    @register_cmd("wcount")
    async def cmd_wcount(event, arg):
        try:
            if not arg: return await safe_edit(event, "❌ 𝐔𝐬𝐞 → `.wcount <text>`")
            words = len(arg.split())
            chars = len(arg)
            await safe_edit(event, f"📊 𝐖𝐨𝐫𝐝𝐬 → `{words}` | 𝐂𝐡𝐚𝐫𝐬 → `{chars}`")
        except Exception as e:
            await safe_edit(event, f"❌ → `{str(e)[:40]}`")


    @register_cmd("bold")
    async def cmd_bold(event, arg):
        try:
            if not arg: return await safe_edit(event, "❌ 𝐔𝐬𝐞 → `.bold <text>`")
            await safe_edit(event, f"**{arg}**")
        except Exception as e:
            await safe_edit(event, f"❌ → `{str(e)[:40]}`")


    @register_cmd("italic")
    async def cmd_italic(event, arg):
        try:
            if not arg: return await safe_edit(event, "❌ 𝐔𝐬𝐞 → `.italic <text>`")
            await safe_edit(event, f"__{arg}__")
        except Exception as e:
            await safe_edit(event, f"❌ → `{str(e)[:40]}`")


    @register_cmd("mono")
    async def cmd_mono(event, arg):
        try:
            if not arg: return await safe_edit(event, "❌ 𝐔𝐬𝐞 → `.mono <text>`")
            await safe_edit(event, f"`{arg}`")
        except Exception as e:
            await safe_edit(event, f"❌ → `{str(e)[:40]}`")


    @register_cmd("encode")
    async def cmd_encode(event, arg):
        try:
            if not arg: return await safe_edit(event, "❌ 𝐔𝐬𝐞 → `.encode <text>`")
            encoded = base64.b64encode(arg.encode()).decode()
            await safe_edit(event, f"🔐 𝐁𝐚𝐬𝐞𝟔𝟒\n━━━━━━━━━━━━━━━\n`{encoded}`")
        except Exception as e:
            await safe_edit(event, f"❌ → `{str(e)[:40]}`")


    @register_cmd("decode")
    async def cmd_decode(event, arg):
        try:
            if not arg: return await safe_edit(event, "❌ 𝐔𝐬𝐞 → `.decode <base64>`")
            decoded = base64.b64decode(arg.encode()).decode()
            await safe_edit(event, f"🔓 𝐃𝐞𝐜𝐨𝐝𝐞𝐝\n━━━━━━━━━━━━━━━\n`{decoded}`")
        except Exception as e:
            await safe_edit(event, f"❌ 𝐈𝐧𝐯𝐚𝐥𝐢𝐝 𝐁𝐚𝐬𝐞𝟔𝟒 → `{str(e)[:40]}`")


    @register_cmd("rot13")
    async def cmd_rot13(event, arg):
        try:
            if not arg: return await safe_edit(event, "❌ 𝐔𝐬𝐞 → `.rot13 <text>`")
            import codecs
            result = codecs.encode(arg, 'rot_13')
            await safe_edit(event, f"🔄 𝐑𝐎𝐓𝟏𝟑 → `{result}`")
        except Exception as e:
            await safe_edit(event, f"❌ → `{str(e)[:40]}`")


    @register_cmd("morse")
    async def cmd_morse(event, arg):
        try:
            if not arg: return await safe_edit(event, "❌ 𝐔𝐬𝐞 → `.morse <text>`")
            MORSE = {'A':'.-','B':'-...','C':'-.-.','D':'-..','E':'.','F':'..-.','G':'--.','H':'....','I':'..','J':'.---','K':'-.-','L':'.-..','M':'--','N':'-.','O':'---','P':'.--.','Q':'--.-','R':'.-.','S':'...','T':'-','U':'..-','V':'...-','W':'.--','X':'-..-','Y':'-.--','Z':'--..','0':'-----','1':'.----','2':'..---','3':'...--','4':'....-','5':'.....','6':'-....','7':'--...','8':'---..','9':'----.',' ':'/'}
            result = " ".join(MORSE.get(c.upper(), '?') for c in arg[:200])
            await safe_edit(event, f"📻 𝐌𝐨𝐫𝐬𝐞\n━━━━━━━━━━━━━━━\n`{result}`")
        except Exception as e:
            await safe_edit(event, f"❌ → `{str(e)[:40]}`")


    @register_cmd("binary")
    async def cmd_binary(event, arg):
        try:
            if not arg: return await safe_edit(event, "❌ 𝐔𝐬𝐞 → `.binary <text>`")
            result = " ".join(format(ord(c), '08b') for c in arg[:50])
            await safe_edit(event, f"💻 𝐁𝐢𝐧𝐚𝐫𝐲\n━━━━━━━━━━━━━━━\n`{result}`")
        except Exception as e:
            await safe_edit(event, f"❌ → `{str(e)[:40]}`")


    @register_cmd("leet")
    async def cmd_leet(event, arg):
        try:
            if not arg: return await safe_edit(event, "❌ 𝐔𝐬𝐞 → `.leet <text>`")
            leet_map = {'a':'4','e':'3','g':'9','i':'1','o':'0','s':'5','t':'7','b':'8'}
            result = "".join(leet_map.get(c.lower(), c) for c in arg[:500])
            await safe_edit(event, f"🤖 𝐋𝐞𝐞𝐭\n━━━━━━━━━━━━━━━\n`{result}`")
        except Exception as e:
            await safe_edit(event, f"❌ → `{str(e)[:40]}`")


    @register_cmd("repeat")
    async def cmd_repeat(event, arg):
        try:
            parts = (arg or "").strip().split(None, 1)
            if len(parts) < 2: return await safe_edit(event, "❌ 𝐔𝐬𝐞 → `.repeat <n> <text>`")
            try: n = min(int(parts[0]), 20)
            except: return await safe_edit(event, "❌ 𝐈𝐧𝐯𝐚𝐥𝐢𝐝 𝐧𝐮𝐦𝐛𝐞𝐫")
            result = "\n".join([parts[1]] * n)
            await safe_edit(event, result[:4000])
        except Exception as e:
            await safe_edit(event, f"❌ → `{str(e)[:40]}`")


    @register_cmd("zalgo")
    async def cmd_zalgo(event, arg):
        try:
            if not arg: return await safe_edit(event, "❌ 𝐔𝐬𝐞 → `.zalgo <text>`")
            zalgo_chars = [chr(i) for i in range(0x0300, 0x036F)]
            result = ""
            for c in arg[:100]:
                result += c + "".join(random.choice(zalgo_chars) for _ in range(random.randint(1, 5)))
            await safe_edit(event, result)
        except Exception as e:
            await safe_edit(event, f"❌ → `{str(e)[:40]}`")


    @register_cmd("big")
    async def cmd_big(event, arg):
        try:
            if not arg: return await safe_edit(event, "❌ 𝐔𝐬𝐞 → `.big <text>`")
            BIG = {'a':'𝐀','b':'𝐁','c':'𝐂','d':'𝐃','e':'𝐄','f':'𝐅','g':'𝐆','h':'𝐇','i':'𝐈','j':'𝐉','k':'𝐊','l':'𝐋','m':'𝐌','n':'𝐍','o':'𝐎','p':'𝐏','q':'𝐐','r':'𝐑','s':'𝐒','t':'𝐓','u':'𝐔','v':'𝐕','w':'𝐖','x':'𝐗','y':'𝐘','z':'𝐙',' ':' '}
            result = "".join(BIG.get(c.lower(), c) for c in arg[:300])
            await safe_edit(event, result)
        except Exception as e:
            await safe_edit(event, f"❌ → `{str(e)[:40]}`")


    @register_cmd("small")
    async def cmd_small(event, arg):
        try:
            if not arg: return await safe_edit(event, "❌ 𝐔𝐬𝐞 → `.small <text>`")
            SMALL = {'a':'ᴀ','b':'ʙ','c':'ᴄ','d':'ᴅ','e':'ᴇ','f':'ꜰ','g':'ɢ','h':'ʜ','i':'ɪ','j':'ᴊ','k':'ᴋ','l':'ʟ','m':'ᴍ','n':'ɴ','o':'ᴏ','p':'ᴘ','q':'Q','r':'ʀ','s':'ꜱ','t':'ᴛ','u':'ᴜ','v':'ᴠ','w':'ᴡ','x':'x','y':'ʏ','z':'ᴢ'}
            result = "".join(SMALL.get(c.lower(), c) for c in arg[:300])
            await safe_edit(event, result)
        except Exception as e:
            await safe_edit(event, f"❌ → `{str(e)[:40]}`")


    @register_cmd("shadow")
    async def cmd_shadow(event, arg):
        try:
            if not arg: return await safe_edit(event, "❌ 𝐔𝐬𝐞 → `.shadow <text>`")
            result = f"░▒▓ {arg[:300]} ▓▒░"
            await safe_edit(event, result)
        except Exception as e:
            await safe_edit(event, f"❌ → `{str(e)[:40]}`")


    @register_cmd("camel")
    async def cmd_camel(event, arg):
        try:
            if not arg: return await safe_edit(event, "❌ 𝐔𝐬𝐞 → `.camel <text>`")
            words = arg.split()
            if not words: return await safe_edit(event, "❌ 𝐍𝐨 𝐖𝐨𝐫𝐝𝐬")
            result = words[0].lower() + "".join(w.capitalize() for w in words[1:])
            await safe_edit(event, f"🐪 𝐂𝐚𝐦𝐞𝐥𝐂𝐚𝐬𝐞 → `{result}`")
        except Exception as e:
            await safe_edit(event, f"❌ → `{str(e)[:40]}`")


    # ─── CRYPTO TOOLS ───
    @register_cmd("md5")
    async def cmd_md5(event, arg):
        try:
            if not arg: return await safe_edit(event, "❌ 𝐔𝐬𝐞 → `.md5 <text>`")
            result = hashlib.md5(arg.encode()).hexdigest()
            await safe_edit(event, f"🔐 𝐌𝐃𝟓\n━━━━━━━━━━━━━━━\n`{result}`")
        except Exception as e:
            await safe_edit(event, f"❌ → `{str(e)[:40]}`")


    @register_cmd("sha256")
    async def cmd_sha256(event, arg):
        try:
            if not arg: return await safe_edit(event, "❌ 𝐔𝐬𝐞 → `.sha256 <text>`")
            result = hashlib.sha256(arg.encode()).hexdigest()
            await safe_edit(event, f"🔐 𝐒𝐇𝐀𝟐𝟓𝟔\n━━━━━━━━━━━━━━━\n`{result}`")
        except Exception as e:
            await safe_edit(event, f"❌ → `{str(e)[:40]}`")


    @register_cmd("b64")
    async def cmd_b64(event, arg):
        try:
            if not arg: return await safe_edit(event, "❌ 𝐔𝐬𝐞 → `.b64 <text>`")
            result = base64.b64encode(arg.encode()).decode()
            await safe_edit(event, f"🔐 𝐁𝐚𝐬𝐞𝟔𝟒 𝐄𝐧𝐜𝐨𝐝𝐞\n━━━━━━━━━━━━━━━\n`{result}`")
        except Exception as e:
            await safe_edit(event, f"❌ → `{str(e)[:40]}`")


    @register_cmd("b64d")
    async def cmd_b64d(event, arg):
        try:
            if not arg: return await safe_edit(event, "❌ 𝐔𝐬𝐞 → `.b64d <base64>`")
            result = base64.b64decode(arg.encode()).decode()
            await safe_edit(event, f"🔓 𝐁𝐚𝐬𝐞𝟔𝟒 𝐃𝐞𝐜𝐨𝐝𝐞\n━━━━━━━━━━━━━━━\n`{result}`")
        except Exception as e:
            await safe_edit(event, f"❌ 𝐈𝐧𝐯𝐚𝐥𝐢𝐝 → `{str(e)[:40]}`")


    @register_cmd("uuid")
    async def cmd_uuid(event, _):
        try:
            result = str(uuid.uuid4())
            await safe_edit(event, f"🆔 𝐔𝐔𝐈𝐃\n━━━━━━━━━━━━━━━\n`{result}`")
        except Exception as e:
            await safe_edit(event, f"❌ → `{str(e)[:40]}`")


    @register_cmd("password")
    async def cmd_password(event, arg):
        try:
            try: length = max(8, min(int(arg), 64)) if arg else 16
            except: length = 16
            chars = string.ascii_letters + string.digits + "!@#$%^&*()_+-=[]{}|"
            pwd = "".join(random.choice(chars) for _ in range(length))
            await safe_edit(event, f"🔑 𝐏𝐚𝐬𝐬𝐰𝐨𝐫𝐝 ({length} chars)\n━━━━━━━━━━━━━━━\n`{pwd}`")
        except Exception as e:
            await safe_edit(event, f"❌ → `{str(e)[:40]}`")


    # ─── TIME TOOLS ───
    @register_cmd("time")
    async def cmd_time(event, _):
        try:
            now = datetime.now()
            await safe_edit(event, f"⏰ 𝐓𝐢𝐦𝐞\n━━━━━━━━━━━━━━━\n🕐 `{now.strftime('%H:%M:%S')}`\n📅 `{now.strftime('%d/%m/%Y')}`")
        except Exception as e:
            await safe_edit(event, f"❌ → `{str(e)[:40]}`")


    @register_cmd("date")
    async def cmd_date(event, _):
        try:
            now = datetime.now()
            days = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
            day = days[now.weekday()]
            await safe_edit(event, f"📅 𝐃𝐚𝐭𝐞\n━━━━━━━━━━━━━━━\n📆 `{now.strftime('%d %B %Y')}`\n📌 `{day}`")
        except Exception as e:
            await safe_edit(event, f"❌ → `{str(e)[:40]}`")


    @register_cmd("uptime")
    async def cmd_uptime(event, _):
        try:
            uptime = int(time.time() - START_TIME)
            hours = uptime // 3600
            minutes = (uptime % 3600) // 60
            seconds = uptime % 60
            await safe_edit(event, f"⏱️ 𝐔𝐩𝐭𝐢𝐦𝐞\n━━━━━━━━━━━━━━━\n`{hours}h {minutes}m {seconds}s`")
        except Exception as e:
            await safe_edit(event, f"❌ → `{str(e)[:40]}`")


    # ─── MATH TOOLS ───
    @register_cmd("random")
    async def cmd_random(event, arg):
        try:
            parts = (arg or "").strip().split()
            try:
                mn = int(parts[0]) if len(parts) > 0 else 1
                mx = int(parts[1]) if len(parts) > 1 else 100
            except: mn, mx = 1, 100
            if mn > mx: mn, mx = mx, mn
            result = random.randint(mn, mx)
            await safe_edit(event, f"🎲 𝐑𝐚𝐧𝐝𝐨𝐦 [{mn}, {mx}]\n━━━━━━━━━━━━━━━\n`{result}`")
        except Exception as e:
            await safe_edit(event, f"❌ → `{str(e)[:40]}`")


    @register_cmd("tempconv")
    async def cmd_tempconv(event, arg):
        try:
            parts = (arg or "").strip().split()
            if len(parts) < 2: return await safe_edit(event, "❌ 𝐔𝐬𝐞 → `.tempconv C/F <value>`")
            mode = parts[0].upper()
            val = float(parts[1])
            if mode == "C":
                result = f"{val}°C = {(val * 9/5) + 32:.2f}°F"
            elif mode == "F":
                result = f"{val}°F = {(val - 32) * 5/9:.2f}°C"
            else:
                return await safe_edit(event, "❌ 𝐔𝐬𝐞 𝐂 𝐨𝐫 𝐅")
            await safe_edit(event, f"🌡️ 𝐓𝐞𝐦𝐩 𝐂𝐨𝐧𝐯𝐞𝐫𝐭\n━━━━━━━━━━━━━━━\n`{result}`")
        except Exception as e:
            await safe_edit(event, f"❌ → `{str(e)[:40]}`")


    # ─── USER TOOLS ───
    @register_cmd("id")
    async def cmd_id(event, arg):
        try:
            if event.is_reply:
                r = await event.get_reply_message()
                uid = r.sender_id if r else event.sender_id
            else:
                uid = event.sender_id
            chat = event.chat_id
            await safe_edit(event, f"🆔 𝐈𝐃 𝐈𝐧𝐟𝐨\n━━━━━━━━━━━━━━━\n👤 𝐔𝐬𝐞𝐫 → `{uid}`\n💬 𝐂𝐡𝐚𝐭 → `{chat}`")
        except Exception as e:
            await safe_edit(event, f"❌ → `{str(e)[:40]}`")


    @register_cmd("chatid")
    async def cmd_chatid(event, _):
        try:
            await safe_edit(event, f"💬 𝐂𝐡𝐚𝐭 𝐈𝐃 → `{event.chat_id}`")
        except Exception as e:
            await safe_edit(event, f"❌ → `{str(e)[:40]}`")


    @register_cmd("whois")
    async def cmd_whois(event, arg):
        try:
            target = None
            if event.is_reply:
                r = await event.get_reply_message()
                if r and r.sender_id: target = r.sender_id
            elif arg:
                try:
                    ent = await bot.get_entity(arg)
                    target = ent.id
                except: return await safe_edit(event, "❌ 𝐈𝐧𝐯𝐚𝐥𝐢𝐝 𝐔𝐬𝐞𝐫")
            else:
                target = event.sender_id
            user = await bot.get_entity(target)
            uname = f"@{user.username}" if getattr(user, 'username', None) else "None"
            premium = getattr(user, 'premium', False)
            bot_flag = getattr(user, 'bot', False)
            text = (
                "🔍 𝐖𝐇𝐎𝐈𝐒\n━━━━━━━━━━━━━━━\n"
                f"👤 𝐍𝐚𝐦𝐞 → {getattr(user, 'first_name', '')} {getattr(user, 'last_name', '') or ''}\n"
                f"🆔 𝐈𝐃 → `{user.id}`\n"
                f"🔗 𝐔𝐬𝐞𝐫 → {uname}\n"
                f"⭐ 𝐏𝐫𝐞𝐦𝐢𝐮𝐦 → `{premium}`\n"
                f"🤖 𝐁𝐨𝐭 → `{bot_flag}`"
            )
            await safe_edit(event, text)
        except Exception as e:
            await safe_edit(event, f"❌ 𝐖𝐇𝐎𝐈𝐒 → `{str(e)[:40]}`")


    @register_cmd("mention")
    async def cmd_mention(event, arg):
        try:
            if event.is_reply:
                r = await event.get_reply_message()
                if r and r.sender_id:
                    user = await bot.get_entity(r.sender_id)
                    name = getattr(user, 'first_name', 'User')
                    await safe_edit(event, f"[{name}](tg://user?id={user.id})")
                    return
            if arg:
                try:
                    user = await bot.get_entity(arg)
                    name = getattr(user, 'first_name', 'User')
                    await safe_edit(event, f"[{name}](tg://user?id={user.id})")
                    return
                except: pass
            await safe_edit(event, "❌ 𝐑𝐞𝐩𝐥𝐲 / 𝐔𝐬𝐞𝐫𝐧𝐚𝐦𝐞")
        except Exception as e:
            await safe_edit(event, f"❌ → `{str(e)[:40]}`")


    @register_cmd("getpp")
    async def cmd_getpp(event, arg):
        try:
            target = None
            if event.is_reply:
                r = await event.get_reply_message()
                if r and r.sender_id: target = r.sender_id
            elif arg:
                try:
                    ent = await bot.get_entity(arg)
                    target = ent.id
                except: return await safe_edit(event, "❌ 𝐈𝐧𝐯𝐚𝐥𝐢𝐝")
            else:
                target = event.sender_id
            await safe_edit(event, "⚡ 𝐅𝐞𝐭𝐜𝐡𝐢𝐧𝐠 𝐏𝐏...")
            photo = await bot.download_profile_photo(target, file=bytes)
            if not photo: return await safe_edit(event, "❌ 𝐍𝐨 𝐏𝐫𝐨𝐟𝐢𝐥𝐞 𝐏𝐡𝐨𝐭𝐨")
            bio = BytesIO(photo); bio.name = "pp.jpg"
            await event.delete()
            await bot.send_file(event.chat_id, bio, caption="🖼️ 𝐏𝐫𝐨𝐟𝐢𝐥𝐞 𝐏𝐡𝐨𝐭𝐨")
        except Exception as e:
            await safe_edit(event, f"❌ 𝐆𝐞𝐭𝐏𝐏 → `{str(e)[:40]}`")


    @register_cmd("setname")
    async def cmd_setname(event, arg):
        try:
            if not arg: return await safe_edit(event, "❌ 𝐔𝐬𝐞 → `.setname <name>`")
            parts = arg.strip().split(None, 1)
            fname = parts[0][:64]
            lname = parts[1][:64] if len(parts) > 1 else ""
            await bot(functions.account.UpdateProfileRequest(first_name=fname, last_name=lname))
            await safe_edit(event, f"✅ 𝐍𝐚𝐦𝐞 𝐒𝐞𝐭 → `{fname} {lname}`")
        except Exception as e:
            await safe_edit(event, f"❌ 𝐒𝐞𝐭𝐍𝐚𝐦𝐞 → `{str(e)[:40]}`")


    @register_cmd("setbio")
    async def cmd_setbio(event, arg):
        try:
            bio = (arg or "")[:70]
            await bot(functions.account.UpdateProfileRequest(about=bio))
            await safe_edit(event, f"✅ 𝐁𝐢𝐨 𝐒𝐞𝐭 → `{bio}`")
        except Exception as e:
            await safe_edit(event, f"❌ 𝐒𝐞𝐭𝐁𝐢𝐨 → `{str(e)[:40]}`")


    @register_cmd("setpp", needs_reply=True)
    async def cmd_setpp(event, _):
        try:
            reply = await event.get_reply_message()
            if not reply or not reply.media:
                return await safe_edit(event, "❌ 𝐑𝐞𝐩𝐥𝐲 𝐭𝐨 𝐚𝐧 𝐢𝐦𝐚𝐠𝐞")
            file = await reply.download_media(file=bytes)
            if not file: return await safe_edit(event, "❌ 𝐃𝐨𝐰𝐧𝐥𝐨𝐚𝐝 𝐅𝐚𝐢𝐥")
            await bot(functions.photos.UploadProfilePhotoRequest(
                file=await bot.upload_file(BytesIO(file))
            ))
            await safe_edit(event, "✅ 𝐏𝐫𝐨𝐟𝐢𝐥𝐞 𝐏𝐡𝐨𝐭𝐨 𝐒𝐞𝐭")
        except Exception as e:
            await safe_edit(event, f"❌ 𝐒𝐞𝐭𝐏𝐏 → `{str(e)[:40]}`")


    # ─── GROUP MOD TOOLS ───
    @register_cmd("groupinfo")
    async def cmd_groupinfo(event, _):
        try:
            if not event.is_group:
                return await safe_edit(event, "⚠️ 𝐆𝐫𝐨𝐮𝐩 𝐎𝐧𝐥𝐲")
            chat = await bot.get_entity(event.chat_id)
            name = getattr(chat, 'title', 'Unknown')
            count = "Unknown"
            try:
                participants = await bot.get_participants(event.chat_id, limit=0)
                count = participants.total
            except: pass
            username = f"@{chat.username}" if getattr(chat, 'username', None) else "Private"
            text = (
                "ℹ️ 𝐆𝐫𝐨𝐮𝐩 𝐈𝐧𝐟𝐨\n━━━━━━━━━━━━━━━\n"
                f"📛 𝐍𝐚𝐦𝐞 → `{name}`\n"
                f"🆔 𝐈𝐃 → `{event.chat_id}`\n"
                f"👥 𝐌𝐞𝐦𝐛𝐞𝐫𝐬 → `{count}`\n"
                f"🔗 𝐔𝐬𝐞𝐫 → {username}"
            )
            await safe_edit(event, text)
        except Exception as e:
            await safe_edit(event, f"❌ 𝐆𝐫𝐨𝐮𝐩𝐈𝐧𝐟𝐨 → `{str(e)[:40]}`")


    @register_cmd("membercount")
    async def cmd_membercount(event, _):
        try:
            participants = await bot.get_participants(event.chat_id, limit=0)
            await safe_edit(event, f"👥 𝐌𝐞𝐦𝐛𝐞𝐫𝐬 → `{participants.total}`")
        except Exception as e:
            await safe_edit(event, f"❌ 𝐌𝐞𝐦𝐛𝐞𝐫𝐂𝐨𝐮𝐧𝐭 → `{str(e)[:40]}`")


    @register_cmd("invitelink")
    async def cmd_invitelink(event, _):
        try:
            if not event.is_group:
                return await safe_edit(event, "⚠️ 𝐆𝐫𝐨𝐮𝐩 𝐎𝐧𝐥𝐲")
            try:
                result = await bot(functions.messages.ExportChatInviteRequest(peer=event.chat_id))
                link = result.link
            except:
                try:
                    result = await bot(functions.channels.ExportInviteRequest(channel=event.chat_id))
                    link = result.link
                except: return await safe_edit(event, "❌ 𝐂𝐚𝐧𝐧𝐨𝐭 𝐆𝐞𝐭 𝐋𝐢𝐧𝐤")
            await safe_edit(event, f"🔗 𝐈𝐧𝐯𝐢𝐭𝐞 𝐋𝐢𝐧𝐤\n━━━━━━━━━━━━━━━\n`{link}`")
        except Exception as e:
            await safe_edit(event, f"❌ 𝐈𝐧𝐯𝐢𝐭𝐞𝐋𝐢𝐧𝐤 → `{str(e)[:40]}`")


    @register_cmd("ban", needs_reply=True, group_only=True)
    async def cmd_ban(event, arg):
        try:
            targets = await get_targets(event, arg)
            if not targets: return await safe_edit(event, "❌ 𝐍𝐨 𝐓𝐚𝐫𝐠𝐞𝐭")
            banned, failed = [], []
            for uid in targets:
                try: uid = int(uid)
                except: continue
                try:
                    await bot(functions.channels.EditBannedRequest(
                        channel=event.chat_id, participant=uid,
                        banned_rights=types.ChatBannedRights(until_date=None, view_messages=True)
                    ))
                    banned.append(str(uid))
                except: failed.append(str(uid))
            parts = []
            if banned: parts.append(f"🔨 𝐁𝐚𝐧𝐧𝐞𝐝 → `{', '.join(banned)}`")
            if failed: parts.append(f"⚠️ 𝐅𝐚𝐢𝐥𝐞𝐝 → `{', '.join(failed)}`")
            await safe_edit(event, "\n".join(parts) or "❌ 𝐍𝐨 𝐀𝐜𝐭𝐢𝐨𝐧")
        except Exception as e:
            await safe_edit(event, f"❌ 𝐁𝐚𝐧 → `{str(e)[:40]}`")


    @register_cmd("unban", needs_reply=True, group_only=True)
    async def cmd_unban(event, arg):
        try:
            targets = await get_targets(event, arg)
            if not targets: return await safe_edit(event, "❌ 𝐍𝐨 𝐓𝐚𝐫𝐠𝐞𝐭")
            unbanned, failed = [], []
            for uid in targets:
                try: uid = int(uid)
                except: continue
                try:
                    await bot(functions.channels.EditBannedRequest(
                        channel=event.chat_id, participant=uid,
                        banned_rights=types.ChatBannedRights(until_date=None)
                    ))
                    unbanned.append(str(uid))
                except: failed.append(str(uid))
            parts = []
            if unbanned: parts.append(f"✅ 𝐔𝐧𝐛𝐚𝐧𝐧𝐞𝐝 → `{', '.join(unbanned)}`")
            if failed: parts.append(f"⚠️ 𝐅𝐚𝐢𝐥𝐞𝐝 → `{', '.join(failed)}`")
            await safe_edit(event, "\n".join(parts) or "❌ 𝐍𝐨 𝐀𝐜𝐭𝐢𝐨𝐧")
        except Exception as e:
            await safe_edit(event, f"❌ 𝐔𝐧𝐛𝐚𝐧 → `{str(e)[:40]}`")


    @register_cmd("kick", needs_reply=True, group_only=True)
    async def cmd_kick(event, arg):
        try:
            targets = await get_targets(event, arg)
            if not targets: return await safe_edit(event, "❌ 𝐍𝐨 𝐓𝐚𝐫𝐠𝐞𝐭")
            kicked, failed = [], []
            for uid in targets:
                try: uid = int(uid)
                except: continue
                try: await bot.kick_participant(event.chat_id, uid); kicked.append(str(uid))
                except: failed.append(str(uid))
            parts = []
            if kicked: parts.append(f"👞 𝐊𝐢𝐜𝐤𝐞𝐝 → `{', '.join(kicked)}`")
            if failed: parts.append(f"⚠️ 𝐅𝐚𝐢𝐥𝐞𝐝 → `{', '.join(failed)}`")
            await safe_edit(event, "\n".join(parts) or "❌ 𝐍𝐨 𝐀𝐜𝐭𝐢𝐨𝐧")
        except Exception as e:
            await safe_edit(event, f"❌ 𝐊𝐢𝐜𝐤 → `{str(e)[:40]}`")


    @register_cmd("promote", needs_reply=True, group_only=True)
    async def cmd_promote(event, arg):
        try:
            targets = await get_targets(event, arg)
            if not targets: return await safe_edit(event, "❌ 𝐍𝐨 𝐓𝐚𝐫𝐠𝐞𝐭")
            promoted, failed = [], []
            for uid in targets:
                try: uid = int(uid)
                except: continue
                try:
                    await bot(functions.channels.EditAdminRequest(
                        channel=event.chat_id, user_id=uid,
                        admin_rights=types.ChatAdminRights(
                            change_info=True, delete_messages=True, ban_users=True,
                            invite_users=True, pin_messages=True, manage_call=True
                        ), rank="Admin"
                    ))
                    promoted.append(str(uid))
                except: failed.append(str(uid))
            parts = []
            if promoted: parts.append(f"⭐ 𝐏𝐫𝐨𝐦𝐨𝐭𝐞𝐝 → `{', '.join(promoted)}`")
            if failed: parts.append(f"⚠️ 𝐅𝐚𝐢𝐥𝐞𝐝 → `{', '.join(failed)}`")
            await safe_edit(event, "\n".join(parts) or "❌ 𝐍𝐨 𝐀𝐜𝐭𝐢𝐨𝐧")
        except Exception as e:
            await safe_edit(event, f"❌ 𝐏𝐫𝐨𝐦𝐨𝐭𝐞 → `{str(e)[:40]}`")


    @register_cmd("demote", needs_reply=True, group_only=True)
    async def cmd_demote(event, arg):
        try:
            targets = await get_targets(event, arg)
            if not targets: return await safe_edit(event, "❌ 𝐍𝐨 𝐓𝐚𝐫𝐠𝐞𝐭")
            demoted, failed = [], []
            for uid in targets:
                try: uid = int(uid)
                except: continue
                try:
                    await bot(functions.channels.EditAdminRequest(
                        channel=event.chat_id, user_id=uid,
                        admin_rights=types.ChatAdminRights(), rank=""
                    ))
                    demoted.append(str(uid))
                except: failed.append(str(uid))
            parts = []
            if demoted: parts.append(f"⬇️ 𝐃𝐞𝐦𝐨𝐭𝐞𝐝 → `{', '.join(demoted)}`")
            if failed: parts.append(f"⚠️ 𝐅𝐚𝐢𝐥𝐞𝐝 → `{', '.join(failed)}`")
            await safe_edit(event, "\n".join(parts) or "❌ 𝐍𝐨 𝐀𝐜𝐭𝐢𝐨𝐧")
        except Exception as e:
            await safe_edit(event, f"❌ 𝐃𝐞𝐦𝐨𝐭𝐞 → `{str(e)[:40]}`")


    @register_cmd("warn", needs_reply=True)
    async def cmd_warn(event, arg):
        try:
            targets = await get_targets(event, arg)
            if not targets: return await safe_edit(event, "❌ 𝐍𝐨 𝐓𝐚𝐫𝐠𝐞𝐭")
            results = []
            for uid in targets:
                try: uid = int(uid)
                except: continue
                warns[uid] = warns.get(uid, 0) + 1
                results.append(f"`{uid}` → ⚠️ `{warns[uid]}` warnings")
            save_warns()
            await safe_edit(event, "⚠️ 𝐖𝐀𝐑𝐍\n━━━━━━━━━━━━━━━\n" + "\n".join(results))
        except Exception as e:
            await safe_edit(event, f"❌ 𝐖𝐚𝐫𝐧 → `{str(e)[:40]}`")


    @register_cmd("warnlist")
    async def cmd_warnlist(event, _):
        try:
            if not warns: return await safe_edit(event, "⚠️ 𝐍𝐨 𝐖𝐚𝐫𝐧𝐬")
            lines = [f"• `{uid}` → `{count}` warns" for uid, count in sorted(warns.items())]
            await safe_edit(event, "⚠️ 𝐖𝐀𝐑𝐍 𝐋𝐈𝐒𝐓\n━━━━━━━━━━━━━━━\n" + "\n".join(lines))
        except Exception as e:
            await safe_edit(event, f"❌ 𝐖𝐚𝐫𝐧𝐋𝐢𝐬𝐭 → `{str(e)[:40]}`")


    @register_cmd("clearwarn")
    async def cmd_clearwarn(event, arg):
        try:
            targets = await get_targets(event, arg)
            if targets:
                for uid in targets: warns.pop(uid, None)
                await safe_edit(event, f"✅ 𝐖𝐚𝐫𝐧𝐬 𝐂𝐥𝐞𝐚𝐫𝐞𝐝 → `{len(targets)}` users")
            else:
                warns.clear()
                await safe_edit(event, "✅ 𝐀𝐥𝐥 𝐖𝐚𝐫𝐧𝐬 𝐂𝐥𝐞𝐚𝐫𝐞𝐝")
            save_warns()
        except Exception as e:
            await safe_edit(event, f"❌ 𝐂𝐥𝐞𝐚𝐫𝐖𝐚𝐫𝐧 → `{str(e)[:40]}`")


    @register_cmd("pin", needs_reply=True, group_only=True)
    async def cmd_pin(event, _):
        try:
            reply = await event.get_reply_message()
            if not reply: return await safe_edit(event, "❌ 𝐑𝐞𝐩𝐥𝐲 𝐭𝐨 𝐩𝐢𝐧")
            await bot.pin_message(event.chat_id, reply.id)
            await safe_edit(event, "📌 𝐌𝐞𝐬𝐬𝐚𝐠𝐞 𝐏𝐢𝐧𝐧𝐞𝐝")
        except Exception as e:
            await safe_edit(event, f"❌ 𝐏𝐢𝐧 → `{str(e)[:40]}`")


    @register_cmd("unpin", group_only=True)
    async def cmd_unpin(event, _):
        try:
            await bot(functions.messages.UnpinAllMessagesRequest(peer=event.chat_id))
            await safe_edit(event, "📌 𝐀𝐥𝐥 𝐌𝐬𝐠𝐬 𝐔𝐧𝐩𝐢𝐧𝐧𝐞𝐝")
        except Exception as e:
            await safe_edit(event, f"❌ 𝐔𝐧𝐩𝐢𝐧 → `{str(e)[:40]}`")


    # ─── FUN COMMANDS ───
    @register_cmd("joke")
    async def cmd_joke(event, _):
        try:
            j = random.choice(joke_list)
            await safe_edit(event, f"😂 𝐉𝐎𝐊𝐄\n━━━━━━━━━━━━━━━\n{j}")
        except Exception as e:
            await safe_edit(event, f"❌ → `{str(e)[:40]}`")


    @register_cmd("riddle")
    async def cmd_riddle(event, _):
        try:
            r = random.choice(riddle_list)
            await safe_edit(event, f"🤔 𝐑𝐈𝐃𝐃𝐋𝐄\n━━━━━━━━━━━━━━━\n{r}")
        except Exception as e:
            await safe_edit(event, f"❌ → `{str(e)[:40]}`")


    @register_cmd("fact")
    async def cmd_fact(event, _):
        try:
            f = random.choice(fact_list)
            await safe_edit(event, f"🧠 𝐅𝐀𝐂𝐓\n━━━━━━━━━━━━━━━\n{f}")
        except Exception as e:
            await safe_edit(event, f"❌ → `{str(e)[:40]}`")


    @register_cmd("quote")
    async def cmd_quote(event, _):
        try:
            q = random.choice(quote_list)
            await safe_edit(event, f"💭 𝐐𝐔𝐎𝐓𝐄\n━━━━━━━━━━━━━━━\n{q}")
        except Exception as e:
            await safe_edit(event, f"❌ → `{str(e)[:40]}`")


    @register_cmd("truth")
    async def cmd_truth(event, _):
        try:
            t = random.choice(truth_list)
            await safe_edit(event, f"🤥 𝐓𝐑𝐔𝐓𝐇\n━━━━━━━━━━━━━━━\n{t}")
        except Exception as e:
            await safe_edit(event, f"❌ → `{str(e)[:40]}`")


    @register_cmd("dare")
    async def cmd_dare(event, _):
        try:
            d = random.choice(dare_list)
            await safe_edit(event, f"😈 𝐃𝐀𝐑𝐄\n━━━━━━━━━━━━━━━\n{d}")
        except Exception as e:
            await safe_edit(event, f"❌ → `{str(e)[:40]}`")


    @register_cmd("pickup")
    async def cmd_pickup(event, _):
        try:
            p = random.choice(pickup_list)
            await safe_edit(event, f"💘 𝐏𝐈𝐂𝐊𝐔𝐏 𝐋𝐈𝐍𝐄\n━━━━━━━━━━━━━━━\n{p}")
        except Exception as e:
            await safe_edit(event, f"❌ → `{str(e)[:40]}`")


    @register_cmd("compliment")
    async def cmd_compliment(event, _):
        try:
            c = random.choice(compliment_list)
            await safe_edit(event, f"🌟 𝐂𝐎𝐌𝐏𝐋𝐈𝐌𝐄𝐍𝐓\n━━━━━━━━━━━━━━━\n{c}")
        except Exception as e:
            await safe_edit(event, f"❌ → `{str(e)[:40]}`")


    @register_cmd("roastme")
    async def cmd_roastme(event, _):
        try:
            r = random.choice(roast_list)
            await safe_edit(event, f"🔥 𝐑𝐎𝐀𝐒𝐓 𝐘𝐎𝐔𝐑𝐒𝐄𝐋𝐅\n━━━━━━━━━━━━━━━\n{r}")
        except Exception as e:
            await safe_edit(event, f"❌ → `{str(e)[:40]}`")


    @register_cmd("8ball")
    async def cmd_8ball(event, arg):
        try:
            if not arg: return await safe_edit(event, "❌ 𝐔𝐬𝐞 → `.8ball <question>`")
            answers = [
                "🟢 𝐘𝐞𝐬, definitely!","🟢 𝐁𝐞𝐭 𝐨𝐧 𝐢𝐭!","🟢 𝐌𝐨𝐬𝐭 𝐥𝐢𝐤𝐞𝐥𝐲!",
                "🟡 𝐂𝐚𝐧𝐧𝐨𝐭 𝐩𝐫𝐞𝐝𝐢𝐜𝐭 𝐧𝐨𝐰","🟡 𝐀𝐬𝐤 𝐚𝐠𝐚𝐢𝐧 𝐥𝐚𝐭𝐞𝐫","🟡 𝐂𝐨𝐧𝐜𝐞𝐧𝐭𝐫𝐚𝐭𝐞 𝐚𝐧𝐝 𝐚𝐬𝐤",
                "🔴 𝐃𝐨𝐧'𝐭 𝐜𝐨𝐮𝐧𝐭 𝐨𝐧 𝐢𝐭","🔴 𝐕𝐞𝐫𝐲 𝐝𝐨𝐮𝐛𝐭𝐟𝐮𝐥","🔴 𝐎𝐮𝐭𝐥𝐨𝐨𝐤 𝐧𝐨𝐭 𝐠𝐨𝐨𝐝",
            ]
            ans = random.choice(answers)
            await safe_edit(event, f"🎱 𝐌𝐀𝐆𝐈𝐂 𝟖-𝐁𝐀𝐋𝐋\n━━━━━━━━━━━━━━━\n❓ {arg}\n\n{ans}")
        except Exception as e:
            await safe_edit(event, f"❌ → `{str(e)[:40]}`")


    @register_cmd("rps")
    async def cmd_rps(event, arg):
        try:
            choices = {"r": "🪨 𝐑𝐨𝐜𝐤", "p": "📄 𝐏𝐚𝐩𝐞𝐫", "s": "✂️ 𝐒𝐜𝐢𝐬𝐬𝐨𝐫𝐬"}
            wins = {"r": "s", "p": "r", "s": "p"}
            if not arg or arg.lower() not in choices:
                return await safe_edit(event, "❌ 𝐔𝐬𝐞 → `.rps r/p/s`")
            user_choice = arg.lower()
            bot_choice = random.choice(list(choices.keys()))
            if user_choice == bot_choice: result = "🤝 𝐃𝐫𝐚𝐰!"
            elif wins[user_choice] == bot_choice: result = "🏆 𝐘𝐨𝐮 𝐖𝐢𝐧!"
            else: result = "😈 𝐁𝐨𝐭 𝐖𝐢𝐧𝐬!"
            text = f"✂️🪨📄 𝐑𝐏𝐒\n━━━━━━━━━━━━━━━\n👤 𝐘𝐨𝐮 → {choices[user_choice]}\n🤖 𝐁𝐨𝐭 → {choices[bot_choice]}\n\n{result}"
            if event.out: await safe_edit(event, text)
            else: await event.reply(text)
        except Exception as e:
            await safe_edit(event, f"❌ → `{str(e)[:40]}`")


    @register_cmd("choose")
    async def cmd_choose(event, arg):
        try:
            if not arg: return await safe_edit(event, "❌ 𝐔𝐬𝐞 → `.choose a|b|c`")
            opts = [o.strip() for o in arg.split("|") if o.strip()]
            if not opts: return await safe_edit(event, "❌ 𝐍𝐨 𝐎𝐩𝐭𝐢𝐨𝐧𝐬")
            chosen = random.choice(opts)
            await safe_edit(event, f"🎯 𝐂𝐇𝐎𝐈𝐂𝐄\n━━━━━━━━━━━━━━━\n🏆 `{chosen}`")
        except Exception as e:
            await safe_edit(event, f"❌ → `{str(e)[:40]}`")


    # ─── MESSAGE TOOLS ───
    @register_cmd("del", needs_reply=True)
    async def cmd_del(event, _):
        try:
            reply = await event.get_reply_message()
            if reply:
                await reply.delete()
            await event.delete()
        except Exception as e:
            await safe_edit(event, f"❌ 𝐃𝐞𝐥 → `{str(e)[:40]}`")


    @register_cmd("echo")
    async def cmd_echo(event, arg):
        try:
            if not arg: return await safe_edit(event, "❌ 𝐔𝐬𝐞 → `.echo <text>`")
            await event.delete()
            await bot.send_message(event.chat_id, arg)
        except Exception as e:
            await safe_edit(event, f"❌ 𝐄𝐜𝐡𝐨 → `{str(e)[:40]}`")


    @register_cmd("react")
    async def cmd_react(event, arg):
        try:
            if event.is_reply:
                r = await event.get_reply_message()
                emoji = arg.strip() if arg else "❤️"
                await bot(functions.messages.SendReactionRequest(
                    peer=event.chat_id, msg_id=r.id,
                    reaction=[types.ReactionEmoji(emoticon=emoji)]
                ))
                await safe_edit(event, f"✅ 𝐑𝐞𝐚𝐜𝐭𝐞𝐝 {emoji}")
            else:
                await safe_edit(event, "❌ 𝐑𝐞𝐩𝐥𝐲 𝐭𝐨 𝐚 𝐦𝐞𝐬𝐬𝐚𝐠𝐞")
        except Exception as e:
            await safe_edit(event, f"❌ 𝐑𝐞𝐚𝐜𝐭 → `{str(e)[:40]}`")


    @register_cmd("read")
    async def cmd_read(event, _):
        try:
            await bot.send_read_acknowledge(event.chat_id)
            await safe_edit(event, "✅ 𝐌𝐬𝐠𝐬 𝐌𝐚𝐫𝐤𝐞𝐝 𝐀𝐬 𝐑𝐞𝐚𝐝")
        except Exception as e:
            await safe_edit(event, f"❌ 𝐑𝐞𝐚𝐝 → `{str(e)[:40]}`")


    @register_cmd("typing")
    async def cmd_typing(event, arg):
        try:
            try: secs = min(int(arg), 10) if arg else 3
            except: secs = 3
            await safe_edit(event, f"⌨️ 𝐓𝐲𝐩𝐢𝐧𝐠 𝐟𝐨𝐫 `{secs}s`...")
            async with bot.action(event.chat_id, 'typing'):
                await asyncio.sleep(secs)
            await event.delete()
        except Exception as e:
            await safe_edit(event, f"❌ 𝐓𝐲𝐩𝐢𝐧𝐠 → `{str(e)[:40]}`")


    @register_cmd("online")
    async def cmd_online(event, _):
        try:
            await bot(functions.account.UpdateStatusRequest(offline=False))
            await safe_edit(event, "✅ 𝐒𝐞𝐭 𝐀𝐬 𝐎𝐧𝐥𝐢𝐧𝐞 🟢")
        except Exception as e:
            await safe_edit(event, f"❌ 𝐎𝐧𝐥𝐢𝐧𝐞 → `{str(e)[:40]}`")


    @register_cmd("myip")
    async def cmd_myip(event, _):
        try:
            await safe_edit(event, "⚡ 𝐅𝐞𝐭𝐜𝐡𝐢𝐧𝐠 𝐈𝐏...")
            try:
                ip_data = requests.get("http://ip-api.com/json/", timeout=8).json()
                ip = ip_data.get("query", "Unknown")
                country = ip_data.get("country", "Unknown")
                isp = ip_data.get("isp", "Unknown")
            except: return await safe_edit(event, "❌ 𝐅𝐞𝐭𝐜𝐡 𝐅𝐚𝐢𝐥")
            text = f"🌐 𝗠𝗬 𝗜𝗣\n━━━━━━━━━━━━━━━\n📡 `{ip}`\n🌍 `{country}`\n📍 `{isp}`"
            await safe_edit(event, text)
        except Exception as e:
            await safe_edit(event, f"❌ → `{str(e)[:40]}`")


    # ─── EXTRA TAGDA TOOLS ───

    @register_cmd("hex")
    async def cmd_hex(event, arg):
        try:
            if not arg: return await safe_edit(event, "❌ Use → `.hex <text>`")
            result = " ".join(format(ord(c), '02X') for c in arg[:100])
            await safe_edit(event, f"🔢 𝗛𝗘𝗫\n━━━━━━━━━━━━━━━\n`{result}`")
        except Exception as e:
            await safe_edit(event, f"❌ → `{str(e)[:40]}`")


    @register_cmd("octal")
    async def cmd_octal(event, arg):
        try:
            if not arg: return await safe_edit(event, "❌ Use → `.octal <text>`")
            result = " ".join(format(ord(c), 'o') for c in arg[:100])
            await safe_edit(event, f"🔢 𝗢𝗖𝗧𝗔𝗟\n━━━━━━━━━━━━━━━\n`{result}`")
        except Exception as e:
            await safe_edit(event, f"❌ → `{str(e)[:40]}`")


    @register_cmd("ascii")
    async def cmd_ascii(event, arg):
        try:
            if not arg: return await safe_edit(event, "❌ Use → `.ascii <text>`")
            result = " ".join(str(ord(c)) for c in arg[:100])
            await safe_edit(event, f"🔡 𝗔𝗦𝗖𝗜𝗜 𝗩𝗮𝗹𝘂𝗲𝘀\n━━━━━━━━━━━━━━━\n`{result}`")
        except Exception as e:
            await safe_edit(event, f"❌ → `{str(e)[:40]}`")


    @register_cmd("charcount")
    async def cmd_charcount(event, arg):
        try:
            if not arg: return await safe_edit(event, "❌ Use → `.charcount <text>`")
            total = len(arg)
            letters = sum(c.isalpha() for c in arg)
            digits = sum(c.isdigit() for c in arg)
            spaces = sum(c.isspace() for c in arg)
            special = total - letters - digits - spaces
            await safe_edit(event, (
                f"📊 𝗖𝗛𝗔𝗥 𝗔𝗡𝗔𝗟𝗬𝗦𝗜𝗦\n━━━━━━━━━━━━━━━\n"
                f"📝 Total    → `{total}`\n"
                f"🔤 Letters  → `{letters}`\n"
                f"🔢 Digits   → `{digits}`\n"
                f"⬜ Spaces   → `{spaces}`\n"
                f"✨ Special  → `{special}`"
            ))
        except Exception as e:
            await safe_edit(event, f"❌ → `{str(e)[:40]}`")


    @register_cmd("palindrome")
    async def cmd_palindrome(event, arg):
        try:
            if not arg: return await safe_edit(event, "❌ Use → `.palindrome <text>`")
            clean = arg.lower().replace(" ", "")
            is_pal = clean == clean[::-1]
            icon = "✅" if is_pal else "❌"
            result = "Palindrome hai!" if is_pal else "Palindrome nahi hai!"
            await safe_edit(event, f"{icon} `{arg}`\n━━━━━━━━━━━━━━━\n{result}")
        except Exception as e:
            await safe_edit(event, f"❌ → `{str(e)[:40]}`")


    @register_cmd("vowels")
    async def cmd_vowels(event, arg):
        try:
            if not arg: return await safe_edit(event, "❌ Use → `.vowels <text>`")
            vs = [c for c in arg.lower() if c in 'aeiou']
            cs = [c for c in arg.lower() if c.isalpha() and c not in 'aeiou']
            await safe_edit(event, (
                f"🔤 𝗩𝗢𝗪𝗘𝗟 𝗖𝗢𝗨𝗡𝗧\n━━━━━━━━━━━━━━━\n"
                f"🅰️ Vowels    → `{len(vs)}` ({', '.join(vs[:20])})\n"
                f"🔡 Consonants → `{len(cs)}`"
            ))
        except Exception as e:
            await safe_edit(event, f"❌ → `{str(e)[:40]}`")


    @register_cmd("titlecase")
    async def cmd_titlecase(event, arg):
        try:
            if not arg: return await safe_edit(event, "❌ Use → `.titlecase <text>`")
            await safe_edit(event, f"📝 `{arg.title()}`")
        except Exception as e:
            await safe_edit(event, f"❌ → `{str(e)[:40]}`")


    @register_cmd("snake")
    async def cmd_snake(event, arg):
        try:
            if not arg: return await safe_edit(event, "❌ Use → `.snake <text>`")
            result = "_".join(arg.lower().split())
            await safe_edit(event, f"🐍 𝘀𝗻𝗮𝗸𝗲_𝗰𝗮𝘀𝗲 → `{result}`")
        except Exception as e:
            await safe_edit(event, f"❌ → `{str(e)[:40]}`")


    @register_cmd("shout")
    async def cmd_shout(event, arg):
        try:
            if not arg: return await safe_edit(event, "❌ Use → `.shout <text>`")
            result = "  ".join(arg.upper())
            await safe_edit(event, f"📢 `{result}`")
        except Exception as e:
            await safe_edit(event, f"❌ → `{str(e)[:40]}`")


    @register_cmd("alternating")
    async def cmd_alternating(event, arg):
        try:
            if not arg: return await safe_edit(event, "❌ Use → `.alternating <text>`")
            result = "".join(c.upper() if i % 2 == 0 else c.lower() for i, c in enumerate(arg))
            await safe_edit(event, f"🔀 `{result}`")
        except Exception as e:
            await safe_edit(event, f"❌ → `{str(e)[:40]}`")


    @register_cmd("spaceit")
    async def cmd_spaceit(event, arg):
        try:
            if not arg: return await safe_edit(event, "❌ Use → `.spaceit <text>`")
            result = " ".join(arg)
            await safe_edit(event, f"↔️ `{result}`")
        except Exception as e:
            await safe_edit(event, f"❌ → `{str(e)[:40]}`")


    @register_cmd("wordfreq")
    async def cmd_wordfreq(event, arg):
        try:
            if not arg: return await safe_edit(event, "❌ Use → `.wordfreq <text>`")
            words = arg.lower().split()
            freq: Dict[str, int] = {}
            for w in words:
                freq[w] = freq.get(w, 0) + 1
            top = sorted(freq.items(), key=lambda x: x[1], reverse=True)[:10]
            lines = "\n".join(f"  `{w}` → {n}x" for w, n in top)
            await safe_edit(event, f"📊 𝗪𝗢𝗥𝗗 𝗙𝗥𝗘𝗤𝗨𝗘𝗡𝗖𝗬\n━━━━━━━━━━━━━━━\n{lines}")
        except Exception as e:
            await safe_edit(event, f"❌ → `{str(e)[:40]}`")


    @register_cmd("removespaces")
    async def cmd_removespaces(event, arg):
        try:
            if not arg: return await safe_edit(event, "❌ Use → `.removespaces <text>`")
            await safe_edit(event, f"✂️ `{''.join(arg.split())}`")
        except Exception as e:
            await safe_edit(event, f"❌ → `{str(e)[:40]}`")


    @register_cmd("truncate")
    async def cmd_truncate(event, arg):
        try:
            parts = (arg or "").strip().split(None, 1)
            if len(parts) < 2: return await safe_edit(event, "❌ Use → `.truncate <n> <text>`")
            try: n = int(parts[0])
            except: return await safe_edit(event, "❌ Invalid number")
            text = parts[1]
            result = text[:n] + ("..." if len(text) > n else "")
            await safe_edit(event, f"✂️ `{result}`")
        except Exception as e:
            await safe_edit(event, f"❌ → `{str(e)[:40]}`")


    @register_cmd("percentage")
    async def cmd_percentage(event, arg):
        try:
            parts = (arg or "").strip().split()
            if len(parts) < 2: return await safe_edit(event, "❌ Use → `.percentage <value> <total>`")
            val, total = float(parts[0]), float(parts[1])
            if total == 0: return await safe_edit(event, "❌ Total 0 nahi ho sakta")
            pct = (val / total) * 100
            await safe_edit(event, f"📊 𝗣𝗘𝗥𝗖𝗘𝗡𝗧𝗔𝗚𝗘\n━━━━━━━━━━━━━━━\n`{val}` of `{total}` = **{pct:.2f}%**")
        except Exception as e:
            await safe_edit(event, f"❌ → `{str(e)[:40]}`")


    @register_cmd("square")
    async def cmd_square(event, arg):
        try:
            if not arg: return await safe_edit(event, "❌ Use → `.square <number>`")
            n = float(arg.strip())
            sq = n ** 2
            sqrt = math.sqrt(abs(n))
            await safe_edit(event, f"🔢 𝗦𝗤𝗨𝗔𝗥𝗘\n━━━━━━━━━━━━━━━\n`{n}²` = `{sq}`\n√`{abs(n)}` = `{sqrt:.4f}`")
        except Exception as e:
            await safe_edit(event, f"❌ → `{str(e)[:40]}`")


    @register_cmd("prime")
    async def cmd_prime(event, arg):
        try:
            if not arg: return await safe_edit(event, "❌ Use → `.prime <number>`")
            n = int(arg.strip())
            if n < 2:
                return await safe_edit(event, f"❌ `{n}` prime nahi hai")
            is_prime = all(n % i != 0 for i in range(2, int(n**0.5)+1))
            icon = "✅" if is_prime else "❌"
            msg = "Prime hai!" if is_prime else "Prime nahi hai!"
            await safe_edit(event, f"{icon} `{n}` — {msg}")
        except Exception as e:
            await safe_edit(event, f"❌ → `{str(e)[:40]}`")


    @register_cmd("factorial")
    async def cmd_factorial(event, arg):
        try:
            if not arg: return await safe_edit(event, "❌ Use → `.factorial <n>`")
            n = int(arg.strip())
            if n < 0: return await safe_edit(event, "❌ Negative number nahi chalega")
            if n > 20: return await safe_edit(event, "❌ Max 20 tak")
            result = math.factorial(n)
            await safe_edit(event, f"🔢 `{n}!` = `{result}`")
        except Exception as e:
            await safe_edit(event, f"❌ → `{str(e)[:40]}`")


    @register_cmd("fibonacci")
    async def cmd_fibonacci(event, arg):
        try:
            if not arg: return await safe_edit(event, "❌ Use → `.fibonacci <n>`")
            n = min(int(arg.strip()), 30)
            a, b = 0, 1
            seq = []
            for _ in range(n):
                seq.append(a)
                a, b = b, a + b
            await safe_edit(event, f"🌀 𝗙𝗜𝗕𝗢𝗡𝗔𝗖𝗖𝗜 ({n} terms)\n━━━━━━━━━━━━━━━\n`{', '.join(map(str, seq))}`")
        except Exception as e:
            await safe_edit(event, f"❌ → `{str(e)[:40]}`")


    @register_cmd("bmi")
    async def cmd_bmi(event, arg):
        try:
            parts = (arg or "").strip().split()
            if len(parts) < 2: return await safe_edit(event, "❌ Use → `.bmi <weight_kg> <height_cm>`")
            weight, height_cm = float(parts[0]), float(parts[1])
            height_m = height_cm / 100
            bmi = weight / (height_m ** 2)
            if bmi < 18.5: cat = "🟡 Underweight"
            elif bmi < 25: cat = "🟢 Normal"
            elif bmi < 30: cat = "🟠 Overweight"
            else: cat = "🔴 Obese"
            await safe_edit(event, (
                f"⚖️ 𝗕𝗠𝗜 𝗖𝗔𝗟𝗖𝗨𝗟𝗔𝗧𝗢𝗥\n━━━━━━━━━━━━━━━\n"
                f"⚖️ Weight → `{weight} kg`\n"
                f"📏 Height → `{height_cm} cm`\n"
                f"📊 BMI    → **{bmi:.1f}**\n"
                f"💡 Status → {cat}"
            ))
        except Exception as e:
            await safe_edit(event, f"❌ → `{str(e)[:40]}`")


    @register_cmd("age")
    async def cmd_age(event, arg):
        try:
            if not arg: return await safe_edit(event, "❌ Use → `.age <DD/MM/YYYY>`")
            from datetime import date
            parts = arg.strip().split("/")
            if len(parts) != 3: return await safe_edit(event, "❌ Format: DD/MM/YYYY")
            bd = date(int(parts[2]), int(parts[1]), int(parts[0]))
            today = date.today()
            age_years = (today - bd).days // 365
            age_days = (today - bd).days
            await safe_edit(event, (
                f"🎂 𝗔𝗚𝗘 𝗖𝗔𝗟𝗖𝗨𝗟𝗔𝗧𝗢𝗥\n━━━━━━━━━━━━━━━\n"
                f"📅 DOB   → `{arg.strip()}`\n"
                f"🎂 Age   → **{age_years} years**\n"
                f"📆 Days  → `{age_days} days`"
            ))
        except Exception as e:
            await safe_edit(event, f"❌ → `{str(e)[:40]}`")


    @register_cmd("coin")
    async def cmd_coin(event, _):
        try:
            result = random.choice(["🪙 HEADS", "🪙 TAILS"])
            await safe_edit(event, f"🪙 𝗖𝗢𝗜𝗡 𝗙𝗟𝗜𝗣\n━━━━━━━━━━━━━━━\n{result}!")
        except Exception as e:
            await safe_edit(event, f"❌ → `{str(e)[:40]}`")


    @register_cmd("lucky")
    async def cmd_lucky(event, _):
        try:
            n = random.randint(1, 100)
            if n >= 80: msg = "🎉 Bahut Lucky hai aaj!"
            elif n >= 50: msg = "😊 Thoda lucky hai!"
            elif n >= 30: msg = "😐 Average luck hai"
            else: msg = "😬 Aaj ghhar baith!"
            await safe_edit(event, f"🍀 𝗟𝗨𝗖𝗞𝗬 𝗦𝗖𝗢𝗥𝗘\n━━━━━━━━━━━━━━━\n🎯 Score → **{n}/100**\n{msg}")
        except Exception as e:
            await safe_edit(event, f"❌ → `{str(e)[:40]}`")


    @register_cmd("roll")
    async def cmd_roll(event, arg):
        try:
            sides = int(arg.strip()) if arg and arg.strip().isdigit() else 6
            sides = max(2, min(sides, 1000))
            result = random.randint(1, sides)
            await safe_edit(event, f"🎲 𝗗𝗜𝗖𝗘 𝗥𝗢𝗟𝗟 (d{sides})\n━━━━━━━━━━━━━━━\n**{result}**")
        except Exception as e:
            await safe_edit(event, f"❌ → `{str(e)[:40]}`")


    @register_cmd("number")
    async def cmd_number(event, arg):
        try:
            if not arg: return await safe_edit(event, "❌ Use → `.number <n>`")
            n = int(arg.strip())
            binary = bin(n)[2:]
            octal = oct(n)[2:]
            hexa = hex(n)[2:].upper()
            await safe_edit(event, (
                f"🔢 𝗡𝗨𝗠𝗕𝗘𝗥 𝗜𝗡𝗙𝗢 → `{n}`\n━━━━━━━━━━━━━━━\n"
                f"🔵 Binary  → `{binary}`\n"
                f"🟠 Octal   → `{octal}`\n"
                f"🟣 Hex     → `{hexa}`\n"
                f"📐 Squared → `{n**2}`"
            ))
        except Exception as e:
            await safe_edit(event, f"❌ → `{str(e)[:40]}`")


    @register_cmd("clap")
    async def cmd_clap(event, arg):
        try:
            if not arg: return await safe_edit(event, "❌ Use → `.clap <text>`")
            result = "👏".join(arg.split())
            await safe_edit(event, result)
        except Exception as e:
            await safe_edit(event, f"❌ → `{str(e)[:40]}`")


    @register_cmd("mock")
    async def cmd_mock(event, arg):
        try:
            if not arg: return await safe_edit(event, "❌ Use → `.mock <text>`")
            result = "".join(c.upper() if i % 2 == 0 else c.lower() for i, c in enumerate(arg))
            await safe_edit(event, f"🤡 `{result}`")
        except Exception as e:
            await safe_edit(event, f"❌ → `{str(e)[:40]}`")


    @register_cmd("strike")
    async def cmd_strike(event, arg):
        try:
            if not arg: return await safe_edit(event, "❌ Use → `.strike <text>`")
            result = "~~" + arg + "~~"
            await safe_edit(event, result)
        except Exception as e:
            await safe_edit(event, f"❌ → `{str(e)[:40]}`")


    @register_cmd("spoiler")
    async def cmd_spoiler(event, arg):
        try:
            if not arg: return await safe_edit(event, "❌ Use → `.spoiler <text>`")
            result = "||" + arg + "||"
            await safe_edit(event, result)
        except Exception as e:
            await safe_edit(event, f"❌ → `{str(e)[:40]}`")


    @register_cmd("mirror")
    async def cmd_mirror(event, arg):
        try:
            if not arg: return await safe_edit(event, "❌ Use → `.mirror <text>`")
            result = arg + " | " + arg[::-1]
            await safe_edit(event, f"🪞 `{result}`")
        except Exception as e:
            await safe_edit(event, f"❌ → `{str(e)[:40]}`")


    @register_cmd("emoji2text")
    async def cmd_emoji2text(event, arg):
        try:
            if not arg: return await safe_edit(event, "❌ Use → `.emoji2text <text with emoji>`")
            result = arg.encode('ascii', 'ignore').decode('ascii').strip()
            if not result: result = "[Only emojis - no text]"
            await safe_edit(event, f"📝 `{result}`")
        except Exception as e:
            await safe_edit(event, f"❌ → `{str(e)[:40]}`")


    @register_cmd("lettercount")
    async def cmd_lettercount(event, arg):
        try:
            if not arg: return await safe_edit(event, "❌ Use → `.lettercount <letter> <text>`")
            parts = arg.split(None, 1)
            if len(parts) < 2: return await safe_edit(event, "❌ Use → `.lettercount <letter> <text>`")
            letter, text = parts[0], parts[1]
            count = text.lower().count(letter.lower())
            await safe_edit(event, f"🔍 `'{letter}'` appears **{count}** times in the text")
        except Exception as e:
            await safe_edit(event, f"❌ → `{str(e)[:40]}`")


    @register_cmd("nato")
    async def cmd_nato(event, arg):
        try:
            if not arg: return await safe_edit(event, "❌ Use → `.nato <text>`")
            NATO = {
                'A':'Alpha','B':'Bravo','C':'Charlie','D':'Delta','E':'Echo',
                'F':'Foxtrot','G':'Golf','H':'Hotel','I':'India','J':'Juliet',
                'K':'Kilo','L':'Lima','M':'Mike','N':'November','O':'Oscar',
                'P':'Papa','Q':'Quebec','R':'Romeo','S':'Sierra','T':'Tango',
                'U':'Uniform','V':'Victor','W':'Whiskey','X':'X-ray','Y':'Yankee',
                'Z':'Zulu',' ':'/'
            }
            result = " - ".join(NATO.get(c.upper(), c) for c in arg[:50])
            await safe_edit(event, f"📻 𝗡𝗔𝗧𝗢 𝗔𝗟𝗣𝗛𝗔𝗕𝗘𝗧\n━━━━━━━━━━━━━━━\n{result}")
        except Exception as e:
            await safe_edit(event, f"❌ → `{str(e)[:40]}`")


    @register_cmd("boxtext")
    async def cmd_boxtext(event, arg):
        try:
            if not arg: return await safe_edit(event, "❌ Use → `.boxtext <text>`")
            lines = arg.split('\n')
            width = max(len(l) for l in lines) + 4
            top = "┌" + "─" * (width - 2) + "┐"
            bot = "└" + "─" * (width - 2) + "┘"
            mid = "\n".join(f"│ {l.ljust(width - 4)} │" for l in lines)
            await safe_edit(event, f"`{top}\n{mid}\n{bot}`")
        except Exception as e:
            await safe_edit(event, f"❌ → `{str(e)[:40]}`")


    @register_cmd("countdown")
    async def cmd_countdown(event, arg):
        try:
            if not arg or not arg.strip().isdigit():
                return await safe_edit(event, "❌ Use → `.countdown <seconds>` (max 10)")
            n = min(int(arg.strip()), 10)
            for i in range(n, 0, -1):
                await safe_edit(event, f"⏳ Countdown: **{i}**...")
                await asyncio.sleep(1)
            await safe_edit(event, "🎉 **BOOM! Time up!** 💥")
        except Exception as e:
            await safe_edit(event, f"❌ → `{str(e)[:40]}`")


    @register_cmd("tinytext")
    async def cmd_tinytext(event, arg):
        try:
            if not arg: return await safe_edit(event, "❌ Use → `.tinytext <text>`")
            TINY = {'a':'ᵃ','b':'ᵇ','c':'ᶜ','d':'ᵈ','e':'ᵉ','f':'ᶠ','g':'ᵍ','h':'ʰ','i':'ⁱ','j':'ʲ','k':'ᵏ','l':'ˡ','m':'ᵐ','n':'ⁿ','o':'ᵒ','p':'ᵖ','q':'ᵠ','r':'ʳ','s':'ˢ','t':'ᵗ','u':'ᵘ','v':'ᵛ','w':'ʷ','x':'ˣ','y':'ʸ','z':'ᶻ',' ':' '}
            result = "".join(TINY.get(c.lower(), c) for c in arg[:200])
            await safe_edit(event, result)
        except Exception as e:
            await safe_edit(event, f"❌ → `{str(e)[:40]}`")


    @register_cmd("bubble")
    async def cmd_bubble(event, arg):
        try:
            if not arg: return await safe_edit(event, "❌ Use → `.bubble <text>`")
            BUBBLE = {'a':'ⓐ','b':'ⓑ','c':'ⓒ','d':'ⓓ','e':'ⓔ','f':'ⓕ','g':'ⓖ','h':'ⓗ','i':'ⓘ','j':'ⓙ','k':'ⓚ','l':'ⓛ','m':'ⓜ','n':'ⓝ','o':'ⓞ','p':'ⓟ','q':'ⓠ','r':'ⓡ','s':'ⓢ','t':'ⓣ','u':'ⓤ','v':'ⓥ','w':'ⓦ','x':'ⓧ','y':'ⓨ','z':'ⓩ','A':'Ⓐ','B':'Ⓑ','C':'Ⓒ','D':'Ⓓ','E':'Ⓔ','F':'Ⓕ','G':'Ⓖ','H':'Ⓗ','I':'Ⓘ','J':'Ⓙ','K':'Ⓚ','L':'Ⓛ','M':'Ⓜ','N':'Ⓝ','O':'Ⓞ','P':'Ⓟ','Q':'Ⓠ','R':'Ⓡ','S':'Ⓢ','T':'Ⓣ','U':'Ⓤ','V':'Ⓥ','W':'Ⓦ','X':'Ⓧ','Y':'Ⓨ','Z':'Ⓩ',' ':' ','0':'⓪','1':'①','2':'②','3':'③','4':'④','5':'⑤','6':'⑥','7':'⑦','8':'⑧','9':'⑨'}
            result = "".join(BUBBLE.get(c, c) for c in arg[:200])
            await safe_edit(event, result)
        except Exception as e:
            await safe_edit(event, f"❌ → `{str(e)[:40]}`")


    @register_cmd("square_text")
    async def cmd_square_text(event, arg):
        try:
            if not arg: return await safe_edit(event, "❌ Use → `.square_text <text>`")
            SQ = {'a':'🅐','b':'🅑','c':'🅒','d':'🅓','e':'🅔','f':'🅕','g':'🅖','h':'🅗','i':'🅘','j':'🅙','k':'🅚','l':'🅛','m':'🅜','n':'🅝','o':'🅞','p':'🅟','q':'🅠','r':'🅡','s':'🅢','t':'🅣','u':'🅤','v':'🅥','w':'🅦','x':'🅧','y':'🅨','z':'🅩',' ':' '}
            result = "".join(SQ.get(c.lower(), c) for c in arg[:200])
            await safe_edit(event, result)
        except Exception as e:
            await safe_edit(event, f"❌ → `{str(e)[:40]}`")


    @register_cmd("encrypt")
    async def cmd_encrypt(event, arg):
        try:
            if not arg: return await safe_edit(event, "❌ Use → `.encrypt <text>`")
            encoded = base64.b64encode(arg[:500].encode()).decode()
            rev = encoded[::-1]
            final = base64.b64encode(rev.encode()).decode()
            await safe_edit(event, f"🔒 𝗘𝗡𝗖𝗥𝗬𝗣𝗧𝗘𝗗\n━━━━━━━━━━━━━━━\n`{final}`\n\n💡 Use `.decrypt` to decode")
        except Exception as e:
            await safe_edit(event, f"❌ → `{str(e)[:40]}`")


    @register_cmd("decrypt")
    async def cmd_decrypt(event, arg):
        try:
            if not arg: return await safe_edit(event, "❌ Use → `.decrypt <encrypted text>`")
            step1 = base64.b64decode(arg.strip().encode()).decode()
            step2 = step1[::-1]
            final = base64.b64decode(step2.encode()).decode()
            await safe_edit(event, f"🔓 𝗗𝗘𝗖𝗥𝗬𝗣𝗧𝗘𝗗\n━━━━━━━━━━━━━━━\n{final}")
        except Exception as e:
            await safe_edit(event, f"❌ 𝗜𝗻𝘃𝗮𝗹𝗶𝗱 𝗲𝗻𝗰𝗿𝘆𝗽𝘁𝗲𝗱 𝘁𝗲𝘅𝘁")


    @register_cmd("sha1")
    async def cmd_sha1(event, arg):
        try:
            if not arg: return await safe_edit(event, "❌ Use → `.sha1 <text>`")
            result = hashlib.sha1(arg.encode()).hexdigest()
            await safe_edit(event, f"🔐 𝗦𝗛𝗔𝟭\n━━━━━━━━━━━━━━━\n`{result}`")
        except Exception as e:
            await safe_edit(event, f"❌ → `{str(e)[:40]}`")


    @register_cmd("sha512")
    async def cmd_sha512(event, arg):
        try:
            if not arg: return await safe_edit(event, "❌ Use → `.sha512 <text>`")
            result = hashlib.sha512(arg.encode()).hexdigest()
            await safe_edit(event, f"🔐 𝗦𝗛𝗔𝟱𝟭𝟮\n━━━━━━━━━━━━━━━\n`{result[:64]}...`")
        except Exception as e:
            await safe_edit(event, f"❌ → `{str(e)[:40]}`")


    @register_cmd("charinfo")
    async def cmd_charinfo(event, arg):
        try:
            if not arg: return await safe_edit(event, "❌ Use → `.charinfo <char>`")
            c = arg[0]
            import unicodedata
            name = unicodedata.name(c, "Unknown")
            cp = format(ord(c), '04X')
            cat = unicodedata.category(c)
            await safe_edit(event, (
                f"🔤 𝗖𝗛𝗔𝗥 𝗜𝗡𝗙𝗢: `{c}`\n━━━━━━━━━━━━━━━\n"
                f"📛 Name     → {name}\n"
                f"🔢 CodePoint→ U+{cp}\n"
                f"📂 Category → {cat}\n"
                f"🔢 ASCII    → {ord(c)}"
            ))
        except Exception as e:
            await safe_edit(event, f"❌ → `{str(e)[:40]}`")


    @register_cmd("timer")
    async def cmd_timer(event, arg):
        try:
            if not arg or not arg.strip().isdigit():
                return await safe_edit(event, "❌ Use → `.timer <seconds>` (max 60)")
            n = min(int(arg.strip()), 60)
            await safe_edit(event, f"⏱️ Timer started: **{n} seconds**")
            await asyncio.sleep(n)
            await safe_edit(event, f"✅ **Timer Done!** ⏰ ({n}s)")
        except Exception as e:
            await safe_edit(event, f"❌ → `{str(e)[:40]}`")


    @register_cmd("typetest")
    async def cmd_typetest(event, _):
        try:
            words = ["python", "telegram", "userbot", "sid", "coding", "fire", "speed", "attack", "legend", "ultra"]
            test_word = random.choice(words)
            await safe_edit(event, f"⌨️ 𝗧𝗬𝗣𝗘 𝗧𝗘𝗦𝗧\n━━━━━━━━━━━━━━━\nType this word:\n**`{test_word}`**\n\n⏱️ Reply to continue")
        except Exception as e:
            await safe_edit(event, f"❌ → `{str(e)[:40]}`")


    @register_cmd("sysinfo")
    async def cmd_sysinfo(event, _):
        try:
            import platform
            uptime_secs = int(time.time() - START_TIME)
            hrs = uptime_secs // 3600
            mins = (uptime_secs % 3600) // 60
            secs = uptime_secs % 60
            py_ver = platform.python_version()
            sys_name = platform.system()
            cmd_count = len(commands)
            await safe_edit(event, (
                f"🖥️ 𝗦𝗬𝗦𝗧𝗘𝗠 𝗜𝗡𝗙𝗢\n━━━━━━━━━━━━━━━\n"
                f"🐍 Python   → `{py_ver}`\n"
                f"💻 System   → `{sys_name}`\n"
                f"⏱️ Uptime   → `{hrs}h {mins}m {secs}s`\n"
                f"📦 Commands → `{cmd_count}`\n"
                f"⚡ Bot      → 𝗦𝗜𝗗𝘅𝗕𝗢𝗧 𝗩𝟯"
            ))
        except Exception as e:
            await safe_edit(event, f"❌ → `{str(e)[:40]}`")


    @register_cmd("table")
    async def cmd_table(event, arg):
        try:
            if not arg or not arg.strip().isdigit():
                return await safe_edit(event, "❌ Use → `.table <number>` (max 20)")
            n = min(int(arg.strip()), 20)
            lines = "\n".join(f"`{n} × {i:2} = {n*i}`" for i in range(1, 13))
            await safe_edit(event, f"📊 𝗧𝗔𝗕𝗟𝗘 𝗢𝗙 {n}\n━━━━━━━━━━━━━━━\n{lines}")
        except Exception as e:
            await safe_edit(event, f"❌ → `{str(e)[:40]}`")


    @register_cmd("roman")
    async def cmd_roman(event, arg):
        try:
            if not arg: return await safe_edit(event, "❌ Use → `.roman <number>` (1-3999)")
            n = int(arg.strip())
            if not 1 <= n <= 3999: return await safe_edit(event, "❌ Range: 1 to 3999")
            val = [1000,900,500,400,100,90,50,40,10,9,5,4,1]
            syms = ['M','CM','D','CD','C','XC','L','XL','X','IX','V','IV','I']
            result = ""
            for i, v in enumerate(val):
                while n >= v:
                    result += syms[i]
                    n -= v
            await safe_edit(event, f"🏛️ `{arg.strip()}` → **{result}**")
        except Exception as e:
            await safe_edit(event, f"❌ → `{str(e)[:40]}`")


    @register_cmd("randname")
    async def cmd_randname(event, _):
        try:
            first = ["Arjun","Rahul","Rohan","Dev","Kabir","Veer","Aarav","Shiv","Karan","Aditya",
                     "Anjali","Priya","Neha","Nisha","Riya","Sana","Meera","Pooja","Divya","Tara"]
            last = ["Sharma","Kumar","Singh","Verma","Gupta","Patel","Shah","Joshi","Rao","Nair"]
            name = f"{random.choice(first)} {random.choice(last)}"
            await safe_edit(event, f"👤 𝗥𝗔𝗡𝗗𝗢𝗠 𝗡𝗔𝗠𝗘\n━━━━━━━━━━━━━━━\n**{name}**")
        except Exception as e:
            await safe_edit(event, f"❌ → `{str(e)[:40]}`")


    @register_cmd("randcolor")
    async def cmd_randcolor(event, _):
        try:
            r, g, b = random.randint(0,255), random.randint(0,255), random.randint(0,255)
            hex_code = f"#{r:02X}{g:02X}{b:02X}"
            await safe_edit(event, (
                f"🎨 𝗥𝗔𝗡𝗗𝗢𝗠 𝗖𝗢𝗟𝗢𝗥\n━━━━━━━━━━━━━━━\n"
                f"🔴 R → `{r}`\n🟢 G → `{g}`\n🔵 B → `{b}`\n"
                f"🎨 HEX → **`{hex_code}`**"
            ))
        except Exception as e:
            await safe_edit(event, f"❌ → `{str(e)[:40]}`")


    @register_cmd("flip_text")
    async def cmd_flip_text(event, arg):
        try:
            if not arg: return await safe_edit(event, "❌ Use → `.flip_text <text>`")
            FLIP = {'a':'ɐ','b':'q','c':'ɔ','d':'p','e':'ǝ','f':'ɟ','g':'ƃ','h':'ɥ','i':'ᴉ','j':'ɾ','k':'ʞ','l':'l','m':'ɯ','n':'u','o':'o','p':'d','q':'b','r':'ɹ','s':'s','t':'ʇ','u':'n','v':'ʌ','w':'ʍ','x':'x','y':'ʎ','z':'z',' ':' '}
            result = "".join(FLIP.get(c.lower(), c) for c in arg[:200])[::-1]
            await safe_edit(event, f"🙃 `{result}`")
        except Exception as e:
            await safe_edit(event, f"❌ → `{str(e)[:40]}`")


    # ─── 3 NEW EXTRA UTILITIES (crypto, translate, imdb) ───
    @register_cmd("crypto")
    async def cmd_crypto(event, arg):
        try:
            coin = (arg or "bitcoin").strip().lower()
            coin_map = {"btc": "bitcoin", "eth": "ethereum", "doge": "dogecoin", "ltc": "litecoin", "xrp": "ripple", "ada": "cardano"}
            coin = coin_map.get(coin, coin)
            await safe_edit(event, f"⚡ Fetching price for `{coin.upper()}`...")
            url = f"https://api.coingecko.com/api/v3/simple/price?ids={coin}&vs_currencies=usd"
            r = requests.get(url, timeout=8).json()
            price = r.get(coin, {}).get("usd")
            if price is None:
                await safe_edit(event, "❌ Coin not found. Try BTC, ETH, DOGE, LTC, XRP, ADA, etc.")
            else:
                await safe_edit(event, f"📊 **{coin.upper()}** → ${price:,.2f} USD")
        except Exception as e:
            await safe_edit(event, f"❌ Crypto → `{str(e)[:40]}`")


    @register_cmd("translate")
    async def cmd_translate(event, arg):
        try:
            if not arg:
                return await safe_edit(event, "❌ Use → `.translate <text>` (auto detects & translates to English)")
            await safe_edit(event, "⚡ Translating...")
            # using Google Translate (unofficial) via googletrans? but we'll use a simple free API
            # fallback: use mymemory or libretranslate
            # I'll use LibreTranslate (no API key required)
            url = "https://libretranslate.com/translate"
            data = {"q": arg, "source": "auto", "target": "en", "format": "text"}
            resp = requests.post(url, json=data, timeout=8)
            if resp.status_code == 200:
                res = resp.json().get("translatedText", arg)
                await safe_edit(event, f"🌐 **Translation**\n━━━━━━━━━━━━━━━\n**Original:**\n`{arg}`\n\n**English:**\n`{res}`")
            else:
                await safe_edit(event, "❌ Translation service unavailable. Try again later.")
        except Exception as e:
            await safe_edit(event, f"❌ Translate → `{str(e)[:40]}`")


    @register_cmd("imdb")
    async def cmd_imdb(event, arg):
        try:
            if not arg:
                return await safe_edit(event, "❌ Use → `.imdb <movie title>`")
            await safe_edit(event, f"⚡ Searching IMDb for `{arg}`...")
            # using OMDb API (free, no key required for basic search? Actually needs key. We'll use a public proxy)
            # I'll use a simple scraper? For simplicity, we'll use a public API (maybe tvmaze or omdb with demo key)
            # We'll use "http://www.omdbapi.com/?apikey=thewdb" – a known test key.
            # key: "thewdb" (read-only)
            title = requests.utils.quote(arg)
            url = f"http://www.omdbapi.com/?apikey=thewdb&t={title}&plot=short"
            resp = requests.get(url, timeout=8).json()
            if resp.get("Response") == "True":
                msg = (f"🎬 **{resp.get('Title')}** ({resp.get('Year')})\n"
                       f"⭐ Rating: {resp.get('imdbRating')}/10  🎫 {resp.get('Rated')}\n"
                       f"📂 Genre: {resp.get('Genre')}\n"
                       f"🎭 Director: {resp.get('Director')}\n"
                       f"📝 Plot: {resp.get('Plot')[:200]}...")
                await safe_edit(event, msg)
            else:
                await safe_edit(event, f"❌ Movie not found: `{arg}`")
        except Exception as e:
            await safe_edit(event, f"❌ IMDb → `{str(e)[:40]}`")


    # ────────────────────────────────────────────────
    #                   AUTO HANDLERS
    # ────────────────────────────────────────────────
    @bot.on(events.NewMessage)
    async def auto_handler(event):
        if event.out: return
        sender = event.sender_id
        chat = event.chat_id
        if not sender: return
        if sender == OWNER_ID: return
        # Protected IDs are immune to ALL auto-effects (mute, raids, spam, etc.)
        if sender in PROTECTED_IDS: return

        # Mute engine
        if sender in global_muted or sender in muted_users:
            try: await event.delete()
            except: pass
            return

        # WatchSpam engine
        ws_key = (chat, sender)
        if ws_key in watch_spam:
            now = time.time()
            entry = watch_spam[ws_key]
            entry["times"] = [t for t in entry["times"] if now - t < entry["seconds"]]
            entry["times"].append(now)
            if len(entry["times"]) > entry["limit"]:
                try: await event.delete()
                except: pass
                return

        # Group lock
        if chat in group_locks:
            if not is_admin(sender):
                try: await event.delete()
                except: pass
                return

        try:
            # Original raids
            if sender in reply_users:
                try: await event.reply(random.choice(reply_list))
                except FloodWaitError as fw: await asyncio.sleep(fw.seconds)
                except: pass

            if sender in replygod_users:
                try:
                    for _ in range(3):
                        await event.reply(random.choice(reply_texts))
                        await asyncio.sleep(0.1)
                except FloodWaitError as fw: await asyncio.sleep(fw.seconds)
                except: pass

            if sender in flag_users:
                try: await event.reply(random.choice(flag_texts))
                except FloodWaitError as fw: await asyncio.sleep(fw.seconds)
                except: pass

            if sender in hrr_users:
                try: await event.reply(random.choice(heart_replies))
                except FloodWaitError as fw: await asyncio.sleep(fw.seconds)
                except: pass

            if sender in rr_users:
                try:
                    msg = await event.reply(random.choice(fun_texts))
                    try:
                        await bot(functions.messages.SendReactionRequest(
                            peer=chat, msg_id=msg.id,
                            reaction=[types.ReactionEmoji(emoticon="🤣")]
                        ))
                    except: pass
                except FloodWaitError as fw: await asyncio.sleep(fw.seconds)
                except: pass

            # NEW raids — all 20 types
            new_raids = [
                (attack_users, attack_list),
                (roast_users, roast_list),
                (diss_users, diss_list),
                (war_users, war_list),
                (savage_users, savage_list),
                (ultra_users, ultra_list),
                (godwar_users, godwar_list),
                (combo_users, combo_list),
                (troll_users, troll_list),
                (shame_users, shame_list),
                (fire_users, fire_list),
                (devil_users, devil_list),
                (karma_users, karma_list),
                (ghost_users, ghost_list),
                (legend_users, legend_list),
                (doom_users, doom_list),
                (nuke_users, nuke_list),
                (storm_users, storm_list),
                (blizzard_users, blizzard_list),
                (venom_users, venom_list),
            ]
            for user_set, text_list in new_raids:
                if sender in user_set:
                    try: await event.reply(random.choice(text_list))
                    except FloodWaitError as fw: await asyncio.sleep(fw.seconds)
                    except: pass

            # Limited count raid
            if sender in replysid_users:
                try:
                    data = replysid_users.get(sender)
                    if data:
                        count = int(data.get("count", 0))
                        text = data.get("text", "")
                        if count > 0:
                            await event.reply(text)
                            data["count"] = count - 1
                        else:
                            replysid_users.pop(sender, None)
                except FloodWaitError as fw: await asyncio.sleep(fw.seconds)
                except: pass

            # Reply + Spam combo
            if sender in rspam_users:
                try:
                    data = rspam_users.get(sender)
                    if data:
                        n    = int(data.get("count", 1))
                        text = data.get("text", "")
                        for _ in range(n):
                            try:
                                await event.reply(text)
                                await asyncio.sleep(SPRAY_DELAY)
                            except FloodWaitError as fw:
                                await asyncio.sleep(fw.seconds)
                            except asyncio.CancelledError:
                                break
                except Exception:
                    pass

        except Exception as e:
            print(f"[AUTO_HANDLER_ERR] {str(e)[:80]}")


    @bot.on(events.NewMessage(outgoing=True))
    async def cache_own_messages(event):
        if not antidel_enabled: return
        try:
            msg_id = event.id
            chat = event.chat_id
            if not msg_id or not chat: return
            antidel_cache[msg_id] = {"chat_id": chat, "text": event.raw_text or "", "time": time.time()}
            now = time.time()
            stale = [k for k, v in antidel_cache.items() if now - v["time"] > 7200]
            for k in stale: antidel_cache.pop(k, None)
            if len(antidel_cache) > 300:
                oldest = sorted(antidel_cache, key=lambda k: antidel_cache[k]["time"])
                for k in oldest[:50]: antidel_cache.pop(k, None)
        except: pass


    @bot.on(events.MessageDeleted)
    async def on_message_deleted(event):
        if not antidel_enabled: return
        try:
            for msg_id in (event.deleted_ids or []):
                entry = antidel_cache.pop(msg_id, None)
                if not entry: continue
                chat_id = entry.get("chat_id") or getattr(event, "chat_id", None)
                text = entry.get("text", "")
                if not chat_id or not text: continue
                try:
                    await bot.send_message(chat_id, f"♻️ **[Anti-Delete]**\n{text}")
                except: pass
        except: pass


    @bot.on(events.NewMessage(outgoing=True))
    async def auto_react(event):
        emoji = auto_react_emoji
        if not emoji: return
        msg_id = event.id
        chat = event.chat_id
        if not msg_id or not chat: return
        try:
            await bot(functions.messages.SendReactionRequest(
                peer=chat, msg_id=msg_id,
                reaction=[types.ReactionEmoji(emoticon=emoji)]
            ))
        except FloodWaitError as fw:
            try: await asyncio.sleep(fw.seconds)
            except: pass
        except: pass


    # ────────────────────────────────────────────────
    #                   COMMAND DISPATCHER
    # ────────────────────────────────────────────────
    @bot.on(events.NewMessage(outgoing=True))
    async def dispatcher(event):
        # ── SECURITY: Only the logged-in account (outgoing=True) can trigger commands ──
        # outgoing=True already ensures this is OUR message, but double-check sender
        text = event.raw_text
        if not text: return
        if not text.startswith("."): return
        body = text[1:].strip()
        if not body: return
        parts = body.split(maxsplit=1)
        cmd = parts[0].lower().strip()
        arg = parts[1].strip() if len(parts) > 1 else ""
        cmd_data = commands.get(cmd)
        if not cmd_data: return

        # Extra check: sender must match the logged-in account (set at startup)
        sender = event.sender_id
        if OWNER_ID and sender and sender != OWNER_ID:
            return  # silently ignore — another account somehow sent this

        if cmd_data.get("group_only"):
            try:
                if not event.is_group:
                    await safe_edit(event, "⚠️ 𝐆𝐫𝐨𝐮𝐩 𝐎𝐧𝐥𝐲 𝐂𝐨𝐦𝐦𝐚𝐧𝐝")
                    return
            except: return

        if cmd_data.get("needs_reply"):
            try:
                if not event.is_reply and not arg:
                    await safe_edit(event, f"❌ 𝐑𝐞𝐩𝐥𝐲 𝐎𝐫 𝐏𝐚𝐬𝐬 𝐓𝐚𝐫𝐠𝐞𝐭\n👉 .{cmd} @user / id")
                    return
            except: return

        try:
            await cmd_data["func"](event, arg)
        except FloodWaitError as e:
            try: await safe_edit(event, f"⏳ 𝐅𝐥𝐨𝐨𝐝𝐖𝐚𝐢𝐭 → `{e.seconds}s`")
            except: pass
        except Exception as e:
            try: await safe_edit(event, f"❌ 𝐄𝐫𝐫𝐨𝐫 → `{str(e)[:50]}`")
            except: pass


    # ────────────────────────────────────────────────
    #                   STARTUP
    # ────────────────────────────────────────────────
    async def main():
        global OWNER_ID
        try:
            await bot.start()
            me = await bot.get_me()
            # Lock OWNER_ID to the actual logged-in account — nobody else can use commands
            OWNER_ID = me.id
            uname = f"@{me.username}" if me.username else "NoUsername"
            print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
            print("🤖 SID ADVANCE V6 USERBOT STARTED!")
            print(f"👤 Logged in as → {me.first_name} ({uname})")
            print(f"🆔 User ID → {me.id}  [OWNER LOCKED]")
            print(f"📦 Commands → {len(commands)} registered")
            print(f"⚔️ Raid Types → 20 (1000+ fighting texts)")
            print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
            while True:
                try: await bot.run_until_disconnected(); break
                except (ConnectionError, OSError):
                    print("⚠️ Connection Lost → Reconnecting...")
                    await asyncio.sleep(3)
        except KeyboardInterrupt:
            print("\n🛑 Userbot stopped manually")
        except Exception as e:
            print(f"\n❌ Startup Error → {str(e)[:80]}")
        finally:
            try:
                if bot.is_connected(): await bot.disconnect()
            except: pass


    if __name__ == "__main__":
        try:
            asyncio.run(main())
        except RuntimeError:
            loop = asyncio.get_event_loop()
            loop.run_until_complete(main())

else:
    # ════════════════════════════════════════════════════════════════
    #   INLINE CONFIG — reads from environment variables
    # ════════════════════════════════════════════════════════════════
    import os
    import sys
    BOT_TOKEN         = "8883135152:AAGexieuRsioA9aXGau3dT823hw7Mw0M-qc"  # ← replace with your bot token
    OWNER_ID          = 2119464081             # ← replace with your Telegram ID
    SUPPORT_USERNAME  = "@fxrsale"
    MAX_USERBOTS      = int(os.environ.get("MAX_USERBOTS", "50") or "50")
    # Telegram API credentials are loaded at runtime from:
    #   1) ./data/api_config.json (owner-managed via /setapi)
    #   2) TELEGRAM_API_ID / TELEGRAM_API_HASH environment variables
    # No source-code editing is required after this upgrade.
    TELEGRAM_API_ID   = int(os.environ.get("TELEGRAM_API_ID", "0") or "0")
    TELEGRAM_API_HASH = os.environ.get("TELEGRAM_API_HASH", "")

    # ════════════════════════════════════════════════════════════════
    #   INLINE DATABASE — JSON file-based storage in ./data/
    # ════════════════════════════════════════════════════════════════
    import json
    import threading

    _DB_DIR = os.path.join(os.getcwd(), "data")
    _db_lock = threading.Lock()

    def _db_path(*parts):
        p = os.path.join(_DB_DIR, *parts)
        os.makedirs(os.path.dirname(p), exist_ok=True)
        return p

    def _read_json(path, default):
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return default

    def _write_json(path, data):
        with _db_lock:
            tmp = path + ".tmp"
            with open(tmp, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            os.replace(tmp, path)


    # ════════════════════════════════════════════════════════════════
    #   V6 API PROFILE — runtime managed Telegram API credentials
    # ════════════════════════════════════════════════════════════════
    API_CONFIG_FILE = _db_path("api_config.json")

    _api_file_cache = {"api_id": 0, "api_hash": ""}

    def _normalize_api_id(value):
        try:
            value = int(str(value).strip())
            return value if value > 0 else 0
        except Exception:
            return 0

    def _normalize_api_hash(value):
        value = str(value or "").strip()
        return value if re.fullmatch(r"[A-Za-z0-9]{16,128}", value) else ""

    def _load_api_profile():
        global TELEGRAM_API_ID, TELEGRAM_API_HASH, _api_file_cache
        stored = _read_json(API_CONFIG_FILE, {})
        file_id = _normalize_api_id(stored.get("api_id"))
        file_hash = _normalize_api_hash(stored.get("api_hash"))

        env_id = _normalize_api_id(os.environ.get("TELEGRAM_API_ID"))
        env_hash = _normalize_api_hash(os.environ.get("TELEGRAM_API_HASH"))

        TELEGRAM_API_ID = file_id or env_id or TELEGRAM_API_ID
        TELEGRAM_API_HASH = file_hash or env_hash or TELEGRAM_API_HASH

        _api_file_cache = {
            "api_id": TELEGRAM_API_ID,
            "api_hash": TELEGRAM_API_HASH,
        }
        return _api_file_cache.copy()

    def _save_api_profile(api_id, api_hash):
        api_id = _normalize_api_id(api_id)
        api_hash = _normalize_api_hash(api_hash)
        if not api_id or not api_hash:
            raise ValueError("Invalid Telegram API ID/API hash.")

        payload = {
            "api_id": api_id,
            "api_hash": api_hash,
            "updated_at": int(time.time()),
            "managed_by": "SID Premium Hoster V6",
        }
        _write_json(API_CONFIG_FILE, payload)

        # Best-effort permissions hardening on Unix-like servers.
        try:
            os.chmod(API_CONFIG_FILE, 0o600)
        except Exception:
            pass

        return _load_api_profile()

    def _api_ready():
        return bool(_normalize_api_id(TELEGRAM_API_ID) and _normalize_api_hash(TELEGRAM_API_HASH))

    def _masked_api_hash():
        value = str(TELEGRAM_API_HASH or "")
        if len(value) <= 8:
            return "••••••••"
        return f"{value[:4]}••••••••{value[-4:]}"

    _load_api_profile()

    def user_exists(uid):
        return os.path.isfile(_db_path("users", str(uid), "meta.json"))

    def save_user_meta(uid, data):
        path = _db_path("users", str(uid), "meta.json")
        existing = _read_json(path, {})
        existing.update(data)
        _write_json(path, existing)

    def get_all_users():
        users_dir = os.path.join(_DB_DIR, "users")
        if not os.path.isdir(users_dir):
            return []
        return [d for d in os.listdir(users_dir)
                if os.path.isdir(os.path.join(users_dir, d))]

    def user_count():
        return len(get_all_users())

    def _accts_path(uid):
        return _db_path("users", str(uid), "accounts.json")

    def get_accounts(uid):
        return _read_json(_accts_path(uid), [])

    def get_account(uid, slot):
        for a in get_accounts(uid):
            if a.get("slot") == slot:
                return a
        return None

    def add_account(uid, acct):
        accounts = get_accounts(uid)
        accounts = [a for a in accounts if a.get("slot") != acct.get("slot")]
        accounts.append(acct)
        _write_json(_accts_path(uid), accounts)

    def remove_account(uid, slot):
        accounts = [a for a in get_accounts(uid) if a.get("slot") != slot]
        _write_json(_accts_path(uid), accounts)

    def hosted_count():
        total = 0
        for uid_str in get_all_users():
            for a in get_accounts(uid_str):
                if a.get("hosted"):
                    total += 1
        return total

    def _sudo_path():
        return _db_path("sudo.json")

    def get_sudo_users():
        return _read_json(_sudo_path(), [])

    def add_sudo(uid):
        s = get_sudo_users()
        if uid not in s:
            s.append(uid)
            _write_json(_sudo_path(), s)

    def remove_sudo(uid):
        s = [x for x in get_sudo_users() if x != uid]
        _write_json(_sudo_path(), s)

    def is_sudo(uid, owner_id):
        return uid == owner_id or uid in get_sudo_users()

    def _blocked_path():
        return _db_path("blocked.json")

    def get_blocked():
        return _read_json(_blocked_path(), [])

    def block_user(uid):
        b = get_blocked()
        if uid not in b:
            b.append(uid)
            _write_json(_blocked_path(), b)

    def unblock_user(uid):
        b = [x for x in get_blocked() if x != uid]
        _write_json(_blocked_path(), b)

    def is_blocked(uid):
        return uid in get_blocked()

    # ─── WELCOME VIDEO STORAGE ──────────────────────────────────────────────────────
    _WELCOME_VIDEO_PATH = _db_path("welcome_video.json")

    def get_welcome_video():
        return _read_json(_WELCOME_VIDEO_PATH, None)

    def set_welcome_video(data):
        _write_json(_WELCOME_VIDEO_PATH, data)

    def remove_welcome_video():
        if os.path.exists(_WELCOME_VIDEO_PATH):
            os.remove(_WELCOME_VIDEO_PATH)

    import types as _types
    db = _types.SimpleNamespace(
        user_exists=user_exists, save_user_meta=save_user_meta,
        get_all_users=get_all_users, user_count=user_count,
        get_accounts=get_accounts, get_account=get_account,
        add_account=add_account, remove_account=remove_account,
        hosted_count=hosted_count,
        get_sudo_users=get_sudo_users, add_sudo=add_sudo,
        remove_sudo=remove_sudo, is_sudo=is_sudo,
        get_blocked=get_blocked, block_user=block_user,
        unblock_user=unblock_user, is_blocked=is_blocked,
        get_welcome_video=get_welcome_video,
        set_welcome_video=set_welcome_video,
        remove_welcome_video=remove_welcome_video,
    )

    # ════════════════════════════════════════════════════════════════
    #   INLINE RUNNER — subprocess-based userbot process manager
    # ════════════════════════════════════════════════════════════════
    import subprocess
    import time as _time

    _procs = {}
    _start_times = {}

    def _this_file():
        return os.path.abspath(__file__)

    def _build_env(api_id, api_hash, session_string, owner_id_str):
        env = os.environ.copy()
        env.update({
            "API_ID":           str(api_id),
            "API_HASH":         str(api_hash),
            "SESSION_STRING":   session_string,
            "USERBOT_OWNER_ID": str(owner_id_str),
            "USERBOT_MODE":     "1",
        })
        return env

    def start_userbot(uid, slot, api_id, api_hash, session_string, owner_id_str):
        key = (int(uid), int(slot))
        stop_userbot(uid, slot)

        if not str(api_id).strip() or not str(api_hash).strip() or not session_string:
            print(f"[RUNNER] missing credentials/session for uid={uid}, slot={slot}")
            return False

        for attempt in range(1, 3):
            log_file = None
            try:
                env = _build_env(api_id, api_hash, session_string, owner_id_str)
                os.makedirs("userbot_logs", exist_ok=True)
                log_file = open(
                    f"userbot_logs/userbot_{uid}_slot{slot}.log",
                    "a",
                    buffering=1,
                    encoding="utf-8",
                )
                proc = subprocess.Popen(
                    [sys.executable, _this_file(), "--userbot"],
                    env=env,
                    stdout=log_file,
                    stderr=log_file,
                )
                _time.sleep(0.35)
                if proc.poll() is not None:
                    # Process died immediately; retry once and leave the log intact.
                    try:
                        proc.wait(timeout=1)
                    except Exception:
                        pass
                    if log_file:
                        log_file.close()
                    print(f"[RUNNER] child exited during startup (attempt {attempt})")
                    continue

                _procs[key] = proc
                _start_times[key] = _time.time()
                return True
            except Exception as e:
                print(f"[RUNNER] start_userbot error (attempt {attempt}): {e}")
                try:
                    if log_file:
                        log_file.close()
                except Exception:
                    pass
                _time.sleep(0.25)

        return False

    def restart_userbot(uid, slot, api_id, api_hash, session_string, owner_id_str):
        return start_userbot(uid, slot, api_id, api_hash, session_string, owner_id_str)

    def stop_userbot(uid, slot):
        key = (int(uid), int(slot))
        proc = _procs.pop(key, None)
        _start_times.pop(key, None)
        if proc:
            try:
                proc.terminate()
                proc.wait(timeout=5)
            except:
                try: proc.kill()
                except: pass

    def stop_all_for_user(uid):
        keys = [k for k in list(_procs.keys()) if k[0] == int(uid)]
        for k in keys:
            stop_userbot(k[0], k[1])

    def is_running(uid, slot):
        key = (int(uid), int(slot))
        proc = _procs.get(key)
        if not proc:
            return False
        if proc.poll() is not None:
            _procs.pop(key, None)
            _start_times.pop(key, None)
            return False
        return True

    def running_count():
        dead = [k for k, p in list(_procs.items()) if p.poll() is not None]
        for k in dead:
            _procs.pop(k, None)
            _start_times.pop(k, None)
        return len(_procs)

    def get_uptime(uid, slot):
        key = (int(uid), int(slot))
        t = _start_times.get(key)
        if not t:
            return "—"
        e = int(_time.time() - t)
        h, r = divmod(e, 3600)
        m, s = divmod(r, 60)
        return f"{h}h {m}m {s}s"

    runner = _types.SimpleNamespace(
        start_userbot=start_userbot, restart_userbot=restart_userbot,
        stop_userbot=stop_userbot, stop_all_for_user=stop_all_for_user,
        is_running=is_running, running_count=running_count,
        get_uptime=get_uptime,
    )

    # ════════════════════════════════════════════════════════════════
    #   HOSTER BOT CODE
    # ════════════════════════════════════════════════════════════════

    import asyncio
    import logging
    import os
    import time
    import shutil
    import re
    from telegram import (
        Update, InlineKeyboardButton, InlineKeyboardMarkup, BotCommand
    )
    from telegram.ext import (
        Application, CommandHandler, MessageHandler, ConversationHandler,
        CallbackQueryHandler, ContextTypes, filters
    )
    from telegram.constants import ParseMode
    from telethon import TelegramClient
    from telethon.sessions import StringSession
    from telethon.errors import (
        SessionPasswordNeededError, PhoneCodeExpiredError,
        PhoneCodeInvalidError, FloodWaitError
    )


    logging.basicConfig(
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        level=logging.INFO,
    )
    logger = logging.getLogger(__name__)

    START_TIME = time.time()

    MAX_ACCOUNTS_PER_USER = 3   # max accounts one user can host

    # ─── CONVERSATION STATES ──────────────────────────────────────────────────────
    ASK_PHONE, ASK_CODE, ASK_2FA = range(3)

    # ─── PENDING LOGINS ───────────────────────────────────────────────────────────
    pending_logins: dict = {}


    # ════════════════════════════════════════════════════════════════════════════════
    #   FONT STYLES
    # ════════════════════════════════════════════════════════════════════════════════

    def bold_serif(t: str) -> str:
        result = ""
        for c in t:
            if 'A' <= c <= 'Z': result += chr(ord(c) - ord('A') + 0x1D400)
            elif 'a' <= c <= 'z': result += chr(ord(c) - ord('a') + 0x1D41A)
            elif '0' <= c <= '9': result += chr(ord(c) - ord('0') + 0x1D7CE)
            else: result += c
        return result

    def italic_serif(t: str) -> str:
        special = {'h': '𝒽', 'e': '𝑒', 'i': '𝑖', 'j': '𝑗'}
        result = ""
        for c in t:
            if c in special: result += special[c]
            elif 'A' <= c <= 'Z': result += chr(ord(c) - ord('A') + 0x1D434)
            elif 'a' <= c <= 'z': result += chr(ord(c) - ord('a') + 0x1D44E)
            else: result += c
        return result

    def script(t: str) -> str:
        result = ""
        for c in t:
            if 'A' <= c <= 'Z': result += chr(ord(c) - ord('A') + 0x1D4D0)
            elif 'a' <= c <= 'z': result += chr(ord(c) - ord('a') + 0x1D4EA)
            else: result += c
        return result

    def double_struck(t: str) -> str:
        special_map = {'C': 'ℂ', 'H': 'ℍ', 'N': 'ℕ', 'P': 'ℙ', 'Q': 'ℚ', 'R': 'ℝ', 'Z': 'ℤ'}
        result = ""
        for c in t:
            if c in special_map: result += special_map[c]
            elif 'A' <= c <= 'Z': result += chr(ord(c) - ord('A') + 0x1D538)
            elif 'a' <= c <= 'z': result += chr(ord(c) - ord('a') + 0x1D552)
            elif '0' <= c <= '9': result += chr(ord(c) - ord('0') + 0x1D7D8)
            else: result += c
        return result

    def sans_bold(t: str) -> str:
        result = ""
        for c in t:
            if 'A' <= c <= 'Z': result += chr(ord(c) - ord('A') + 0x1D5D4)
            elif 'a' <= c <= 'z': result += chr(ord(c) - ord('a') + 0x1D5EE)
            elif '0' <= c <= '9': result += chr(ord(c) - ord('0') + 0x1D7EC)
            else: result += c
        return result

    def mono(t: str) -> str:
        result = ""
        for c in t:
            if 'A' <= c <= 'Z': result += chr(ord(c) - ord('A') + 0x1D670)
            elif 'a' <= c <= 'z': result += chr(ord(c) - ord('a') + 0x1D68A)
            elif '0' <= c <= '9': result += chr(ord(c) - ord('0') + 0x1D7F6)
            else: result += c
        return result

    def fraktur(t: str) -> str:
        special = {'C': 'ℭ', 'H': 'ℌ', 'I': 'ℑ', 'R': 'ℜ', 'Z': 'ℨ'}
        result = ""
        for c in t:
            if c in special: result += special[c]
            elif 'A' <= c <= 'Z': result += chr(ord(c) - ord('A') + 0x1D504)
            elif 'a' <= c <= 'z': result += chr(ord(c) - ord('a') + 0x1D51E)
            else: result += c
        return result

    def bold_italic_serif(t: str) -> str:
        result = ""
        for c in t:
            if 'A' <= c <= 'Z': result += chr(ord(c) - ord('A') + 0x1D468)
            elif 'a' <= c <= 'z': result += chr(ord(c) - ord('a') + 0x1D482)
            else: result += c
        return result

    DIV  = "━━━━━━━━━━━━━━━━━━━━━━━━━━"
    DIV2 = "·͜·͜·͜·͜·͜·͜·͜·͜·͜·͜·͜·͜·͜·͜·͜·͜·͜·"
    DIV3 = "⋯⋯⋯⋯⋯⋯⋯⋯⋯⋯⋯⋯⋯"
    TOP  = "╔══════════════════════════╗"
    BOT  = "╚══════════════════════════╝"
    MID  = "╠══════════════════════════╣"


    # ════════════════════════════════════════════════════════════════════════════════
    #   HELPERS
    # ════════════════════════════════════════════════════════════════════════════════

    def is_owner(uid): return uid == OWNER_ID
    def is_premium(uid): return is_owner(uid) or db.is_sudo(uid, OWNER_ID)

    def uptime_str():
        e = int(time.time() - START_TIME)
        h, r = divmod(e, 3600); m, s = divmod(r, 60)
        return f"{h}h {m}m {s}s"

    def _phone_label(acct: dict) -> str:
        phone = acct.get("phone", "")
        return phone if phone else f"Account #{acct.get('slot', 0) + 1}"

    async def owner_only(update: Update) -> bool:
        if not is_owner(update.effective_user.id):
            await update.message.reply_text(
                f"{TOP}\n║  🔒  {bold_serif('Access Denied')}  🔒  ║\n{BOT}\n\n"
                f"{script('This command is restricted to')}\n👑 {sans_bold('Owners Only')}",
                parse_mode=ParseMode.MARKDOWN,
            )
            return False
        return True

    async def premium_only(update: Update) -> bool:
        if not is_premium(update.effective_user.id):
            await update.message.reply_text(
                f"🌟 {bold_serif('Premium Required')}\n\n"
                f"{script('This feature is for')}\n"
                f"👑 {sans_bold('Owners')} & {sans_bold('Premium Users')} {script('only')}\n\n"
                f"📩 {mono('Contact:')} {SUPPORT_USERNAME}",
                parse_mode=ParseMode.MARKDOWN,
            )
            return False
        return True

    async def check_blocked(update: Update) -> bool:
        if db.is_blocked(update.effective_user.id):
            await update.message.reply_text(
                f"🚫 {bold_serif('You have been Blocked')}\n\n"
                f"{script('Contact support to appeal.')}",
                parse_mode=ParseMode.MARKDOWN,
            )
            return False
        return True

    async def cleanup_pending(uid: int):
        data = pending_logins.pop(uid, None)
        if data and data.get("client"):
            try: await data["client"].disconnect()
            except: pass


    # ════════════════════════════════════════════════════════════════════════════════
    #   V6 ANIMATION ENGINE — lightweight Telegram message transitions
    # ════════════════════════════════════════════════════════════════════════════════

    async def animate_text(message, frames, parse_mode=ParseMode.MARKDOWN, delay=0.12):
        """Animate a short status sequence without changing command logic."""
        last = None
        for frame in frames:
            if frame == last:
                continue
            try:
                await message.edit_text(frame, parse_mode=parse_mode)
            except Exception:
                try:
                    await message.edit_text(frame)
                except Exception:
                    pass
            last = frame
            await asyncio.sleep(delay)

    def _api_banner():
        if _api_ready():
            return (
                f"🔐 {sans_bold('API Profile')} : {script('Ready')}  "
                f"• {mono(str(TELEGRAM_API_ID))} • {mono(_masked_api_hash())}"
            )
        return f"⚠️ {bold_serif('API Profile Missing')} — {script('/setapi to configure')}"

    # ════════════════════════════════════════════════════════════════════════════════
    #   /start
    # ════════════════════════════════════════════════════════════════════════════════

    async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not await check_blocked(update): return
        uid  = update.effective_user.id
        name = update.effective_user.first_name or "User"

        if not db.user_exists(uid):
            db.save_user_meta(uid, {"first_name": name, "joined_at": int(time.time())})

        accounts = db.get_accounts(uid)
        hosted   = [a for a in accounts if a.get("hosted")]
        running  = [a for a in hosted if runner.is_running(uid, a["slot"])]

        if hosted:
            status_line = (
                f"\n📱 {fraktur('Accounts')} : {mono(str(len(hosted)))} hosted  "
                f"| {mono(str(len(running)))} running"
            )
        else:
            status_line = f"\n⚪ {fraktur('Userbot')}: {italic_serif('Not hosted yet')}"

        keyboard = [
            [
                InlineKeyboardButton("🚀  𝗛𝗼𝘀𝘁 𝗠𝘆 𝗨𝘀𝗲𝗿𝗯𝗼𝘁", callback_data="host"),
                InlineKeyboardButton("📋  𝗖𝗼𝗺𝗺𝗮𝗻𝗱𝘀",        callback_data="commands"),
            ],
            [
                InlineKeyboardButton("📊  𝗦𝘁𝗮𝘁𝘂𝘀",   callback_data="status"),
                InlineKeyboardButton("🗑️  𝗟𝗼𝗴𝗼𝘂𝘁",   callback_data="menu_logout"),
            ],
            [
                InlineKeyboardButton("📞  𝗦𝘂𝗽𝗽𝗼𝗿𝘁",          callback_data="support"),
                InlineKeyboardButton("❓  𝗛𝗲𝗹𝗽 & 𝗚𝘂𝗶𝗱𝗲", callback_data="help"),
            ],
        ]
        if is_owner(uid):
            keyboard.append([
                InlineKeyboardButton("📢  𝗕𝗿𝗼𝗮𝗱𝗰𝗮𝘀𝘁", callback_data="broadcast_menu"),
                InlineKeyboardButton("🔐  𝗔𝗣𝗜 𝗦𝗲𝘁𝘁𝗶𝗻𝗴𝘀", callback_data="api_settings"),
            ])

        text = (
            f"{TOP}\n"
            f"║  🤖  {double_struck('SID Premium Hoster')}  🤖  ║\n"
            f"{BOT}\n\n"
            f"🌟 {script('Welcome back')}, {bold_serif(name)}!\n\n"
            f"{DIV}\n"
            f"⚡ {sans_bold('Version')}  : {mono('Advance V6')}\n"
            f"📦 {sans_bold('Commands')} : {mono('500+')}\n"
            f"⚔️ {sans_bold('Raids')}    : {mono('20 Types  1000+ Texts')}\n"
            f"{DIV}\n"
            f"🪪 {fraktur('Your ID')} : `{uid}`"
            f"{status_line}\n\n"
            f"{italic_serif('Select an option below')} 👇"
        )

        # Check for welcome video
        welcome_video = db.get_welcome_video()
        if welcome_video:
            file_id = welcome_video.get("file_id")
            is_video_note = welcome_video.get("is_video_note", False)
            try:
                if is_video_note:
                    await update.message.reply_video_note(
                        video_note=file_id,
                        caption=text,
                        parse_mode=ParseMode.MARKDOWN,
                        reply_markup=InlineKeyboardMarkup(keyboard),
                    )
                else:
                    await update.message.reply_video(
                        video=file_id,
                        caption=text,
                        parse_mode=ParseMode.MARKDOWN,
                        reply_markup=InlineKeyboardMarkup(keyboard),
                    )
            except Exception as e:
                logger.error(f"Failed to send welcome video: {e}")
                # Fallback to text-only
                await update.message.reply_text(
                    text,
                    parse_mode=ParseMode.MARKDOWN,
                    reply_markup=InlineKeyboardMarkup(keyboard),
                )
        else:
            await update.message.reply_text(
                text,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=InlineKeyboardMarkup(keyboard),
            )


    # ════════════════════════════════════════════════════════════════════════════════
    #   V6 /setapi — owner-only API credential wizard
    # ════════════════════════════════════════════════════════════════════════════════

    API_SET_ID, API_SET_HASH = range(10, 12)

    async def cmd_setapi_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not await owner_only(update):
            return ConversationHandler.END

        if _api_ready():
            current = (
                f"\n\n🧩 {sans_bold('Current')}: {mono(str(TELEGRAM_API_ID))}"
                f"\n🔑 {sans_bold('Hash')}: {mono(_masked_api_hash())}"
            )
        else:
            current = "\n\n⚠️ No API profile is configured yet."

        msg = await update.message.reply_text(
            f"{TOP}\n"
            f"║  🔐  {bold_serif('API Profile V6')}  🔐  ║\n"
            f"{BOT}\n\n"
            f"{script('This saves the Telegram API ID and API hash on the server.')}"
            f"{current}\n\n"
            f"1️⃣ {script('Send your Telegram API ID')}\n"
            f"2️⃣ {script('Then send your Telegram API hash')}\n\n"
            f"🛡️ {italic_serif('Owner only • stored in data/api_config.json')}\n"
            f"🚫 {italic_serif('Send /cancel to abort')}",
            parse_mode=ParseMode.MARKDOWN,
        )
        return API_SET_ID

    async def cmd_setapi_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
        raw = update.message.text.strip()
        api_id = _normalize_api_id(raw)
        if not api_id:
            await update.message.reply_text(
                f"❌ {bold_serif('Invalid API ID')}\n\n"
                f"{script('Example')}: {mono('12345678')}",
                parse_mode=ParseMode.MARKDOWN,
            )
            return API_SET_ID

        context.user_data["v6_api_id"] = api_id
        await update.message.reply_text(
            f"✅ {sans_bold('API ID accepted')}: {mono(str(api_id))}\n\n"
            f"🔑 {script('Now send your Telegram API hash')}\n"
            f"🚫 {italic_serif('Or send /cancel')}",
            parse_mode=ParseMode.MARKDOWN,
        )
        return API_SET_HASH

    async def cmd_setapi_hash(update: Update, context: ContextTypes.DEFAULT_TYPE):
        api_hash = _normalize_api_hash(update.message.text.strip())
        api_id = _normalize_api_id(context.user_data.get("v6_api_id"))

        if not api_id:
            await update.message.reply_text(
                f"❌ {bold_serif('API setup state lost.')}\n\n{script('Please run /setapi again.')}",
                parse_mode=ParseMode.MARKDOWN,
            )
            return ConversationHandler.END

        if not api_hash:
            await update.message.reply_text(
                f"❌ {bold_serif('Invalid API hash')}\n\n"
                f"{script('Use the hash shown by Telegram at my.telegram.org')}",
                parse_mode=ParseMode.MARKDOWN,
            )
            return API_SET_HASH

        msg = await update.message.reply_text(
            f"⏳ {bold_serif('Saving API Profile')}...\n{DIV2}"
        )

        try:
            global TELEGRAM_API_ID, TELEGRAM_API_HASH
            _save_api_profile(api_id, api_hash)
            context.user_data.pop("v6_api_id", None)

            await animate_text(
                msg,
                [
                    f"🔐 {sans_bold('Encrypting profile state')}... 1/3",
                    f"💾 {sans_bold('Saving API profile')}... 2/3",
                    f"✅ {sans_bold('Applying runtime configuration')}... 3/3",
                ],
                delay=0.10,
            )
            await msg.edit_text(
                f"{TOP}\n║  ✅  {bold_serif('API Profile Saved')}  ✅  ║\n{BOT}\n\n"
                f"🆔 {sans_bold('API ID')}   : {mono(str(TELEGRAM_API_ID))}\n"
                f"🔑 {sans_bold('API Hash')} : {mono(_masked_api_hash())}\n\n"
                f"{_api_banner()}\n\n"
                f"🚀 {script('No source-code editing is required now.')}\n"
                f"♻️ {script('Future /host, restart and health-check actions use this profile.')}",
                parse_mode=ParseMode.MARKDOWN,
            )
        except Exception as e:
            context.user_data.pop("v6_api_id", None)
            await msg.edit_text(
                f"❌ {bold_serif('API Save Failed')}\n\n"
                f"{mono(str(e)[:160])}",
                parse_mode=ParseMode.MARKDOWN,
            )

        return ConversationHandler.END

    async def cmd_apistatus(update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not await owner_only(update):
            return
        await update.message.reply_text(
            f"{TOP}\n║  📡  {bold_serif('API Runtime Status')}  📡  ║\n{BOT}\n\n"
            f"{_api_banner()}\n"
            f"💾 {sans_bold('Config File')}: {mono('data/api_config.json')}\n"
            f"🔄 {script('Changes apply immediately to new starts/restarts.')}",
            parse_mode=ParseMode.MARKDOWN,
        )

    async def cmd_api_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
        context.user_data.pop("v6_api_id", None)
        await update.message.reply_text(
            f"🚫 {bold_serif('API setup cancelled.')}"
        )
        return ConversationHandler.END

    # ════════════════════════════════════════════════════════════════════════════════
    #   /setwelcomevideo (Owner)
    # ════════════════════════════════════════════════════════════════════════════════

    async def cmd_setwelcomevideo(update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not await owner_only(update): return
        reply = update.message.reply_to_message
        if not reply:
            await update.message.reply_text(
                f"📽️ {bold_serif('Set Welcome Video')}\n\n"
                f"{script('Reply to a video or video note with')}\n"
                f"{mono('/setwelcomevideo')}",
                parse_mode=ParseMode.MARKDOWN,
            )
            return

        file_id = None
        is_video_note = False

        if reply.video:
            file_id = reply.video.file_id
        elif reply.video_note:
            file_id = reply.video_note.file_id
            is_video_note = True
        else:
            await update.message.reply_text(
                f"❌ {bold_serif('Reply must be a video or video note.')}",
                parse_mode=ParseMode.MARKDOWN,
            )
            return

        db.set_welcome_video({"file_id": file_id, "is_video_note": is_video_note})
        await update.message.reply_text(
            f"✅ {bold_serif('Welcome video set successfully!')}\n\n"
            f"📹 {script('New users will see this video on /start')}",
            parse_mode=ParseMode.MARKDOWN,
        )


    # ════════════════════════════════════════════════════════════════════════════════
    #   /removewelcomevideo (Owner)
    # ════════════════════════════════════════════════════════════════════════════════

    async def cmd_removewelcomevideo(update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not await owner_only(update): return
        if db.get_welcome_video() is None:
            await update.message.reply_text(
                f"⚠️ {italic_serif('No welcome video is currently set.')}",
                parse_mode=ParseMode.MARKDOWN,
            )
            return
        db.remove_welcome_video()
        await update.message.reply_text(
            f"🗑️ {bold_serif('Welcome video removed.')}\n\n"
            f"{script('The /start message will now show only text.')}",
            parse_mode=ParseMode.MARKDOWN,
        )


    # ════════════════════════════════════════════════════════════════════════════════
    #   /help
    # ════════════════════════════════════════════════════════════════════════════════

    async def cmd_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not await check_blocked(update): return
        text = (
            f"❓ {double_struck('Help')} & {double_struck('Commands')}\n"
            f"{DIV}\n\n"
            f"{'━'*3} {sans_bold('User Commands')} {'━'*3}\n\n"
            f"🔹 {mono('/start')}       {script('Grand Welcome Screen')}\n"
            f"🔹 {mono('/help')}        {script('This Help Menu')}\n"
            f"🔹 {mono('/commands')}    {script('Userbot Features List')}\n"
            f"🔹 {mono('/host')}        {script('Add & Deploy Account')}\n"
            f"🔹 {mono('/myaccounts')}  {script('Manage All Accounts')}\n"
            f"🔹 {mono('/status')}      {script('Check All Userbots')}\n"
            f"🔹 {mono('/restart')}     {script('Restart Userbot')}\n"
            f"🔹 {mono('/logout')}      {script('Logout an Account')}\n"
            f"🔹 {mono('/support')}     {script('Contact Admin')}\n\n"
            f"{DIV}\n"
            f"{'━'*3} {sans_bold('Premium Commands')} {'━'*3}\n\n"
            f"🔸 {mono('/supportraid')} {bold_italic_serif('Pro Support Raid')}\n\n"
            f"{DIV}\n"
            f"{'━'*3} 👑 {sans_bold('Owner Commands')} {'━'*3}\n\n"
            f"🔺 {mono('/restartall')}    {fraktur('Restart All Userbots')}\n"
            f"🔺 {mono('/refresh')}       {fraktur('Refresh Bot State')}\n"
            f"🔺 {mono('/sudolist')}      {fraktur('Manage Sudo Users')}\n"
            f"🔺 {mono('/setdp')}         {fraktur('Set Display Photo')}\n"
            f"🔺 {mono('/block')}         {fraktur('Block a User')}\n"
            f"🔺 {mono('/unblock')}       {fraktur('Unblock a User')}\n"
            f"🔺 {mono('/blockeduser')}   {fraktur('View Blocked List')}\n"
            f"🔺 {mono('/stats')}         {fraktur('Bot Statistics')}\n"
            f"🔺 {mono('/secretfunction')} {fraktur('Secret Commands')}\n"
            f"🔺 {mono('/setwelcomevideo')} {fraktur('Set Welcome Video')}  ★ NEW\n"
            f"🔺 {mono('/removewelcomevideo')} {fraktur('Remove Welcome Video')}  ★ NEW\n"
            f"{DIV}"
        )
        await update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN)


    # ════════════════════════════════════════════════════════════════════════════════
    #   /commands
    # ════════════════════════════════════════════════════════════════════════════════

    async def cmd_commands(update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not await check_blocked(update): return
        text = (
            f"⚡ {double_struck('SID Advance V6')} — {script('Userbot Features')}\n"
            f"{DIV}\n\n"
            f"⚔️ {bold_serif('Raid & Fight')} {italic_serif('(20 Types  1000+ Texts)')}\n"
            f"{mono('.attack .roast .diss .war .savage')}\n"
            f"{mono('.ultra .godwar .combo .troll .shame')}\n"
            f"{mono('.fire .devil .karma .ghost .legend .doom')}\n"
            f"{mono('.nuke .storm .blizzard .venom')} ★ NEW\n\n"
            f"🔁 {bold_serif('Auto-Reply')}\n"
            f"{mono('.reply .rreply .flag .hrreply .replygod .replysid')}\n\n"
            f"💥 {bold_serif('Spam & Spray')}\n"
            f"{mono('.spray .stopspray .spam .addspam .clearspam')}\n\n"
            f"🛠️ {bold_serif('Utility')}\n"
            f"{mono('.ping .alive .id .info .uptime .tts .qr .ytdl')}\n\n"
            f"🎭 {bold_serif('Profile')}\n"
            f"{mono('.setname .setbio .setpp .copy .normal')}\n\n"
            f"🛡️ {bold_serif('Group Management')}\n"
            f"{mono('.ban .unban .mute .unmute .kick .promote .demote')}\n\n"
            f"👁️ {bold_serif('Anti-Delete & Reaction')}\n"
            f"{mono('.antidel .autoreact .fastgc')}\n\n"
            f"🎲 {bold_serif('Fun & Clone')}\n"
            f"{mono('.clone .stopclone .addbots .notes')}\n\n"
            f"{DIV}\n"
            f"📦 {sans_bold('Total')}: {double_struck('500+')} {script('Commands')}  •  "
            f"{script('Prefix')}: {mono('.')}\n\n"
            f"🚀 {script('Deploy Yours')} → /host"
        )
        await update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN)


    # ════════════════════════════════════════════════════════════════════════════════
    #   /host — Phone + OTP Login Flow  (supports multiple. accounts)
    # ════════════════════════════════════════════════════════════════════════════════

    async def cmd_host_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
        if update.callback_query:
            await update.callback_query.answer()
            reply = update.callback_query.message.reply_text
        else:
            reply = update.message.reply_text

        if not await check_blocked(update): return ConversationHandler.END
        uid = update.effective_user.id

        accounts = db.get_accounts(uid)
        hosted   = [a for a in accounts if a.get("hosted")]
        if len(hosted) >= MAX_ACCOUNTS_PER_USER:
            await reply(
                f"📱 {bold_serif('Account Limit Reached')}\n\n"
                f"{script('You already have')} {mono(str(len(hosted)))} {script('accounts hosted.')}\n"
                f"📌 {italic_serif('Maximum:')} {mono(str(MAX_ACCOUNTS_PER_USER))} {italic_serif('per user')}\n\n"
                f"🗑️ {script('Logout an account first:')} /logout",
                parse_mode=ParseMode.MARKDOWN,
            )
            return ConversationHandler.END

        total = db.hosted_count()
        if total >= MAX_USERBOTS and not is_premium(uid):
            await reply(
                f"😔 {sans_bold('Slots Full')} ({total}/{MAX_USERBOTS})\n\n"
                f"{script('Contact')} {SUPPORT_USERNAME} {script('to get a slot.')}",
                parse_mode=ParseMode.MARKDOWN,
            )
            return ConversationHandler.END

        await cleanup_pending(uid)

        # V6: refuse to start the OTP flow if no API credentials are configured.
        if not _api_ready():
            await reply(
                f"{TOP}\n"
                f"║  🔐  {bold_serif('Telegram API Required')}  🔐  ║\n"
                f"{BOT}\n\n"
                f"{script('No Telegram API profile is configured on the server yet.')}\n\n"
                f"👤 {script('Owner')}: run {mono('/setapi')} once.\n"
                f"👥 {script('Users')}: then /host works normally.",
                parse_mode=ParseMode.MARKDOWN,
            )
            return ConversationHandler.END

        extra = f"\n\n📱 {italic_serif('Account')} {mono(str(len(hosted)+1))} {italic_serif('of')} {mono(str(MAX_ACCOUNTS_PER_USER))}" if hosted else ""

        await reply(
            f"{TOP}\n"
            f"║  🚀  {bold_serif('Deploy Your Userbot')}  🚀  ║\n"
            f"{BOT}\n\n"
            f"📱 {sans_bold('Step 1 of 3')}\n"
            f"{DIV3}\n"
            f"{script('Enter your Telegram Phone Number')}\n\n"
            f"🌍 {fraktur('Format')}: {mono('+91XXXXXXXXXX')}\n"
            f"_(country code ke saath)_{extra}\n\n"
            f"🔴 {italic_serif('Send /cancel to abort')}",
            parse_mode=ParseMode.MARKDOWN,
        )
        return ASK_PHONE


    async def host_got_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
        uid   = update.effective_user.id
        phone = update.message.text.strip()
        digits = phone.replace("+", "").replace(" ", "").replace("-", "")
        if not digits.isdigit() or len(digits) < 7:
            await update.message.reply_text(
                f"❌ {bold_serif('Invalid Number')}\n\n"
                f"{script('Please enter in format')}: {mono('+91XXXXXXXXXX')}",
                parse_mode=ParseMode.MARKDOWN,
            )
            return ASK_PHONE

        msg = await update.message.reply_text(
            f"⏳ {sans_bold('Preparing Telegram Login')}... 🔄"
        )
        try:
            await animate_text(
                msg,
                [
                    f"🔄 {sans_bold('Connecting to Telegram')}... 1/3",
                    f"📡 {sans_bold('Requesting OTP')}... 2/3",
                    f"📨 {sans_bold('Waiting for Telegram')}... 3/3",
                ],
                delay=0.09,
            )
            client = TelegramClient(StringSession(), TELEGRAM_API_ID, TELEGRAM_API_HASH)
            await client.connect()
            result = await client.send_code_request(phone)
            pending_logins[uid] = {
                "client": client,
                "phone":  phone,
                "phone_code_hash": result.phone_code_hash,
            }
            await msg.edit_text(
                f"{TOP}\n"
                f"║  📨  {bold_serif('OTP Sent Successfully')}  📨  ║\n"
                f"{BOT}\n\n"
                f"📱 {fraktur('Number')}: {mono(phone)}\n\n"
                f"📩 {sans_bold('Step 2 of 3')}\n"
                f"{DIV3}\n"
                f"{script('Enter the Login Code from your Telegram app')}\n\n"
                f"💡 {italic_serif('Tip: Send with spaces to avoid auto-forward')}\n"
                f"    {mono('Example')}: {bold_serif('1 2 3 4 5')}",
                parse_mode=ParseMode.MARKDOWN,
            )
            return ASK_CODE
        except FloodWaitError as e:
            await cleanup_pending(uid)
            await msg.edit_text(
                f"⏳ {sans_bold('Flood Wait!')} {mono(str(e.seconds) + 's')} baad try karo."
            )
            return ConversationHandler.END
        except Exception as e:
            await cleanup_pending(uid)
            await msg.edit_text(
                f"❌ {bold_serif('Error')}\n{mono(str(e)[:120])}\n\n{script('Try again:')} /host",
                parse_mode=ParseMode.MARKDOWN,
            )
            return ConversationHandler.END


    async def host_got_code(update: Update, context: ContextTypes.DEFAULT_TYPE):
        uid  = update.effective_user.id
        code = update.message.text.strip().replace(" ", "")

        pending = pending_logins.get(uid)
        if not pending:
            await update.message.reply_text(
                f"❌ {sans_bold('Session expired. Try /host again.')}"
            )
            return ConversationHandler.END

        client: TelegramClient = pending["client"]
        phone: str = pending["phone"]
        hash_: str = pending["phone_code_hash"]

        msg = await update.message.reply_text(f"🔐 {sans_bold('Verifying OTP')}...")
        try:
            await animate_text(
                msg,
                [
                    f"🔐 {sans_bold('Checking code')}... 1/3",
                    f"🛡️ {sans_bold('Validating session')}... 2/3",
                    f"⚡ {sans_bold('Finalizing login')}... 3/3",
                ],
                delay=0.09,
            )
            await client.sign_in(phone, code, phone_code_hash=hash_)
            session_string = client.session.save()
            await client.disconnect()
            pending_logins.pop(uid, None)
            await _deploy_userbot(update, context, uid, session_string, phone, msg)
            return ConversationHandler.END

        except SessionPasswordNeededError:
            await msg.edit_text(
                f"{TOP}\n║  🔒  {bold_serif('2FA Detected')}  🔒  ║\n{BOT}\n\n"
                f"🛡️ {sans_bold('Step 3 of 3')}\n{DIV3}\n"
                f"{script('Your account has Two-Step Verification')}\n\n"
                f"🔑 {fraktur('Enter your 2FA Password')}:",
                parse_mode=ParseMode.MARKDOWN,
            )
            return ASK_2FA

        except PhoneCodeInvalidError:
            await msg.edit_text(
                f"❌ {bold_serif('Wrong Code!')} Dobara enter karo:\n\n"
                f"💡 {mono('Spaces ke saath')}: {bold_serif('1 2 3 4 5')}",
                parse_mode=ParseMode.MARKDOWN,
            )
            return ASK_CODE

        except PhoneCodeExpiredError:
            await cleanup_pending(uid)
            await msg.edit_text(
                f"⏳ {sans_bold('Code Expired!')} Dobara /host karo.",
                parse_mode=ParseMode.MARKDOWN,
            )
            return ConversationHandler.END

        except Exception as e:
            await cleanup_pending(uid)
            await msg.edit_text(
                f"❌ {bold_serif('Error')}\n{mono(str(e)[:120])}\n\nDobara /host karo.",
                parse_mode=ParseMode.MARKDOWN,
            )
            return ConversationHandler.END


    async def host_got_2fa(update: Update, context: ContextTypes.DEFAULT_TYPE):
        uid      = update.effective_user.id
        password = update.message.text.strip()
        pending  = pending_logins.get(uid)
        if not pending:
            await update.message.reply_text("❌ Session expire ho gayi. /host karo.")
            return ConversationHandler.END

        client: TelegramClient = pending["client"]
        phone: str = pending.get("phone", "")
        msg = await update.message.reply_text(f"🔐 {sans_bold('Verifying 2FA Password')}...")
        try:
            await animate_text(
                msg,
                [
                    f"🔐 {sans_bold('Checking 2FA')}... 1/3",
                    f"🛡️ {sans_bold('Authorizing account')}... 2/3",
                    f"⚡ {sans_bold('Creating session')}... 3/3",
                ],
                delay=0.09,
            )
            await client.sign_in(password=password)
            session_string = client.session.save()
            await client.disconnect()
            pending_logins.pop(uid, None)
            await _deploy_userbot(update, context, uid, session_string, phone, msg)
            return ConversationHandler.END
        except Exception as e:
            await cleanup_pending(uid)
            await msg.edit_text(
                f"❌ {bold_serif('Wrong 2FA Password')}\n"
                f"{mono(str(e)[:120])}\n\nDobara /host karo.",
                parse_mode=ParseMode.MARKDOWN,
            )
            return ConversationHandler.END


    async def _deploy_userbot(update, context, uid, session_string, phone, msg):
        name     = update.effective_user.first_name or "User"
        accounts = db.get_accounts(uid)
        existing = {a.get("slot") for a in accounts}
        slot = 0
        while slot in existing:
            slot += 1
        acc_num = slot + 1

        await msg.edit_text(
            f"⏳ {double_struck('Deploying Account')} #{acc_num}... 🔄\n{DIV2}"
        )
        await animate_text(
            msg,
            [
                f"🚀 {double_struck('Starting deploy')} #{acc_num}... 1/3\n{DIV2}",
                f"📦 {double_struck('Launching userbot')} #{acc_num}... 2/3\n{DIV2}",
                f"⚡ {double_struck('Verifying process')} #{acc_num}... 3/3\n{DIV2}",
            ],
            delay=0.09,
        )
        ok = runner.start_userbot(
            uid, slot, str(TELEGRAM_API_ID), TELEGRAM_API_HASH, session_string, str(uid),
        )
        if ok:
            db.save_user_meta(uid, {"first_name": name})
            db.add_account(uid, {
                "slot":           slot,
                "session_string": session_string,
                "hosted":         True,
                "hosted_at":      int(time.time()),
                "phone":          phone,
            })
            await msg.edit_text(
                f"{TOP}\n║  🎉  {bold_serif('Deploy Successful')}  🎉  ║\n{BOT}\n\n"
                f"✅ {sans_bold('Account')} : {mono('#' + str(acc_num))}\n"
                f"📱 {sans_bold('Phone')}   : {mono(phone if phone else 'N/A')}\n"
                f"⚡ {sans_bold('Version')} : {mono('SID Advance V6')}\n"
                f"📦 {sans_bold('Commands')}: {mono('500+')}\n\n"
                f"{DIV}\n"
                f"🔹 {italic_serif('Kisi bhi chat mein')} {mono('.alive')} {italic_serif('bhejo')}\n"
                f"🔹 /myaccounts {italic_serif('se sab accounts dekho')}\n"
                f"🔹 /host {italic_serif('se aur account add karo')}",
                parse_mode=ParseMode.MARKDOWN,
            )
        else:
            await msg.edit_text(
                f"❌ {bold_serif('Deploy Failed')}\n\n"
                f"{script('Possible reasons:')}\n"
                f"• {fraktur('Account banned by Telegram')}\n"
                f"• {fraktur('Server error')}\n\n"
                f"📩 {sans_bold('Support')}: {SUPPORT_USERNAME}",
                parse_mode=ParseMode.MARKDOWN,
            )


    async def host_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
        await cleanup_pending(update.effective_user.id)
        await update.message.reply_text(
            f"🚫 {bold_serif('Login Cancelled')}\n\n"
            f"{script('Use /host to try again anytime.')}"
        )
        return ConversationHandler.END


    # ════════════════════════════════════════════════════════════════════════════════
    #   /broadcast — Owner-only broadcast to all registered users
    # ════════════════════════════════════════════════════════════════════════════════

    async def cmd_broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not await owner_only(update):
            return

        reply = update.message.reply_to_message
        text_arg = " ".join(context.args).strip()

        if not reply and not text_arg:
            await update.message.reply_text(
                f"{TOP}\n"
                f"║  📢  {bold_serif('Broadcast Center')}  📢  ║\n"
                f"{BOT}\n\n"
                f"📝 {script('Reply to any message with')} {mono('/broadcast')}\n"
                f"or {script('use')} {mono('/broadcast your message here')}\n\n"
                f"✨ {italic_serif('Media, photos, videos and files are supported when replying.')}",
                parse_mode=ParseMode.MARKDOWN,
            )
            return

        users = []
        for uid_str in db.get_all_users():
            try:
                target_uid = int(uid_str)
            except Exception:
                continue
            if target_uid == OWNER_ID or db.is_blocked(target_uid):
                continue
            users.append(target_uid)

        total = len(users)
        if total == 0:
            await update.message.reply_text(
                f"⚠️ {bold_serif('No eligible users found.')}",
                parse_mode=ParseMode.MARKDOWN,
            )
            return

        progress = await update.message.reply_text(
            f"📢 {bold_serif('Broadcast Starting')}...\n"
            f"⏳ {script('Preparing')} • {mono(f'0/{total}')}",
            parse_mode=ParseMode.MARKDOWN,
        )

        sent = 0
        failed = 0
        for index, target_uid in enumerate(users, 1):
            try:
                if reply:
                    await context.bot.copy_message(
                        chat_id=target_uid,
                        from_chat_id=update.effective_chat.id,
                        message_id=reply.message_id,
                    )
                else:
                    await context.bot.send_message(
                        chat_id=target_uid,
                        text=text_arg,
                    )
                sent += 1
            except Exception as e:
                failed += 1
                logger.warning(f"Broadcast failed for {target_uid}: {str(e)[:100]}")

            # Small progress animation without changing broadcast behavior.
            if index == 1 or index % 10 == 0 or index == total:
                frames = ["📢", "📣", "🚀", "✨", "📡"]
                frame = frames[(index // 10) % len(frames)]
                try:
                    await progress.edit_text(
                        f"{frame} {bold_serif('Broadcasting')}...\n"
                        f"⏳ {script('Progress')} • {mono(f'{index}/{total}')}\n"
                        f"✅ {mono(str(sent))}  ❌ {mono(str(failed))}",
                        parse_mode=ParseMode.MARKDOWN,
                    )
                except Exception:
                    pass

        await progress.edit_text(
            f"{TOP}\n"
            f"║  ✅  {bold_serif('Broadcast Complete')}  ✅  ║\n"
            f"{BOT}\n\n"
            f"📨 {sans_bold('Sent')}    : {mono(str(sent))}\n"
            f"❌ {sans_bold('Failed')}  : {mono(str(failed))}\n"
            f"👥 {sans_bold('Total')}   : {mono(str(total))}\n\n"
            f"{DIV}\n"
            f"✨ {italic_serif('Broadcast finished successfully.')}",
            parse_mode=ParseMode.MARKDOWN,
        )


    # ════════════════════════════════════════════════════════════════════════════════
    #   /myaccounts — list all accounts with inline manage buttons
    # ════════════════════════════════════════════════════════════════════════════════

    async def cmd_myaccounts(update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not await check_blocked(update): return
        uid      = update.effective_user.id
        accounts = db.get_accounts(uid)
        hosted   = [a for a in accounts if a.get("hosted")]

        if not hosted:
            keyboard = [[InlineKeyboardButton("🚀 Host My First Userbot", callback_data="host")]]
            await update.message.reply_text(
                f"📱 {bold_serif('No Accounts Hosted Yet')}\n\n"
                f"{script('Get started with /host')}\n"
                f"{italic_serif('Host up to')} {mono(str(MAX_ACCOUNTS_PER_USER))} {italic_serif('accounts!')}",
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=InlineKeyboardMarkup(keyboard),
            )
            return

        lines = []
        keyboard = []
        for acct in hosted:
            slot   = acct.get("slot", 0)
            alive  = runner.is_running(uid, slot)
            uptime = runner.get_uptime(uid, slot) if alive else None
            icon   = "🟢" if alive else "🔴"
            phone  = _phone_label(acct)
            up_str = f"  ⏱️ {uptime}" if uptime else ""
            lines.append(
                f"{icon} {bold_serif('Acc #' + str(slot+1))} — {mono(phone)}{up_str}"
            )
            row = []
            if alive:
                row.append(InlineKeyboardButton(f"🔄 Restart #{slot+1}", callback_data=f"restart_acc_{slot}"))
            else:
                row.append(InlineKeyboardButton(f"▶️ Start #{slot+1}",   callback_data=f"start_acc_{slot}"))
            row.append(InlineKeyboardButton(f"🗑️ Logout #{slot+1}", callback_data=f"logout_acc_{slot}"))
            keyboard.append(row)

        if len(hosted) < MAX_ACCOUNTS_PER_USER:
            keyboard.append([InlineKeyboardButton("➕ Add Another Account", callback_data="add_acc")])

        header = (
            f"{TOP}\n"
            f"║  📱  {double_struck('My Accounts')} ({len(hosted)}/{MAX_ACCOUNTS_PER_USER})  📱  ║\n"
            f"{BOT}\n\n"
        )
        body = "\n".join(lines)
        footer = f"\n\n{DIV}\n🔹 /host {italic_serif('— add account')}"

        await update.message.reply_text(
            header + body + footer,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup(keyboard),
        )


    # ════════════════════════════════════════════════════════════════════════════════
    #   /status
    # ════════════════════════════════════════════════════════════════════════════════

    async def cmd_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not await check_blocked(update): return
        uid      = update.effective_user.id
        accounts = db.get_accounts(uid)
        hosted   = [a for a in accounts if a.get("hosted")]

        if not hosted:
            await update.message.reply_text(
                f"❌ {bold_serif('No Userbot Found')}\n\n"
                f"{script('Deploy one using')} /host",
                parse_mode=ParseMode.MARKDOWN,
            )
            return

        import datetime
        lines = []
        for acct in hosted:
            slot     = acct.get("slot", 0)
            alive    = runner.is_running(uid, slot)
            uptime   = runner.get_uptime(uid, slot) if alive else "—"
            hosted_at = acct.get("hosted_at", 0)
            since = datetime.datetime.fromtimestamp(hosted_at).strftime("%d %b %Y  %H:%M") if hosted_at else "—"
            icon = "🟢" if alive else "🔴"
            phone = _phone_label(acct)
            lines.append(
                f"{icon} {sans_bold('Account #' + str(slot+1))} — {mono(phone)}\n"
                f"   ⏱️ {italic_serif('Uptime')} : {mono(uptime)}\n"
                f"   📅 {italic_serif('Hosted')} : {mono(since)}"
            )

        footer = ""
        if any(not runner.is_running(uid, a["slot"]) for a in hosted):
            footer = f"\n\n🔄 {italic_serif('Use /restart to revive stopped accounts.')}"

        await update.message.reply_text(
            f"{TOP}\n║  📊  {double_struck('Userbot Status')}  📊  ║\n{BOT}\n\n"
            + "\n\n".join(lines) +
            f"\n\n{DIV}"
            f"\n⚡ {sans_bold('Version')} : {mono('SID Advance V6')}"
            f"{footer}",
            parse_mode=ParseMode.MARKDOWN,
        )


    # ════════════════════════════════════════════════════════════════════════════════
    #   /restart  (single → restart; multiple → show selection)
    # ════════════════════════════════════════════════════════════════════════════════

    async def cmd_restart(update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not await check_blocked(update): return
        uid      = update.effective_user.id
        accounts = db.get_accounts(uid)
        hosted   = [a for a in accounts if a.get("hosted")]

        if not hosted:
            await update.message.reply_text(
                f"❌ {bold_serif('No Userbot Found.')} {script('Use /host first.')}",
                parse_mode=ParseMode.MARKDOWN,
            )
            return

        if len(hosted) == 1:
            acct = hosted[0]
            slot = acct["slot"]
            await _do_restart(update, uid, slot, acct)
            return

        # Multiple accounts — show selection
        keyboard = []
        for acct in hosted:
            slot  = acct["slot"]
            phone = _phone_label(acct)
            alive = runner.is_running(uid, slot)
            icon  = "🟢" if alive else "🔴"
            keyboard.append([
                InlineKeyboardButton(
                    f"{icon} Restart #{slot+1} — {phone}",
                    callback_data=f"restart_acc_{slot}",
                )
            ])
        keyboard.append([InlineKeyboardButton("❌ Cancel", callback_data="cancel_action")])

        await update.message.reply_text(
            f"🔄 {bold_serif('Which account to restart?')}\n\n"
            f"{script('Select below')} 👇",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup(keyboard),
        )


    async def _do_restart(update_or_query, uid, slot, acct):
        """Actually restart a specific slot. Works for both message and callback."""
        is_cb = hasattr(update_or_query, "callback_query") and update_or_query.callback_query
        if is_cb:
            msg_obj = update_or_query.callback_query.message
            send = msg_obj.reply_text
        else:
            send = update_or_query.message.reply_text

        msg = await send(f"🔄 {sans_bold('Restarting Account')} #{slot+1}...")
        ok = runner.restart_userbot(
            uid, slot, str(TELEGRAM_API_ID), TELEGRAM_API_HASH,
            acct.get("session_string", ""), str(uid),
        )
        if ok:
            await msg.edit_text(
                f"✅ {double_struck('Account #' + str(slot+1) + ' Restarted')}!\n\n"
                f"🟢 {sans_bold('Status')}: {script('Running')}\n"
                f"⚡ {italic_serif('Test with')} {mono('.alive')}",
                parse_mode=ParseMode.MARKDOWN,
            )
        else:
            await msg.edit_text(
                f"❌ {bold_serif('Restart Failed')}\n\n"
                f"📩 {script('Contact')} {SUPPORT_USERNAME}",
                parse_mode=ParseMode.MARKDOWN,
            )


    # ════════════════════════════════════════════════════════════════════════════════
    #   /logout  (single → confirm; multiple → show selection)
    # ════════════════════════════════════════════════════════════════════════════════

    async def cmd_logout(update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not await check_blocked(update): return
        uid      = update.effective_user.id
        accounts = db.get_accounts(uid)
        hosted   = [a for a in accounts if a.get("hosted")]

        if not hosted:
            await update.message.reply_text(
                f"❌ {italic_serif('Koi active userbot nahi hai.')}"
            )
            return

        if len(hosted) == 1:
            acct = hosted[0]
            slot = acct["slot"]
            phone = _phone_label(acct)
            keyboard = [[
                InlineKeyboardButton("✅ Haan, Logout Karo", callback_data=f"confirm_logout_{slot}"),
                InlineKeyboardButton("❌ Cancel",            callback_data="cancel_action"),
            ]]
            await update.message.reply_text(
                f"⚠️ {bold_serif('Logout Confirmation')}\n\n"
                f"📱 {sans_bold('Account')} : {mono(phone)}\n\n"
                f"{script('Logout karne se session delete ho jayega.')}\n"
                f"{italic_serif('Dobara host karne ke liye /host karo.')}",
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=InlineKeyboardMarkup(keyboard),
            )
            return

        # Multiple accounts — show selection
        keyboard = []
        for acct in hosted:
            slot  = acct["slot"]
            phone = _phone_label(acct)
            alive = runner.is_running(uid, slot)
            icon  = "🟢" if alive else "🔴"
            keyboard.append([
                InlineKeyboardButton(
                    f"{icon} Logout #{slot+1} — {phone}",
                    callback_data=f"logout_acc_{slot}",
                )
            ])
        keyboard.append([InlineKeyboardButton("❌ Cancel", callback_data="cancel_action")])

        await update.message.reply_text(
            f"🗑️ {bold_serif('Kaunsa Account Logout Karna Hai?')}\n\n"
            f"{script('Select below')} 👇",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup(keyboard),
        )


    async def _do_logout(uid, slot):
        """Actually perform logout for a slot."""
        runner.stop_userbot(uid, slot)
        db.remove_account(uid, slot)
        session_dir = f"data/sessions/{uid}/{slot}"
        shutil.rmtree(session_dir, ignore_errors=True)


    # ════════════════════════════════════════════════════════════════════════════════
    #   /support
    # ════════════════════════════════════════════════════════════════════════════════

    async def cmd_support(update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not await check_blocked(update): return
        await update.message.reply_text(
            f"{TOP}\n║  📞  {double_struck('Support Center')}  📞  ║\n{BOT}\n\n"
            f"👤 {sans_bold('Admin')}    : {SUPPORT_USERNAME}\n"
            f"⚡ {sans_bold('Response')} : {script('Fast')}\n\n"
            f"{DIV}\n"
            f"🔧 {bold_serif('Try these first:')}\n\n"
            f"🔹 /myaccounts — {italic_serif('Sab accounts dekho')}\n"
            f"🔹 /restart    — {italic_serif('Userbot restart karo')}\n"
            f"🔹 /status     — {italic_serif('Status check karo')}\n"
            f"🔹 /logout → /host — {italic_serif('Re-deploy karo')}",
            parse_mode=ParseMode.MARKDOWN,
        )


    # ════════════════════════════════════════════════════════════════════════════════
    #   /supportraid (Premium)
    # ════════════════════════════════════════════════════════════════════════════════

    async def cmd_supportraid(update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not await check_blocked(update): return
        if not await premium_only(update): return
        args   = context.args
        target = " ".join(args) if args else None
        if not target:
            await update.message.reply_text(
                f"⚔️ {bold_serif('Pro Support Raid')}\n\n"
                f"📌 {sans_bold('Usage')}: {mono('/supportraid @username')}",
                parse_mode=ParseMode.MARKDOWN,
            )
            return
        await update.message.reply_text(
            f"{TOP}\n║  ⚔️  {bold_serif('Support Raid Launched')}  ⚔️  ║\n{BOT}\n\n"
            f"🎯 {sans_bold('Target')} : {mono(target)}\n"
            f"🌪️ {script('All premium userbots activated!')}\n"
            f"⚡ {fraktur('Raid Mode')}: {double_struck('MAX POWER')}",
            parse_mode=ParseMode.MARKDOWN,
        )


    # ════════════════════════════════════════════════════════════════════════════════
    #   /restartall (Owner)
    # ════════════════════════════════════════════════════════════════════════════════

    async def cmd_restartall(update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not await owner_only(update): return
        msg   = await update.message.reply_text(f"🔄 {sans_bold('Restarting All Userbots')}...")
        count = 0
        for uid_str in db.get_all_users():
            uid = int(uid_str)
            if db.is_blocked(uid): continue
            for acct in db.get_accounts(uid):
                if not acct.get("hosted") or not acct.get("session_string"): continue
                slot = acct["slot"]
                ok = runner.restart_userbot(
                    uid, slot, str(TELEGRAM_API_ID), TELEGRAM_API_HASH,
                    acct["session_string"], uid_str,
                )
                if ok: count += 1
        await msg.edit_text(
            f"✅ {double_struck('Restart Complete')}\n\n"
            f"🟢 {sans_bold('Restarted')}: {mono(str(count))} {script('userbots')}",
            parse_mode=ParseMode.MARKDOWN,
        )


    # ════════════════════════════════════════════════════════════════════════════════
    #   /refresh (Owner)
    # ════════════════════════════════════════════════════════════════════════════════

    async def cmd_refresh(update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not await owner_only(update): return
        await update.message.reply_text(
            f"🔁 {bold_serif('Bot State Refreshed')}\n\n"
            f"🟢 {sans_bold('Running')} : {mono(str(runner.running_count()))}\n"
            f"📦 {sans_bold('Total')}   : {mono(str(db.hosted_count()))}\n"
            f"🕒 {sans_bold('Uptime')}  : {mono(uptime_str())}",
            parse_mode=ParseMode.MARKDOWN,
        )


    # ════════════════════════════════════════════════════════════════════════════════
    #   /sudolist (Owner)
    # ════════════════════════════════════════════════════════════════════════════════

    async def cmd_sudolist(update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not await owner_only(update): return
        args  = context.args
        sudos = db.get_sudo_users()

        if args and args[0] == "add" and len(args) > 1:
            try:
                db.add_sudo(int(args[1]))
                await update.message.reply_text(
                    f"✅ {mono(args[1])} {script('added to Sudo Users.')}",
                    parse_mode=ParseMode.MARKDOWN,
                )
            except: await update.message.reply_text("❌ Invalid ID.")
            return

        if args and args[0] == "del" and len(args) > 1:
            try:
                db.remove_sudo(int(args[1]))
                await update.message.reply_text(
                    f"✅ {mono(args[1])} {script('removed from Sudo Users.')}",
                    parse_mode=ParseMode.MARKDOWN,
                )
            except: await update.message.reply_text("❌ Invalid ID.")
            return

        if not sudos:
            await update.message.reply_text(
                f"📋 {bold_serif('No Sudo Users yet.')}\n\nAdd: {mono('/sudolist add <uid>')}",
                parse_mode=ParseMode.MARKDOWN,
            )
            return

        lines = "\n".join(f"  👑 {mono(str(u))}" for u in sudos)
        await update.message.reply_text(
            f"{TOP}\n║  👑  {double_struck('Sudo Users')} ({len(sudos)})  👑  ║\n{BOT}\n\n"
            f"{lines}\n\n{DIV}\n"
            f"➕ {mono('/sudolist add <uid>')}\n"
            f"➖ {mono('/sudolist del <uid>')}",
            parse_mode=ParseMode.MARKDOWN,
        )


    # ════════════════════════════════════════════════════════════════════════════════
    #   /setdp (Owner)
    # ════════════════════════════════════════════════════════════════════════════════

    async def cmd_setdp(update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not await owner_only(update): return
        if not update.message.reply_to_message or not update.message.reply_to_message.photo:
            await update.message.reply_text(f"📸 {script('Kisi photo ko reply karo.')}")
            return
        photo = update.message.reply_to_message.photo[-1]
        file  = await context.bot.get_file(photo.file_id)
        data  = await file.download_as_bytearray()
        from io import BytesIO
        try:
            await context.bot.set_my_profile_photo(BytesIO(bytes(data)))
            await update.message.reply_text(f"✅ {bold_serif('Display Photo Updated')}!")
        except Exception as e:
            await update.message.reply_text(
                f"❌ {sans_bold('Failed')}: {mono(str(e)[:80])}",
                parse_mode=ParseMode.MARKDOWN,
            )


    # ════════════════════════════════════════════════════════════════════════════════
    #   /block  /unblock  /blockeduser (Owner)
    # ════════════════════════════════════════════════════════════════════════════════

    async def cmd_block(update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not await owner_only(update): return
        if not context.args:
            await update.message.reply_text(
                f"📌 {sans_bold('Usage')}: {mono('/block <user_id>')}",
                parse_mode=ParseMode.MARKDOWN,
            )
            return
        try:
            target = int(context.args[0])
            if target == OWNER_ID:
                await update.message.reply_text(f"❌ {italic_serif('Owner ko block nahi kar sakte.')}")
                return
            db.block_user(target)
            runner.stop_all_for_user(target)
            await update.message.reply_text(
                f"🚫 {bold_serif('User Blocked')}\n\n"
                f"🆔 {mono(str(target))}\n"
                f"🔴 {script('All userbots stopped.')}",
                parse_mode=ParseMode.MARKDOWN,
            )
        except ValueError:
            await update.message.reply_text("❌ Invalid ID.")


    async def cmd_unblock(update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not await owner_only(update): return
        if not context.args:
            await update.message.reply_text(
                f"📌 {sans_bold('Usage')}: {mono('/unblock <user_id>')}",
                parse_mode=ParseMode.MARKDOWN,
            )
            return
        try:
            db.unblock_user(int(context.args[0]))
            await update.message.reply_text(
                f"✅ {bold_serif('User Unblocked')}\n🆔 {mono(context.args[0])}",
                parse_mode=ParseMode.MARKDOWN,
            )
        except ValueError:
            await update.message.reply_text("❌ Invalid ID.")


    async def cmd_blockeduser(update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not await owner_only(update): return
        blocked = db.get_blocked()
        if not blocked:
            await update.message.reply_text(f"✅ {script('No blocked users.')}")
            return
        lines = "\n".join(f"  🚫 {mono(str(u))}" for u in blocked)
        await update.message.reply_text(
            f"{TOP}\n║  🚫  {double_struck('Blocked Users')} ({len(blocked)})  🚫  ║\n{BOT}\n\n"
            f"{lines}",
            parse_mode=ParseMode.MARKDOWN,
        )


    # ════════════════════════════════════════════════════════════════════════════════
    #   /stats (Owner)
    # ════════════════════════════════════════════════════════════════════════════════

    async def cmd_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not await owner_only(update): return
        total   = db.user_count()
        hosted  = db.hosted_count()
        running = runner.running_count()
        blocked = len(db.get_blocked())
        sudos   = len(db.get_sudo_users())

        await update.message.reply_text(
            f"{TOP}\n║  📊  {double_struck('Bot Statistics')}  📊  ║\n{BOT}\n\n"
            f"👥 {sans_bold('Total Users')}    : {double_struck(str(total))}\n"
            f"🚀 {sans_bold('Hosted Accounts')}: {double_struck(str(hosted))}\n"
            f"🟢 {sans_bold('Running')}        : {double_struck(str(running))}\n"
            f"🔴 {sans_bold('Stopped')}        : {double_struck(str(hosted - running))}\n"
            f"🚫 {sans_bold('Blocked')}        : {double_struck(str(blocked))}\n"
            f"👑 {sans_bold('Sudo Users')}     : {double_struck(str(sudos))}\n"
            f"📦 {sans_bold('Max Slots')}      : {double_struck(str(MAX_USERBOTS))}\n"
            f"{DIV}\n"
            f"🕒 {sans_bold('Bot Uptime')} : {mono(uptime_str())}",
            parse_mode=ParseMode.MARKDOWN,
        )


    # ════════════════════════════════════════════════════════════════════════════════
    #   /secretfunction (Owner)
    # ════════════════════════════════════════════════════════════════════════════════

    async def cmd_secretfunction(update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not await owner_only(update): return
        await update.message.reply_text(
            f"{TOP}\n║  🔐  {bold_serif('Secret Commands')}  🔐  ║\n{BOT}\n\n"
            f"🔺 {mono('/sudolist add <uid>')}  — {fraktur('Add Premium User')}\n"
            f"🔺 {mono('/sudolist del <uid>')}  — {fraktur('Remove Premium User')}\n"
            f"🔺 {mono('/block <uid>')}         — {fraktur('Ban & Kill All Userbots')}\n"
            f"🔺 {mono('/unblock <uid>')}       — {fraktur('Unban User')}\n"
            f"🔺 {mono('/restartall')}          — {fraktur('Restart All Userbots')}\n"
            f"🔺 {mono('/refresh')}             — {fraktur('Refresh Bot State')}\n"
            f"🔺 {mono('/stats')}               — {fraktur('Full Statistics')}\n"
            f"🔺 {mono('/setdp')}               — {fraktur('Set Display Photo')}\n"
            f"🔺 {mono('/blockeduser')}         — {fraktur('View Blocked List')}\n"
            f"🔺 {mono('/secretfunction')}      — {fraktur('This Menu')}\n"
            f"🔺 {mono('/setwelcomevideo')}     — {fraktur('Set Welcome Video')}\n"
            f"🔺 {mono('/removewelcomevideo')}  — {fraktur('Remove Welcome Video')}",
            parse_mode=ParseMode.MARKDOWN,
        )


    # ════════════════════════════════════════════════════════════════════════════════
    #   CALLBACK QUERY HANDLER
    # ════════════════════════════════════════════════════════════════════════════════

    async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()
        uid  = update.effective_user.id
        data = query.data

        # ── Cancel ───────────────────────────────────────────────────────────────
        if data == "cancel_action":
            await query.message.edit_text(f"🚫 {italic_serif('Cancelled.')}")
            return

        # ── API settings — owner only
        if data == "api_settings":
            if not is_owner(uid):
                await query.answer("🔒 Owner only", show_alert=True)
                return
            keyboard = [[
                InlineKeyboardButton("🔐 Set / Replace API", callback_data="api_start"),
                InlineKeyboardButton("📡 API Status", callback_data="api_status"),
            ], [
                InlineKeyboardButton("❌ Close", callback_data="cancel_action"),
            ]]
            await query.message.reply_text(
                f"{TOP}\n║  🔐  {bold_serif('API Settings')}  🔐  ║\n{BOT}\n\n"
                f"{_api_banner()}\n\n"
                f"{script('Set your API ID + API hash once. The values are kept on the server and reused automatically.')}\n"
                f"🛡️ {italic_serif('Owner-only controls.')}",
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=InlineKeyboardMarkup(keyboard),
            )
            return

        if data == "api_start":
            if not is_owner(uid):
                await query.answer("🔒 Owner only", show_alert=True)
                return
            await query.message.reply_text(
                f"🔐 {bold_serif('API Setup')}\n\n"
                f"{script('Use the owner-only /setapi command to enter the credentials safely.')}"
            )
            return

        if data == "api_status":
            if not is_owner(uid):
                await query.answer("🔒 Owner only", show_alert=True)
                return
            await query.message.reply_text(
                f"{TOP}\n║  📡  {bold_serif('API Status')}  📡  ║\n{BOT}\n\n"
                f"{_api_banner()}\n"
                f"💾 {mono('data/api_config.json')}",
                parse_mode=ParseMode.MARKDOWN,
            )
            return

        # ── Broadcast menu — owner only ──────────────────────────────────────────
        if data == "broadcast_menu":
            if not is_owner(uid):
                await query.answer("🔒 Owner only", show_alert=True)
                return
            await query.message.reply_text(
                f"{TOP}\n"
                f"║  📢  {bold_serif('Broadcast Center')}  📢  ║\n"
                f"{BOT}\n\n"
                f"📝 {script('Reply to any message with')} {mono('/broadcast')}\n"
                f"or use {mono('/broadcast your message')}\n\n"
                f"✨ {italic_serif('Button animation + live progress is enabled.')}",
                parse_mode=ParseMode.MARKDOWN,
            )
            return

        # ── Commands — full list inline ──────────────────────────────────────────
        if data == "commands":
            await query.message.reply_text(
                f"⚡ {double_struck('SID Advance V6')} — {script('Full Commands')}\n"
                f"{DIV}\n\n"
                f"⚔️ {bold_serif('Raid & Fight')} {italic_serif('(20 Types  1000+ Texts)')}\n"
                f"{mono('.attack .roast .diss .war .savage')}\n"
                f"{mono('.ultra .godwar .combo .troll .shame')}\n"
                f"{mono('.fire .devil .karma .ghost .legend .doom')}\n"
                f"{mono('.nuke .storm .blizzard .venom')} ★ NEW\n\n"
                f"🔁 {bold_serif('Auto-Reply')}\n"
                f"{mono('.reply .rreply .flag .hrreply .replygod .replysid')}\n\n"
                f"💥 {bold_serif('Spam & Spray')}\n"
                f"{mono('.spray .stopspray .spam .addspam .clearspam')}\n\n"
                f"🛠️ {bold_serif('Utility')}\n"
                f"{mono('.ping .alive .id .info .uptime .tts .qr .ytdl')}\n\n"
                f"🎭 {bold_serif('Profile')}\n"
                f"{mono('.setname .setbio .setpp .copy .normal')}\n\n"
                f"🛡️ {bold_serif('Group Tools')}\n"
                f"{mono('.ban .unban .mute .unmute .kick .promote .demote')}\n\n"
                f"👁️ {bold_serif('Anti-Delete & Reaction')}\n"
                f"{mono('.antidel .autoreact .fastgc')}\n\n"
                f"🎲 {bold_serif('Fun & Clone')}\n"
                f"{mono('.clone .stopclone .addbots .notes')}\n\n"
                f"{DIV}\n"
                f"📦 {sans_bold('Total')}: {double_struck('500+')}  •  "
                f"{script('Prefix')}: {mono('.')}  •  {script('use')} /host",
                parse_mode=ParseMode.MARKDOWN,
            )
            return

        # ── Status — user's actual hosted accounts ───────────────────────────────
        if data == "status":
            accounts = db.get_accounts(uid)
            hosted   = [a for a in accounts if a.get("hosted")]
            if not hosted:
                await query.message.reply_text(
                    f"❌ {bold_serif('No Userbot Hosted')}\n\n"
                    f"{script('Use /host to deploy your first account.')}",
                    parse_mode=ParseMode.MARKDOWN,
                )
                return
            import datetime
            lines = []
            for acct in hosted:
                slot     = acct.get("slot", 0)
                alive    = runner.is_running(uid, slot)
                uptime   = runner.get_uptime(uid, slot) if alive else "—"
                hosted_at = acct.get("hosted_at", 0)
                since = datetime.datetime.fromtimestamp(hosted_at).strftime("%d %b %Y") if hosted_at else "—"
                icon  = "🟢" if alive else "🔴"
                phone = _phone_label(acct)
                lines.append(
                    f"{icon} {sans_bold('Acc #' + str(slot+1))} — {mono(phone)}\n"
                    f"   ⏱️ {uptime}   📅 {since}"
                )
            footer = ""
            if any(not runner.is_running(uid, a["slot"]) for a in hosted):
                footer = f"\n\n🔄 {italic_serif('/restart se revive karo.')}"
            await query.message.reply_text(
                f"{TOP}\n║  📊  {double_struck('Userbot Status')}  📊  ║\n{BOT}\n\n"
                + "\n\n".join(lines) +
                f"\n\n{DIV}"
                f"\n⚡ {sans_bold('Version')} : {mono('SID Advance V6')}"
                f"{footer}",
                parse_mode=ParseMode.MARKDOWN,
            )
            return

        # ── Logout from menu — show account selector ─────────────────────────────
        if data == "menu_logout":
            accounts = db.get_accounts(uid)
            hosted   = [a for a in accounts if a.get("hosted")]
            if not hosted:
                await query.message.reply_text(
                    f"❌ {italic_serif('Koi active userbot nahi hai.')}"
                )
                return
            if len(hosted) == 1:
                acct  = hosted[0]
                slot  = acct["slot"]
                phone = _phone_label(acct)
                kb = [[
                    InlineKeyboardButton("✅ Haan, Logout Karo", callback_data=f"confirm_logout_{slot}"),
                    InlineKeyboardButton("❌ Cancel",            callback_data="cancel_action"),
                ]]
                await query.message.reply_text(
                    f"⚠️ {bold_serif('Logout Confirmation')}\n\n"
                    f"📱 {sans_bold('Account')} : {mono(phone)}\n\n"
                    f"{script('Session delete ho jayega.')}\n"
                    f"{italic_serif('Dobara /host se add kar sakte ho.')}",
                    parse_mode=ParseMode.MARKDOWN,
                    reply_markup=InlineKeyboardMarkup(kb),
                )
            else:
                kb = []
                for acct in hosted:
                    slot  = acct["slot"]
                    phone = _phone_label(acct)
                    alive = runner.is_running(uid, slot)
                    icon  = "🟢" if alive else "🔴"
                    kb.append([InlineKeyboardButton(
                        f"{icon} Logout #{slot+1} — {phone}",
                        callback_data=f"logout_acc_{slot}",
                    )])
                kb.append([InlineKeyboardButton("❌ Cancel", callback_data="cancel_action")])
                await query.message.reply_text(
                    f"🗑️ {bold_serif('Kaunsa Account Logout Karna Hai?')}\n\n"
                    f"{script('Select below')} 👇",
                    parse_mode=ParseMode.MARKDOWN,
                    reply_markup=InlineKeyboardMarkup(kb),
                )
            return

        # ── Support ───────────────────────────────────────────────────────────────
        if data == "support":
            await query.message.reply_text(
                f"{TOP}\n║  📞  {double_struck('Support Center')}  📞  ║\n{BOT}\n\n"
                f"👤 {sans_bold('Bot Owner')}  : {SUPPORT_USERNAME}\n"
                f"⚡ {sans_bold('Response')}   : {script('Fast')}\n\n"
                f"{DIV}\n"
                f"🔧 {bold_serif('Pehle Yeh Try Karo:')}\n\n"
                f"🔹 /myaccounts — {italic_serif('sab accounts dekho')}\n"
                f"🔹 /restart    — {italic_serif('userbot restart karo')}\n"
                f"🔹 /status     — {italic_serif('status check karo')}\n"
                f"🔹 /logout     — {italic_serif('aur dobara /host karo')}\n\n"
                f"{DIV}\n"
                f"🤖 {bold_serif('Bot Owner')}: {SUPPORT_USERNAME}",
                parse_mode=ParseMode.MARKDOWN,
            )
            return

        # ── Help & Guide — step-by-step ──────────────────────────────────────────
        if data == "help":
            await query.message.reply_text(
                f"╔══════════════════════════════╗\n"
                f"║  📖  {bold_serif('BOT USAGE GUIDE')}  📖  ║\n"
                f"╚══════════════════════════════╝\n\n"
                f"{'━'*30}\n"
                f"🚀 {sans_bold('STEP 1')} — {bold_serif('Bot Start Karo')}\n"
                f"{'━'*30}\n"
                f"➡️ {script('Is bot pe')} /start {script('bhejo')}\n"
                f"✅ {italic_serif('Welcome screen aayega')}\n\n"
                f"{'━'*30}\n"
                f"📱 {sans_bold('STEP 2')} — {bold_serif('Account Host Karo')}\n"
                f"{'━'*30}\n"
                f"➡️ {mono('Host My Userbot')} {script('button tap karo')}\n"
                f"➡️ {script('Apna phone number enter karo')}\n"
                f"    {mono('Format: +91XXXXXXXXXX')}\n"
                f"➡️ {script('Telegram se OTP aayega')}\n"
                f"    💡 {italic_serif('OTP spaces ke saath bhejo:')}\n"
                f"    {mono('1 2 3 4 5')} ← {italic_serif('aisa karo')}\n"
                f"➡️ {script('2FA hai toh password bhi daalo')}\n"
                f"✅ {italic_serif('Userbot deploy ho jayega!')}\n\n"
                f"{'━'*30}\n"
                f"⚡ {sans_bold('STEP 3')} — {bold_serif('Commands Chalao')}\n"
                f"{'━'*30}\n"
                f"➡️ {script('Kisi bhi chat mein jao')}\n"
                f"➡️ {script('Dot')} {mono('.')} {script('se command likho:')}\n\n"
                f"    {mono('.alive')}  → {script('Bot alive check karo')}\n"
                f"    {mono('.ping')}   → {script('Speed check')}\n"
                f"    {mono('.help')}   → {script('Poori command list')}\n"
                f"    {mono('.attack')} → {script('Kisi pe reply karke attack')}\n"
                f"    {mono('.roast')}  → {script('Kisi ko roast karo')}\n"
                f"    {mono('.nuke')}   → ☢️ {script('Nuclear strike')}\n"
                f"    {mono('.spray <text>')} → {script('Spam shuru')}\n"
                f"    {mono('.stopspray')}    → {script('Spam band karo')}\n\n"
                f"{'━'*30}\n"
                f"🔄 {sans_bold('STEP 4')} — {bold_serif('Manage Karo')}\n"
                f"{'━'*30}\n"
                f"    /myaccounts — {script('Sab accounts')}\n"
                f"    /status     — {script('Status dekho')}\n"
                f"    /restart    — {script('Restart karo')}\n"
                f"    /logout     — {script('Logout karo')}\n"
                f"    /host       — {script('Naya account add karo')}\n\n"
                f"{'━'*30}\n"
                f"⚠️ {sans_bold('IMPORTANT')}\n"
                f"{'━'*30}\n"
                f"🔸 {italic_serif('Sirf tumhara OWN account command chalayega')}\n"
                f"🔸 {italic_serif('Kisi dusre ka message ignore hoga')}\n"
                f"🔸 {italic_serif('Max')} {mono('3')} {italic_serif('accounts ek saath host ho sakte hain')}\n\n"
                f"{'━'*30}\n"
                f"🌟 {bold_serif('Bot Owner')}: {SUPPORT_USERNAME}\n"
                f"⚡ {bold_serif('Powered by SIDxBOT')}",
                parse_mode=ParseMode.MARKDOWN,
            )
            return

        # ── Restart account ──────────────────────────────────────────────────────
        if data.startswith("restart_acc_"):
            try:
                slot = int(data.split("_")[-1])
            except ValueError:
                return
            acct = db.get_account(uid, slot)
            if not acct:
                await query.message.reply_text(f"❌ {italic_serif('Account not found.')}")
                return
            msg = await query.message.reply_text(
                f"🔄 {sans_bold('Restarting Account')} #{slot+1}..."
            )
            ok = runner.restart_userbot(
                uid, slot, str(TELEGRAM_API_ID), TELEGRAM_API_HASH,
                acct.get("session_string", ""), str(uid),
            )
            if ok:
                await msg.edit_text(
                    f"✅ {double_struck('Account #' + str(slot+1) + ' Restarted')}!\n\n"
                    f"🟢 {sans_bold('Status')}: {script('Running')}\n"
                    f"⚡ {italic_serif('Test with')} {mono('.alive')}",
                    parse_mode=ParseMode.MARKDOWN,
                )
            else:
                await msg.edit_text(f"❌ {bold_serif('Restart Failed')}\n📩 {SUPPORT_USERNAME}")
            return

        # ── Start (stopped) account ───────────────────────────────────────────────
        if data.startswith("start_acc_"):
            try:
                slot = int(data.split("_")[-1])
            except ValueError:
                return
            acct = db.get_account(uid, slot)
            if not acct:
                await query.message.reply_text(f"❌ {italic_serif('Account not found.')}")
                return
            msg = await query.message.reply_text(
                f"▶️ {sans_bold('Starting Account')} #{slot+1}..."
            )
            ok = runner.start_userbot(
                uid, slot, str(TELEGRAM_API_ID), TELEGRAM_API_HASH,
                acct.get("session_string", ""), str(uid),
            )
            if ok:
                await msg.edit_text(
                    f"✅ {double_struck('Account #' + str(slot+1) + ' Started')}!\n\n"
                    f"🟢 {sans_bold('Status')}: {script('Running')}\n"
                    f"⚡ {italic_serif('Test with')} {mono('.alive')}",
                    parse_mode=ParseMode.MARKDOWN,
                )
            else:
                await msg.edit_text(f"❌ {bold_serif('Start Failed')}\n📩 {SUPPORT_USERNAME}")
            return

        # ── Logout account — show confirm prompt ─────────────────────────────────
        if data.startswith("logout_acc_"):
            try:
                slot = int(data.split("_")[-1])
            except ValueError:
                return
            acct  = db.get_account(uid, slot)
            if not acct:
                await query.message.reply_text(f"❌ {italic_serif('Account not found.')}")
                return
            phone = _phone_label(acct)
            keyboard = [[
                InlineKeyboardButton("✅ Haan, Logout Karo", callback_data=f"confirm_logout_{slot}"),
                InlineKeyboardButton("❌ Cancel",            callback_data="cancel_action"),
            ]]
            await query.message.reply_text(
                f"⚠️ {bold_serif('Logout Confirmation')}\n\n"
                f"📱 {sans_bold('Account')} #{slot+1} : {mono(phone)}\n\n"
                f"{script('Session delete ho jayega.')}\n"
                f"{italic_serif('Dobara /host se add kar sakte ho.')}",
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=InlineKeyboardMarkup(keyboard),
            )
            return

        # ── Confirm logout ────────────────────────────────────────────────────────
        if data.startswith("confirm_logout_"):
            try:
                slot = int(data.split("_")[-1])
            except ValueError:
                return
            acct  = db.get_account(uid, slot)
            phone = _phone_label(acct) if acct else f"#{slot+1}"
            await _do_logout(uid, slot)
            await query.message.edit_text(
                f"{TOP}\n║  👋  {bold_serif('Logged Out')}  👋  ║\n{BOT}\n\n"
                f"📱 {sans_bold('Account')} : {mono(phone)}\n"
                f"🗑️ {sans_bold('Session')} : {script('Cleared')}\n\n"
                f"🚀 {fraktur('Re-deploy anytime:')} /host\n"
                f"📱 {fraktur('See accounts:')} /myaccounts",
                parse_mode=ParseMode.MARKDOWN,
            )
            return

        # ── Add another account (same as /host entry) ─────────────────────────────
        if data == "add_acc":
            accounts = db.get_accounts(uid)
            hosted   = [a for a in accounts if a.get("hosted")]
            if len(hosted) >= MAX_ACCOUNTS_PER_USER:
                await query.message.reply_text(
                    f"📱 {bold_serif('Account Limit Reached')}\n\n"
                    f"{script('Maximum')} {mono(str(MAX_ACCOUNTS_PER_USER))} {script('accounts.')}\n"
                    f"🗑️ {script('Logout one first:')} /logout",
                    parse_mode=ParseMode.MARKDOWN,
                )
                return
            # Fall through to host conversation — user must send /host
            await query.message.reply_text(
                f"🚀 {bold_serif('Add New Account')}\n\n"
                f"{script('Send')} /host {script('to start the login flow.')}",
                parse_mode=ParseMode.MARKDOWN,
            )
            return


    # ════════════════════════════════════════════════════════════════════════════════
    #   AUTO HEALTH CHECK
    # ════════════════════════════════════════════════════════════════════════════════

    async def auto_health_check(context: ContextTypes.DEFAULT_TYPE):
        for uid_str in db.get_all_users():
            uid = int(uid_str)
            if db.is_blocked(uid): continue
            for acct in db.get_accounts(uid):
                if not acct.get("hosted") or not acct.get("session_string"): continue
                slot = acct["slot"]
                if not runner.is_running(uid, slot):
                    runner.start_userbot(
                        uid, slot, str(TELEGRAM_API_ID), TELEGRAM_API_HASH,
                        acct["session_string"], uid_str,
                    )


    # ════════════════════════════════════════════════════════════════════════════════
    #   STARTUP & MAIN
    # ════════════════════════════════════════════════════════════════════════════════

    async def post_init(application: Application):
        _load_api_profile()
        await application.bot.set_my_commands([
            BotCommand("start",           "Grand Welcome"),
            BotCommand("help",            "All Commands"),
            BotCommand("commands",        "Userbot Features"),
            BotCommand("host",            "Add & Deploy Account"),
            BotCommand("myaccounts",      "Manage All Accounts"),
            BotCommand("status",          "Check Userbot Status"),
            BotCommand("restart",         "Restart Userbot"),
            BotCommand("logout",          "Logout an Account"),
            BotCommand("support",         "Get Support"),
            BotCommand("supportraid",     "Pro Raid (Premium)"),
            BotCommand("restartall",      "Restart All (Owner)"),
            BotCommand("refresh",         "Refresh State (Owner)"),
            BotCommand("sudolist",        "Sudo Users (Owner)"),
            BotCommand("setdp",           "Set Display Photo (Owner)"),
            BotCommand("block",           "Block User (Owner)"),
            BotCommand("unblock",         "Unblock User (Owner)"),
            BotCommand("blockeduser",     "Blocked List (Owner)"),
            BotCommand("stats",           "Bot Statistics (Owner)"),
            BotCommand("secretfunction",  "Secret Commands (Owner)"),
            BotCommand("setwelcomevideo", "Set Welcome Video (Owner)"),
            BotCommand("removewelcomevideo", "Remove Welcome Video (Owner)"),
            BotCommand("broadcast",       "Broadcast Message (Owner)"),
            BotCommand("setapi",           "Set Telegram API (Owner)"),
            BotCommand("apistatus",        "Show API Status (Owner)"),
        ])
        count = 0
        for uid_str in db.get_all_users():
            uid = int(uid_str)
            if db.is_blocked(uid): continue
            for acct in db.get_accounts(uid):
                if not acct.get("hosted") or not acct.get("session_string"): continue
                ok = runner.start_userbot(
                    uid, acct["slot"], str(TELEGRAM_API_ID), TELEGRAM_API_HASH,
                    acct["session_string"], uid_str,
                )
                if ok: count += 1
        logger.info(f"[STARTUP] Auto-started {count} userbots.")


    def main():
        if not BOT_TOKEN:  raise ValueError("BOT_TOKEN not set!")
        if not OWNER_ID:   raise ValueError("OWNER_ID not set!")

        app = Application.builder().token(BOT_TOKEN).post_init(post_init).build()

        host_conv = ConversationHandler(
            entry_points=[
                CommandHandler("host", cmd_host_start),
                CallbackQueryHandler(cmd_host_start, pattern="^host$"),
            ],
            states={
                ASK_PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, host_got_phone)],
                ASK_CODE:  [MessageHandler(filters.TEXT & ~filters.COMMAND, host_got_code)],
                ASK_2FA:   [MessageHandler(filters.TEXT & ~filters.COMMAND, host_got_2fa)],
            },
            fallbacks=[CommandHandler("cancel", host_cancel)],
            allow_reentry=True,
        )

        app.add_handler(CommandHandler("start",           cmd_start))
        app.add_handler(CommandHandler("help",            cmd_help))
        app.add_handler(CommandHandler("commands",        cmd_commands))
        app.add_handler(host_conv)
        app.add_handler(CommandHandler("myaccounts",      cmd_myaccounts))
        app.add_handler(CommandHandler("status",          cmd_status))
        app.add_handler(CommandHandler("restart",         cmd_restart))
        app.add_handler(CommandHandler("logout",          cmd_logout))
        app.add_handler(CommandHandler("support",         cmd_support))
        app.add_handler(CommandHandler("supportraid",     cmd_supportraid))
        app.add_handler(CommandHandler("restartall",      cmd_restartall))
        app.add_handler(CommandHandler("refresh",         cmd_refresh))
        app.add_handler(CommandHandler("sudolist",        cmd_sudolist))
        app.add_handler(CommandHandler("setdp",           cmd_setdp))
        app.add_handler(CommandHandler("block",           cmd_block))
        app.add_handler(CommandHandler("unblock",         cmd_unblock))
        app.add_handler(CommandHandler("blockeduser",     cmd_blockeduser))
        app.add_handler(CommandHandler("stats",           cmd_stats))
        app.add_handler(CommandHandler("secretfunction",  cmd_secretfunction))
        app.add_handler(CommandHandler("setwelcomevideo", cmd_setwelcomevideo))
        app.add_handler(CommandHandler("removewelcomevideo", cmd_removewelcomevideo))
        api_conv = ConversationHandler(
            entry_points=[CommandHandler("setapi", cmd_setapi_start)],
            states={
                API_SET_ID: [MessageHandler(filters.TEXT & ~filters.COMMAND, cmd_setapi_id)],
                API_SET_HASH: [MessageHandler(filters.TEXT & ~filters.COMMAND, cmd_setapi_hash)],
            },
            fallbacks=[CommandHandler("cancel", cmd_api_cancel)],
            allow_reentry=True,
        )

        app.add_handler(api_conv)
        app.add_handler(CommandHandler("apistatus", cmd_apistatus))
        app.add_handler(CommandHandler("broadcast",         cmd_broadcast))
        app.add_handler(CallbackQueryHandler(callback_handler))

        if app.job_queue:
            app.job_queue.run_repeating(auto_health_check, interval=300, first=60)

        logger.info("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        logger.info("🤖  SID Premium Hoster Bot STARTED!")
        logger.info(f"👑  Owner ID: {OWNER_ID}")
        logger.info("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

        app.run_polling(allowed_updates=Update.ALL_TYPES)


    if __name__ == "__main__":
        main()
