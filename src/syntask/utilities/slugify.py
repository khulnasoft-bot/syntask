# Allows prefect to be used side-by-side with unicode-slugify
# See https://github.com/synopkg/synopkg/issues/6945

from slugify import slugify

__all__ = ["slugify"]
