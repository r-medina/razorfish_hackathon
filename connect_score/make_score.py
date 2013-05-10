from citiconnect.models import User
#import numpy as np

def get_network_score(user):
    return user.connections_1/1000.

def get_resume_score(user):
    return user.educations + user.recommendations

def get_activity_score(user):
    return 8.2

def make_score(user):
    user.network_score = get_network_score(user)
    user.resume_score = get_resume_score(user)
    user.activity_score = get_activity_score(user)
    user.save()

