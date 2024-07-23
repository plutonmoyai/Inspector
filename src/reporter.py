import json
import os

class Reporter:
    def __init__(self, vulnerabilities, project_path):
        self.vulnerabilities = vulnerabilities
        self.project_path = project_path

    def create_report(self):
        project_name = os.path.basename(os.path.normpath(self.project_path))
        file_name = f'{project_name}-report.json'
        file_path = os.path.join(self.project_path, file_name)

        i = 2
        while os.path.exists(file_path):
            file_name = f'{project_name}-report-{i}.json'
            file_path = os.path.join(self.project_path, file_name)
            i += 1

        with open(file_path, 'w') as f:
            json.dump(self.vulnerabilities, f, indent=4, ensure_ascii=False)
        print(f"Report generated: {file_path}")