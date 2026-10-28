Wubi 86 / 98 / 06 + Rime Ice / 五笔三版本与雾凇拼音
SPDX-License-Identifier: CC0-1.0

首次安装请先看 START-HERE.txt：从主程序、Rime插件、Python打包导入，到候选字体和正常输入。
浏览器与打印版：INSTALL-GUIDE.html。完整手工组装仍见 MANUAL-INSTALL.txt。
New users: START-HERE.txt covers app/plugin installation through candidate-font setup.
INSTALL-GUIDE.html is the browser/print edition of that complete guide.

无需Python的完整手动步骤：MANUAL-INSTALL.txt。
No-Python installation: MANUAL-INSTALL.txt.
手动来源记录模板：manual/UPSTREAM-SOURCE.txt。

四个方案同时安装，在同一Rime原生菜单并列选择：
  新世纪五笔   schema_id: wubi06
  五笔86      schema_id: wubi86
  五笔98      schema_id: wubi98
  雾凇拼音    schema_id: rime_ice

五笔保留原有拼音反查、拆分注释、简繁、Emoji、单字模式、快符、日期、时间、
农历和计算器等功能，三版使用独立码表、拆分库和学习词库。
雾凇保留上游全拼、英文与中英混输、拆字反查、简繁、Emoji及Lua工具。
本配置仅增加全拼方案，不安装雾凇的双拼、九键或桌面外观。
新世纪方案名称与schema_id保持原样，现有app的06字根图片提示继续识别它。
86、98、雾凇不显示06图片。主程序和Rime插件无需修改或重新编译。

Python快速安装（Windows -> Android）

1. 自行下载两个项目的完整ZIP，各自解压，先不要将整包互相覆盖：
     五笔：https://github.com/myshiqiqi/rime-wubi/tree/master
     雾凇：https://github.com/iDvel/rime-ice
   两个项目均选择 Code -> Download ZIP。复现已检查的雾凇快照也可下载：
     https://github.com/iDvel/rime-ice/archive/da1fbe602e38f26db846fa10120ee64c2b0324c0.zip
   固定快照解压后的文件夹带提交编号，运行时改成这个实际目录即可。
   使用默认分支ZIP时通常得到：
     D:\Downloads\rime-wubi-master
     D:\Downloads\rime-ice-main
   五笔目录应有wubi.schema.yaml和tables/86、98、06；雾凇目录应有
   rime_ice.schema.yaml、rime_ice.dict.yaml、cn_dicts、en_dicts和lua。

2. 解压本配置包，保留make_android_import.py、rime、lua、说明文件的相对位置。
   安装Python 3，在本包目录打开PowerShell，运行一整行（修改实际路径）：
     py -3 .\make_android_import.py --upstream "D:\Downloads\rime-wubi-master" --ice-upstream "D:\Downloads\rime-ice-main"
   没有py命令时，可用python代替py -3。两个上游目录参数都需要。

3. 会生成wubi-and-ice-android.zip。传到手机，在Fcitx5 Android的
   “高级 -> 导入用户数据”导入。重启输入法，执行Rime Deploy / 部署，
   再重启输入法，使五笔Lua的方案菜单读取最新列表。
   雾凇完整词库较大，包含上游默认启用的腾讯词库，首次部署需要更长时间。
   请等待部署结束；不需要自行运行雾凇的词库构建脚本。

4. 键盘工具栏“更多”（⋮）-> 当前Rime方案项 -> 在原生子菜单点选
   “新世纪五笔”“五笔86”“五笔98”或“雾凇拼音”。
   四个都是同级输入方案；五笔中的z+拼音反查仍只是五笔的辅助功能。

本工具完全离线，只读取用户已下载的资源，不联网，也不执行上游Python/Lua。
上游Lua在输入法加载相应方案时由Rime正常运行。

如何共存

