import json


def non_object_kvs(root, keys) -> str:
    try:
        for key in keys:
            root = root[key]
    except KeyError:
        return ''

    if not isinstance(root, dict):
        return ''

    root = {k: v for k, v in root.items() if not isinstance(v, dict)}
    if not root:
        return ''
    return json.dumps(root)[1:-1]


class JSONStream(object):
    def __init__(self, merge=None):
        if merge is None:
            merge = {}
        self.merge = dict(merge)
        self.last_string = ''
        self.last_char = ''

        self._scope = []
        self._bytes_count = 0
        self._on_string = False

    def _set_last_char(self, c):
        if c not in json.decoder.WHITESPACE_STR:
            self.last_char = c

    def stream(self, chunk, _w=json.decoder.WHITESPACE.match):
        end = _w(chunk, 0).end()
        s = chunk[:end]
        self._set_last_char(s[:-1])
        for end, next_char in enumerate(chunk[end:], start=end):
            if next_char == '{' and self.last_char != '\\':
                if self.last_string:
                    self._scope.append(self.last_string)

                self._set_last_char(next_char)
                s += next_char + self.stream(chunk[end + 1:])
                break

            elif next_char == '}' and self.last_char != '\\':
                v = non_object_kvs(self.merge, self._scope)
                if self._scope:
                    self._scope.pop()
                if v and self.last_char != '{':
                    v = ',' + v
                s += v

            elif next_char == '"' and self.last_char != '\\':
                self._on_string = not self._on_string
                if self._on_string:
                    self.last_string = ''

            elif self._on_string:
                self.last_string += next_char

            self._set_last_char(next_char)
            s += next_char

        return s
