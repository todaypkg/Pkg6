import os
from telethon import TelegramClient, events
from telethon.sessions import StringSession
from telethon.tl.types import Message

# --- إعداد متغيرات البيئة ---
api_id = int(os.getenv("API_ID"))  # معرف API من تيليجرام
api_hash = os.getenv("API_HASH")   # API Hash من تيليجرام
bot_token = os.getenv("BOT_TOKEN") # توكن البوت من متغير البيئة
session_string = os.getenv("dr")  # الجلسة المخزنة في Heroku باسم dr

# --- إنشاء عميل Telethon باستخدام الجلسة المخزنة ---
try:
    client = TelegramClient(StringSession(session_string), api_id, api_hash)
except Exception as e:
    print(f"❌ فشل في تحميل الجلسة: {e}")
    exit()

# --- إعداد مجلد الحفظ ---
os.makedirs("saved_content", exist_ok=True)

# --- الرد على أمر /start ---
@client.on(events.NewMessage(pattern='/start'))
async def start(event):
    # إرسال رسالة ترحيبية وطلب الرابط
    await event.reply("مرحبًا! أرسل لي رابط منشور من تيليجرام لأقوم بحفظه وإرساله لك.")

# --- التعامل مع الروابط ---
@client.on(events.NewMessage)
async def handle_link(event):
    if event.message.text.startswith('/start'):
        return  # إذا كان الأمر /start، لا نحتاج لمعالجة رابط

    try:
        # استخراج الرابط من الرسالة
        link = event.message.text.strip()

        if "t.me/" not in link:
            await event.reply("❌ الرجاء إرسال رابط صالح من تيليجرام.")
            return
        
        # استخراج معلومات المنشور
        try:
            channel_username = link.split("/")[-2]
            message_id = int(link.split("/")[-1])

            # جلب المنشور باستخدام TelegramClient
            post = await client.get_messages(channel_username, ids=message_id)

            if not post:
                await event.reply("❌ لم أستطع العثور على المنشور.")
                return

            # حفظ الوسائط أو النصوص
            if post.media:
                file_path = await client.download_media(post, file="saved_content/")
                # إعادة إرسال الوسائط عبر البوت
                await event.client.send_file(event.chat_id, file_path, caption="تم حفظ الوسائط بنجاح!")
                await event.reply("✅ تم حفظ الوسائط وإرسالها بنجاح!")
            else:
                # حفظ النصوص في ملف
                text_content = f"📅 التاريخ: {post.date}\n👤 المرسل: {post.sender_id}\n💬 النص:\n{post.text}\n\n"
                with open("saved_content/saved_texts.txt", "a", encoding="utf-8") as f:
                    f.write(text_content)
                # إعادة إرسال النصوص عبر البوت
                await event.client.send_message(event.chat_id, "تم حفظ النص التالي:\n\n" + post.text)
                await event.reply("✅ تم حفظ النص وإرساله بنجاح!")
        
        except Exception as e:
            await event.reply(f"❌ حدث خطأ أثناء معالجة الرابط: {e}")

    except Exception as e:
        await event.reply(f"❌ حدث خطأ غير متوقع: {e}")

# --- بدء الجلسة ---
try:
    print("✅ البوت يعمل الآن ...")
    client.start(bot_token=bot_token)
    client.run_until_disconnected()
except Exception as e:
    print(f"❌ فشل في بدء الجلسة: {e}")
