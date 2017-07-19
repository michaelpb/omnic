from enum import Enum


class Task(Enum):
    FUNC = 1          # Synchronous function
    DOWNLOAD = 2      # Downloading a file
    CONVERT = 3       # Running a converter
    MULTICONVERT = 4  # Full conversion path
