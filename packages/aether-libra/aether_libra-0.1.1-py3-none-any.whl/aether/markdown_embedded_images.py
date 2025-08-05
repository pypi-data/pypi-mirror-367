# import re
# import base64
# from pathlib import Path


# def convert_md_with_embedded_images(md_path: str) -> str:
#     """
#     Markdownファイル内の画像リンクをbase64に埋め込み変換したMarkdown文字列を返す。

#     Parameters:
#     - md_path: 埋め込み処理をしたいMarkdownファイルのパス

#     Returns:
#     - base64埋め込み画像に置換されたMarkdown文字列

#     Example:
#     >>> md = convert_md_with_embedded_images("docs/guide.md")
#     >>> print(md[:200])
#     """
#     md_path = Path(md_path)
#     base_dir = md_path.parent
#     md_text = md_path.read_text(encoding="utf-8")

#     pattern = re.compile(r'!\[(.*?)\]\((.*?)\)')

#     def replace_func(match):
#         alt_text, img_path = match.groups()
#         full_path = base_dir / img_path

#         if not full_path.exists():
#             return f"**[画像が見つかりません: {img_path}]**"

#         ext = full_path.suffix.lower().lstrip('.')
#         mime = f"image/{'jpeg' if ext in ('jpg', 'jpeg') else ext}"
#         img_base64 = base64.b64encode(full_path.read_bytes()).decode()
#         return f'![{alt_text}](data:{mime};base64,{img_base64})'

#     return pattern.sub(replace_func, md_text)


import re
import base64
from pathlib import Path
from PIL import Image
from io import BytesIO

def convert_md_with_embedded_images(md_path: str, resize_width: int | None = 1440) -> str:
    """
    Markdownファイル内の画像リンクをbase64に埋め込み変換したMarkdown文字列を返す。
    オプションで画像の幅をリサイズすることも可能。

    Parameters:
    - md_path: 埋め込み処理をしたいMarkdownファイルのパス
    - resize_width: 画像のリサイズ後の横幅（ピクセル単位）。Noneならリサイズしない。

    Returns:
    - base64埋め込み画像に置換されたMarkdown文字列

    Example:
    >>> md = convert_md_with_embedded_images("docs/guide.md", resize_width=600)
    >>> print(md[:200])
    """
    md_path = Path(md_path)
    base_dir = md_path.parent
    md_text = md_path.read_text(encoding="utf-8")

    pattern = re.compile(r'!\[(.*?)\]\((.*?)\)')

    def replace_func(match):
        alt_text, img_path = match.groups()
        full_path = base_dir / img_path

        if not full_path.exists():
            return f"**[画像が見つかりません: {img_path}]**"

        ext = full_path.suffix.lower().lstrip('.')
        mime = f"image/{'jpeg' if ext in ('jpg', 'jpeg') else ext}"

        # リサイズ処理（PIL使用）
        if resize_width is not None:
            with Image.open(full_path) as img:
                aspect = img.height / img.width
                resized = img.resize((resize_width, int(resize_width * aspect)))
                buffer = BytesIO()
                resized.save(buffer, format=img.format or "PNG")
                img_bytes = buffer.getvalue()
        else:
            img_bytes = full_path.read_bytes()

        img_base64 = base64.b64encode(img_bytes).decode()
        return f'![{alt_text}](data:{mime};base64,{img_base64})'

    return pattern.sub(replace_func, md_text)
