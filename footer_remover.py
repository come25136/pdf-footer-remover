import sys
import os
import fitz
from pathlib import Path

args = sys.argv

if (len(args) < 2):
    print("ファイルパスを指定してください")
    exit(1)

input_file = args[1]  # 処理するPDFのファイルパス

# PDF ファイルを開く
pdf_path = input_file
doc = fitz.open(pdf_path)

# 全ページを処理
for page_num in range(len(doc)):
    page = doc.load_page(page_num)

    # pymupdf v1.22.0 だとこれが呼ばれないので上手く動く(多分)
    # v.1.24.0+になると勝手に呼ばれるらしい
    # page.wrap_contents()

    text_page = page.get_textpage()

    # ページからテキストとその位置を抽出
    block = text_page.extractDICT()

    # 各テキストブロックを処理
    for block_in_blocks in block["blocks"]:
        for line in block_in_blocks["lines"]:
            for span in line["spans"]:
                if page.mediabox_size.x - 100 <= span["bbox"][0] and page.mediabox_size.y - 100 <= span["bbox"][3]:
                    if span["text"].isdigit():
                        print(
                            f"{page_num+1} ページ目で検出 x:{span["bbox"][0]} y:{page.mediabox_size.y - span["bbox"][3]}")
                        # page.add_freetext_annot(span["bbox"],text="unko", fill_color=[1,1,1])
                        page.add_redact_annot(span["bbox"])

    # https://stackoverflow.com/questions/72033672/delete-text-from-pdf-using-fitz
    page.apply_redactions()

output_file_path, _ = os.path.splitext(input_file)

# 新しいPDFを保存
output_path = f"{output_file_path}_removed.pdf"
file_path_obj = Path(output_path)
if not file_path_obj.exists():
    file_path_obj.touch()

doc.save(output_path)
doc.close()

print(f"編集されたPDFが {output_path} に保存されました。")
