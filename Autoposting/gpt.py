import aiohttp
import asyncio
import time


async def generate_text(prompt, TOKEN):
    print(prompt, TOKEN)
    async with aiohttp.ClientSession() as session:
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {TOKEN}'
        }
        data = {
            "messages": [{"role": "user", "content": f'Сейчас ты будешь выполнять роль редактора. Напиши статью примерно на 1000 символов по теме:{prompt}'}],
            'max_tokens': 1024,
            'temperature': 0.7,
            'n': 1,
            'model':'gpt-3.5-turbo'
        }
        try:
            async with session.post('https://api.openai.com/v1/chat/completions', headers=headers, json=data) as response:
                response_json = await response.json()
                print(response_json)
                return response_json['choices'][0]['message']['content']
        except:
            return "err"


