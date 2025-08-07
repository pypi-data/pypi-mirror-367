# **Word Game Solver**

A solver for word-based games.

Currently, only the **Word Finder** solver is implemented.  
It searches for all possible words of a specific length that can be formed using only the letters or letter combinations provided by the user.

---

## **Basic Algorithm Description**

**Summary:**  
An English words file is used to generate a database based on that file; anagram techniques are used to solve the problem.

**Detailed:**  
This is achieved thanks to a file with all the English words, which is read, cleaned, processed, and stored in an in-memory database. This database is a dict where the key is the word sorted alphabetically and its value is a list with the original word. If another word is an anagram, it would be stored under the same key but the original word would be added to the existing list, making each key unique and its value contain all possible anagrams.

User inputs are stored, cleaned, verified, processed, and stored again. In the case of the entered set of letters, it is sorted alphabetically, then all possible combinations of that set of letters with the specified length are generated. Then all those combinations are searched in the database, and the database returns all the words found. These are stored and shown to the user via the console, and a user history file is saved.

---

## **Features**

### Word Finder
- Enter the desired word length (e.g., `5`)
- Input a set of letters (e.g., `"nyogbsfo"`)
- Returns all valid English words (e.g., `bongo`, `bongs`, `boons`, etc.)
- Uses anagram-solving logic
- Based on a plain English word list (`words.txt`)

---

## **Usage**

If installed manually (by cloning from GitHub or downloading the project), it can be started from the project root with the following command:

**For Unix-like systems (Linux, macOS):**
```bash
python3 main.py
```

**For Windows systems (PowerShell or CMD):**
```
py main.py
```

**If installed as a package, you can run the following command on both Unix-like and Windows systems:**

```
wordfinder
```

A simple interactive menu will appear:
```
Options:
Select game:................0
View history:...............1
Delete history:.............2
Help:.......................3
About:......................4
Exit the CLI application:...5
Select an option:
```
Choosing the Select game option opens a submenu where you can select the desired game solver or exit.
Currently, only the Word Finder game is available.
Simply enter the length of the words to search for and a set of letters from which those words can be formed.
The CLI application will display on the console all valid matches from words.txt.
The history stores all word length and letter set inputs, along with the corresponding results.
This data is saved across sessions and can be deleted at any time via the menu.

---

## **Project Structure**

```
.
├── LICENSE
├── README.md
├── main.py
├── pyproject.toml
├── src
│   └── word_game_solver
│       ├── __about__.py
│       ├── __init__.py
│       ├── cli.py
│       ├── info
│       │   ├── LICENSE
│       │   ├── README.md
│       │   ├── about.txt
│       │   ├── help.md
│       │   ├── history.txt
│       │   └── log.txt
│       ├── utils.py
│       ├── word_files
│       │   └── english_words.txt
│       └── wordfinder.py
```

---

## **Example Output (CLI in Action)**

```
Word Game Solver
Welcome: user
Date: 2025-08-04 Time: 10:34:00

Options:
Select game:................0
View history:...............1
Delete history:.............2
Help:.......................3
About:......................4
Exit the CLI application:...5
Select an option: 0

Games:
Word Finder...1
Exit..........2
Select a game: 1

Word Finder
Enter the length of the word to guess: 5
Enter all available letters: nyogbsfo
Number of possible words: 6
Possible words: bongo bongs boons goofs goofy goons
```

---

## **License**
This project is licensed under the MIT License.

---

## **Notes**
You can replace words.txt with any other word list you prefer.
The program filters each line to remove special characters, digits, and whitespace, and converts all text to lowercase.
Only simple alphabetic characters (A–Z, a–z) are currently supported—no accented letters or special symbols.

This project is intended 100% for educational purposes.

It is fully compatible with Unix-like systems (GNU/Linux, macOS, etc.) and Windows.

---