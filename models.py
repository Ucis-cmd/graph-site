from peewee import SqliteDatabase, Model, CharField, TextField, FloatField

db = SqliteDatabase("dinosaur.db")


# Dinozauru datubāzes kolonnas
class Dinosaur(Model):
    name = CharField()
    diet = CharField()
    period = CharField()
    period_name = CharField()
    lived_in = CharField()
    type = CharField()
    length = FloatField(null=True)
    taxonomy = TextField()
    clade1 = CharField()
    clade2 = CharField()
    clade3 = CharField()
    clade4 = CharField()
    clade5 = CharField()
    named_by = CharField()
    species = CharField()
    link = CharField()

    class Meta:
        database = db


def initialize_db():
    db.connection()
    db.create_tables([Dinosaur])
