# Documents for api

## Account  
### Message
|   Item   | URL | Method | Information | Result | Other |
| :------- | -------------- | :----------: | :-----------: | ----| --------------------------- |
|  GetMessage | /#api_version#/get_message | GET | Login Required | JSON message list| N/A |
| MarkAsRead | /#api_version#/read_message/<mid> | GET | Login Required | JSON message list| mid=0 to mark all as read |