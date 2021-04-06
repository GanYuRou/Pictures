import hashlib
import datetime


class PasswordUtil:

    @staticmethod
    def password_hash(user_code, password, create_datetime):
        create_timestamp = datetime.datetime.timestamp(create_datetime) * 1000
        password_hash_str = user_code + ':' + password + ':' + str(create_timestamp)
        return hashlib.md5(password_hash_str.encode('utf-8')).hexdigest()
