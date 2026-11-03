# 数据字段

`species.json` 是维护入口；`species.csv` 由构建脚本自动导出。当前 schemaVersion 为 1。

| 字段 | 含义 |
| --- | --- |
| `id` | 本库标识，使用学名加下划线。不是全球分类数据库 ID |
| `number` | 本批展示序号 |
| `commonNameZh` / `commonNameEn` | 水族中文常用名、英文名 |
| `scientificName` / `family` | 参考来源使用的学名、科名 |
| `synonyms` | 来源记录的其他写法（如有） |
| `caption` | 贴纸的主要外观特征短句 |
| `depiction` | 插画所表现的阶段、性别、姿态等；不是经验证的物种数据库 |
| `sticker.file` | 相对于仓库根目录的 PNG 路径 |
| `sticker.width` / `height` / `transparent` | 文件规格 |
| `sticker.license` | 生成贴纸的发布许可 |
| `sticker.reviewStatus` / `reviewNotes` | 实际审核范围与限制，无数值质量评分 |
| `references[]` | 参考照片路径、原页面、作者、许可和观察记录链接 |
| `verificationSources[]` | 额外核对的形态资料（如有） |

不包含饲养参数、分布范围或保护等级。中文名称不能替代学名；当前分类未系统对照最新名录。页面各鱼大小按版式排布，不代表真实体长。

第三方照片许可：9 张 CC BY 4.0、1 张 CC0 1.0。字段 `references[].license` 只对应照片；贴纸的许可在 `sticker.license` 中。
