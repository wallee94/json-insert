import json


class JSONStream:
    """
    Single JSON stream, implements methods to write a JSON string an read it back in
    chunks with its keys deep merged with the keys from a dict
    """

    def __init__(self, merge=None):
        if merge is None:
            merge = {}
        self.merge = dict(merge)
        self.last_string = ''
        self.last_char = ''

        self._scope = []
        self._bytes_count = 0
        self._on_string = False

    def kvs_in_scope(self):
        """
        Returns the non-dict key-values in self.merge for the current scope
        """
        root = self.merge
        try:
            for key in self._scope:
                root = root[key]
        except (KeyError, TypeError):
            return ''

        if isinstance(root, dict):
            root = {
                k: v for k, v in root.items()
                if not isinstance(v, dict)
            }
            if root:
                return json.dumps(root)[1:-1]

        return ''

    def process_chunk(self, chunk):
        s = ''
        for end, next_char in enumerate(chunk):
            if next_char == '{' and self.last_char != '\\':
                if self.last_string:
                    self._scope.append(self.last_string)

                self.last_char = next_char
                s += next_char + self.process_chunk(chunk[end + 1:])
                break

            elif next_char == '}' and self.last_char != '\\':
                # An object is closed. Append keys for the scope (if any)
                last_key = ''
                more_kvs = self.kvs_in_scope()
                if self._scope:
                    last_key = self._scope.pop()
                if more_kvs and self.last_string != last_key:
                    more_kvs = ', ' + more_kvs

                s += more_kvs

            elif next_char == '"' and self.last_char != '\\':
                self._on_string = not self._on_string
                if self._on_string:
                    self.last_string = ''

            elif self._on_string:
                self.last_string += next_char

            self.last_char = next_char
            s += next_char

        return s

    def stream(self, it):
        """
        Takes a str or an iterable of str and yields the resulting json in chunks. The
        output chunk can have a different length then the input when keys are added.
        Expects the string to be a valid JSON.
        """
        for chunk in it:
            yield self.process_chunk(chunk)

    async def astream(self, async_gen):
        """
        Async version of `stream`. Takes an async generator
        """
        async for chunk in async_gen:
            yield self.process_chunk(chunk)
