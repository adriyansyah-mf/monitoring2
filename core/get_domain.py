import datetime

import certstream
import re
import subprocess
from sqlalchemy.orm import sessionmaker
from core.run_httpx import run_httpx_command
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from core.run_nuclei import run_nuclei_command
from models.db import engine
from models.DomainsNotLive import DomainsNotLiveModel
from models.DomainsLive import DomainsModel






Session = sessionmaker(bind=engine)

def insert_not_live(session, domain, CN):
    try:
        with session.begin():
            query = DomainsNotLiveModel.insert().values(domain=domain, tanggal=datetime.date.today(), cname=CN)
            session.execute(query)
            session.commit()
            session.close()
    except Exception as e:
        print(f"Error occurred while inserting: {e}")

def insert_live(session, domain, CN):
    try:
        with session.begin():
            query = DomainsModel.insert().values(domain=domain, tanggal=datetime.date.today(), cname=CN, scanned=False)
            session.execute(query)
            session.commit()
            session.close()
    except Exception as e:
        print(f"Error occurred while inserting: {e}")



class PatternFileHandler(FileSystemEventHandler):
    def __init__(self, handler):
        self.handler = handler

    def on_modified(self, event):
        if event.src_path == self.handler.target_file_path:
            print(f"File {event.src_path} has been modified, reloading patterns.")
            self.handler.load_patterns()

class CertStreamHandler:
    def __init__(self, target_file_path, certstream_url):
        self.target_file_path = target_file_path
        self.certstream_url = certstream_url
        self.load_patterns()

    def load_patterns(self):
        self.regex_patterns = []
        with open(self.target_file_path) as file:
            patterns = file.readlines()
            for pattern in patterns:
                regex_pattern = self._pattern_to_regex(pattern)
                self.regex_patterns.append(re.compile(regex_pattern))

    def _pattern_to_regex(self, pattern):
        pattern = pattern.strip()
        regex = pattern.replace('*.', r'([a-zA-Z0-9-]+\.)*')  # Replace * with .*
        return f'^{regex}$'

    def print_callback(self, message, context):
        CN = message['data']['leaf_cert']['subject']['CN']
        domains = message['data']['leaf_cert']['all_domains']
        for domain in domains:
            for regex in self.regex_patterns:
                if regex.search(domain):
                    print(f"GOT DOMAIN {domain}")
                    with Session() as session:
                        httpx_output = run_httpx_command(domain)
                        if httpx_output is not False:
                            insert_live(session, httpx_output['url'], CN)
                            run_nuclei_command(httpx_output['url'])
                        else:
                            insert_not_live(session, domain, CN)

    def on_open(self):
        print("Connection successfully established!")

    def on_error(self, instance, exception):
        print("Exception in CertStreamClient! -> {}".format(exception))

    def start_listening(self):
        try:
            certstream.listen_for_events(
                self.print_callback,
                on_open=self.on_open,
                on_error=self.on_error,
                url=self.certstream_url
            )
        except Exception as e:
            print(f"Error occurred while listening to CertStream: {e}")

if __name__ == "__main__":
    handler = CertStreamHandler("../target.txt", "wss://certstream.calidog.io/")
    handler.start_listening()
