import config
import logging
import os
import telegram.replykeyboardmarkup
from telegram import Audio, File
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import eyed3

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO, filename='logs.log')
logging.basicConfig()

logger = logging.getLogger(__name__)

chat_id_to_mp3 = {}

def done(bot, update):
    logger.info("[Command] done")
    logger.info("[ChatID] " + str(update.message.chat_id))
    bot.send_message(chat_id=update.message.chat_id, text="Enviando áudio modificado...")
    bot.send_audio(chat_id=update.message.chat_id, audio=open(str(update.message.chat_id) + ".mp3", 'rb'), timeout=500)
    del chat_id_to_mp3[update.message.chat_id]
    os.remove(str(update.message.chat_id) + ".mp3")
    bot.send_message(chat_id=update.message.chat_id, text="Aqui Estar Sua Música :) ")

def add_tag(bot, update):
    logger.info("[Handler] add_tag")
    logger.info("[ChatID] " + str(update.message.chat_id))
    if update.message.chat_id not in chat_id_to_mp3:
        bot.send_message(chat_id=update.message.chat_id, text="Espere por favor até o ficheiro ser transferido e repetir")    
        return

    tag = update.message.text.split()
    if tag[0] == 'artista':
        chat_id_to_mp3[update.message.chat_id].tag.artist = " ".join(tag[1:])
    elif tag[0] == 'título':
        chat_id_to_mp3[update.message.chat_id].tag.title = " ".join(tag[1:])
    elif tag[0] == 'álbum':
        chat_id_to_mp3[update.message.chat_id].tag.album = " ".join(tag[1:])
    elif tag[0] == 'genre':
        chat_id_to_mp3[update.message.chat_id].tag.genre = " ".join(tag[1:])
    elif tag[0] == 'faixa':
        chat_id_to_mp3[update.message.chat_id].tag.track_num = " ".join(tag[1:])
    else:
        bot.send_message(chat_id=update.message.chat_id, text="Marca inválida; as marcas válidas são: artista, título, álbum e faixa")    
        return
    
    chat_id_to_mp3[update.message.chat_id].tag.save()
    bot.send_message(chat_id=update.message.chat_id, text=tag[0] + " Foi definido envie /done pra Salva a Tag: " + " ".join(tag[1:]))

def audio(bot: telegram.Bot, update):
    logger.info("[Handler] audio")
    logger.info("[ChatID] " + str(update.message.chat_id))
    bot.send_message (chat_id=update.message.chat_id, text="Mensagem recebida, a transferir o ficheiro...")
    audio_file = bot.getFile(update.message.audio.file_id)
    # print ("File ID:", audio_file.file_id)
    # print ("Downloading file...")
    audio_file.download(str(update.message.chat_id) + ".mp3")
    bot.send_message (chat_id=update.message.chat_id, text="Pronto para aceitar as marcas")
    chat_id_to_mp3[update.message.chat_id] = eyed3.load(str(update.message.chat_id) + ".mp3")

def unknown(bot: telegram.Bot, update):
    logger.info("[Handler] unknown")
    logger.info("[ChatID] " + str(update.message.chat_id))
    bot.send_message(chat_id=update.message.chat_id, text="Desculpe, não percebi esse comando..")
    

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

    updater.start_polling(timeout=100)
