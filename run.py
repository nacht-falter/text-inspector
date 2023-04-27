import os
import re
import time

SEPARATOR = "------------------------------"
STORAGE = {}

class Text:
    """
    Creates an instance of a text. Retrieves text input from file or user input.

    Attributes:
    title: Title of the text instance provided by user
    text: Text contents provided by user

    Methods:
    get_text(): Display a menu to select an input method
    user_input(): Read text from command line interface
    file_input(): Read text from file
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
        input_method_menu = Menu("Please choose an input method for your text", False, False, self.user_input, self.file_input)
        return input_method_menu.display_menu()

    def user_input(self):
        """Read text from user input"""
        print("Please enter or paste your text. To save your input enter a new line and press Ctrl-D.\n")
        lines = []
        while True:
            try:
                """
                Read multiline input:
                https://stackoverflow.com/questions/30239092/how-to-get-multiline-input-from-the-user
                """
                while True:
                    try:
                        line = input()
                    except EOFError:
                        break
                    lines.append(line)
                if len(lines) == 0:
                    raise ValueError("No input received.")
                else:
                    return lines 
            except ValueError as e:
                print(f"Invalid data: {e}. Please try again.")

    def file_input(self):
        """Read text from file"""
        while True:
            try:
                file_name = str(input("Please enter the name of the file you want to check\n(File upload not possible in the online version. Type example1.txt or example2.txt for examples)\n"))
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
        self.return_value = None
    
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
                    self.return_value = self.menu_items[option - 1]()
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
        return self.return_value

def display_header():
    """Clear terminal and display a header"""
    os.system("clear")  # Source?
    print(SEPARATOR)
    print("Welcome to " + "Text Inspector!".upper())
    print(f"{SEPARATOR}\n")

def select_text():
    """Display a menu to create a new text or load an existing text"""
    select_text_menu = Menu("What would you like to do?", False, True, create_new_text, load_text)
    text = select_text_menu.display_menu()
    return text

def create_new_text():
    """Create a new text from command line input or file"""
    new_text = Text()
    return new_text

def load_text():
    """Load an existing text from storage"""
    print("Load existing text")

def spell_check():
    """Check for spelling errors in the selected text"""
    print("Spell check")
    print(current_text.text)
    time.sleep(3)

def suggest_synonyms():
    """Suggest synonyms for frequently used words"""
    print("synonyms")
    print(current_text.text)
    time.sleep(1)

def display_metrics():
    """Display metrics for the seleced text"""
    print("metrics")
    print(current_text.text)
    time.sleep(1)

current_text = select_text()
main_menu = Menu("What would you like to do?", True, False, spell_check, suggest_synonyms, display_metrics)
main_menu.display_menu()
