import yaml
import subprocess
import logging
import inspect


class Helper:
    """
    Helper class providing logging utilities, colorized output, YAML file reading, and shell command execution.
    """
    COLORIZE = True
    colors = {
        "red": 31,
        "green": 32,
        "yellow": 33,
        "white": 37,
        "magenta": 35,
        "cyan": 36
    }
    logger = logging.getLogger("kubeverse")
    logger.setLevel(logging.DEBUG)
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    formatter = logging.Formatter('[%(levelname)s] %(message)s')
    ch.setFormatter(formatter)
    if not logger.hasHandlers():
        logger.addHandler(ch)
    else:
        logger.handlers.clear()
        logger.addHandler(ch)

    @classmethod
    def colorize(cls, message: str, color: str) -> str:
        """
        Return the message string colorized for terminal output if COLORIZE is enabled.
        Args:
            message (str): The message to colorize.
            color (str): The color name (e.g., 'red', 'green').
        Returns:
            str: The colorized message.
        Raises:
            ValueError: If the color is not valid.
        """
        if not cls.COLORIZE:
            return message
        if color in cls.colors:
            return f"\033[{ cls.colors[color] };5m{ message }\033[0m"
        else:
            raise ValueError(f"Invalid color: {color}")

    @classmethod
    def log_error(cls, message: str):
        """
        Log an error message in red with the calling function name.
        """
        caller = inspect.stack()[1].function
        cls.logger.error(f"{caller} - {cls.colorize(message, 'red')}")

    @classmethod
    def log_info(cls, message: str):
        """
        Log an info message in green with the calling function name.
        """
        caller = inspect.stack()[1].function
        cls.logger.info(f"{caller} - {cls.colorize(message, 'green')}")

    @classmethod
    def log_warning(cls, message: str):
        """
        Log a warning message in yellow with the calling function name.
        """
        caller = inspect.stack()[1].function
        cls.logger.warning(f"{caller} - {cls.colorize(message, 'yellow')}")

    @classmethod
    def log_debug(cls, message: str):
        """
        Log a debug message in white with the calling function name.
        """
        caller = inspect.stack()[1].function
        cls.logger.debug(f"{caller} - {cls.colorize(message, 'white')}")

    @classmethod
    def log_critical(cls, message: str):
        """
        Log a critical message in magenta with the calling function name.
        """
        caller = inspect.stack()[1].function
        cls.logger.critical(f"{caller} - {cls.colorize(message, 'magenta')}")

    @classmethod
    def log_shell(cls, message: str):
        """
        Log a shell command message in cyan with the calling function name.
        """
        caller = inspect.stack()[1].function
        cls.logger.debug(f"{caller} - {cls.colorize(message, 'cyan')}")

    @staticmethod
    def get_yaml(filename: str):
        """
        Read a YAML file and return its contents as a Python object.
        Args:
            filename (str): Path to the YAML file.
        Returns:
            object: Parsed YAML content.
        Raises:
            Exception: If the file cannot be read or parsed.
        """
        try:
            with open(filename, "r") as file:
                result = yaml.safe_load(file)
        except Exception as exc:
            Helper.log_error(f"Failed to get yaml '{ filename }'. Exception: { exc }")
            raise Exception(f"Failed to get yaml '{ filename }'. Exception: { exc }")
        return result

    @staticmethod
    def run_shell(cmd: str, output_return: bool = False, output_print: bool = False) -> str:
        """
        Run a shell command with optional output capture and printing.
        Args:
            cmd (str): The shell command to execute.
            output_return (bool): If True, return the command output.
            output_print (bool): If True, print the command output.
        Returns:
            str or None: The command output if output_return is True, else None.
        Raises:
            Exception: If the command fails or returns a non-zero exit code.
        """
        capture_output = True
        if output_return == False and output_print == False:
            capture_output = False
        try:
            Helper.log_shell(f"_> { cmd }")
            result = subprocess.run(
                cmd, shell = True, capture_output = capture_output, text = True
            )
        except Exception as exc:
            Helper.log_error(f"Failed to run command '{ cmd }'. Exception: { exc }")
            raise Exception(f"Failed to run command '{ cmd }'. Exception: { exc }")
        if result.returncode != 0:
            Helper.log_error(f"Wrong exit code: { result.returncode } - Command '{ cmd }'")
            raise Exception(f"Wrong exit code: { result.returncode } - Command '{ cmd }'")
        if output_print == True:
            Helper.log_shell(f"Output: { result.stdout }")
        if output_return == True:
            return result.stdout
        return None
