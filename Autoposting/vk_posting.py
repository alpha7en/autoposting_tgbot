import vk_api
from vk_api import VkUpload

def post_photo_to_group(group_id, photo_path, caption, token):
    try:
        vk_session = vk_api.VkApi(token=token)
        vk = vk_session.get_api()
        upload = VkUpload(vk_session)
        photo = upload.photo(photos=photo_path, album_id='-', group_id=group_id)[0]
        vk_photo_url = f"https://vk.com/photo{photo['owner_id']}_{photo['id']}"
        vk.wall.post(owner_id=f"-{group_id}", message=caption, attachments=[vk_photo_url])
        return "пост опубликован"
    except:
        return "произошла ошибка во время публикации. Возможно указан неверный vk token или group id"

def post_text_to_group(group_id, message,token):
    try:
        vk_session = vk_api.VkApi(token=token)
        vk = vk_session.get_api()
        vk.wall.post(owner_id=f"-{group_id}", message=message)
        return "пост опубликован"
    except:return "произошла ошибка во время публикации. Возможно указан неверный vk token или group id"

