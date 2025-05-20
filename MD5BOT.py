import asyncio
import json
import random
from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackContext

# Cấu hình bot
BOT_CONFIG = {
    'TOKEN': '7777783236:AAFLH6v7H9Ryzo0GmdwEK53nYl3EehJm_FI',
    'GROUP_ID': -1002400652968,
    'ADMIN_ID': 7221856841
}

BALANCE_FILE = "balance.json"
CODE_FILE = "codes.json"  # File lưu mã code

def load_codes():
    """Tải dữ liệu mã code từ file"""
    try:
        with open(CODE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def save_codes():
    """Lưu mã code vào file"""
    try:
        with open(CODE_FILE, "w", encoding="utf-8") as f:
            json.dump(CODE_STORE, f, ensure_ascii=False, indent=4)
    except Exception as e:
        print(f"⚠️ Lỗi khi lưu mã code: {e}")

# Load dữ liệu mã code khi bot khởi động
CODE_STORE = load_codes()
CODE_STORE = {}

# 📌 Tải dữ liệu khi bot khởi động
def load_balance():
    try:
        with open(BALANCE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def save_balance():
    try:
        with open(BALANCE_FILE, "w", encoding="utf-8") as f:
            json.dump(user_money, f, ensure_ascii=False, indent=4)
    except Exception as e:
        print(f"⚠️ Lỗi khi lưu dữ liệu: {e}")

user_money = load_balance()

async def send_welcome_message(application: Application):
    """Gửi tin nhắn chào mừng khi bot khởi động"""
    welcome_text = "🎲 **Chào mừng đến với bot tài xỉu by hp!**\n💰 Hãy thử vận may ngay!"
    await application.bot.send_message(chat_id=BOT_CONFIG['GROUP_ID'], text=welcome_text)

async def menu(update: Update, context: CallbackContext):
    """Lệnh /menu - Hiển thị danh sách lệnh"""
    menu_text = (
        "📌 *Danh sách lệnh bot:* \n\n"
        "✅ /dangky - Đăng ký tài khoản\n"
        "🎲 /taixiu <tài/xỉu> <số tiền hoặc 'all'> - Chơi tài xỉu\n"
        "🏆 /top - Xem bảng xếp hạng\n"
        "💰 /sodu - Xem số dư\n"
        "🔑 /codevip <mã code> - Nhập code tiền\n"
        "🛠 /code <số tiền> (Admin) - Tạo mã code\n"
        "💰 /admoney <số tiền> (Admin) - Cộng tiền\n"
        "📜 /menu - Xem danh sách lệnh"
    )
    await update.message.reply_text(menu_text, parse_mode="Markdown")

async def dangky(update: Update, context: CallbackContext):
    """Lệnh /dangky - Đăng ký tài khoản"""
    user_id = str(update.message.from_user.id)
    if user_id in user_money:
        await update.message.reply_text("✅ Bạn đã đăng ký trước đó!")
        return

    user_money[user_id] = 1000  
    save_balance()
    await update.message.reply_text("🎉 Bạn đã đăng ký thành công! Số dư: 1000 VNĐ")

async def sodu(update: Update, context: CallbackContext):
    """Lệnh /sodu - Hiển thị số dư của người dùng"""
    user_id = str(update.message.from_user.id)
    balance = user_money.get(user_id, 0)
    await update.message.reply_text(f"💰 **Số dư của bạn:** {balance:,} VNĐ", parse_mode="Markdown")

async def code(update: Update, context: CallbackContext):
    """Lệnh /code - Admin tạo mã code nhận tiền"""
    if update.message.from_user.id != BOT_CONFIG['ADMIN_ID']:
        await update.message.reply_text("❌ Bạn không có quyền sử dụng lệnh này!")
        return

    if len(context.args) < 1:
        await update.message.reply_text("📌 **Cú pháp:** /code <số tiền>")
        return

    try:
        amount = int(context.args[0])
        if amount <= 0:
            raise ValueError
    except ValueError:
        await update.message.reply_text("❌ Số tiền không hợp lệ! Vui lòng nhập số dương.")
        return

    code = str(random.randint(100000, 999999))  # Tạo mã code ngẫu nhiên
    CODE_STORE[code] = amount  # Lưu vào bộ nhớ
    save_codes()  # Lưu vào file JSON

    await update.message.reply_text(f"✅ **Mã code:** `{code}` - Giá trị: {amount:,} VNĐ", parse_mode="Markdown")
    
async def codevip(update: Update, context: CallbackContext):
    """Lệnh /codevip - Nhập code để nhận tiền"""
    user_id = str(update.message.from_user.id)

    if not context.args:
        await update.message.reply_text("📌 **Cú pháp:** /codevip <mã code>")
        return

    code = context.args[0]

    if code in CODE_STORE:
        amount = CODE_STORE.pop(code)  # Xóa code sau khi sử dụng
        user_money[user_id] = user_money.get(user_id, 0) + amount
        save_balance()
        save_codes()  # Cập nhật file mã code
        await update.message.reply_text(f"🎉 **Bạn đã nhận được {amount:,} VNĐ!**", parse_mode="Markdown")
    else:
        await update.message.reply_text("❌ Mã code không hợp lệ hoặc đã được sử dụng!")
async def admoney(update: Update, context: CallbackContext):
    """Lệnh /admoney - Admin cộng tiền"""
    if update.message.from_user.id != BOT_CONFIG['ADMIN_ID']:
        await update.message.reply_text("❌ Bạn không có quyền!")
        return

    if not update.message.reply_to_message:
        await update.message.reply_text("📌 **Reply tin nhắn cần cộng tiền!**")
        return

    try:
        amount = int(context.args[0])
    except (IndexError, ValueError):
        await update.message.reply_text("📌 **Cú pháp:** /admoney <số tiền>")
        return

    target_user_id = str(update.message.reply_to_message.from_user.id)
    user_money[target_user_id] = user_money.get(target_user_id, 1000) + amount
    save_balance()
    await update.message.reply_text(f"✅ **Đã cộng {amount} VNĐ!** 💰 Số dư: {user_money[target_user_id]}")

async def top(update: Update, context: CallbackContext):
    """Lệnh /top - Hiển thị bảng xếp hạng"""
    if not user_money:
        await update.message.reply_text("📌 **Chưa có ai chơi!**")
        return

    sorted_users = sorted(user_money.items(), key=lambda x: x[1], reverse=True)[:10]
    top_text = "🏆 *BẢNG XẾP HẠNG ĐẠI GIA* 🏆\n"
    medals = ["🥇", "🥈", "🥉"] + ["🎖️"] * 7

    for i, (user_id, balance) in enumerate(sorted_users):
        top_text += f"{medals[i]} *User {user_id}* ─ 💵 *{balance:,} VNĐ*\n"

    await update.message.reply_text(top_text, parse_mode="Markdown")

async def taixiu(update: Update, context: CallbackContext):
    """Lệnh /taixiu - Chơi tài xỉu với hiệu ứng xúc xắc"""
    user_id = str(update.message.from_user.id)

    # Kiểm tra nếu chưa đăng ký
    if user_id not in user_money:
        await update.message.reply_text("⚠️ Bạn chưa đăng ký! Hãy dùng /dangky trước.")
        return

    # Kiểm tra cú pháp lệnh
    if len(context.args) < 2:
        await update.message.reply_text("📌 **Cú pháp:** /taixiu <tài/xỉu> <số tiền hoặc 'all'>")
        return

    bet_choice = context.args[0].lower()
    bet_amount = context.args[1]

    if bet_choice not in ["tài", "xỉu"]:
        await update.message.reply_text("❌ Bạn chỉ có thể chọn 'tài' hoặc 'xỉu'.")
        return

    # Xử lý số tiền cược
    balance = user_money.get(user_id, 0)
    if bet_amount == "all":
        bet_amount = balance
    else:
        try:
            bet_amount = int(bet_amount)
            if bet_amount <= 0:
                raise ValueError
        except ValueError:
            await update.message.reply_text("❌ Số tiền cược không hợp lệ!")
            return

    if bet_amount > balance:
        await update.message.reply_text("❌ Bạn không có đủ tiền để cược!")
        return

    # Hiệu ứng tung xúc xắc
    dice_results = []
    total_points = 0
    for _ in range(3):
        msg = await update.message.reply_dice(emoji="🎲")
        dice_value = msg.dice.value
        dice_results.append(dice_value)
        total_points += dice_value
        await asyncio.sleep(3)  # Đợi hiệu ứng tung xúc xắc

    # Xác định kết quả
    result = "tài" if total_points >= 11 else "xỉu"
    win = result == bet_choice

    # Cập nhật số dư
    if win:
        winnings = bet_amount * 2
        user_money[user_id] += bet_amount
        result_text = f"🎉 **Bạn thắng!** +{bet_amount:,} VNĐ\n💰 Số dư mới: {user_money[user_id]:,} VNĐ"
    else:
        user_money[user_id] -= bet_amount
        result_text = f"😢 **Bạn thua!** -{bet_amount:,} VNĐ\n💰 Số dư mới: {user_money[user_id]:,} VNĐ"

    save_balance()

    # Gửi kết quả
    await update.message.reply_text(
        f"🎲 **Kết quả:** {dice_results} = {total_points} ({result.upper()})\n{result_text}",
        parse_mode="Markdown"
    )

    
async def main():
    app = Application.builder().token(BOT_CONFIG["TOKEN"]).build()
    app.add_handler(CommandHandler("dangky", dangky))
    app.add_handler(CommandHandler("sodu", sodu))
    app.add_handler(CommandHandler("code", code))
    app.add_handler(CommandHandler("codevip", codevip))
    app.add_handler(CommandHandler("admoney", admoney))
    app.add_handler(CommandHandler("top", top))
    app.add_handler(CommandHandler("menu", menu))
    app.add_handler(CommandHandler("taixiu", taixiu))

    print("🤖 Bot đang chạy...")
    await app.initialize()
    await app.start()
    await send_welcome_message(app)
    await app.updater.start_polling()
    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(main())