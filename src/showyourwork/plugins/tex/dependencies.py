import json
import re
from pathlib import Path
from xml.etree import ElementTree

from showyourwork import paths


def parse_dependencies(
    xmlfile: paths.PathLike, depfile: paths.PathLike, base_path: paths.PathLike
) -> None:
    base_path = Path(base_path).resolve()
    xmlfile = Path(xmlfile)
    data = xmlfile.read_text()
    xml_tree = ElementTree.fromstring("<HTML>" + data + "</HTML>")

    # Parse the \graphicspath command
    #
    # Note that if there are multiple calls, only the last one is read. Same for
    # multiple directories within a graphicspath call.
    gpath_elements = xml_tree.findall("GRAPHICSPATH")
    graphics_path = base_path
    if len(gpath_elements) > 0:
        if len(gpath_elements) > 1:
            # TODO(dfm): Add a warning here.
            pass
        text = gpath_elements[-1].text
        if text is not None:
            graphics_path = re.findall("\\{(.*?)\\}", text)[0]
            graphics_path = base_path / graphics_path

    # Extract all the figure dependencies
    figures = {}
    unlabeled_graphics = []
    for figure in xml_tree.findall("FIGURE"):
        graphics = [
            graphics_path / graphic.text
            for graphic in figure.findall("GRAPHICS")
            if graphic.text is not None
        ]

        # Get the figure \label, if it exists
        labels = figure.findall("LABEL")
        if len(labels):
            if len(labels) > 1:
                # TODO(dfm): Add a warning here.
                pass
            label = labels[0].text
            figures[label] = graphics
        else:
            unlabeled_graphics.extend(graphics)

    # Find any other free-floating graphics
    unlabeled_graphics.extend(
        graphics_path / graphic.text
        for graphic in xml_tree.findall("GRAPHICS")
        if graphic.text is not None
    )

    # Parse files included using the \input statement; these will be made
    # explicit dependencies of the build
    files = [
        base_path / file.text
        for file in xml_tree.findall("INPUT")
        if file.text is not None
    ]

    with open(depfile, "w") as f:
        json.dump(
            {"figures": figures, "unlabled": unlabeled_graphics, "files": files},
            f,
            sort_keys=True,
            indent=2,
        )