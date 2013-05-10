from flask import request, make_response, Response, session, redirect, url_for, render_template
from flask_oauth import OAuth
from citiconnect import app
from models import User
import json

oauth = OAuth()

linkedin = oauth.remote_app(
        base_url ='http://api.linkedin.com/v1/',
        name='linkedin',
        consumer_key='2hjvezdzq589',
        consumer_secret='RG1YTVEbbbLRY8rQ',
        request_token_url='https://api.linkedin.com/uas/oauth/requestToken',
        access_token_url='https://api.linkedin.com/uas/oauth/accessToken',
        authorize_url='https://www.linkedin.com/uas/oauth/authenticate')

@app.before_first_request
def before_first_request():
    session['user_oauth_token'] = None
    session['user_oauth_secret'] = None


@linkedin.tokengetter
def get_token():
    """This is used by the API to look for the auth token and secret
    it should use for API calls. During the authorization handshake
    a temporary set of token and secret is used, but afterwards this
    function has to return the token and secret. If you don't want
    to store this in the database, consider putting it into the
    session instead.
    """
    try:
        oauth_token = session['user_oauth_token']
        oauth_secret = session['user_oauth_secret']
        if oauth_token and oauth_secret:
            return oauth_token, oauth_secret
    except KeyError:
        pass


@app.route('/login')
def login():
    """
    Calling into authorize will cause the OpenID auth machinery to kick
    in. When all worked out as expected, the remote application will
    redirect back to the callback URL provided.
    """
    return linkedin.authorize(callback=url_for('oauth_authorized', \
                                               next=request.args.get('next') or request.referrer or None))


@app.route('/oauth_authorized')
@linkedin.authorized_handler
def oauth_authorized(resp,oauth_token=None):
    """
    Called after authorization. After this function finished handling,
    the OAuth information is removed from the session again. When this
    happened, the tokengetter from above is used to retrieve the oauth
    token and secret.
    If the application redirected back after denying, the response passed
    to the function will be `None`. Otherwise a dictionary with the values
    the application submitted. Note that LinkedIn itself does not really
    redirect back unless the user clicks on the application name.
    """
    next_url = request.args.get('next') or url_for('index')
    if resp is None:
        flash(u'You denied the request to sign in.')
        return redirect(next_url)

    session['user_oauth_token'] = resp['oauth_token']
    session['user_oauth_secret'] = resp['oauth_token_secret']
    session['user_id'] = get_id()


    make_user()

    return redirect(next_url)


@app.route('/')
def index():
    try:
        token = session['user_oauth_token']
    except KeyError:
        token = None
        
    if token == None:
        #return redirect(url_for('login'))
        return render_template('home.html')

    user = User.objects(uid=session['user_id']).first()
        
    if user.in_group:
        if user.network_score is not None:
            return redirect('/go')
        else:
            return redirect('/score')
    else:
        return redirect('/join_group')
    # check if in group
    # no?
    #return redirect('/join_group')
    # yes?
    # check if they have a score
    # yes?
    # return redirect('/score')
    # no?    
    # return redirect('/go')

@app.route('/go')
def init_score_button_page():
    return render_template('go_page.html')


@app.route('/get_score')
def get_score():
    # if everything goes right
    return redirect('/score')


@app.route('/join_group')
def join():
    return render_template('join_group.html')


@app.route('/score')
def score_page():
    return render_template('score_page.html')


@app.route('/check')
def check():
    #req_url = 'http://api.linkedin.com/v1/people/~:(lastName,firstName,id,educations,num-recommenders,positions:(startDate,endDate),connections:(id))?format=json'
    #req_url = 'http://api.linkedin.com/v1/people/~:(lastName,firstName,id,educations,num-recommenders,positions:(startDate,endDate))?format=json'
    #req_url = 'http://api.linkedin.com/v1/groups/4409416?format=json'
    req_url = 'http://api.linkedin.com/v1/people/~/group-memberships/4409416?format=json'
    #req_url = 'http://api.linkedin.com/v1/people/~/picture-urls::(original)?format=json'
    #req_url = 'http://api.linkedin.com/v1/groups/4409416:(id,name,short-description,description,relation-to-viewer:(membership-state,available-actions),posts,counts-by-category,is-open-to-non-members,category,website-url,locale,location:(country,postal-code),allow-member-invites,site-group-url,small-logo-url,large-logo-url)?format=json'
    #req_url = 'http://api.linkedin.com/v1/groups/4409416:(id,name,relation-to-viewer:(membership-state))?format=json'
    #req_url = 'http://api.linkedin.com/v1/people/id=DHBm9Oo-M6:(positions)?format=json'
    #req_url = 'http://api.linkedin.com/v1/people/~:(num-recommenders)?format=json'
    #req_url = 'http://api.linkedin.com/v1/people/~:(network)?format=json'
    
    resp = linkedin.get(req_url)
    thing = resp.data
    #return json.dumps(thing)
    return str(thing['membershipState']['code'])


'''
@app.route('/')
def index():
    return "Hello, World!"
'''

def make_user():
    # first api call
    user_req_url = 'http://api.linkedin.com/v1/people/~:(lastName,firstName,id,connections:(id),educations,num-recommenders,positions:(startDate,endDate))?format=json'


    if User.objects(uid=session['user_id']).first():
        return

    resp = linkedin.get(user_req_url)
    linkedin_user = resp.data

    user = User()

    user.uid = linkedin_user['id']
    user.first_name = linkedin_user['firstName']
    user.last_name = linkedin_user['lastName']
    user.connections_1 = linkedin_user['connections']['_total']
    user.educations = linkedin_user['educations']['_total']
    user.recommendations = linkedin_user['numRecommenders']

    # second api call
    user_req_url = 'http://api.linkedin.com/v1/people/~/group-memberships/4409416?format=json'
    resp = linkedin.get(user_req_url)
    group_info = resp.data

    if group_info['membershipState']['code'] == 'member':
        user.in_group = True
    else:
        user.in_group = False

    user.save()

def get_id():
    user_req_url = 'http://api.linkedin.com/v1/people/~:(id)?format=json'

    resp = linkedin.get(user_req_url)
    linkedin_user = resp.data
    return linkedin_user['id']
