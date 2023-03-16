import click
import datetime
import os
import shutil
import re
from rich.pretty import pprint

from bs4 import BeautifulSoup
from markdownify import markdownify as md

from pathlib import Path

old_content = Path("/old-content/")
new_content = Path("/new-content/")

REVISED_RE = re.compile(
    r"Revised \$Date: (\d\d\d\d\-\d\d\-\d\d \d\d\:\d\d:\d\d .....)\s+\(.*\) \$"
)
REVISED_DT_FORMAT = "%Y-%m-%d %H:%M:%S %z"


COPYRIGHT_RE = re.compile(r"Copyright\s+(.*)\.")


def new_path(path):
    """Given an existing path, return the new one. Ensuring directories are created"""
    new_path = str(path)
    new_path = new_path.replace(str(old_content), str(new_content))
    os.makedirs(os.path.dirname(new_path), exist_ok=True)

    return Path(new_path)


def handle_images():
    """Copy all images into place"""
    image_suffixes = [".png", ".jpg", ".gif"]

    for suffix in image_suffixes:
        for img in old_content.glob(f"**/*{suffix}"):
            new_path = str(img)
            new_path = new_path.replace(str(old_content), str(new_content))

            os.makedirs(os.path.dirname(new_path), exist_ok=True)
            shutil.copy(str(img), str(new_path))


def get_revised_date(raw):
    m = REVISED_RE.search(raw)
    if m:
        try:
            raw_date = m.group(1).strip()
            dt = datetime.datetime.strptime(raw_date, REVISED_DT_FORMAT)
            return dt
        except Exception as e:
            print(e)
            pass
    return None


def get_copyright(raw):
    """Find the copyright lines and concatenate them"""
    matches = COPYRIGHT_RE.findall(raw)
    if not matches:
        click.secho("- No Matches", fg="green")
        return

    results = ". ".join(matches)
    return f"{results}."


def soup(raw):
    """Convert raw html contents to BeautifulSoup object"""
    return BeautifulSoup(raw, "html.parser")


def get_title(soup):
    if not soup.title:
        return None
    return soup.title.string.replace("\n", "")


def clean_markdown(markdown):
    """Remove things we don't want in our ultimate markdown"""
    markdown = REVISED_RE.sub("", markdown)
    markdown = COPYRIGHT_RE.sub("", markdown)
    markdown = re.sub(r"Revised \$Date\$", "", markdown)
    markdown = re.sub(r"\n\n\n\n", "\n", markdown)
    return markdown


def build_frontmatter(metadata):
    lines = ["---"]
    for k, v in metadata.items():
        if v:
            lines.append(f"{k}: {v}")
        else:
            lines.append(f"{k}: ")
    lines.append("---")

    return "\n".join(lines)


def handle_html():
    """Copy and parse all HTML into Markdown in new content"""

    for html in old_content.glob("**/*.html"):
        p = new_path(html)
        print(f"{html} -> {p}")
        raw = open(html).read()

        # Determine Front Matter elements
        rd = get_revised_date(raw)
        copyright = get_copyright(raw)

        s = soup(raw)
        title = get_title(s)

        metadata = {
            "title": title,
            "copyright": copyright,
            "revised": rd and rd.strftime(REVISED_DT_FORMAT),
        }
        frontmatter = build_frontmatter(metadata)

        pprint(metadata, expand_all=True)
        markdown = md(raw)
        markdown = clean_markdown(markdown)

        click.secho(f"Writing {p}...", fg="green")
        with open(p, "w") as f:
            f.write(frontmatter)
            f.write(markdown)


@click.command
def cli():
    handle_images()
    handle_html()
