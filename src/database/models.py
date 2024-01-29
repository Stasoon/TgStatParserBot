from peewee import (
    Model, PostgresqlDatabase, SqliteDatabase, AutoField,
    SmallIntegerField, BigIntegerField, IntegerField,
    DateTimeField, CharField, TextField, BooleanField,
    ForeignKeyField
)


db = SqliteDatabase(
    database='data.db'
    # DatabaseConfig.NAME,
    # user=DatabaseConfig.USER, password=DatabaseConfig.PASSWORD,
    # host=DatabaseConfig.HOST, port=DatabaseConfig.PORT
)


class _BaseModel(Model):
    class Meta:
        database = db


class User(_BaseModel):
    """ Пользователь бота """
    class Meta:
        db_table = 'users'

    telegram_id = BigIntegerField(primary_key=True, unique=True, null=False)
    name = CharField(default='Пользователь')
    username = CharField(null=True, default='Пользователь')
    referral_link = CharField(null=True)
    last_activity = DateTimeField(null=True)
    registration_timestamp = DateTimeField()


class RequestsCounter(_BaseModel):
    user = ForeignKeyField(model=User)
    request_count = IntegerField(default=0)
    last_request_time = DateTimeField(null=True)


class Admin(_BaseModel):
    """ Администратор бота """
    class Meta:
        db_table = 'admins'

    telegram_id = BigIntegerField(unique=True, null=False)
    name = CharField()


def register_models() -> None:
    for model in _BaseModel.__subclasses__():
        model.create_table()
