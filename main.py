import telebot
from keep_alive import keep_alive
keep_alive()

TOKEN = '7732904937:AAEfjgFjcDSKtZ28CK1e0q58kOxrfcSvNXY'  # Thay bằng token của bạn
bot = telebot.TeleBot(TOKEN)

admin_id = 7221856841  # Thay bằng Telegram ID của admin

# Cấu trúc: {user_id: {"username": ..., "coin": ...}}
users = {}

# ========== NGƯỜI DÙNG ==========

@bot.message_handler(commands=['start'])
def start(msg):
    uid = msg.from_user.id
    if uid not in users:
        users[uid] = {"username": msg.from_user.username or "NoName", "coin": 0}
    bot.reply_to(msg, "🎲 Chào mừng đến với bot Tài/Xỉu!\nDùng /menu để xem các lệnh.")

@bot.message_handler(commands=['menu'])
def menu_nguoi_dung(msg):
    bot.reply_to(msg,
        "📱 *Menu người dùng:*\n"
        "/napxu - Hướng dẫn nạp xu\n"
        "/sodu - Xem số dư\n"
        "/txmd5 <md5> - Dự đoán Tài/Xỉu từ MD5\n"
        "/tx <chuỗi t x> - Phân tích chuỗi kết quả\n"
        "/hotro - Liên hệ hỗ trợ",
        parse_mode='Markdown')

@bot.message_handler(commands=['napxu'])
def yeu_cau_napxu(msg):
    uid = msg.from_user.id
    username = msg.from_user.username or "Không có username"
    huong_dan = (
        "💰 Hướng dẫn nạp xu:\n"
        "1. Chuyển khoản MOMO/MB BANK cho admin.\n"
        "2. STK : 8834811249.\n"
        "3. NGÂN HÀNG ADMIN : BIDV.\n"
        "4. CHỦ TÀI KHOẢN : LE QUANG HUNG.\n"
        "5. Ghi chú: Telegram ID @GetIDcnBot hoặc Username.\n"
        "6. Chờ admin cộng xu.\n\n"
        "7. LƯU Ý CHỈ HỖ TRỢ TRÊN 30XU.\n\n"
        f"🔁 Bạn: @{username} (ID: {uid})"
    )
    bot.reply_to(msg, huong_dan)
    bot.send_message(admin_id, f"📥 Yêu cầu nạp xu từ @{username} (ID: {uid})")

@bot.message_handler(commands=['sodu'])
def so_du(msg):
    uid = msg.from_user.id
    if uid in users:
        xu = users[uid]["coin"]
        bot.reply_to(msg, f"💰 Số dư hiện tại: {xu} xu")
    else:
        bot.reply_to(msg, "❌ Bạn chưa được đăng ký!")

@bot.message_handler(commands=['hotro'])
def hotro(msg):
    bot.reply_to(msg, "📞 Liên hệ hỗ trợ: @LQHng_W")

# ========== TÍNH NĂNG TÀI/XỈU ==========

@bot.message_handler(commands=['txmd5'])
def tx_md5(msg):
    uid = msg.from_user.id
    if uid not in users or users[uid]["coin"] <= 0:
        bot.reply_to(msg, "❗ Bạn cần nạp xu để dùng lệnh này. Dùng /napxu để nạp.")
        return

    args = msg.text.split()
    if len(args) != 2:
        bot.reply_to(msg, "❗ Cú pháp đúng: /txmd5 <md5>")
        return

    md5 = args[1]
    try:
        last_char = md5[-1]
        num = int(last_char, 16)
        kq = "🎯 TÀI" if num >= 8 else "🎯 XỈU"
        users[uid]["coin"] -= 1
        bot.reply_to(msg, f"🐱‍👤Kết quả dự đoán từ MD5🤖: {kq}\n💰 Xu còn lại: {users[uid]['coin']}")
    except:
        bot.reply_to(msg, "❌ MD5 không hợp lệ!")

