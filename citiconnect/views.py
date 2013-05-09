from flask import request, make_response, Response, session, redirect, url_for, render_template
from flask_oauth import OAuth
from citiconnect import app

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
    
    return redirect(next_url)


@app.route('/')
def index():
    try:
        token = session['user_oauth_token']
    except KeyError:
        token = None
        
    if token == None:
        return redirect(url_for('login'))
    
    profile_req_url = 'http://api.linkedin.com/v1/people/~?format=json'
    resp = linkedin.get(profile_req_url)
    
    if resp.status == 200:
        profile = resp.data
        return render_template('home.html',Profile=profile)


'''
@app.route('/')
def index():
    return "Hello, World!"
'''
