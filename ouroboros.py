from telegram import (Update, Bot,
            InlineKeyboardMarkup, InlineKeyboardButton)
from telegram.ext import (Application, CommandHandler, filters,
            ConversationHandler, MessageHandler,
            CallbackQueryHandler, CallbackContext)
from dotenv import load_dotenv
from connection.SQL_db import engine
from connection.twillo_connection import send_otp
from models import Base
import os, random, logging, uuid, database as db, pandas as pd


# Logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logging.getLogger("httpx").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)

# get token
load_dotenv("./connection/credentials.env")
token = os.getenv('TELEGRAM_TOKEN')
bot = Bot(token)

# Sending Personal Message
async def send_message_user(chat_id, message):
    try:
        await bot.send_message(chat_id=chat_id, message=message)
    except:
        return ConversationHandler.END

### Code for Each Commands Starts Here

# ------------------------------------------------------------------------------------------------
# Start Conversation
START_ID_INPUT, START_OTP_INPUT = range(0, 2)

async def start(update: Update, context: CallbackContext):
    try:
        await update.message.reply_text("Hello, I am Ouroboros Bot")
        await update.message.reply_text("I will be helping you for registering a complaint, query.")
        user_id = str(update.message.chat_id)
        context.user_data["user_id"] = user_id
        if db.check_verfiy(user_id):
            user = db.get_user(user_id)
            await update.message.reply_text(f"Welcome {user.name} to Ouroboros Bot!\
                \nPlease enter command /help for more information")
            return ConversationHandler.END
        else:
            await update.message.reply_text("Oops! I guess you are not registered yet.")
            await update.message.reply_text("Please enter your ID:")
            return START_ID_INPUT
    except Exception as e:
        return ConversationHandler.END

async def handle_id(update: Update, context: CallbackContext):
    try:
        id = str(update.message.text).strip().upper()
        user = db.get_user_by_id(id)
        if user is None:
            await update.message.reply_text("Invalid ID. Please enter a valid ID:")
            return START_ID_INPUT
        else:
            context.user_data['id'] = id
            otp = "".join(str(random.randrange(10)) for _ in range(6))
            db.add_verify_code(id=id, user_id=context.user_data['user_id'], code=otp)
            # print(otp)
            await send_otp(mobile=user.mobile, code=otp)
        await update.message.reply_text(f"Your ID is {id}. Please enter your OTP:")
        return START_OTP_INPUT
    except Exception as e:
        return ConversationHandler.END

async def handle_otp(update: Update, context: CallbackContext):
    try:
        user_otp = str(update.message.text).strip()
        user_id = context.user_data['user_id']

        if db.verify_code(user_id, user_otp):
            await update.message.reply_text("Your OTP is verified. You are successfully registered!")
            user = db.get_user(user_id)
            await update.message.reply_text(f"Welcome {user.name} to Ouroboros Bot!\
                \nPlease enter command /help for more information")
            return ConversationHandler.END
        else:
            await update.message.reply_text("Invalid OTP. Please enter a valid OTP:")
            return START_OTP_INPUT
    except Exception as e:
        return ConversationHandler.END

conversation_handler_start = ConversationHandler(
    name='start_conversation',
    entry_points=[CommandHandler('start', start)],
    states={
        START_ID_INPUT : [
            MessageHandler(filters.Regex("1[hH][kK][0-9]{2}[a-zA-Z]{2}[0-9]{3}"), handle_id),
            MessageHandler(filters.Regex("[0-9]{5}"), handle_id)
        ],
        START_OTP_INPUT : [
            MessageHandler(filters.Regex("[0-9]{6}"), handle_otp)
        ]
    },
    fallbacks=[CommandHandler('cancel', ConversationHandler.END)]
)


# ------------------------------------------------------------------------------------------------
# About Command Handler
async def about_handler(update:Update, context:CallbackContext):
    try:
        await update.message.reply_text("I am Ouroboros Bot, Department of CSE, HKBKCE")
        await update.message.reply_text("You can do a complaint directly to HoD, with full privacy and track updates on your registered complaint.")
        await update.message.reply_text("You can ask your doubts to your facutly or mentor, and track what is the status of your doubt solution.")
        await update.message.reply_text("Soon more updates will be given to bots...\
            \nPlease help us to improve by giving your feedback at /feedback.")
        await update.message.reply_text("For any help, use /help command.")
        return ConversationHandler.END
    except:
        return ConversationHandler.END


# ------------------------------------------------------------------------------------------------
# Help Command Handler
async def help_handler(update:Update, context:CallbackContext):
    try:
        user = db.get_user(str(update.message.chat_id))
        if user is None:
            await update.message.reply_text("Sorry, Can't find your information.")
            await update.message.reply_text("Please register yourself using /start command.")
            return ConversationHandler.END
        await update.message.reply_text("Here, are the list of commands which you can use to help yourself out.")
        if user.user_type == db.Account.student:
            await update.message.reply_text("You can use following commands to interact with me:")
            await update.message.reply_text("/me - To get your information")
            await update.message.reply_text("/about - To get information about me")
            await update.message.reply_text("/help - To get help related to commands")
            await update.message.reply_text("/complaint - To perform operation related to complaint")
            await update.message.reply_text("/query - To perform operation related to query")
            await update.message.reply_text("/feedback - To give feedback to developer")
        elif user.user_type == db.Account.teacher:
            await update.message.reply_text("You can use following commands to interact with me:")
            await update.message.reply_text("/me - To get your information")
            await update.message.reply_text("/about - To get information about me")
            await update.message.reply_text("/help - To get help related to commands")
            await update.message.reply_text("/query - To perform operation related to query")
            await update.message.reply_text("/feedback - To give feedback to developer")
        elif user.user_type == db.Account.admin:
            await update.message.reply_text("You can use following commands to interact with me:")
            await update.message.reply_text("/me - To get your information")
            await update.message.reply_text("/about - To get information about me")
            await update.message.reply_text("/help - To get help related to commands")
            await update.message.reply_text("/user - To access & Manipulate user information")
            await update.message.reply_text("/complaint - To perform operation related to complaint")
            await update.message.reply_text("/query - To perform operation related to query")
            await update.message.reply_text("/feedback - To give feedback to developer")
        return ConversationHandler.END
    except Exception as e:
        return ConversationHandler.END


# ------------------------------------------------------------------------------------------------
# Me Command Handler
async def me_handler(update:Update, context:CallbackContext):
    try:
        user = db.get_user(str(update.message.chat_id))
        if user is None:
            await update.message.reply_text("Sorry, Can't find your information.")
            await update.message.reply_text("Please register yourself using /start command.")
            return ConversationHandler.END
        await update.message.reply_text("Here, is what I got information about you")
        if user.user_type == db.Account.student:
            student, user = db.get_student(str(update.message.chat_id))
            await update.message.reply_text(f"Student's:\
                \n Name: {user.name}\
                \n ID: {user.id}\
                \n Mobile: {user.mobile}\
                \n Level: {user.user_type}\
                \n Semester: {student.sem}\
                \n Section: {student.sec}")
        elif user.user_type == db.Account.teacher:
            teacher, user = db.get_teacher(str(update.message.chat_id))
            await update.message.reply_text(f"Teacher's:\
                \n Name: {user.name}\
                \n ID: {user.id}\
                \n Mobile: {user.mobile}\
                \n Level: {user.user_type}\
                \n Branch: {teacher.branch}")
        elif user.user_type == db.Account.admin:
            await update.message.reply_text(f"Administrator's:\
                \n Name: {user.name}\
                \n ID: {user.id}\
                \n Mobile: {user.mobile}\
                \n Level: {user.user_type}")
        return ConversationHandler.END
    except Exception as e:
        return ConversationHandler.END


