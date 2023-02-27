from bs4.element import Tag
import requests
from requests.models import Response
from bs4 import BeautifulSoup
from collections import deque

from parse_utils import parse_tag

class WeeklyNvimArticleParser:
    def __init__(self, url: str) -> None:
        """
        Reads the index html page received from the passed URL and tries to look for the latest article. It then
        parses it and stores it for later usage.
        """
        # Load article page
        post: Response = requests.get(f"{url}/latest")
        self.html: BeautifulSoup = BeautifulSoup(post.text, 'html.parser')
        self.text_queue: deque[str] = deque()

        # Save title in queue
        title: Tag = self.html.head.title    # type: ignore
        self.text_queue.append(f"*=== {title.text} ===*")

        # Parse article page
        self.parse_document()

    def parse_document(self):
        """
        Parses the whole stored document and saves it into a queue
        """
        for element in self.html.find_all():
            texts: list[str] = parse_tag(element)
            if not texts:
                continue

            for text in texts:
                self.text_queue.append(text)

    def print_document(self):
        """
        Prints the whole read document into terminal
        """
        while len(self.text_queue) != 0:
            print(self.text_queue.popleft())

    def get_document_text(self) -> list[str]:
        """
        Returns a formatted string with all the parsed text
        """
        text = []
        while len(self.text_queue) != 0:
            text.append(self.text_queue.popleft())
        return text

