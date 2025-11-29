import sqlite3
from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
import threading


class API_db():
    def __init__(self):
        self.conn = sqlite3.connect('api.db', check_same_thread=False)
        self.cursor = self.conn.cursor()
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS API (
        api_key TEXT PRIMARY KEY)''')
        self.conn.commit()

    def check_api(self, api_key):
        res = self.cursor.execute('''SELECT api_key FROM API WHERE api_key = ?''', (api_key,)).fetchone()
        if res is not None:
            return True
        return False

    def add_api_key(self, api_key):
        try:
            self.cursor.execute('''INSERT INTO API (api_key) VALUES(?)''', (api_key, ))
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False


class TariffPlan:
    def __init__(self):
        self.conn = sqlite3.connect('database.db', check_same_thread=False)
        self.cursor = self.conn.cursor()
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS TariffPlan (
            user_login TEXT NOT NULL PRIMARY KEY,
            password TEXT NOT NULL,
            tariff TEXT NOT NULL,
            end_date_tariff DATETIME,
            number_of_count INTEGER NOT NULL,
            max_number_of_count INTEGER NOT NULL,
            API_perm BOOLEAN NOT NULL,
            history_life INTEGER NOT NULL,
            history TEXT)''')
        self.conn.commit()

        self.scheduler = BackgroundScheduler()
        self.start_scheduler()

    def get_tariff_settings(self, tariff_name):
        tariff_settings = {
            "Бесплатный": {
                "max_requests": -1,
                "api_perm": False,
                "history_life_days": 30,
                "price": 0,
                "duration_days": None,
                "features": {
                    "Базовый SEO анализ": True,
                    "GEO анализ": True,
                    "Основные рекомендации": True,
                    "Расширенная аналитика": False,
                    "Приоритетная поддержка": False
                }
            },
            "Pro": {
                "max_requests": 50,
                "api_perm": False,
                "history_life_days": 90,
                "price": 990,
                "duration_days": 30,
                "features": {
                    "Базовый SEO анализ": True,
                    "GEO анализ": True,
                    "Основные рекомендации": True,
                    "Расширенная аналитика": True,
                    "Приоритетная поддержка": True,
                    "История анализов": True
                }
            },
            "Бизнес": {
                "max_requests": -1,
                "api_perm": True,
                "history_life_days": 365,
                "price": 2990,
                "duration_days": 30,
                "features": {
                    "Базовый SEO анализ": True,
                    "GEO анализ": True,
                    "Основные рекомендации": True,
                    "Расширенная аналитика": True,
                    "Приоритетная поддержка": True,
                    "История анализов": True,
                    "API доступ": True,
                    "White-label отчеты": True,
                    "Персональный менеджер": True,
                    "Кастомные метрики": True
                }
            }
        }
        return tariff_settings.get(tariff_name, tariff_settings["Бесплатный"])

    def register_user(self, user_login, password):
        try:
            tariff_settings = self.get_tariff_settings("Бесплатный")

            self.cursor.execute('''INSERT INTO TariffPlan 
                (user_login, password, tariff, end_date_tariff, number_of_count, 
                 max_number_of_count, API_perm, history_life, history) 
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                                (user_login, password, "Бесплатный", None, 0,
                                 tariff_settings["max_requests"], tariff_settings["api_perm"],
                                 tariff_settings["history_life_days"], ""))

            self.conn.commit()
            return True, "Пользователь успешно зарегистрирован с бесплатным тарифом"

        except sqlite3.IntegrityError:
            return False, "Пользователь с таким логином уже существует"
        except Exception as e:
            return False, f"Ошибка при регистрации: {str(e)}"

    def purchase_tariff(self, user_login, tariff_name, payment_successful=True):
        if not payment_successful:
            return False, "Оплата не прошла"

        self.cursor.execute('SELECT password FROM TariffPlan WHERE user_login = ?', (user_login,))
        user_exists = self.cursor.fetchone()

        if not user_exists:
            return False, "Пользователь не найден"

        tariff_settings = self.get_tariff_settings(tariff_name)

        if tariff_name == "Бесплатный":
            end_date = None
        else:
            end_date = datetime.now() + timedelta(seconds=30)

        try:
            if end_date:
                self.cursor.execute('''UPDATE TariffPlan SET 
                    tariff = ?, end_date_tariff = ?, 
                    number_of_count = 0, max_number_of_count = ?, 
                    API_perm = ?, history_life = ?
                    WHERE user_login = ?''',
                                    (tariff_name, end_date,
                                     tariff_settings["max_requests"], tariff_settings["api_perm"],
                                     tariff_settings["history_life_days"], user_login))

                self.schedule_tariff_expiration(user_login, end_date)
            else:
                self.cursor.execute('''UPDATE TariffPlan SET 
                    tariff = ?, end_date_tariff = NULL, 
                    number_of_count = 0, max_number_of_count = ?, 
                    API_perm = ?, history_life = ?
                    WHERE user_login = ?''',
                                    (tariff_name,
                                     tariff_settings["max_requests"], tariff_settings["api_perm"],
                                     tariff_settings["history_life_days"], user_login))

            self.conn.commit()

            return True, f"Тариф {tariff_name} успешно активирован"

        except Exception as e:
            return False, f"Ошибка: {str(e)}"

    def schedule_tariff_expiration(self, user_login, end_date):
        self.scheduler.add_job(
            self.downgrade_to_free,
            'date',
            run_date=end_date,
            args=[user_login],
            id=f"tariff_expire_{user_login}_{end_date.timestamp()}"
        )

    def check_and_increment_request(self, user_login):
        try:
            self.cursor.execute('''SELECT number_of_count, max_number_of_count, tariff 
                                FROM TariffPlan WHERE user_login = ?''', (user_login,))
            result = self.cursor.fetchone()

            if not result:
                return False, "Пользователь не найден"

            current_count, max_count, tariff = result

            if max_count != -1 and current_count >= max_count:
                return False, f"Лимит запросов исчерпан для тарифа {tariff}"

            if max_count != -1:
                self.cursor.execute('''UPDATE TariffPlan SET number_of_count = number_of_count + 1 
                                    WHERE user_login = ?''', (user_login,))
                self.conn.commit()

                return True, f"Запрос учтен. Использовано {current_count + 1}/{max_count}"
            else:
                return True, "Запрос выполнен (безлимитный тариф)"

        except Exception as e:
            return False, f"Ошибка: {str(e)}"

    def reset_monthly_requests(self):
        try:
            self.cursor.execute('''UPDATE TariffPlan SET number_of_count = 0''')
            self.conn.commit()
            print(f"{datetime.now()}: Ежемесячные запросы сброшены для всех пользователей")
        except Exception as e:
            print(f"Ошибка при сбросе запросов: {e}")

    def downgrade_to_free(self, user_login):
        try:
            free_settings = self.get_tariff_settings("Бесплатный")

            self.cursor.execute('''UPDATE TariffPlan SET 
                tariff = "Бесплатный", 
                end_date_tariff = NULL,
                number_of_count = 0,
                max_number_of_count = ?,
                API_perm = ?,
                history_life = ?
                WHERE user_login = ?''',
                                (free_settings["max_requests"],
                                 free_settings["api_perm"],
                                 free_settings["history_life_days"], user_login))

            self.conn.commit()
            print(f"{datetime.now()}: Пользователь {user_login} переведен на бесплатный тариф")

        except Exception as e:
            print(f"Ошибка при переводе на бесплатный тариф: {e}")

    def check_expired_tariffs(self):
        try:
            now = datetime.now()
            self.cursor.execute('''SELECT user_login FROM TariffPlan 
                                WHERE end_date_tariff < ? AND tariff != "Бесплатный"''', (now,))
            expired_users = self.cursor.fetchall()

            for user in expired_users:
                self.downgrade_to_free(user[0])
                print(f"{datetime.now()}: Тариф пользователя {user[0]} автоматически переведен на бесплатный")

        except Exception as e:
            print(f"Ошибка при проверке просроченных тарифов: {e}")

    def start_scheduler(self):
        self.scheduler.add_job(
            self.check_expired_tariffs,
            CronTrigger(hour=0, minute=0),
            id='daily_expired_check'
        )

        self.scheduler.add_job(
            self.reset_monthly_requests,
            CronTrigger(day=1, hour=0, minute=0),
            id='monthly_reset'
        )

        self.scheduler.start()
        print("Планировщик APScheduler запущен")

    def get_user_info(self, user_login):
        try:
            self.cursor.execute('''SELECT * FROM TariffPlan WHERE user_login = ?''', (user_login,))
            return self.cursor.fetchone()
        except Exception as e:
            print(f"Ошибка при получении информации о пользователе: {e}")
            return None

    def get_tariff_features(self, user_login):
        try:
            self.cursor.execute('''SELECT tariff FROM TariffPlan WHERE user_login = ?''', (user_login,))
            result = self.cursor.fetchone()

            if result:
                tariff_name = result[0]
                tariff_settings = self.get_tariff_settings(tariff_name)
                return tariff_settings["features"]
            return None

        except Exception as e:
            print(f"Ошибка при получении функций тарифа: {e}")
            return None

    def get_scheduled_jobs(self):
        return self.scheduler.get_jobs()

    def shutdown(self):
        self.scheduler.shutdown()
        self.conn.close()
        print("Планировщик остановлен, соединение с БД закрыто")