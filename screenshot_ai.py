from playwright.sync_api import sync_playwright
from transformers import pipeline
from PIL import Image
import json

# Настраиваем модель captioner
captioner = pipeline("image-to-text", model="Salesforce/blip-image-captioning-large")

TARGET_URL = "https://character.ai/chat/dqSPWeWsnYjgZ1OwP1yZGXEYcaMxjNpGbOjS1Ch08jA"
COOKIES_FILE = 'cookies.json'

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()

    # Загружаем куки, если есть
    try:
        with open(COOKIES_FILE, 'r') as f:
            cookies = json.load(f)
            context.add_cookies(cookies)
        print("Куки загружены.")
    except FileNotFoundError:
        print("Куки не найдены. Нужно залогиниться вручную и сохранить куки.")

    print("Переход на страницу...")
    page.goto(TARGET_URL)

    # Если нужно, дождитесь загрузки
    page.wait_for_timeout(10000)

    # Проверьте, залогинены ли вы, например, по наличию элемента профиля
    # Можно вставить проверку или просто продолжить

    # Сделать скриншот
    screenshot_path = 'screenshot.png'
    page.screenshot(path=screenshot_path)
    print("Скриншот сделан.")

    # Обработка изображения
    image = Image.open(screenshot_path)
    description = captioner(image)[0]['generated_text']
    print("Описание:", description)

    # Найти поле для ввода сообщения
    try:
        input_box = page.wait_for_selector('textarea[placeholder="Сообщение..."]', timeout=15000)
        print("Нашел поле для ввода.")
        input_box.click()
        input_box.type(description)
        input_box.press('Enter')
        print("Сообщение отправлено.")
    except:
        print("Не удалось найти поле для ввода или отправить сообщение.")

    # Сохраняем куки перед закрытием
    cookies = context.cookies()
    with open(COOKIES_FILE, 'w') as f:
        json.dump(cookies, f)
    print("Куки сохранены.")

    # Оставляем браузер открытым
    input("Браузер остается открытым. Нажмите Enter, чтобы закрыть.")
    # Закрываем
    browser.close()