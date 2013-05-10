#import numpy as np

def get_network_score(user):
    return user.connections_1/800. + user.connections_2/300000.

def get_resume_score(user):
    return user.educations + user.recommendations + user.months_worked/12.

def get_activity_score(user):
    return user.activities_last_month/3.

def make_score(user):
    user.network_score = get_network_score(user)
    user.resume_score = get_resume_score(user)
    user.activity_score = get_activity_score(user)
    user.save()
