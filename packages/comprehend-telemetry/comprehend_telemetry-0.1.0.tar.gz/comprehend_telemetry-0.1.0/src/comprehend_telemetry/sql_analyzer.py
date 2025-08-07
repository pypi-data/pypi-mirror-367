"""SQL analyzer module for extracting table operations and normalizing queries."""

import re
from enum import Enum
from typing import Dict, List, NamedTuple, Iterator
from dataclasses import dataclass


class TokenType(Enum):
    """SQL token types."""
    KEYWORD = 'keyword'
    IDENTIFIER = 'identifier'
    ID_QUOTE = 'id-quote'
    STRING = 'string'
    COMMENT = 'comment'
    PUNCT = 'punct'
    OPERATOR = 'operator'
    WHITESPACE = 'whitespace'
    UNKNOWN = 'unknown'


@dataclass
class Token:
    """Represents a SQL token with type and value."""
    type: TokenType
    value: str


class SQLAnalysisResult(NamedTuple):
    """Result of SQL analysis containing table operations and normalized queries."""
    table_operations: Dict[str, List[str]]
    normalized_query: str
    presentable_query: str


# SQL keywords for classification
KEYWORDS = {
    'SELECT', 'FROM', 'WHERE', 'INSERT', 'REPLACE', 'INTO', 'VALUES', 'DELETE', 'UPDATE',
    'MERGE', 'SET', 'JOIN', 'LEFT', 'RIGHT', 'FULL', 'OUTER', 'INNER', 'ON', 'AS', 'AND', 'OR',
    'NOT', 'IS', 'NULL', 'IN', 'WITH', 'RECURSIVE', 'UNION', 'ALL',
    'GROUP', 'BY', 'HAVING', 'ORDER', 'LIMIT', 'OFFSET', 'LATERAL', 'USING'
}


def tokenize_sql(sql: str) -> Iterator[Token]:
    """
    Tokenizes SQL string into tokens.

    Captures various SQL elements:
    - Comments (-- and /* */)
    - String literals (single quoted)
    - Quoted identifiers (double quotes, backticks, brackets)
    - Words (identifiers/keywords)
    - Punctuation
    - Operators
    - Whitespace
    - Unknown characters
    """
    # Regex pattern for tokenizing SQL
    pattern = r"(--[^\n]*|\/\*[\s\S]*?\*\/)|('[^']*')|(" + r'"(?:[^"]*)"' + r")|(`[^`]*`)|(\[[^\]]+\])|(\b[a-zA-Z_][\w$]*\b)|([(),;])|(<=|>=|<>|!=|=|<|>)|(\s+)|(\S)"

    for match in re.finditer(pattern, sql):
        groups = match.groups()

        # Comment (group 0)
        if groups[0]:
            yield Token(type=TokenType.COMMENT, value=groups[0])

        # Single quoted string literal (group 1)
        elif groups[1]:
            yield Token(type=TokenType.STRING, value=groups[1])

        # Double quoted identifier (group 2)
        elif groups[2]:
            yield Token(type=TokenType.ID_QUOTE, value='"')
            yield Token(type=TokenType.IDENTIFIER, value=groups[2][1:-1])  # Remove quotes
            yield Token(type=TokenType.ID_QUOTE, value='"')

        # Backtick quoted identifier (group 3)
        elif groups[3]:
            yield Token(type=TokenType.ID_QUOTE, value='`')
            yield Token(type=TokenType.IDENTIFIER, value=groups[3][1:-1])  # Remove backticks
            yield Token(type=TokenType.ID_QUOTE, value='`')

        # Bracket quoted identifier (group 4)
        elif groups[4]:
            yield Token(type=TokenType.ID_QUOTE, value='[')
            yield Token(type=TokenType.IDENTIFIER, value=groups[4][1:-1])  # Remove brackets
            yield Token(type=TokenType.ID_QUOTE, value=']')

        # Word - classify as keyword or identifier (group 5)
        elif groups[5]:
            word = groups[5]
            token_type = TokenType.KEYWORD if word.upper() in KEYWORDS else TokenType.IDENTIFIER
            yield Token(type=token_type, value=word)

        # Punctuation (group 6)
        elif groups[6]:
            yield Token(type=TokenType.PUNCT, value=groups[6])

        # Operator (group 7)
        elif groups[7]:
            yield Token(type=TokenType.OPERATOR, value=groups[7])

        # Whitespace (group 8)
        elif groups[8]:
            yield Token(type=TokenType.WHITESPACE, value=groups[8])

        # Unknown character (group 9)
        elif groups[9]:
            yield Token(type=TokenType.UNKNOWN, value=groups[9])


