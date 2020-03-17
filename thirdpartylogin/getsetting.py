
import jwt
import time
from . import setting as my_local_settings
from python_settings import settings
from datetime import datetime, timedelta

settings.configure(my_local_settings) 
headers = {
   'kid': settings.key_id
}

payload = {
   'iss': settings.team_id,
   'iat': int(datetime.utcnow().timestamp()),
   'exp': int(datetime.now().timestamp()) + (60 * 60),
   'aud': 'https://appleid.apple.com',
   'sub': settings.bundle_id,
}

client_secret = jwt.encode(
   payload, 
   settings.private_key, 
   algorithm='ES256', 
   headers=headers
).decode("utf-8")

