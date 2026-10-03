# AGENTS GUIDE

这个项目旨在解析已有的 aoe2de tree-related mod，并进行图形贴图替换，创建新的 mod.

## Code Style Requirements

### General
- Modern syntax for the target language version
- No deprecated patterns
- Type-safe by default
- Directly manage the `.env` file or database. Treat this as an alpha-stage project under active development.
- Use English for all code and comments unless i18n or external requirements mandate otherwise.

#### Simplicity First

Minimum code that solves the problem. Nothing speculative.

-No features beyond what was asked.
-No abstractions for single-use code.
-No "flexibility" or "configurability" that wasn't requested.
-No error handling for impossible scenarios.
-If you write 200 lines and it could be 50, rewrite it.

Ask yourself: "Would a senior engineer say this is overcomplicated?" If yes, simplify.

## Resource

In the `reference` folder, you can find 

## Project structure

```text
.
- .agents/  # Project-specific agent configurations.
- agent/  # agent generated files.
  - reports/  # gather all one-time agent reports here.
    - YYMMDD_HHMM-*.md  # report prefix with date.
- reference/  # relevant resources, such as tools, other mod projects. Treat this as read-only reference material.
  - reference.md/ provide related links and resources. use it as a starting point.
```
