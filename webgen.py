#!/usr/bin/env python3
# Aliaume LOPEZ
# 2024
#
# This is a simple static website generator
# that takes as input a list of bibtex files
# plus a template repository and generates
# a static website.

import os
import shutil
import sys
import argparse
import bibtexparser
from bibtexparser.bibdatabase import BibDatabase
import yaml
from pathlib import Path
import dataclasses
from jinja2 import Environment, FileSystemLoader
from typing import List, Dict, Literal
import itertools

@dataclasses.dataclass
class WebsiteConfig:
    papers: List[dict]
    template_dir: Path
    output_dir: Path

@dataclasses.dataclass
class Paper:
    title: str
    authors: List[str]
    year: int
    sha256: List[str]
    doi: List[str]
    arxiv: List[str]
    url: List[str]

    entry: str

    kind : Literal["book", "journal", "code", "conference", "preprint", "thesis", "other"] = "other"

    def __getitem__(self, key):
        return getattr(self, key)
    
    def get(self, key, default):
        return getattr(self, key, default)

type_mapping = {
    "article": "journal",
    "inproceedings": "conference",
    "book": "book",
    "phdthesis": "thesis",
    "mastersthesis": "thesis",
    "techreport": "preprint",
    "misc": "other",
    "unpublished": "other",
    "software": "code",
    "manual": "book",
    "proceedings": "conference",
    "incollection": "book",
    "inbook": "book",
    "collection": "book",
    "conference": "conference",
    "other": "other"
}

def infer_kind(entry):
    entrytype = entry.get("ENTRYTYPE", "other")
    kind = type_mapping.get(entrytype, "other")
    if kind == "other" and entry.get("eprint",None) is not None:
        return "preprint"
    return kind

def entry_to_paper(entry) -> Paper:
    title = entry.get("title", "Unknown Title")
    year = int(entry.get("year", "0").strip())
    authors = list(map(str.strip, entry.get("author", "").replace("\n"," ").split(" and ")))
    sha256  = list(filter(lambda x: x, map(str.strip, entry.get("sha256", "").split(",")    )))
    doi     = list(filter(lambda x: x, map(str.strip, entry.get("doi",    "").split(",")    )))
    arxiv   = list(filter(lambda x: x, map(str.strip, entry.get("eprint", "").split(",")    )))
    url     = list(filter(lambda x: x, map(str.strip, entry.get("url",    "").split(",")    )))

    kind = infer_kind(entry)

    db = BibDatabase()
    db.entries = [entry]
    bibcode = bibtexparser.dumps(db).strip()
    return Paper(title, authors, year, sha256, doi, arxiv, url, bibcode, kind)

@dataclasses.dataclass
class Website:
    papers: List[dict]
    sha256s: Dict[str,List[dict]]
    dois: Dict[str,List[dict]]
    arxivs: Dict[str,List[dict]]
    authors: Dict[str,List[dict]]
    templates: Environment
    output_dir: Path
    template_dir: Path

def config_to_website(config: WebsiteConfig) -> Website:
    papers = []
    sha256s = {}
    dois = {}
    arxivs = {}
    authors = {}
    env = Environment(loader=FileSystemLoader(config.template_dir))

    for paper in config.papers:
        papers.append(paper)
        for sha256 in paper.sha256:
            sha256s.setdefault(sha256, []).append(paper)
        for doi in paper.doi:
            dois.setdefault(doi, []).append(paper)
        for arxiv in paper.arxiv:
            arxivs.setdefault(arxiv, []).append(paper)
        for author in paper.authors:
            authors.setdefault(author, []).append(paper)

    return Website(papers, sha256s, dois, arxivs, authors, env, config.output_dir, config.template_dir)

def render_website(website: Website):
    # create the output directory if it does not exist already
    website.output_dir.mkdir(parents=True, exist_ok=True)
    for name in ['sha256', 'doi', 'arxiv', 'author']:
        render_list(website, name)
    render_index(website)
    render_hugelist(website)
    render_page(website, "404")
    render_page(website, "about")
    render_static_files(website)

def render_hugelist(website: Website):
    template = website.templates.get_template('hugelist.html')
    by_year = sorted(website.papers, key=lambda x: x.year, reverse=True)
    grouped = [ (year, list(papers)) for (year, papers) in itertools.groupby(by_year, key=lambda x: x.year) ]
    total = len(website.papers)
    with open(website.output_dir / 'list.html', 'w') as f:
        f.write(template.render(title="List", papers_by_year=grouped, root_url=".", total=total))

def render_page(website: Website, name : str):
    template = website.templates.get_template(f'{name}.html')
    with open(website.output_dir / f'{name}.html', 'w') as f:
        f.write(template.render(title=name, root_url="."))

def render_index(website: Website):
    template = website.templates.get_template('index.html')
    total = len(website.papers)

    with open(website.output_dir / 'index.html', 'w') as f:
        f.write(template.render(title="Search", total=total, root_url="."))

def render_list(website: Website, name : str):
    template = website.templates.get_template(f'result.html')
    d = getattr(website, name + "s")
    for identifier, papers in d.items():
        # create the directory if it does not exist already
        outpath =  website.output_dir / name / f'{identifier}.html'
        outpath.parent.mkdir(parents=True, exist_ok=True)
        with open(website.output_dir / name / f'{identifier}.html', 'w') as f:
            title = f"{name} — {identifier[:10]}"
            f.write(template.render(title=title, 
                                    field=name, 
                                    identifier=identifier,
                                    papers=papers,
                                    total=len(papers),
                                    root_url="../.."))

def read_bibtex(bibtex_file):
    with open(bibtex_file, 'r') as f:
        return bibtexparser.load(f)

def render_static_files(website: Website):
    css_dir = website.output_dir / "static" / "css"
    css_dir.mkdir(parents=True, exist_ok=True)
    # now we copy style.css to the static directory
    style_dest = css_dir / "style.css"
    style_orig = website.template_dir / "style.css"
    shutil.copyfile(style_orig, style_dest)



def main():
    parser = argparse.ArgumentParser(description='Generate a static website from a list of bibtex files')
    parser.add_argument('bibtex_files', type=str, nargs='+', help='List of bibtex files')
    parser.add_argument('--template', type=str, default='template', help='Template directory')
    parser.add_argument('--output', type=str, default='output', help='Output directory')
    args = parser.parse_args()

    # Check that the template directory exists
    if not os.path.exists(args.template):
        print(f"Error: template directory {args.template} does not exist")
        sys.exit(1)

    # creates the website config
    papers = []
    for f in args.bibtex_files:
        bibdatabase = read_bibtex(f)
        for entry in bibdatabase.entries:
            papers.append(entry_to_paper(entry))

    config = WebsiteConfig(
        papers=papers,
        template_dir=Path(args.template),
        output_dir=Path(args.output)
    )

    # creates the website
    website = config_to_website(config)

    # renders the website
    render_website(website)

if __name__ == '__main__':
    main()
