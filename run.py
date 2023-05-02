import os, time, re, random, string, gspread
from spellchecker import SpellChecker
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
from nltk.corpus import wordnet
from nltk.corpus import stopwords
from termcolor import colored
from google.oauth2.service_account import Credentials

# Google Drive API integration:
SCOPE = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive.file",
    "https://www.googleapis.com/auth/drive",
]
CREDS = Credentials.from_service_account_file("creds.json")
SCOPED_CREDS = CREDS.with_scopes(SCOPE)
GSPREAD_CLIENT = gspread.authorize(SCOPED_CREDS)
SHEET = GSPREAD_CLIENT.open("text-inspector-storage")

SEPARATOR = "------------------------------"
storage = {}


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

    def __init__(self, new_text):
        if new_text:
            self.title = self.get_title()
            self.text = self.get_text()

    def get_title(self):
        """Get instance title from user input"""
        while True:
            try:
                title = str(input("Please enter a title for your text:\n"))

                if len(title) == 0:
                    # Colorize terminal output: https://stackoverflow.com/questions/37340049/how-do-i-print-colored-output-to-the-terminal-in-python
                    raise ValueError(colored("The title can't be empty. Please provide a valid title", "red"))
                elif not re.match(
                    "^[a-zA-Z0-9 _-]*$", title
                ):  # https://stackoverflow.com/questions/19970532/how-to-check-a-string-for-a-special-character
                    raise ValueError(colored("The title cannot contain any special characters or numbers", "red"))
                elif title in storage:
                    print(colored("A text with this title already exists. Please choose a different title.", "red"))
                else:
                    return title

            except ValueError as e:
                print(colored(f"Invalid data: {e}. Please try again.", "red"))

    def get_text(self):
        """Create a new menu to determine input method"""
        while True:
            input_method_menu = Menu(
                "Please choose an input method for your text.", False, False, self.user_input, self.file_input
            )
            text = input_method_menu.display_menu()

            if text is not None:
                return text

    def user_input(self):
        """Read text from user input"""
        print("Please enter or paste your text.")
        print("To save your input enter 'Done!' on a new line and press Enter.")
        print("To select a different input method enter 'Go back!' on a new line and press Enter.\n")

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
                        if line == "Done!":
                            break
                        elif line == "Go back!":
                            return None
                    except EOFError:
                        break
                    lines.append(line)

                if len(lines) == 0:
                    raise ValueError(colored("No input received.", "red"))
                else:
                    return "\n".join(lines)

            except ValueError as e:
                print(colored(f"Invalid data: {e}. Please try again.", "red"))

    def file_input(self):
        """Read text from file"""
        while True:
            print("Please enter the name of your file.")
            print("To select a different input method press 'b' and hit Enter.")
            try:
                user_input = input("Enter 'example1.txt' or 'example2.md' for examples).\n")
                if user_input == "b":
                    return None
                else:
                    f = open(f"{user_input}", "r")
                    lines = f.read()
                    f.close()
                    print("\nSuccess! Here is the text from your file:\n")
                    print(lines)
                    input("Press Enter to continue.")
                    return lines

            except FileNotFoundError:
                print(colored("File not found. Please try again with a different file.\n", "red"))

    def spell_check(self):
        """Check for spelling errors in the selected text"""
        # pyspellchecker documentation: https://pyspellchecker.readthedocs.io/en/latest/
        spell = SpellChecker(language="en")
        # Split text into list with words and punctuation: https://stackoverflow.com/questions/367155/splitting-a-string-into-words-and-punctuation
        tokenized_text = re.findall(r"[\w'’-]+|[ .,!?@#$%&*;:<>=()[\]{}–—\n]", self.text)
        misspelled = {word for word in spell.unknown(tokenized_text) if word != "\n"}

        corrected_text = []

        def display_spelling_suggestions(word, suggestions, total, index):
            """Display suggestions one by one and let user accept, edit or skip to next"""
            display_header()
            print(SEPARATOR)
            print("Spell check")
            print(SEPARATOR)
            print(f"Current text: {colored(self.title, 'yellow')}")

            print(f"\n{total} possible spelling errors found.")
            print(f"\nPossible spelling error: {colored(word, 'red')}.")
            print(f"(Error {index} of {total})")
            print("\nPlease choose one of the following suggestions:\n")

            option_count = 1

            if suggestions is not None:
                for suggestion in suggestions:
                    print(f"{option_count}. Replace with: {suggestion}")
                    option_count += 1
                    if option_count > 5:
                        break
            else:
                print("No suggestions found")

            print("\nPress 'e' to enter custom replacement")
            print("Press 's' to skip")

            while True:
                option = input("\nPlease choose an option:\n")

                try:
                    if option.isdigit() and int(option) < option_count:
                        return list(suggestions)[int(option) - 1]
                    elif option == "e":
                        return input("Please enter your replacement:\n")
                    elif option == "s":
                        return word
                    else:
                        raise ValueError

                except ValueError:
                    print(
                        colored(
                            f"Invalid choice. Possible values are numbers between 1 and {option_count - 1} and the letters e and s.",
                            "red",
                        )
                    )
                    time.sleep(2)

        index = 1
        if len(misspelled) != 0:
            for word in tokenized_text:
                # match alphanumeric words including hyphens and underscores: https://stackoverflow.com/questions/34916716/regular-expression-to-match-alphanumeric-hyphen-underscore-and-space-string
                if re.match(r"^[a-zA-Z]([\w-]*[a-zA-Z])?$", word) and word in misspelled:
                    suggestions = spell.candidates(word)
                    # Call display_suggestions method and pass it the current word and its suggestions
                    corrected_text.append(display_spelling_suggestions(word, suggestions, len(misspelled), index))
                    index += 1
                else:
                    corrected_text.append(word)

            self.text = "".join(corrected_text)

            display_header()
            self.display_text()
        else:
            self.no_suggestions("Spell check")

    def suggest_synonyms(self):
        """Check for repeating words and suggest synonyms"""
        tokenized_text = re.findall(r"[\w'-]+|[ .,!?@#$%&*;:<>=()[\]{}\n]", self.text)
        # Get most frequent words from count_words() and convert it to dictionary
        most_used_words = dict(self.count_words()[2])

        def display_synonym_suggestions(word, count, suggestions, total, index):
            """Display suggestions one by one and let user accept, edit or skip to next"""
            display_header()
            print(SEPARATOR)
            print("Synonym Suggestions")
            print(SEPARATOR)
            print(f"Current text: {colored(self.title, 'yellow')}\n")
            print(f"{total} frequently used words found.\n")
            print(
                f"The word '{colored(word, 'red')}' occurs {count} times in the text. Here are a few synonyms, which you might consider using instead:"
            )
            print(f"(Suggestion {index} of {total})\n")

            counter = 0
            if suggestions:
                for suggestion in suggestions:
                    if counter < 15:
                        print(suggestion)
                    counter += 1
            else:
                print("No suggestions found")

            input("\nPress Enter to go to next suggestion")

        def get_synonyms(word):
            """
            Get synonyms for a word from wordnet:
            https://towardsdatascience.com/synonyms-and-antonyms-in-python-a865a5e14ce8
            """
            synonyms = set()
            # Filter out common words by using stop words: https://pythonspot.com/nltk-stop-words/
            for synonym in wordnet.synsets(word):
                for lemma in synonym.lemmas():
                    lemma_name = lemma.name()
                    if lemma_name != word and lemma_name:
                        synonyms.add(lemma.name())
            return synonyms

        repeating_words = set(word for word in tokenized_text if word in most_used_words and most_used_words[word] >= 4)
        index = 1
        suggested_words = []
        if len(repeating_words) != 0:
            for word in tokenized_text:
                if word in repeating_words and word not in suggested_words:
                    synonyms = get_synonyms(word)
                    suggested_words.append(word)
                    # Call display_suggestions method and pass it the current word, the word count and the synonyms as well as the sentence
                    display_synonym_suggestions(word, most_used_words[word], synonyms, len(repeating_words), index)
                    index += 1

            display_header()
            self.display_text()
        else:
            self.no_suggestions("Synonyms")

    def no_suggestions(self, method):
        """Display a message when there are no suggestions"""
        display_header()
        print(SEPARATOR)
        print(method)
        print(f"{SEPARATOR}\n")
        if method == "Spell check":
            print("No spelling errors found")
        else:
            print("No suggestions found.")
        input("\nPress Enter to return to menu.\n")

    def display_text(self):
        """Print the revised text to the console"""
        print("Here is your revised text:\n")
        print(f"{SEPARATOR}\n")
        print(self.text)
        print(f"\n{SEPARATOR}")
        input("\nPress Enter to return to menu.\n")

    def display_metrics(self):
        """Display metrics for the seleced text"""
        display_header()

        total_words, unique_words, most_used_words = self.count_words()
        total_sentences, sentence_lengths = self.count_sentences()

        print(f"Selected Text: {self.title}\n")
        print("Text Metrics:\n")
        print(f"Words: {total_words}")
        print(f"Unique words: {len(unique_words)}")
        print(f"Sentences: {total_sentences}")
        print(f"Longest sentence: {max(sentence_lengths)} words")
        print(f"Shortest sentence: {min(sentence_lengths)} words")
        print(f"Average words per sentence: {round(total_words / total_sentences)}")

        print(f"\nMost used words (lemmatized, not including very common words):")

        counter = 0
        for lemma, occurences in most_used_words:
            if counter < 15:
                print(f"{lemma}: {occurences}")
            counter += 1

        input("\nPress Enter to return to menu.\n")

    def count_words(self):
        """Get total word count, unique word count, and word frequency"""
        total_words = 0

        # Tokenize text with nltk.tokenize. NLTK documentation: https://www.nltk.org/api/nltk.tokenize.html?highlight=tokenize#module-nltk.tokenize
        tokenized_text = word_tokenize(self.text)
        stop_words = set(stopwords.words("english"))
        lemmas = {}
        unique_words = set()

        for word in tokenized_text:
            if re.match(r"^[a-za-z]([\w-]*[a-za-z])?$", word):
                total_words += 1
                unique_words.add(word)
                # Retrieve lemmas from WordNetLemmatizer: https://www.nltk.org/api/nltk.stem.wordnet.html?highlight=lemmatizer#nltk.stem.wordnet.WordNetLemmatizer
                lemmatizer = WordNetLemmatizer()
                lemma = lemmatizer.lemmatize(word)

                if word not in stop_words and len(word) > 3:
                    if lemma in lemmas:
                        lemmas[lemma] += 1
                    else:
                        lemmas[lemma] = 1

        # Sort the dictionary: https://realpython.com/sort-python-dictionary/#getting-keys-values-or-both-from-a-dictionary
        most_used_words = sorted(lemmas.items(), key=lambda item: item[1], reverse=True)

        return total_words, unique_words, most_used_words

    def count_sentences(self):
        """Get total sentence count, longest/shortest sentence and average words per sentence"""
        # Total sentence count: https://stackoverflow.com/questions/15228054/how-to-count-the-amount-of-sentences-in-a-paragraph-in-python
        all_sentences = re.split(r"[.!?]+", self.text)
        total_sentences = len(all_sentences)

        # Longest/shortest sentences:
        sentence_lengths = set()
        for sentence in all_sentences:
            words = re.findall(r"\w+", sentence)
            if len(words) > 0:
                sentence_lengths.add(len(words))

        return total_sentences, sentence_lengths

    def save_text(self):
        """Save text to storage and go back to text selection"""
        storage[self.title] = self

        return "break"


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

            option = input("\nPlease choose an option:\n")

            try:
                option = int(option)

                if option <= len(self.menu_items):
                    # Call the function passed to the Menu class according to user selection:
                    self.return_value = self.menu_items[option - 1]()

                    if self.return_value == "break":
                        break

                    if self.repeat == False:
                        break

                elif self.exit_option == True and option == option_count:
                    exit_program()
                else:
                    raise ValueError

            except ValueError:
                print(colored(f"Invalid choice. Please enter a number between 1 and {option_count}.\n", "red"))
                time.sleep(2)

        return self.return_value