不要把两个上游整包直接互相覆盖。五笔与雾凇都有default.yaml，但内容不同。
工具保留五笔default.yaml，把雾凇原件复制为ice_defaults.yaml（内容不变），
再用本包custom补丁让雾凇及其辅助方案读取自己的默认配置。五笔rime.lua保留，
双方所需lua与opencc文件合并，不会用空文件夹覆盖已复制的资源。

为了使五笔三版共存，工具在用户本地生成九个独立词库，仅修改头部的name
及扩展词库import_tables标识。原始注释、作者信息和词条正文保留。
雾凇的词库、Lua、OpenCC、二进制lua/lunar.db等选定资源保持字节原样。
雾凇默认半角与中文模式，Shift不取消正在组合的字母，Enter提交原始字母。

打开菜单与常用功能

共同操作：
- 触屏：键盘工具栏“更多”（⋮）-> 当前Rime方案项 -> 点选目标方案。
- 实体键盘：F4、Ctrl+`、Ctrl+Shift+`打开Rime原生方案菜单。
- Enter提交当前原始字母，默认半角。简繁、Emoji等可从Rime选项菜单切换。

五笔06/86/98：
- 拼音反查：z后接拼音，例如znihao，再选择候选。
- 显示拆分：Rime选项菜单“显示拆分”；上游快捷键Ctrl+Shift+H。
- 简繁：菜单或Ctrl+Shift+F；单字：菜单或Ctrl+Shift+D。
- 日期/时间：date、time、week；农历/节气按上游说明nl、jq。
- 计算器：=1+2；帮助：help。
- mode后按数字键1/2/3/4切换方案；next后按数字键选功能。
  这两个上游文本命令依赖数字按键，点候选文字可能会将标签作为文字上屏。
  触屏切换请使用原生Rime菜单。

雾凇拼音（全拼）：
- 直接输入nihao，候选应出现“你好”；可使用上游简拼、英文和中英混输。
- 日期rq，时间sj，星期xq，农历nl。
- 计算器前缀cC，例如cC1+2；与五笔的=前缀不同。
- 拆字反查前缀uU，后接部件拼音；不要使用五笔的z反查前缀。
- 简繁与Emoji使用雾凇自己的选项；[和]可取当前候选首字或末字。
- 其他功能及设置见自行下载的上游说明。

五笔拆分注释可能需要专用字形。若出现方块，可自行从五笔上游font目录取得
“黑体字根.ttf”，用现有app的字体导入功能应用到候选文字。本包和生成的导入ZIP
均不包含字体。06字根图片提示直接使用app现有图片，不依赖此字体。

直接复制文件或用WinRAR更新私人导出ZIP

需要准备目录时，选择一个不存在的新目录：
  py -3 .\make_android_import.py --upstream "D:\Downloads\rime-wubi-master" --ice-upstream "D:\Downloads\rime-ice-main" --prepare "D:\Downloads\wubi-and-ice-rime"

将生成目录的内容放到Android用户目录data/rime，保留lua、opencc、cn_dicts、
en_dicts、source-info等子目录，不要多套一层wubi-and-ice-rime文件夹。

目录权限受限时，用WinRAR打开自己的有效Fcitx5导出ZIP的工作副本，将准备内容
加入external/data/rime/，替换同名文件。保留metadata.json、其他备份目录、
UTF-8文件名和父目录记录，保持ZIP格式。无需修改额外应用校验清单。
完整无Python的复制路径、九个词库重命名与十二处头部编辑见MANUAL-INSTALL.txt。

导入只合并、覆盖，不删除手机已有文件。想要干净Rime目录，先保存私人备份和
个性配置，再单独清理手机data/rime；app设置、主题、字体等不需要清理。
本包覆盖五笔与雾凇对应的custom补丁，旧个性设置请安装后逐项合并。
用户数据导出可能含剪贴板、历史及个人词库，请勿公开分享。

资源、署名与许可

本公开包只含新写的15份YAML、两个Lua兼容适配器、离线helper、手动指南和
CC0-1.0许可。没有附带上游词库、拆分表、上游Lua、OpenCC数据、字体、图片、
引擎或app。两个适配器处理五笔未完成算式与无效候选编号的运行错误，保留正常功能。

