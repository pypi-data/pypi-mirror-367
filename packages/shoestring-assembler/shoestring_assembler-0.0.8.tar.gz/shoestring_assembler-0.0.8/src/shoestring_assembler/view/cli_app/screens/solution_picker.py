from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Footer, Header, OptionList, Label, Markdown, Button, Footer
from textual.containers import HorizontalGroup, Vertical, VerticalScroll
from textual.widgets.option_list import Option
from textual import on
from textual.reactive import reactive

from shoestring_assembler.interface.signals import BackSignal

import urllib.request
import yaml

INSTRUCTIONS = """
### Select which solution you want to download.
Use your mouse to click and scroll

or

Use `tab` and `shift + tab` to move between sections.
Use the `up` and `down` arrows to move up and down the list.
Use `Enter` to select the solution you want.
Press `esc` to go back.
"""


class SolutionList(OptionList):
    def __init__(
        self, *content, provider=None, solution_list={}, do_focus=False, **kwargs
    ):
        super().__init__(*content, **kwargs)
        self.solution_list = solution_list
        self.provider = provider
        self.do_focus = do_focus

    def on_mount(self):
        if self.do_focus:
            self.app.set_focus(self)
        for index, solution in enumerate(self.solution_list):
            self.add_option(Option(solution["name"], id=f"{self.provider}@{index}"))
        return super().on_mount()


class VersionList(OptionList):

    def __init__(self, *content, version_list=[], **kwargs):
        super().__init__(*content, **kwargs)
        self.version_list = version_list

    def on_mount(self):
        self.app.set_focus(self)
        for index, version in enumerate(self.version_list):
            self.add_option(Option(version, id=version))
        return super().on_mount()


class SolutionPicker(Screen):
    SUB_TITLE = "Select the Solution to Download"
    CSS_PATH = "solution_picker.tcss"
    BINDINGS = [("escape", "back", "Back")]

    def __init__(self, provider_list, **kwargs):
        super().__init__(**kwargs)
        self.provider_list = provider_list
        self.available_versions = []

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        is_first = True
        yield Header()
        with VerticalScroll():
            yield Markdown(INSTRUCTIONS)
            for tag, values in self.provider_list["providers"].items():
                yield Label(values["name"])
                yield SolutionList(
                    provider=tag,
                    solution_list=values["solutions"],
                    do_focus=is_first,
                )
                is_first = False
        with HorizontalGroup(classes="bottom_bar"):
            yield Button.error("Back (esc)", id="back")
        yield Footer()

    @on(OptionList.OptionSelected)
    def handle_selected(self, event):
        id = event.option.id
        provider, index = id.split("@")
        result = self.provider_list["providers"][provider]["solutions"][int(index)]
        self.dismiss(result)

    @on(Button.Pressed,"#back")
    def action_back(self):
        self.dismiss(BackSignal())


class SolutionVersionPicker(Screen):
    SUB_TITLE = "Select the Version to Download"
    CSS_PATH = "solution_picker.tcss"

    BINDINGS = [("escape", "back", "Back")]

    def __init__(self, available_versions, **kwargs):
        super().__init__(**kwargs)
        self.available_versions = available_versions

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        yield Header()
        with VerticalScroll():
            yield Markdown(INSTRUCTIONS)
            yield VersionList(version_list=self.available_versions)
        with Vertical(classes="bottom_bar"):
            yield Button.error("Back (esc)", id="back")

    @on(OptionList.OptionSelected)
    def handle_selected(self, event):
        self.dismiss(event.option.id)
        
    @on(Button.Pressed,"#back")
    def action_back(self):
        self.dismiss(BackSignal())


# if __name__ == "__main__":
#     # fetch solution list
#     with urllib.request.urlopen(
#         "https://github.com/DigitalShoestringSolutions/solution_list/raw/refs/heads/main/list.yaml"
#     ) as web_in:
#         content = web_in.read()
#         provider_list = yaml.safe_load(content)
#     result = SolutionPickerApp(provider_list).run()
#     print(result)
