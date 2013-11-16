import pickle
import hmac
import uuid
import hashlib
import memcache

class Session(dict):
    _registered = False

    class SessionNotRegisterException(Exception):
        pass
    class InvalidSessionException(Exception):
        pass
    class ConnectMemcachedServerException(Exception):
        pass

    @classmethod
    def register(cls, secret, memcached_address=["127.0.0.1:11211"], expires_days=7):
        cls.secret = secret
        cls.memcached_address = memcached_address
        cls.expires_days = expires_days
        cls._registered = True

    def __init__(self, request_handler):
        if not Session._registered:
            raise SessionNotRegisterException()
        self.request_handler = request_handler
        self.ssid = request_handler.get_secure_cookie("ssid")
        self.verf = request_handler.get_secure_cookie("verf")
        self._check_ssid()
        data = self.load()
        for key, value in data.items():
            self[key] = value

    # read datas from memcached server
    def load(self):
        mc = self._get_memclient()
        data = mc.get(self.ssid)
        if data:
            data = pickle.loads(data)
        else:
            data = dict()
        return data

    # save datas to memcached server
    def save(self):
        # Don't need other attribute
        data = dict(self.items())
        data = pickle.dumps(data, pickle.HIGHEST_PROTOCOL)
        timeout = Session.expires_days * 24 * 60 * 60
        mc = self._get_memclient()
        mc.set(self.ssid, data, timeout)

    def clear(self):
        super(Session, self).clear()
        self.request_handler.clear_cookie("ssid")
        self.request_handler.clear_cookie("verf")
        mc = self._get_memclient()
        mc.delete(self.ssid)

    def _get_memclient(self):
        mc = memcache.Client(Session.memcached_address)
        if not mc.get_stats():
            raise ConnectMemcachedServerException()
        return mc

    def _check_ssid(self):
        if not (self.ssid and self.verf):
            self.ssid = self._generate_ssid()
            self.verf = self._generate_verf(self.ssid)
            self.request_handler.set_secure_cookie("ssid", self.ssid, self.expires_days)
            self.request_handler.set_secure_cookie("verf", self.verf, self.expires_days)
        elif self.verf != self._generate_verf(self.ssid):
            self.request_handler.clear_cookie("ssid")
            self.request_handler.clear_cookie("verf")
            raise InvalidSessionException()

    def _generate_ssid(self):
        return hashlib.sha256(Session.secret + str(uuid.uuid4())).hexdigest()

    def _generate_verf(self, ssid):
        return hmac.new(ssid, Session.secret, hashlib.sha256).hexdigest()
