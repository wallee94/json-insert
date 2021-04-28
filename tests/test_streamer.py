import asyncio
import json
import os
from unittest import TestCase

from json_insert import JSONStream

with open(os.path.join(os.path.dirname(__file__), 'files', 'simple.json'), 'r') as f:
    example = f.read()


def chunks_gen(s):
    """
    yields chunks 20 chars long from s
    """
    yield from (s[i:i + 20] for i in range(0, len(s), 20))


class JSONStreamTest(TestCase):
    def test_whole_json(self):
        streamer = JSONStream()
        s = '{"key": "value"}'
        self.assertEqual(streamer.process_chunk(s), s)

    def test_json_in_chunks(self):
        streamer = JSONStream()
        s = ''.join(streamer.process_chunk(chunk) for chunk in chunks_gen(example))
        self.assertEqual(s, example)

    def test_merge_json_with_unicode_and_escapes(self):
        json_with_unicode = {
            "Image": {
                "Width": 800,
                "Height": 600,
                "Title": 'What about the "laughing" 😂 emoji',
                "Thumbnail": {
                    "Url": "http://www.example.com/image/481989943",
                    "Height": 125,
                    "Width": 100
                },
                "Animated": False,
                "IDs": [116, 943, 234, 38793]
            }
        }

        streamer = JSONStream({
            'Image': {
                "is_working": True,
                'Thumbnail': {
                    'trust': False
                }
            }
        })
        dump = json.dumps(json_with_unicode)
        s = ''.join(streamer.process_chunk(chunk) for chunk in chunks_gen(dump))
        got = json.loads(s)

        want = json_with_unicode
        want['Image']['is_working'] = True
        want['Image']['Thumbnail']['trust'] = False
        self.assertDictEqual(got, want)

    def test_merge_json_chunks(self):
        streamer = JSONStream({
            'glossary': {
                'GlossDiv': {
                    'added': True,
                    'created_at': '2021-02-15'
                }
            }
        })

        s = ''.join(streamer.process_chunk(chunk) for chunk in chunks_gen(example))
        got = json.loads(s)

        want = json.loads(example)
        want['glossary']['GlossDiv']['added'] = True
        want['glossary']['GlossDiv']['created_at'] = '2021-02-15'
        self.assertDictEqual(got, want)

    def test_iterator_without_merge(self):
        gen = chunks_gen(example)
        streamer = JSONStream()
        self.assertEqual(''.join(streamer.stream(gen)), example)

    def test_async_generator_without_merge(self):
        async def async_gen(s):
            for chunk in chunks_gen(s):
                yield chunk

        async def _test_async_generator_without_merge():
            streamer = JSONStream()
            got = ''.join([s async for s in streamer.astream(async_gen(example))])
            self.assertEqual(got, example)

        loop = asyncio.get_event_loop()
        loop.run_until_complete(_test_async_generator_without_merge())
        loop.close()

    def test_stream_single_str(self):
        merge = {'a': {'b': {'c': 2}}}
        streamer = JSONStream(merge)
        got = ''.join(streamer.stream('{"a": {"b": {"d": 3}, "e": 4}}'))
        self.assertEqual(got, '{"a": {"b": {"d": 3, "c": 2}, "e": 4}}')

    def test_append_to_empty(self):
        merge = {'a': 1, 'b': 2}
        streamer = JSONStream(merge)
        got = ''.join(streamer.stream('{}'))
        self.assertEqual(got, '{"a": 1, "b": 2}')

    def test_append_to_flat_json(self):
        merge = {'a': 1, 'b': 2}
        streamer = JSONStream(merge)
        got = ''.join(streamer.stream('{"c": 3, "d": 4}'))
        self.assertEqual(got, '{"c": 3, "d": 4, "a": 1, "b": 2}')
