from typing import Optional, List
from enum import Enum
import logging
import re

from .reserved_words import RESERVED_WORDS, RESERVED_WORDS_ORACLE_MODE


__all__ = [
    "escape_identifier",
    "IdentifierException",
    "IdentifierType",
    "SqlMode",
]


logger = logging.getLogger("mysql_quote_identifiers")


class IdentifierException(Exception):
    pass


class IdentifierType(Enum):
    """
    https://mariadb.com/docs/server/reference/sql-structure/sql-language-structure/identifier-names#maximum-length:
    - Databases, tables, columns, indexes, constraints, stored routines, triggers, events, views, tablespaces, servers and log file groups have a maximum length of 64 characters.
    - Compound statement labels have a maximum length of 16 characters.
    - Aliases have a maximum length of 256 characters, except for column aliases in CREATE VIEW statements, which are checked against the maximum column length of 64 characters (not the maximum alias length of 256 characters).
    - Users have a maximum length of 80 characters.
    - Roles have a maximum length of 128 characters.
    - Multi-byte characters do not count extra towards the character limit.
    """

    DATABASE = 1
    TABLE = 2
    COLUMN = 3
    INDEX = 4
    CONSTRAINT = 5
    ROUTINE = 6
    TRIGGER = 7
    EVENT = 8
    VIEW = 9
    TABLESPACE = 10
    SERVER = 11
    LOG_FILE_GROUPS = 12
    COMPOUND_STATEMENT = 13
    ALIAS = 14
    COLUMN_ALIAS = 15
    USER = 16
    ROLE = 17


# Dictionary mapping IdentifierType to maximum length
IDENTIFIER_LENGTHS = {
    IdentifierType.DATABASE: 64,
    IdentifierType.TABLE: 64,
    IdentifierType.COLUMN: 64,
    IdentifierType.INDEX: 64,
    IdentifierType.CONSTRAINT: 64,
    IdentifierType.ROUTINE: 64,
    IdentifierType.TRIGGER: 64,
    IdentifierType.EVENT: 64,
    IdentifierType.VIEW: 64,
    IdentifierType.TABLESPACE: 64,
    IdentifierType.SERVER: 64,
    IdentifierType.LOG_FILE_GROUPS: 64,
    IdentifierType.COMPOUND_STATEMENT: 16,
    IdentifierType.ALIAS: 256,
    IdentifierType.COLUMN_ALIAS: 64,
    IdentifierType.USER: 80,
    IdentifierType.ROLE: 128,
}


class SqlMode(Enum):
    ANSI_QUOTES = 0
    ORACLE = 1


"""
UNQUOTED
The following characters are valid, and allow identifiers to be unquoted:
- ASCII: [0-9,a-z,A-Z$_] (numerals 0-9, basic Latin letters, both lowercase and uppercase, dollar sign, underscore)
- Extended: U+0080 .. U+FFFF
"""
unquoted_allowed = re.compile(r'^[0-9a-zA-Z_\$\u0080-\uFFFF]+$')
"""
QUOTED
The following characters are valid, but identifiers using them must be quoted:
    ASCII: U+0001 .. U+007F (full Unicode Basic Multilingual Plane (BMP) except for U+0000)
    Extended: U+0080 .. U+FFFF
    CANT DO THIS HERE: Identifier quotes can themselves be used as part of an identifier, as long as they are quoted.
"""
quoted_allowed = re.compile(r'^[\u0001-\u007F\u0080-\uFFFF]+$')


