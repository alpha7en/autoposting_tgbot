import aiogram
import asyncio
from vk_posting import post_photo_to_group
from aiogram import types, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.utils.exceptions import BotBlocked, ChatNotFound
from keyboards import *
import os
import gpt

class Bot:
    def __init__(self, token, db,TOKENS_gpt):
        self.TOKENS_gpt=TOKENS_gpt
        self.bot = aiogram.Bot(token)
        self.storage = MemoryStorage()
        self.dp = Dispatcher(self.bot, storage=self.storage)
        self.db = db
        self.register_handlers()

    def register_handlers(self):
        self.dp.register_message_handler(self.start_handler, commands=['start'])
        self.dp.register_callback_query_handler(self.button_handler)
        self.dp.register_message_handler(self.text_handler, content_types=[types.ContentType.TEXT])
        self.dp.register_message_handler(self.photo_handler, content_types=[types.ContentType.PHOTO])
        self.dp.register_message_handler(self.cancel_posting, commands=['cancel'], state='posting')

    async  def reset(self, user_id):
        self.db.update_state(user_id, 'start')
        post = self.db.get_post(user_id)
        if post["image_path"] != "":
            if os.path.isfile(post["image_path"]): os.remove(post["image_path"])
        self.db.set_post(user_id, text="", image_path="", date="", channels="")
    async def start_handler(self, message: types.Message):
        user_id = message.from_user.id
        self.db.add_user(user_id)
        await self.send_message(user_id, "Привет! Выбери режим настройки или режим постинга.", reply_markup=get_main_keyboard())
        await self.reset(user_id)

    async def get_items(self, user_id, page):
        items = self.db.get_channels(user_id)
        if items == None: return None
        start_index = (page - 1) * 4
        end_index = start_index + 4
        # Проверяем, что на странице есть элементы
        if start_index >= len(items):
            return None
        # Получаем элементы на странице
        if end_index >= len(items):
            return items[start_index:]
        else:
            return items[start_index:end_index]

    async def post_to_channel(self, post_text:str, photo_path: str, channel_id: str):
        try:
        # Проверяем, добавлен ли бот в канал и имеет ли он права на публикацию
            member = await self.bot.get_chat_member(channel_id, self.bot.id)
            if member.status not in ["administrator", "creator"]:
                return "Бот не является администратором"
            # Отправляем пост с фото и текстом
            if photo_path != "":
                with open(photo_path, 'rb') as photo:
                    await self.bot.send_photo(channel_id, photo, caption=post_text)
            else:
                if post_text=="": return "в вашем посте ничего нет"
                else: await self.bot.send_message(channel_id, text=post_text)

            return "Пост успешно опубликован"
        except (BotBlocked, ChatNotFound):
            return "Бот заблокирован, чат/канал не найден или у бота недостаточно прав для публикации"
        except Exception as err:
            print(err)
            return "Произошла ошибка.\nВозможно у бота недостаточно прав"

    async def button_handler(self, query: types.CallbackQuery):
        user_id = query.from_user.id
        data = query.data

        if data == 'setup_mode':
            await self.bot.delete_message(chat_id=query.message.chat.id, message_id=query.message.message_id)
            await self.send_message(user_id, "Выбери действие:", reply_markup=get_setup_keyboard())
            self.db.update_state(user_id, 'setup')
        elif data == 'posting_mode':
            await self.bot.delete_message(chat_id=query.message.chat.id, message_id=query.message.message_id)
            await self.send_message(user_id, "Выбери действие:", reply_markup=get_posting_keyboard())
            self.db.update_state(user_id, 'posting')
        elif data == 'preview':
            post = self.db.get_post(user_id)
            await self.bot.delete_message(chat_id=query.message.chat.id, message_id=query.message.message_id)
            if post["image_path"] != "":
                await self.bot.send_photo(chat_id=query.message.chat.id, photo=(post["image_path"])[6:-4],
                                     caption=post["text"], reply_markup=get_send_text_manually_keyboard())
            else:
                if post["text"]!= '':
                    await self.send_message(user_id, post["text"], reply_markup=get_send_text_manually_keyboard())
                else:await self.send_message(user_id, 'вы не добавили текст', reply_markup=get_send_text_manually_keyboard())
            self.db.update_state(user_id, 'posting')
        elif data == 'back':
            await self.bot.delete_message(chat_id=query.message.chat.id, message_id=query.message.message_id)
            await self.send_message(user_id, "Главное меню", reply_markup=get_main_keyboard())
            await self.reset(user_id)

        elif data == 'add_group':
            await self.bot.delete_message(chat_id=query.message.chat.id, message_id=query.message.message_id)
            msg=await self.send_message(user_id, "введите незанятое название паблика/чата (название не должно содержать спец. символов и должно быть не более 10 символов)", reply_markup=get_add_group_keyboard())
            self.db.update_state(user_id, f'add_group_{msg.message_id}')

        elif data == 'send_text_manually':
            await self.bot.delete_message(chat_id=query.message.chat.id, message_id=query.message.message_id)
            msg = await self.send_message(user_id, "Пришлите текст поста (до 1024 символов)", reply_markup=get_send_text_manually_keyboard())
            self.db.update_state(user_id, f'send_text_manually_{msg.message_id}')
        elif data == 'add_photo':
            await self.bot.delete_message(chat_id=query.message.chat.id, message_id=query.message.message_id)
            msg = await self.send_message(user_id, "Пришлите фото для поста", reply_markup=get_send_text_manually_keyboard())
            self.db.update_state(user_id, f'send_photo_manually_{msg.message_id}')
        elif data == 'generate_text':
            await self.bot.delete_message(chat_id=query.message.chat.id, message_id=query.message.message_id)
            msg = await self.send_message(user_id, "Пришлите описание статьи",
                                          reply_markup=get_send_text_manually_keyboard())
            self.db.update_state(user_id, f'send_gpt_{msg.message_id}')
        elif data=='gpt_ok':
            await self.bot.delete_message(chat_id=query.message.chat.id, message_id=query.message.message_id)
            state = self.db.get_state(user_id)
            self.db.set_post_text(user_id, text=state.split("_")[1])
            # Сохранение данных поста в базе данных или другом хранилище
            await self.send_message(user_id, "Текст поста сохранен\n\nВыбери действие:",
                                    reply_markup=get_posting_keyboard())
            self.db.update_state(user_id, 'posting')
        elif data=='gpt_new':
            await self.bot.delete_message(chat_id=query.message.chat.id, message_id=query.message.message_id)
            state = self.db.get_state(user_id)
            prompt = state.split("_")[2]
            t = await gpt.generate_text(prompt=prompt, TOKEN=self.TOKENS_gpt[int(user_id) % len(self.TOKENS_gpt)])
            if t == 'err':
                await self.send_message(user_id, "произошла ошибка, попробуйте позже\n\nВыбери действие:",
                                        reply_markup=get_posting_keyboard())
                self.db.update_state(user_id, 'posting')
                print(f"ошибка с токеном {self.TOKENS_gpt[int(user_id) % len(self.TOKENS_gpt)]}")
            else:
                if len(t) > 1024:
                    t = t[0:1023]
                # Сохранение данных поста в базе данных или другом хранилище
                await self.send_message(user_id, f"ТЕКСТ СТАТЬИ:\n {t}",
                                        reply_markup=get_gpt_keyboard())
                self.db.update_state(user_id, f'gptwaiting_{t}_{prompt}')
        elif data == 'send_post' and self.db.get_state(user_id)=='posting':
            items=await self.get_items(user_id=user_id, page=1)
            next_items=await self.get_items(user_id=user_id, page=2)

            if items != [''] and items != None:
                if next_items == None:
                    await self.bot.delete_message(chat_id=query.message.chat.id, message_id=query.message.message_id)
                    await self.send_message(user_id, "куда отправить:",
                                            reply_markup=get_channels_keyboard(items, 1,last=True))
                    self.db.update_state(user_id, 'channels_setup')
                else:
                    await self.bot.delete_message(chat_id=query.message.chat.id, message_id=query.message.message_id)
                    await self.send_message(user_id, "куда отправить:",
                                                  reply_markup=get_channels_keyboard(items,1))
                    self.db.update_state(user_id, 'channels_setup')
            else:
                await self.reset(user_id)
                await self.bot.edit_message_text(chat_id=query.message.chat.id, message_id=query.message.message_id, text="вы еще не добавили каналов/групп", reply_markup=get_main_keyboard())

        elif data.startswith('ch_next') and self.db.get_state(user_id).startswith('channels_setup'):
            page = int(data.split(':')[1])
            items = await self.get_items(user_id, page + 1)
            next_items=await self.get_items(user_id, page + 2)
            state = (self.db.get_state(user_id))
            if next_items == [''] or next_items == None:
                await self.bot.edit_message_text(chat_id=query.message.chat.id,
                                                 message_id=query.message.message_id,
                                                 text="куда отправить:",
                                                 reply_markup=get_channels_keyboard(items, page + 1, last=True, state=state))
            else:
                await self.bot.edit_message_text(chat_id=query.message.chat.id,
                                            message_id=query.message.message_id,
                                            text="куда отправить:",
                                            reply_markup=get_channels_keyboard(items, page + 1, state=state))
        elif data.startswith('ch_prev') and self.db.get_state(user_id).startswith('channels_setup'):
            page = int(data.split(':')[1])
            state = (self.db.get_state(user_id))
            items = await self.get_items(user_id, page - 1)
            await self.bot.edit_message_text(chat_id=query.message.chat.id,
                                             message_id=query.message.message_id,
                                             text="куда отправить:",
                                             reply_markup=get_channels_keyboard(items, page - 1, state=state))

        elif data.startswith('ch_item') and self.db.get_state(user_id).startswith('channels_setup'):
            t=data.split(":")

            state=self.db.get_state(user_id)
            if "&"+t[1] not in state:
                state+='&'+t[1]
                self.db.update_state(user_id, state)
            else:
                new='channels_setup'
                x=state.split('&')
                x.pop(0)
                for i in x:
                    if i !=t[1]:
                        new+='&'+i
                print(new)
                state=new
                self.db.update_state(user_id, new)



            items = await self.get_items(user_id, int(t[2]))
            next_items = await self.get_items(user_id,int(t[2]) + 1)
            last=(next_items == [''] or next_items == None)
            await self.bot.edit_message_text(chat_id=query.message.chat.id,
                                             message_id=query.message.message_id,
                                             text="куда отправить:",
                                             reply_markup=get_channels_keyboard(items, int(t[2]), state=state,last=last))
        elif data.startswith('ch_confirm') and self.db.get_state(user_id).startswith('channels_setup'):
            state = (self.db.get_state(user_id)).split('&')
            if len(state)>1:
                await self.bot.delete_message(chat_id=query.message.chat.id, message_id=query.message.message_id)
                state.pop(0)
                for i in state:

                    inf=self.db.get_group_information(user_id, i)
                    post=self.db.get_post(user_id)
                    if inf["social"]=="tg":
                        ans=await self.post_to_channel(post_text=post["text"], photo_path=post["image_path"], channel_id=inf["url"])
                        await self.send_message(user_id, f'{i}:\n{ans}')
                    elif post["text"] != "":
                        token=self.db.get_vk_token(user_id)
                        if token=="":
                            await self.send_message(user_id, 'вы не установили vk_token, вернитесь в настройки и измените его (поста будет удалён)')
                        else:
                            if post["image_path"]!="":
                                ans=post_photo_to_group(group_id=i, photo_path=post["image_path"], caption=post["text"], token=token)
                            else:
                                ans=post_text_to_group(group_id=i, message=post["text"],token=token)

                            await self.send_message(user_id, f'{i}:\n{ans}')
                    else:
                        await self.send_message(user_id,'ваш пост не содержал текста')
            elif query.message.text != "вы не выбрали ни одного канала":
                t = data.split(":")
                items = await self.get_items(user_id, int(t[1]))
                next_items = await self.get_items(user_id, int(t[1]) + 1)
                last = (next_items == [''] or next_items == None)
                await self.bot.edit_message_text(chat_id=query.message.chat.id,
                                                 message_id=query.message.message_id,
                                                 text="вы не выбрали ни одного канала",
                                                 reply_markup=get_channels_keyboard(items, int(t[1]), state=state,
                                                                                    last=last))




        elif data=="vk" or data=="tg":
            state = self.db.get_state(user_id)
            if state.startswith('select_social_'):
                await self.bot.delete_message(chat_id=query.message.chat.id, message_id=query.message.message_id)
                group=state[len('select_social_'):]
                if data=="vk":
                    msg = await self.send_message(user_id,
                                                  "пришлите id вашего сообщества (не забудьте, что пользователь, токен которого вы указали, должен быть администратором):")
                    self.db.update_state(user_id, f'socvk{state}_{msg.message_id}')

                if data=="tg":
                    await self.send_message(user_id, "выберите тип:",
                                            reply_markup=get_soc_type_tg_keyboard())
                    self.db.update_state(user_id, f'soctg_{group}')
        elif data=="tg_channel":
            await self.bot.delete_message(chat_id=query.message.chat.id, message_id=query.message.message_id)
            state = self.db.get_state(user_id)
            msg = await self.send_message(user_id, "пришлите id вашего канала\n'-xxxxxxxxx'\n(не забудьте назначить бота администратором и дать ему разрешени писать):")
            self.db.update_state(user_id, f'chan{state}_{msg.message_id}')
        elif data=="tg_chat":
            await self.bot.delete_message(chat_id=query.message.chat.id, message_id=query.message.message_id)
            state = self.db.get_state(user_id)
            msg=await self.send_message(user_id, "пришлите id вашего чата\n'-xxxxxxxxx'\n(не забудьте назначить бота администратором и дать ему разрешени писать):")
            self.db.update_state(user_id, f'chat{state}_{msg.message_id}')
        elif data == "edit_group" and self.db.get_state(user_id) == 'setup':
            items = await self.get_items(user_id=user_id, page=1)
            next_items = await self.get_items(user_id=user_id, page=2)

            if items != [''] and items != None:
                if next_items == None:
                    await self.bot.delete_message(chat_id=query.message.chat.id, message_id=query.message.message_id)
                    await self.send_message(user_id, "выберите:",
                                            reply_markup=get_channels_rem_keyboard(items, 1, last=True))
                    self.db.update_state(user_id, 'channels_rem_edit')
                else:
                    await self.bot.delete_message(chat_id=query.message.chat.id, message_id=query.message.message_id)
                    await self.send_message(user_id, "выберите:",
                                            reply_markup=get_channels_rem_keyboard(items, 1))
                    self.db.update_state(user_id, 'channels_rem_edit')
            else:
                await self.reset(user_id)
                await self.bot.edit_message_text(chat_id=query.message.chat.id, message_id=query.message.message_id,
                                                 text="вы еще не добавили каналов/групп",
                                                 reply_markup=get_setup_keyboard())
        #VK
        elif data=="remove_group"and self.db.get_state(user_id)=='setup':
            items=await self.get_items(user_id=user_id, page=1)
            next_items=await self.get_items(user_id=user_id, page=2)

            if items != [''] and items != None:
                if next_items == None:
                    await self.bot.delete_message(chat_id=query.message.chat.id, message_id=query.message.message_id)
                    await self.send_message(user_id, "выберите:",
                                            reply_markup=get_channels_rem_keyboard(items, 1,last=True))
                    self.db.update_state(user_id, 'channels_rem')
                else:
                    await self.bot.delete_message(chat_id=query.message.chat.id, message_id=query.message.message_id)
                    await self.send_message(user_id, "выберите:",
                                                  reply_markup=get_channels_rem_keyboard(items,1))
                    self.db.update_state(user_id, 'channels_rem')
            else:
                await self.reset(user_id)
                await self.bot.edit_message_text(chat_id=query.message.chat.id, message_id=query.message.message_id, text="вы еще не добавили каналов/групп", reply_markup=get_setup_keyboard())
        elif data.startswith('rem_next') and self.db.get_state(user_id).startswith('channels_rem'):
            page = int(data.split(':')[1])
            items = await self.get_items(user_id, page + 1)
            next_items = await self.get_items(user_id, page + 2)
            if next_items != [''] and next_items == None:
                await self.bot.edit_message_text(chat_id=query.message.chat.id,
                                                 message_id=query.message.message_id,
                                                 text="выберите:",
                                                 reply_markup=get_channels_rem_keyboard(items, page + 1, last=True))
            else:
                await self.bot.edit_message_text(chat_id=query.message.chat.id,
                                                 message_id=query.message.message_id,
                                                 text="выберите:",
                                                 reply_markup=get_channels_rem_keyboard(items, page + 1))
        elif data.startswith('rem_prev') and self.db.get_state(user_id).startswith('channels_rem'):
            page = int(data.split(':')[1])
            items = await self.get_items(user_id, page - 1)
            await self.bot.edit_message_text(chat_id=query.message.chat.id,
                                             message_id=query.message.message_id,
                                             text="выберите:",
                                             reply_markup=get_channels_rem_keyboard(items, page - 1))
        elif data.startswith('ri:') and self.db.get_state(user_id).startswith('channels_rem'):
            channel=data[len("ri:"):]

            if self.db.get_state(user_id)=='channels_rem':
                self.db.rem_channel(user_id=user_id, channel=channel)
                await self.bot.delete_message(chat_id=query.message.chat.id, message_id=query.message.message_id)
                await self.send_message(user_id, "Удалено!\n\nВыбери действие:", reply_markup=get_setup_keyboard())
                self.db.update_state(user_id, 'setup')
            else:
                await self.bot.delete_message(chat_id=query.message.chat.id, message_id=query.message.message_id)
                await self.send_message(user_id, "выберите площадку:",
                                        reply_markup=get_select_social_keyboard())
                self.db.update_state(user_id, f"select_social_{channel}")

        elif data =="vk_token_edit":
            await self.bot.delete_message(chat_id=query.message.chat.id, message_id=query.message.message_id)
            msg = await self.send_message(user_id, "Пришлите ваш vk_token", reply_markup=get_send_text_manually_keyboard())
            self.db.update_state(user_id, f'vk_token_edit_{msg.message_id}')



    async def send_message(self, chat_id, text, reply_markup=None):
        return await self.bot.send_message(chat_id, text, reply_markup=reply_markup)

    async def delete_message(self, chat_id, message_id):
        await self.bot.delete_message(chat_id, message_id)

    async def text_handler(self, message: types.Message):
        user_id = message.from_user.id
        state = self.db.get_state(user_id)

        if state.startswith('send_text_manually'):
            await self.bot.delete_message(chat_id=message.chat.id, message_id=state[len('send_text_manually_'):])
            text = message.text
            #проверка длины текста
            lt=len(text)-1024
            if lt<=0:
                self.db.set_post_text(user_id, text=text)
                # Сохранение данных поста в базе данных или другом хранилище
                await self.send_message(user_id, "Текст поста сохранен\n\nВыбери действие:", reply_markup=get_posting_keyboard())
                self.db.update_state(user_id, 'posting')
            else:
                msg = await self.send_message(user_id, f"Текст слишком большой, уменьшите его на {lt}",
                                              reply_markup=get_send_text_manually_keyboard())
                self.db.update_state(user_id, f'send_text_manually_{msg.message_id}')
        elif state.startswith("vk_token_edit_"):

            await self.bot.delete_message(chat_id=message.chat.id, message_id=state[len('vk_token_edit_'):])
            text = message.text
            self.db.update_vk_token(user_id, text)
            await self.send_message(user_id, "vk_token успешно сохранён\n\nВыбери действие:", reply_markup=get_setup_keyboard())
            self.db.update_state(user_id, 'setup')

        elif state.startswith("send_gpt_"):
            await self.bot.edit_message_text(chat_id=message.chat.id, message_id=state[len('send_gpt_'):], text="генерация...")

        #await self.bot.delete_message(chat_id=message.chat.id, message_id=state[len('send_gpt_'):])
            prompt = message.text

            t = await gpt.generate_text(prompt=prompt, TOKEN=self.TOKENS_gpt[int(user_id) % len(self.TOKENS_gpt)])
            await self.bot.delete_message(chat_id=message.chat.id, message_id=state[len('send_gpt_'):])
            if t=='err':
                await self.send_message(user_id, "произошла ошибка, попробуйте позже\n\nВыбери действие:",
                                        reply_markup=get_posting_keyboard())
                self.db.update_state(user_id, 'posting')
                print(f"ошибка с токеном {self.TOKENS_gpt[int(user_id) % len(self.TOKENS_gpt)]}")
            else:
                if len(t)>1024:
                    t=t[0:1023]
                # Сохранение данных поста в базе данных или другом хранилище
                await self.send_message(user_id, f"ТЕКСТ СТАТЬИ:\n {t}",
                                        reply_markup=get_gpt_keyboard())
                self.db.update_state(user_id, f'gptwaiting_{t}_{prompt}')
        elif state.startswith("add_group"):
            text=message.text
            await self.bot.delete_message(chat_id=message.chat.id, message_id=state[len('add_group_'):])
            groups=self.db.get_channels(user_id)
            if text not in groups:
                self.db.add_channel(user_id, text)
                await self.send_message(user_id, "выберите площадку:",
                                        reply_markup=get_select_social_keyboard())
                self.db.update_state(user_id, f"select_social_{text}")
            else:
                msg=await self.send_message(user_id, "это имя занято, введите новое",
                                        reply_markup=get_add_group_keyboard())
                self.db.update_state(user_id, f'add_group_{msg.message_id}')
        #tg канал
        elif state.startswith("chansoctg_"):
            st = state.split('_')
            text=message.text
            await self.bot.delete_message(chat_id=message.chat.id, message_id=st[2])
            ####ПРОВЕРКА ВАЛИДНОСТИ КАНАЛА
            self.db.add_group_information(user_id,st[1], "tg", "channel", text)
            self.db.update_state(user_id, f'setup')
            await self.send_message(user_id, "Выбери действие:", reply_markup=get_setup_keyboard())
        #tg chat
        elif state.startswith("chatsoctg_"):
            st = state.split('_')
            text = message.text
            await self.bot.delete_message(chat_id=message.chat.id, message_id=st[2])
            ####ПРОВЕРКА ВАЛИДНОСТИ КАНАЛА
            print(st)
            self.db.add_group_information(user_id, st[1], "tg", "chat", text)
            self.db.update_state(user_id, f'setup')
            await self.send_message(user_id, "Выбери действие:", reply_markup=get_setup_keyboard())
        elif state.startswith("socvk"):

            st = state.split('_')
            text = message.text
            await self.bot.delete_message(chat_id=message.chat.id, message_id=st[3])
            ####ПРОВЕРКА ВАЛИДНОСТИ группы
            print(st)
            self.db.add_group_information(user_id, st[2], "vk", "vk", text)
            self.db.update_state(user_id, f'setup')
            await self.send_message(user_id, "Выбери действие:", reply_markup=get_setup_keyboard())

    async def photo_handler(self, message: types.Message):
        user_id = message.from_user.id
        state = self.db.get_state(user_id)
        if state.startswith('send_photo_manually'):
            await self.bot.delete_message(chat_id=message.chat.id, message_id=state[len('send_photo_manually_'):])
            photo = message.photo[-1]
            # Реализация сохранения фотографии поста
            # Получение и сохранение фотографии в отдельной папке
            image_path = f'image/{photo.file_id}.jpg'
            post=self.db.get_post(user_id)
            if post["image_path"] != "":
                if os.path.isfile(post["image_path"]): os.remove(post["image_path"])

            await photo.download(image_path)
            self.db.set_post_image_path(user_id, image_path=image_path)
            await self.send_message(user_id, "Фотография поста сохранена\n\nВыбери действие:",
                                    reply_markup=get_posting_keyboard())
            self.db.update_state(user_id, 'posting')

    async def cancel_posting(self, message: types.Message):
        user_id = message.from_user.id
        prev_message_id = await self.db.get_prev_message(user_id)
        if prev_message_id:
            await self.bot.delete_message(chat_id=message.chat.id, message_id=prev_message_id[0])
        await message.answer("Вы отменили постинг.", reply_markup=get_main_keyboard())
        await self.db.update_state(user_id, 'start')
        await self.db.update_prev_message(user_id, str(message.message_id))

    # Другие методы для работы с Telegram API

# Создание объекта Bot и запуск бота
