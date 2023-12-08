import json
import typing as t


def save_to_json(content: t.Any, filename: str) -> None:
    """
    Save rules dictionary into file as json.

    Args:
        content: dict to save
        filename: name of the output file
    """
    with open(filename, 'w') as savefile:
        savefile.write(json.dumps(content, indent=2))


def load_from_json(filename: str) -> t.Any:
    """
    Load rules dictionary from file.

    Args:
        filename: name of the file to load dictionary from

    Returns:
        dictionary of rules to execute
    """
    with open(filename) as loadfile:
        return json.loads(loadfile.read())
