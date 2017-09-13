# Documents for api v1.0
## Account
### Auth
#### Login
| API Name | Login |
| :---: | ----: |
| URL | /api_v1/login |
| Method | POST |
Request parameters
```
    "email": email,
    "password": password,
    "captcha": captcha #验证码验证字段
```
Response json
```
{
    "status": number, # 1 for success; 0 for fail
    "token": token,
    "expire_time": token_expire_tiem
}
```

### User_Message
|   Item   | URL | Method | Information | Result | Other |
| :------- | -------------- | :----------: | :-----------: | ----| --------------------------- |
|  GetMessage | /#api_version#/get_message | GET | Login Required | JSON message list| N/A |
| MarkAsRead | /#api_version#/read_message/<mid> | GET | Login Required | JSON message list| mid=0 to mark all as read |


## User_Manage
### Group
In this api, if authentication fail return -1,
#### Create Group

| API Name | Create Group |
| :---: | ----: |
| URL | /api_v1/create_group |
| Method | POST |
Request parameters
```
{
    "token": user_login_token,
    "name": group_name,
    "type": group_type,
    "tel": manager_telephone_number,
    "short": group_short_name
}
```
Response json
```
{
    "id": group_id,
    "status": status_flag

}
```

#
#### Delete Group
| API Name | Delete Group |
| :---: | ----: |
| URL | /api_v1/delete_group |
| Method | POST |
Request parameters
```
{
    "token": user_login_token,
    "id": group_id
}
```
Response json
```
{
    "stats": status_flag

}
```

#
#### View Group
| API Name | View Group |
| :---: | ----: |
| URL | /api_v1/view_group |
| Method | POST |
| Description | Get group information by group_id |
Request parameters
```
{
    "token": user_login_token,
    "id" : group_id
}
```
Response json
```
{
    "id" : group_id,
    "name": group_name,
    "type": group_type,
    "tel": manager_telephone_number,
    "short": group_short_name,
    "icon": group_icon,
    "member_counter": group_member_counter,
    "manager": group_owner,
    ""
}
```

#
#### Edit Group
| API Name | Edit Group |
| :---: | ----: |
| URL | /api_v1/edit_group |
| Method | POST |
| Description | Modify group information |
Request parameters
```
{
    "token": user_login_token,
    "id" : group_id,
    "edit_item": edit_data
}
```
Response json
```
{
    "id": group_id,
    "status": success_or_fail_code
}
```
#

### User Manage
| API Name | Register |
| :---: | ----: |
| URL | /api_v1/register |
| Method | POST |
Request parameters
```
{
    "token": user_login_token,
    "name": group_name,
    "type": group_type,
    "tel": manager_telephone_number,
    "short": group_short_name,
}
```
Response json
```
{
    "id": group_id
    "stats": status_flag

}
```
#


### Account Manage
#### Get Balance
| API Name | Register |
| :---: | ----: |
| URL | /api_v1/balance |
| Method | GET |
Request parameters
```
Headers:
{
    Authorication: "Bearer $(token)"
}
```
Response json
```
{
    "balance": balance
}
```