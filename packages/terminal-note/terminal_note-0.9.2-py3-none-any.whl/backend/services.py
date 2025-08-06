import argparse
import subprocess
import shutil
import os
import __init__

from backend.file_handler import TerminalNote
from backend.strategy import HandlerService
from sys import argv
from pathlib import Path


def open_config_file():
    editors = ["vi", "vim", "nvim", "micro", "nano"]
    editor = TerminalNote().EDITOR

    if not shutil.which(editor):
        editor_list = [editor for editor in editors if shutil.which(editor)]
        if len(editor_list) < 1:
            print("Редактор в системе не найден")
            return
        else:
            editor = editor_list[0]

    path_to_config = f"{Path.home()}/.config/terminal-note/config.toml"
    subprocess.run([editor, path_to_config], check=True)


def file_service():
    parser = argparse.ArgumentParser(
        description="Terminal-Note - сохранение и управление заметками в терминале. Где заранее определёны директория и расширение файла.",
        usage="tn [--help] [--config] [-i [TEXT]] [-o] [-d] [-r] [TEXT]",
        epilog=r"""
        Примеры: tn "Проверить логи вечером" или tn -i "Оптимизировать запрос" или tn -o или tn -r или tn -d"
        """)
    parser.add_argument(
        "-c",
        "--config",
        nargs="?",
        help="Открывает кофиг файл, если конфиг не создан, то создаёт его. Конфиг находится по адресу $HOME/.config/terminal-note/config.toml",
    )
    # Флаг -i, который требует текст
    parser.add_argument(
        "-i",
        nargs="?",
        const="",  # если -i без текста, то args.i == ''
        metavar="text",
        help='inline заметка, без открытия редактора. tn -i [text]. Имя файла в который сохранена заметка в фомате "YYYY-MM-DD H:M:S".',
    )
    # Позиционный аргумент — текст заметки
    parser.add_argument(
        "text",
        nargs="?",
        help='inline заметка, без открытия редактора. Не требует ввода флага -i: tn [text]. Имя файла в который сохранена заметка фомате "YYYY-MM-DD H:M:S".',
    )

    parser.add_argument(
       "-o", 
        nargs="?",
        help="В списке ищем нужный файл. При выборе, редактор откроет его для изменения. Если файла нет, утилита создаст файл с именем введёным в поле поиска, затем редактор открывает новый файл для изменения.",
    )
    parser.add_argument(
        "-d",
        nargs="?",
        help="В списке ищем нужный файл. При выборе файл удалится или можно отменить операцию. Корзины нет, файл удаляется навсегда.",
    )
    parser.add_argument(
        "-r",
        nargs="?",
        help="В списке ищем нужный файл. Если файл в формате .md, то его открывает утилита frogmouth. Если файл имеет другое расширение, то он будет прочитан утилитой на выбор: less, cat, bat. Утилиту нужно указать в конфиг файле.",
    )
    args = parser.parse_args()
    file_service = HandlerService(TerminalNote())
    note_text = None
    try:
        if args.i is not None:
            if args.i == "":
                parser.error("Флаг -i требует указания текста после него.")
            note_text = args.i
            file_service.inline_note(note_text)
        elif args.text:
            note_text = args.text
            file_service.inline_note(note_text)

        if argv[1] == "-r":
            file_service.read()

        if argv[1] == "-d":
            file_service.delete()

        if argv[1] == "-o":
            file_service.update()
        if argv[1] == "-c":
            open_config_file()
        if argv[1] == "--config":
            open_config_file()

    except IndexError:
        print("Используй tn --help для получения описания")


def main():
    file_service()


if __name__ == "__main__":
    main()
