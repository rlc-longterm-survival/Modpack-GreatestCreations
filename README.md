# GreatestCreations-Twenty

> 🌐 **简体中文** · Translations coming s∞n™

自用水槽包，和 RLC3 有不小的关系（但没有继承 RLC3 的工业科技部分）。主要要素：

- [原 版 内 容 及其附属](./mods-sorted/topic/create/)
- [Hex Casting 半家桶](./mods-sorted/topic/hexcasting/)
- [Valkyrien Skies 以及机械动力风格的相关游戏内容](./mods-sorted/topic/valkyrien/)
- [美食和更多美食](./mods-sorted/topic/delights/)
- [小科技](./mods-sorted/topic/muggle/)
  - [集成电路](./mods-sorted/topic/muggle/integrated-circuit.pw.toml)
  - [Supplementaries](./mods-sorted/topic/muggle/supplementaries.pw.toml)
  - [这不比箱子好用](./mods-sorted/topic/muggle/sophisticated-backpacks.pw.toml)
  - [抽屉仙人](./mods-sorted/topic/muggle/storagedrawers.pw.toml)
- [好卡，谁在跑图](./mods-sorted/worldgen/)
- [优化越多，优化越少](./mods-sorted/optim/)

## 构建说明

### 系统要求

- 需要[特供版 Packwiz](https://github.com/rlc-longterm-survival/packwiz)。
  - 如果不需要使用 Packwiz 自动寻找合适模组版本/自动更新的特性，使用[原版 Packwiz](https://packwiz.infra.link/) 也能正常导出或安装此包。
  - 若执意使用原版 Packwiz，不得在未手动核实最新版本号的情况下使用其自动选择模组版本和自动更新模组的功能。原版中的 bug 可能导致其静默使用某旧版本而非最新版本，并且无法将 Fabric 模组识别为符合版本要求的模组。特供版修复了这些问题。

- 需要系统支持原生符号链接。
  - 类 UNIX 系统通常无须额外操作。Windows 须在设置中开启“开发人员模式”，并确保在 NTFS、ReFS 等现代文件系统上工作。

### 模组增删、伺服与打包

为保持仓库整洁，文件存在预处理流程。必须先由与处理流程生成衍生文件，才能交由 Packwiz 进一步处理。推荐使用快捷命令无感完成这些操作。

使用快捷命令需要类 Bash 终端。Windows 上可以使用 Git Bash。首先执行：

```bash
source build/envsetup.sh
```

然后使用快捷命令：

- `refresh`：手动增删、编辑、移动文件后刷新衍生文件及索引。代替 `packwiz refresh`。
  - 如果确信修改不影响衍生文件，也可直接使用 `packwiz refresh`。

- `build`：导出 Modrinth 格式整合包，构建产物在 `dist/` 中。代替 `packwiz modrinth export`。

- `serve`：伺服，即启动本地服务端提供整合包文件，以便通过 packwiz-installer 进行安装。代替 `packwiz serve`。
  - 可使用 `PORT`（大写）环境变量覆盖默认端口号。

- `addmod <platform> <specifier> <path>`：添加模组（只能添加模组，而非其他类型内容），并在添加后归入 `mods-sorted` 中指定子文件夹。代替 `packwiz <platform> add <specifier>`（只会将模组添加到 `mods`，不会归入 `mods-sorted` 中）。
  - `<platform>`：模组下载平台，`curseforge` (`cf`) 或 `modrinth` (`mr`)。
  - `<specifier>`：模组标识符，可以是名称（搜索）、slug、版本 ID、描述页 URL 或者版本页 URL。
  - `<path>`：归入的子文件夹路径（可以是多层路径）。可以以 `mods-sorted/` 开头（为了方便自动补全；这个前缀会在处理时自动去除）也可以不。指定子文件夹必须存在，除非子文件夹路径开头添加 `+` 字符。
  - 如果该命令没有导致 `mods` 中出现新文件，只是更新了已有文件，则该文件保持原有位置，`<path>` 参数无影响；如果由于安装依赖新增了多个文件，所有新增文件都归入 `<path>` 指定文件夹。

- `resortmod <path>`：将 `mods` 中的所有未归类新文件归入 `mods-sorted` 的指定子文件夹中。
  - 主要用于 `addmod` 最后一步归类失败的情况（例如由于子文件夹路径打错）。

- `rmmod <slug>`：移除指定模组（只能处理模组，而非其他类型内容），一并删除其在 `mods-sorted` 中的源文件。代替 `packwiz remove <slug>`。

所有快捷命令执行操作前都会先自动进行必要的衍生文件生成。

与 `mods` 中内容增删与整包校验/导出无关的操作（如模组更新、资源包安装），仍应使用原 Packwiz 命令进行。

> [!TIP]
>
> 如果 `mods` 中有非符号链接文件（说明是尚未归入 `mods-sorted` 文件夹的模组文件），命令在试图更新 `mods` 文件夹时会发出警告，且不会删除这些文件。应当尽快将它们正确归类。

<details>
<summary>不使用快捷命令</summary>

如果不想使用快捷命令，在直接交由 Packwiz 执行各种操作前，需要确保相关衍生文件为最新状态：

- `mods` 文件夹：仓库中的 `mods-sorted` 文件夹是分子文件夹整理的。由于 MC 1.20.1 没有可靠的机制可以加载子文件夹中的模组（尤其是 Fabric 模组），需要先将 `mods-sorted` 中的文件展平到 `mods` 中。
  - `python build/toolkit.py flatten mods`
  - 命令会以相对路径符号链接的形式将文件平展到 `mods` 中。编辑 `mods` 中的文件“映像”会一并修改 `mods-sorted` 中的源文件。

- `config/customwindowtitle-client.toml`：游戏窗口标题根据 `pack.toml` 中的整合包名称与版本号生成。
  - `python build/toolkit.py write-config`

确保衍生文件为最新状态后，即可使用 Packwiz 命令进行导出、伺服、模组增删等操作。模组增删后，需要执行操作维护 `mods-sorted` 文件夹：

- 增加模组：`python build/toolkit.py sort mods [-c] <path>`
  - 添加 `-c` 参数以允许创建不存在的子文件夹。
  - `mods` 中所有未分类的新文件都将归入指定子文件夹。如果希望将不同文件归入不同文件夹，可手动移动文件进行归类，然后执行 `python build/toolkit.py flatten mods` 维护 `mods` 的状态。

- 删除模组：`python build/toolkit.py dangerously-prune mods`
  - 危险！只允许在依次执行 `flatten mods` 和 `packwiz remove` 之后使用，其他场合切勿使用！
  - 会列出待删除的文件，需要手动确认。

手动增删、编辑、移动文件后，要保证整合包状态正确维护，须依次执行：

- `python build/toolkit.py flatten mods`
- `python build/toolkit.py write-config`
- `packwiz refresh`

导出整合包时，宜将输出路径设置到 `dist` 文件夹中，以免之后误将导出的 zip 文件检入 Git 中。

> [!CAUTION]
>
> `mods-sorted` 是模组列表的唯一真实数据来源，`mods` 文件夹是衍生文件，并且是 gitignore 的。整合包发布、Git 推送前，`mods` 文件夹中不应该留有任何非符号链接的内容。同样地，删除 `mods` 中的模组，须确保 `mods-sorted` 中的源文件也被删除。
</details>

### `mods-sorted` 文件夹的额外说明

- `mods-sorted` 是 packwizignore 的。只有衍生的 `mods` 会出现在整合包里。
- `mods-sorted` 中只有文件和文件型符号链接会被链接到 `mods` 中。
- `mods-sorted` 文件夹自身之下也可以放文件，不一定要在子文件夹下。要将模组归入 `mods-sorted` 自身中，`<path>` 参数可以是 `.`。
- `mods-sorted` 中，名称以 `.` 开头或以 `.disabled` 结尾的文件/文件夹及其子树，不会被链接到 `mods` 中，也不会被自动删除。
