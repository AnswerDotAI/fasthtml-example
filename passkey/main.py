from fasthtml.common import *
from webauthn import (generate_registration_options, options_to_json, verify_registration_response,
    generate_authentication_options, verify_authentication_response)
from webauthn.helpers.structs import (RegistrationCredential, AuthenticationCredential, AuthenticatorSelectionCriteria,
    ResidentKeyRequirement, UserVerificationRequirement)
from webauthn.helpers import base64url_to_bytes, bytes_to_base64url
from base64 import urlsafe_b64decode, urlsafe_b64encode
from json import dumps,loads

app,rt = fast_app()

# { 'uid': bytes, 'username': str, 'public_key': bytes, 'sign_count': int, 'credential_id': bytes }
challenges = {}
auths = {}
utf = 'utf-8'

def origin_kw(request):
    host = request.url.hostname
    scheme = 'http' if host in ("localhost", "127.0.0.1") else 'https'
    origin = f"{scheme}://{request.url.netloc}"
    return dict(expected_origin=origin, expected_rp_id=host)

@rt
def add_credential(response:str, data:dict, session, request):
    uid = session.pop('uid').encode(utf)
    challenge= challenges.pop(uid, None)
    kw = origin_kw(request)
    data['response'] = loads(response)
    res = verify_registration_response(credential=data, expected_challenge=challenge, require_user_verification=True, **kw)
    cred_id = res.credential_id
    auths[cred_id] = {'uid': uid, 'public_key': res.credential_public_key, 'sign_count': res.sign_count, 'credential_id': cred_id}
    return P('registered!')

regevt = '''
startRegistration({ optionsJSON: %s }).then(r => {
    htmx.ajax('POST', '/add_credential', { values: r, target:'#result' });
});
'''

def name2uid(name): return urlsafe_b64encode(name.encode(utf))
def uid2name(uid):  return urlsafe_b64decode(uid).decode(utf)

@rt
def register(username:str, session, request):
    uid = name2uid(username)
    host = request.url.hostname
    selec = AuthenticatorSelectionCriteria(resident_key=ResidentKeyRequirement.REQUIRED, require_resident_key=True)
    creation_opt = generate_registration_options(
        rp_id=host, rp_name="WebAuthn Demo", user_name=username, user_id=uid, authenticator_selection=selec)
    challenges[uid] = creation_opt.challenge
    session['uid'] = uid.decode(utf)
    return Script(regevt % options_to_json(creation_opt))

authevt = """
SimpleWebAuthnBrowser.startAuthentication({ optionsJSON: %s }).then(r => {
    htmx.ajax('POST', '/verify_auth', { values: r, target:'#result' });
});
"""

@rt
def request_auth(session, request):
    auth_opts = generate_authentication_options(rp_id=request.url.hostname, user_verification=UserVerificationRequirement.PREFERRED)
    session['auth_challenge'] = bytes_to_base64url(auth_opts.challenge)
    return Script(authevt % options_to_json(auth_opts))

@rt
def verify_auth(response:str, id:str, data:dict, session, request):
    challenge= base64url_to_bytes(session.pop('auth_challenge'))
    cred_id= base64url_to_bytes(id)
    stored_cred = auths.get(cred_id, None)
    if not stored_cred: return P('not registered!')
    kw = origin_kw(request)
    data['response'] = loads(response)
    verification = verify_authentication_response(
        credential_public_key=stored_cred['public_key'], credential_current_sign_count=stored_cred['sign_count'],
        credential=data, expected_challenge=challenge, require_user_verification=True, **kw)
    auths[cred_id]['sign_count'] = verification.new_sign_count
    session['uid'] = stored_cred['uid'].decode(utf)
    return P('logged in!')

@rt
def index():
    simplewebauthn = 'https://cdn.jsdelivr.net/npm/@simplewebauthn/browser@13.1.0/dist/bundle/index.umd.min.js'
    return Titled(
        'Passkey demo',
        Script(src=simplewebauthn),
        Script('const { startRegistration, startAuthentication } = SimpleWebAuthnBrowser;'),
        Form(
            Input(placeholder='user name', id='username'),
            Button('Register', id='regbtn'),
            hx_post=register, target_id='scripts'),
        Button('Authenticate', id='authbtn', hx_post=request_auth, target_id='scripts'),
        Div(id='scripts'), Div(id='result')
    )

serve()

