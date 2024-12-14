import os
import platform
from telethon import TelegramClient, events
from telethon.sessions import StringSession

# --- إعداد متغيرات Heroku ---
api_id = int(os.getenv("API_ID"))  # API_ID المخزن في Heroku
api_hash = os.getenv("API_HASH")   # API_HASH المخزن في Heroku
sessions = os.getenv("SESSIONS").split(",")  # قائمة String Sessions مفصولة بفواصل

# --- التأكد من وجود مجلد لحفظ الوسائط ---
os.makedirs("saved_media", exist_ok=True)

# --- إنشاء قائمة العملاء ---
clients = []
for session in sessions:
    client = TelegramClient(StringSession(session), api_id, api_hash)
    clients.append(client)

# --- التعامل مع الرسائل ذاتية التدمير فقط ---
async def handle_self_destruct_message(event, client_username):
    print("تم استقبال رسالة جديدة...")
    if event.photo or event.video or event.document:
        # التحقق من أن الرسالة ذاتية التدمير عبر `ttl_period`
        if event.message.ttl_period:
            print(f"تم الكشف عن رسالة ذاتية التدمير بـ ttl_period: {event.message.ttl_period}")
            try:
                media = await event.download_media(file="saved_media/")
                system_info = platform.system()
                node_name = platform.node()

                # إعداد الرسالة المخصصة
                custom_message = f"\U0001F4A5 {client_username} استقبل رسالة ذاتية التدمير! \U0001F4A5\n"
                custom_message += f"\u2728 الجهاز: {node_name}\n\u2728 النظام: {system_info}\n"
                custom_message += f"الرسالة ستُدمر بعد {event.message.ttl_period} ثانية."

                # إرسال الإعلام إلى الرسائل المحفوظة
                await event.respond(custom_message)
                print("تم إرسال الرسالة المخصصة.")

                await event.reply(file=media, caption="\U0001F4F8 تم التقاط الرسالة ذاتية التدمير!")
                print("تم إرسال الوسائط إلى الرسائل المحفوظة.")

            except Exception as e:
                print(f"حدث خطأ أثناء معالجة الوسائط: {e}")
        else:
            print("هذه الرسالة ليست ذاتية التدمير.")

# --- ربط كل عميل بالحدث ---
for client in clients:
    username = f"Client_{clients.index(client)+1}"  # اسم مميز لكل جلسة

    @client.on(events.NewMessage)  # استقبال الرسائل
    async def handler(event, username=username):
        await handle_self_destruct_message(event, username)

    client.start()  # بدء تشغيل العميل
    print(f"تم تشغيل الجلسة: {username}")

# --- إبقاء الجلسات قيد التشغيل ---
print("كل الجلسات قيد التشغيل الآن...")
for client in clients:
    client.run_until_disconnected()
