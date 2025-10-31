
from collections.abc import Callable
from typing import Optional
import requests
from pydantic import BaseModel

# Base pydantic
class User(BaseModel):
    name: str
    age: int

class UpdateUser(BaseModel):
    name: Optional[str] = None
    age: Optional[int] = None

def get_func_name(func: Callable):
    return func.__name__

# Will get id and validate id from user
def get_id() -> int:
    while True:
        try:
            user_id = int(input('User ID: '))
        except ValueError:
            print('user_id must be int')
            continue

        if user_id == '':
            continue
        
        if 0 > user_id or user_id > 99:
            print('user_id must be between 0 and 99')
            continue
        break
    return user_id

# Will get name and validate name from user
def get_name(**kwargs):
    if 'empty' in kwargs.keys():
        empty = kwargs['empty']
    else:
        empty = False

    while True:
        name = input('Name: ')
        if name == '':
            if empty:
                name = None
                break
            continue

        if len(name) > 99:
            print('Name is too long')
            continue
        break
    return name

# Will get age and validate age from user
def get_age(**kwargs):
    if 'empty' in kwargs.keys():
        empty = kwargs['empty']
    else:
        empty = False

    while True:
        age = input('Age: ')
        try:
            age = int(age)
        except ValueError:
            if age == '':
                if empty:
                    age = None
                    break
                continue
            print('Age must be int')
            continue
        
        if 0 > age or age > 200:
            print('Age must be between 0 and 200')
            continue
        break
    return age


def create_user(base_url: str, port: int) -> int:
    # Get user input
    user_id = get_id()
    user = User(
        name=get_name(),
        age=get_age()
    )
    
    # API request
    response = requests.post(
        f'{base_url}:{port}/users/{user_id}',
        json=user.__dict__
    )
    
    # Print response
    body = response.__dict__ 
    if response.status_code != 201:
        print(body['detail'])
        return response.status_code

    print('User was created successfully')
    return response.status_code


def update_user(base_url: str, port: int) -> int:
    # Get user input
    user_id = get_id()
    user = UpdateUser(
        name=get_name(empty=True),
        age=get_age(empty=True)
    )

    # API request
    response = requests.put(
        f'{base_url}:{port}/users/{user_id}',
        json=user.__dict__
    )

    # Print response
    body = response.json()
    if response.status_code != 200:
        print(body['detail'])
        return response.status_code

    print('User was updated successfully')
    return response.status_code

            
def get_all_users(base_url: str, port: int) -> int:
    # API request
    response = requests.get(
        f'{base_url}:{port}/users/all/'
    )

    # Print response
    body = response.json()
    if response.status_code != 200:
        print(body)
        print('Could not get all users')
        return response.status_code

    for user_id, user in body.items():
        print(f'ID: {user_id}, Name: {user['name']}, Age: {user['age']}')

    return response.status_code


def get_user(base_url: str, port: int) -> int:
    # Get user input
    user_id = get_id()

    # API request
    response = requests.get(
        f'{base_url}:{port}/users/{user_id}'
    )
    
    # Print response
    body = response.json()
    if response.status_code != 200:
        print(body['detail'])
        return response.status_code
        
    print(f'Name: {body['name']}, Age: {body['age']}')
    return response.status_code

def delete_user(base_url: str, port: int) -> int:
    # Get user input
    user_id = get_id()

    # API request
    response = requests.delete(
        f'{base_url}:{port}/users/{user_id}'
    )

    # Print response
    body = response.json() 
    if response.status_code != 200:
        print(body['detail'])
        return response.status_code

    print('User successfully deleted')
    return response.status_code

def search_by_name(base_url: str, port: int) -> int:
    # Get user input
    name = get_name()

    # API request
    response = requests.get(
        f'{base_url}:{port}/users/search/?name={name}',
    )

    # Print response
    body = response.json()
    if response.status_code != 200:
        print(body)
        print(body['detail'])
        return response.status_code
       
    print(f'User: {name} found, age: {body['age']}')
    return response.status_code

def root(base_url: str, port: int) -> int:
    response = requests.get(
        f'{base_url}:{port}/'
    )
    print(response.json())

def main():

    api_functions: dict[str: Callable] = {
        'root': root,
        'update_user': update_user,
        'get_user': get_user,
        'create_user': create_user,
        'delete_user': delete_user,
        'search_by_name': search_by_name,
        'get_all_users': get_all_users,
    }

    url = 'http://backend'
    port = 8000

    running = True
    input()
    
    while running:
        func_names: list[str] = api_functions.keys()
        # Get API call
        valid: bool = False
        response: str = ''

        while not valid:
            response = input('API call: ')

            if response == 'exit':
                running = False
                break
            if response not in func_names:
                print('Invalid API call.')
            else:
                valid = True

        if not running:
            break 
        # Call front end
        func: Callable = api_functions[response]
        func(base_url=url, port=port)


if __name__ == '__main__':
    main()



