# Scrachy
Scrachy was primarily developed to provide a flexible cache storage backend for [Scrapy](https://scrapy.org/) that stores its data in a relational database using [SQLAlchemy](https://www.sqlalchemy.org/).
However, it now has several other additional features including middleware for using Selenium to download requests.
It also comes with a downloader middleware that will optionally ignore requests that are already in the cache.

# Install
You can install the latest version from git:

```
>pip install git+https://bitbucket.org/reidswanson/scrachy.git
``` 

or from PyPI:

```
>pip install scrachy
```

> **NOTE** : `libnss3` must be installed for `chromedriver` to work.
> For example: `sudo apt install libnss3`

> **NOTE**: At least on Ubuntu, you must install `chromium-chromedriver`.
> The version downloaded by the webdriver manager fails with an error about the user data directory.

# Documentation
A brief guide to minimally using the cache storage engine and the Selenium backend are given below.
For other configuration options and features please see the full documentation on [Read the Docs](https://scrachy.readthedocs.io/en/latest).

## Storage Backend
To (minimally) use the storage backend you simply need to enable caching by adding the following to your `settings.py` file:  
```python
# Enable caching
HTTPCACHE_ENABLED = True

# Set the storage backend to the one provided by Scrachy.
HTTPCACHE_STORAGE = 'scrachy.middleware.httpcache.AlchemyCacheStorage'

# One of the supported SqlAlchemy dialects
SCRACHY_DB_DIALECT = '<database-dialect>'

# The name of the driver (that must be installed as an extra) and used.
SCRACHY_DB_DRIVER = '<database-driver>'

# Options for connecting to the database
SCRACHY_DB_HOST = '<database-hostname>'
SCRACHY_DB_PORT = '<database-port>'
SCRACHY_DB_SCHEMA = <database-schema>
SCRACHY_DB_DATABASE = '<database-name>'
SCRACHY_DB_USERNAME = '<username>'

# Note, do not store this value in the settings file. Use an environment
# variable or python-dotenv.
SCRACHY_DB_PASSWORD = '<password>'

# A dictionary of other connection arguments
SCRACHY_DB_CONNECT_ARGS = {}

# there may be a conflict with the compression middleware. If you encounter
# errors either disable it or move it after the caching middleware.
DOWNLOADER_MIDDLEWARES = {
   ...
   'scrapy.downloadermiddlewares.http.compression.HttpCompressionMiddleware': None,
}
```

# Selenium
There are two Selenium middleware classes provided by Scrachy.
To use them, first add one of them to the `DOWNLOADER_MIDDLEWARES`

```python
DOWNLOADER_MIDDLEWARES = {
    ...
    'scrachy.middleware.selenium.SeleniumMiddleware': 800,  # or AsyncSeleniumMiddleware
    ...
}
```

Then in your spider parsing code use a `SeleniumRequest` instead of a `scrapy.http.Request`.


# License
Scrachy is released using the GNU Lesser General Public License.
See the [LICENSE](LICENSE.md) file for more details.
Files that are adapted or use code from other sources are indicated either at the top of the file or at the location of the code snippet.
Some of these files were adapted from code released under a 3-clause BSD license.
Those files should indicate the original copyright in a comment at the top of the file.
See the [BSD_LICENSE](BSD_LICENSE.md) file for details of this license.