def has_balanced_parens(tokens: List[Token], start: int, end: int) -> bool:
    """Check if parentheses are balanced between start and end indices."""
    balance = 0
    for i in range(start, end):
        if i >= len(tokens):
            break
        token = tokens[i]
        if token.type == TokenType.PUNCT:
            if token.value == '(':
                balance += 1
            elif token.value == ')':
                balance -= 1

        # Early exit: unbalanced in wrong direction
        if balance < 0:
            return False
    return balance == 0


def analyze_sql_tokens(tokens: List[Token]) -> Dict[str, any]:
    """Analyze tokens to extract table operations and create normalized query."""
    alias_names = set()
    table_ops = {}
    normalized_tokens = []

    current_op = None  # {"ops": ["SELECT"], "at": 0}
    last_token_type = None

    def append_token(val: str, token_type: str):
        """Add token to normalized output with spacing."""
        nonlocal last_token_type
        if normalized_tokens and token_type != 'punct' and last_token_type != 'punct':
            normalized_tokens.append(' ')
        normalized_tokens.append(val)
        last_token_type = token_type

    i = 0
    while i < len(tokens):
        token = tokens[i]

        # Record operation context
        if token.type == TokenType.KEYWORD and token.value.upper() in ['SELECT', 'INSERT', 'UPDATE', 'DELETE']:
            current_op = {"ops": [token.value.upper()], "at": i}
        elif token.type == TokenType.KEYWORD and token.value.upper() == 'USING':
            current_op = {"ops": ["SELECT"], "at": i}
        elif token.type == TokenType.KEYWORD and token.value.upper() == 'REPLACE':
            current_op = {"ops": ["INSERT", "UPDATE"], "at": i}
        elif token.type == TokenType.KEYWORD and token.value.upper() == 'MERGE':
            # Look ahead for INSERT/UPDATE/DELETE operations
            saw_insert = saw_update = saw_delete = False
            for j in range(i + 1, len(tokens)):
                if tokens[j].type == TokenType.KEYWORD:
                    kw = tokens[j].value.upper()
                    if kw == "INSERT":
                        saw_insert = True
                    elif kw == "UPDATE":
                        saw_update = True
                    elif kw == "DELETE":
                        saw_delete = True

            current_op = {"ops": [], "at": i}
            if saw_insert:
                current_op["ops"].append("INSERT")
            if saw_update:
                current_op["ops"].append("UPDATE")
            if saw_delete:
                current_op["ops"].append("DELETE")

        # Detect CTE-style alias: <identifier> AS (
        if (token.type == TokenType.IDENTIFIER and
            i + 2 < len(tokens) and
            tokens[i + 1].type == TokenType.KEYWORD and tokens[i + 1].value.upper() == 'AS' and
            tokens[i + 2].type == TokenType.PUNCT and tokens[i + 2].value == '('):

            alias = token.value.lower()
            alias_names.add(alias)
            append_token(token.value, 'identifier')
            append_token('AS', 'keyword')
            append_token('(', 'punct')
            i += 3
            continue

        # Detect AS <alias> (table aliases, subquery aliases, etc.)
        if (token.type == TokenType.KEYWORD and token.value.upper() == 'AS' and
            i + 1 < len(tokens) and tokens[i + 1].type == TokenType.IDENTIFIER):

            alias = tokens[i + 1].value.lower()
            alias_names.add(alias)
            append_token(token.value, 'keyword')
            append_token(tokens[i + 1].value, 'identifier')
            i += 2
            continue

        # Record table name if in FROM, JOIN, INTO, UPDATE
        if (token.type == TokenType.KEYWORD and
            token.value.upper() in ['FROM', 'JOIN', 'INTO', 'UPDATE', 'USING'] and
            i + 1 < len(tokens) and tokens[i + 1].type == TokenType.IDENTIFIER and
            not (token.value.upper() in ['FROM', 'JOIN', 'USING'] and
                 i + 2 < len(tokens) and tokens[i + 2].value == "(")):  # functions

            table = tokens[i + 1].value.lower()
            if (current_op and table not in alias_names and
                has_balanced_parens(tokens, current_op["at"], i)):
                if table not in table_ops:
                    table_ops[table] = set()
                for op in current_op["ops"]:
                    table_ops[table].add(op)

        # Normalize IN (...) clauses
        if (token.type == TokenType.KEYWORD and token.value.upper() == 'IN' and
            i + 1 < len(tokens) and tokens[i + 1].value == '(' and
            i + 2 < len(tokens)):  # make sure something exists inside

            append_token('IN', 'keyword')
            append_token('(', 'punct')

            first_inside = tokens[i + 2]
            if first_inside.type == TokenType.KEYWORD:
                # Subquery → parse normally
                i += 2
                continue
            else:
                # Literal list → collapse
                append_token('...', 'identifier')

                # Skip until matching ')'
                depth = 1
                j = i + 3
                while j < len(tokens) and depth > 0:
                    if tokens[j].value == '(':
                        depth += 1
                    elif tokens[j].value == ')':
                        depth -= 1
                    j += 1

                append_token(')', 'punct')
                i = j
                continue

        # Normalize VALUES (...) clauses
        if (token.type == TokenType.KEYWORD and token.value.upper() == 'VALUES' and
            i + 1 < len(tokens) and tokens[i + 1].value == '('):

            append_token('VALUES', 'keyword')
            append_token('(', 'punct')
            append_token('...', 'identifier')
            append_token(')', 'punct')

            # Skip all VALUES tuples including comma-separated ones
            depth = 0
            j = i + 1
            while j < len(tokens):
                if tokens[j].value == '(':
                    depth += 1
                elif tokens[j].value == ')':
                    depth -= 1
                    if depth == 0:
                        # Check if there's a comma after this closing paren (more tuples)
                        k = j + 1
                        while (k < len(tokens) and
                               tokens[k].type in [TokenType.WHITESPACE, TokenType.COMMENT]):
                            k += 1
                        if k < len(tokens) and tokens[k].value == ',':
                            # More tuples, continue skipping
                            j = k + 1
                            continue
                        else:
                            # No more tuples, we're done
                            break
                j += 1

            i = j + 1
            continue

        # Process token for normalization
        if token.type == TokenType.WHITESPACE or token.type == TokenType.COMMENT or token.type == TokenType.ID_QUOTE:
            # Skip whitespace, comments, and quote characters
            pass
        elif token.type == TokenType.KEYWORD:
            # Normalize to uppercase
            append_token(token.value.upper(), 'keyword')
        elif token.type == TokenType.IDENTIFIER:
            # Normalize to lowercase
            append_token(token.value.lower(), 'identifier')
        else:
            append_token(token.value, token.type.value)

        i += 1

    return {
        "table_operations": {k: list(v) for k, v in table_ops.items()},
        "normalized_query": ''.join(normalized_tokens)
    }


