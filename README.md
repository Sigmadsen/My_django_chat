# My_django_chat
(Simple chat)
An application with 2 models:
● Thread (fields - participants, created, updated)
● Message (fields - sender, text, thread, created, is_read)
Thread can’t have more than 2 participants.

1. Implement REST endpoints for:
● creation (if a thread with particular users exists - just return it.);
● removing a thread;
● retrieving the list of threads for any user;
● creation of a message and retrieving message list for the thread;
● marking the message as read;
● retrieving a number of unread messages for the user.
2. Customize Django admin.
3. Provide pagination(LimitOffsetPagination) where it is needed.
4. Validation in URLs is required, comments are welcome.
5. Add a README.md file with a description of how to run the test task.
6. Create a dump of a database to load test data.
7. Give access to the project in the GIT repository. (Public Access)
Requirements:
- Djangо, DRF
- authentication Simple JWT or Django Token;
- database – SQLite