# Copyright (C) 2025 Spuzkov

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.


import re

from textual import log, on
from textual.app import App, ComposeResult
from textual.containers import Container, Vertical
from textual.validation import Function, ValidationResult
from textual.widgets import Header, Input, Pretty, TextArea

from dispozitsi.errors import (
    DuplicateSemanticError,
    SemanticNotValidIdentifierError,
    UnknownPatternError,
)
from dispozitsi.pattern_file_handler import PatternFileHandler
from dispozitsi.pattern_handler import GrokPatternHandler
from dispozitsi.reactives import Pattern, Sample


class Dispozitsi(App):
    def __init__(self):
        super().__init__(css_path=["styles.tcss"])
        self.pattern_handler = GrokPatternHandler()
        self.pattern_file_handler = PatternFileHandler()
        self.lines_in_sample_text_area: int = 0

        # INPUT PATTERN FIELD RELATED
        self.input_pattern = Input(
            placeholder="e.g. %{USERNAME:username}",
            validators=[
                Function(
                    self.__validate_input_pattern,
                    "Pattern doesn't fully match the sample.",
                )
            ],
            select_on_focus=False,
            id="grok-pattern-container",
        )
        self.input_pattern.border_title = "Grok Pattern"

        # SAMPLE TEXTAREA RELATED
        self.sample_text_area = TextArea(id="sample-container")
        self.sample_text_area.border_title = "Sample"
        self.sample_text_area.show_line_numbers = True

        # OUTCOME PRETTY RELATED
        self.pretty_outcome = Pretty([{}], id="outcome")
        self.pretty_outcome.border_title = "Outcome"

    def compose(self) -> ComposeResult:
        yield Header()
        with Vertical(classes="layout-left"):
            yield self.input_pattern
            yield Pretty([], id="information")
            yield self.sample_text_area
        with Container(classes="layout-right"):
            yield self.pretty_outcome

    def on_mount(self) -> None:
        self.title = "Dispozitsi"
        self.sub_title = "Grok Debugger"
        self.query_one("HeaderIcon").visible = False
        self.pattern_file_handler.load_patterns()
        self.notify(
            "Bugs and slowness expected.\n"
            "The debugger is still in its early days, "
            "but please go ahead and try it! "
            "You can report issues and wanted features to:\n"
            "https://codeberg.org/spuzkov/dispozitsi/issues",
            timeout=6,
        )

    @on(Input.Changed)
    def on_input_change(self, event: Input.Changed) -> None:
        Pattern.pattern = event.value
        self.__update_sample_text_area_line_count()
        self.revalidate()

    @on(TextArea.Changed)
    def on_sample_change(self, event: TextArea.Changed) -> None:
        Sample.sample = event.text_area.text
        self.__update_sample_text_area_line_count()
        self.revalidate()

    def revalidate(self) -> None:
        """Does Input revalidation"""
        revalidation = self.input_pattern.validate(Pattern.pattern)
        if revalidation.is_valid:
            self.__apply_widget_updates_on_validation_success()
        else:
            self.__apply_widget_updates_on_validation_failure(validation=revalidation)

    def __validate_input_pattern(self, input_value: str) -> re.Match | None:
        """Checks if the given pattern works with the given sample."""
        try:
            if self.lines_in_sample_text_area >= 1:
                for line in self.sample_text_area.document.lines:
                    compiled = self.pattern_handler.compile(input_value.__str__())
                    return re.fullmatch(compiled, line)
        except (
            UnknownPatternError,
            DuplicateSemanticError,
            SemanticNotValidIdentifierError,
        ) as custom_error:
            self.query_one("#outcome").update(custom_error.msg)
        except re.error:
            pass  # pass, because it complains about stupid shit

    def __update_sample_text_area_line_count(self):
        self.lines_in_sample_text_area = self.sample_text_area.document.line_count

    def __apply_widget_updates_on_validation_success(self) -> None:
        log.info("Validation was a success.")
        self.pattern_handler.dictify_pattern_matches(self.sample_text_area.document.lines)
        self.query_one("#outcome").update(self.pattern_handler.results)
        self.query_one("#information").update("OK")

    def __apply_widget_updates_on_validation_failure(self, validation: ValidationResult) -> None:
        log.info("Validation was a failure.")
        self.query_one("#information").update(validation.failure_descriptions)
        if not (
            self.pattern_handler.duplicate_semantic_detected
            or self.pattern_handler.unknown_pattern_key_detected
            or self.pattern_handler.invalid_semantic_identifier_detected
        ):
            self.query_one("#outcome").update([None])


if __name__ == "__main__":
    Dispozitsi().run()
