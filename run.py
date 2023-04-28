from enum import unique
import os
import re
import time
from spellchecker import SpellChecker

SEPARATOR = "------------------------------"
STORAGE = {}


class Text:
    """
    Creates an instance of a text. Retrieves text input from file or user input.

    Attributes:
    - title: Title of the text instance provided by user
    - text: Text contents provided by user

    Methods:
    - get_text(): Display a menu to select an input method
    - user_input(): Read text from command line interface
    - file_input(): Read text from file
    - spell_check(): Run a spell check on text
    - suggest_synonyms(): Suggest synonyms for repeated words
    - display_suggestions(): Display suggestions and let user confirm, skip or enter custom word
    - display_text(): Prints the revised text to the console
    - display_metrics(): Display text metrics
    """

    def __init__(self):
        self.title = self.get_title()
        self.text = self.get_text()
        # Split text into list with words and punctuation: https://stackoverflow.com/questions/367155/splitting-a-string-into-words-and-punctuation
        self.split_text = re.findall(r"[\w'-]+|[ .,!?@#$%&*;:<>=()[\]{}\n]", self.text)

    def get_title(self):
        """Get instance title from user input"""
        while True:
            try:
                title = str(input("Please enter a title for your text\n"))

                if len(title) == 0:
                    raise ValueError("The title can't be empty. Please provide a valid title")
                elif not re.match(
                    "^[a-zA-Z0-9 _-]*$", title
                ):  # https://stackoverflow.com/questions/19970532/how-to-check-a-string-for-a-special-character
                    raise ValueError("The title cannot contain any special characters or numbers")
                else:
                    return title

            except ValueError as e:
                print(f"Invalid data: {e}. Please try again.")

    def get_text(self):
        """Create a new menu to determine input method"""
        input_method_menu = Menu(
            "Please choose an input method for your text", False, False, self.user_input, self.file_input
        )

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
                    return "\n".join(lines)

            except ValueError as e:
                print(f"Invalid data: {e}. Please try again.")

    def file_input(self):
        """Read text from file"""
        while True:
            try:
                file_name = str(
                    input(
                        "Please enter the name of the file you want to check\nType example1.txt or example2.txt for examples)\n"
                    )
                )

                f = open(f"{file_name}", "r")
                lines = f.read()
                f.close()

                return "\n".join(lines)

            except FileNotFoundError:
                print("File not found. Please try again with a different file.\n")

    def spell_check(self):
        """Check for spelling errors in the selected text"""
        # pyspellchecker documentation: https://pyspellchecker.readthedocs.io/en/latest/
        spell = SpellChecker(language="en")
        misspelled = spell.unknown(self.split_text)
        time.sleep(2)
        corrected_text = []
        i = 0

        for word in self.split_text:
            # match alphanumeric words including hyphens and underscores: https://stackoverflow.com/questions/34916716/regular-expression-to-match-alphanumeric-hyphen-underscore-and-space-string
            if re.match(r"^[a-zA-Z]([\w-]*[a-zA-Z])?$", word) and word in misspelled:
                suggestions = spell.candidates(word)
                # Call display_suggestions method and pass it the current word and its suggestions
                corrected_text.append(self.display_suggestions(word, suggestions))
            else:
                corrected_text.append(word)

            i += 1

        self.text = "".join(corrected_text)

        display_header()
        self.display_text()

    def suggest_synonyms(self):
        """Check for repeating words and suggest synonyms"""
        print("Suggest synonyms")
        input("Press Enter to return to Menu")

    def display_suggestions(self, word, suggestions):
        """Display suggestions one by one and let user accept, edit or skip to next"""
        os.system("clear")
        display_header()
        print(f"Current text: {self.title}")
        print(f"Spelling error found: {word}")
        print("\nPlease choose one of the following replacements:\n")
        option_count = 1

        if suggestions is not None:
            for suggestion in suggestions:
                print(f"{option_count}. Replace with: {suggestion}")
                option_count += 1
                if option_count > 5:
                    break
        else:
            print("No suggestions found")

        print(f"\nPress 'e' to enter custom replacement")
        print(f"Press 's' to skip")

        while True:
            option = input("\nPlease choose an option: ")

            try:
                if option.isdigit() and int(option) < option_count:
                    return list(suggestions)[int(option) - 1]
                elif option == "e":
                    return input("Please enter your replacement: ")
                elif option == "s":
                    return word
                else:
                    raise ValueError

            except ValueError:
                print(
                    f"Invalid choice. Possible values are numbers between 1 and {option_count} and the letters e and s.\n"
                )
                time.sleep(2)

    def display_text(self):
        """Print the revised text to the console"""
        print("Here is your revised text:\n")
        print(f"{SEPARATOR}\n")
        print(self.text)
        print(f"\n{SEPARATOR}")
        input("\nPress Enter to return to menu.")

    def display_metrics(self):
        """Display metrics for the seleced text"""
        display_header()
        print(f"Selected Text: {self.title}\n")
        print("Text Metrics:")

        # Total word count and unique words:
        total_words = 0
        unique_words = {}
        for word in self.split_text:
            if re.match(r"^[a-za-z]([\w-]*[a-za-z])?$", word):
                total_words += 1
                if word in unique_words:
                    unique_words[word] += 1
                else:
                    unique_words[word] = 1

        # Total sentence count: https://stackoverflow.com/questions/15228054/how-to-count-the-amount-of-sentences-in-a-paragraph-in-python
        all_sentences = re.split(r"[.!?]+", self.text)
        total_sentences = len(all_sentences)

        # Longest/shortest sentences:
        sentence_lengths = set()
        for sentence in all_sentences:
            words = re.findall(r"\w+", sentence)
            if len(words) > 0:
                sentence_lengths.add(len(words))

        # Average words per sentence:
        words_per_sentence = round(total_words / total_sentences)

        print(f"Words: {total_words}")
        print(f"Sentences: {total_sentences}")
        print(f"Longest sentence: {max(sentence_lengths)} words")
        print(f"Shortest sentence: {min(sentence_lengths)} words")
        print(f"Average words per sentence: {words_per_sentence}")

        input("\nPress Enter to return to menu.")


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
        """Clear the console and display the menu"""
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
                option_count += 1

            option = input("\nPlease choose an option: ")

            try:
                option = int(option)

                if option <= len(self.menu_items):
                    # Call the function passed to the Menu class according to user selection:
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
    os.system("clear")  # https://www.pythonpip.com/python-tutorials/how-to-clear-console-in-python/
    print(SEPARATOR)
    print("Welcome to " + "Text Inspector!".upper())
    print(f"{SEPARATOR}\n")


def select_text():
    """Create a new text or load an existing one"""
    select_text_menu = Menu("What would you like to do?", False, True, create_new_text, load_text)
    text = select_text_menu.display_menu()

    return text


def create_new_text():
    """Create a new text from command line input or from file"""
    new_text = Text()

    return new_text


def load_text():
    """Load an existing text from storage"""
    print("Load existing text")


def main():
    """Run the program"""
    current_text = select_text()

    main_menu = Menu(
        f"Selected text: {current_text.title}\n\nWhat would you like to do?",
        True,
        False,
        current_text.spell_check,
        current_text.suggest_synonyms,
        current_text.display_metrics,
        select_text,
    )

    main_menu.display_menu()


main()
