import sqlite3


class Database:
    def __init__(self, db_name):

        self.connection = sqlite3.connect(db_name)
        self.cursor = self.connection.cursor()
        self.create_tables()

    def create_tables(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                user_id INTEGER UNIQUE,
                state TEXT,
                channels TEXT,
                naming TEXT,
                vk_token TEXT
            )
        """)
        self.cursor.execute("""
                    CREATE TABLE IF NOT EXISTS posts (
                        id INTEGER PRIMARY KEY,
                        user_id INTEGER UNIQUE,
                        text TEXT,
                        image_path TEXT,
                        date TEXT,
                        channels TEXT
                    )
        """)
        self.connection.commit()

    def add_user(self, user_id):
        self.cursor.execute("INSERT OR IGNORE INTO users (user_id, state, channels, naming, vk_token) VALUES (?, ?, ?, ?, ?)", (user_id, '', '', '',''))
        self.cursor.execute("INSERT OR IGNORE INTO posts (user_id, text, image_path, date, channels) VALUES (?, ?, ?, ?, ?)",(int(user_id), "", "", "", ""))
        self.connection.commit()

    def remove_user(self, user_id):
        self.cursor.execute("DELETE FROM users WHERE user_id=?", (user_id,))
        self.connection.commit()

    def get_user(self, user_id):
        self.cursor.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
        return self.cursor.fetchone()


    def update_state(self, user_id, state):
        self.cursor.execute("UPDATE users SET state=? WHERE user_id=?", (state, user_id))
        self.connection.commit()
        return
    def get_state(self, user_id):
        self.cursor.execute("SELECT state FROM users WHERE user_id=?", (user_id,))
        return self.cursor.fetchone()[0]
    def close(self):
        self.connection.close()
        return

    def set_post(self, user_id, text="", image_path="", date="", channels=""):
        self.cursor.execute("UPDATE posts SET text=?, image_path=?, date=?, channels=? WHERE user_id=?", (text, image_path, date, channels, int(user_id)))
        self.connection.commit()
    def set_post_text(self, user_id, text=""):
        self.cursor.execute("UPDATE posts SET text=? WHERE user_id=?", (text, int(user_id)))
        self.connection.commit()
    def set_post_image_path(self, user_id, image_path=""):
        self.cursor.execute("UPDATE posts SET image_path=? WHERE user_id=?", (image_path, int(user_id)))
        self.connection.commit()
    def get_post(self, user_id):
        self.cursor.execute("SELECT * FROM posts WHERE user_id=?", (user_id,))
        post= self.cursor.fetchone()
        return {"text": post[2], "image_path": post[3], "date": post[4], "channels": post[5]}

    def get_channels(self, user_id):
        self.cursor.execute("SELECT channels FROM users WHERE user_id=?", (user_id,))
        return self.cursor.fetchone()[0].split('&')

    def get_channels_str(self, user_id):
        self.cursor.execute("SELECT channels FROM users WHERE user_id=?", (user_id,))
        return self.cursor.fetchone()[0]
    def set_channels(self, user_id, channels):
        t=''
        for i in range(channels):
            t+=i+'&'
        self.cursor.execute("UPDATE users SET channels=? WHERE user_id=?", (t[:-1], user_id,))
        self.connection.commit()
        return

    def rem_channel(self, user_id, channel):
        channels=self.get_channels(user_id)
        channels.remove(channel)
        txt=''
        for i in channels:
            txt+=i+'&'
        self.cursor.execute("UPDATE users SET channels=? WHERE user_id=?", (txt[:-1], user_id,))
        self.connection.commit()
        allgroup=self.get_all_group_information(user_id).split(",")
        new=''
        for i in allgroup:
            if (channel+':') not in i:
                new+=i+','
        self.cursor.execute("UPDATE users SET naming=? WHERE user_id=?", (new, user_id,))
        self.connection.commit()
        return




    def add_channel(self, user_id, channel):
        t = self.get_channels_str(user_id)
        if t!="":t += '&'+channel
        else: t+=channel
        print(t)
        self.cursor.execute("UPDATE users SET channels=? WHERE user_id=?", (t, user_id,))
        self.connection.commit()
        return

    def get_all_group_information(self, user_id):
        self.cursor.execute("SELECT naming FROM users WHERE user_id=?", (user_id,))
        return self.cursor.fetchone()[0]

    def add_group_information(self, user_id, group_name, social, type, url):
        if self.get_all_group_information(user_id) != '':
            st=f',{group_name}:{social}:{type}:{url}'
        else:
            st = f'{group_name}:{social}:{type}:{url}'
        s=self.get_all_group_information(user_id)
        self.cursor.execute("UPDATE users SET naming=? WHERE user_id=?", (s+st, user_id,))
        self.connection.commit()
        return


    def get_vk_token(self, user_id):
        self.cursor.execute("SELECT vk_token FROM users WHERE user_id=?", (user_id,))
        return self.cursor.fetchone()[0]

    def update_vk_token(self, user_id, token):
        self.cursor.execute("UPDATE users SET vk_token=? WHERE user_id=?", (token, user_id))
        self.connection.commit()
        return
    def get_group_information(self,user_id, group_name):
        groups=(self.get_all_group_information(user_id)).split(",")
        tx=''
        for i in groups:
            if group_name in i:tx=i.split(':')
        return {"social":tx[1], "type":tx[2], "url":tx[3]}


    # def update_prev_message(self, user_id, prev_message_id):
    #     self.cursor.execute("UPDATE users SET prev_message_id=? WHERE chat_id=?", (prev_message_id, user_id))
    #     self.connection.commit()
    #
    # def get_prev_message(self, user_id):
    #     self.cursor.execute("SELECT prev_message_id FROM users WHERE chat_id=?", (user_id,))
    #     return self.cursor.fetchone()

    #method for saving photos to the database for the user (for each user a list of file names with photos)

    # Другие методы для работы с базой данных
