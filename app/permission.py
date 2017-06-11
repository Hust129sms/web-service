class UserPermission:
    CHARGE = 0x01
    CREATE_GROUP = 0x02
    VIEW_MEMBER = 0x04
    VIEW_RESPONSE = 0x08
    SEND_SMS = 0x10

    ADMINISTER = 0xffff


class AdminPermission:
    EDIT_CHARGE = 0x01
    BAN_USER = 0x02
