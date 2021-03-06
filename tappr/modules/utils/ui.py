import curses

from dataclasses import dataclass, field
from typing import List, Optional, Callable, Dict
from rich.progress import Progress, SpinnerColumn, TimeElapsedColumn, TextColumn
from rich.console import Console
from pygments.lexers import YamlLexer
from pygments.styles import get_style_by_name
from prompt_toolkit.styles.pygments import style_from_pygments_cls
from prompt_toolkit.lexers import PygmentsLexer
from prompt_toolkit import prompt, HTML
from prompt_toolkit.completion import WordCompleter


KEYS_ENTER = (curses.KEY_ENTER, ord("\n"), ord("\r"))
KEYS_UP = (curses.KEY_UP, ord("k"))
KEYS_DOWN = (curses.KEY_DOWN, ord("j"))
KEYS_SELECT = (curses.KEY_RIGHT, ord(" "))

console = Console()


# noinspection PyTypeChecker,PyBroadException
@dataclass
class Picker:
    options: List[str]
    title: Optional[str] = None
    indicator: str = "=>"
    default_index: int = 0
    multiselect: bool = False
    min_selection_count: int = 0
    options_map_func: Optional[Callable[[str], str]] = None
    all_selected: List[str] = field(init=False, default_factory=list)
    custom_handlers: Dict[str, Callable[["Picker"], str]] = field(init=False, default_factory=dict)
    index: int = field(init=False, default=0)
    scroll_top: int = field(init=False, default=0)

    def __post_init__(self):
        if len(self.options) == 0:
            raise ValueError("options should not be an empty list")

        if self.default_index >= len(self.options):
            raise ValueError("default_index should be less than the length of options")

        if self.multiselect and self.min_selection_count > len(self.options):
            raise ValueError("min_selection_count is bigger than the available options, you will not be able to make any selection")

        self.index = self.default_index

    def move_up(self):
        self.index -= 1
        if self.index < 0:
            self.index = len(self.options) - 1

    def move_down(self):
        self.index += 1
        if self.index >= len(self.options):
            self.index = 0

    def mark_index(self):
        if self.multiselect:
            if self.index in self.all_selected:
                self.all_selected.remove(self.index)
            else:
                self.all_selected.append(self.index)

    def get_selected(self):
        if self.multiselect:
            return_list = []
            for selected in self.all_selected:
                return_list.append(self.options[selected])
            return return_list
        else:
            return self.options[self.index], self.index

    def get_title_lines(self):
        if self.title:
            return self.title.split("\n") + [""]
        return []

    def get_option_lines(self):
        lines = []
        for index, option in enumerate(self.options):
            if self.options_map_func:
                option = self.options_map_func(option)
            if index == self.index:
                prefix = self.indicator
            else:
                prefix = len(self.indicator) * " "

            if self.multiselect and index in self.all_selected:
                fmt = curses.color_pair(1)
                line = ("{0} {1}".format(prefix, option), fmt)
            else:
                line = "{0} {1}".format(prefix, option)
            lines.append(line)

        return lines

    def get_lines(self):
        title_lines = self.get_title_lines()
        option_lines = self.get_option_lines()
        lines = title_lines + option_lines
        current_line = self.index + len(title_lines) + 1
        return lines, current_line

    def draw(self, screen):
        screen.clear()
        x, y = 1, 1
        max_y, max_x = screen.getmaxyx()
        max_rows = max_y - y
        lines, current_line = self.get_lines()
        if current_line <= self.scroll_top:
            self.scroll_top = 0
        elif current_line - self.scroll_top > max_rows:
            self.scroll_top = current_line - max_rows
        lines_to_draw = lines[self.scroll_top : self.scroll_top + max_rows]
        for line in lines_to_draw:
            if type(line) is tuple:
                screen.addnstr(y, x, line[0], max_x - 2, line[1])
            else:
                screen.addnstr(y, x, line, max_x - 2)
            y += 1
        screen.refresh()

    def run_loop(self, screen):
        while True:
            self.draw(screen)
            c = screen.getch()
            if c in KEYS_UP:
                self.move_up()
            elif c in KEYS_DOWN:
                self.move_down()
            elif c in KEYS_ENTER:
                if self.multiselect and len(self.all_selected) < self.min_selection_count:
                    continue
                return self.get_selected()
            elif c in KEYS_SELECT and self.multiselect:
                self.mark_index()
            elif c in self.custom_handlers:
                ret = self.custom_handlers[c](self)
                if ret:
                    return ret

    @staticmethod
    def config_curses():
        try:
            curses.use_default_colors()
            curses.curs_set(0)
            curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_WHITE)
        except Exception:
            curses.initscr()

    def _start(self, screen):
        self.config_curses()
        return self.run_loop(screen)

    def start(self):
        return curses.wrapper(self._start)


class UI:
    def __init__(self, subprocess_helper, logger):
        self.sh = subprocess_helper
        self.logger = logger

    def progress(self, cmd, message, state):
        self.logger.msg(f"Running: {cmd}", bold=False) if state["verbose"] else None
        proc, out, err = None, None, None
        with Progress(TextColumn(f"{message}"), SpinnerColumn(spinner_name="point"), TimeElapsedColumn(), transient=True) as progress:
            task = progress.add_task("", total=1)
            while not progress.finished:
                proc, out, err = self.sh.run_proc(f"{cmd}")
                progress.update(task_id=task, advance=1)

        self.logger.msg(f"\n{out.decode()}", bold=False) if state["verbose"] and out else None
        self.logger.msg(f"\n{err.decode()}", bold=False) if state["verbose"] and err else None
        return proc, out, err

    def sh_call(self, cmd, msg, spinner_msg, error_msg, state):
        self.logger.msg(msg, bold=False)
        proc, _, _ = self.progress(cmd=cmd, state=state, message=spinner_msg)
        if proc.returncode != 0 and error_msg is not None:
            self.logger.msg(error_msg)
        return proc.returncode

    # noinspection PyTypeChecker
    @staticmethod
    def yaml_prompt(message, auto_complete_list=None, default=""):
        console.rule(f"{message}")
        style = style_from_pygments_cls(get_style_by_name("native"))
        if auto_complete_list:
            auto_complete_list = WordCompleter(auto_complete_list)
        else:
            auto_complete_list = list()
        return prompt(
            bottom_toolbar=HTML('Press <b><style bg="ansired">[ESC]</style></b> and <b><style bg="ansired">[ENTER]</style></b> when you are done'),
            lexer=PygmentsLexer(YamlLexer),
            style=style,
            include_default_pygments_style=False,
            completer=auto_complete_list,
            multiline=True,
            default=default,
            wrap_lines=True,
        )
