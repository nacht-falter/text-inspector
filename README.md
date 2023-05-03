# Text Inspector
## A quick and lightweight text analysis tool
[Text Inspector](https://github.com/nacht-falter/text-inspector) is a quick and easy to use command line tool for text analysis written in python using [NLTK](https://www.nltk.org) and [pyspellchecker](https://github.com/barrust/pyspellchecker). The tool provides features such as spell checking, synonym suggestion and text metrics and can process plain text files or read from user input.
Its aim is to provide a quick and lightweight command line alternative to more comprehensive tools for gaining a better understanding of a text by focussing on essential features.
[Text Inspector](https://github.com/nacht-falter/text-inspector) includes an import/export feature, which allows for storing and recovering texts from previous sessions.
So far only English texts are supported.

## Features
### Existing features
#### Import texts from storage
- On starting the application you can decide if you want to import texts from the database. If you have previously used [Text Inspector](https://github.com/nacht-falter/text-inspector) and exported your texts, you can enter your recovery key to restore your texts. The texts will then be available from the [text selection menu](#text-selection).
- For demonstration purposes you can enter "examples" in the recovery key input field, which will import some example texts from the database.

#### Text selection
- From the text selection menu you can select a text, either by loading it from storage or by creating a new text. The option to load a text will only be available if you have already created a new text item or if you have imported texts from the database.
- When you decide to load an existing text, you can preview the available texts before selecting one. You can also delete texts you don't need anymore from this menu.

#### Text creation
- When you create a new text item, you will be asked to provide a title for the text. Next, you can choose to enter the text from the command line or to provide a text file.
- If you choose to enter text from the command line, you can paste the text or enter it manually. To save your input, enter "Done!" on a new line and press Enter. (Alternatively you can try pressing "Ctrl-D" (or "Ctrl-Z" on Windows) on a new line.)
- Providing a text file will only work, if you are running [Text Inspector](https://github.com/nacht-falter/text-inspector) locally on your machine. If you are using the [version deployed to Heroku](https://text-inspector.herokuapp.com/), you can read from example files uploaded to the server to test the feature.

#### Text processing
Once you have created or selected a text you can choose from four options:
- **Spell check**: This will check your text for spelling errors and display suggestions for each mistake found. You can decide to accept a correction, provide a custom suggestion or skip to the next mistake.
- **Suggest synonyms**: This will check the text for repeatedly used words and suggest synonyms for each word. This feature is meant to provide insight into frequently used words in the text and does not provide the option to replace the original words with the suggested synonyms (may be added in the future). You will have to do that yourself using your favourite text editor.
- **Text metrics**: This will display metrics for the selected text:
	- Total word count
	- Unique word count
	- Sentence count
	- Longest/shortest sentence
	- Average words per sentence
	- Frequently used words (lemmatized and very common words not included)
- **Save text**: This will save changes made to the text and return to the [text selection menu](#text-selection).

#### Exporting texts
When you exit the application from the text selection menu, you can decide, if you want to store your text items in the database. If you choose to do that, you will be provided with a recovery key, which you can use to restore your saved texts on your next visit.
⚠ The current version of [Text Inspector](https://github.com/nacht-falter/text-inspector) uses [Google Sheets](https://www.google.com/sheets/about/) to store the text items and your texts will be stored in plain text. Please make sure your exported texts do not contain any sensitive information! ⚠️

### Future Features
- Add support for other languages than english.
- Read input from URL: Let the user provide a URL to a text file as an alternative to command line input or reading a local file.
- User dictionary: Let the user add words to a custom dictionary serving as a white-list for the spell check feature.
- Let user accept or reject synonym suggestions.
- Add readability score to text metrics

## Data model
The application is based on a class as data model. For each text item created by the user the application creates instances of the `Text` class, which stores the title and the text contents  as instance attributes. Furthermore, the class provides the central functionality of the application by supplying methods for spell checking, synonym suggestion and text metrics. 

Another class `Menu` provides functionality for navigation within the application by displaying the main menus of the application. The `Menu` class takes functions or methods as input and lets the user decide which functionality should be executed. 
