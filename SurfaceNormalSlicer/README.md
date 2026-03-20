# SurfaceNormalSlicer — 3D Slicer 表面法向量切片重构插件

**作者**: 鲁奥晗  
**学号**: 2023012411

---

## 1. 插件简介

**SurfaceNormalSlicer** 是一款为 [3D Slicer](https://www.slicer.org/) 设计的 Python 脚本插件。该插件实现了从 **FreeSurfer 皮层重构** 到 **3D Slicer 任意轴向切片重构** 的完整临床工作流。

通过本插件，用户可以在 3D 视图中直接点击大脑皮层表面的任意一点，插件将自动计算该点的外切面法向量，并**实时重定向 2D 切片视图**（如 Red 视图），使其与该法向量垂直。用户可以在该视图中自由滚动，观察病变与皮层表面的空间关系，并可选择将重采样结果导出为 DICOM 序列。

---

## 2. 核心工作流

1. **FreeSurfer 重构**：将 MRI 扫描数据导入 FreeSurfer，完成皮层重构（生成 `lh.pial` / `rh.pial` 等文件）。
2. **数据导入**：将原始 MRI DICOM/NIfTI 和 FreeSurfer 皮层表面模型导入 3D Slicer。
3. **交互式拾取**：在 3D 视图中点击大脑表面任意点。
4. **实时预览**：插件自动计算法向量，并实时更新切片视图方向，实现任意轴向的切片重构与预览。
5. **重采样与导出**：一键生成沿法向量方向的完整重采样体积，并可通过 Slicer 导出为 DICOM。

---

## 3. 安装指南

1. 下载本仓库中的 `SurfaceNormalSlicer.py` 文件。
2. 打开 3D Slicer（建议版本 5.x 或更高）。
3. 导航至菜单栏：`Edit` → `Application Settings`。
4. 在左侧面板选择 `Modules`。
5. 在 `Additional module paths` 区域，点击 `Add` 按钮，选择包含 `SurfaceNormalSlicer.py` 文件的文件夹。
6. 点击 `OK` 并**重启 3D Slicer**。
7. 重启后，在模块选择器（Module Selector）中搜索 `Surface Normal Slicer` 即可找到并打开该插件。

---

## 4. 使用步骤

### 步骤一：准备与导入数据

1. **导入原始 MRI**：将您的原始 MRI 数据（DICOM 或 NIfTI）拖入 3D Slicer 并加载。
2. **导入皮层表面**：
   - 推荐安装 **SlicerFreeSurfer** 扩展（通过 Slicer 的 Extension Manager 安装）。
   - 安装后，直接将 FreeSurfer 的 `lh.pial` 或 `rh.pial` 文件拖入 Slicer 即可加载为 3D 模型（Model Node）。
   - 或者，您也可以先使用 FreeSurfer 的 `mris_convert` 工具将 `.pial` 转换为 `.stl` 或 `.vtk` 格式，再导入 Slicer。

### 步骤二：配置插件并交互拾取

1. 打开 `Surface Normal Slicer` 模块。
2. 在 **Input** 面板中：
   - **MRI Volume**: 选择您导入的原始 MRI 体积。
   - **Cortical Surface**: 选择您导入的皮层表面模型。
3. 在 **Interactive Surface Picking** 面板中：
   - 点击 **Enable Surface Picking** 按钮（按钮会变绿表示已激活）。
   - 在 3D 视图中，使用鼠标点击皮层表面的任意位置。
   - 插件面板会实时显示您点击的 RAS 坐标和计算出的表面法向量。
   - **Target Slice View**（默认 Red 视图）会立即重定向，显示该点的切面（即与法向量垂直的平面）。
   - 您可以在该 2D 视图中滚动鼠标滚轮，查看沿该法向量轴向的不同深度切片。

### 步骤三：生成重采样体积与导出（可选）

如果您希望将当前方向的切片保存为独立的体积数据：
1. 展开 **Generate Resampled Volume (Optional)** 面板。
2. 设置 **Slice Spacing (mm)**（切片间距，默认 1.0 mm）和 **Number of Slices**（切片总数，默认 60）。
3. 输入输出体积的名称（如 `NormalSlices`）。
4. 点击 **Generate Resampled Volume** 按钮。
5. 插件将生成一个新的体积节点。
6. 若需导出，请点击 Slicer 左上角的 `DICOM` 模块，或通过菜单栏 `File` → `Export to DICOM` 将新生成的体积导出为 DICOM 序列。

---

## 5. 核心算法说明

1. **表面法向量计算**：
   - 插件首先检查表面模型是否包含法向量数据。如果没有，则使用 `vtkPolyDataNormals` 自动计算顶点的外向法向量。
   - 使用 `vtkPointLocator` 构建空间索引，快速找到距离用户点击位置最近的表面顶点，并提取其法向量。
2. **切片视图重定向**：
   - 基于提取的法向量（作为 Z 轴），使用 Gram-Schmidt 正交化方法计算出切面内的 X 和 Y 正交基向量。
   - 调用 `vtkMRMLSliceNode.SetSliceToRASByNTP()` 方法，将 2D 切片视图的法线（Normal）、横向（Transverse）和位置（Position）实时更新为计算出的参数。
3. **体积重采样**：
   - 构建 4×4 的 RAS 变换矩阵。
   - 使用 `vtkImageReslice` 执行线性插值重采样，生成指定间距和层数的新体积数据。

---

## 6. 依赖项

| 依赖 | 说明 |
|---|---|
| 3D Slicer 5.x+ | 宿主平台 |
| Python 3.x | 脚本运行环境（Slicer 内置） |
| VTK | 图像处理、空间索引与重采样（Slicer 内置） |
| NumPy | 向量与矩阵计算（Slicer 内置） |
| SlicerFreeSurfer | （可选但推荐）用于直接导入 FreeSurfer 表面文件 |

---

## 7. 许可证

MIT License
