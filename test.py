import requests, pathlib, json

pdf_path=pathlib.Path("data/pdf.pdf").resolve()

def parse_pdf(url="http://localhost:8000/parse"):
    with pdf_path.open("rb") as f:
        r = requests.post(
            url,
            files={"file": f},
            data={
                "dump_md": "true",
                "draw_layout": "true"
            },
            timeout=120
        )
    r.raise_for_status()
    print(r.json())

parse_pdf()