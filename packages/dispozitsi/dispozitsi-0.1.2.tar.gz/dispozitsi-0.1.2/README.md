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

## Development

For managing the project, I use [Hatch](https://hatch.pypa.io/1.12/), so [install it](https://hatch.pypa.io/1.12/install/).

Clone project 

```bash
  git clone https://codeberg.org/spuzkov/dispozitsi.git
```

Create your environment and attach to it: 

```bash
  hatch env create
  hatch shell
```

Now, in another terminal window (make sure you have attached to your environment here as well), open the logs for debugging and seeing what is going on:

```bash
  textual console
```

Then in your original terminal window, run:

```bash
  textual run --dev src/dispozitsi/app.py
```

You should now see logs in the debugging terminal window.


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
