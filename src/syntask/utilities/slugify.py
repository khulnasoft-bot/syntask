# Allows syntask to be used side-by-side with unicode-slugify
# See https://github.com/Synopkg/syntask/issues/6945

from slugify import slugify

__all__ = ["slugify"]
