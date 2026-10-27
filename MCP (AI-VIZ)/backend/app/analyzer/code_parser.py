"""
Code parser utilities – source line extraction, token info, etc.
"""
import ast
import tokenize
import io
from typing import List, Optional


def get_source_line(code: str, line_number: int) -> Optional[str]:
    """Return the source code line at the given 1-based line number."""
    lines = code.splitlines()
    if 1 <= line_number <= len(lines):
        return lines[line_number - 1].rstrip()
    return None


def get_source_lines(code: str) -> List[str]:
    """Return all source lines (1-indexed in the returned list at index line-1)."""
    return code.splitlines()


def get_tokens(code: str) -> List[dict]:
    """Return token information for the source."""
    tokens = []
    try:
        for tok in tokenize.generate_tokens(io.StringIO(code).readline):
            if tok.type not in (tokenize.NEWLINE, tokenize.NL,
                                 tokenize.COMMENT, tokenize.ENDMARKER):
                tokens.append(
                    {
                        "type": tokenize.tok_name[tok.type],
                        "string": tok.string,
                        "start_line": tok.start[0],
                        "start_col": tok.start[1],
                    }
                )
    except tokenize.TokenError:
        pass
    return tokens


def has_syntax_error(code: str) -> Optional[dict]:
    """
    Return None if code is syntactically valid.
    Return error dict if there is a SyntaxError.
    """
    try:
        ast.parse(code)
        return None
    except SyntaxError as e:
        return {
            "type": "SyntaxError",
            "message": e.msg,
            "line": e.lineno,
            "offset": e.offset,
            "text": e.text,
        }
