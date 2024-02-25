from typing import Dict
from aiofiles import open as aiopen
import orjson

from pathlib import Path
from .entities import (
    FlutterTranslate, FlutterTranslateTemplate,
    FlutterLocale
)


class FlutterTranslationManager:
    LANG_CODES = {"af", "sq", "ar", "hy", "be", "bs", "bg", "zh", "hr", "cs", "nl", "en", "et", "mk", "fa", "fi", "fr", "ka", "de", "el", "hu", "is", "id", "it", "ja", "kk", "ko", "lv", "lt", "ms", "mn", "ne", "nb", "pl", "pt", "ro", "ru", "sr", "sk", "sl", "so", "es", "sv", "tg", "th", "tr", "tk", "uk", "uz", "vi"}
    FILE_PATH = Path(__file__).absolute().parent.parent / "cache/flutter_i10n.json"
    
    def __init__(
        self, 
        default_code: str,
        default_translate: FlutterTranslate,
        definions: Dict[str, FlutterTranslateTemplate],
    ) -> None:
        self.definions = definions
        self._translations: Dict[str, FlutterTranslate] = {}
        self.default_code = default_code
        
        default_translate._translations.update({
            code: loc.translate
            for code, loc in self.definions.items()
        })
        self._translations[default_code] = default_translate
    
    @property
    def needed_locales(self):
        return self.LANG_CODES.difference(self._translations.keys())
    
    @property
    def all_locales(self):
        needed_keys = set(self.definions.keys())
        return [
            FlutterLocale(
                code=code,
                preview_name=loc.preview_name,
                available=(
                    loc.readonly or (
                        bool(loc.preview_name)
                        and needed_keys.issubset(loc._translations)
                    )
                ),
                readonly=loc.readonly,
            )
            for code, loc in self._translations.items()
        ]
    
    def rem_translation(self, code: str):
        if code not in self._translations or self._translations[code].readonly:
            raise KeyError("Invalid code")
        del self._translations[code]
    
    def translation(self, code: str, *, safe = False):
        if code not in self.LANG_CODES:
            raise KeyError("Unknown lang code!")
        elif code not in self._translations:
            if safe: return None
            self._translations[code] = FlutterTranslate.from_manager(self)
            
        loc = self._translations[code]
        if not safe and loc.readonly:
            raise KeyError("This locale - readonly!")
        return loc
    
    async def save(self):
        async with aiopen(self.FILE_PATH, "wb") as f:
            f.write(orjson.dumps({
                key: el.to_json()
                for key, el in self._translations.items()
                if not el.readonly
            }))
    
    def load(self):
        if not self.FILE_PATH.exists(): return
        try:
            with open(self.FILE_PATH, "rb") as f:
                data = orjson.loads(f.read())
                self._translations.update({
                    key: FlutterTranslate.from_json(self, json)
                    for key, json in data.items()
                })
        except:
            pass


