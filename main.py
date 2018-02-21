import config
import logging
import telegram.replykeyboardmarkup
from telegram import Audio, File
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from mp3_tagger import MP3File

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

chat_id_to_file = {}
chat_id_to_mp3 = {}

def done(bot, update):
    print("Sending modified audio...")
    bot.send_audio(chat_id=update.message.chat_id, audio=open(str(update.message.chat_id) + ".mp3", 'rb'), timeout=500)
    print("All done.")

def add_tag(bot, update):
    tag = update.message.text.split()
    if tag[0] == 'artist':
        chat_id_to_mp3[update.message.chat_id].artist = " ".join(tag[1:])
    elif tag[0] == 'title':
        chat_id_to_mp3[update.message.chat_id].song = " ".join(tag[1:])
    elif tag[0] == 'album':
        chat_id_to_mp3[update.message.chat_id].album = " ".join(tag[1:])
    elif tag[0] == 'genre':
        chat_id_to_mp3[update.message.chat_id].genre = " ".join(tag[1:])
    elif tag[0] == 'track':
        chat_id_to_mp3[update.message.chat_id].track = " ".join(tag[1:])
    else:
        bot.send_message(chat_id=update.message.chat_id, text="Invalid tag, valid tags are: artist, title, album, genre, track")    
        return
    
    chat_id_to_mp3[update.message.chat_id].save()
    bot.send_message(chat_id=update.message.chat_id, text=tag[0] + " Has been set to: " + " ".join(tag[1:]))

def audio(bot: telegram.Bot, update):
    bot.send_message (chat_id=update.message.chat_id, text="Message recieved, Downloading file...")
    chat_id_to_file[update.message.chat_id] = bot.getFile(update.message.audio.file_id)
    print ("File ID:", chat_id_to_file[update.message.chat_id].file_id)
    print ("Downloading file...")
    chat_id_to_file[update.message.chat_id].download(str(update.message.chat_id) + ".mp3")
    bot.send_message (chat_id=update.message.chat_id, text="Ready to accept tags.")
    chat_id_to_mp3[update.message.chat_id] = MP3File(str(update.message.chat_id) + ".mp3")

def unknown(bot: telegram.Bot, update):
    bot.send_message(chat_id=update.message.chat_id, text="Sorry, I didn't understand that command.")
    

if __name__ == '__main__':
    updater = Updater(token=config.BOT_TOKEN)
    dispatcher = updater.dispatcher
    
    done_handler = CommandHandler('done', done)
    dispatcher.add_handler(done_handler)

    add_tag_handler = MessageHandler(Filters.text, add_tag)
    dispatcher.add_handler(add_tag_handler)

    audio_handler = MessageHandler(Filters.audio, audio)
    dispatcher.add_handler(audio_handler)

    unknown_handler = MessageHandler(Filters.command, unknown)
    dispatcher.add_handler(unknown_handler)

    updater.start_polling()
