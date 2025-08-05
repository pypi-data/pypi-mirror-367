# Changelog

## 0.1.0 (2025-08-04)

Full Changelog: [v0.1.0-alpha.3...v0.1.0](https://github.com/anchorbrowser/AnchorBrowser-SDK-Python/compare/v0.1.0-alpha.3...v0.1.0)

### Features

* **client:** support file upload requests ([1d061c7](https://github.com/anchorbrowser/AnchorBrowser-SDK-Python/commit/1d061c76863effca616217013dbd3b123d38ff67))

## 0.1.0-alpha.3 (2025-07-25)

Full Changelog: [v0.1.0-alpha.2...v0.1.0-alpha.3](https://github.com/anchorbrowser/AnchorBrowser-SDK-Python/compare/v0.1.0-alpha.2...v0.1.0-alpha.3)

### Chores

* **project:** add settings file for vscode ([700d561](https://github.com/anchorbrowser/AnchorBrowser-SDK-Python/commit/700d5613b0d22d41afa095b4dc4e62d8cfb822ae))

## 0.1.0-alpha.2 (2025-07-23)

Full Changelog: [v0.1.0-alpha.1...v0.1.0-alpha.2](https://github.com/anchorbrowser/AnchorBrowser-SDK-Python/compare/v0.1.0-alpha.1...v0.1.0-alpha.2)

### Features

* **agent:** add Agent and Browser resources for AI task execution ([36eab12](https://github.com/anchorbrowser/AnchorBrowser-SDK-Python/commit/36eab12a4d3ea747a6f863c3c43cc51a03461ba4))


### Bug Fixes

* **parsing:** parse extra field types ([0348a34](https://github.com/anchorbrowser/AnchorBrowser-SDK-Python/commit/0348a34079f2fc5ecf9ad5d5eaf1fed486d0263c))


### Refactors

* add type hints to agent and browser resource methods for improved clarity ([047d45c](https://github.com/anchorbrowser/AnchorBrowser-SDK-Python/commit/047d45c79efd205353f21b9ec6d9960d332ddc94))

## 0.1.0-alpha.1 (2025-07-22)

Full Changelog: [v0.0.1-alpha.0...v0.1.0-alpha.1](https://github.com/anchorbrowser/AnchorBrowser-SDK-Python/compare/v0.0.1-alpha.0...v0.1.0-alpha.1)

### Features

* **api:** update via SDK Studio ([aae0b21](https://github.com/anchorbrowser/AnchorBrowser-SDK-Python/commit/aae0b2165a6e1d5752caae8f7ccc2a9803fa0e81))
* **api:** update via SDK Studio ([4bc1b11](https://github.com/anchorbrowser/AnchorBrowser-SDK-Python/commit/4bc1b11fe99772232badf8edd0cbc5f42786d5ab))
* **api:** update via SDK Studio ([36c7b5d](https://github.com/anchorbrowser/AnchorBrowser-SDK-Python/commit/36c7b5d7d35c515def4505bed61642a3a2b99bb0))
* **api:** update via SDK Studio ([de3b1cb](https://github.com/anchorbrowser/AnchorBrowser-SDK-Python/commit/de3b1cb78e3089c9d4467ce44cb6bd278defa9dd))
* **api:** update via SDK Studio ([16a14ae](https://github.com/anchorbrowser/AnchorBrowser-SDK-Python/commit/16a14aeece153205879d85d7d65eeb24ba14710d))
* clean up environment call outs ([e3b0db4](https://github.com/anchorbrowser/AnchorBrowser-SDK-Python/commit/e3b0db42d94a9addd13907a9534fbcba1a13bd1a))
* **client:** add support for aiohttp ([eb810df](https://github.com/anchorbrowser/AnchorBrowser-SDK-Python/commit/eb810df52b8d0edfdc4d74949f12a3719465958e))


### Bug Fixes

* **ci:** correct conditional ([74e90a4](https://github.com/anchorbrowser/AnchorBrowser-SDK-Python/commit/74e90a4749ce0c8966e5b5f2a6b2120741031601))
* **client:** don't send Content-Type header on GET requests ([8bb8fc4](https://github.com/anchorbrowser/AnchorBrowser-SDK-Python/commit/8bb8fc43c4f49b519d431826b23325c1b7f841c3))
* **parsing:** correctly handle nested discriminated unions ([9664c69](https://github.com/anchorbrowser/AnchorBrowser-SDK-Python/commit/9664c696f73468a579ec87a7faaeeef9c6ede277))
* **parsing:** ignore empty metadata ([b3d415d](https://github.com/anchorbrowser/AnchorBrowser-SDK-Python/commit/b3d415d8f3f05794e646968b21f3ad28f4652001))
* **tests:** fix: tests which call HTTP endpoints directly with the example parameters ([174dbf2](https://github.com/anchorbrowser/AnchorBrowser-SDK-Python/commit/174dbf26c1ffa0a33390a359bfc00d1c1dc2b4f2))


### Chores

* change publish docs url ([5662a25](https://github.com/anchorbrowser/AnchorBrowser-SDK-Python/commit/5662a2553ef5c8646d818cea97f95bf4a3f03f24))
* **ci:** change upload type ([6246e63](https://github.com/anchorbrowser/AnchorBrowser-SDK-Python/commit/6246e63a1735788dc76d302b093a42c063bc94ee))
* **ci:** enable for pull requests ([7da816f](https://github.com/anchorbrowser/AnchorBrowser-SDK-Python/commit/7da816f307b68431eb5ceeb1aad2bd37bda04acf))
* **ci:** only run for pushes and fork pull requests ([fad4348](https://github.com/anchorbrowser/AnchorBrowser-SDK-Python/commit/fad4348ddbe022b93b8379064d91a4fdbcadb528))
* configure new SDK language ([f87cd53](https://github.com/anchorbrowser/AnchorBrowser-SDK-Python/commit/f87cd53bf4539fb7ca20186221f7e62bd99a0063))
* **internal:** bump pinned h11 dep ([e85f2f1](https://github.com/anchorbrowser/AnchorBrowser-SDK-Python/commit/e85f2f1d727ef7e7555ce2152f0c7c6fa735df19))
* **internal:** codegen related update ([813ecf6](https://github.com/anchorbrowser/AnchorBrowser-SDK-Python/commit/813ecf6bb7c1089271535ac91266d5c44a2bf1a0))
* **internal:** update conftest.py ([5d6fe7f](https://github.com/anchorbrowser/AnchorBrowser-SDK-Python/commit/5d6fe7f72c136e58b2ac50f8e853c7bd56a91b5b))
* **package:** mark python 3.13 as supported ([14c652e](https://github.com/anchorbrowser/AnchorBrowser-SDK-Python/commit/14c652e67860243ec945d12eb2d9db6fa8070e2f))
* **readme:** fix version rendering on pypi ([4029dea](https://github.com/anchorbrowser/AnchorBrowser-SDK-Python/commit/4029dea3455d630d095526cb62eda9910356628a))
* **readme:** update badges ([4cf2b25](https://github.com/anchorbrowser/AnchorBrowser-SDK-Python/commit/4cf2b25723384e3e99bab05db2c1f44f3227e260))
* **tests:** add tests for httpx client instantiation & proxies ([948c071](https://github.com/anchorbrowser/AnchorBrowser-SDK-Python/commit/948c071f0b5083cb63402e35fdf3de750919f684))
* **tests:** skip some failing tests on the latest python versions ([cd1c00c](https://github.com/anchorbrowser/AnchorBrowser-SDK-Python/commit/cd1c00c96b61adc92c8072ebb34c56e3607db945))
* update SDK settings ([607f825](https://github.com/anchorbrowser/AnchorBrowser-SDK-Python/commit/607f8254e2ce04ae90a6801cb273e11eddf4c5d7))
* update SDK settings ([75484da](https://github.com/anchorbrowser/AnchorBrowser-SDK-Python/commit/75484da80e2128d0907f658bf5db8d4cf6b4c215))


### Documentation

* **client:** fix httpx.Timeout documentation reference ([7ac2730](https://github.com/anchorbrowser/AnchorBrowser-SDK-Python/commit/7ac27300a8082c206a8573b90553de758bc9c349))
