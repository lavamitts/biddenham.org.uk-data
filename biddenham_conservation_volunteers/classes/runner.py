from .task import Task
from docx import Document
import os
import sys
import utils.string_utils as su
from common.style import Colour


class Runner:
    def make_tasks(self):
        # Task list v89 2026.docx
        # Display instructions to the user
        print(f"\nPlace your original Word document in the folder {Colour.BOLD}{Colour.MAGENTA}resources/input{Colour.RESET} and then enter the filename at the prompt.\n")
        print(f"\nPlease {Colour.BOLD}{Colour.MAGENTA}make all corrections{Colour.RESET} to the Word document in advance of running this function.\n")

        # Capture the filename from the user
        filename = input("Please enter the filename of the Word document: ").strip()
        filename = su.add_file_extension(filename, "docx")

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
            print(f"\n{Colour.RED}AN ERROR HAS OCCURRED.")
            print(f"\nFile '{Colour.CYAN}{filename}{Colour.RESET}' not found. Please check.\n")
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
            task.insert_event_via_api()

        print(f"\n{Colour.CYAN}COMPLETE{Colour.RESET}\n========")
        print(f"\nData extracted to folder '{Colour.CYAN}resources/output{Colour.RESET}'\n")
