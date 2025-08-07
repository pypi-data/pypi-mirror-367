
# Dispozitsi

A debugger for Logstash's Grok parsing language. This debugger has a simple but lovely terminal user interface (TUI) that follows the ["bish bash bosh"](https://en.wiktionary.org/wiki/bish_bash_bosh) -principle. The debugger will take a pattern and sample and then generate outcome. Outcome will be shown to you as a list of dictionaries.

## Note: Still in development (bugs expected)
## Installation

Install with [pipx](https://github.com/pypa/pipx) (recommended)

```bash
  pipx install dispozitsi
```

Install with [pip](https://pip.pypa.io/en/stable/installation/)

```bash
  pip install dispozitsi
```

### Run command

```bash
  dispozitsi
```
## Roadmap

- Add pattern suggestions

- Make slow regex fast regex

- Highlighting for matches

- Allow log file insertion

- Allow to continue from previous state, meaning pattern, sample and outcome stay as they were on program launch.

- Display hints on how to fix broken pattern

- Keyboard shortcuts

- More [pattern](https://github.com/logstash-plugins/logstash-patterns-core/tree/main/patterns/ecs-v1) support (maybe)

- Documentation on patterns with examples, so that user can easily check what patterns suits their usecase.
