import os

basedir = os.path.abspath(os.path.dirname(__file__))

db = "mysql+pymysql://iconsult-dev:2:yQB}vE+W5!jk7k@privatedb.apu.edu.my/iconsult_dev"


class Config(object):
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or db

    SQLALCHEMY_TRACK_MODIFICATIONS = False
