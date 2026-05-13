class Task:
    def __init__(self, row):
        self.date = row.cells[0].text.strip()
        self.task_number = row.cells[1].text.strip()
        self.location = row.cells[2].text.strip()
        self.nature_of_task = row.cells[3].text.strip()
        self.start_time = row.cells[4].text.strip()
        self.end_time = row.cells[5].text.strip()
        self.leader = row.cells[6].text.strip()
        self.tools = row.cells[7].text.strip()
        self.title = f"Biddenham Conservation Volunteers - {self.nature_of_task} {self.location}"
        self.format_tools()

    def format_tools(self):
        if "tools in shed" in self.tools.lower():
            self.tools = self.tools.replace("tools in shed", "")
            self.tools = self.tools.strip()
            self.tools = self.tools.strip(",")
            self.tools = self.tools.strip()
            self.tools += ". Tools are available in the shed"

    def __repr__(self):
        return f"Task(date='{self.date}', task_number='{self.task_number}', location='{self.location}')"

    @property
    def prose_representation(self):
        template = "<img src='/wp-content/uploads/2025/06/conservation-volunteers-1024x285.webp' width='240' height='67' />"
        template += f"<p>On {self.date}, the Biddenham Conservation Volunteers will be carrying out {self.nature_of_task} at {self.location}. This will start at {self.start_time} and end at {self.end_time}. The session will be led by {self.leader}.</p>"
        if self.tools != "":
            template += f"<p>Please bring {self.tools}.</p>"
        template += "<p>We hope to see you there.</p>"
        template += "\n<p><a href='/biddenham-conservation-volunteers/'>Find out more about the work of the Biddenham Conservation Volunteers</a>"
        template += '\n<p>If you would like to join us, please contact Gilly Cowan, and she will send you further information.</p>'
        template += '\n<p class="email icon"><a href="mailto:gillycowan@btinternet.com">gillycowan@btinternet.com</a></p>'
        return template
