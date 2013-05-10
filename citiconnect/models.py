from datetime import datetime
from flask.ext.mongoengine import MongoEngine
from citiconnect import db


def my_save(obj, *args, **kwargs):
    obj.date_modified = datetime.now()
    return super(db.Document, obj).save(*args, **kwargs)

class User(db.Document):
    uid = db.StringField(max_length=10,required=True,unique=True)
    first_name = db.StringField(max_length=100,required=True)
    last_name = db.StringField(max_length=100,required=True)
    in_group = db.BooleanField()
    connections_1 = db.IntField(required=True)
    connections_2 = db.IntField()
    educations = db.IntField(required=True)
    recommendations = db.IntField(required=True)
    activities_last_month = db.IntField()
    months_worked = db.IntField()
    #positions = db.ListField(db.EmbeddedDocumentField(Positions))
    network_score = db.FloatField()
    resume_score = db.FloatField()
    activity_score = db.FloatField()
    date_modified = db.DateTimeField()
    def save(self, *args, **kwargs):
        return my_save(self, *args, **kwargs)
    def __unicode__(self):
        return self.first_name


'''
class Positions(db.EmbeddedDocument):
    start_date = db.
    end_date = db.
''' 
