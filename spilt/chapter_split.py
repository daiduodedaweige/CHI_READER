import os
import re
import fitz  # PyMuPDF


def is_target_title(title: str) -> bool:
    """
    只匹配下面三种目录标题前缀：
    - AX.X
    - BX.X
    - CX.X

    例如：
    A1.2 xxx        -> 匹配
    B3.4.5 xxx      -> 匹配
    C2.1 xxx        -> 匹配

    例如：
    A1.2.3 xxx      -> 不匹配
    B1.2.3.4 xxx    -> 不匹配
    C1.2.3 xxx      -> 不匹配
    """
    title = title.strip()

    patterns = [
        r"^A\d+\.\d+(?!\.)\b",       # A1.2
        r"^B\d+\.\d+(?!\.)\b",       # B1.2 
        r"^C\d+\.\d+(?!\.)\b",       # C1.2
    ]

    return any(re.match(pattern, title) for pattern in patterns)


def safe_filename(name: str) -> str:
    """
    清理文件名中的非法字符，避免保存失败
    """
    return re.sub(r'[\\/:*?"<>|]', "_", name).strip()


SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PARENT_DIR = os.path.dirname(SCRIPT_DIR)
OUT_DIR = os.path.join(PARENT_DIR, "out")

doc = fitz.open("IHI0050H_amba_chi_architecture_spec.pdf")
toc = doc.get_toc()  # [level, title, page]

# 只保留目标章节
target_toc = [(level, title, page) for level, title, page in toc if is_target_title(title)]

# 创建输出目录（脚本父级目录下的 out）
os.makedirs(OUT_DIR, exist_ok=True)

# 切分并导出
for i in range(len(target_toc)):
    _, title, start_page = target_toc[i]
    end_page = target_toc[i + 1][2] - 1 if i + 1 < len(target_toc) else doc.page_count

    new_doc = fitz.open()
    new_doc.insert_pdf(doc, from_page=start_page - 1, to_page=end_page - 1)

    output_path = os.path.join(OUT_DIR, f"{safe_filename(title)}.pdf")
    new_doc.save(output_path)
    new_doc.close()

doc.close()