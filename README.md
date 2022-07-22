# Joe's RSS Thingy

## Introduction

Scripts to organize and annotate links under the _Discoveries_ sections from the [LNL](https://latenightlinux.com/) in markdown files. Links (discoveries) from each episode are grouped in a separate markdown file. Annotations are taken from _content_ attribute of the `<meta name="description" />` tags for each link, if exists.

## Installation

```
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Running

Enter the python environment:
```
source venv/bin/activate
python rss_to_md.py
```

Optionally, `combine_markdown.sh` can be used to create a single markdown document `ALL_DISCOVERIES` with all links, using `md_template.md` as a header.


## License

MIT License
