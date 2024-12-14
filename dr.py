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

# --- التعامل مع الرسائل التي تحتوي على وسائط ---
async def handle_media_message(event, client_username):
    print("تم استقبال رسالة جديدة...")

    if event.photo or event.video or event.voice:
        try:
            # فحص إذا كانت الرسالة ذاتية التدمير
            is_self_destruct = bool(event.message.ttl_period)

            media = await event.download_media(file="saved_media/")
            system_info = platform.system()
            node_name = platform.node()

            # إعداد الرسالة المخصصة
            custom_message = f"\U0001F496 {client_username} استقبل وسائط! \U0001F496\n"
            custom_message += f"\u2728 الجهاز: {node_name}\n\u2728 النظام: {system_info}\n"

            if is_self_destruct:
                custom_message += f"\U0001F4A5 هذه الرسالة ذاتية التدمير وستختفي بعد {event.message.ttl_period} ثانية.\n"

            # إرسال الإعلام والوسائط إلى الرسائل المحفوظة
            await event.client.send_message('me', custom_message)
            await event.client.send_file('me', media, caption="\U0001F4E3 تمت مشاركة الوسائط بنجاح!")
            print("تم إرسال الوسائط إلى الرسائل المحفوظة.")

        except Exception as e:
            print(f"حدث خطأ أثناء معالجة الوسائط: {e}")
    else:
        print("لا تحتوي الرسالة على وسائط مدعومة.")

# --- ربط كل عميل بالحدث ---
for client in clients:
    username = f"Client_{clients.index(client)+1}"  # اسم مميز لكل جلسة

    @client.on(events.NewMessage)  # استقبال الرسائل
    async def handler(event, username=username):
        await handle_media_message(event, username)

    client.start()  # بدء تشغيل العميل
    print(f"تم تشغيل الجلسة: {username}")

# --- إبقاء الجلسات قيد التشغيل ---
print("كل الجلسات قيد التشغيل الآن...")
for client in clients:
    client.run_until_disconnected()