def analyze_sql(sql: str) -> SQLAnalysisResult:
    """
    Analyzes SQL to extract table operations and create normalized/presentable versions.

    Performs a rough tokenization of the SQL, extracts the tables involved and the operations on them, and
    produces two versions of the query:
    - A normalized version for hashing purposes that does not account for whitespace, comments, and collapses
      IN clauses and VALUES clauses that might cause a cardinality explosion.
    - A presentable version that only does the IN clause and VALUES clause collapsing

    Args:
        sql: The SQL query to analyze

    Returns:
        SQLAnalysisResult with table operations and normalized queries
    """
    semantic_tokens = []
    presentable_tokens = []

    # State for presentable query processing
    seeking_in_paren = False
    analyzing_in = False
    skipping_in = False
    seeking_values_paren = False
    skipping_values = False
    looking_for_comma_or_end = False
    values_depth = 0
    skipped_whitespace = []

    for token in tokenize_sql(sql):
        # Build semantic tokens (for normalization)
        if token.type == TokenType.WHITESPACE or token.type == TokenType.COMMENT or token.type == TokenType.ID_QUOTE:
            # Skip
            pass
        elif token.type == TokenType.KEYWORD:
            # Normalize to uppercase
            semantic_tokens.append(Token(TokenType.KEYWORD, token.value.upper()))
        elif token.type == TokenType.IDENTIFIER:
            # Normalize to lowercase
            semantic_tokens.append(Token(TokenType.IDENTIFIER, token.value.lower()))
        else:
            semantic_tokens.append(token)

        # Build presentable tokens (with VALUES/IN collapsing)
        if seeking_in_paren:
            # We saw IN, and now look for an opening (. Skip whitespace/comments, bail if anything else.
            presentable_tokens.append(token)
            if token.type in [TokenType.COMMENT, TokenType.WHITESPACE]:
                pass
            elif token.type == TokenType.PUNCT:
                seeking_in_paren = False
                analyzing_in = token.value == "("
            else:
                seeking_in_paren = False
        elif analyzing_in:
            # We saw the opening paren of an IN. Pass over whitespace and comments. If we see a
            # keyword we know it's not something to collapse, it's a sub-query. Otherwise, we
            # enter skipping mode.
            if token.type in [TokenType.COMMENT, TokenType.WHITESPACE]:
                presentable_tokens.append(token)
            elif token.type in [TokenType.KEYWORD, TokenType.PUNCT]:  # maybe immediate ), certainly not a value
                presentable_tokens.append(token)
                analyzing_in = False
            else:
                analyzing_in = False
                skipping_in = True
                presentable_tokens.append(Token(TokenType.UNKNOWN, "..."))
        elif skipping_in:
            # Omit tokens until a closing ).
            if token.type == TokenType.PUNCT and token.value == ")":
                presentable_tokens.append(token)
                skipping_in = False
        elif seeking_values_paren:
            # We saw VALUES, and now look for an opening (. Skip whitespace/comments, bail if anything else.
            if token.type in [TokenType.COMMENT, TokenType.WHITESPACE]:
                presentable_tokens.append(token)
            elif token.type == TokenType.PUNCT:
                if token.value == "(":
                    # Just add the opening paren, "..." and closing paren - preserve original spacing
                    presentable_tokens.append(token)
                    presentable_tokens.append(Token(TokenType.UNKNOWN, "..."))
                    presentable_tokens.append(Token(TokenType.PUNCT, ")"))
                    seeking_values_paren = False
                    skipping_values = True
                    values_depth = 1
                else:
                    # Not what we expected, go back to normal processing
                    presentable_tokens.append(token)
                    seeking_values_paren = False
            else:
                # Not what we expected, go back to normal processing
                presentable_tokens.append(token)
                seeking_values_paren = False
        elif skipping_values:
            # Skip everything until we've consumed all VALUES tuples
            if token.type == TokenType.PUNCT:
                if token.value == "(":
                    values_depth += 1
                elif token.value == ")":
                    values_depth -= 1
                    if values_depth == 0:
                        # This closes a tuple, check for comma indicating more tuples
                        looking_for_comma_or_end = True
                        skipping_values = False
        elif looking_for_comma_or_end:
            # After closing a VALUES tuple, look for comma (more tuples) or end of VALUES
            if token.type in [TokenType.COMMENT, TokenType.WHITESPACE]:
                # Collect whitespace/comments while looking for comma or end
                skipped_whitespace.append(token)
            elif token.type == TokenType.PUNCT:
                if token.value == ",":
                    # More tuples coming, clear skipped whitespace and continue skipping
                    skipped_whitespace = []
                    looking_for_comma_or_end = False
                    skipping_values = True
                else:
                    # Not a comma, so VALUES clause is done
                    # Add back the skipped whitespace, then the current token
                    presentable_tokens.extend(skipped_whitespace)
                    presentable_tokens.append(token)
                    skipped_whitespace = []
                    looking_for_comma_or_end = False
            else:
                # VALUES clause is done, resume normal processing
                # Add back the skipped whitespace, then the current token
                presentable_tokens.extend(skipped_whitespace)
                presentable_tokens.append(token)
                skipped_whitespace = []
                looking_for_comma_or_end = False
        else:
            presentable_tokens.append(token)
            seeking_in_paren = token.type == TokenType.KEYWORD and token.value.upper() == "IN"
            seeking_values_paren = token.type == TokenType.KEYWORD and token.value.upper() == "VALUES"

    # Analyze semantic tokens for table operations
    analysis_result = analyze_sql_tokens(semantic_tokens)

    return SQLAnalysisResult(
        table_operations=analysis_result["table_operations"],
        normalized_query=analysis_result["normalized_query"],
        presentable_query=''.join(t.value for t in presentable_tokens)
    )