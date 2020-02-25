from common.message import MessageType
from common.util import md5
from pprint import pprint
from server.memory import *
from server.util import database
from common.message import MessageType
from server.util import add_target_type


def run(sc, parameters):
    user_id = sc_to_user_id[sc]

    uid = parameters[0]
    accepted = parameters[1]
    c = database.get_cursor()
    sql="SELECT 1 from friends where from_user_id=%d and to_user_id=%d and accepted=0"%(uid, user_id)
    c.execute(sql)
    rows = c.fetchall()
    if len(rows) == 0:
        return

    if not accepted:
        c = database.get_cursor()
        spl="delete from friends where from_user_id=%d and to_user_id=%d and accepted=0"%(uid,user_id)
        c.execute(sql)
        return

    if accepted:
        c = database.get_cursor()
        sql="update friends set accepted=1 where from_user_id=%d and to_user_id=%d and accepted=0"%(uid, user_id)
        c.execute(sql)
        c = database.get_cursor()
        sql="insert into friends (from_user_id,to_user_id,accepted) values (%d,%d,1)"%(user_id, uid)
        c.execute(sql)

        sc.send(MessageType.contact_info, add_target_type(database.get_user(uid), 0))

        if uid in user_id_to_sc:
            user_id_to_sc[uid].send(MessageType.contact_info, add_target_type(database.get_user(user_id), 0))
