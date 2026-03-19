# ObliqueSliceResampler — 3D Slicer MRI 任意轴分层切片插件

**作者**: 鲁奥晗  
**学号**: 2023012411

---

## 1. 插件简介

**ObliqueSliceResampler** 是一款为 [3D Slicer](https://www.slicer.org/) 设计的 Python 脚本插件（Scripted Module）。其核心功能是允许用户在 MRI 三维重构后，通过在 3D 视图中放置**两个解剖学标志点**（Fiducials）来定义一条自定义轴，并以该轴方向为法向量，自动生成一系列等间距的**斜面重采样切片**（Oblique Resampled Slices），以便更直观地观察特定方向上的病变。

**典型应用场景**：以右侧中央沟外切面的垂线为轴，对该方向进行分层切片，从而系统性地评估病变与中央沟的空间关系。

---

## 2. 安装指南

1. 下载本仓库中的 `ObliqueSliceResampler.py` 文件。
2. 打开 3D Slicer（建议版本 5.x 或更高）。
3. 导航至菜单栏：`Edit` → `Application Settings`。
4. 在左侧面板选择 `Modules`。
5. 在 `Additional module paths` 区域，点击 `Add` 按钮，选择包含 `ObliqueSliceResampler.py` 文件的文件夹。
6. 点击 `OK` 并**重启 3D Slicer**。
7. 重启后，在模块选择器（Module Selector）中搜索 `Oblique Slice Resampler` 即可找到并打开该插件。

---

## 3. 使用步骤

### 步骤一：准备数据

1. 在 3D Slicer 中加载您的 MRI 体积数据（支持 NIfTI、DICOM 等格式）。
2. 切换到 `Markups` 模块，创建一个新的 Fiducial 列表（例如命名为 `AxisPoints`）。
3. 在 3D 视图或 2D 切片视图中，精确放置**恰好两个**标志点，定义您的自定义轴（例如右侧中央沟的两个端点）。

### 步骤二：配置插件参数

打开 `Oblique Slice Resampler` 模块，按照下表配置各参数：

| 参数 | 说明 | 默认值 |
|---|---|---|
| **Input Volume** | 选择已加载的 MRI 体积数据 | — |
| **Axis Fiducials (2 pts)** | 选择包含两个标志点的 Fiducial 列表 | — |
| **Slice Spacing (mm)** | 相邻切片之间的间距（毫米） | 2.0 mm |
| **Number of Slices** | 要生成的切片总数 | 50 |
| **Output Volume Name** | 输出重采样体积的名称 | ObliqueSlices |

### 步骤三：生成切片

点击底部的 `Generate Slices` 按钮。插件将自动执行以下操作：
- 计算两点之间的轴向量并标准化。
- 构建垂直于该轴的正交平面基向量。
- 使用 VTK 的 `vtkImageReslice` 执行线性插值重采样。
- 将生成的体积数据注册到 Slicer 场景中，并自动切换视图显示。

---

## 4. 核心算法说明

本插件的核心算法分为以下四个步骤：

**1. 轴定义**：从两个标志点的 RAS 坐标计算轴向量。

**2. 正交基计算**：使用 Gram-Schmidt 正交化方法，在垂直于轴向量的平面内计算两个正交单位向量，作为输出体积的平面内坐标轴。

**3. 变换矩阵构建**：将正交基向量和原点组合成一个 4×4 的 RAS 变换矩阵，传递给 `vtkImageReslice`。

**4. 图像重采样**：`vtkImageReslice` 根据变换矩阵，对原始 MRI 体积进行线性插值重采样，生成指定数量和间距的切片序列。

---

## 5. 注意事项

- 必须且只能选择**两个**标志点来定义轴。若点数不等于 2，插件将显示错误提示。
- 若切片数量过多，超出原始图像有效区域的部分将显示为黑色背景（像素值为 0）。
- 处理高分辨率 MRI 数据时，重采样过程可能需要数秒，请耐心等待。

---

## 6. 依赖项

| 依赖 | 说明 |
|---|---|
| 3D Slicer 5.x+ | 宿主平台 |
| Python 3.x | 脚本运行环境（Slicer 内置） |
| VTK | 图像处理与重采样（Slicer 内置） |
| NumPy | 数值计算（Slicer 内置） |

---

## 7. 许可证

MIT License
