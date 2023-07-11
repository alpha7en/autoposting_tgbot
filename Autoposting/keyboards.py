from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def get_main_keyboard():
    keyboard = InlineKeyboardMarkup()
    keyboard.row(
        InlineKeyboardButton('⚙️ Настройки', callback_data='setup_mode'),
        InlineKeyboardButton('✉️ Постинг', callback_data='posting_mode')
    )
    return keyboard

def get_setup_keyboard():
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton('➕ добавить группу/чат', callback_data='add_group'))
    keyboard.add(InlineKeyboardButton('➖ удалить группу/чат', callback_data='remove_group'))
    keyboard.add(InlineKeyboardButton('✏️ изменить группу/чат', callback_data='edit_group'))
    keyboard.add(InlineKeyboardButton('️🔧 настроить vk token', callback_data='vk_token_edit'))
    keyboard.add(InlineKeyboardButton('↩️ назад', callback_data='back'))
    return keyboard

def get_posting_keyboard():
    keyboard = InlineKeyboardMarkup()
    keyboard.row(
        InlineKeyboardButton('🪄 сгенерировать текст', callback_data='generate_text'),
        InlineKeyboardButton('✏️ добавить текст', callback_data='send_text_manually')
    )
    keyboard.row(
        InlineKeyboardButton('🖼️ добавить фото', callback_data='add_photo'),
        InlineKeyboardButton('📰 превью', callback_data='preview')
    )
    keyboard.row(
        InlineKeyboardButton('↩️ назад', callback_data='back'),
        InlineKeyboardButton('📨 отправить', callback_data='send_post')
    )
    return keyboard

def get_send_text_manually_keyboard():
    keyboard = InlineKeyboardMarkup()
    keyboard.row(
        InlineKeyboardButton('↩️ назад', callback_data='posting_mode')
    )
    return keyboard

def get_gpt_keyboard():
    keyboard = InlineKeyboardMarkup()
    keyboard.row(
        InlineKeyboardButton('✅', callback_data='gpt_ok'),
        InlineKeyboardButton('🔄️', callback_data='gpt_new')
    )
    keyboard.row(
        InlineKeyboardButton('↩️ назад', callback_data='posting_mode')
    )
    return keyboard

def get_channels_keyboard(items, page, last=False, state=''):
    keyboard = InlineKeyboardMarkup(row_width=2)
    # Добавляем элементы списка
    st=state.split('&')
    st.pop(0)
    for item in items:
        if item not in st:
            button = InlineKeyboardButton(text=item, callback_data=f"ch_item:{item}:{page}")
            keyboard.insert(button)
        else:
            button = InlineKeyboardButton(text="✅"+item, callback_data=f"ch_item:{item}:{page}")
            keyboard.insert(button)
    # Добавляем кнопки для перелистывания страниц
    if page ==1:
        if not last:
            keyboard.row(
                InlineKeyboardButton(text=str(page), callback_data="ch_noop"),
                InlineKeyboardButton(text="➡️", callback_data=f"ch_next:{page}"),
            )
    elif last:
        keyboard.row(
            InlineKeyboardButton(text="⬅️", callback_data=f"ch_prev:{page}"),
            InlineKeyboardButton(text=str(page), callback_data="ch_noop"),
        )
    else:
        keyboard.row(
            InlineKeyboardButton(text="⬅️", callback_data=f"ch_prev:{page}"),
            InlineKeyboardButton(text=str(page), callback_data="ch_noop"),
            InlineKeyboardButton(text="➡️", callback_data=f"ch_next:{page}"),
        )
    # Добавляем кнопку подтверждения и возврата
    keyboard.row(
        InlineKeyboardButton('↩️ назад', callback_data='posting_mode'),
        InlineKeyboardButton(text="📨 готово", callback_data=f"ch_confirm:{page}"))
    return keyboard

def get_add_group_keyboard():
    keyboard = InlineKeyboardMarkup()
    keyboard.row(
        InlineKeyboardButton('↩️ назад', callback_data='setup_mode')
    )
    return keyboard

def get_select_social_keyboard():
    keyboard = InlineKeyboardMarkup()
    keyboard.row(
        InlineKeyboardButton('vk', callback_data='vk'),
        InlineKeyboardButton('tg', callback_data='tg')
    )
    return keyboard
def get_soc_type_vk_keyboard():
    keyboard = InlineKeyboardMarkup()
    keyboard.row(
        InlineKeyboardButton('??', callback_data='vk'),
        InlineKeyboardButton('??', callback_data='tg')
    )
    return keyboard
def get_soc_type_tg_keyboard():
    keyboard = InlineKeyboardMarkup()
    keyboard.row(
        InlineKeyboardButton('канал', callback_data='tg_channel'),
        InlineKeyboardButton('чат', callback_data='tg_chat')
    )
    return keyboard

def get_remove_group_keyboard(items):
    keyboard = InlineKeyboardMarkup(row_width=2)
    for item in items:
        button = InlineKeyboardButton(text=item, callback_data=f"rem:{item}")
        keyboard.insert(button)
    keyboard.add(InlineKeyboardButton('↩️ назад', callback_data='setup_mode'))
    return keyboard

def get_channels_rem_keyboard(items, page, last=False):
    keyboard = InlineKeyboardMarkup(row_width=2)
    # Добавляем элементы списка
    for item in items:
        button = InlineKeyboardButton(text=item, callback_data=f"ri:{item}")
        keyboard.insert(button)
    # Добавляем кнопки для перелистывания страниц
    if page ==1:
        if not last:
            keyboard.row(
                InlineKeyboardButton(text=str(page), callback_data="ch_noop"),
                InlineKeyboardButton(text="➡️", callback_data=f"rem_next:{page}"),
            )
    elif last:
        keyboard.row(
            InlineKeyboardButton(text="⬅️", callback_data=f"rem_prev:{page}"),
            InlineKeyboardButton(text=str(page), callback_data="ch_noop"),
        )
    else:
        keyboard.row(
            InlineKeyboardButton(text="⬅️", callback_data=f"rem_prev:{page}"),
            InlineKeyboardButton(text=str(page), callback_data="ch_noop"),
            InlineKeyboardButton(text="➡️", callback_data=f"rem_next:{page}"),
        )
    # Добавляем кнопку подтверждения и возврата
    keyboard.add(
        InlineKeyboardButton('↩️ назад', callback_data='setup_mode'))
    return keyboard