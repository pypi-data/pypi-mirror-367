from typing import List
from .models import Token, VOID_TOKEN, TokenType


class ParserBase:
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.num_of_tokens = len(self.tokens)
        self.current_pos = 0

    def _peek(self):
        if self.current_pos < self.num_of_tokens:
            return self.tokens[self.current_pos]
        return VOID_TOKEN

    def _look_ahead(self, num: int = 1):
        pos = self.current_pos + num
        if pos < self.num_of_tokens:
            return self.tokens[pos]
        return VOID_TOKEN

    def _consume(self, num: int = 1):
        buf = []
        for x in range(num):
            if self.current_pos < self.num_of_tokens:
                buf.append(self.tokens[self.current_pos])
                self.current_pos += 1
            else:
                break
        return buf

    def _consume_one(self):
        if self.current_pos < self.num_of_tokens:
            tok = self.tokens[self.current_pos]
            self.current_pos += 1
            return tok
        return VOID_TOKEN

    def _consume_enclosure(self):
        stack = 0
        buf = []
        while self.current_pos < self.num_of_tokens:
            tok = self._consume_one()
            buf.append(tok.value)
            if tok.token_type == TokenType.OPEN_PAREN:
                stack += 1
            elif tok.token_type == TokenType.CLOSE_PAREN:
                stack -= 1
                if stack == 0:
                    break
        return " ".join(buf)

    def _consume_enclosured_elements(self):
        stack = 0
        buf = []
        while self.current_pos < self.num_of_tokens:
            tok = self._consume_one()
            if tok.token_type == TokenType.OPEN_PAREN:
                stack += 1
            elif tok.token_type == TokenType.CLOSE_PAREN:
                stack -= 1
                if stack == 0:
                    break
            elif tok.token_type in [TokenType.IDENTIFIER, TokenType.QUOTED_IDENTIFIER]:
                buf.append(tok.value)
        return buf

    def _read_enclosure(self):
        stack = 0
        tok_buf = []
        while self.current_pos < self.num_of_tokens:
            current_token = self.tokens[self.current_pos]
            if current_token.token_type == TokenType.OPEN_PAREN:
                stack = stack + 1
                tok_buf.append(self._consume_one())
            elif current_token.token_type == TokenType.CLOSE_PAREN:
                stack = stack - 1
                tok_buf.append(self._consume_one())
                if stack == 0:
                    break
            else:
                tok_buf.append(self._consume_one())

        return tok_buf

    def _look_back(self, num: int = 1):
        pos = self.current_pos - num
        if pos > -1:
            return self.tokens[pos]
        return VOID_TOKEN

    def _is_keyword(self, tok: Token, keyword_name: str):
        return (
            tok.token_type == TokenType.KEYWORD and tok.uval() == keyword_name.upper()
        )

    def _is_comma(self, tok: Token):
        return tok.token_type == TokenType.PUNCTUATION and tok.value == ","

    def _is_possible_column(self, tok: Token):
        return tok.token_type in [
            TokenType.IDENTIFIER,
            TokenType.QUOTED_IDENTIFIER,
            TokenType.KEYWORD,
        ]

    def _is_expr_ending(self, tok: Token):
        return tok.token_type == TokenType.CLOSE_PAREN or self._is_keyword(tok, "END")

    def debug(self, header=None):
        header = header if header else "DEBUG"
        print(
            header,
            " ".join(t.value for t in self.tokens[self.current_pos :]),
        )

    def to_string(self):
        return " ".join(t.value for t in self.tokens)
