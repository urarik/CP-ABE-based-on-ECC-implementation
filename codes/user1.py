import socketio
from ECC import curve, Point
from abe_utils import *

serverSocket = socketio.Client()
serverSocket.connect('http://127.0.0.1:8080')
attr_list = ['doctor', 'nurse', 'engineers', 'greece', 'america']
name = ""
attr_index = []


def init():
    global name, attr_index
    attributes_str = input("attr = ")
    attributes = attributes_str.split(' ')
    attr_index = []
    for i in range(0, len(attr_list)):
        attr_index.append(False)
    for attribute in attributes:
        attr_index[attr_list.index(attribute)] = True

    name = input("name = ")
    serverSocket.emit('user_init', {'name': name, 'attributes': attr_index})


@serverSocket.event
def encrypt(data):  # 같은 속성이 조건에 여러번 나왔을 때?
    public_keys = data['pk']
    access_condition = input("Type condition(and, or): ")
    msg = input("msg: ")
    conditions = access_condition.split(' ')
    postfix = make_postfix(conditions)
    root = make_tree(postfix)
    A, p = levelorder(root)
    pk = []
    for attr in p:
        key = public_keys[attr_list.index(attr)]
        pk.append(Point(key, curve))

    M = msg_tp_point(msg)
    s = curve.generatePrivateKey()
    c0 = M + s * curve.G
    l = len(A[0])
    lamb = []
    ome = []
    v = [s]
    u = [0]
    for j in range(1, l):
        v.append(curve.generatePrivateKey())
        u.append(curve.generatePrivateKey())
    for a in A:
        lamb.append(vector_mult(v, a))
        ome.append(vector_mult(u, a))

    c1 = []
    c2 = []
    for lam, om, _p in zip(lamb, ome, pk):
        c1.append((lam * curve.G + om * _p).compress())
        c2.append((om * curve.G).compress())
    to = input('to= ')
    serverSocket.emit('send', {'from': name, 'to': to, 'c0': c0.compress(), 'c1': c1, 'c2': c2, 'p': p})
    start()
    return c0, c1, c2


@serverSocket.event
def message(data):
    cx = 1
    p = data['p']
    c2 = data['c2']
    c1 = data['c1']
    c0 = data['c0']
    res = verify1(c1, c2, p, attr_index)
    if res:
        serverSocket.emit('decrypt', {'name': name, 'c0': c0, 'c1': res[0], 'c2': res[1], 'p': res[2],
                                      'from': data['from']})
    else:
        decrypt_fail(data)


@serverSocket.event
def decrypt(data):
    sum_c1 = Point(None, None)
    c0 = data['c0']
    c1 = data['c1']
    res = data['res']
    res_point = Point(res, curve)
    for _c1 in c1:
        c1_point = Point(_c1, curve)
        sum_c1 += c1_point
    sg = sum_c1 - res_point
    c0_point = Point(c0, curve)
    m = c0_point - sg
    print("\nMsg from " + data['from'] + ' ' + point_to_msg(m) + '\n')


@serverSocket.event
def decrypt_fail(data):
    print(f"\n{data['from']} tried to send message to you but fail due to lack of attribute(s)...")


def start():
    print("\n1: send message, 2: Exit")
    cmd = int(input("Cmd? "))
    if cmd == 1:
        serverSocket.emit('get_pk')
    elif cmd == 2:
        return


if __name__ == '__main__':
    init()
    start()
