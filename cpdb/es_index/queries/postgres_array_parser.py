import string
from datetime import datetime


INITIAL = 0
ARRAY = 1
ROW = 2
STRING = 3
NUMBER = 4
QUOTED_STRING = 5
DECIMAL = 6
DATETIME = 7
JSON = 8


class NewRow(object):
    pass


class PostgresArrayLexer(object):
    def __init__(self, source):
        self._state = INITIAL
        self._source = source
        self._source_len = len(source)
        self._begin_ind = 0
        self._end_ind = 0

    def to_state(self, state):
        self._state = state

    def begin_with(self, val):
        if self._source[self._end_ind:].startswith(val):
            self.advance(len(val))
            return True
        return False

    def begin_with_number(self):
        advanced = False
        numbers = [str(num) for num in range(0, 10)]
        while self.have_more() and self._source[self._end_ind] in numbers:
            self.advance()
            advanced = True
        return advanced

    def begin_with_char(self):
        advanced = False
        chars = string.ascii_letters + '{}'
        while self.have_more() and self._source[self._end_ind] in chars:
            self.advance()
            advanced = True
        return advanced

    def begin_with_inner_char(self):
        advanced = False
        numbers = ''.join([str(num) for num in range(0, 10)])
        chars = string.ascii_letters + '/:-._\'?&=%;{}' + numbers
        while self.have_more() and self._source[self._end_ind] in chars:
            self.advance()
            advanced = True
        return advanced

    def advance(self, pos=1):
        self._end_ind += pos

    def have_more(self):
        return self._end_ind < self._source_len

    def discard_token(self):
        self._begin_ind = self._end_ind

    @property
    def token(self):
        return self._source[self._begin_ind: self._end_ind]

    def error(self):  # pragma: no cover
        return Exception(
            '%d: Encountered unanticipated chars %s (whole string was "%s")' % (
                self._state, self._source[self._begin_ind: self._end_ind + 1], self._source
            )
        )

    def swallow(self):
        while self.have_more():
            if self._state == INITIAL:
                if self.begin_with('{'):
                    self.discard_token()
                    self.to_state(ARRAY)
                else:  # pragma: no cover
                    raise self.error()
            elif self._state == ARRAY:
                if self.begin_with('"('):
                    self.discard_token()
                    yield NewRow
                    self.to_state(ROW)
                elif self.begin_with(','):
                    self.discard_token()
                elif self.begin_with('}'):
                    self.discard_token()
                    self.to_state(INITIAL)
                else:  # pragma: no cover
                    raise self.error()
            elif self._state == ROW:
                if self.begin_with_number():
                    self.to_state(NUMBER)
                elif self.begin_with(','):
                    yield None
                    self.discard_token()
                elif self.begin_with('t,'):
                    yield True
                    self.discard_token()
                elif self.begin_with('t)"'):
                    yield True
                    self.discard_token()
                    self.to_state(ARRAY)
                elif self.begin_with('f,'):
                    yield False
                    self.discard_token()
                elif self.begin_with('f)"'):
                    yield False
                    self.discard_token()
                    self.to_state(ARRAY)
                elif self.begin_with_char():
                    self.to_state(STRING)
                elif self.begin_with('\\"'):
                    self.discard_token()
                    self.to_state(QUOTED_STRING)
                elif self.begin_with(')"'):
                    yield None
                    self.discard_token()
                    self.to_state(ARRAY)
                else:  # pragma: no cover
                    raise self.error()
            elif self._state == NUMBER:
                if self.begin_with(','):
                    yield int(self.token[:-1])
                    self.discard_token()
                    self.to_state(ROW)
                elif self.begin_with(')"'):
                    yield int(self.token[:-2])
                    self.discard_token()
                    self.to_state(ARRAY)
                elif self.begin_with('.'):
                    self.to_state(DECIMAL)
                elif self.begin_with('-'):
                    self.to_state(DATETIME)
                else:  # pragma: no cover
                    raise self.error()
            elif self._state == STRING:
                if self.begin_with(','):
                    yield unicode(self.token[:-1], 'utf8')
                    self.discard_token()
                    self.to_state(ROW)
                elif self.begin_with(')"'):
                    yield unicode(self.token[:-2], 'utf8')
                    self.discard_token()
                    self.to_state(ARRAY)
                elif self.begin_with_inner_char():
                    pass
                else:  # pragma: no cover
                    raise self.error()
            elif self._state == QUOTED_STRING:
                if self.begin_with('\\"\\"'):
                    pass
                elif self.begin_with('\\",'):
                    yield unicode(self.token[:-3], 'utf8')
                    self.discard_token()
                    self.to_state(ROW)
                elif self.begin_with('\\")"'):
                    yield unicode(self.token[:-4], 'utf8')
                    self.discard_token()
                    self.to_state(ARRAY)
                else:
                    self.advance()
            elif self._state == DECIMAL:
                if self.begin_with_number():
                    pass
                elif self.begin_with(','):
                    yield float(self.token[:-1])
                    self.discard_token()
                    self.to_state(ROW)
                elif self.begin_with(')"'):
                    yield float(self.token[:-2])
                    self.discard_token()
                    self.to_state(ARRAY)
                else:  # pragma: no cover
                    raise self.error()
            elif self._state == DATETIME:
                if self.begin_with_number():
                    pass
                elif self.begin_with('-'):
                    pass
                elif self.begin_with(','):
                    yield datetime.strptime(self.token[:-1], '%Y-%m-%d')
                    self.discard_token()
                    self.to_state(ROW)
                elif self.begin_with(')"'):
                    yield datetime.strptime(self.token[:-2], '%Y-%m-%d')
                    self.discard_token()
                    self.to_state(ARRAY)
                else:  # pragma: no cover
                    raise self.error()


def parse_postgres_row_array(array):
    result = []
    row = []
    for val in PostgresArrayLexer(array).swallow():
        if val == NewRow:
            if len([val for val in row if val is not None]) > 0:
                result.append(tuple(row))
            row = []
        else:
            row.append(val)
    if len([val for val in row if val is not None]) > 0:
        result.append(tuple(row))
    return result
