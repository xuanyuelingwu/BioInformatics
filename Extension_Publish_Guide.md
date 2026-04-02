# 3D Slicer Extension 发布指南

**作者**: 鲁奥晗  
**学号**: 2023012411

---

## 1. 概述

要将插件发布到 3D Slicer 的 Extension Manager（扩展管理器）中，供全球用户直接搜索和一键安装，必须将其打包为符合官方规范的 **Extension**，并提交到 **Slicer Extensions Index** 仓库。

我已经为您将 `SurfaceNormalSlicer` 重构为标准的 Extension 结构，并推送到您的 GitHub 仓库中的 `SlicerSurfaceNormalSlicer` 目录。

---

## 2. 目录结构说明

符合官方规范的 Extension 必须包含 `CMakeLists.txt`，即使是纯 Python 脚本也需要。我已经为您创建了以下结构：

```text
SlicerSurfaceNormalSlicer/           ← Extension 根目录
├── CMakeLists.txt                   ← Extension 级 CMake 配置（包含元数据）
├── SurfaceNormalSlicer.json         ← 提交给官方的 Catalog Entry 文件
├── README.md                        ← Extension 说明文档
└── SurfaceNormalSlicer/             ← 模块子目录
    ├── CMakeLists.txt               ← 模块级 CMake 配置
    ├── SurfaceNormalSlicer.py       ← 核心 Python 代码
    └── Resources/
        └── Icons/
            └── SurfaceNormalSlicer.png  ← 模块图标
```

---

## 3. 发布操作步骤

请按照以下步骤将您的 Extension 提交到官方索引：

### 步骤一：准备独立的 GitHub 仓库（推荐）
虽然目前代码在您的 `BioInformatics` 仓库中，但 Slicer 官方**强烈建议**每个 Extension 拥有独立的 GitHub 仓库。
1. 在您的 GitHub 上创建一个新仓库，命名为 `SlicerSurfaceNormalSlicer`。
2. 将 `BioInformatics/SlicerSurfaceNormalSlicer/` 目录下的所有文件移动到这个新仓库的根目录。
3. 确保 `SurfaceNormalSlicer.json` 文件中的 `scm_url` 指向这个新仓库的地址。

### 步骤二：Fork 官方索引仓库
1. 登录 GitHub，访问 [Slicer Extensions Index 仓库](https://github.com/Slicer/ExtensionsIndex)。
2. 点击右上角的 **Fork** 按钮，将其 Fork 到您的个人账号下。

### 步骤三：上传 Catalog Entry 文件
1. 在您 Fork 的 `ExtensionsIndex` 仓库中，找到与当前 Slicer 稳定版对应的分支（例如 `5.6` 或 `main` 用于预览版）。
2. 点击 **Add file** → **Upload files**。
3. 将我为您生成的 `SurfaceNormalSlicer.json` 文件上传到该仓库的根目录。
4. 提交更改（Commit changes）。

### 步骤四：创建 Pull Request (PR)
1. 在您 Fork 的仓库页面，点击 **Contribute** → **Open pull request**。
2. 确保目标仓库是 `Slicer/ExtensionsIndex`，目标分支是您刚才上传文件的分支。
3. 填写 PR 标题（例如：`ENH: Add SurfaceNormalSlicer extension`）。
4. 按照 PR 模板填写必要信息（通常需要确认您已阅读开发者指南）。
5. 点击 **Create pull request**。

### 步骤五：等待审核与自动构建
1. 提交 PR 后，Slicer 官方的 CI/CD 系统（CDash）会自动拉取您的代码，并在 Windows、macOS 和 Linux 上进行测试构建。
2. 如果构建通过，Slicer 核心开发者会审核您的 PR 并合并。
3. 合并后的第二天，您的插件就会出现在全球所有 3D Slicer 用户的 Extension Manager 中！

---

## 4. 常见问题解答

**Q: 我的插件是纯 Python 写的，为什么还需要 CMakeLists.txt？**  
A: Slicer 的 Extension 构建系统（基于 CMake 和 CPack）需要通过 `CMakeLists.txt` 来识别模块、打包资源文件并生成安装包。对于纯 Python 插件，CMake 只是起到“打包”作用，不会进行实际的 C++ 编译。

**Q: 以后更新代码怎么办？**  
A: 您只需要在自己的 `SlicerSurfaceNormalSlicer` 仓库中提交代码更新。Slicer 的服务器每天晚上会自动拉取您仓库的最新代码（根据 `.json` 文件中的 `scm_revision`，通常是 `main` 分支），并自动打包发布新版本。您**不需要**每次更新都去官方仓库提 PR。
