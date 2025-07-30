import gspread
from telegram import Update, InputMediaPhoto
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters
from oauth2client.service_account import ServiceAccountCredentials

# Telegram Token
TOKEN = "8209077922:AAHGQzOji8MuEDra50-NLuWr_yeBR1_sUro"
# Google Sheets setup
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
client = gspread.authorize(creds)
sheet = client.open_by_url("https://docs.google.com/spreadsheets/d/1O_xtxhWxRcg-rKU7cHODjoxro_B7rIL30SReqa5SDBw").worksheet("Table 1")

# Main bot logic
async def reply_with_product(update: Update, context: ContextTypes.DEFAULT_TYPE):
    code = update.message.text.strip()

    rows = sheet.get_all_records(expected_headers=[
        "OFFER", "Price", "name", "SKU Code", "Price after discount",
        "photo1", "photo2", "photo3", "photo4", "photo5",
        "materials", "size"
    ])

    for row in rows:
        if str(row["SKU Code"]).strip() == code:
            name = row.get("name", "").strip() or "بدون اسم"
            price = str(row.get("Price", "")).strip()
            price_after = str(row.get("Price after discount", "")).strip()
            offer = row.get("OFFER", "").strip()
            materials = row.get("materials", "").strip()
            size = row.get("size", "").strip()

            # الصور
            photo_fields = ["photo1", "photo2", "photo3", "photo4", "photo5"]
            images = [str(row.get(field, "")).strip() for field in photo_fields]
            images = [img for img in images if img.startswith("http")]

            if not images:
                await update.message.reply_text(
                    f"📦 المنتج: {name}\n💰 السعر قبل الخصم: {price} جنيه\n💸 السعر بعد الخصم: {price_after} جنيه\n🎁 العرض: {offer}\n⚠️ لا توجد صور متاحة حالياً للمنتج."
                )
                return

            # بناء الرسالة
            caption_lines = [f"📦 المنتج: {name}"]
            if price:
                caption_lines.append(f"💰 السعر قبل الخصم: {price} جنيه")
            if price_after:
                caption_lines.append(f"🔥 السعر بعد الخصم: {price_after} جنيه")
            if offer:
                caption_lines.append(f"🎁 العرض: {offer}")
            if materials:
                caption_lines.append(f"🧵 الخامة: {materials}")
            if size:
                caption_lines.append(f"📏 المقاسات: {size}")

            caption = "\n".join(caption_lines)

            # إرسال الصور
            media = []
            for i, img in enumerate(images):
                if i == 0:
                    media.append(InputMediaPhoto(media=img, caption=caption))
                else:
                    media.append(InputMediaPhoto(media=img))

            await update.message.reply_media_group(media=media)
            return

    await update.message.reply_text("❌ الكود غير موجود. تأكد إنه مكتوب بشكل صحيح.")

# Run bot
app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, reply_with_product))
print("✅ Bot is running and waiting for messages...")
app.run_polling()
