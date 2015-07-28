# -*- coding: utf-8 -*-
from peewee import SqliteDatabase, Model, CharField, DateTimeField, BigIntegerField

database = SqliteDatabase(None)


class BaseModel(Model):
    class Meta:
        database = database


class MobileStation(BaseModel):
    imsi = CharField()
    number = CharField()


class Measure(BaseModel):
    """
    Usage:

    import time
    import db_models
    db_models.database.init('sample.db')
    with db_models.database.transaction():
        db_models.Measure.create(imsi="123", time=time.time(), ta="3737467")

    for measure in db_models.Measure.select():
        print "measure.imsi: ", measure.imsi
        print "measure.time: ", measure.time

    """
    # mobile_station = ForeignKeyField(MobileStation)
    imsi = CharField()
    time = DateTimeField()
    ta = BigIntegerField()
