#!/usr/bin/env python3
"""Build the static catalog and reproducible download using Python's standard library."""
import argparse
import csv
import hashlib
import html
import io
import json
from pathlib import Path
import struct
import zipfile

ROOT = Path(__file__).resolve().parents[1]
REPO = 'https://github.com/lanmaohu/marine-fish-stickers'
SITE = 'https://lanmaohu.github.io/marine-fish-stickers/'


def safe_file(relative):
    path = (ROOT / relative).resolve()
    if not path.is_relative_to(ROOT) or not path.is_file():
        raise ValueError(f'Missing or unsafe path: {relative}')
    return path


def build():
    data = json.loads((ROOT / 'data/species.json').read_text())
    fish = data['species']
    assert len(fish) == data['speciesCount']
    assert len({f['id'] for f in fish}) == len(fish), 'Duplicate fish ID'
    assert len({f['sticker']['file'] for f in fish}) == len(fish), 'Duplicate image'
    count, version = len(fish), data['version']
    archive_name = f'marine-fish-stickers-v{version}.zip'
    release = f'{REPO}/releases/download/v{version}/{archive_name}'
    cards, rows, sums = [], [], []
    credits = ['# 参考摄影与署名\n', '参考照片保留原文件与原许可；贴纸是改变姿态、背景和表现方式后的 AI 重绘。摄影师未参与审核，也不代表认可生成图。分发素材时请保留本文与许可链接。\n']
    table = io.StringIO(newline='')
    writer = csv.writer(table)
    writer.writerow(['id', '中文常用名', '英文名', '学名', '科', 'PNG路径', '贴纸许可', '参考照片', '摄影师', '照片许可', '审核说明'])
    for f in fish:
        sticker = f['sticker']
        path = safe_file(sticker['file'])
        header = path.read_bytes()[:33]
        assert header[:8] == b'\x89PNG\r\n\x1a\n', f'Not PNG: {path}'
        width, height, depth, color = struct.unpack('>IIBB', header[16:26])
        assert (width, height, depth, color) == (sticker['width'], sticker['height'], 8, 6), f'Unexpected PNG format: {path}'
        assert sticker['license'] == 'CC-BY-4.0'
        sums.append(f"{hashlib.sha256(path.read_bytes()).hexdigest()}  {sticker['file']}")
        for ref in f['references']:
            safe_file(ref['file'])
            assert all(ref.get(key) for key in ['author', 'page', 'license', 'licenseUrl'])
        ref = f['references'][0]
        esc = html.escape
        query = ' '.join([f['commonNameZh'], f['commonNameEn'], f['scientificName'], f['family']] + f.get('synonyms', []))
        cards.append(f'''<article class="card" data-name="{esc(f['commonNameZh'])}" data-search="{esc(query)}">
<div class="picture"><span class="number">{f['number']}</span><img class="fish" src="{sticker['file']}" alt="{esc(f['commonNameZh'])}贴纸" width="1254" height="1254" data-sticker="{sticker['file']}" data-reference="{ref['file']}"></div>
<div class="info"><h2>{esc(f['commonNameZh'])}</h2><p class="latin">{esc(f['scientificName'])}</p><p class="feature">{esc(f['caption'])}</p>
<div class="actions"><a class="single-download" href="{sticker['file']}" download>下载 PNG ↗</a><button class="compare" aria-pressed="false">看参考照片</button></div>
<p class="credit"><a href="{ref['page']}" target="_blank" rel="noopener">参考摄影：{esc(ref['author'])}</a> · <a href="{ref['licenseUrl']}" target="_blank" rel="noopener">{ref['license']}</a></p></div></article>''')
        rows.append(f"| {f['number']} | {f['commonNameZh']} | {f['commonNameEn']} | *{f['scientificName']}* | [{f['family']}]({sticker['file'].rsplit('/', 1)[0]}/) | [PNG]({sticker['file']}?raw=true) |")
        writer.writerow([f['id'], f['commonNameZh'], f['commonNameEn'], f['scientificName'], f['family'], sticker['file'], sticker['license'], ref['page'], ref['author'], ref['license'], sticker['reviewNotes']])
        credits.append(f"## {f['number']} {f['commonNameZh']} · *{f['scientificName']}*\n")
        for ref in f['references']:
            credits.append(f"- 摄影师：{ref['author']}\n- 原图：[iNaturalist 照片页面]({ref['page']}) · [观察记录]({ref['observation']})\n- 许可：[{ref['license']}]({ref['licenseUrl']})\n- 仓库参考图：[{Path(ref['file']).name}]({ref['file']})\n- 修改说明：参考照片文件未修改；贴纸经 AI 重新绘制，改变了姿态、背景与表现形式。\n")
    page = (ROOT / 'templates/gallery.html').read_text()
    for key, value in {'COUNT': str(count), 'PAD_COUNT': f'{count:02d}', 'VERSION': version, 'CARDS': '\n'.join(cards)}.items():
        page = page.replace('{{' + key + '}}', value)
    assert '{{' not in page, 'Unresolved template placeholder'
    readme = f'''# 海水鱼贴纸库 · Marine Fish Stickers

**{count} 种常见海水观赏鱼，一种一张白边透明贴纸。** 附中文常用名、英文名、学名、参考照片、摄影师署名和生成提示词。

[在线画廊]({SITE}) · [下载全部贴纸与资料（ZIP）]({release}) · [版本记录]({REPO}/releases) · [English](#english)

![首批海水鱼贴纸总览](previews/collection.png)

由 [lanmaohu](https://github.com/lanmaohu) 发布。贴纸采用 **[CC BY 4.0](LICENSE.md)**：署名后可商用、修改和分享。网页与构建代码采用 MIT；第三方照片保留各自许可，见 [CREDITS.md](CREDITS.md)。

## 预览与下载

- **看全部：** [打开在线画廊]({SITE})，可搜索中英文名、学名或科名，切换深浅背景，并对照真实参考照片。
- **下载一张：** 在在线画廊点击「下载 PNG」，或在下表打开原图保存。
- **下载整包：** [v{version} 素材包]({release})。下载包含 {count} 张 PNG、10 张参考照片、预览页、数据、提示词与署名许可，可离线浏览。
- **下载项目：** 使用 GitHub 的 Code → Download ZIP，或 `git clone {REPO}.git`。
- **校验：** [下载包 SHA-256](downloads/SHA256SUMS.txt) · [单张 PNG SHA-256](data/stickers.sha256)。

所有贴纸为 **1254 × 1254 像素 PNG，含真实透明通道**。画面为完整单鱼、侧身朝左、白色描边；展示尺寸不代表真实体长。

## 鱼种目录

| 编号 | 中文常用名 | English | 学名 | 科 | 原图 |
| --- | --- | --- | --- | --- | --- |
{chr(10).join(rows)}

## 文件结构

```text
stickers/<Family>/<Genus_species>.png  每种鱼的最终贴纸
previews/collection.png               九种鱼总览
references/                          10 张实际参考照片
data/species.json                     完整鱼种记录与来源
data/species.csv                      表格版本
data/stickers.sha256                  PNG 校验值
prompts/                             生成提示词与修正说明
downloads/                           可直接下载的素材包
index.html + assets/                  静态画廊
templates/ + scripts/build.py         画廊与下载包构建入口
CREDITS.md / NOTICE.md / LICENSE.md   来源、制作范围与许可
```

## 如何制作

1. 选择这批具有不同体形、色彩和花纹的海水观赏鱼，记录中英文名、学名及科名。
2. 从 iNaturalist 获取有明确许可的真实照片，逐图保留作者、原页面和许可链接。
3. 使用 Codex 内置 image_gen，参照照片逐种绘制，统一白边、透明底和朝向。
4. 对照参考做外观初检；泗水玫瑰清理了白边，麒麟鱼修正了错误的鳞片纹理。
5. 导出原始 PNG，整理成可搜索、可追溯的素材库。实际提示词保存在 [prompts/](prompts/)。

这些是 **AI 插画**。已检查整体轮廓和主要花纹，尚未经独立鱼类专家审定。分类名称按参考来源记录，未系统对照最新名录。细鳍条、体表细节和雌雄鉴别仍可能有误；不要将插画作为鉴定依据。完整范围见 [NOTICE.md](NOTICE.md)。

## 使用数据

字段说明见 [data/README.md](data/README.md)。例如：

```python
import json
from pathlib import Path

catalog = json.loads(Path('data/species.json').read_text(encoding='utf-8'))
by_name = {{fish['scientificName']: fish for fish in catalog['species']}}
print(by_name['Amphiprion ocellaris']['sticker']['file'])
```

文件也可以通过固定地址读取：

```text
https://raw.githubusercontent.com/lanmaohu/marine-fish-stickers/main/stickers/Pomacentridae/Amphiprion_ocellaris.png
```

## 本地浏览与维护

解压后直接打开 `index.html` 即可浏览。若要验证下载按钮，可在项目目录运行：

```bash
python3 -m http.server 8000
```

再打开 `http://localhost:8000`。仅使用 Python 标准库，无需安装网页框架。

修改 `data/species.json` 或网页模板后，运行：

```bash
python3 scripts/build.py
python3 scripts/build.py --check
```

脚本检查图片规格与引用文件，更新画廊、README、CSV、署名、下载包和校验值。新增鱼种还需更新总览图。贡献方式见 [CONTRIBUTING.md](CONTRIBUTING.md)。

## 署名与致谢

建议署名：**海水鱼贴纸：lanmaohu / marine-fish-stickers，CC BY 4.0。参考摄影师见 CREDITS.md；说明是否修改。** 请保留项目与许可链接。

参考摄影师逐图列于 [CREDITS.md](CREDITS.md)。仓库的组织方式受 [花叔鸟类贴纸库](https://github.com/alchaincyf/huashu-bird-sticker) 启发，本项目独立制作，未使用其图片、代码或物种数据。

发现鱼体、名称或署名问题，欢迎 [提交纠错]({REPO}/issues/new?template=correction.md)。

## English

{count} marine aquarium fish, one transparent white-outline PNG sticker per species. Each image is 1254 × 1254 px. The library includes Chinese and English names, scientific names, source photos, photographer credits, prompts, a searchable gallery, and a downloadable archive.

**Artwork: CC BY 4.0. Code: MIT. Reference photographs retain their own licenses.** The stickers are AI illustrations based on real photographs, visually checked but not independently reviewed by an ichthyologist. Display sizes are not to scale. See [credits](CREDITS.md), [license](LICENSE.md), and [production notes](NOTICE.md).
'''
    outputs = {
        'index.html': page.encode(),
        'README.md': readme.encode(),
        'CREDITS.md': '\n'.join(credits).encode(),
        'data/species.csv': ('\ufeff' + table.getvalue()).encode(),
        'data/stickers.sha256': ('\n'.join(sums) + '\n').encode(),
    }
    # Stable ordering and timestamps keep unchanged releases byte-for-byte reproducible.
    package_files = set(outputs)
    for path in ROOT.rglob('*'):
        relative = path.relative_to(ROOT)
        if path.is_file() and not any(part.startswith('.') or part in {'downloads', '__pycache__'} for part in relative.parts):
            package_files.add(relative.as_posix())
    archive = io.BytesIO()
    with zipfile.ZipFile(archive, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=6) as bundle:
        for relative in sorted(package_files):
            info = zipfile.ZipInfo(f'marine-fish-stickers/{relative}', (2026, 11, 3, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            bundle.writestr(info, outputs.get(relative) if relative in outputs else (ROOT / relative).read_bytes())
    content = archive.getvalue()
    outputs['downloads/' + archive_name] = content
    outputs['downloads/SHA256SUMS.txt'] = f'{hashlib.sha256(content).hexdigest()}  {archive_name}\n'.encode()
    return outputs, count


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true', help='Validate files and detect stale generated outputs without writing')
    args = parser.parse_args()
    outputs, count = build()
    stale = []
    for name, content in outputs.items():
        path = ROOT / name
        if args.check:
            if not path.is_file() or path.read_bytes() != content:
                stale.append(name)
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(content)
    if stale:
        raise SystemExit('Out of date; run python3 scripts/build.py: ' + ', '.join(stale))
    print(f'{"Verified" if args.check else "Built"}: {count} stickers; {len(outputs)} generated outputs.')
