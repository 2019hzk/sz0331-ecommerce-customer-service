from pathlib import  Path

def load_prompt_template_content(template_file_stem: str) -> str:
    prompt_template_file_path =Path(__file__).resolve().parents[0]/ "jinja2"/f"{template_file_stem}.jinja2"

    return  prompt_template_file_path.read_text(encoding="utf-8")
