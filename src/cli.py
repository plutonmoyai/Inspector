import click
from scanner import DependencyScanner
from reporter import Reporter

class CustomCommand(click.Command):
    def format_help(self, ctx, formatter):
        super().format_help(ctx, formatter)
        formatter.write("\nDeveloper:\n  S. Sercan 'PlutonLib' Uyan | https://github.com/plutonlib\n  For contact: x0pluton@proton.me")

@click.command(cls=CustomCommand)
@click.argument('project_path', type=click.Path(exists=True))
@click.option('--language', prompt='Select the language (Just type English)', help='Choose the language for the report (e.g., en, tr, es).')
def scan(project_path, language):
    """Scans the specified project for dependency vulnerabilities."""
    scanner = DependencyScanner(project_path, language)
    vulnerabilities = scanner.scan()
    if not vulnerabilities:
        print("No vulnerabilities found or an error occurred during scanning.")
    else:
        reporter = Reporter(vulnerabilities, project_path)
        reporter.create_report()
        print("Scanning completed and report generated.")

if __name__ == '__main__':
    scan()
