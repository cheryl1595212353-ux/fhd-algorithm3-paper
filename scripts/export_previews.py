"""Export the full PDF and a page-exact numerical/appendix excerpt."""
import hashlib
import json
import shutil
from pathlib import Path
from pypdf import PdfReader, PdfWriter

ROOT = Path(__file__).resolve().parents[1]


def flatten(outline):
    for item in outline:
        if isinstance(item, list):
            yield from flatten(item)
        else:
            yield item


def main():
    source = ROOT / "build/main.pdf"
    reader = PdfReader(source)
    titles = {str(d.title).strip(): reader.get_destination_page_number(d) for d in flatten(reader.outline)}
    start = titles["Numerical experiments"]
    heading = "Declaration of Generative AI and AI-Assisted Technologies"
    ends = []
    for i in range(start, len(reader.pages)):
        lines = reader.pages[i].extract_text().splitlines()
        if lines and lines[0].startswith("Scalar-potential"):
            lines = lines[1:]  # Discard this manuscript's running page header.
        text = " ".join(" ".join(lines).split())
        if heading in text:
            ends.append(i - 1 if text.startswith(heading) else i)
    if not ends:
        raise ValueError("Cannot locate the end of the numerical/appendix excerpt")
    # If a declaration shares the final appendix page, retain that whole page.
    end = min(ends)
    if not 0 <= start <= end < len(reader.pages):
        raise ValueError("Invalid numerical section bounds")
    output = ROOT / "previews"
    output.mkdir(exist_ok=True)
    shutil.copy2(source, output / "manuscript.pdf")
    writer = PdfWriter()
    for i in range(start, end + 1):
        writer.add_page(reader.pages[i])
    writer.add_metadata({"/Title": "Numerical experiments and absolute-error appendix (excerpt)",
                         "/Subject": "Page-exact excerpt from the complete manuscript; original page numbers retained"})
    with (output / "numerical_experiments.pdf").open("wb") as stream:
        writer.write(stream)
    report = {"full_pages": len(reader.pages), "excerpt_pages": end - start + 1,
              "source_pages_one_based": list(range(start + 1, end + 2)),
              "method": "Extract unchanged pages from the compiled full manuscript; no second TeX source",
              "note": "Bounds use the numerical-section bookmark and declaration heading; original numbering and cross-references are retained.",
              "main_tex_sha256": hashlib.sha256((ROOT / "main.tex").read_bytes()).hexdigest(),
              "manuscript_sha256": hashlib.sha256(source.read_bytes()).hexdigest()}
    (output / "provenance.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
