from pathlib import Path

from pdf_oxide import PdfDocument


def extract_pdf_text(pdf_path: Path) -> str:
	doc = PdfDocument(str(pdf_path))

	page_count = getattr(doc, "page_count", None)
	if callable(page_count):
		try:
			page_count = page_count()
		except Exception:
			page_count = None

	pages_text = []
	if isinstance(page_count, int) and page_count > 0:
		for page in range(1, page_count + 1):
			try:
				pages_text.append(doc.extract_text(page) or "")
			except Exception as exc:
				print(f"Warning: failed to extract page {page} in {pdf_path}: {exc}")
		if pages_text:
			return "\n\n".join(pages_text).strip()

	# 兼容没有 page_count 的情况：遇到异常时停止。
	max_pages = 10000
	for page in range(1, max_pages + 1):
		try:
			pages_text.append(doc.extract_text(page) or "")
		except Exception:
			break

	return "\n\n".join(pages_text).strip()


def main() -> None:
	project_root = Path(__file__).resolve().parent.parent
	input_dir = project_root / "out"
	output_dir = project_root / "out_md"

	output_dir.mkdir(parents=True, exist_ok=True)

	pdf_files = [p for p in input_dir.rglob("*") if p.is_file() and p.suffix.lower() == ".pdf"]
	if not pdf_files:
		print(f"No PDF files found in: {input_dir}")
		return

	for pdf_file in sorted(pdf_files):
		relative_path = pdf_file.relative_to(input_dir)
		md_file = (output_dir / relative_path).with_suffix(".md")
		md_file.parent.mkdir(parents=True, exist_ok=True)

		try:
			text = extract_pdf_text(pdf_file)
			md_file.write_text(text, encoding="utf-8")
			print(f"Extracted: {pdf_file} -> {md_file}")
		except Exception as exc:
			print(f"Failed: {pdf_file} ({exc})")


if __name__ == "__main__":
	main()