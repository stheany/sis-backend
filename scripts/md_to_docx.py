#!/usr/bin/env python3
"""
Small, purpose-built Markdown -> .docx converter for this repo's API spec
docs. Not a general CommonMark implementation — handles exactly the subset
used in docs/API_Specification_NCS_BKLV_SOAP.md: #/## headings, GFM pipe
tables, fenced code blocks, **bold**, `inline code`, and --- dividers.

Usage:
    python scripts/md_to_docx.py <input.md> <output.docx> [--title "Doc Title"]
"""
import argparse
import re

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
from docx.shared import Pt, RGBColor, Inches

CODE_FONT = 'Consolas'
BODY_FONT = 'Calibri'


def _set_cell_shading(cell, hex_color):
    shd = OxmlElement('w:shd')
    shd.set(qn('w:fill'), hex_color)
    cell._tc.get_or_add_tcPr().append(shd)


def _set_paragraph_shading(paragraph, hex_color):
    shd = OxmlElement('w:shd')
    shd.set(qn('w:fill'), hex_color)
    paragraph._p.get_or_add_pPr().append(shd)


def _add_inline_runs(paragraph, text):
    """Handle **bold** and `inline code` spans within one line of text."""
    token_re = re.compile(r'(\*\*.+?\*\*|`.+?`)')
    for part in token_re.split(text):
        if not part:
            continue
        if part.startswith('**') and part.endswith('**'):
            run = paragraph.add_run(part[2:-2])
            run.bold = True
        elif part.startswith('`') and part.endswith('`'):
            run = paragraph.add_run(part[1:-1])
            run.font.name = CODE_FONT
            run.font.size = Pt(9.5)
        else:
            paragraph.add_run(part)


def _add_code_block(doc, lines):
    table = doc.add_table(rows=1, cols=1)
    table.autofit = True
    cell = table.rows[0].cells[0]
    _set_cell_shading(cell, 'F2F2F2')
    cell.paragraphs[0].text = ''
    first = True
    for line in lines:
        p = cell.paragraphs[0] if first else cell.add_paragraph()
        first = False
        run = p.add_run(line if line else ' ')
        run.font.name = CODE_FONT
        run.font.size = Pt(8.5)
        p.paragraph_format.space_after = Pt(0)
    doc.add_paragraph()


def _add_table(doc, header, rows):
    table = doc.add_table(rows=1, cols=len(header))
    table.style = 'Light Grid Accent 1'
    for i, h in enumerate(header):
        cell = table.rows[0].cells[i]
        cell.text = ''
        _add_inline_runs(cell.paragraphs[0], h)
        for run in cell.paragraphs[0].runs:
            run.bold = True
        _set_cell_shading(cell, 'DDEBF7')
    for row in rows:
        cells = table.add_row().cells
        for i, val in enumerate(row):
            cells[i].text = ''
            _add_inline_runs(cells[i].paragraphs[0], val)
    doc.add_paragraph()


def convert(md_path, docx_path, title=None):
    with open(md_path, encoding='utf-8') as f:
        lines = f.read().splitlines()

    doc = Document()
    style = doc.styles['Normal']
    style.font.name = BODY_FONT
    style.font.size = Pt(10.5)

    i = 0
    n = len(lines)
    while i < n:
        line = lines[i]

        if line.startswith('```'):
            i += 1
            block = []
            while i < n and not lines[i].startswith('```'):
                block.append(lines[i])
                i += 1
            i += 1  # skip closing fence
            _add_code_block(doc, block)
            continue

        if line.startswith('# '):
            h = doc.add_heading(line[2:].strip(), level=0)
            i += 1
            continue

        if line.startswith('## '):
            doc.add_heading(line[3:].strip(), level=1)
            i += 1
            continue

        if line.startswith('### '):
            doc.add_heading(line[4:].strip(), level=2)
            i += 1
            continue

        if line.strip() == '---':
            p = doc.add_paragraph()
            pPr = p._p.get_or_add_pPr()
            pBdr = OxmlElement('w:pBdr')
            bottom = OxmlElement('w:bottom')
            bottom.set(qn('w:val'), 'single')
            bottom.set(qn('w:sz'), '6')
            bottom.set(qn('w:space'), '1')
            bottom.set(qn('w:color'), 'AAAAAA')
            pBdr.append(bottom)
            pPr.append(pBdr)
            i += 1
            continue

        if line.startswith('|'):
            table_lines = []
            while i < n and lines[i].startswith('|'):
                table_lines.append(lines[i])
                i += 1
            header = [c.strip() for c in table_lines[0].strip('|').split('|')]
            body_rows = [
                [c.strip() for c in row.strip('|').split('|')]
                for row in table_lines[2:]
            ]
            _add_table(doc, header, body_rows)
            continue

        if line.strip() == '':
            i += 1
            continue

        # bold "label" lines, e.g. "**Version:** 1.0 · **Date:** ..."
        p = doc.add_paragraph()
        _add_inline_runs(p, line)
        i += 1

    doc.core_properties.title = title or 'API Specification'
    doc.save(docx_path)
    print(f'Wrote {docx_path}')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('input_md')
    parser.add_argument('output_docx')
    parser.add_argument('--title', default=None)
    args = parser.parse_args()
    convert(args.input_md, args.output_docx, args.title)