def display_header():
    """Clear terminal and display a header"""
    os.system("clear")  # https://www.pythonpip.com/python-tutorials/how-to-clear-console-in-python/
    print(SEPARATOR)
    print("Welcome to " + "Text Inspector!".upper())
    print(f"{SEPARATOR}\n")


def select_text():
    """Create a new text or load an existing one"""
    if storage:
        select_text_menu = Menu("What would you like to do?", False, True, create_new_text, load_text)
    else:
        select_text_menu = Menu("What would you like to do?", False, True, create_new_text)

    text = select_text_menu.display_menu()

    return text


def create_new_text():
    """Create a new text from command line input or from file"""
    new_text = Text(True)

    return new_text


def load_text():
    """Load an existing text from storage"""
    while True:
        display_header()
        print("Available texts:\n")

        counter = 1

        for title in storage:
            print(f"{counter}: {title}")
            counter += 1
        print("\nPress 'd' to display a text.")
        print("Press 's' to select a text.")

        option = input("\nPlease select an option:\n")

        try:
            if option == "d":
                index = int(input("Please choose a text:\n"))

                if index < counter:
                    print(f"\nTitle: {list(storage.keys())[index - 1]}")
                    print(list(storage.values())[index - 1].text)
                    input("\nPress Enter to go back\n")
                else:
                    raise ValueError

            elif option == "s":
                index = int(input("Please choose a text:\n"))
                if index < counter:
                    return list(storage.values())[index - 1]
                else:
                    raise ValueError
            else:
                raise ValueError

        except ValueError:
            print(
                colored(
                    f"Invalid choice. Please enter 'd' or 's' and then a number between 1 and {counter - 1}.\n", "red"
                )
            )
            time.sleep(2)