@bot.message_handler(commands=['tx'])
def phan_tich_tx(msg):
    uid = msg.from_user.id
    if uid not in users or users[uid]["coin"] <= 0:
        bot.reply_to(msg, "❗ Bạn cần nạp xu để dùng lệnh này. Dùng /napxu để nạp.")
        return

    chuoi = msg.text[4:].strip().lower().replace(" ", "")
    if not chuoi or not all(c in "tx" for c in chuoi):
        bot.reply_to(msg, "❗ Vui lòng nhập chuỗi gồm T hoặc X.\nVí dụ: /tx t t x x t")
        return

    so_tai = chuoi.count("t")
    so_xiu = chuoi.count("x")

    # Dự đoán kết quả cuối cùng
    if so_tai > so_xiu:
        ket_qua = "🔥 KẾT LUẬN: Dự đoán *TÀI* 🎯"
        icon = "💥💥💥"
    elif so_xiu > so_tai:
        ket_qua = "❄️ KẾT LUẬN: Dự đoán *XỈU* 🎯"
        icon = "🌊🌊🌊"
    else:
        ket_qua = "⚖️ KẾT LUẬN: *Hòa số lượng* – Không thể xác định rõ!"
        icon = "❔❔❔"

    # Trừ 1 xu
    users[uid]["coin"] -= 1
    bot.reply_to(msg,
        f"📊 Phân tích: {so_tai} Tài - {so_xiu} Xỉu\n"
        f"{ket_qua}\n"
        f"{icon}\n"
        f"💰 Xu còn lại: {users[uid]['coin']}",
        parse_mode='Markdown'
    )

# ========== ADMIN ==========

@bot.message_handler(commands=['menuadmin'])
def menu_admin(msg):
    if msg.from_user.id != admin_id:
        return
    bot.reply_to(msg,
        "🛠 *Menu quản trị:*\n"
        "/add <user_id> - Thêm người dùng\n"
        "/ban <user_id> - Xoá người dùng\n"
        "/congxu <user_id> <số_xu> - Cộng xu\n"
        "/danhsach - Xem danh sách người dùng",
        parse_mode='Markdown')

@bot.message_handler(commands=['add'])
def add_user(msg):
    if msg.from_user.id != admin_id:
        return
    args = msg.text.split()
    if len(args) != 2:
        bot.reply_to(msg, "❗ Cú pháp: /add <user_id>")
        return
    uid = int(args[1])
    if uid not in users:
        users[uid] = {"username": f"user_{uid}", "coin": 0}
        bot.reply_to(msg, f"✅ Đã thêm người dùng {uid}")
    else:
        bot.reply_to(msg, "⚠️ Người dùng đã tồn tại.")

@bot.message_handler(commands=['ban'])
def ban_user(msg):
    if msg.from_user.id != admin_id:
        return
    args = msg.text.split()
    if len(args) != 2:
        bot.reply_to(msg, "❗ Cú pháp: /ban <user_id>")
        return
    uid = int(args[1])
    if uid in users:
        users.pop(uid)
        bot.reply_to(msg, f"🚫 Đã xoá người dùng {uid}")
    else:
        bot.reply_to(msg, "⚠️ Người dùng không tồn tại!")

@bot.message_handler(commands=['congxu'])
def cong_xu(msg):
    if msg.from_user.id != admin_id:
        return
    args = msg.text.split()
    if len(args) != 3:
        bot.reply_to(msg, "❗ Cú pháp: /congxu <user_id> <số_xu>")
        return
    uid = int(args[1])
    xu = int(args[2])
    if uid in users:
        users[uid]["coin"] += xu
        bot.reply_to(msg, f"✅ Đã cộng {xu} xu cho {uid}. Tổng: {users[uid]['coin']}")
    else:
        bot.reply_to(msg, "⚠️ Người dùng không tồn tại!")

@bot.message_handler(commands=['danhsach'])
def danh_sach(msg):
    if msg.from_user.id != admin_id:
        return
    if not users:
        bot.reply_to(msg, "📋 Danh sách người dùng trống.")
        return
    ds = "\n".join([f"{u} (@{d['username']}): {d['coin']} xu" for u, d in users.items()])
    bot.reply_to(msg, f"📋 Danh sách người dùng:\n{ds}")

# ========== KHỞI CHẠY ==========

print("🤖 Bot đang chạy...")
bot.infinity_polling()
