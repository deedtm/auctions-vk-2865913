import os

import dotenv
from rich.console import Console
from rich.table import Table

if not os.path.exists(".env"):
    with open(".env", "w") as f:
        f.write("")
console = Console()

header = lambda s: "[bold magenta]" + f"[ {s} ]".center(50, "=") + "[/bold magenta]"
mini_header = lambda s: "[bold magenta]" + f"[ {s} ]" + "[/bold magenta]"
success = lambda s: "[yellow]" + s + "[/yellow]"
info = lambda s: "[italic blue]" + s + "[/italic blue]"
important = lambda s: "[bold]" + s + "[/bold]"


def set_group_tokens():
    print()
    console.print(header("Установка токенов группы"))
    console.print(
        info(
            f"Все токены должны иметь доступ к {important('управлению, сообщениям, документам и стене сообщества')}"
        )
    )
    console.print(info("Для окончания установки нажмите Enter без ввода чего-либо"))
    i = 1
    auction_token = input(f"Введите токен группы №{i}: ")
    tokens = [auction_token]
    while auction_token:
        i += 1
        auction_token = input(f"Введите токен группы №{i}: ")
        if auction_token:
            tokens.append(auction_token)
        else:
            break

    dotenv.set_key(".env", "PUBLISHER_TOKENS", " ".join(tokens), quote_mode="never")
    console.print(success("Токены групп успешно установлены!"))


def set_user_token():
    print()
    console.print(header("Установка токена пользователя"))
    console.print(info("Токену должны быть предоставлены права на стену и группы"))
    user_token = input("Введите токен: ")
    dotenv.set_key(".env", "USER_TOKEN", user_token, quote_mode="never")
    console.print(success("Токен пользователя успешно установлен!"))


def set_moderator_ids():
    print()
    console.print(header("Установка айди модераторов"))
    console.print(info(f"Введите айди {important('модераторов')} через пробел"))
    moderator_ids = console.input(f"Введите айди {important('модераторов')}: ")
    dotenv.set_key(".env", "MODERATORS_IDS", moderator_ids, quote_mode="never")
    console.print(success("Айди модераторов успешно установлены!"))


def set_admin_ids():
    print()
    console.print(header("Установка айди админов"))
    console.print(info(f"Введите айди {important('админов')} через пробел"))
    admin_ids = console.input(f"Введите айди {important('админов')}: ")
    dotenv.set_key(".env", "ADMINS_IDS", admin_ids, quote_mode="never")
    console.print(success("Айди админов успешно установлены!"))


def set_terminal():
    print()
    console.print(header("Установка терминала"))
    console.print(info("Введите данные от терминала"))
    terminal_key = console.input("Введите ключ терминала: ")
    secret_key = console.input("Введите пароль терминала: ")
    dotenv.set_key(".env", "TERMINAL_KEY", terminal_key, quote_mode="never")
    dotenv.set_key(".env", "SECRET_KEY", secret_key, quote_mode="never")
    console.print(success("Ключ и пароль терминала успешно установлены!"))


def set_full_tokens():
    print()
    console.print(header("Полная установка токенов"))
    set_group_tokens()
    set_user_token()
    console.print(success("Полная установка токенов завершена!"))
    main_menu()


def set_full_env():
    print()
    console.print(header("Полная установка окружения"))
    set_group_tokens()
    set_user_token()
    set_moderator_ids()
    set_admin_ids()
    set_terminal()
    console.print(success("Полная установка окружения завершена!"))
    main_menu()


def reset_group_tokens():
    print()
    console.print(header("Сброс токенов для аукционов"))
    dotenv.unset_key(".env", "PUBLISHER_TOKENS")
    console.print(success("Токены для аукционов успешно сброшены!"))


def reset_user_token():
    print()
    console.print(header("Сброс токена пользователя"))
    dotenv.unset_key(".env", "USER_TOKEN")
    console.print(success("Токен пользователя успешно сброшен!"))


def reset_moderator_ids():
    print()
    console.print(header("Сброс айди модераторов"))
    dotenv.unset_key(".env", "MODERATORS_IDS")
    console.print(success("Айди модераторов успешно сброшены!"))


def reset_admins_ids():
    print()
    console.print(header("Сброс айди админов"))
    dotenv.unset_key(".env", "ADMINS_IDS")
    console.print(success("Айди админов успешно сброшены!"))


def reset_terminal():
    print()
    console.print(header("Сброс терминала"))
    dotenv.unset_key(".env", "TERMINAL_KEY")
    dotenv.unset_key(".env", "SECRET_KEY")
    console.print(success("Ключ и пароль терминала успешно сброшены!"))


def reset_full_env():
    print()
    console.print(header("Полный сброс окружения"))
    reset_group_tokens()
    reset_moderator_ids()
    reset_admins_ids()
    reset_terminal()
    console.print(success("Полный сброс окружения завершен!"))
    main_menu()


def full_setup_menu():
    while True:
        console.print(header("Полная установка"))
        console.print("[green]1. Полная установка окружения[/green]")
        console.print("[green]2. Полная установка токенов[/green]")
        console.print("[white]3. Назад[/white]")

        choice = input("Выберите действие: ")
        print()
        if choice == "1":
            set_full_env()
        elif choice == "2":
            set_full_tokens()
        elif choice == "3":
            break
        else:
            console.print("[red]Неверный выбор[/red]")
    main_menu()


def setup_menu():
    while True:
        console.print(header("Установка окружения"))
        console.print("[green]1. Установить токены группы[/green]")
        console.print("[green]2. Установить токен пользователя[/green]")
        console.print("[green]3. Установить айди модераторов[/green]")
        console.print("[green]4. Установить айди админов[/green]")
        console.print("[green]5. Установить терминал[/green]")
        console.print("[white]6. Назад[/white]")

        choice = input("Выберите действие: ")
        print()
        if choice == "1":
            set_group_tokens()
        elif choice == "2":
            set_user_token()
        elif choice == "3":
            set_moderator_ids()
        elif choice == "4":
            set_admin_ids()
        elif choice == "5":
            set_terminal()
        elif choice == "6":
            break
        else:
            console.print("[red]Неверный выбор[/red]")


def reset_menu():
    while True:
        console.print(header("Сброс окружения"))
        console.print("[green]1. Сбросить токены[/green]")
        console.print("[green]2. Сбросить токен пользователя[/green]")
        console.print("[green]3. Сбросить айди модераторов[/green]")
        console.print("[green]4. Сбросить айди админов[/green]")
        console.print("[green]5. Сбросить терминал[/green]")
        console.print("[white]6. Назад[/white]")

        choice = input("Выберите действие: ")
        print()
        if choice == "1":
            reset_group_tokens()
        elif choice == "2":
            reset_user_token()
        elif choice == "3":
            reset_moderator_ids()
        elif choice == "4":
            reset_admins_ids()
        elif choice == "5":
            reset_terminal()
        else:
            console.print("[red]Неверный выбор[/red]")


def main_menu():
    while True:
        console.print(header("Менеджер окружения"))
        console.print("[green]1. Полная установка >[/green]")
        console.print("[green]2. Установка >[/green]")
        console.print("[green]3. Сброс >[/green]")
        console.print("[white]4. Выход[/white]")

        choice = input("Выберите действие: ")
        print()
        if choice == "1":
            full_setup_menu()
        elif choice == "2":
            setup_menu()
        elif choice == "3":
            reset_menu()
        elif choice == "4":
            console.print("[italic blue]Выход из менеджера окружения...[/italic blue]")
            exit(0)
        else:
            console.print("[red]Неверный выбор[/red]")


if __name__ == "__main__":
    main_menu()
