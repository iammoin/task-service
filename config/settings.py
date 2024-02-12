import os

class Environment:
    """Class to get environment variables"""

    @classmethod
    def get_string(cls, config_name, default=""):
        return str(os.getenv(config_name, default))
    
class DB:
    host = Environment.get_string("DATABASE_HOST", "db")
    port = Environment.get_string("DATABASE_PORT", '5432')
    name = Environment.get_string("POSTGRES_DB")#, "postgres")
    user = Environment.get_string("POSTGRES_USER")#, "postgres")
    pass_ = Environment.get_string("POSTGRES_PASSWORD")#, "postgres")

class JWTToken:
    algorithm = Environment.get_string("JWT_ALGORITHM", "HS256")
    secret = Environment.get_string("JWT_SECRET", "secret")
    access_token_expire_minutes = Environment.get_string("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", "86400")