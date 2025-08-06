import tomllib
from pathlib import Path

import __init__

path_to_config = f"{Path.home()}/.config/terminal-note/config.toml"


class Config:
    if Path(path_to_config).exists():
        with open(path_to_config, "rb") as f:
            config_data = tomllib.load(f)
    else:
        with open(f"{Path(__file__).parent}/config.toml", "rb") as f:
            config_data = tomllib.load(f)
        with open(f"{Path(__file__).parent}/config.toml", "r") as f:
            dump = f.read()
        Path(f"{Path.home()}/.config/terminal-note").mkdir(511, True, True)
        with open(path_to_config, "w") as f:
            f.write(dump)
    
    PATH_TO_STORAGE = config_data["backend"]["path_to_storage_directory"].replace(
        "$HOME", str(Path.home())
    )
    FILE_READER = config_data["backend"]["file_reader"]
    PATH_TO_TEMPLATE_FILE = config_data["template"]["path_to_template_note"].replace(
        "$HOME", str(Path.home())
    )
    EDITOR = config_data["editor"]["editor"]
    EXTENSION = config_data["backend"]["file_extension"]
    ERRORS = {
        "file_created": {0: "Файл создан"},
        "file_exists": {1: "Файл существует"},
        "template_is_not_exists": {2: "Шаблон не существует"},
        "editor_error": {3: "Редактор не найден"},
        "file_is_not_exists": {4: "Файл не существует"},
        "file_deleted": {5: "Файл удалён"},
        "text_saved": {6: "Заметка сохранена"},
        "text_saved_error": {7: "Ошибка при сохранении"},
    }
    MODE = config_data["mode"]["storage_mode"]

    if not Path(PATH_TO_STORAGE).exists():
        Path(PATH_TO_STORAGE).mkdir(511, True, True)


config = Config()
