from ECC import curve, Point
from hashlib import sha256
import socketio
from aiohttp import web
from abe_utils import verify2

# issuing and revoking users' attributes
# map GID to attribute list


class Key:
    __slots__ = 'master_key', 'public_key'
    pass


class Attribute:
    def __init__(self):
        self.list = ['doctor', 'nurse', 'engineers', 'greece', 'america']
        self.public_key = []
        self.k = []


key = Key()
attribute = Attribute()
users = {}
sids = {}

sio = socketio.AsyncServer(async_mode='aiohttp', cors_allowed_origins='*')
app = web.Application()
sio.attach(app)


def setup():
    key.master_key = curve.generatePrivateKey()
    key.public_key = curve.generatePublicKey(key.master_key)
    for i in range(0, len(attribute.list)):
        k = curve.generatePrivateKey()
        attribute.k.append(k)
        attribute.public_key.append(curve.generatePublicKey(k).compress())


@sio.event
def user_init(sid, data):
    name = data["name"]
    print(f"A user {name} wants to get attribute about ", end='')
    attributes = data["attributes"]
    for i, _attribute in enumerate(attributes):
        if _attribute:
            print(attribute.list[i], end=' ')
    # ans = input("accept?(y/n) ")
    ans = 'y'
    if ans == 'y':
        keys = []
        for i, _attribute in enumerate(attributes):
            if _attribute:
                k = attribute.k[i]
                h = int.from_bytes(sha256(name.encode('utf-8')).digest(), 'big')
                sk = k + h * key.master_key
                keys.append(sk)
            else:
                keys.append(-1)
        users[name] = keys
        print("success!")
        sids[name] = sid


@sio.event
async def send(sid, data):
    if data['to'] in sids:
        await sio.emit('message',
                       {'from': data['from'], 'c0': data['c0'], 'c1': data['c1'], 'c2': data['c2'], 'p': data['p']},
                       room=sids[data['to']])


@sio.event
async def decrypt(sid, data):
    name = data['name']
    c1 = data['c1']
    c2 = data['c2']
    p = data['p']
    sk = users[name]
    if verify2(c2, p, sk):
        res = Point((None, None), curve)
        for _p, _c2 in zip(p, c2):
            c2_point = Point(_c2, curve)
            sk_p = sk[attribute.list.index(_p)]
            res += sk_p * c2_point
        await sio.emit('decrypt', {'res': res.compress(), 'c1': data['c1'], 'c0': data['c0'], 'from': data['from']},
                       room=sid)
    else:
        await sio.emit('decrypt_fail', {'from': data['from']},
                       room=sid)


@sio.event
async def get_pk(sid):
    await sio.emit('encrypt', {'pk': attribute.public_key}, room=sid)


if __name__ == '__main__':
    setup()
    web.run_app(app)
