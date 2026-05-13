import logging
import random
import nest_asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
import os

# --- CONFIGURATION ---
TOKEN = os.getenv("BOT_TOKEN")
nest_asyncio.apply()
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# --- QUESTIONS DATABASE ---
QUESTIONS = [
       {"q": "50. بماذا يُلقَّب موقع جرش الأثري؟", "options": ["مدينة الورود", "بومبي الشرق", "ثغر الأردن", "وادي القمر"], "correct": 1},
    {"q": "51. ما اسم الشعب الذي بنى مدينة البتراء قديماً؟", "options": ["العمونيون", "المؤابيون", "الأنباط", "الأدوميون"], "correct": 2},
    {"q": "52. في أي مدينة أردنية توجد قلعة الكرك؟", "options": ["عجلون", "مادبا", "الكرك", "الشوبك"], "correct": 2},
    {"q": "53. في أي عام أُدرجت البتراء ضمن عجائب الدنيا السبع الجديدة؟", "options": ["2000", "2005", "2007", "2010"], "correct": 2},
    {"q": "54. ما اسم الموقع الأثري الروماني الذي يحتوي على أعمدة هرقل؟", "options": ["جرش", "أم قيس", "قلعة عمّان", "طبقة فحل"], "correct": 2},
    {"q": "55. ما اسم المدينة الأثرية الرومانية التي تقع شمال الأردن وتشتهر بشارعها المعمود؟", "options": ["البتراء", "جرش", "العقبة", "أم الرصاص"], "correct": 1},
    {"q": "56. في أي قرن بُنيت قلعة الكرك؟", "options": ["القرن العاشر", "القرن الحادي عشر", "القرن الثاني عشر الميلادي", "القرن الثالث عشر"], "correct": 2},
    {"q": "57. ما اسم الموقع الديني الذي يُعتقد أنه مدفن النبي موسى عليه السلام؟", "options": ["جبل عجلون", "جبل نيبو", "جبل شيحان", "جبل التحكيم"], "correct": 1},
    {"q": "58. في أي محافظة يقع جبل نيبو؟", "options": ["عمّان", "الكرك", "مادبا", "البلقاء"], "correct": 2},
    {"q": "59. أي مدينة أردنية تحتوي على مسرح روماني لا يزال يُستخدم حتى اليوم؟", "options": ["إربد", "السلط", "عمّان", "معان"], "correct": 2},
    {"q": "60. كم يسع المسرح الروماني في عمّان من المتفرجين؟", "options": ["3000 متفرج", "حوالي 6000 متفرج", "10000 متفرج", "15000 متفرج"], "correct": 1},
    {"q": "61. في أي عام أُدرج موقع المغطس على قائمة التراث العالمي لليونسكو؟", "options": ["2010", "2015", "2018", "2020"], "correct": 1},
    {"q": "62. ما المدينة الأردنية التي كانت عاصمة للأنباط؟", "options": ["جرش", "البتراء", "مادبا", "أم قيس"], "correct": 1},
    {"q": "63. أي مدينة أردنية كانت تُعرف باسم جدارا؟", "options": ["بيت رأس", "قويلبة", "أم قيس", "طبقة فحل"], "correct": 2},
    {"q": "64. أي حضارة بنت مدينة جرش القديمة؟", "options": ["الحضارة اليونانية", "الحضارة الرومانية", "الحضارة الأنباط", "الحضارة الفارسية"], "correct": 1},
    {"q": "65. أي حضارة قديمة اشتهرت ببناء مدينة البتراء؟", "options": ["الرومان", "الغساسنة", "الأنباط", "البيزنطيون"], "correct": 2},
    {"q": "66. ما اسم أكبر سد في الأردن؟", "options": ["سد الوحدة", "سد الملك طلال", "سد الكرامة", "سد وادي العرب"], "correct": 0}
]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_name = update.effective_user.first_name
    await update.message.reply_text(
        f"مرحباً بك {user_name} في مسابقة معالم أثرية في الأردنّ 🇯🇴\n\n"
        "اضغط /quiz للبدء باختبار معلوماتك!"
    )

async def send_question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Pick a random question from the entire list
    random_idx = random.randint(0, len(QUESTIONS) - 1)
    q_data = QUESTIONS[random_idx]
    
    context.user_data['current_q_idx'] = random_idx

    # Create buttons for options
    keyboard = [[InlineKeyboardButton(opt, callback_data=f"ans_{i}")] for i, opt in enumerate(q_data['options'])]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    text = f"سؤال المعالم الأثرية:\n\n{q_data['q']}"
    
    # If called from a button, edit the message; if from /quiz, send new
    if update.callback_query:
        await update.callback_query.edit_message_text(text=text, reply_markup=reply_markup)
    else:
        await update.message.reply_text(text, reply_markup=reply_markup)

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data.startswith("ans_"):
        selected = int(data.replace("ans_", ""))
        q_idx = context.user_data.get('current_q_idx')
        
        correct = QUESTIONS[q_idx]['correct']
        
        if selected == correct:
            result_text = "✅ إجابة صحيحة! أحسنت."
        else:
            ans_text = QUESTIONS[q_idx]['options'][correct]
            result_text = f"❌ إجابة خاطئة.\nالصحيح هو: {ans_text}"

        # Show result and button for next question
        keyboard = [[InlineKeyboardButton("سؤال آخر 🔄", callback_data="next_question")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            text=f"السؤال: {QUESTIONS[q_idx]['q']}\n\n{result_text}",
            reply_markup=reply_markup
        )

    elif data == "next_question":
        await send_question(update, context)

def main():
    app = Application.builder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("quiz", send_question))
    app.add_handler(CallbackQueryHandler(handle_callback))
    
    print("البوت يعمل الآن... جرب إرسال /quiz")
    app.run_polling(close_loop=False)

if __name__ == '__main__':
    main()
