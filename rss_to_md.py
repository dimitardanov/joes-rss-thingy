import os
import time
import re
import random
import feedparser
import requests
from bs4 import BeautifulSoup


# Globals
RSS_URL = "https://latenightlinux.com/feed/mp3"
MD_DIR = "markdown_files"
INTER_REQ_SLEEP = 5




class RSSFeedEntryData():
    """A class to store and analyze an RSS feed entry."""

    def __init__(self, title, date, url, summary, content):
        """
        Initialize RSSFeedEntryData and create BeautifulSoup from "content".
        
        Args:
            title: RSS Feed Entry title
            date: Publication date
            url: url of the RSS Entry page
            summary: description of the RSS Feed Entry <description> tag content
            content: html of the RSS Feed Entry <content:encoded> tag contents
        """
        self.title = title
        self.date = date
        self.url = url
        self.summary = summary
        self.content = content
        self.soup = BeautifulSoup(content, 'html5lib')
        self.discoveries = {}
    
    def _add_discovery(self, title, url):
        """Add a discovery entry."""
        self.discoveries[title] = {"url": url}
    
    def _add_discovery_descr(self, title, descr):
        """Add a description to an existing discovery entry."""
        self.discoveries[title]["descr"] = descr

    def scan_for_discoveries(self):
        """Find urls of the "Discoveries" section if exists."""
        is_discoveries_section = False
        for para in self.soup.find_all("p"):
            # Section titles in <strong> tags
            # Detect section boundary, 
            # set/unset a flag if going through a "Discoveries" section
            if para.find("strong"):
                if "Discoveries" in para.find("strong").stripped_strings:
                    is_discoveries_section = True
                else:
                    is_discoveries_section = False
                continue
            # Store "discoveries"
            # in case a paragraph has multiple discoveries
            if is_discoveries_section:
                for link_tag in para.find_all("a"):
                    title = link_tag.get_text()
                    url = link_tag.attrs["href"]
                    self._add_discovery(title, url)

    def get_descriptions(self):
        for title in self.discoveries.keys():
            url = self.discoveries[title]["url"]
            descr = get_description_from_url(url)
            self._add_discovery_descr(title, descr)
            time.sleep(INTER_REQ_SLEEP)

    def _encode_md_urls(self):
        """Return markdown code for discoveries."""
        mdown = []
        for title in self.discoveries.keys():
            url = self.discoveries[title]["url"]
            descr = self.discoveries[title]["descr"]
            mdown.append(f"[{title}]({url}) -- {descr}\n\n")
        return "".join(mdown)

    def get_markdown_repr(self):
        """Return a string, formatted as markdown of the data."""
        discoveries = self._encode_md_urls()
        return f"""## [{self.title}]({self.url})

_{self.date}_

__{self.summary}__

### Discoveries

{discoveries}
---\n\n"""

    def count_discoveries(self):
        """Return the number of discoveries for the entry."""
        return len(self.discoveries.keys())

    def create_filename(self):
        """Return a lexically sortable filename e.g.:"0032-..." """
        try:
            entry_no = int(re.search("\d+$", self.title).group(0))
        except:
            entry_no = random.randint(9000, 9999)
        return f"{entry_no:04d} -- {self.title}.md"




def get_web_page(url):
    """Return the HTML for a given url"""    
    try:
        resp = requests.get(url, timeout=5)
        resp.raise_for_status()
        return resp.text
    except:
        return "Error"


def _check_if_meta_description(tag):
    """Check if the given tag is <meta name="description" content="..."/>."""
    return (tag.name.lower() == "meta"
            and (tag.has_attr("name") and tag.attrs.get("name") == "description")
            and (tag.has_attr("content") and tag.attrs.get("content"))
            )


def get_description_from_html(html):
    """
    Return the desription (value of content attribute of a meta tag)
    if the given html has one, otherwise return 'None'.
    In the rest of the cases return "Error"
    """
    if html == "Error":
        return html
    
    try:
        soup = BeautifulSoup(html, "html5lib")
        descr = soup.find(_check_if_meta_description).get("content")
        return descr
    except:
        return "None"


def get_description_from_url(url):
    """
    Return a description string from the web page for the given url
    """
    html = get_web_page(url)
    return get_description_from_html(html)



def create_markdown_dir(dir_name):
    """Create a directory in the current dir if doesn't exist."""
    if not os.path.exists(dir_name):
        os.mkdir(dir_name)


def save_entry_markdown(entry, dir_name):
    """
    Save a RSSFeedEntryData to markdown in the dir_name.

    Creates a markdown file containing the data from 
    a given RSSFeedEntryData instance if the file does not exist
    and the entry has "discoveries".
    """
    file_name = entry.create_filename()
    file_path = os.path.join(dir_name, file_name)
    if (not os.path.exists(file_path)) and entry.count_discoveries() > 0:
        with open(file_path, 'w') as fh:
            fh.write(entry.get_markdown_repr())


def md_file_exists(entry_data, dir_name):
    """Check if a corresponding markdown file exists"""
    file_name = entry_data.create_filename()
    file_path = os.path.join(dir_name, file_name)
    return os.path.exists(file_path)

    


if __name__ == "__main__":

    create_markdown_dir(MD_DIR)

    try:
        print(f"Downloading RSS feed from {RSS_URL}...")
        pf = feedparser.parse(RSS_URL)
        print("Done.")
        print()
    except:
        print("Error occurred in downloading the feed.")

    print("Processing the feed...")
    print()
    for entry in pf["entries"]:
        print(f"Processing: {entry.title}...")
        print(f"\turl: {entry.link}")
        e_data = RSSFeedEntryData(
                title = entry.title,
                date = time.strftime("%Y-%m-%d", entry.published_parsed),
                url = entry.link,
                summary = entry.summary,
                content = entry.content[0].value
                )
        e_data.scan_for_discoveries()
        # Check if markdown file exists
        if md_file_exists(e_data, MD_DIR):
            print(f"\tMarkdown file for {entry.title} exists. Skipping.")
        # Skip if no "discoveries" are found
        elif e_data.count_discoveries() == 0:
            print(f"\tNo Discoveries found in the entry. Skipping.")
        else:
            e_data.get_descriptions()
            save_entry_markdown(e_data, MD_DIR)
            print(f"\tSaved markdown file with {e_data.count_discoveries()} discoveries.")
        print()
