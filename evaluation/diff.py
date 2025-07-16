"""
Zhang-Shaha (ZSS) differencing on PlantUML documents.
"""


import os
import subprocess
import xml.etree.ElementTree as ET
from typing import List, Tuple

from zss import Node, simple_distance
from zss.compare import Operation


def strip_ns(tag: str) -> str:
    """
    Strips namespaces from XML tags.

    Args:
        tag: XML tag.

    Returns:
        XML tag with its namespace stripped.
    """
    return tag.split('}')[-1] if '}' in tag else tag


def xml_to_zss(xml: ET.Element) -> Node:
    """
    Converts XML documents into zss-compatible trees.

    Args:
        xml: XML document.

    Returns:
        zss tree.
    """
    id = ':'.join([strip_ns(xml.tag),
                   xml.attrib.get('name', ''),
                   xml.attrib.get('xmi:type', '')])
    return Node(id, list(map(xml_to_zss, xml)))


def puml_to_xml(files: List[str]) -> List[str]:
    """
    Converts PlantUML documents into XML.

    Args:
        files: List of paths to PlantUML documents.

    Returns:
        List of paths to the generated XML documents.
    """
    xml_files = []

    for file in files:
        xml_files.append(file.replace('.puml', '.xmi'))

        if not os.path.exists(xml_files[-1]):
            script_dir = os.path.dirname(os.path.abspath(__file__))
            plantuml_path = os.path.join(script_dir, 'plantuml.jar')
            subprocess.run(['java', '-jar', plantuml_path, '-txmi', file])

    return xml_files


def comp_puml_metrics(file1: str, file2: str) -> Tuple[float, ...]:
    """
    Computes differencing metrics between two PlantUML documents.

    Args:
        file1: Path to first PlantUML document, considered the ground truth.
        file2: Path to second PlantUML document, considered the model output.

    Returns:
        Edit distance, true positives, false positives, false negatives,
        precision, recall, and F1 score.
    """
    try:
        xml1, xml2 = map(ET.parse, puml_to_xml([file1, file2]))
        zss1, zss2 = map(xml_to_zss, [xml1.getroot(), xml2.getroot()])
        dist, ops = simple_distance(zss1, zss2, return_operations=True)

        tp = sum(1 for op in ops if op.type == Operation.match)
        fp = sum(1 for op in ops if op.type in [Operation.insert, Operation.update])
        fn = sum(1 for op in ops if op.type in [Operation.remove, Operation.update])
        prec = tp / (tp + fp)
        recall = tp / (tp + fn)
        f1 = 2 * prec * recall / (prec + recall)

    except:
        dist = tp = fp = fn = prec = recall = f1 = float('nan')

    return dist, tp, fp, fn, prec, recall, f1
