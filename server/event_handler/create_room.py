from pprint import pprint
from common.message import MessageType
from server.broadcast import broadcast
import server.memory
from common.util import md5
from server.util import database
from server.util import add_target_type


def run(sc, parameters):
    user_id = server.memory.sc_to_user_id[sc]
    c = database.get_cursor()
    sql="insert into rooms (room_name) values ('%s')"%parameters

    c.execute(sql)
    c.fetchall()
    sc.send(MessageType.contact_info, add_target_type(database.get_room(c.lastrowid), 1))
    database.addc_to_room(user_id, c.lastrowid)
    sc.send(MessageType.general_msg, '创建成功，群号为：' + str(c.lastrowid))
