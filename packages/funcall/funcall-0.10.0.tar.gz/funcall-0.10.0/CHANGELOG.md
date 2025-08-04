## v0.10.0

[v0.9.1...v0.10.0](https://github.com/Jannchie/funcall/compare/v0.9.1...v0.10.0)

### :sparkles: Features

- **context**: auto-wrap context if not Context - By [Jianqi Pan](mailto:jannchie@gmail.com) in [86cb43a](https://github.com/Jannchie/funcall/commit/86cb43a)

### :memo: Documentation

- **dynamic-tools**: remove dynamic tools usage guide - By [Jianqi Pan](mailto:jannchie@gmail.com) in [d31ebbf](https://github.com/Jannchie/funcall/commit/d31ebbf)

### :wrench: Chores

- **dependencies**: move pytest-asyncio to dev group - By [Jianqi Pan](mailto:jannchie@gmail.com) in [dc2a1de](https://github.com/Jannchie/funcall/commit/dc2a1de)
- **deps**: update lock file - By [Jianqi Pan](mailto:jannchie@gmail.com) in [18fe787](https://github.com/Jannchie/funcall/commit/18fe787)

## v0.9.1

[v0.9.0...v0.9.1](https://github.com/Jannchie/funcall/compare/v0.9.0...v0.9.1)

### :art: Refactors

- **funcall**: update completion tool param typing and usage - By [Jianqi Pan](mailto:jannchie@gmail.com) in [5d8b5a2](https://github.com/Jannchie/funcall/commit/5d8b5a2)

### :wrench: Chores

- **deps**: update lock file - By [Jianqi Pan](mailto:jannchie@gmail.com) in [315567d](https://github.com/Jannchie/funcall/commit/315567d)

## v0.9.0

[v0.8.0...v0.9.0](https://github.com/Jannchie/funcall/compare/v0.8.0...v0.9.0)

### :sparkles: Features

- **funcall**: add dynamic tool and function management apis - By [Jianqi Pan](mailto:jannchie@gmail.com) in [b92d4ba](https://github.com/Jannchie/funcall/commit/b92d4ba)

### :wrench: Chores

- update lock file - By [Jianqi Pan](mailto:jannchie@gmail.com) in [cd6fce6](https://github.com/Jannchie/funcall/commit/cd6fce6)

## v0.8.0

[v0.7.0...v0.8.0](https://github.com/Jannchie/funcall/compare/v0.7.0...v0.8.0)

### :sparkles: Features

- **examples**: add openai function call completion example - By [Jianqi Pan](mailto:jannchie@gmail.com) in [6778d4c](https://github.com/Jannchie/funcall/commit/6778d4c)

### :art: Refactors

- **litellm**: rename litellm target to completion - By [Jianqi Pan](mailto:jannchie@gmail.com) in [f01f0d2](https://github.com/Jannchie/funcall/commit/f01f0d2)

## v0.7.0

[v0.6.0...v0.7.0](https://github.com/Jannchie/funcall/compare/v0.6.0...v0.7.0)

### :sparkles: Features

- **decorators**: add tool decorator and ToolWrapper class - By [Jianqi Pan](mailto:jannchie@gmail.com) in [3b4ea44](https://github.com/Jannchie/funcall/commit/3b4ea44)

### :adhesive_bandage: Fixes

- **typing**: add type ignore for union and tool choice - By [Jianqi Pan](mailto:jannchie@gmail.com) in [b6df111](https://github.com/Jannchie/funcall/commit/b6df111)

### :memo: Documentation

- **project**: update project description in pyproject.toml - By [Jianqi Pan](mailto:jannchie@gmail.com) in [968736f](https://github.com/Jannchie/funcall/commit/968736f)

## v0.6.0

[v0.5.0...v0.6.0](https://github.com/Jannchie/funcall/compare/v0.5.0...v0.6.0)

### :rocket: Breaking Changes

- **funcall**: modularize and reorganize core logic - By [Jianqi Pan](mailto:jannchie@gmail.com) in [7501399](https://github.com/Jannchie/funcall/commit/7501399)

### :sparkles: Features

- **funcall**: add call_function and async variants && improve litellm required field handling && add examples and tests - By [Jianqi Pan](mailto:jannchie@gmail.com) in [b7bf0da](https://github.com/Jannchie/funcall/commit/b7bf0da)

## v0.5.0

[v0.4.0...v0.5.0](https://github.com/Jannchie/funcall/compare/v0.4.0...v0.5.0)

### :rocket: Breaking Changes

- **funcall**: rewrite funcall for clarity and extensibility - By [Jianqi Pan](mailto:jannchie@gmail.com) in [fd87cb6](https://github.com/Jannchie/funcall/commit/fd87cb6)

## v0.4.0

[v0.3.0...v0.4.0](https://github.com/Jannchie/funcall/compare/v0.3.0...v0.4.0)

### :rocket: Breaking Changes

- **schema**: simplify params_to_schema signature and remove unused no_refs parameter - By [Jianqi Pan](mailto:jannchie@gmail.com) in [f5055a2](https://github.com/Jannchie/funcall/commit/f5055a2)

### :sparkles: Features

- **funcall**: add async support for function call handling - By [Jianqi Pan](mailto:jannchie@gmail.com) in [d0aa612](https://github.com/Jannchie/funcall/commit/d0aa612)
- **funcall**: add litellm support for function call handling - By [Jianqi Pan](mailto:jannchie@gmail.com) in [5fa1c33](https://github.com/Jannchie/funcall/commit/5fa1c33)
- **schema**: support inline schema without $refs - By [Jianqi Pan](mailto:jannchie@gmail.com) in [0e09282](https://github.com/Jannchie/funcall/commit/0e09282)

### :art: Refactors

- **params-to-schema**: remove redundant exception handling - By [Jianqi Pan](mailto:jannchie@gmail.com) in [8f8139d](https://github.com/Jannchie/funcall/commit/8f8139d)

## v0.3.0

[v0.2.0...v0.3.0](https://github.com/Jannchie/funcall/compare/v0.2.0...v0.3.0)

### :rocket: Breaking Changes

- **params-to-schema**: disallow bare dict types in params and add better type checks - By [Jianqi Pan](mailto:jannchie@gmail.com) in [6516e63](https://github.com/Jannchie/funcall/commit/6516e63)

### :sparkles: Features

- **funcall**: support context params and improve array handling - By [Jianqi Pan](mailto:jannchie@gmail.com) in [ee9de86](https://github.com/Jannchie/funcall/commit/ee9de86)
- **funcall**: add dataclass support for parameter schema and function call - By [Jianqi Pan](mailto:jannchie@gmail.com) in [795c09d](https://github.com/Jannchie/funcall/commit/795c09d)

## v0.2.0

[v0.1.0...v0.2.0](https://github.com/Jannchie/funcall/compare/v0.1.0...v0.2.0)

### :sparkles: Features

- **testing**: add pytest config && update pyproject.toml for pytest-cov && improve funcall param type hints && add tests - By [Jianqi Pan](mailto:jannchie@gmail.com) in [4d66871](https://github.com/Jannchie/funcall/commit/4d66871)

## v0.1.0

[9bcbc5e83f7d97b4a639e78ea61aa415c4e20a4d...v0.1.0](https://github.com/Jannchie/funcall/compare/9bcbc5e83f7d97b4a639e78ea61aa415c4e20a4d...v0.1.0)

### :wrench: Chores

- **ci**: add github actions workflow for python package build and release - By [Jianqi Pan](mailto:jannchie@gmail.com) in [5fd7312](https://github.com/Jannchie/funcall/commit/5fd7312)
