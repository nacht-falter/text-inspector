import os
import re
import time

SEPARATOR = "------------------------------"

class Text:
    """
    Creates an instance of a text. Retrieves text input from file or user input.

    Attributes:
    ...

    Methods:
    ...
    """

    def __init__(self):
        self.title = self.get_title()
        self.text = self.get_text()

    def get_title(self):
        """Get instance title from user input"""
        while True:
            try:
                title = str(input("Please enter a title for your text\n"))
                if len(title) == 0:
                    raise ValueError("The title can't be empty. Please provide a valid title")
                elif not re.match("^[a-zA-Z0-9 _-]*$", title):  # Source?
                    raise ValueError("The title cannot contain any special characters or numbers")
                else:
                    return title
            except ValueError as e:
                print(f"Invalid data: {e}. Please try again.")

    def get_text(self):
        """Create a new menu to determine input method"""
        select_menu = Menu("Please choose an input method for your text", False, False, self.user_input, self.file_input)
        return select_menu.display_menu()

    def user_input(self):
        """Read text from user input"""
        while True:
            try:
                input_text = str(input("Please enter or paste your text here\n"))
                if len(input_text) == 0:
                    raise ValueError("No input received. Please provide some text")
                else:
                    return input_text
            except ValueError as e:
                print(f"Invalid data: {e}. Please try again.")

    def file_input(self):
        """Read text from file"""
        while True:
            try:
                file_name = str(input("Please enter the name of the file you want to check (type example1.txt or example2.txt for examples)\n"))
                f = open(f"{file_name}", "r")
                lines = f.read()
                f.close()
                return lines
            except FileNotFoundError:
                print("File not found. Please try again with a different file.\n")


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
                time.sleep(1)

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

new_text = Text()
print(new_text.text)
main_menu = Menu("What would you like to do?", True, False, spell_check, suggest_synonyms, display_metrics)
main_menu.display_menu()
