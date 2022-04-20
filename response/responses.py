from models import HTTPException

UNAUTORIZED = {
    401: {
        "model": HTTPException,
        "description": "The user was not autorized to realize this operation."
    }
}

USER_ALREADY_REGISTERED = {
    400: {
        "model": HTTPException,
        "description": "User with this username is already registered."
    }
}

ENTITY_NOT_FOUND = {
    404: {
        "model": HTTPException,
        "description": "Entity with specified id was not found."
    }
}