import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'da9sdj28du20d9qdasd832jdadsadj2830djj8f8sd8fjjw8'
    DATABASE_PATH = 'database.db'
    YANDEX_API_KEY = "AQVN2E_gKuTJc_B1jb1gPQK4jAQiEbl5RZtSkmGU"
    YANDEX_FOLDER_ID = "b1g80nc4mkh3lm4s25h7"