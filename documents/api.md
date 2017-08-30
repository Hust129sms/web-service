# Documents for api

## Account  
### User_Message
|   Item   | URL | Method | Information | Result | Other |
| :------- | -------------- | :----------: | :-----------: | ----| --------------------------- |
|  GetMessage | /#api_version#/get_message | GET | Login Required | JSON message list| N/A |
| MarkAsRead | /#api_version#/read_message/<mid> | GET | Login Required | JSON message list| mid=0 to mark all as read |


## User_Manage
### Group
| API Name | Create Group |
| URL | /api_v1/create_group |
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

| API Name | Delete Group |
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

| API Name | View Group |
| URL | /api_v1/group/<id> |
| Method | GET |
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

### User Manage
| API Name | Register |
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