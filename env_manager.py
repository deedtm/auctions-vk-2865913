import os
import dotenv
from rich.console import Console
from rich.table import Table

if not os.path.exists(".env"):
    with open('.env', 'w') as f:
        f.write('')
console = Console()

header = lambda s: "[bold magenta]" + f"[ {s} ]".center(50, "=") + "[/bold magenta]"
mini_header = lambda s: "[bold magenta]" + f"[ {s} ]" + "[/bold magenta]"
success = lambda s: "[yellow]" + s + "[/yellow]"
info = lambda s: "[italic blue]" + s + "[/italic blue]"


def set_bot_token():
    print()
    console.print(header("Установка токена бота"))
    console.print(info("Токен должен иметь доступ к сообщениям сообщества"))
    bot_token = input("Введите токен: ")
    dotenv.set_key(".env", "VK_TOKEN", bot_token, quote_mode="never")
    console.print(success("Токен бота успешно установлен!"))


def set_auction_tokens():
    print()
    console.print(header("Установка токенов для аукционов"))
    console.print(info("Все токены должны иметь доступ к стене сообщества"))
    console.print(info("Для окончания установки нажмите Enter без ввода чего-либо"))
    i = 1
    auction_token = input(f"Введите токен {i} для аукционов: ")
    tokens = [auction_token]
    while auction_token:
        i += 1
        auction_token = input(
            f"Введите токен {i} для аукционов (или нажмите Enter для завершения): "
        )
        if auction_token:
            tokens.append(auction_token)
        else:
            break


    dotenv.set_key(".env", "PUBLISHER_TOKENS", " ".join(tokens), quote_mode="never")
    console.print(success("Токены для аукционов успешно установлены!"))


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
    console.print(info("Введите айди модераторов через пробел"))
    moderator_ids = input("Введите айди модераторов: ")
    dotenv.set_key(".env", "MODERATORS_IDS", moderator_ids, quote_mode="never")
    console.print(success("Айди модераторов успешно установлены!"))


def set_full_tokens():
    print()
    console.print(header("Полная установка токенов"))
    set_bot_token()
    set_auction_tokens()
    set_user_token()
    console.print(success("Полная установка токенов завершена!"))
    main_menu()


def set_full_env():
    print()
    console.print(header("Полная установка окружения"))
    set_bot_token()
    set_auction_tokens()
    set_moderator_ids()
    console.print(success("Полная установка окружения завершена!"))
    main_menu()


def reset_bot_token():
    print()
    console.print(header("Сброс токена бота"))
    dotenv.unset_key(".env", "VK_TOKEN")
    console.print(success("Токен бота успешно сброшен!"))


def reset_auction_tokens():
    print()
    console.print(header("Сброс токенов для аукционов"))
    dotenv.unset_key(".env", "PUBLISHER_TOKENS")
    dotenv.unset_key(".env", "PUBLISHER_WATERFALLS")
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


def reset_full_env():
    print()
    console.print(header("Полный сброс окружения"))
    reset_bot_token()
    reset_auction_tokens()
    reset_moderator_ids()
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
        console.print("[green]1. Установить токен бота[/green]")
        console.print("[green]2. Установить токены для обслуживания аукционов[/green]")
        console.print("[green]3. Установить токен пользователя[/green]")
        console.print("[green]4. Установить айди модераторов[/green]")
        console.print("[white]5. Назад[/white]")

        choice = input("Выберите действие: ")
        print()
        if choice == "1":
            set_bot_token()
        elif choice == "2":
            set_auction_tokens()
        elif choice == "3":
            set_user_token()
        elif choice == "4":
            set_moderator_ids()
        elif choice == "5":
            break
        else:
            console.print("[red]Неверный выбор[/red]")


def reset_menu():
    while True:
        console.print(header("Сброс окружения"))
        console.print("[green]1. Сбросить токен бота[/green]")
        console.print("[green]2. Сбросить токены для обслуживания аукционов[/green]")
        console.print("[green]3. Сбросить токен пользователя[/green]")
        console.print("[green]4. Сбросить айди модераторов[/green]")
        console.print("[white]5. Назад[/white]")

        choice = input("Выберите действие: ")
        print()
        if choice == "1":
            reset_bot_token()
        elif choice == "2":
            reset_auction_tokens()
        elif choice == "3":
            reset_user_token()
        elif choice == "4":
            reset_moderator_ids()
        elif choice == "5":
            break
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