def import_texts():
    """Import stored texts with recovery key"""
    while True:
        print("Would you like to import texts from a previous session?")
        option = input("Please enter 'yes' or 'no'.\n")
        try:
            if option.lower() == "yes":
                while True:
                    try:
                        user_input = input("Please enter your recovery key or enter 'b' to go back:\n")
                        if user_input == "b":
                            break
                        else:
                            worksheet = SHEET.worksheet(recovery_key)
                            if worksheet:
                                print("\nImporting texts ...")
                                texts = worksheet.get_all_values()
                                for text in texts:
                                    new_text = Text(False)
                                    new_text.title = text[0]
                                    new_text.text = text[1]
                                    storage[new_text.title] = new_text
                                    # Make recovery_key accessible on global scope in order to reuse it for the next export:
                                    global user_recovery_key
                                    user_recovery_key = recovery_key
                                print("\nYour texts have been successfully recovered.")
                                break
                            else:
                                raise Exception

                    except Exception:
                        print(colored("Invalid recovery key. Please try again with a valid key.", "red"))
            elif option.lower() == "no":
                print("Ok! Continuing without import.")
                break
            else:
                raise ValueError

        except ValueError:
            print(colored("Invalid option. Please answer 'yes|Yes' or 'no|No'.", "red"))


def exit_program():
    """Function to run on exit"""
    display_header()
    if storage:
        print("Before you go ...")
        print("\nWould you like to save your texts to the database?")
        print("If so, please make sure your texts don't contain any sensitive information.\n")

        while True:
            option = input("Please enter 'yes' or 'no'.\n")

            try:
                if option.lower() == "yes":
                    export_texts()
                    break
                elif option.lower() == "no":
                    print("Ok! Your texts have been deleted.")
                    break
                else:
                    raise ValueError

            except ValueError:
                print(colored("Invalid option. Please answer 'yes|Yes' or 'no|No'.", "red"))

    print("\nExiting. Thank you for using Text Inspector!")
    exit()


