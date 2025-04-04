# My Django Chat

## How to Run

1. **Rename dump file `db_dump.sqlite3` to `db.sqlite3` to use test data:**

2. **Build the Docker image:**
   ```sh
   docker compose build
   ```
3. **Start the containers:**
   ```sh
   docker compose up -d
   ```


## Steps to Test
1. **Create admin token**![Create admin token](./docs/screenshots/step_1_create_admin_token.png)
   - Send a `POST` request to `localhost:8000/api/token/` with username:admin and password:admin and save the token
   - You can use Postman or a browser
2. **Set up token to send requests**![Set up token to send requests](./docs/screenshots/step_2_set_up_token_to_send_requests.png)
   - Set it as `Bearer` token
3. **Create a thread with user4**![Create a thread with user4](./docs/screenshots/step_3_create_a_thread_with_user_4_status_code_201.png)
   - Send a `POST` request to `localhost:8000/api/threads/` with body `{"username":"user4"}`
4. **Get a thread with user4**![Get a thread with user4](./docs/screenshots/step_4_get_a_thread_with_user_4_status_code_200.png)
   - Send a `POST` request to `localhost:8000/api/threads/` with body `{"username":"user4"}`
5. **Delete a thread with id 10**![Delete a thread with id 10](./docs/screenshots/step_5_delete_a_thread_with_id_10_status_code_204.png)
   - Send a `DELETE` request to `localhost:8000/api/threads/<put your thread_id here>/`
6. **Check list of threads for thread_id 10**![Check list of threads for thread_id 10](./docs/screenshots/step_6_check_list_of_threads_for_thread_id_10_does_not_exist.png)
   - Send a `GET` request to `localhost:8000/api/threads/` and look for you thread_id in the top of the list
7. **Create a thread with user4 again**![Create a thread with user4 again](./docs/screenshots/step_7_create_a_thread_with_user_4_again.png)
   - Send a `POST` request to `localhost:8000/api/threads/` with body `{"username":"user4"}`
8. **Check list of threads for thread id 11 exist**![Check list of threads for thread id 11 exist](./docs/screenshots/step_8_check_list_of_threads_for_thread_id_11_exist.png)
   - Send a `GET` request to `localhost:8000/api/threads/` and look for you thread_id in the top of the list
9. **Get messages from thread id 11**![Get messages from thread id 11](./docs/screenshots/step_9_get_messages_from_thread_id_11.png)
   - Send a `GET` request to `localhost:8000/api/threads/<put your thread_id here>/messages/`
10. **Try to mark message as not read**![Try to mark message id 30 as not read](./docs/screenshots/step_10_try_to_mark_message_id_30_as_not_read_status_code_400.png)
    - Send a `PATCH` request to `localhost:8000/api/threads/<put your thread_id here>/messages/<put your message_id here>/` with body `{"is_read":false}`
11. **Try to mark own message as read**![Try to mark own message as read stats code 400](./docs/screenshots/step_11_try_to_mark_own_message_as_read_status_code_400.png)
    - Send a `PATCH` request to `localhost:8000/api/threads/<put your thread_id here>/messages/<put your message_id here>/` with body `{"is_read":true}`
12. **Get auth token for user 4**![Get auth token for user 4](./docs/screenshots/step_12_get_auth_token_for_user_4.png)
    - Send a `POST` request to `localhost:8000/api/token/` with username:user4 and password:mypassword123 and save the token
    - Use this token in the next request
13. **Try to mark other user message as read**![Try to mark other user message as read status code 200](./docs/screenshots/step_13_try_to_mark_other_user_message_as_read_status_code_200.png)
    - Send a `PATCH` request to `localhost:8000/api/threads/<put your thread_id here>/messages/<put your message_id here>/` with body `{"is_read":true}`
14. **Check unread message count**![Check unread message count](./docs/screenshots/step_14_check_unread_message_count.png)
    - Send a `GET` request to `localhost:8000/api/threads/<put your thread_id here>/messages/unread_count/`
15. **Create and check new message in thread**![Create and check new message in thread](./docs/screenshots/step_15_create_and_check_new_message_in_thread.png)
    - Send a `POST` request to `localhost:8000/api/threads/<put your thread_id here>/messages/` with body `{"text":"123123"}`
    - Send a `GET` request to `localhost:8000/api/threads/<put your thread_id here>/messages/`
16. **Check again unread message count increased**![Check again unread message count increased](./docs/screenshots/step_16_check_again_unread_message_count_increased.png)
    - Send a `GET` request to `localhost:8000/api/threads/<put your thread_id here>/messages/unread_count/`
17. **Handle url 404 as json**![Handle url 404 as json](./docs/screenshots/step_17_handle_url_404_as_json.png)
    - Send any `POST` request to any invalid url 
18. **Check Django admin customization**![Check Django admin customization](./docs/screenshots/step_18_check_django_admin_customization.png)
19. **Check messages pagination page 1**![Check messages pagination page 1](./docs/screenshots/step_19_check_messages_pagination_page_1.png)
20. **Check messages pagination page 2**![Check messages pagination page 2](./docs/screenshots/step_20_check_messages_pagination_page_2.png)
21. **Check a restriction on API for marking a message as `read`**![Patch other fields](./docs/screenshots/step_21_try_to_patch_other_fields_via_api_for_marking_message_as_read.png)
    - Send a `PATCH` request to `localhost:8000/api/threads/<put your thread_id here>/messages/<put your message_id here>/` with body `{"text":"some random text"}`
22. **Check the restriction message**![Check the restriction message](./docs/screenshots/step_22_only_the_is_read_field_allowed_to_patch.png)

---

## Description

### Simple Chat Application
Two main models:

- **Thread**
  - Fields: `participants, created, updated`
  - A thread can't have more than 2 participants

- **Message**
  - Fields: `sender, text, thread, created, is_read`

### API Endpoints:
1. **Thread management:**
   - Create a thread (if a thread with particular users exists - just return it.)
   - Delete a thread
   - Retrieve a user's thread list

2. **Message management:**
   - Create a message
   - Retrieve message list for a thread
   - Mark a message as read
   - Retrieving a number of unread messages for the user.
---

## Tech Stack
- **Backend:** `Django, Django REST Framework`
- **Authentication:** `Simple JWT`
- **Database:** `SQLite`
- **Containerization:** `Docker`

---