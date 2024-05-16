import requests
import logging

logging.basicConfig(filename='logs.txt', level=logging.ERROR, format="%(asctime)s FILE: %(filename)s IN: %(funcName)s MESSAGE: %(message)s", filemode="w")

IAM_TOKEN = ''
FOLDER_ID = ''
PROMT = 'Ты дружелюбный помочник для ответа на самые разные задачи. Старайся давать креативние и понятные ответы. Отвечай коротко, по 2 или 3 предложения. Отвечай на русском языке простым языком.'

def create_new_token():
    global IAM_TOKEN
    try:
        """Создание нового токена"""
        metadata_url = "http://169.254.169.254/computeMetadata/v1/instance/service-accounts/default/token"
        headers = {"Metadata-Flavor": "Google"}
        response = requests.get(metadata_url, headers=headers)
        IAM_TOKEN = response.json()['access_token']
    except:
        pass

# Выполняем запрос к YandexGPT
def ask_gpt(text):
    try:
        iam_token = IAM_TOKEN
        folder_id = FOLDER_ID  # Folder_id для доступа к YandexGPT

        headers = {
            'Authorization': f'Bearer {iam_token}',
            'Content-Type': 'application/json'
        }
        data = {
        "modelUri": f"gpt://{folder_id}/yandexgpt-lite",  # модель для генерации текста
        "completionOptions": {
            "stream": False,  # потоковая передача частично сгенерированного текста выключена
            "temperature": 0.6,  # чем выше значение этого параметра, тем более креативными будут ответы модели (0-1)
            "maxTokens": "200"  # максимальное число сгенерированных токенов, очень важный параметр для экономии токенов
        },
        "messages": [
            {
                "role": "system",  # пользователь спрашивает у модели
                "text": PROMT  # передаём текст, на который модель будет отвечать
            },
            {
                "role": "user",  # пользователь спрашивает у модели
                "text": text  # передаём текст, на который модель будет отвечать
            }
        ]
        }

        # Выполняем запрос к YandexGPT
        response = requests.post("https://llm.api.cloud.yandex.net/foundationModels/v1/completion",
                             headers=headers,
                             json=data)

        # Проверяем, не произошла ли ошибка при запросе
        if response.status_code == 200:
            # достаём ответ YandexGPT
            text = response.json()["result"]["alternatives"][0]["message"]["text"]
            return text
        else:
            logging.error(response)
            raise RuntimeError(
                'Invalid response received: code: {}, message: {}'.format(
                    {response.status_code}, {response.text}
                )
            )
    except:
        return 'Ошибка. В скором времени проблема будет исправлена. Попробуйте говорить громце и более чётко.'


def stt(data):
    try:
        # iam_token, folder_id для доступа к Yandex SpeechKit
        iam_token = IAM_TOKEN
        folder_id = FOLDER_ID

        # Указываем параметры запроса
        params = "&".join([
            "topic=general",  # используем основную версию модели
            f"folderId={folder_id}",
            "lang=ru-RU"  # распознаём голосовое сообщение на русском языке
        ])

        # Аутентификация через IAM-токен
        headers = {
            'Authorization': f'Bearer {iam_token}',
        }

        # Выполняем запрос
        response = requests.post(
            f"https://stt.api.cloud.yandex.net/speech/v1/stt:recognize?{params}",
            headers=headers,
            data=data
        )

        # Читаем json в словарь
        decoded_data = response.json()
        # Проверяем, не произошла ли ошибка при запросе
        if decoded_data.get("error_code") is None:
            return decoded_data.get("result")  # Возвращаем статус и текст из аудио
        else:
            logging.error(decoded_data)
            return "При запросе в SpeechKit возникла ошибка"
    except:
        logging.error('Ошибка при распознавание речи')
        return "При запросе в SpeechKit возникла ошибка"

def tts(text: str):
    try:
        # Токен, Folder_id для доступа к Yandex SpeechKit
        iam_token = IAM_TOKEN
        folder_id = FOLDER_ID

        # Аутентификация через IAM-токен
        headers = {
            'Authorization': f'Bearer {iam_token}',
        }
        data = {
            'text': text,  # текст, который нужно преобразовать в голосовое сообщение
            'lang': 'ru-RU',  # язык текста - русский
            'voice': 'filipp',  # голос Филлипа
            'folderId': folder_id,
        }
        # Выполняем запрос
        response = requests.post('https://tts.api.cloud.yandex.net/speech/v1/tts:synthesize', headers=headers, data=data)

        if response.status_code == 200:
            return response.content  # Возвращаем голосовое сообщение
        else:
            logging.error(response)
            return f"При запросе в SpeechKit возникла ошибка {response.status_code}"
    except:
        logging.error('Ошибка при работе с синтезом речи.')
        return f"При запросе в SpeechKit возникла ошибка {response.status_code}"

def count_all_tokens(messages):
    try:
        iam_token = IAM_TOKEN
        folder_id = FOLDER_ID  # Folder_id для доступа к YandexGPT
        headers = {
            'Authorization': f'Bearer {iam_token}',
           'Content-Type': 'application/json'
        }

        data = {
            "modelUri": f"gpt://{folder_id}/yandexgpt/latest",
            'maxTokens': 2000,
            'messages': []
        }

        for ell in messages:
            data['messages'].append(ell)

        count_tokens_res = requests.post(
            "https://llm.api.cloud.yandex.net/foundationModels/v1/tokenizeCompletion",
            json=data,
            headers=headers
            ).json()['tokens']

        return len(count_tokens_res)
    except:
        logging.error('Ошибка при подсчете токенов.')
        return 0