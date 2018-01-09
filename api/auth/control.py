import bcrypt
import random
import string
import datetime
import jwt
from random import randint
from flask import current_app as app
from validate_email import validate_email
from api.exceptions import InvalidEmail, AccountExists, NoAccount, InvalidCredentials, UserNotVerified
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

class AuthControl(object):
    def __init__(self, db):
        self.db = db

    def signup(self, email, password):
        if not self.is_valid_email(email):
            raise InvalidEmail('Invalid email address.')
        if self.db.users.find_one({"email": email}) is not None:
            raise AccountExists('Account already exists')
        account = {
            'email': email,
            'password': self.hash_password(password),
            'is_verified': False,
            'role': ['user'],
            'email_verification_token': self.random_string(48)
        }
        try:
            user_id = self.db.users.insert_one(account).inserted_id
        except Exception:
            raise
        else:
            account = self.db.users.find_one({'_id': user_id})
            msg = MIMEMultipart()
            msg['From'] = 'jeeves@ynos.in'
            msg['To'] = account['email']
            msg['Subject'] = 'YNOS - signup confirmation '
            body = "Hi,\n\nWelcome to YNOS Venture Engine. \nYour account with the email id: "+email+" has been created.\n\n " \
                "Please click on the link below to verify your account. \nhttp://0.0.0.0:8080/auth/verify-email/"+account[
                'email_verification_token']+"\n\nPlease ignore, if this was not you."
            # body = "Account created successfully! Please click http://0.0.0.0:8080/auth/verify-email/" + account[
            #     'email_verification_token'] + "' to verify your email ID./>"
            msg.attach(MIMEText(body, 'plain'))
            text = msg.as_string()
            self.send_email(account[u'email'], text)
        return {'message': 'Account created successfully'}

    def hash_password(self, password):
        salt = bcrypt.gensalt()
        hash = bcrypt.hashpw(password.encode('UTF-8'), salt)
        return hash

    def check_password(self, password, hash):
        print (hash)
        print (bcrypt.hashpw(password.encode('utf-8'), hash))
        return bcrypt.hashpw(password.encode('utf-8'), hash) == hash
        # return True


    def is_valid_email(self, email):
        return validate_email(email)

    def verify_email(self, token):
        user = self.db.users.find_one({'email_verification_token': token})
        if user is not None:
            try:
                self.db.users.update({'_id': user['_id']},
                                     {'$set': {'is_verified': True, 'email_verification_token': 'Done'}}, upsert=False)
                return 'Account successfully verified!'
            except Exception:
                raise

    def send_email(self, email, message):
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login("vishwanathavin@gmail.com", "vishwarajini")
        server.sendmail("jeeves@ynos.in", email, message)
        server.quit()
        return

    def random_string(self, length):
        pool = string.ascii_letters + string.digits
        return ''.join(random.choice(pool) for i in range(length))

    def check_otp(self):
        pass

    def authorize_request(self, req):
        pass

    def signin(self, email, password):
        if not self.is_valid_email(email):
            raise InvalidEmail('Invalid email address.')
        user = self.db.users.find_one({"email": email})
        if user is None:
            raise NoAccount("Account doesn't exist")
        if not user['is_verified']:
            raise UserNotVerified('Please verify your email ID')
        if self.check_password(password, user['password']):
            token = self.encode_auth_token(user['email'].__str__())
            return {'message': 'Login successful!', 'token': token.decode('utf-8')}
        else:
            raise InvalidCredentials('Please provide valid credentials')

    def forgot_password(self, email):
        if not self.is_valid_email(email):
            raise InvalidEmail('Invalid email address')
        user = self.db.users.find_one({"email": email})
        if user is None:
            raise NoAccount('Account does not exist with provided email address')
        token = self.random_string(48)
        self.db.users.update({'_id': user['_id']}, {'$set': {'password_reset_token': token}}, upsert=False)
        msg = MIMEMultipart()
        msg['From'] = 'jeeves@ynos.in'
        msg['To'] = user['email']
        msg['Subject'] = 'YNOS - Did you ask for a forgot password link '
        body = "Please click http://0.0.0.0:8080/auth/forgot-password/" + token + "' to reset your password."
        msg.attach(MIMEText(body, 'plain'))
        text = msg.as_string()
        self.send_email(user[u'email'], text)
        return "Password link sent to registered mailID"
    def reset_password(self, token, password):
        user = self.db.users.find_one({'password_reset_token': token})
        if user is None:
            raise NoAccount('No account exists with the provided email ID')
        if user['password_reset_token'] == token:
            self.db.users.update({'_id': user['_id']},
                                 {'$set': {'password': self.hash_password(password), 'password_reset_token': None}},
                                 upsert=False)
            return {'message': 'Password reset Successful!'}
        else:
            raise InvalidCredentials('Please provide valid credentials')

    def encode_auth_token(self, user_id):
        try:
            payload = {
                'exp': datetime.datetime.utcnow() + datetime.timedelta(days=0, seconds=60),
                'iat': datetime.datetime.utcnow(),
                'sub': user_id
            }
            return jwt.encode(
                payload,
                app.config.get('SECRET_KEY'),
                algorithm='HS256'  # HMAC + SHA256
            )
        except Exception as e:
            return e

    def decode_auth_token(self,auth_token):
        # decode the auth token and return user
        try:
            payload = jwt.decode(auth_token, app.config.get('SECRET_KEY'))
            result = {'status': 'valid', 'user': payload['sub']}
            return result
        except jwt.ExpiredSignatureError:
            result = {'status': 'expired', 'error': 'Your session is expired, please login again'}
            return result
        except jwt.InvalidTokenError:
            result = {'status': 'invalid', 'error': 'You need to login again'}
            return result

