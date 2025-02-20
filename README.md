# My Django Chat

## How to Run

1. **Build the Docker image:**
   ```sh
   docker compose build
   ```
2. **Start the containers:**
   ```sh
   docker compose up -d
   ```
3. **Create a superuser:**
   ```sh
   docker compose exec web python manage.py createsuperuser
   ```
4. **Obtain an access token**
   - Send a `POST` request to [http://localhost:8000/api/token/](http://localhost:8000/api/token/)
   - Use the credentials from the previous step
   - You can use Postman or a browser

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