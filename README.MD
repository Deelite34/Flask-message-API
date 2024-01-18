# Flask message api
Training project, that provides message API using flask-restful.

## Features:
- Uses flask, SQLAlchemy, Docker, PostgreSQL, Celery
- Uses marshmallow for serialization and deserialization of data, 
  alembic for database migrations, blueprints and application factory pattern
- JWT token stores additional info on identity of owner of the token
- Endspoints used to register account and log in
- Email activation with celery and external brevo API
- Uses JWT token to access api after logging in
- Hashing and salting of the stored password for security
- CRUD operations on messages
- Unit tests with pytest, mock of external api use

## Installation
1. Create .env file using example and set required values.
2. Build and install the project
```
Docker compose build
Docker compose up
```

## Tests
You can use custom shortcut command inside container to run the tests.
```
docker compose exec flask bash
flask test
```

## Endpoints
### /api/v1/account/
`POST`  
Register account, and send activation email to specified email  
```
{  
    "username": "sample_user",  
    "password": "some_password123",
    "email": "email@abc.com",
}
```
Response  
code 201
```
{
    "username": "sample_user", 
    "email": "email@abc.com" 
}
```

### /api/v1/account/login/
`POST`  
Send credentials, and receive JWT tokens if account is valid and active.  
Access token is required for CRUD operations on messages  
Request body  
```
{
    "username": "user1",
    "password": "password",
}
```

Response  
code 200  
```
{
    "access_token": "tokenhere",
    "refresh_token": "tokenhere"
}
```


### /account/login/refresh/  
`POST`  
Receive fresh pair of JWT tokens.  
Header with refresh JWT token is required.  

Response  
code 200  
```
{
    "access_token": "tokenhere"
}
```


### /api/v1/message/
Header with JWT Token received after logging in is required for all methods.  
`GET`  
List messages created by current user  

Response  
code 200  
```
[
    {
        "id": 1,
        "title": "My message",
        "content": "lorem ipsum sit doloret ames",
        "created": "2024-01-15T13:02:47.192956"
    }
]
```

### /api/v1/message/12  
Header with JWT Token received after logging in is required for all methods.  
`GET`  
List single message made by current user.  
JWT Token is required.  

Response  
code 200  
```
[
    {
        "id": 12,
        "title": "My message",
        "content": "lorem ipsum sit doloret ames",
        "created": "2024-01-15T13:02:47.192956"
    }
]
```

`POST`  
Create message.  
JWT Token is required.  
Request body  
```
{   
    "title": "My message",
    "content": "lorem ipsum sit doloret ames"
}
```

Response  
code 201  
```
{
    "id": 2,
    "title": "My message",
    "content": "lorem ipsum sit doloret ames",
    "created": "2024-01-16T16:07:34.474193"
}
```

`PUT`  
Create new, or update resource if it exists  
JWT Token is required.  

Request body  
```
{   
    "title": "My message",
    "content": "lorem ipsum sit doloret ames"
}
```

Response  
If resource did not exist before: code 201  
If resource was updated: code 200
```
{
    "id": 2,
    "title": "My message",
    "content": "lorem ipsum sit doloret ames",
    "created": "2024-01-16T16:07:34.474193"
}
```


`DELETE`  
Delete specific owned message.  
JWT Token is required.  

Response  
code 204  
