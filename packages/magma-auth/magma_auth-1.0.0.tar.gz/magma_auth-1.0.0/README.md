# magma-auth
Python package for MAGMA Authentication

## Install module
Check here: https://pypi.org/project/magma-auth/

```python
pip install magma-auth
```

## Import module
```python
from magma_auth import auth
```

### Login using username and password
This will save (encrypted) your username and password.

```python
auth.login(
    username="<USERNAME>",
    password="<PASSWORD"
)
```
Renew or re-login
```python
auth.renew()
```
### Save your token
```python
auth.save_token("<TOKEN>")
```

### Get your token
```python
auth.token
```

### Get token expired time
```python
auth.expired_at
```

### Validate and check your token
This will check and validate token from MAGMA server.
```python
from magma_auth import validate_token

validate_token(token)
```