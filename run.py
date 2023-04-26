import os
import time

SEPARATOR = "-------------------------"

class Menu:
    """
    Creates a menuself.
    
    Arguments:
    - Menu title
    - At least one function

    Methods:
    - display_menu(): Clears the terminal and displays the menu
    """
    def __init__(self, title, *args):
        self.menu_title = title
        self.menu_items = args

    def display_menu(self):
        while True:
            os.system("clear")
            print(self.menu_title)
            print(SEPARATOR)
            i = 1
            for item in self.menu_items:
                """
                # Get function name and docstring:
                # https://stackoverflow.com/questions/251464/how-to-get-a-function-name-as-a-string
                # https://stackoverflow.com/questions/34277363/how-to-print-your-functions-documentation-python
                """
                menu_item = f"{item.__name__}: {item.__doc__}"
                print(f'{i}. {menu_item.capitalize().replace("_", " ")}')
                i += 1
            print(f"{i}. Exit")
            option = int(input("\nPlease choose an option: "))
            try:
                if option in range(1, len(self.menu_items) + 1):
                    self.menu_items[option - 1]()
                elif option == len(self.menu_items) + 1:
                    print("Thank you for using Text Inspector!")
                    exit()
                else:
                    raise ValueError
            except ValueError:
                print(f"Invalid choice. Please enter a number between 1 and {len(self.menu_items)}.\n")
                time.sleep(2)