APP_LOCALE = FlutterTranslationManager(
    default_code="ru", 
    default_translate=FlutterTranslate("Русский"), 
    definions={
        # SSO Layout
        "personal_area": FlutterTranslateTemplate("Личный кабинет"),
        "accept_policy": FlutterTranslateTemplate("Регистрируясь, Вы соглашаетесь с нашей \n правовой политикой"),
        
        # Enter phone side
        "select_phone_code": FlutterTranslateTemplate("Выберите телефонный код"),
        "incorrect_password_range": FlutterTranslateTemplate("Пароль должен быть в диапазоне {range} символов"),
        "incorrect_password": FlutterTranslateTemplate("Пароль неверен!"),
        "required_update": FlutterTranslateTemplate("Ошибка работы с сервером, скорее всего вам необходимо обновить приложение"),
        "account_blocked": FlutterTranslateTemplate("Данный аккаунт заблокирован"),
        "session_reject": FlutterTranslateTemplate("Ваша сессия была анулирована"),
        
        "enter_phone_title": FlutterTranslateTemplate("Укажите пожалуйста, \nномер телефона и пароль \nдля авторизации / регистрации"),
        "enter_login_password": FlutterTranslateTemplate("Введите ваш пароль"),
        "change_lang": FlutterTranslateTemplate("Сменить язык"),
        "lang_polyfill": FlutterTranslateTemplate("Язык: {name}"),
        
        "switch_role": FlutterTranslateTemplate("Сменить роль"),
        "role_polyfill": FlutterTranslateTemplate("Роль: {name}"),
        
        "expert": FlutterTranslateTemplate("Эксперт"),
        "client": FlutterTranslateTemplate("Клиент"),
        
        # Registration side
        "referal_code_description": FlutterTranslateTemplate("Реферальный код - цифро-буквенная последовательность из {count} символов"),
        "referer_not_found": FlutterTranslateTemplate("Реферальный код введен неверно, пользователь не найден!"),
        "password_confirm_difference": FlutterTranslateTemplate("Пароль и подтверждение пароля не совпадают"),
        "any_field_incorrect": FlutterTranslateTemplate("Одно из полей неверно!"),
        
        "name_field": FlutterTranslateTemplate("Имя"),
        "surname_field": FlutterTranslateTemplate("Фамилия"),
        "email_field": FlutterTranslateTemplate("Email"),
        "create_password_field": FlutterTranslateTemplate("Придумайте пароль"),
        "repeat_password_field": FlutterTranslateTemplate("Повторите пароль"),
        "current_password_field": FlutterTranslateTemplate("Текущий пароль"),
        "new_password_field": FlutterTranslateTemplate("Новый пароль"),
        
        "change_password_title": FlutterTranslateTemplate("Смена пароля"),
        "error_change_password": FlutterTranslateTemplate("Отклонено! Пароль неверен."),
        "enter_referal_code": FlutterTranslateTemplate("Введите реферальный код"),
        "registration_required_fill": FlutterTranslateTemplate("Вам необходимо пройти регистрацию!\n Для этого заполните \nвсе необходимые поля."),
        
        # Заголовки вкладок
        "main_page": FlutterTranslateTemplate(
            "Главная",
            description="Заголовок главной вкладки у клиента"
        ),
        "news_page": FlutterTranslateTemplate(
            "Новости",
            description="Заголовок новостной вкладки"
        ),
        "bonus_page": FlutterTranslateTemplate(
            "Мои бонусы",
            description="Заголовок вкладки бонунов клиента"
        ),
        "finance_page": FlutterTranslateTemplate(
            "Мои финансы",
            description="Заголовок вкладки финансов эксперта"
        ),
        "chat_page": FlutterTranslateTemplate(
            "Чат",
            description="Заголовок вкладки чатов"
        ),
        "profile_page": FlutterTranslateTemplate(
            "Профиль",
            description="Заголовок вкладки профиля"
        ),
        "schedule_page": FlutterTranslateTemplate(
            "Расписание",
            description="Заголовок вкладки расписания у эксперта"
        ),
        
        # Заголовки страниц
        "hello": FlutterTranslateTemplate("Привет"),
        "main_title": FlutterTranslateTemplate(
            "Найди своего эксперта",
            description="Заголовок вкладки поиска у клиента"
        ),
        "news_title": FlutterTranslateTemplate(
            "Будь в курсе новостей",
            description="Заголовок вкладки с новостями"
        ),
        "actual_chat_title": FlutterTranslateTemplate("Актуальные"),
        "archive_chat_title": FlutterTranslateTemplate("Архив"),
        
        # Статусы чата
        "pre_payment_status": FlutterTranslateTemplate("Требуется оплата"),
        "archived_status": FlutterTranslateTemplate("Архив, ждет оценки"),
        "in_telegram": FlutterTranslateTemplate("В телеграм"),
        "can_start_status": FlutterTranslateTemplate("Можно начать"),
        "cancel_payment": FlutterTranslateTemplate("Отменить оплату"),
        
        "not_time_for_lesson": FlutterTranslateTemplate("Отклонено, скорее всего время урока еще не настало."),
        "success_cancel": FlutterTranslateTemplate("Успешно отменено!"),
        "success_copy": FlutterTranslateTemplate("Успешно скопировано!"),
        
        # Доп надписи главной страницы
        "news_mini_redirect": FlutterTranslateTemplate(
            "Смотреть все новости",
            description="Переход из главной страницы в новости"
        ),
        "sort": FlutterTranslateTemplate("Сортировка"),
        "sort_by_rating": FlutterTranslateTemplate("По рейтингу"),
        "sort_by_count": FlutterTranslateTemplate("По популярности"),
        
        "schedule_edit_coming_days": FlutterTranslateTemplate("Смена расписания доступна только на предстоящие дни!"),
        "free_today_tag": FlutterTranslateTemplate("Свободны сегодня"),
        "free_today_description": FlutterTranslateTemplate("Показать экспертов \nсвободных сегодня"),
        "select_range": FlutterTranslateTemplate("Выбрать период"),
        "from": FlutterTranslateTemplate(
            "с",
            description="\"От\". Пример: \"С 20 по 30\""
        ),
        "to": FlutterTranslateTemplate(
            "по",
            description="\"До\". Пример: \"С 20 по 30\""
        ),
        "clean": FlutterTranslateTemplate("Очистить"),
        "rub": FlutterTranslateTemplate("руб"),
        "reviews": FlutterTranslateTemplate("Отзывы"),
        "buy": FlutterTranslateTemplate("Приобрести"),
        "booking": FlutterTranslateTemplate("Забронировать"),
        "withdraw_all_time": FlutterTranslateTemplate("Выведено за все время"),
        "included_comission": FlutterTranslateTemplate("С учетом комиссии сервиса"),
        "withdraw_history": FlutterTranslateTemplate("История выплат"),
        "withdrawal_count": FlutterTranslateTemplate("Выведено на все время"),
        "withdrawal_allowed_count": FlutterTranslateTemplate("Доступно для \nвывода"),
        "request_withdraw_title": FlutterTranslateTemplate("Заказать выплату"),
        "service_calendar": FlutterTranslateTemplate("Календарь услуг"),
        
        "add_service": FlutterTranslateTemplate("Добавить услугу"),
        "success": FlutterTranslateTemplate("Успешно"),
        "request_cancelled": FlutterTranslateTemplate("Запрос отклонен!"),
        
        # Перевод для времени отдыха у эксперта
        "rest": FlutterTranslateTemplate("Отдых"),
        "hour_already_busy": FlutterTranslateTemplate("Данный час уже занят"),
        "working_mode": FlutterTranslateTemplate("Режим работы"),
        "take_day_off": FlutterTranslateTemplate("Сделать выходным"),
        "make_day_work": FlutterTranslateTemplate("Сделать рабочим"),
        "working_hours": FlutterTranslateTemplate("Рабочие часы"),
        "add_rest_hour": FlutterTranslateTemplate("Добавить час отдыха"),
        "rest_hours": FlutterTranslateTemplate("Часы отдыха"),
        "remove_rest_hour": FlutterTranslateTemplate("Удалить время отдыха"),
        "weekend": FlutterTranslateTemplate("Выходной"),
        
        # Перевод для сеансов у эксперта
        "sessions": FlutterTranslateTemplate("Сеансы"),
        "save": FlutterTranslateTemplate("Сохранить"),
        "remove": FlutterTranslateTemplate("Удалить"),
        "cancel": FlutterTranslateTemplate("Отменить"),
        "sessions_client_processing": FlutterTranslateTemplate("Клиент в процессе оплаты"),
        "invalid_data": FlutterTranslateTemplate("Ошибка, проверьте правильность данных!"),
        
        "schedule_search_placeholder": FlutterTranslateTemplate("Я ищу..."),
        "about_me": FlutterTranslateTemplate("Обо мне"),
        "personal_info": FlutterTranslateTemplate("Личная информация"),
        
        # Перевод для бонусной программы
        "bonus_program": FlutterTranslateTemplate("Бонусная программа"),
        "bonus_points": FlutterTranslateTemplate("Мои бонусные \nбаллы"),
        "your_referal_code": FlutterTranslateTemplate("Ваш реферальный код"),
        "total_invited": FlutterTranslateTemplate("Всего приглашено"),
        "my_referals": FlutterTranslateTemplate("Мои рефералы"),
        "about_referal": FlutterTranslateTemplate("Подробнее о реферальной программе"),
        "last_payments": FlutterTranslateTemplate("Последние платежи"),
        "has_no_referals": FlutterTranslateTemplate("У вас нет рефералов"),
        "income": FlutterTranslateTemplate("Доход"),
        "more": FlutterTranslateTemplate("Подробнее"),
        "sessions_archive": FlutterTranslateTemplate("Архив сеансов"),
        "sessions_archive_description": FlutterTranslateTemplate("Посмотрите архив своих сеансов"),
        "change_password": FlutterTranslateTemplate("Сменить пароль"),
        "price_field": FlutterTranslateTemplate("Стоимость"),
        "exit": FlutterTranslateTemplate("Выход"),
        
        "name_not_in_range": FlutterTranslateTemplate("Длина имени должна находиться в диапазоне {range} символов"),
        "surname_not_in_range": FlutterTranslateTemplate("Длина фамилия должна находиться в диапазоне {range} символов"),
        "email_not_in_range": FlutterTranslateTemplate("Длина фамилия должна находиться в диапазоне {range} символов"),
        "incorrect_email_format": FlutterTranslateTemplate("Длина фамилия должна находиться в диапазоне {range} символов"),
        
        "category_not_selected": FlutterTranslateTemplate("Категория не выбрана"),
        "title_not_in_range": FlutterTranslateTemplate("Длина названия должна находиться в диапазоне {range} символов"),
        "price_not_in_range": FlutterTranslateTemplate("Цена должна составлять хотя-бы {count} руб"),
        "description_not_in_range": FlutterTranslateTemplate("Описание не может быть пустым и должно быть длинной {range} символов"),
        "invalid_telegram_link": FlutterTranslateTemplate("Ссылка телеграм некорректна"),
        "invalid_telegram_prefix": FlutterTranslateTemplate("Телеграм ссылка должна начинаться с"),
        "serverside_validate_error": FlutterTranslateTemplate("Сервер отклонил запрос, проверьте правильность данных"),
        
        "add_service_title": FlutterTranslateTemplate("Добавление услуги"),
        "service_category": FlutterTranslateTemplate("Категория услуги"),
        "service_name": FlutterTranslateTemplate("Название услуги"),
        "service_price": FlutterTranslateTemplate("Цена за услугу"),
        "through_telegram": FlutterTranslateTemplate("Работа через телеграм"),
        "telegram": FlutterTranslateTemplate("Телеграм"),
        "service_in_telegram": FlutterTranslateTemplate("Добавить телеграм канал"),
        "service_description": FlutterTranslateTemplate("Описание услуги"),
        "about_expert": FlutterTranslateTemplate("Об эксперте"),
        "service": FlutterTranslateTemplate("Услуга"),
        "rating": FlutterTranslateTemplate("Рейтинг"),
        "sessions_count": FlutterTranslateTemplate("Кол-во уроков"),
        
        "service_not_selected": FlutterTranslateTemplate("Услуга не выбрана!"),
        "time_not_selected": FlutterTranslateTemplate("Время не выбрано!"),
        "time_already_booking": FlutterTranslateTemplate("Данное время возможно уже занято, попробуйте другое!"),
        "not_paid_error": FlutterTranslateTemplate("Сервер заблокировад запрос. Возможно у вас есть не оплаченные заказы, перейдите в чат"),
        
        # Перевод для чата
        "income_call": FlutterTranslateTemplate("Входящий звонок"),
        "outcome_call": FlutterTranslateTemplate("Исходящий звонок"),
        "call_ended": FlutterTranslateTemplate("Звонок завершен!"),
        "big_file_size": FlutterTranslateTemplate("Размер файла слишком большой. Макс: {size}"),
        "fail_connect": FlutterTranslateTemplate("Попытка соединения неудачна!"),
        "lost_connection": FlutterTranslateTemplate("Потеряно соединение с сервером!"),
        "session_client_preview": FlutterTranslateTemplate("Консультация еще не началась, ожидайте. \nЭксперт должен ее начать в {hour}:00"),
        "session_started": FlutterTranslateTemplate("Консультация началась"),
        "session_ended": FlutterTranslateTemplate("Консультация закончилась"),
        "chat_join": FlutterTranslateTemplate("{name} присоединился"),
        "chat_leave": FlutterTranslateTemplate("{name} вышел"),
        "chat_input_placeholder": FlutterTranslateTemplate("Сообщение"),
        "expert_registration": FlutterTranslateTemplate("Регистрация к эксперту"),
        "use_bonuses": FlutterTranslateTemplate("Использовать бонусные рубли (доступно: {count})"),
        "max_bonuses": FlutterTranslateTemplate("Не более {count}р", description="Ограничение на кол-во использования бонусов для оплаты"),
        "bonus_rubles": FlutterTranslateTemplate("Бонусные рубли"),
        "pay": FlutterTranslateTemplate("Оплатить"),
        "faq": FlutterTranslateTemplate("FAQ"),
        "referals_list": FlutterTranslateTemplate("Список рефералов"),
        "search_referals": FlutterTranslateTemplate("Поиск рефералов"),
        "income": FlutterTranslateTemplate("Доход"),
        "incorrect_card": FlutterTranslateTemplate("Неверно введена карта"),
        "incorrect_bank_name": FlutterTranslateTemplate("Название банка должно быть в диапазоне {range} символов"),
        "incorrect_cardholder": FlutterTranslateTemplate("ФИО должно быть в диапазоне {range} символов"),
        "withdraw_cancelled": FlutterTranslateTemplate("Запрос отклонен. Скорее всего у вас маленький баланс (минимальная сумма вывода {count}), либо вы уже запросили вывод."),
        "card_number_field": FlutterTranslateTemplate("Номер карты"),
        "bank_name_field": FlutterTranslateTemplate("Банк"),
        "full_name_field": FlutterTranslateTemplate("ФИО"),
        
        "session_feedback": FlutterTranslateTemplate("Как прошла ваша\n консультация?"),
        "request_feedback": FlutterTranslateTemplate("Оставьте отзыв"),
        "send": FlutterTranslateTemplate("Отправить"),
        "connecting": FlutterTranslateTemplate("Соединение"),
        "change_avatar": FlutterTranslateTemplate("Сменить аватар"),
        
        "freetime": FlutterTranslateTemplate("Свободное время"),
        "start_work": FlutterTranslateTemplate("Начало работы"),
        "end_work": FlutterTranslateTemplate("Конец работы"),
        "processing": FlutterTranslateTemplate("В обработке"),
        "paid": FlutterTranslateTemplate("Оплачено"),
        "cancelled": FlutterTranslateTemplate("Отменено"),
        
        "withdraw": FlutterTranslateTemplate("Вывод на карту"),
        "select_phone_code": FlutterTranslateTemplate("Выберите телефонный код"),
        "enter_phone": FlutterTranslateTemplate("Укажите пожалуйста, \nномер телефона \nдля авторизации / регистрации"),
        "enter_password": FlutterTranslateTemplate("Введите ваш пароль"),
        
        "next": FlutterTranslateTemplate("Далее"),
        "change_lang_title": FlutterTranslateTemplate("Выберите язык"),
        "success_change": FlutterTranslateTemplate("Успешно изменено!"),
        "change": FlutterTranslateTemplate("Сменить"),
    }
)
