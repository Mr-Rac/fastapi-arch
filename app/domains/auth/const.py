from enum import Enum


class TokenType(str, Enum):
    ACCESS = "access"
    REFRESH = "refresh"


class TokenHeader:
    ACCESS = "AUTHORIZATION"
    REFRESH = "AUTHORIZATION-REFRESH"
    NEW = "AUTHORIZATION-NEW"

    @classmethod
    def get(cls, token_type: TokenType, is_new: bool = False) -> str | None:
        if token_type == TokenType.ACCESS:
            return cls.ACCESS if not is_new else cls.NEW
        elif token_type == TokenType.REFRESH:
            return cls.REFRESH
        return None
