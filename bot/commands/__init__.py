from .add_option import AddOption
from .new_poll import NewPoll
from .show_options import ShowOptions
from .start import Start

COMMANDS = {
    "add_option": AddOption,
    "new_poll": NewPoll,
    "show_options": ShowOptions,
    "start": Start,
}