用户下载的上游代码与数据保留原作者权利，不属于本包CC0声明范围。
五笔参考快照没有明确LICENSE，分发含其资源的成品前请向来源核实授权。
雾凇项目声明GPL-3.0-only，并含不同来源和条款的组件，详见上游LICENSE与
others/docs/Credits.md；工具将这两份说明保存在source-info/rime-ice/。
UPSTREAM-SOURCE.txt记录双方来源、所选路径、源/输出摘要及本地变更。
手动方法使用本包manual/UPSTREAM-SOURCE.txt模板，无需计算摘要。
本地改配置或下载资源不会使第三方数据变成“无版权”或重新授权为CC0。
Rime、Fcitx5 Android、插件和现有字根图片的许可与权利保持原状。

English quick start

Download and extract both upstream ZIPs yourself, into separate folders:
  https://github.com/myshiqiqi/rime-wubi/tree/master
  https://github.com/iDvel/rime-ice
Extract this overlay kit separately and install Python 3. In the kit folder run:
  py -3 .\make_android_import.py --upstream "D:\Downloads\rime-wubi-master" --ice-upstream "D:\Downloads\rime-ice-main"
Import wubi-and-ice-android.zip on Android, restart, run Rime Deploy, then restart
again. Ice's full dictionaries take longer to deploy. Use toolbar More -> current
Rime scheme -> native submenu to select Wubi06 / Wubi86 / Wubi98 / Rime Ice.
F4 or Ctrl+grave opens the native menu on a physical keyboard.

The existing Wubi06 schema ID/name and app image hints are preserved. Ice appears
as a full-Pinyin sibling; this kit does not add its double-Pinyin or T9 schemes.
No app or plugin changes/rebuilds are needed. Both upstream defaults coexist under
separate filenames. The helper is offline and never executes downloaded code.

In Ice, nihao should offer 你好; rq/sj/nl trigger date/time/lunar, cC1+2 invokes its
calculator, and uU is the radical-lookup prefix. In Wubi, znihao is Pinyin reverse
lookup, =1+2 invokes the calculator, and date/time/week are utility keywords.
Enter commits raw narrow letters. Wubi's typed mode/next commands need numeric-key
selection; use the native Rime menu for touch selection.

--prepare "NEW_FOLDER" creates a directory (plus four kit reference documents)
for direct copying or adding to your private export's external/data/rime/ path. Import merges, never deletes existing
phone files. Back up customizations. See MANUAL-INSTALL.txt for every no-Python
file operation and header edit, including a WinRAR import walkthrough.

Only this kit's own configuration/helper/guards/docs are CC0. Users obtain all
third-party data and code themselves; original attribution/rights remain.
Ice declares GPL-3.0-only and includes components with other terms (see its LICENSE
and Credits.md). The checked Wubi snapshot has no explicit LICENSE. Check source
terms before sharing any assembled dictionary/code bundle. Keep personal backups
and user words private. The app, engine, plugin and existing image retain their
original licenses and rights.

参考快照 / Reference snapshots:
  myshiqiqi/rime-wubi e5c4bc88684d0c1549da393dd8ba845e48e66973
  iDvel/rime-ice da1fbe602e38f26db846fa10120ee64c2b0324c0

验证范围 / Validation scope:
已在Linux librime1.13.1 + Lua5.4中实际部署四个方案，验证雾凇拼音、英文、
原始Enter、日期、农历、计算器、拆字反查、Emoji、简繁、以词定字，以及原生
菜单/API触屏候选切换；五笔原有输入与工具功能回归通过，未出现Lua运行错误。
Android设备界面尚未实际测试，首次安装仍需确认手机上的菜单与输入行为。
Validated with Linux librime1.13.1 + Lua5.4: deployment of all four schemes;
Ice Pinyin, English, raw Enter, date/lunar, calculator, radical lookup, Emoji,
traditional conversion, character selection, native/API touch menu switching;
and Wubi regressions. No Lua runtime errors in these checks. Android device UI
remains untested.
