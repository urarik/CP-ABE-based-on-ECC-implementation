from ECC import Point, curve
import queue

attr_list = ['doctor', 'nurse', 'engineers', 'greece', 'america']


class Node:
    __slots__ = 'value', 'is_leaf', 'l_child', 'r_child', 'v'

    def __init__(self, value, is_leaf):
        self.value = value
        self.is_leaf = is_leaf
        self.l_child = None
        self.r_child = None
        self.v = []


def vector_mult(a, b):
    if len(a) != len(b):
        pass

    res = 0
    for i in range(0, len(a)):
        res += a[i] * b[i]
    return res


def msg_tp_point(msg):
    if len(msg) > 1e+76:
        pass  # partition?

    def int_to_bin(n):
        l_l = []
        while n != 0:
            d = n % 2
            l_l.append(d)
            n = n // 2
        while len(l_l) < 8:
            l_l.append(0)
        return l_l

    num = 256  # 8 bit of N(padding)
    res = 0
    for char in msg:
        binary_list = int_to_bin(ord(char))
        for b in binary_list:
            if b == 1:
                res += num
            num *= 2

    while True:
        y = curve.isExistY(res)
        if y is not False:
            break
        res += 1
    return Point((res, y), curve)


def point_to_msg(point):
    x = point.x

    def get_8bit(num):
        res = 0
        t = 1
        for i in range(8):
            if num % 2 == 1:
                res += t
            t *= 2
            num //= 2
        return num, res

    (x, dummy) = get_8bit(x)

    str_list = []
    while x != 0:
        (x, num) = get_8bit(x)
        str_list.append(chr(num))
    return ''.join(str_list)


def make_postfix(conditions):
    buffer = []
    stack = [0]
    for condition in conditions:
        if condition == 'and' or condition == 'or' or condition == '(':
            while stack[-1] == 'and' and stack[-1] != '(' and condition != '(':
                buffer.append(stack.pop())
            stack.append(condition)
        elif condition == ')':
            while stack[-1] != '(':
                buffer.append(stack.pop())
            stack.pop()
        else:
            buffer.append(condition)

    while len(stack) != 1:
        buffer.append(stack.pop())

    return buffer


def make_tree(postfix):
    stack = []
    for term in postfix:
        if term == 'and' or term == 'or':
            r_child = stack.pop()
            l_child = stack.pop()
            node = Node(term, False)
            node.l_child = l_child
            node.r_child = r_child
            stack.append(node)
        else:
            node = Node(term, True)
            stack.append(node)
    return stack[0]


def levelorder(root):
    node_queue = queue.Queue()
    node_queue.put(root)
    root.v = [1]
    c = 1
    A = []
    p = []
    while True:
        length = node_queue.qsize()
        if length == 0:
            break
        for i in range(0, length):
            node = node_queue.get()
            if node.l_child is not None:
                node_queue.put(node.l_child)
            if node.r_child is not None:
                node_queue.put(node.r_child)
            if node.value == 'and':
                while c != len(node.v):
                    node.v.append(0)
                v = []
                for j in range(0, c):
                    v.append(0)
                v.append(-1)
                node.l_child.v = v
                v = node.v.copy()
                v.append(1)
                node.r_child.v = v
                c += 1
            elif node.value == 'or':
                node.l_child.v = node.v.copy()
                node.r_child.v = node.v.copy()
            else:
                A.append(node.v)
                p.append(node.value)
    for a in A:
        if len(a) < c:
            for i in range(0, c - len(a)):
                a.append(0)
    return A, p


def inorder(node):
    if node is not None:
        inorder(node.l_child)
        print(node.value, end=' ')
        inorder(node.r_child)


def preorder(node):
    if node is not None:
        print(node.value, end=' ')
        preorder(node.l_child)
        preorder(node.r_child)


# def verify_authority(c1, c2, p, attr_index):
#     if attr_index[0] is True or attr_index[1] is False:
#         return _verify1(c1, c2, p, attr_index)
#     else:
#         return _verify2(c2, p, attr_index)


def verify1(c1, c2, p, attr_index):
    res = Point(None, None)
    state = False
    new_c1 = []
    new_c2 = []
    new_p = []
    for _p, _c1, _c2 in zip(p, c1, c2):
        if attr_index[attr_list.index(_p)]:
            if not state:
                state = True
            c2_point = Point(_c2, curve)
            res += c2_point
            new_c1.append(_c1)
            new_c2.append(_c2)
            new_p.append(_p)

    if state and res.x is None and res.y is None:
        return new_c1, new_c2, new_p
    else:
        return False


def verify2(c2, p, attr_index):
    res = Point(None, None)

    for _p, _c2 in zip(p, c2):
        if attr_index[attr_list.index(_p)] != -1:
            c2_point = Point(_c2, curve)
            res += c2_point

    if res.x is None and res.y is None:
        return True
    else:
        return False
