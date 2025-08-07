## **Basic Help:**

### Word Finder
- Enter the desired word length (e.g., `5`)
- Provide a set of letters (e.g., `"nyogbsfo"`)
- Generate all valid English words (e.g., `bongo`, `bongs`, `boons`, etc.)

---

## **Detailed Help:**

### **This is the main menu:**
```
Word Game Solver
Options:
Select game:................0
View history:...............1
Delete history:.............2
Help:.......................3
About:......................4
Exit the CLI application:...5
Select an option:
```
**Select game:**
When this menu is selected, another menu appears for selecting games or exiting to the main menu.

**View history:**
View the user's current history.

**Delete history:**
Delete the user's current history.

**Help:**
User help, what each menu is for, and how the application works.

**About:**
Information about the project.

**Exit the CLI application:**
Quit the application completely.

### **This is the Select game menu:**
```
Word Game Solver
Games:
Word Finder...1
Exit................2
Select a Game:
```
**Word Finder:**
Once this option is selected, the menu for that specific game will appear.

**Exit:**
Exit the game selection and return to the main menu.

### **This is the game menu, Word Finder:**
```
Word Finder
Enter the length of the word to guess: 5
Enter all available letters: nyogbsfo
Number of possible words: 6
Possible words: bongo bongs boons goofs goofy goons
```
Here in this example, 5 was selected for the word length, and nyogbsfo as the letter set, generating 2 outputs, 6 as the number of words, and the words found.

---

## **Visual example of CLI application in operation:**

```
Word Game Solver
Welcome: user
Date: 2025-08-04 Hours: 10:34:00

Word Game Solver
Options:
Select game:................0
View history:...............1
Delete history:..........2
Help:....................3
About:....................4
Exit the CLI application:...5
Select an option: 0

Word Game Solver
Games:
Word Finder...1
Exit..............2
Select a Game: 1

Word Finder
Enter the length of the word to guess: 5
Enter all available letters: nyogbsfo
Number of possible words: 6
Possible words: bongo bongs boons goofs goofy goons

Word Game Solver
Games:
words Finder...1
Exit..............2
Select a Game:
```