Changelog
=========


(unreleased)
------------
- Feat: add MinioWriter for S3-compatible object storage. [Bruno Rahle,
  Claude]

  Add MinioWriter class that mirrors FileWriter interface but writes to configurable MinIO/S3 buckets. Supports pandas DataFrames, JSON objects, HTTP responses, and async streaming with automatic bucket creation and timestamp columns.

  🤖 Generated with [Claude Code](https://claude.ai/code)
- Minor changes to file listing. [Bruno Rahle]


0.11.0 (2024-08-20)
-------------------
- Release: version 0.11.0 🚀 [Bruno Rahle]
- Refactor: reorganize imports and add RootedReader to brds.core.fs.
  [Bruno Rahle]


0.10.0 (2024-08-18)
-------------------
- Release: version 0.10.0 🚀 [Bruno Rahle]
- Hotfixing - removing print' [Bruno Rahle]


0.9.0 (2024-08-18)
------------------
- Release: version 0.9.0 🚀 [Bruno Rahle]
- Stream Writer (#12) [Bruno Rahle]

  * Stream Writer

  * Fixing the formatting


0.8.0 (2024-08-18)
------------------
- Release: version 0.8.0 🚀 [Bruno Rahle]
- Fixing the logger. [Bruno Rahle]


0.7.0 (2024-08-18)
------------------
- Release: version 0.7.0 🚀 [Bruno Rahle]
- BREAKING CHANGE: New aiohttp HttpClient (#11) [Bruno Rahle]

  * Breaking Changes to the HttpClient, BrowserEmulator, improvements to the Domain Rate Limiter and Logger

  * Fixing tests

  * Fixing Crawler


0.6.0 (2024-08-18)
------------------
- Release: version 0.6.0 🚀 [Bruno Rahle]
- Fixing Crawler. [Bruno Rahle]
- Fixing tests. [Bruno Rahle]
- Breaking Changes to the HttpClient, BrowserEmulator, improvements to
  the Domain Rate Limiter and Logger. [Bruno Rahle]


0.5.0 (2024-05-27)
------------------
- Release: version 0.5.0 🚀 [Bruno Rahle]
- Fixing lint. [Bruno Rahle]
- Adding pipeline crawl. [Bruno Rahle]
- Fixing formatting. [Bruno Rahle]
- Improvements. [Bruno Rahle]


0.4.1 (2023-09-08)
------------------
- Release: version 0.4.1 🚀 [Bruno Rahle]
- Fixing the release script (#10) [Bruno Rahle]

  * Fixing the release script

  * Adding the automatic next version detection


0.4.0 (2023-09-08)
------------------
- Release: version 0.4.0 🚀 [Bruno Rahle]
- Release: version  🚀 [Bruno Rahle]
- Crawler working with loop variables (#9) [Bruno Rahle]
- Release: version  🚀 [Bruno Rahle]
- Release: version  🚀 [Bruno Rahle]
- Crawler implementation (#8) [Bruno Rahle]

  * Crawler implementation

  * Fixing lint

  * Storing variables


0.3.1 (2023-04-17)
------------------
- Release: version 0.3.1 🚀 [brahle]
- Removing unsupported flag. [brahle]
- Fixing the files. [brahle]
- Removing codecov which is deleted. [brahle]
- CORS. [brahle]


0.3.0 (2023-04-11)
------------------
- Release: version 0.3.0 🚀 [brahle]
- Release: version 0..0 🚀 [brahle]
- Preventing exploits. [brahle]


0.2.8 (2023-04-10)
------------------
- Release: version 0.2.8 🚀 [brahle]
- Also tagging the version from the ref. [brahle]


0.2.7 (2023-04-10)
------------------
- Release: version 0.2.7 🚀 [brahle]
- Fixing the publishing. [brahle]


0.2.6 (2023-04-10)
------------------
- Release: version 0.2.6 🚀 [brahle]
- Fixing return types. [brahle]
- Publish to docker. [brahle]


0.2.5 (2023-04-10)
------------------
- Release: version 0.2.5 🚀 [brahle]
- Adding pandas stubs. [brahle]


0.2.4 (2023-04-10)
------------------
- Release: version 0.2.4 🚀 [brahle]
- Fixing packaging. [brahle]


0.2.3 (2023-04-10)
------------------
- Release: version 0.2.3 🚀 [brahle]
- Adding .typed file. [brahle]


0.2.2 (2023-04-10)
------------------
- Release: version 0.2.2 🚀 [brahle]
- Exposing some additional items. [brahle]


0.2.1 (2023-04-10)
------------------
- Release: version 0.2.1 🚀 [brahle]
- Fixing the formatting. [brahle]


0.2.0 (2023-04-10)
------------------
- Release: version 0.2.0 🚀 [brahle]
- Edit (#7) [Bruno Rahle]


0.1.1 (2023-04-10)
------------------
- Release: version 0.1.1 🚀 [brahle]
- Release: version 0.1.0 🚀 [brahle]
- Merge branch 'main' of github.com:brahle/brds into main. [brahle]
- Br/updates (#6) [Bruno Rahle]

  * Adding FastAPI app to show the datasets

  * Updates to the container


0.1.0 (2023-04-10)
------------------
- Release: version 0.1.0 🚀 [brahle]


0.0.5 (2023-02-18)
------------------
- Release: version 0.0.5 🚀 [brahle]
- Feat: Adding gunzip imporer (#5) [Bruno Rahle]


0.0.4 (2023-02-18)
------------------
- Release: version 0.0.4 🚀 [brahle]
- Updating version (#4) [Bruno Rahle]


0.0.3 (2023-02-18)
------------------
- Release: version 0.0.3 🚀 [brahle]
- Fixing the docs (#3) [Bruno Rahle]


0.0.2 (2023-02-18)
------------------

Fix
~~~
- Release (#2) [Bruno Rahle]

Other
~~~~~
- Release: version 0.0.2 🚀 [brahle]


0.0.1 (2023-02-18)
------------------
- Release: version 0.0.1 🚀 [brahle]
- Feat: Initial version (#1) [Bruno Rahle]

  * Initial version of the brds

  * Fixing license

  * Adding fetcher and importer

  * Fixing the code
- ✅ Ready to clone and code. [brahle]
- Initial commit. [Bruno Rahle]


