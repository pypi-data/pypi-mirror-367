# prettyfmt

`prettyfmt` is a tiny library to make your outputs, logs, and `__str__()`
representations slightly more beautiful.

It offers simple but general functions for formatting and abbreviating objects and
dataclasses, dicts, words and phrases, filenames, titles, long strings, timestamps,
ages, and sizes. It also has Unicode-friendly multilingual slugify functions.

It won't bloat your project.
It's <500 lines of code with minimal dependencies:
[`humanize`](https://github.com/python-humanize/humanize),
[`text-unidecode`](https://github.com/kmike/text-unidecode), and the very small
[`pluralizer-py`](https://github.com/weixu365/pluralizer-py) and
[`strif`](https://github.com/jlevy/strif).

Note the pluralization is for English and fast to import, unlike larger libraries like
[`inflect`](https://github.com/jaraco/inflect).
The two slugification functions are just simple near-equivalents of
[`python-slugify`](https://github.com/un33k/python-slugify).

## Installation

Add the [`prettyfmt`](https://pypi.org/project/prettyfmt/) package to your environment
in the usual way (`uv add prettyfmt`, `poetry add prettyfmt`, or `pip install
prettyfmt`).

## Usage

See
[docstrings](https://github.com/jlevy/prettyfmt/blob/main/src/prettyfmt/prettyfmt.py)
for details on all functions.

```python

from prettyfmt import *

# Simple abbreviations of objects:
abbrev_obj({"a": "very " * 100 + "long", "b": 23})
# -> "{a='very very very very very very very very very very very very ver…', b=23}"

abbrev_obj(["word " * i for i in range(10)], field_max_len=10, list_max_len=4)
# -> "['', 'word ', 'word word ', 'word word…', …]"

# Abbreviate by character length.
abbrev_str("very " * 100 + "long", 32)
# -> 'very very very very very very v…'

# Abbreviate by character length but don't break words.
abbrev_on_words("very " * 100 + "long", 30)
# -> 'very very very very very very…'

# My favorite, abbreviate but don't break words and keep a few words
# on the end since they might be useful.
abbrev_phrase_in_middle("very " * 100 + "long", 40)
# -> 'very very very very … very very very long'

# This makes it very handy for cleaning up document titles.
ugly_title = "A  Very\tVery Very Needlessly Long  {Strange} Document Title [final edited draft23]"
# -> sanitize_title(ugly_title)
'A Very Very Very Needlessly Long Strange Document Title final edited draft23'
abbrev_phrase_in_middle(sanitize_title(ugly_title))
# -> 'A Very Very Very Needlessly Long Strange … final edited draft23'

# You can convert strings to cleaner titles:
ugly_title = "A  Very\tVery Very Needlessly Long  {Strange} Document Title [final edited draft23]"
sanitized = sanitize_title(ugly_title)
# -> 'A Very Very Very Needlessly Long Strange Document Title final edited draft23'

# Underscore and dash slugify based on this:
slugify_snake("Crème Brûlée Recipe & Notes")
# -> 'crème_brûlée_recipe_notes'

slugify_snake("Crème Brûlée Recipe & Notes", ascii=True)
# -> 'creme_brulee_recipe_notes'

slugify_kebab("你好世界 Hello World")
# -> '你好世界-hello-world'

slugify_kebab("你好世界 Hello World", ascii=True)
# -> 'ni-hao-shi-jie-hello-world'

# Formatting durations. Good for logging runtimes:
fmt_timedelta(3.33333)
# -> '3s'
fmt_timedelta(.33333)
# -> '333ms'
fmt_timedelta(.033333)
# -> '33.33ms'
fmt_timedelta(.0033333)
# -> '3.33ms'
fmt_timedelta(.00033333)
# -> '333µs'
fmt_timedelta(.000033333)
# -> '33µs'
fmt_timedelta(3333333)
# -> '39d'

# Ages in seconds or deltas.
# Note we use a sensible single numeral to keep things brief, e.g.
# "33 days ago" and not the messier "1 month and 3 days ago".
# This is important in file listings, etc, where we want to optimize
# for space and legibility.
fmt_age(60 * 60 * 24 * 33)
# -> '33 days ago'

fmt_age(60 * 60 * 24 * 33, brief=True)
# -> '33d ago'

# Use fast lazy import of the minimal pluralizer library.
plural(2, "banana")
# -> 'bananas'

# Simple plurals.
fmt_count_items(23, "banana")
# -> '23 bananas'

fmt_count_items(1, "banana")
# -> '1 banana'

# Sizes
fmt_size_human(12000000)
# -> '11.4M'

fmt_size_dual(12000000)
# -> '11.4M (12000000 bytes)'

# Helpful making __str__() methods or printing output:
fmt_words("Hello", None, "", "world!")
# -> 'Hello world!'

fmt_paras(fmt_words("Hello", "world!"), "", "Goodbye.")
# -> 'Hello world!\n\nGoodbye.'

from dataclasses import dataclass
from pathlib import Path

# Example of `abbrev_obj` to customize __str__().
# Allows sorting and truncating based on key and value.
@dataclass
class MyThing:
   file_path: Path
   title: str
   url: str
   body: str

   def __str__(self) -> str:
      return abbrev_obj(
            self,
            # Put an abbreviated title first, then the file path, then the url.
            # The `body` field will be omitted.
            key_filter={
               "title": 64,
               "file_path": 0,
               "url": 128,
            },
      )

str(MyThing(file_path="/tmp/file.txt", title="Something " + "blah " * 50, url="https://www.example.com", body="..."))
# -> "MyThing(title='Something blah blah blah blah blah blah blah blah blah blah blah…', file_path=/tmp/file.txt, url=https://www.example.com)"
```

For instructions on publishing to PyPI, see [publishing.md](publishing.md).

* * *

*This project was built from
[simple-modern-uv](https://github.com/jlevy/simple-modern-uv).*
