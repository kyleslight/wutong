import pickle
import hmac
import uuid
import hashlib
import memcache

class Session(dict):
    _registered = False

    class SessionNotRegisterError(Exception):
        pass
    class ConnectMemcachedServerError(Exception):
        pass

    @classmethod
    def register(cls, secret, memcached_address=["127.0.0.1:11211"], expires_days=7):
        cls.secret = secret
        cls.memcached_address = memcached_address
        cls.expires_days = expires_days
        cls._registered = True

    def __init__(self, request_handler):
        if not Session._registered:
            raise Session.SessionNotRegisterError()
        self.ssid, self.verf = self._get_ssid_and_verf(request_handler)
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
        mc = self._get_memclient()
        mc.delete(self.ssid)

    def _get_memclient(self):
        mc = memcache.Client(Session.memcached_address)
        if not mc.get_stats():
            raise Session.ConnectMemcachedServerError()
        return mc

    def _get_ssid_and_verf(self, request_handler):
        ssid = request_handler.get_secure_cookie("ssid")
        verf = request_handler.get_secure_cookie("verf")

        if verf != self._generate_verf(ssid):
            request_handler.clear_cookie("ssid")
            request_handler.clear_cookie("verf")
            ssid = verf = None
        if not (ssid and verf):
            ssid = self._generate_ssid()
            verf = self._generate_verf(ssid)
            request_handler.set_secure_cookie("ssid", ssid, Session.expires_days)
            request_handler.set_secure_cookie("verf", verf, Session.expires_days)
        return ssid, verf

    def _generate_ssid(self):
        return hashlib.sha256(Session.secret + str(uuid.uuid4())).hexdigest()

    def _generate_verf(self, ssid):
        if not ssid:
            return None
        return hmac.new(ssid, Session.secret, hashlib.sha256).hexdigest()
