from pathlib import Path
from dataclasses import dataclass, field
from weasyprint import HTML, CSS
from jinja2 import Environment, FileSystemLoader


def convert_to_html(input: str | list):
	"""
	Convert te input recursively to an HTML.
	if the format is `str` it is assumed it is HTML.
	"""
	if isinstance(input, str):
		return(input)
	
	res = ""
	for x in input:
		if isinstance(x, str):
			res += x
		else:
			res += x.to_html()
	return(res)

class Box:
	def __init__(self, title: str = "", body: list | None = None):
		self.title = title
		self.body = list(body) if body is None else body			

	def to_context(self) -> dict:
		"""
		Return a dict with the jinja suitable context
		"""
		return dict(
			title = self.title,
			type = "box",
			body = convert_to_html(self.body)
		)

class Column:
	def __init__(self, content, colspan: int = 1):
		self.colspan = colspan
		self.content = list(content)

	def to_context(self) -> dict:
		return dict(
			colspan = self.colspan,
			content = [x.to_context() for x in self.content]
		)

class Paragraph:
	def __init__(self, body: list | str):
		self.body = body

	def to_html(self) -> str:
		return f"<p>{convert_to_html(self.body)}</p>"
	
class Bulletpoint:
	"""A bullet point with orange triangle"""
	def __init__(self, body: str):
		self.body = body

	def to_html(self) -> str:
		return f"""<span class = "tri-mark">▲</span> {convert_to_html(self.body)} <br>"""

class Poster:
	def __init__(self):
		self.html = None

	def expand_content(self, context: dict) -> dict:
		"""
		Content could be coming in a mix of raw HTML/Box/other types.
		For jinja it needs to be converted to HTML.
		"""
		converted_content = {
			"title": context['title'],
			"author_groups": context["author_groups"],
			"content": {
				"rows": []
			}
			
		}

		for i, row in enumerate(context['content']['rows']):
			columns_context = {
				"columns": []
			}
			for column in row['columns']:
				column_context = column.to_context()
				columns_context["columns"].append(column_context)

			converted_content["content"]["rows"].append(columns_context)
		
		return converted_content


	def render(self, template_file: str | Path, context: dict):
		template_file = Path(template_file)

		self.template_dir = template_file.resolve().parent
		template_name = template_file.name

		print(f"template name = {template_name}")
		print(f"path to template = {self.template_dir}")

		env = Environment(
			loader = FileSystemLoader(self.template_dir),
			autoescape = True,
		)

		template = env.get_template(template_name)

		converted_context = self.expand_content(context)

		print(f"context original = {context}")

		print(f"context converted ti HTML = {converted_context}")
		self.html = template.render(**converted_context)

	def generate_pdf(self, output_file: str | Path, style: str | Path):
		out = Path(output_file)
		style = Path(style)

		HTML(
			string = self.html,
			base_url = self.template_dir
		).write_pdf(out, stylesheets = [CSS(filename = style)])