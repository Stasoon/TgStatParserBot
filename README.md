1) Для парсинга сайта установить playwright (команды для Linux):
- python -m playwright install chromium
- python -m playwright install-deps
- sudo apt install ffmpeg 

2) Создать файл ".env" и в него добавить:
BOT_TOKEN=12345678:AbCDEF_gEodJGIfIeFDhjvUI...
ADMIN_IDS=123456,789101112

3) Чтобы парсинг мог работать, нужно авторизоваться на сайте https://tgstat.ru и затем скопировать в cookies.json куки браузера.
