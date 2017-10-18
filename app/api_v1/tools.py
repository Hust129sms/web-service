import time
import base64
import hmac


def get_auth_token(key, expire=3600):
    '''
        @Args:
            key: str (用户给定的key，需要用户保存以便之后验证token,每次产生token时的key 都可以是同一个key)
            expire: int(最大有效时间，单位为s)
        @Return:
            state: str
    '''
    ts_str = str(time.time() + expire)
    ts_byte = ts_str.encode("utf-8")
    sha1_tshexstr  = hmac.new(key.encode("utf-8"),ts_byte,'sha1').hexdigest()
    token = ts_str+':'+sha1_tshexstr
    b64_token = base64.urlsafe_b64encode(token.encode("utf-8"))
    return b64_token.decode("utf-8")


def show_type(type_number):
    type_number = int(type_number)
    type_list = ['社团/协会', '学生会', '团队', '班级', '学院', '赛事/活动']
    if type_number < 6:
        return type_list[type_number]
    else:
        return type_number