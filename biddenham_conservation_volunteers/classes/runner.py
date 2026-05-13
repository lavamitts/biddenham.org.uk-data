from .task import Task
from colorama import Fore, Style, init
from docx import Document
import os
import sys


class Runner:
    def __init__(self):
        # Initialize colorama (required for Windows support)
        init(autoreset=True)

    def make_tasks(self):
        # Task list v89 2026.docx
        # Display instructions to the user
        print(
            "\nPlace your file in the folder resources/input and then enter the filename at the prompt.\n"
        )

        # Capture the filename from the user
        filename = input("Please enter the filename: ")

        # Construct the full path
        full_path = os.path.join(
            os.getcwd(),
            "biddenham_conservation_volunteers",
            "resources",
            "input",
            filename,
        )

        # Load the Word document
        if not os.path.exists(full_path):
            print(f"\n{Fore.RED}AN ERROR HAS OCCURRED.")
            print(
                f"\nFile '{Fore.CYAN}{filename}{Style.RESET_ALL}' not found. Please check.\n"
            )
            sys.exit()

        doc = Document(full_path)  # Replace with your actual file name

        # Extract tasks from the first table
        tasks = []

        # Assumes the table is the first one in the document
        table = doc.tables[0]

        # Skip the header row (start from row 1)
        for row in table.rows[1:]:
            task = Task(row)
            tasks.append(task)

        # Output the extracted tasks
        for task in tasks:
            # print(task.prose_representation)
            folder = "biddenham_conservation_volunteers/resources/output"
            filename = f"task{task.task_number}.txt"
            path = os.path.join(folder, filename)
            with open(path, "w") as file:
                file.write(f"{task.title}\n\n")
                file.write(task.prose_representation)

        print(f"\n{Fore.CYAN}COMPLETE{Style.RESET_ALL}\n========")
        print(
            f"\nData extracted to folder '{Fore.CYAN}resources/output{Style.RESET_ALL}'\n"
        )
