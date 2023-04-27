import os
import re
import time

SEPARATOR = "------------------------------"

class Menu:
    """
    Creates a menu which generates menu options from passed functions.
    
    Arguments:
    - Menu title (str)
    - A repeat flag (bool)
    - An exit flag (bool) 
    - At least one function

    Methods:
    - display_menu(): Clears the terminal and displays the menu
    """
    def __init__(self, title, repeat, exit_option, *args):
        self.menu_title = title
        self.repeat = repeat 
        self.exit_option = exit_option
        self.menu_items = args
    
    def display_menu(self):
        while True:
            display_header()
            print(f"{self.menu_title}\n")
            i = 1
            option_count = len(self.menu_items)
            for item in self.menu_items:
                """
                # Get function name and docstring:
                # https://stackoverflow.com/questions/251464/how-to-get-a-function-name-as-a-string
                # https://stackoverflow.com/questions/34277363/how-to-print-your-functions-documentation-python
                """
                menu_item = f'{item.__name__.capitalize().replace("_", " ")}: {item.__doc__}'
                print(f"{i}. {menu_item}")
                i += 1

            if self.exit_option == True:
                print(f"{i}. Exit program")
                option_count +=1

            option = input("\nPlease choose an option: ")

            try:
                option = int(option)

                if option <= len(self.menu_items):
                    self.menu_items[option - 1]()
                    if self.repeat == False:
                        break
                elif self.exit_option == True and option == option_count:
                    print("Exiting. Thank you for using Text Inspector!")
                    exit()
                else:
                    raise ValueError

            except ValueError:
                print(f"Invalid choice. Please enter a number between 1 and {option_count}.\n")
                time.sleep(2)

def display_header():
    """Clear terminal and display a header"""
    os.system("clear")  # Source?
    print(SEPARATOR)
    print("Welcome to " + "Text Inspector!".upper())
    print(f"{SEPARATOR}\n")

def spell_check():
    """Check for spelling errors in the selected text"""
    print("Spell check")
    time.sleep(1)

def suggest_synonyms():
    """Suggest synonyms for frequently used words"""
    print("synonyms")
    time.sleep(1)

def display_metrics():
    """Display metrics for the seleced text"""
    print("metrics")
    time.sleep(1)

main_menu = Menu("What would you like to do?", True, True, spell_check, suggest_synonyms, display_metrics)
main_menu.display_menu()
