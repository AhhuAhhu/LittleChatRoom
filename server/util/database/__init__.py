import pymysql
from pprint import pprint
from server.memory import *

conn = pymysql.connect(host='localhost',user='root',passwd='123456',db='chatroom')
conn.autocommit(1)


def get_cursor():
    return conn.cursor()


def commit():
    return conn.commit()


def get_user(user_id):
    c = get_cursor()
    fields = ['id', 'username', 'nickname']
    sql="SELECT id,username,nickname FROM users WHERE id=%d"%user_id
    #row = c.execute('SELECT ' + ','.join(fields) + ' FROM users WHERE id=?', [user_id]).fetchall()
    c.execute(sql)
    row=c.fetchall()
    if len(row) == 0:
        return None
    else:
        user = dict(zip(fields, row[0]))
        user['online'] = user_id in user_id_to_sc
        return user


def get_pending_friend_request(user_id):
    c = get_cursor()
    users = []
    sql="SELECT from_user_id FROM friends WHERE to_user_id=%d AND NOT accepted"%user_id
    c.execute(sql)
    rows=c.fetchall()
    for row in rows:
        uid = row[0]
        # pprint([uid, type(uid)])
        users.append(get_user(uid))
    return users


def get_friends(user_id):
    c = get_cursor()
    users = []
    sql="SELECT to_user_id FROM friends WHERE from_user_id=%d AND accepted"%user_id
    c.execute(sql)
    rows=c.fetchall()
    for row in rows:
        uid = row[0]
        # pprint([uid, type(uid)])
        users.append(get_user(uid))
    return users


def get_user_rooms(user_id):
    c = get_cursor()
    rooms = []
    sql="SELECT room_id FROM room_user WHERE user_id=%d"%user_id
    c.execute(sql)
    rows=c.fetchall()
    for row in rows:
        room_id = row[0]
        rooms.append(get_room(room_id))
    return rooms


def get_user_rooms_id(user_id):
    c = get_cursor()
    rooms = []
    sql="SELECT room_id FROM room_user WHERE user_id=%d"%user_id
    c.execute(sql)
    rows=c.fetchall()
    for row in rows:
        room_id = row[0]
        rooms.append(room_id)
    return rooms


def is_friend_with(from_user_id, to_user_id):
    c = get_cursor()
    sql="SELECT 1 FROM friends WHERE from_user_id=%d AND to_user_id=%d AND accepted=1"%(from_user_id,to_user_id)
    c.execute(sql)
    r=c.fetchall()
    return len(r) > 0


def get_room(room_id):
    c = get_cursor()
    fields = ['id', 'room_name']
    sql="SELECT id,room_name FROM rooms WHERE id=%d"%room_id
    c.execute(sql)
    row=c.fetchall()
    if len(row) == 0:
        return None
    else:
        room = dict(zip(fields, row[0]))
        return room


def in_room(user_id, room_id):
    c = get_cursor()
    sql="SELECT 1 FROM room_user WHERE user_id=%d AND room_id=%d"%(user_id,room_id)
    c.execute(sql)
    row=c.fetchall()
    return len(row) > 0


def add_to_room(user_id, room_id):
    c = get_cursor()
    sql="INSERT INTO room_user (user_id,room_id) VALUES (%d,%d)"%(user_id,room_id)
    r = c.execute(sql)
    return r


def get_room_members_id(room_id):
    c=get_cursor()
    sql="SELECT user_id FROM room_user WHERE room_id=%d"%room_id
    c.execute(sql)
    return list(map(lambda x: x[0], c.fetchall()))


def get_room_members(room_id):
    c=get_cursor()
    sql="SELECT user_id,nickname,username FROM room_user LEFT JOIN users ON users.id=user_id WHERE room_id=%d"%room_id
    c.execute(sql)
    return list(map(lambda x: [x[0], x[1], x[0] in user_id_to_sc, x[2]], c.fetchall()))


def add_to_chat_history(user_id, target_id, target_type, data, sent):
    c = get_cursor()
    sql="INSERT INTO chat_history (user_id,target_id,target_type,data,sent) VALUES (%d,%d,%d,%s,%d)"%(user_id, target_id, target_type, str(data), sent)
    c.execute(sql)
    return c.lastrowid


# [[data:bytes,sent:int]]
def get_chat_history(user_id):
    c = get_cursor()
    sql="SELECT data,sent FROM chat_history WHERE user_id=%d"%user_id
    c.execute(sql)
    ret = list(map(lambda x: [bytearray(x[0]), x[1]],c.fetchall()))
    c = get_cursor()
    sql="UPDATE chat_history SET sent=1 WHERE user_id=%d"%user_id
    c.execute(sql)
    return ret
