# ЛР 2 


### api-service localhost:8000

#### Пользователи
- `POST /users/register` - Регистрация нового пользователя
  ```json
  {
    "username": "string",
    "email": "user@example.com",
    "password": "string"
  }
  ```
- `POST /users/login` - Авторизация пользователя
  ```json
  {
    "email": "user@example.com",
    "password": "string"
  }
  ```
- `GET /users/me` - Получение информации о текущем пользователе
- `GET /users/{user_id}` - Получение информации о пользователе по ID

#### Посты
- `POST /posts/` -- Создание нового поста
  ```json
  {
    "content": "string"
  }
  ```

- `GET /posts/{post_id}` -- Получение поста по id
- `GET /posts/user/{user_id}` -- получение постов пользователя
- `DELETE /posts/{post_id}` - Удаление поста


### Chat service localhost:8001

- `POST /messages/` - Отправка сообщения
  ```json
  {
    "from_user_id": "string",
    "to_user_id": "string",
    "content": "string"
  }
  ```

- `GET /messages/{user_id}` - Получение всех сообщений пользователя
- `GET /messages/{from_user_id}/{to_user_id}` - Получение переписки между пользователями