"""THis is the futur slave worker's code, for now it does nothing than create a file
 something, to test that it has been launched"""

from datetime import datetime
from sys import executable

if __name__ == "__main__":
    with open("testfile.txt", "r") as file:
        file.write(str(datetime.now()))
        file.write("\n" + executable)