# https://stackoverflow.com/questions/51867550/pymysql-escaping-identifiers
# https://mariadb.com/docs/server/reference/sql-structure/sql-language-structure/identifier-names
def escape_identifier(
    identifier: str,
    is_quoted: bool = True,
    sql_mode: Optional[List[SqlMode]] = None,
    only_validate: bool = False,
    identifier_type: IdentifierType = IdentifierType.DATABASE   # Database is the default as it has the most common length and the most common special rule
) -> str:
    """
    Validates and escapes SQL identifiers according to MariaDB/MySQL rules.
    
    This function handles both quoted and unquoted identifiers, though quoted identifiers
    are strongly recommended for security. The function will either automatically wrap
    identifiers in appropriate quotes or validate existing quotes.
    
    Args:
        identifier: The SQL identifier to escape/validate (e.g., table, column name)
        is_quoted: If True (default), handles as quoted identifier. If False, handles as
            unquoted identifier (NOT RECOMMENDED for security reasons)
        only_validate: If True, only validates without escaping
        identifier_type: Specifies the type of identifier (DATABASE, TABLE, etc.) for
            additional validation rules
        sql_mode: List of SQL modes that affect quoting behavior, particularly:
            - SqlMode.ANSI_QUOTES: Uses double quotes instead of backticks
            - SqlMode.ORACLE: Enables Oracle compatibility mode (affects reserved words)
    
    Returns:
        The properly escaped identifier (unless only_validate=True)
    
    Raises:
        IdentifierException: If the identifier contains illegal characters or violates
            validation rules for its type
    """
    sql_mode = [] if sql_mode is None else sql_mode

    # check if all characters in the identifier are allowed
    allowed_characters = quoted_allowed if is_quoted else unquoted_allowed
    if not allowed_characters.match(identifier):
        raise IdentifierException("identifier used illegal characters")

    # Quoting is optional for identifiers that are not reserved words.
    if not is_quoted:
        reserved = RESERVED_WORDS if SqlMode.ORACLE not in sql_mode else RESERVED_WORDS_ORACLE_MODE
        if identifier in reserved:
            raise IdentifierException("unquoted identifiers can not be reserved words")
        
    # quote characters
    # https://mariadb.com/docs/server/reference/sql-structure/sql-language-structure/identifier-names#quote-character
    quote_char = '"' if SqlMode.ANSI_QUOTES in sql_mode else '`'

    identifier_no_quote = identifier
    if is_quoted:
        if only_validate:
            if not identifier.startswith(quote_char) or not identifier.endswith(quote_char):
                raise IdentifierException("identifier needs to start and end with " + quote_char + "to be quoted")

            count = 0
            for char in identifier[1:-1]:
                if char == quote_char:
                    count += 1
                else:
                    if count % 2 != 0:
                        raise IdentifierException(f"the quote char {quote_char} needs to be escaped")

                    count = 0
        else:
            identifier = quote_char + identifier.replace(quote_char, quote_char + quote_char) + quote_char

        identifier_no_quote = identifier[1:-1]

    else:
        if quote_char in identifier:
            raise IdentifierException(f"unquoted identifiers cant contain the quote char {quote_char}")
        
    
    # validate the length
    # https://mariadb.com/docs/server/reference/sql-structure/sql-language-structure/identifier-names#maximum-length
    def get_real_length() -> int:
        if not is_quoted:
            return len(identifier)
        else:
            return len(identifier_no_quote.replace(quote_char + quote_char, quote_char))

    if get_real_length() > IDENTIFIER_LENGTHS[identifier_type]:
        raise IdentifierException(f"identifier of type {identifier_type} cant exceed the length of {IDENTIFIER_LENGTHS[identifier_type]}")

    # implementing further rules https://mariadb.com/docs/server/reference/sql-structure/sql-language-structure/identifier-names#further-rules
    # Database, table and column names can't end with space characters
    if identifier_type is IdentifierType.DATABASE or identifier_type is IdentifierType.TABLE or identifier_type is IdentifierType.COLUMN:
        if identifier_no_quote.endswith(" "):
            raise IdentifierException("database, table and column names can't end with space characters")

    # Identifier names may begin with a numeral, but can't only contain numerals unless quoted.
    if not is_quoted:
        if identifier.isnumeric():
            raise IdentifierException("identifier names may begin with a numeral, but can't only contain numerals unless quoted")

    # An identifier starting with a numeral, followed by an 'e', may be parsed as a floating point number, and needs to be quoted.
    if not is_quoted:
        for char in identifier:
            if char.isnumeric():
                continue

            if char == "e":
                raise IdentifierException("an identifier starting with a numeral, followed by an 'e', may be parsed as a floating point number, and needs to be quoted")
            else:
                break

    # Identifiers are not permitted to contain the ASCII NUL character (U+0000) and supplementary characters (U+10000 and higher).
    for char in identifier:
        numeric = ord(char)
        if numeric == 0 or numeric >= 0x10000:
            raise IdentifierException("identifiers are not permitted to contain the ASCII NUL character (U+0000) and supplementary characters (U+10000 and higher)")

    # Names such as 5e6, 9e are not prohibited, but it's strongly recommended not to use them, as they could lead to ambiguity in certain contexts, being treated as a number or expression.
    if identifier_no_quote.replace("e", "", 1).isnumeric():
        logger.warning("names such as 5e6, 9e are not prohibited, but it's strongly recommended not to use them, as they could lead to ambiguity in certain contexts, being treated as a number or expression")

    return identifier
