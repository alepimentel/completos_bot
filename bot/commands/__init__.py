from .about import About
from .add_option import AddOption
from .config import Config
from .new_poll import NewPoll
from .show_options import ShowOptions
from .start import Start

COMMANDS = {
    "about": About,
    "add_option": AddOption,
    "config": Config,
    "new_poll": NewPoll,
    "show_options": ShowOptions,
    "start": Start,
}
