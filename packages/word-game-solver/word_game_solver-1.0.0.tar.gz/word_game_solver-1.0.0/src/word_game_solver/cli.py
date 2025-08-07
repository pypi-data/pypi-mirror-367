import os

if __name__ != "__main__":
    from . import wordfinder
    from . import utils


"""
User Interface Module.

This module is the only one that communicates with the user. It constitutes
the complete interface for this application. It imports the utils modules and,
in this case, the Wordfinder game module. Each game solver will have its own
module.
This module will contain the minimum logic needed for the interface and will
be kept as clean as possible. It will be based on external reusable functions
like those in the utils module.
All the game solver logic will have its own independent and completely
autonomous module.
This module will contain three main interfaces: the main interface, the game
selection interface, and each game's interface. Each game will have its own
interface for data input and output. The game selection interface will be
responsible for connecting inputs, processing, and outputs. Each interface
will also be responsible for displaying data in the console, saving logs,
and maintaining history, always invoking external functions.
"""


__all__: list[str] = ["run_cli"]


class WordFinderCLI:
    """
    Word Finder Interface.

    This class and its modules are specifically created to be the input
    and output data interface for this game solver. It is responsible
    for capturing input data, and displaying the data on the console as
    output, and saving the user log and history.
    """
    @staticmethod
    def word_finder_input()-> tuple[str, str]:
        """
        Word Finder User Interface, For input data.

        Args:
            None

        Returns:
            tuple
                str: Length of the words to search for.
                str: Letters that must contain the words to search for, they
                    do not have to be all the letters, they can be combinations of some of them.
        """
        print(f"\nWord Finder")
        word_length: str = input(f"Enter the length of the word to guess: ")
        available_letters: str = input(f"Enter all available letters: ")
        return (word_length, available_letters)
    
    @staticmethod
    def word_finder_output(length: str, letters: str, status: bool, result: str)-> None:
        """
        Word Finder User Interface, For output data.

        This method will build and send the output information to the 
        different possible outputs, by console, user history, log, Always
        open an output by console and by log, the output for user history
        will only exist if the input data is correct and generated a result
        of words in the output or simply there were no matches.

        Args:
            length (str): Required length of the searched words.
            letters (str): Letters or combinations of letters that the 
                searched words must have.
            status (bool): Indicates whether the input data was correct or not.
            result (str): If the status is True, it will generate the words
                found or indicate that there are no matches. If it is False,
                it will indicate why the entry failed.

        Returns:
            None
        """
        if status:
            size: int = len(result.split())
            matches: str = result if (result!='') else ('No matches')
            print(f"Number of possible words: {size}")
            print(f"Possible words: {matches}")
            utils.UserHistory.save_history(length, letters, size, matches)
            utils.Logs.history_log("0", matches)
        else:
            print(result)
            utils.Logs.history_log("0", result)


def word_game_solver()-> None:
    """
    Game selection interface

    Here you select games, and some of the available options are displayed
    in the console and saved to the registry. The selected game has its own
    interface for input and output data; the processing logic is separated
    into a dedicated module for game logic. This interface, in turn, serves
    as a data controller/pipeline between the input, processing, and output
    of the selected game.

    Args:
        None

    Returns:
        None
    """
    while True:
        print(f"\nWord Game Solver")
        print(f"Games:")
        print(f"Word Finder...1")
        print(f"Exit................2")
        game: str = input(f"Select a Game: ")

        match game:
            case '1':
                word_length: str
                available_letters: str
                word_length, available_letters = WordFinderCLI.word_finder_input()
                status: bool
                result: str
                status, result = wordfinder.WordFinder.word_finder(word_length, available_letters)
                WordFinderCLI.word_finder_output(word_length, available_letters, status, result)
            case '2':
                print("exit..." + "\n")
                utils.Logs.history_log("0", "exit...")
                break
            case _:                
                print("Invalid game option")
                utils.Logs.history_log("0", "Invalid game option")
        

def run_cli()-> None:
    """
    Main user interface.

    This is the main menu of the user interface, from here the main options
    are displayed, and welcome data is shown, from here the entire main user
    interface is managed and is shown in the console and saved in the log,
    the only option that is not managed from here is the game selection
    interface that has its own separate interface.

    Args:
        None

    Returns:
        None
    """

    utils.clean_console()

    print(f"Word Game Solver")

    date: str
    hours: str
    date, hours = utils.user_datetime().split()
    print(f"Welcome: {utils.username()}Date: {date} Hours: {hours}\n")

    utils.Logs.start_of_log()

    while True:
        print(f"Word Game Solver")
        print(f"Options:")
        print(f"Select game:................0")
        print(f"View history:...............1")
        print(f"Delete history:.............2")
        print(f"Help:.......................3")
        print(f"About:......................4")
        print(f"Exit the CLI application:...5")
        option: str = input("Select an option: ")

        matches: str = ""
        match option:
            case "0":
                word_game_solver()
                continue
            case "1":
                if os.name == "nt":
                    print("Close the file to continue...")
                utils.UserHistory.read_history()
                print(f"History viewed\n")
            case "2":
                utils.UserHistory.delete_history()
                print(f"History deleted\n")
            case "3":
                if os.name == "nt":
                    print("Close the file to continue...")
                utils.user_help()
                print(f"Revised Help\n")
            case "4":
                if os.name == "nt":
                    print("Close the file to continue...")
                utils.about()
                print(f"Revised About\n")
            case "5":
                print(f"Exit...")
                utils.Logs.history_log(option, matches)
                break
            case _:
                print(f"Invalid option.\n")

        utils.Logs.history_log(option, matches)

    utils.Logs.end_of_log()


if __name__ == "__main__":
    """
    Test

    Here we import the test module and run the tests contained in the
    docstring, specifically in 'Examples:'
    Other modules are also imported with the absolute paths that are
    required when importing this module directly.
    """
    import wordfinder
    import utils
    #import doctest
    #doctest.testmod(verbose=True)
    run_cli()