def export_texts():
    """Export texts to Google spreadsheet"""
    print(f"\nUpdating text storage ...")

    if user_recovery_key:
        recovery_key = user_recovery_key
        # Delete the old worksheet: https://docs.gspread.org/en/latest/user-guide.html#deleting-a-worksheet
        worksheet = SHEET.worksheet(recovery_key)
        SHEET.del_worksheet(worksheet)
    else:
        # Generate random string: https://stackoverflow.com/questions/2030053/how-to-generate-random-strings-in-python
        letters = string.ascii_letters
        recovery_key = "".join(random.choice(letters) for i in range(10))

    # Create new worksheet in spreadsheet: https://docs.gspread.org/en/latest/user-guide.html#creating-a-worksheet
    worksheet = SHEET.add_worksheet(title=recovery_key, rows=len(storage), cols=2)

    for title in storage:
        row = [storage[title].title, storage[title].text]
        worksheet.append_row(row)

    print("\nYour texts have been successfully stored in the database.")

    if user_recovery_key:
        print(f"You can use the same recovery key as before to restore them: {colored(recovery_key, 'green')}")
    else:
        print(f"You can import them with the following recovery key: {colored(recovery_key, 'green')}")

    print("Please copy the key and save it.")
    input("\nPress Enter to exit\n")


def main():
    """Run the program"""
    display_header()
    import_texts()

    while True:
        current_text = select_text()

        main_menu = Menu(
            f"Selected text: {current_text.title}\n\nWhat would you like to do?",
            True,
            False,
            current_text.spell_check,
            current_text.suggest_synonyms,
            current_text.display_metrics,
            current_text.save_text,
        )

        main_menu.display_menu()


main()
