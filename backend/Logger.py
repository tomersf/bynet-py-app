from colorama import Fore, Style


class Logger():

    @staticmethod
    def ERROR(message: str):
        print(Style.BRIGHT + Fore.RED + message + Style.RESET_ALL)
