def get_auth_token():
    return 'here is your token'


def show_type(type_number):
    type_number = int(type_number)
    type_list = ['社团/协会','学生会','团队','班级','学院','赛事/活动']
    if type_number < 6:
        return type_list[type_number]
    else:
        return type_number