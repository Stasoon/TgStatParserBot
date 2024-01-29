import os.path
import re
import json
from dataclasses import dataclass

import asyncio
from playwright.async_api import async_playwright, Page, ElementHandle

from src.utils import logger


@dataclass
class PostData:
    # Информация об источнике
    source_title: str
    source_url: str
    source_subscribers_count: int

    # Информация о посте
    post_url: str
    publication_date: str
    views_count: int | str = 0
    reposts_count: int | str = 0


class AuthorizationNeeded(Exception):
    def __init__(self, authorization_link=None):
        message = f'Требуется авторизация! Перейдите по ссылке: {authorization_link}'
        super().__init__(message)
        self.authorization_link = authorization_link


class TgStatParser:
    BASE_URL = 'https://tgstat.ru/search'

    @classmethod
    async def search_key_word(cls, key: str) -> list[PostData]:
        async with async_playwright() as p:
            # Создаём экземпляр браузера и страницу
            browser = await p.chromium.launch()
            page = await browser.new_page()

            await cls.__add_cookies(page=page)
            await page.goto(cls.BASE_URL)

            # Осуществляем поиск
            try:
                await cls.__make_search(page=page, search_key=key)
            except AuthorizationNeeded as e:
                await cls.__handle_auth_error(page=page, authorization_link=e.authorization_link)
                await cls.__make_search(page=page, search_key=key)

            # Ввод даты, с которой искать посты
            # start_date_selector = '#startdate'
            # start_date = datetime.date.today() - datetime.timedelta(days=30)
            # start_date_element = await page.wait_for_selector(start_date_selector)
            # await start_date_element.type(text=f"{start_date.day}.{start_date.month}.{start_date.year}")

            # Ждём загрузки постов
            post_selector = 'div.post-container'
            await page.wait_for_selector(selector=post_selector, timeout=30_000)

            # Собираем посты
            posts = []

            for post_element in await page.query_selector_all(selector=post_selector):
                try:
                    post = await cls.__scrap_post_data(page=page, post_element=post_element)
                except Exception as e:
                    logger.error(e)
                else:
                    posts.append(post)

            await browser.close()

        return posts

    @staticmethod
    async def __add_cookies(page: Page):
        if os.path.exists('cookies.json'):
            with open('cookies.json', 'r') as f:
                cookies = json.load(f)
                await page.context.add_cookies(cookies)

    @staticmethod
    async def __update_cookies_in_storage(page: Page):
        cookies = await page.context.cookies()
        with open('cookies.json', 'w') as f:
            json.dump(obj=cookies, fp=f, indent=4)

    @classmethod
    async def __handle_auth_error(cls, page: Page, authorization_link: str):
        logger.warning('Требуется авторизация!', authorization_link)
        await asyncio.sleep(60)

        await cls.__update_cookies_in_storage(page=page)
        await page.reload()

    @classmethod
    async def __make_search(cls, page: Page, search_key: str):
        # Ищем поле ввода и вставляем ключ поиска
        input_selector = 'input.form-control.form-control-lg'
        await page.wait_for_selector(input_selector)
        await page.type(input_selector, search_key)
        await page.wait_for_timeout(20)

        # Нажимаем кнопку поиска
        button_selector = 'button.btn-info'
        search_button = await page.query_selector(button_selector)
        await search_button.click(timeout=60_000)
        await page.wait_for_timeout(300)

        # Если требуется авторизация
        auth_window = await page.query_selector('a.auth-btn')
        if auth_window:
            authorization_link = await auth_window.get_property('href')
            raise AuthorizationNeeded(authorization_link=authorization_link)

        # Пытаемся сделать сортировку по популярности
        try:
            sort_by_views_button_selector = 'input.sort-button-js[data-metric="views"]'
            sort_by_views_button = await page.wait_for_selector(sort_by_views_button_selector)
            sort_by_views_button = await sort_by_views_button.query_selector('xpath=..')
            await sort_by_views_button.click()
            await page.wait_for_selector('div.posts-list[style*="opacity: 1;"]')
        except Exception as e:
            print('не получилось сортировать по популярности', e)

    @classmethod
    async def __scrape_post_wrapper(cls, page: Page, post_element: ElementHandle) -> PostData | None:
        try:
            return await cls.__scrap_post_data(page=page, post_element=post_element)
        except Exception as e:
            logger.error(f"Error while scraping post: {e}")
            return None

    @classmethod
    async def __scrap_post_data(cls, page: Page, post_element: ElementHandle) -> PostData:
        # Название источника
        title_selector = 'a.text-dark'
        title_element = await post_element.query_selector(title_selector)
        source_title = (await title_element.text_content()).strip()

        # Ссылка на источник
        source_url_ = str(await title_element.get_property('href'))
        domain = re.search(r'/([^/]+)$', source_url_).group(1)
        source_url = domain.replace('@', '', 1) if domain.startswith('@') else f"+{domain}"
        source_url = f"https://t.me/{source_url}"

        # Дата публикации
        date_selector = 'p.text-muted.m-0 > small'
        date_element = await post_element.query_selector(date_selector)
        date_published = await date_element.text_content()

        # Просмотры
        views_selector = 'div.col.col-12.d-flex > a'
        views_element = await post_element.query_selector(views_selector)
        views_str = (await views_element.text_content()).strip()

        # Репосты
        reposts_selector = 'div.col.col-12.d-flex > span'
        reposts_element = await post_element.query_selector(reposts_selector)
        reposts_str = (await reposts_element.text_content()).strip()

        # Ссылка на пост
        post_link_selector = 'div.ml-auto > a.btn'
        post_link_element = await post_element.query_selector(post_link_selector)
        post_link_str = str(await post_link_element.get_property('href'))
        post_number = post_link_str.split('/')[-1]
        post_url = f"{source_url}/{post_number}"

        ### Получение инфо о том, сколько подписчиков у канала, !но ломается контекст
        # try:
        #     await page.goto(source_url_)
        #     subs_count_selector = 'h2.mb-1.text-dark'
        #     await post_element.wait_for_selector(subs_count_selector)
        #     subs_element = await page.query_selector(subs_count_selector)
        #     subs_count = await subs_element.text_content()
        #     source_subscribers_count = int(subs_count) if subs_count and subs_count.isdigit() else 0
        # finally:
        #     await page.go_back()
        # print(source_title, source_url, post_url)

        return PostData(
            source_title=source_title, source_url=source_url, source_subscribers_count=0,
            publication_date=date_published,
            post_url=post_url, views_count=views_str, reposts_count=reposts_str
        )
