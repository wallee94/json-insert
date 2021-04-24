import json
import os
from unittest import TestCase

from json_stream import JSONStream

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
        self.assertEqual(streamer.stream(s), s)

    def test_json_in_chunks(self):
        streamer = JSONStream()
        s = ''.join(streamer.stream(chunk) for chunk in chunks_gen(example))
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
        s = ''.join(streamer.stream(chunk) for chunk in chunks_gen(dump))
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

        s = ''.join(streamer.stream(chunk) for chunk in chunks_gen(example))
        got = json.loads(s)

        want = json.loads(example)
        want['glossary']['GlossDiv']['added'] = True
        want['glossary']['GlossDiv']['created_at'] = '2021-02-15'
        self.assertDictEqual(got, want)
