from enum import Enum


class Environment(Enum):
    PRODUCTION = "production"
    DEVELOPMENT = "development"


class UserTypes(Enum):
    CUSTOMER = "customer"
    ADMIN = "admin"
