#!/usr/bin/python3

import re
import sys, json, subprocess, io, os
from lxml import etree

def serialize_pdf(i, fn):
    boxes = []
    text = []
    textlength = 0
    for run in pdf_to_bboxes(i, fn):
        normalized_text = run["text"]

        # Ensure that each run ends with a space, since pdftotext
        # strips spaces between words. If we do a word-by-word diff,
        # that would be important.
        normalized_text = normalized_text.strip() + " "

        run["text"] = normalized_text
        run["startIndex"] = textlength
        run["textLength"] = len(normalized_text)
        boxes.append(run)
        text.append(normalized_text)
        textlength += len(normalized_text)

    text = "".join(text)
    return boxes, text

def pdf_to_bboxes(pdf_index, fn):
    # Get the bounding boxes of text runs in the PDF.
    # Each text run is returned as a dict.
    box_index = 0
    pdfdict = {
        "index": pdf_index,
        "file": fn,
    }
    xml = subprocess.check_output(["pdftotext", "-bbox", fn, "/dev/stdout"])
    dom = etree.fromstring(xml)
    for i, page in enumerate(dom.findall(".//{http://www.w3.org/1999/xhtml}page")):
        pagedict = {
            "number": i+1,
            "width": float(page.get("width")),
            "height": float(page.get("height"))
        }
        for word in page.findall("{http://www.w3.org/1999/xhtml}word"):
            yield {
                "index": box_index,
                "pdf": pdfdict,
                "page": pagedict,
                "x": float(word.get("xMin")),
                "y": float(word.get("yMin")),
                "width": float(word.get("xMax"))-float(word.get("xMin")),
                "height": float(word.get("yMax"))-float(word.get("yMin")),
                "text": word.text,
                }
            box_index += 1

print(serialize_pdf(0,sys.argv[1])[-1])