# ------------------------------------------------------------------------------------------------
# User Command Handler
USER_TYPE_OPTION, USER_STUD_OPTION, USER_TEACH_OPTION= range(2, 5)
STUD_ADD, STUD_UPDATE, STUD_CHANGE, STUD_DELETE = range(5, 9)
TEACH_ADD, TEACH_UPDATE, TEACH_CHANGE, TEACH_DELETE = range(9, 13)

async def admin_user(update: Update, context:CallbackContext):
    try:
        user = db.get_user(str(update.message.chat_id))
        if user is None:
            await update.message.reply_text("Sorry, Can't find your information.")
            await update.message.reply_text("Please register yourself using /start command.")
            return ConversationHandler.END
        if user.user_type != db.Account.admin:
            await update.message.reply_text("Sorry, You are not authorized to access this command.")
            return ConversationHandler.END
        keyboard = [
            [InlineKeyboardButton(text='Students', callback_data='student')],
            [InlineKeyboardButton(text='Faculty', callback_data='teacher')],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text("Please Select User Type:", reply_markup=reply_markup)
        return USER_TYPE_OPTION
    except Exception as e:
        return ConversationHandler.END

async def handle_user_type_option(update: Update, context: CallbackContext):
    try:
        context.user_data["option"] = str(update.callback_query.data)
        query = update.callback_query
        if context.user_data["option"] == "student":
            keyboard = [
                [InlineKeyboardButton(text="Add Student", callback_data="add")],
                [InlineKeyboardButton(text="Update Student", callback_data="update")],
                [InlineKeyboardButton(text="Promote Student", callback_data="promote")],
                [InlineKeyboardButton(text="Demote Student", callback_data="demote")],
                [InlineKeyboardButton(text="Delete Student", callback_data="delete")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text("Please Select Operation:")
            await query.edit_message_reply_markup(reply_markup=reply_markup)
            return USER_STUD_OPTION

        elif context.user_data["option"] == "teacher":
            keyboard = [
                [InlineKeyboardButton(text="Add Faculty", callback_data="add")],
                [InlineKeyboardButton(text="Update Faculty", callback_data="update")],
                [InlineKeyboardButton(text="Promote Faculty", callback_data="promote")],
                [InlineKeyboardButton(text="Delete Faculty", callback_data="delete")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text("Please Select Operation:")
            await query.edit_message_reply_markup(reply_markup=reply_markup)
            return USER_TEACH_OPTION
    except Exception as e:
        return ConversationHandler.END

async def handle_user_stud_option(update: Update, context: CallbackContext):
    try:
        context.user_data["option"] = str(update.callback_query.data)
        query = update.callback_query
        if context.user_data["option"] == "add":
            await query.message.reply_text("Here is a template for adding student:")
            file = f"{os.getcwd()}/uploads/add_student.csv"
            await query.message.reply_document(document=open(file, "rb"), filename="add_student.csv")
            await query.message.reply_text("Please Keep the header row, and send the data in csv format")
            return STUD_ADD
        elif context.user_data["option"] == "update":
            await query.message.reply_text("Here is a template for updating student:")
            file = f"{os.getcwd()}/uploads/add_student.csv"
            await query.message.reply_document(document=open(file, "rb"), filename="update_student.csv")
            await query.message.reply_text("Please Keep the header row, and send the data in csv format")
            await query.message.reply_text("If you want to update only one field, then keep other fields empty")
            return STUD_UPDATE
        elif context.user_data["option"] == "promote":
            await query.message.reply_text("Here is a template for promoting students to next semester:")
            file = f"{os.getcwd()}/uploads/student.csv"
            await query.message.reply_document(document=open(file, "rb"), filename="promote_student.csv")
            await query.message.reply_text("Please Keep the header row, and send the data in csv format")
            await query.message.reply_text("If you want to promote only one student, then enter its usn:")
            return STUD_CHANGE
        elif context.user_data["option"] == "demote":
            await query.message.reply_text("Here is a template for demoting students to previous semester:")
            file = f"{os.getcwd()}/uploads/student.csv"
            await query.message.reply_document(document=open(file, "rb"), filename="demote_student.csv")
            await query.message.reply_text("Please Keep the header row, and send the data in csv format")
            await query.message.reply_text("If you want to demote only one student, then enter its usn:")
            return STUD_CHANGE
        elif context.user_data["option"] == "delete":
            await query.message.reply_text("Here is a template for deleting students to previous semester:")
            file = f"{os.getcwd()}/uploads/student.csv"
            await query.message.reply_document(document=open(file, "rb"), filename="promote_student.csv")
            await query.message.reply_text("Please Keep the header row, and send the data in csv format")
            await query.message.reply_text("If you want to delete only one student, then enter its usn:")
            return STUD_CHANGE
    except Exception as e:
        return ConversationHandler.END

async def handle_stud_add(update:Update, context:CallbackContext):
    try:
        document = update.message.document
        if document.mime_type != "text/comma-separated-values":
            await update.message.reply_text("Please send the data in csv format")
            return STUD_ADD
        else:
            file_path = f"{os.getcwd()}/uploads/student_data_{uuid.uuid4()}.csv"
            file = await context.bot.get_file(document)
            await file.download_to_drive(file_path)
            await update.message.reply_text("File is successfully uploaded!")
            usn = []
            data = pd.read_csv(file_path, delimiter=',')
            data.replace('', None, inplace=True)
            for index, row in data.iterrows():
                res = db.add_student(id=row['usn'], name=row['name'],
                            mobile=row['mobile'], sem=row['sem'], sec=row['sec'])
                if res is not None:
                    usn.append(res)
            if len(usn) > 0:
                users = ""
                for id in usn:
                    users += id + "\n"
                await update.message.reply_text(f"Data Not Uploaded for Student:\n{users}")
            else:
                await update.message.reply_text(f"All Students data added successfully")
            return ConversationHandler.END
    except Exception as e:
        print(e)
        return ConversationHandler.END

async def handle_stud_update(update:Update, context:CallbackContext):
    try:
        document = update.message.document
        if document.mime_type != "text/comma-separated-values":
            await update.message.reply_text("Please send the data in csv format")
            return STUD_ADD
        else:
            file_path = f"{os.getcwd()}/uploads/student_data_{uuid.uuid4()}.csv"
            file = await context.bot.get_file(document)
            await file.download_to_drive(file_path)
            await update.message.reply_text("File is successfully uploaded!")
            usn = []
            data = pd.read_csv(file_path, delimiter=',')
            data.replace('', None, inplace=True)
            for index, row in data.iterrows():
                res = await db.update_student(id=row['usn'], name=row['name'],
                            mobile=row['mobile'], sem=row['sem'], sec=row['sec'])
                if res is not None:
                    usn.append(res)
            if len(usn) > 0:
                users = ""
                for id in usn:
                    users += id + "\n"
                await update.message.reply_text(f"Data Not Updated for Student:\n{users}")
            else:
                await update.message.reply_text(f"All Students data updated successfully")
            return ConversationHandler.END
    except Exception as e:
        return ConversationHandler.END

async def handle_stud_change(update:Update, context:CallbackContext):
    try:
        student_id = str(update.message.text)
        if context.user_data["option"] == "promote":
            try:
                db.promote_student(student_id)
                await update.message.reply_text("Student is promoted to next sem")
            except Exception as e:
                await update.message.reply_text("Student is not promoted or passed out")
        elif context.user_data["option"] == "demote":
            try:
                db.demote_student(student_id)
                await update.message.reply_text("Student is demoted to previous sem")
            except Exception as e:
                await update.message.reply_text("Student is not admitted yet or not registered yet")
        return ConversationHandler.END
    except Exception as e:
        return ConversationHandler.END

async def handle_stud_change_csv(update:Update, context:CallbackContext):
    try:
        document = update.message.document
        if document.mime_type != "text/comma-separated-values":
            await update.message.reply_text("Please send the data in csv format")
            return STUD_ADD
        else:
            file_path = f"{os.getcwd()}/uploads/student_data_{uuid.uuid4()}.csv"
            file = await context.bot.get_file(document)
            await file.download_to_drive(file_path)
            await update.message.reply_text("File is successfully uploaded!")
            usn = []
            data = pd.read_csv(file_path, delimiter=',')
            data.replace('', None, inplace=True)
            if context.user_data["option"] == "promote":
                for index, row in data.iterrows():
                    try:
                        db.promote_student(row['usn'])
                    except Exception as e:
                        usn.append(row['usn'])
                if len(usn) > 0:
                    users = ""
                    for id in usn:
                        users += id + "\n"
                    await update.message.reply_text(f"These Students are not promoted:\n{users}")
                else:
                    await update.message.reply_text(f"All Students are successfully promoted")
            elif context.user_data["option"] == "demote":
                for index, row in data.iterrows():
                    try:
                        db.demote_student(row['usn'])
                    except Exception as e:
                        usn.append(row['usn'])
                if len(usn) > 0:
                    users = ""
                    for id in usn:
                        users += id + "\n"
                    await update.message.reply_text(f"These Students are not demoted:\n{users}")
                else:
                    await update.message.reply_text(f"All Students are successfully demoted")
            return ConversationHandler.END
    except Exception as e:
        return ConversationHandler.END

async def handle_stud_delete(update:Update, context:CallbackContext):
    try:
        student_id = str(update.message.text)
        db.delete_student(student_id)
        await update.message.reply_text("Student record is successfully deleted")
        return ConversationHandler.END
    except Exception as e:
        return ConversationHandler.END

async def handle_stud_delete_csv(update:Update, context:CallbackContext):
    try:
        document = update.message.document
        if document.mime_type != "text/comma-separated-values":
            await update.message.reply_text("Please send the data in csv format")
            return STUD_ADD
        else:
            file_path = f"{os.getcwd()}/uploads/student_data_{uuid.uuid4()}.csv"
            file = await context.bot.get_file(document)
            await file.download_to_drive(file_path)
            await update.message.reply_text("File is successfully uploaded!")
            usn = []
            data = pd.read_csv(file_path, delimiter=',')
            data.replace('', None, inplace=True)
            for index, row in data.iterrows():
                try:
                    db.delete_student(row['usn'])
                except Exception as e:
                    usn.append(row['usn'])
            if len(usn) > 0:
                users = ""
                for id in usn:
                    users += id + "\n"
                await update.message.reply_text(f"These Students data are not deleted:\n{users}")
            else:
                await update.message.reply_text(f"All Students data are successfully deleted")
            return ConversationHandler.END
    except Exception as e:
        return ConversationHandler.END

async def handle_user_teach_option(update:Update, context:CallbackContext):
    try:
        context.user_data["option"] = str(update.callback_query.data)
        query = update.callback_query
        if context.user_data["option"] == "add":
            await query.message.reply_text("Here is a template for adding faculty:")
            file = f"{os.getcwd()}/uploads/add_teacher.csv"
            await query.message.reply_document(document=open(file, "rb"), filename="add_teacher.csv")
            await query.message.reply_text("Please Keep the header row, and send the data in csv format")
            return TEACH_ADD
        elif context.user_data["option"] == "update":
            await query.message.reply_text("Here is a template for updating faculty:")
            file = f"{os.getcwd()}/uploads/add_teacher.csv"
            await query.message.reply_document(document=open(file, "rb"), filename="update_teacher.csv")
            await query.message.reply_text("Please Keep the header row, and send the data in csv format")
            await query.message.reply_text("If you want to update only one field, then keep other fields empty")
            return TEACH_UPDATE
        elif context.user_data["option"] == "promote":
            await query.message.reply_text("Here is a template for promoting faculty to next semester:")
            file = f"{os.getcwd()}/uploads/teacher.csv"
            await query.message.reply_document(document=open(file, "rb"), filename="promote_teacher.csv")
            await query.message.reply_text("Please Keep the header row, and send the data in csv format")
            await query.message.reply_text("If you want to promote only one faculty, then enter its usn:")
            return TEACH_CHANGE
        elif context.user_data["option"] == "delete":
            await query.message.reply_text("Here is a template for deleting faculty to previous semester:")
            file = f"{os.getcwd()}/uploads/teacher.csv"
            await query.message.reply_document(document=open(file, "rb"), filename="promote_teacher.csv")
            await query.message.reply_text("Please Keep the header row, and send the data in csv format")
            await query.message.reply_text("If you want to delete only one faculty, then enter its usn:")
            return TEACH_CHANGE
    except Exception as e:
        return ConversationHandler.END

async def handle_teach_add(update:Update, context:CallbackContext):
    try:
        document = update.message.document
        if document.mime_type != "text/comma-separated-values":
            await update.message.reply_text("Please send the data in csv format")
            return TEACH_ADD
        else:
            file_path = f"{os.getcwd()}/uploads/teacher_data_{uuid.uuid4()}.csv"
            file = await context.bot.get_file(document)
            await file.download_to_drive(file_path)
            await update.message.reply_text("File is successfully uploaded!")
            staff = []
            data = pd.read_csv(file_path, delimiter=',')
            data.replace('', None, inplace=True)
            for index, row in data.iterrows():
                res = await db.add_teacher(id=row['staff_id'], name=row['name'],
                            mobile=row['mobile'], branch=row['branch'])
                if res is not None:
                    staff.append(res)
            if len(staff) > 0:
                users = ""
                for id in staff:
                    users += id + "\n"
                await update.message.reply_text(f"Data Not Uploaded for Faculty ID:\n{users}")
            else:
                await update.message.reply_text(f"All Faculties data added successfully")
            return ConversationHandler.END
    except Exception as e:
        return ConversationHandler.END

async def handle_teach_update(update:Update, context:CallbackContext):
    try:
        document = update.message.document
        if document.mime_type != "text/comma-separated-values":
            await update.message.reply_text("Please send the data in csv format")
            return TEACH_ADD
        else:
            file_path = f"{os.getcwd()}/uploads/teacher_data_{uuid.uuid4()}.csv"
            file = await context.bot.get_file(document)
            await file.download_to_drive(file_path)
            await update.message.reply_text("File is successfully uploaded!")
            staff = []
            data = pd.read_csv(file_path, delimiter=',')
            data.replace('', None, inplace=True)
            for index, row in data.iterrows():
                res = await db.update_teacher(id=row['staff_id'], name=row['name'],
                            mobile=row['mobile'], branch=row['branch'])
                if res is not None:
                    staff.append(res)
            if len(staff) > 0:
                users = ""
                for id in staff:
                    users += id + "\n"
                await update.message.reply_text(f"Data Not Updated for Faculty ID:\n{users}")
            else:
                await update.message.reply_text(f"All Faculties data updated successfully")
            return ConversationHandler.END
    except Exception as e:
        return ConversationHandler.END

async def handle_teach_change(update:Update, context:CallbackContext):
    try:
        staff_id = str(update.message.text)
        if context.user_data["option"] == "promote":
            try:
                db.promote_teacher(staff_id)
                await update.message.reply_text("Faculty is promoted to admin")
            except Exception as e:
                await update.message.reply_text("Faculty cannot be promoted to admin")
        return ConversationHandler.END
    except Exception as e:
        return ConversationHandler.END

async def handle_teach_change_csv(update:Update, context:CallbackContext):
    try:
        document = update.message.document
        if document.mime_type != "text/comma-separated-values":
            await update.message.reply_text("Please send the data in csv format")
            return TEACH_ADD
        else:
            file_path = f"{os.getcwd()}/uploads/teacher_data_{uuid.uuid4()}.csv"
            file = await context.bot.get_file(document)
            await file.download_to_drive(file_path)
            await update.message.reply_text("File is successfully uploaded!")
            staff = []
            data = pd.read_csv(file_path, delimiter=',')
            data.replace('', None, inplace=True)
            if context.user_data["option"] == "promote":
                for index, row in data.iterrows():
                    try:
                        db.promote_teacher(row['staff_id'])
                    except Exception as e:
                        staff.append(row['staff_id'])
                if len(staff) > 0:
                    users = ""
                    for id in staff:
                        users += id + "\n"
                    await update.message.reply_text(f"These Faculty are not promoted:\n{users}")
                else:
                    await update.message.reply_text(f"All Faculties are successfully promoted")
            return ConversationHandler.END
    except Exception as e:
        return ConversationHandler.END

async def handle_teach_delete(update:Update, context:CallbackContext):
    try:
        staff_id = str(update.message.text)
        db.delete_teacher(staff_id)
        await update.message.reply_text("Faculty record is successfully deleted")
        return ConversationHandler.END
    except:
        return ConversationHandler.END

async def handle_teach_delete_csv(update:Update, context:CallbackContext):
    try:
        document = update.message.document
        if document.mime_type != "text/comma-separated-values":
            await update.message.reply_text("Please send the data in csv format")
            return TEACH_ADD
        else:
            file_path = f"{os.getcwd()}/uploads/teacher_data_{uuid.uuid4()}.csv"
            file = await context.bot.get_file(document)
            await file.download_to_drive(file_path)
            await update.message.reply_text("File is successfully uploaded!")
            staff = []
            data = pd.read_csv(file_path, delimiter=',')
            data.replace('', None, inplace=True)
            for index, row in data.iterrows():
                try:
                    db.delete_teacher(row['staff_id'])
                except Exception as e:
                    staff.append(row['staff_id'])
            if len(staff) > 0:
                users = ""
                for id in staff:
                    users += id + "\n"
                await update.message.reply_text(f"These Faculties data are not deleted:\n{users}")
            else:
                await update.message.reply_text(f"All Faculties data are successfully deleted")
            return ConversationHandler.END
    except Exception as e:
        return ConversationHandler.END

conversation_handler_user = ConversationHandler(
    name='user_conversation',
    entry_points=[CommandHandler('user', admin_user)],
    states={
        USER_TYPE_OPTION: [
            CallbackQueryHandler(handle_user_type_option)
        ],
        USER_STUD_OPTION: [
            CallbackQueryHandler(handle_user_stud_option)
        ],
        USER_TEACH_OPTION: [
            CallbackQueryHandler(handle_user_teach_option)
        ],
        STUD_ADD: [
            MessageHandler(filters.Document.MimeType("text/comma-separated-values"), handle_stud_add)
        ],
        STUD_UPDATE: [
            MessageHandler(filters.Document.MimeType("text/comma-separated-values"), handle_stud_update)
        ],
        STUD_CHANGE: [
            MessageHandler(filters.Regex(".*"), handle_stud_change),
            MessageHandler(filters.Document.MimeType("text/comma-separated-values"), handle_stud_change_csv)
        ],
        STUD_DELETE: [
            MessageHandler(filters.Regex(".*"), handle_stud_delete),
            MessageHandler(filters.Document.MimeType("text/comma-separated-values"), handle_stud_delete_csv)
        ],
        TEACH_ADD: [
            MessageHandler(filters.Document.MimeType("text/comma-separated-values"), handle_teach_add)
        ],
        TEACH_UPDATE: [
            MessageHandler(filters.Document.MimeType("text/comma-separated-values"), handle_teach_update)
        ],
        TEACH_CHANGE: [
            MessageHandler(filters.Regex(".*"), handle_teach_change),
            MessageHandler(filters.Document.MimeType("text/comma-separated-values"), handle_teach_change)
        ],
        TEACH_DELETE: [
            MessageHandler(filters.Regex(".*"), handle_teach_delete),
            MessageHandler(filters.Document.MimeType("text/comma-separated-values"), handle_teach_delete)
        ]
    },
    fallbacks=[
        CommandHandler('cancel', ConversationHandler.END)
    ]
)


# ------------------------------------------------------------------------------------------------
# Complaint Conversation
COMPLAINT_OPTION, COMPLAINT_ID, COMPLAINT_ACTION, COMPLAINT_SUBJECT, COMPLAINT_MESSAGE = range(13, 18)

async def complaint(update: Update, context: CallbackContext):
    try:
        user = db.get_user(str(update.message.chat_id))
        if user is None:
            await update.message.reply_text("Sorry, Can't find your information.")
            await update.message.reply_text("Please register yourself using /start command.")
            return ConversationHandler.END

        context.user_data["user"] = user.id
        context.user_data["role"] = user.user_type

        if user.user_type == db.Account.admin:
            keyboard = [
                [InlineKeyboardButton(text="All Complaints", callback_data="admin-all")],
                [InlineKeyboardButton(text="Unresolved Complaints", callback_data="admin-unresolved")],
                [InlineKeyboardButton(text="Resolved Complaints", callback_data="admin-resolved")],

            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.message.reply_text("Please Select Option:", reply_markup=reply_markup)
            return COMPLAINT_OPTION
        else:
            keyboard = [
                [InlineKeyboardButton(text="My Complaints", callback_data="user-all")],
                [InlineKeyboardButton(text="New Complaint", callback_data="user-new")],
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.message.reply_text("Please Select Option:", reply_markup=reply_markup)
            return COMPLAINT_OPTION
    except Exception as e:
        return ConversationHandler.END

async def handle_complaint_option(update: Update, context:CallbackContext):
    try:
        context.user_data["option"] = str(update.callback_query.data)
        if context.user_data["role"] == db.Account.admin:
            query = update.callback_query
            if context.user_data["option"] == "admin-all":
                complaints = db.get_complaints()
                keyboard = [
                    [InlineKeyboardButton(text=f"Subject: {complaint.subject}\nStatus:{complaint.status}",
                                        callback_data=complaint.id)]
                for complaint in complaints ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                if len(complaints) == 0:
                    await query.message.reply_text("No Complaints Found!")
                    return ConversationHandler.END
                else:
                    await query.edit_message_text("Please Select Complaint:")
                    await query.edit_message_reply_markup(reply_markup=reply_markup)
                    return COMPLAINT_ID

            elif context.user_data["option"] == "admin-unresolved":
                complaints = db.get_active_complaints()
                keyboard = [
                    [InlineKeyboardButton(text=f"Subject: {complaint.subject}\nStatus:{complaint.status}",
                                        callback_data=complaint.id)]
                for complaint in complaints ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                if len(complaints) == 0:
                    await query.message.reply_text("No Complaints Found!")
                    return ConversationHandler.END
                else:
                    await query.edit_message_text("Please Select Complaint:")
                    await query.edit_message_reply_markup(reply_markup=reply_markup)
                return COMPLAINT_ID

            elif context.user_data["option"] == "admin-resolved":
                complaints = db.get_resolved_complaints()
                keyboard = [
                    [InlineKeyboardButton(text=f"Subject: {complaint.subject}\nStatus:{complaint.status}",
                                        callback_data=complaint.id)]
                for complaint in complaints ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                if len(complaints) == 0:
                    await query.message.reply_text("No Complaints Found!")
                    return ConversationHandler.END
                else:
                    await query.edit_message_text("Please Select Complaint:")
                    await query.edit_message_reply_markup(reply_markup=reply_markup)
                return COMPLAINT_ID
        else:
            query = update.callback_query
            if context.user_data["option"] == "user-all":
                complaints = db.get_complaints(str(update.callback_query.message.chat_id))
                keyboard = [
                    [InlineKeyboardButton(text=f"Subject: {complaint.subject}\nStatus:{complaint.status}",
                                        callback_data=complaint.id)]
                for complaint in complaints ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                if len(complaints) == 0:
                    await query.message.reply_text("No Complaints Found!")
                    return ConversationHandler.END
                else:
                    await query.edit_message_text("Please Select Complaint:")
                    await query.edit_message_reply_markup(reply_markup=reply_markup)
                return COMPLAINT_ID

            elif context.user_data["option"] == "user-new":
                await update.callback_query.message.reply_text("Enter Subject for your Complaint:")
                return COMPLAINT_SUBJECT
    except Exception as e:
        return ConversationHandler.END

async def handle_complaint_id(update: Update, context: CallbackContext):
    try:
        context.user_data["complaint"] = db.get_complaint(int(str(update.callback_query.data)))
        user = db.get_user(str(update.callback_query.message.chat_id))
        if user is None:
            await update.callback_query.message.reply_text("Sorry, Can't find your information.")
            await update.callback_query.message.reply_text("Please register yourself using /start command.")
            return ConversationHandler.END
        if user.user_type == db.Account.admin:
            keyboard = [
                [InlineKeyboardButton(text=db.Status.raised, callback_data=db.Status.raised)],
                [InlineKeyboardButton(text=db.Status.rejected, callback_data=db.Status.rejected)],
                [InlineKeyboardButton(text=db.Status.inprogress, callback_data=db.Status.inprogress)],
                [InlineKeyboardButton(text=db.Status.resolved, callback_data=db.Status.resolved)],
                [InlineKeyboardButton(text=db.Status.delete, callback_data=db.Status.delete)]
            ]
        else:
            keyboard = [
                [InlineKeyboardButton(text=db.Status.raised, callback_data=db.Status.raised)],
                [InlineKeyboardButton(text=db.Status.delete, callback_data=db.Status.delete)]
            ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        message = f"Complaint:\
            \nComplaint ID: {context.user_data['complaint'].id}\
            \nComplaint Sender: {context.user_data['complaint'].user}\
            \nComplaint Subject: {context.user_data['complaint'].subject}\
            \nComplaint Description: {context.user_data['complaint'].description}\
            \nComplaint Status: {context.user_data['complaint'].status}"
        query = update.callback_query
        await query.edit_message_text(message)
        await query.edit_message_reply_markup(reply_markup=reply_markup)
        return COMPLAINT_ACTION
    except Exception as e:
        return ConversationHandler.END

async def handle_complaint_action(update: Update, context: CallbackContext):
    try:
        data = str(update.callback_query.data)
        user = db.get_user(str(update.callback_query.message.chat_id))
        if user is None:
            await update.callback_query.message.reply_text("Sorry, Can't find your information.")
            await update.callback_query.message.reply_text("Please register yourself using /start command.")
            return ConversationHandler.END
        if user.user_type == db.Account.admin:
            if data == db.Status.raised:
                db.update_complaint(context.user_data["complaint"].id, db.Status.raised)
                await update.callback_query.message.reply_text("Complaint Status is set to Raised!")
            elif data == db.Status.rejected:
                db.update_complaint(context.user_data["complaint"].id, db.Status.rejected)
                await update.callback_query.message.reply_text("Complaint Status is set to Rejected!")
            elif data == db.Status.inprogress:
                db.update_complaint(context.user_data["complaint"].id, db.Status.inprogress)
                await update.callback_query.message.reply_text("Complaint Status is set to In-Progress!")
            elif data == db.Status.resolved:
                db.update_complaint(context.user_data["complaint"].id, db.Status.resolved)
                await update.callback_query.message.reply_text("Complaint Status is set to Resolved!")
            elif data == db.Status.delete:
                db.delete_complaint(context.user_data["complaint"].id)
                await update.callback_query.message.reply_text("Complaint is deleted!")
        else:
            if data == db.Status.raised:
                db.update_complaint(context.user_data["complaint"].id, db.Status.raised)
                await update.callback_query.message.reply_text("Complaint Status is set to Raised!")
            elif data == db.Status.delete:
                db.delete_complaint(context.user_data["complaint"].id)
                await update.callback_query.message.reply_text("Complaint is deleted!")
        return ConversationHandler.END
    except Exception as e:
        return ConversationHandler.END

async def handle_complaint_subject(update: Update, context: CallbackContext):
    try:
        context.user_data["comp_subject"] = str(update.message.text)
        await update.message.reply_text("Please enter your complaint:")
        return COMPLAINT_MESSAGE
    except Exception as e:
        return ConversationHandler.END

async def handle_complaint_message(update: Update, context: CallbackContext):
    try:
        context.user_data["comp_message"] = str(update.message.text)
        user_id = str(update.message.chat_id)
        user = db.get_user(user_id)
        db.add_complaint(str(user.id), context.user_data["comp_subject"], context.user_data["comp_message"])
        await update.message.reply_text("Your complaint is successfully registered!")
        admin = db.get_admin()
        if admin:
            message = f"New Complaint Recieved\
                \nComplainer Name: {user.name}\
                \nComplainer ID: {user.id}\
                \nComplainer Level: {user.user_type}\
                \nComplaint Subject: {context.user_data['comp_subject']}\
                \nComplaint Message: {context.user_data['comp_message']}"
            send_message_user(admin.user_id, message)
            await update.message.reply_text("Your Complaint is sent to HoD!")
        return ConversationHandler.END
    except Exception as e:
        return ConversationHandler.END

conversation_handler_complaint = ConversationHandler(
    name='complaint_conversation',
    entry_points=[CommandHandler('complaint', complaint)],
    states={
        COMPLAINT_OPTION: [
            CallbackQueryHandler(handle_complaint_option)
        ],
        COMPLAINT_ACTION: [
            CallbackQueryHandler(handle_complaint_action)
        ],
        COMPLAINT_ID: [
            CallbackQueryHandler(handle_complaint_id)
        ],
        COMPLAINT_SUBJECT : [
            MessageHandler(filters.Regex(".*"), handle_complaint_subject)
        ],
        COMPLAINT_MESSAGE : [
            MessageHandler(filters.Regex(".*"), handle_complaint_message)
        ]
    },
    fallbacks=[
        CommandHandler('cancel', ConversationHandler.END)
    ]
)


# ------------------------------------------------------------------------------------------------
# Query Conversation
QUERY_OPTION, QUERY_ID, QUERY_ACTION, QUERY_FACULTY, QUERY_SUBJECT, QUERY_MESSAGE = range(18, 24)

async def query(update: Update, context: CallbackContext):
    try:
        user = db.get_user(str(update.message.chat_id))
        if user is None:
            await update.message.reply_text("Sorry, Can't find your information.")
            await update.message.reply_text("Please register yourself using /start command.")
            return ConversationHandler.END

        context.user_data["user"] = user.id
        context.user_data["role"] = user.user_type

        if user.user_type == db.Account.admin:
            keyboard = [
                [InlineKeyboardButton(text="All Queries", callback_data="admin-all")],
                [InlineKeyboardButton(text="Unresolved Queries", callback_data="admin-unresolved")],
                [InlineKeyboardButton(text="Resolved Queries", callback_data="admin-resolved")],
            ]
        elif user.user_type == db.Account.student:
            keyboard = [
                [InlineKeyboardButton(text="My Queries", callback_data="stud-all")],
                [InlineKeyboardButton(text="New Query", callback_data="stud-new")],
            ]
        elif user.user_type == db.Account.teacher:
            keyboard = [
                [InlineKeyboardButton(text="All Queries", callback_data="teach-all")],
                [InlineKeyboardButton(text="Unresolved Queries", callback_data="teach-unresolved")],
                [InlineKeyboardButton(text="Resolved Queries", callback_data="teach-resolved")],
            ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text("Please Select Option:", reply_markup=reply_markup)
        return QUERY_OPTION
    except Exception as e:
        return ConversationHandler.END

async def handle_query_option(update: Update, context:CallbackContext):
    try:
        context.user_data["option"] = str(update.callback_query.data)
        if context.user_data["role"] == db.Account.admin:
            query = update.callback_query
            if context.user_data["option"] == "admin-all":
                queries = db.get_queries()
                keyboard = [
                    [InlineKeyboardButton(text=f"Subject: {query.subject}\nStatus:{query.status}",
                                        callback_data=query.id)]
                for query in queries ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                if len(queries) == 0:
                    await query.message.reply_text("No Queries Found!")
                    return ConversationHandler.END
                else:
                    await query.edit_message_text("Please Select Query:")
                    await query.edit_message_reply_markup(reply_markup=reply_markup)

            elif context.user_data["option"] == "admin-unresolved":
                queries = db.get_active_queries()
                keyboard = [
                    [InlineKeyboardButton(text=f"Subject: {query.subject}\nStatus:{query.status}",
                                        callback_data=query.id)]
                for query in queries ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                if len(queries) == 0:
                    await query.message.reply_text("No Queries Found!")
                    return ConversationHandler.END
                else:
                    await query.edit_message_text("Please Select Query:")
                    await query.edit_message_reply_markup(reply_markup=reply_markup)

            elif context.user_data["option"] == "admin-resolved":
                queries = db.get_resolved_queries()
                keyboard = [
                    [InlineKeyboardButton(text=f"Subject: {query.subject}\nStatus:{query.status}",
                                        callback_data=query.id)]
                for query in queries ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                if len(queries) == 0:
                    await query.message.reply_text("No Queries Found!")
                    return ConversationHandler.END
                else:
                    await query.edit_message_text("Please Select Query:")
                    await query.edit_message_reply_markup(reply_markup=reply_markup)
            return QUERY_ID

        elif context.user_data["role"] == db.Account.teacher:
            query = update.callback_query
            if context.user_data["option"] == "teach-all":
                queries = db.get_queries(faculty=context.user_data["user"])
                keyboard = [
                    [InlineKeyboardButton(text=f"Subject: {query.subject}\nStatus:{query.status}",
                                        callback_data=query.id)]
                for query in queries ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                if len(queries) == 0:
                    await query.message.reply_text("No Queries Found!")
                    return ConversationHandler.END
                else:
                    await query.edit_message_text("Please Select Query:")
                    await query.edit_message_reply_markup(reply_markup=reply_markup)

            elif context.user_data["option"] == "teach-unresolved":
                queries = db.get_active_queries(faculty=context.user_data["user"])
                keyboard = [
                    [InlineKeyboardButton(text=f"Subject: {query.subject}\nStatus:{query.status}",
                                        callback_data=query.id)]
                for query in queries ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                if len(queries) == 0:
                    await query.message.reply_text("No Queries Found!")
                    return ConversationHandler.END
                else:
                    await query.edit_message_text("Please Select Query:")
                    await query.edit_message_reply_markup(reply_markup=reply_markup)

            elif context.user_data["option"] == "teach-resolved":
                queries = db.get_resolved_queries(faculty=context.user_data["user"])
                keyboard = [
                    [InlineKeyboardButton(text=f"Subject: {query.subject}\nStatus:{query.status}",
                                        callback_data=query.id)]
                for query in queries ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                if len(queries) == 0:
                    await query.message.reply_text("No Queries Found!")
                    return ConversationHandler.END
                else:
                    await query.edit_message_text("Please Select Query:")
                    await query.edit_message_reply_markup(reply_markup=reply_markup)
            return QUERY_ID

        elif context.user_data["role"] == db.Account.student:
            query = update.callback_query
            if context.user_data["option"] == "stud-all":
                queries = db.get_queries(user_id=context.user_data["user"])
                keyboard = [
                    [InlineKeyboardButton(text=f"Subject: {query.subject}\nStatus:{query.status}",
                                        callback_data=query.id)]
                for query in queries ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                if len(queries) == 0:
                    await query.message.reply_text("No Queries Found!")
                    return ConversationHandler.END
                else:
                    await query.edit_message_text("Please Select Query:")
                    await query.edit_message_reply_markup(reply_markup=reply_markup)

        elif context.user_data["option"] == "stud-new":
            await update.callback_query.message.reply_text("Please Select Faculty from the list:")
            teachers = db.get_all_verified_teachers()
            keyboard = [[InlineKeyboardButton(text=teacher.name, callback_data=teacher.id)] for teacher in teachers]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text("Please Select Faculty from the list:")
            await query.edit_message_reply_markup(reply_markup=reply_markup)
            return QUERY_FACULTY
        return QUERY_ID
    except Exception as e:
        return ConversationHandler.END

async def handle_query_id(update: Update, context:CallbackContext):
    try:
        context.user_data["query"] = db.get_query(int(str(update.callback_query.data)))
        user = db.get_user(str(update.callback_query.message.chat_id))
        if user is None:
            await update.callback_query.message.reply_text("Sorry, Can't find your information.")
            await update.callback_query.message.reply_text("Please register yourself using /start command.")
            return ConversationHandler.END

        if user.user_type == db.Account.admin or user.user_type == db.Account.teacher:
            keyboard = [
                [InlineKeyboardButton(text=db.Status.raised, callback_data=db.Status.raised)],
                [InlineKeyboardButton(text=db.Status.rejected, callback_data=db.Status.rejected)],
                [InlineKeyboardButton(text=db.Status.inprogress, callback_data=db.Status.inprogress)],
                [InlineKeyboardButton(text=db.Status.resolved, callback_data=db.Status.resolved)],
                [InlineKeyboardButton(text=db.Status.delete, callback_data=db.Status.delete)]
            ]
        elif user.user_type == db.Account.student:
            keyboard = [
                [InlineKeyboardButton(text=db.Status.raised, callback_data=db.Status.raised)],
                [InlineKeyboardButton(text=db.Status.delete, callback_data=db.Status.delete)]
            ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        student, user1 = db.get_student_detail(context.user_data["query"].user)
        teacher, user2 = db.get_teacher_detail(context.user_data["query"].faculty)
        message = f"Query:\
            \nQuery ID: {context.user_data['query'].id}\
            \nStudent Name: {user1.name}\
            \nStudent Semester: {student.sem}\
            \nStudent Section: {student.sec}\
            \nFaculty Name: {user2.name}\
            \nFaculty Branch: {teacher.branch}\
            \nQuery Subject: {context.user_data['query'].subject}\
            \nQuery Message: {context.user_data['query'].message}\
            \nQuery Status: {context.user_data['query'].status}"
        query = update.callback_query
        await query.edit_message_text(message)
        await query.edit_message_reply_markup(reply_markup=reply_markup)
        return QUERY_ACTION
    except Exception as e:
        return ConversationHandler.END

async def handle_query_action(update: Update, context: CallbackContext):
    try:
        data = str(update.callback_query.data)
        user = db.get_user(str(update.callback_query.message.chat_id))
        if user is None:
            await update.callback_query.message.reply_text("Sorry, Can't find your information.")
            await update.callback_query.message.reply_text("Please register yourself using /start command.")
            return ConversationHandler.END

        if user.user_type == db.Account.admin or user.user_type == db.Account.teacher:
            if data == db.Status.raised:
                db.update_query(context.user_data["query"].id, db.Status.raised)
                await update.callback_query.message.reply_text("Query Status is set to Raised!")
            elif data == db.Status.rejected:
                db.update_query(context.user_data["query"].id, db.Status.rejected)
                await update.callback_query.message.reply_text("Query Status is set to Rejected!")
            elif data == db.Status.inprogress:
                db.update_query(context.user_data["query"].id, db.Status.inprogress)
                await update.callback_query.message.reply_text("Query Status is set to In-Progress!")
            elif data == db.Status.resolved:
                db.update_query(context.user_data["query"].id, db.Status.resolved)
                await update.callback_query.message.reply_text("Query Status is set to Resolved!")
            elif data == db.Status.delete:
                db.delete_query(context.user_data["query"].id)
                await update.callback_query.message.reply_text("Query is deleted!")
        else:
            if data == db.Status.raised:
                db.update_query(context.user_data["query"].id, db.Status.raised)
                await update.callback_query.message.reply_text("Query Status is set to Raised!")
            elif data == db.Status.delete:
                db.delete_query(context.user_data["query"].id)
                await update.callback_query.message.reply_text("Query is deleted!")
        return ConversationHandler.END
    except Exception as e:
        return ConversationHandler.END

async def handle_query_faculty(update: Update, context: CallbackContext):
    try:
        context.user_data["query_teacher"] = str(update.callback_query.data)
        await update.callback_query.message.reply_text("Please Enter Subject of your query")
        return QUERY_SUBJECT
    except:
        return ConversationHandler.END

async def handle_query_subject(update: Update, context: CallbackContext):
    try:
        context.user_data["query_subject"] = str(update.message.text)
        await update.message.reply_text("Please enter your query:")
        return QUERY_MESSAGE
    except:
        return ConversationHandler.END

async def handle_query_message(update: Update, context: CallbackContext):
    try:
        context.user_data["query_message"] = str(update.message.text)
        user_id = str(update.message.chat_id)
        student, stud_user = db.get_student(user_id)
        teacher, teach_user = db.get_teacher_detail(context.user_data["query_teacher"])
        db.add_query(str(stud_user.id), str(teach_user.id), context.user_data["query_subject"], context.user_data["query_message"])
        await update.message.reply_text("Your query is successfully registered!")
        if teacher:
            message = f"New Query Recieved\
                \nStudent Name: {stud_user.name}\
                \nStudent ID: {stud_user.id}\
                \nStudent Semester: {student.sem}\
                \nStudent Section: {student.sec}\
                \nQuery Subject: {context.user_data['query_subject']}\
                \nQuery Message: {context.user_data['query_message']}"
            send_message_user(teacher.user_id, message=message)
            await update.message.reply_text("Your Query is sent to faculty")
        return ConversationHandler.END
    except Exception as e:
        return ConversationHandler.END

conversation_handler_query = ConversationHandler(
    name='query_conversation',
    entry_points=[CommandHandler('query', query)],
    states={
        QUERY_OPTION: [
            CallbackQueryHandler(handle_query_option)
        ],
        QUERY_ID: [
            CallbackQueryHandler(handle_query_id)
        ],
        QUERY_ACTION: [
            CallbackQueryHandler(handle_query_action)
        ],
        QUERY_FACULTY: [
            CallbackQueryHandler(handle_query_faculty)
        ],
        QUERY_SUBJECT : [
            MessageHandler(filters.Regex(".*"), handle_query_subject)
        ],
        QUERY_MESSAGE : [
            MessageHandler(filters.Regex(".*"), handle_query_message)
        ]
    },
    fallbacks=[
        CommandHandler('cancel', ConversationHandler.END)
    ]
)


# ------------------------------------------------------------------------------------------------
# Feedback Conversation
FEEDBACK_OPTION, FEEDBACK_ID, FEEDBACK_ACTION, FEEDBACK_SUBJECT, FEEDBACK_MESSAGE = range(24, 29)

async def feedback(update: Update, context: CallbackContext):
    try:
        user = db.get_user(str(update.message.chat_id))
        if user is None:
            await update.message.reply_text("Sorry, Can't find your information.")
            await update.message.reply_text("Please register yourself using /start command.")
            return ConversationHandler.END

        context.user_data["user"] = user.id
        context.user_data["role"] = user.user_type

        if user.user_type == db.Account.admin:
            keyboard = [
                [InlineKeyboardButton(text="All FeedBack", callback_data="admin-all")],
            ]
        else:
            keyboard = [
                [InlineKeyboardButton(text="My Feedbacks", callback_data="user-all")],
                [InlineKeyboardButton(text="New Feedback", callback_data="user-new")],
            ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text("Please Select Option:", reply_markup=reply_markup)
        return FEEDBACK_OPTION
    except Exception as e:
        return ConversationHandler.END

async def handle_feedback_option(update: Update, context:CallbackContext):
    try:
        context.user_data["option"] = str(update.callback_query.data)
        if context.user_data["role"] == db.Account.admin:
            query = update.callback_query
            if context.user_data["option"] == "admin-all":
                feedbacks = db.get_feedbacks()
                keyboard = [
                    [InlineKeyboardButton(text=f"Subject: {feedback.subject}",
                                        callback_data=feedback.id)]
                for feedback in feedbacks ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                if len(feedbacks) == 0:
                    await query.message.reply_text("No Feedbacks Found!")
                    return ConversationHandler.END
                else:
                    await query.edit_message_text("Please Select Feedback:")
                    await query.edit_message_reply_markup(reply_markup=reply_markup)
                return COMPLAINT_ID

        else:
            query = update.callback_query
            if context.user_data["option"] == "user-all":
                feedbacks = db.get_feedbacks(str(update.callback_query.message.chat_id))
                keyboard = [
                    [InlineKeyboardButton(text=f"Subject: {feedback.subject}",
                                        callback_data=feedback.id)]
                for feedback in feedbacks ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                if len(feedbacks) == 0:
                    await query.message.reply_text("No Feedbacks Found!")
                    return ConversationHandler.END
                else:
                    await query.edit_message_text("Please Select Feedback:")
                    await query.edit_message_reply_markup(reply_markup=reply_markup)
                return COMPLAINT_ID

            elif context.user_data["option"] == "user-new":
                await update.callback_query.message.reply_text("Enter Subject for your Feedback:")
                return FEEDBACK_SUBJECT
    except Exception as e:
        return ConversationHandler.END

async def handle_feedback_id(update: Update, context: CallbackContext):
    try:
        context.user_data["feedback"] = db.get_feedback(int(str(update.callback_query.data)))
        user = db.get_user(str(update.callback_query.message.chat_id))
        if user is None:
            await update.callback_query.message.reply_text("Sorry, Can't find your information.")
            await update.callback_query.message.reply_text("Please register yourself using /start command.")
            return ConversationHandler.END

        keyboard = [
            [InlineKeyboardButton(text=db.Status.delete, callback_data=db.Status.delete)],
            [InlineKeyboardButton(text="End", callback_data="cancel")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        message = f"Feedback:\
            \nFeedback ID: {context.user_data['feedback'].id}\
            \nFeedback Sender: {context.user_data['feedback'].user}\
            \nFeedback Subject: {context.user_data['feedback'].subject}\
            \nFeedback Description: {context.user_data['feedback'].description}"
        query = update.callback_query
        await query.edit_message_text(message)
        await query.edit_message_reply_markup(reply_markup=reply_markup)
        return COMPLAINT_ACTION
    except Exception as e:
        return ConversationHandler.END

async def handle_feedback_action(update: Update, context: CallbackContext):
    try:
        data = str(update.callback_query.data)
        user = db.get_user(str(update.callback_query.message.chat_id))
        if user is None:
            await update.callback_query.message.reply_text("Sorry, Can't find your information.")
            await update.callback_query.message.reply_text("Please register yourself using /start command.")
            return ConversationHandler.END
        if data == "cancel":
            await update.callback_query.message.reply_text("Conversation is ended!")
        elif data == db.Status.delete:
            db.delete_feedback(context.user_data["feedback"].id)
            await update.callback_query.message.reply_text("Feedback is deleted!")
        return ConversationHandler.END
    except Exception as e:
        return ConversationHandler.END

async def handle_feedback_subject(update: Update, context: CallbackContext):
    try:
        context.user_data["feed_subject"] = str(update.message.text)
        await update.message.reply_text("Please enter your feedback:")
        return FEEDBACK_MESSAGE
    except:
        return ConversationHandler.END

async def handle_feedback_message(update: Update, context: CallbackContext):
    try:
        context.user_data["feed_message"] = str(update.message.text)
        user_id = str(update.message.chat_id)
        user = db.get_user(user_id)
        db.add_feedback(str(user.id), context.user_data["feed_subject"], context.user_data["feed_message"])
        await update.message.reply_text("Thank you for your feedback!")
        admin = db.get_admin()
        if admin:
            message = f"New Feedback Recieved\
                \nGiven By: {user.name}\
                \nUser ID: {user.id}\
                \nUser Level: {user.user_type}\
                \nFeedback Subject: {context.user_data['feed_subject']}\
                \nFeedback Message: {context.user_data['feed_message']}"
            send_message_user(admin.user_id, message)
            await update.message.reply_text("Your Feedback is sent to Developer!")
        return ConversationHandler.END
    except Exception as e:
        return ConversationHandler.END

conversation_handler_feedback = ConversationHandler(
    name='feedback_conversation',
    entry_points=[CommandHandler('feedback', feedback)],
    states={
        FEEDBACK_OPTION: [
            CallbackQueryHandler(handle_feedback_option)
        ],
        FEEDBACK_ACTION: [
            CallbackQueryHandler(handle_feedback_action)
        ],
        FEEDBACK_ID: [
            CallbackQueryHandler(handle_feedback_id)
        ],
        FEEDBACK_SUBJECT : [
            MessageHandler(filters.Regex(".*"), handle_feedback_subject)
        ],
        FEEDBACK_MESSAGE : [
            MessageHandler(filters.Regex(".*"), handle_feedback_message)
        ]
    },
    fallbacks=[
        CommandHandler('cancel', ConversationHandler.END)
    ]
)


if __name__ == '__main__':
    Base.metadata.create_all(engine)

    application = Application.builder().token(token).build()

    application.add_handler(CommandHandler('cancel', ConversationHandler.END))
    application.add_handler(CommandHandler('about', about_handler))
    application.add_handler(CommandHandler('help', help_handler))
    application.add_handler(CommandHandler('me', me_handler))

    application.add_handler(conversation_handler_start)
    application.add_handler(conversation_handler_complaint)
    application.add_handler(conversation_handler_query)
    application.add_handler(conversation_handler_feedback)
    application.add_handler(conversation_handler_user)

    application.run_polling(allowed_updates=Update.ALL_TYPES)