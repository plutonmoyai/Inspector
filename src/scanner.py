import os
import subprocess
import json
import requests
from googletrans import Translator

class DependencyScanner:
    def __init__(self, project_path, language):
        self.project_path = project_path
        self.language = language
        self.translator = Translator()
        self.dependency_files = [
            'requirements.txt', 'package.json', 'package-lock.json', 'Pipfile', 
            'Pipfile.lock', 'setup.py', 'pyproject.toml', 'Gemfile', 
            'Gemfile.lock', 'composer.json', 'composer.lock', 'go.mod', 
            'go.sum', 'Cargo.toml', 'Cargo.lock', 'Podfile', 'Podfile.lock', 
            'build.gradle', 'build.gradle.kts', 'pom.xml', 'yarn.lock', 
            'mix.exs', 'mix.lock'
        ]

    def scan(self):
        dependency_file = self.find_dependency_file()
        if not dependency_file:
            raise FileNotFoundError(f"No dependency file found in {self.project_path}.")

        print(f"Running safety check on {dependency_file}...")
        result = subprocess.run(['safety', 'check', '--file=' + dependency_file, '--json'], capture_output=True, text=True)
        
        print(f"Safety check output: {result.stdout}")
        print(f"Safety check error: {result.stderr}")

        try:
            data = json.loads(result.stdout)
        except json.JSONDecodeError:
            raise ValueError("Safety check output could not be parsed as JSON.")

        print(f"Safety check results: {data}")
        
        vulnerabilities = []
        for issue in data.get('vulnerabilities', []):
            translated_description = self.translator.translate(issue['advisory'], src='en', dest=self.language).text
            latest_version = self.get_latest_version(issue['package_name'], dependency_file)
            suggested_version = latest_version if latest_version else 'N/A'
            vulnerabilities.append({
                'package_name': issue['package_name'],
                'affected_version': issue['vulnerable_spec'],
                'description': translated_description,
                'CVE': issue['CVE'],
                'suggested_version': suggested_version
            })
        
        return vulnerabilities

    def find_dependency_file(self):
        for dep_file in self.dependency_files:
            path = os.path.join(self.project_path, dep_file)
            if os.path.exists(path):
                return path
        return None

    def get_latest_version(self, package_name, dependency_file):
        if dependency_file.endswith('.txt') or dependency_file.endswith('.py'):
            return self.get_latest_version_pypi(package_name)
        elif dependency_file.endswith('package.json') or dependency_file.endswith('package-lock.json') or dependency_file.endswith('yarn.lock'):
            return self.get_latest_version_npm(package_name)
        elif dependency_file.endswith('Gemfile') or dependency_file.endswith('Gemfile.lock'):
            return self.get_latest_version_rubygems(package_name)
        elif dependency_file.endswith('composer.json') or dependency_file.endswith('composer.lock'):
            return self.get_latest_version_packagist(package_name)
        elif dependency_file.endswith('go.mod') or dependency_file.endswith('go.sum'):
            return self.get_latest_version_goproxy(package_name)
        elif dependency_file.endswith('Cargo.toml') or dependency_file.endswith('Cargo.lock'):
            return self.get_latest_version_crates(package_name)
        elif dependency_file.endswith('build.gradle') or dependency_file.endswith('pom.xml'):
            return self.get_latest_version_maven(package_name)
        else:
            return None

    def get_latest_version_pypi(self, package_name):
        try:
            response = requests.get(f"https://pypi.org/pypi/{package_name}/json")
            if response.status_code == 200:
                data = response.json()
                return data['info']['version']
        except Exception as e:
            print(f"Could not retrieve the latest version for {package_name} from PyPI: {e}")
        return None

    def get_latest_version_npm(self, package_name):
        try:
            response = requests.get(f"https://registry.npmjs.org/{package_name}")
            if response.status_code == 200:
                data = response.json()
                return data['dist-tags']['latest']
        except Exception as e:
            print(f"Could not retrieve the latest version for {package_name} from NPM: {e}")
        return None

    def get_latest_version_rubygems(self, package_name):
        try:
            response = requests.get(f"https://rubygems.org/api/v1/gems/{package_name}.json")
            if response.status_code == 200:
                data = response.json()
                return data['version']
        except Exception as e:
            print(f"Could not retrieve the latest version for {package_name} from RubyGems: {e}")
        return None

    def get_latest_version_packagist(self, package_name):
        try:
            response = requests.get(f"https://repo.packagist.org/p/{package_name}.json")
            if response.status_code == 200:
                data = response.json()
                return list(data['packages'][package_name].keys())[-1]
        except Exception as e:
            print(f"Could not retrieve the latest version for {package_name} from Packagist: {e}")
        return None

    def get_latest_version_goproxy(self, package_name):
        try:
            response = requests.get(f"https://proxy.golang.org/{package_name}/@latest")
            if response.status_code == 200:
                data = response.json()
                return data['Version']
        except Exception as e:
            print(f"Could not retrieve the latest version for {package_name} from Go Proxy: {e}")
        return None

    def get_latest_version_crates(self, package_name):
        try:
            response = requests.get(f"https://crates.io/api/v1/crates/{package_name}")
            if response.status_code == 200:
                data = response.json()
                return data['crate']['max_version']
        except Exception as e:
            print(f"Could not retrieve the latest version for {package_name} from Crates.io: {e}")
        return None

    def get_latest_version_maven(self, package_name):
        try:
            response = requests.get(f"https://search.maven.org/solrsearch/select?q=g:{package_name}&rows=1&wt=json")
            if response.status_code == 200:
                data = response.json()
                docs = data.get('response', {}).get('docs', [])
                if docs:
                    return docs[0].get('latestVersion')
        except Exception as e:
            print(f"Could not retrieve the latest version for {package_name} from Maven: {e}")
        return None
