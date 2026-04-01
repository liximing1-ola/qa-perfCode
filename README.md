# qa-perfCode

QA 性能工程工具集 - 包含 APK 构建打包、性能测试、数据可视化等功能。

## 项目结构

```
qa-perfCode/
├── appBuild/           # APK 构建打包工具
├── ciBuild/            # CI/CD 集成工具
├── mobilePerf/         # 性能测试工具
└── overseaBuild/       # 海外构建工具
```

## 功能模块

### 1. appBuild - APK 构建打包

#### againBuild/ - 重新构建工具

| 脚本 | 功能 | 用法示例 |
|------|------|----------|
| `againKey.py` | APK 重新签名 | `python againKey.py input.apk output.apk --keystore slp` |
| `changeApk.py` | APK 解包/打包 | `python changeApk.py app.apk -d` / `python changeApk.py app/ -c` |
| `changeRes.py` | 批量替换资源文件 | `python changeRes.py <res_path> <new_res_path>` |

#### DaBao/ - 渠道打包工具

| 脚本 | 功能 | 用法示例 |
|------|------|----------|
| `batchChannelV2.py` | Walle 渠道打包 | `python batchChannelV2.py app.apk channel1,channel2` |
| `changeChannelList.py` | 批量渠道打包 | `python changeChannelList.py app.apk appName version cpu` |
| `getAppInfo.py` | 获取 APK 信息 | `python getAppInfo.py app.apk` |
| `changeImage.py` | 图片批量转灰度 | `python changeImage.py input_dir output_dir` |

### 2. ciBuild - CI/CD 工具

| 脚本 | 功能 |
|------|------|
| `upload_pgyer.py` | 上传应用到蒲公英 |

### 3. mobilePerf - 性能测试

#### 核心模块

| 模块 | 功能 |
|------|------|
| `androidDevice.py` | ADB 设备管理、命令执行、日志采集 |
| `cpu_top.py` | CPU 性能监控和数据采集 |
| `logcat.py` | Logcat 日志监控、启动时间采集 |

#### 工具脚本

| 脚本 | 功能 | 用法示例 |
|------|------|----------|
| `testPhoneTime.py` | 启动时间测试 | `python testPhoneTime.py --mode cold --package com.xxx --activity .MainActivity` |
| `runFps.py` | FPS 测试（自动滑动） | `python runFps.py -c 2000` |
| `changeFile.py` | SoloPi 数据自动拉取 | `python changeFile.py` |
| `chooseFileToChart.py` | SoloPi 数据手动拉取 | `python chooseFileToChart.py` |
| `csvToChart.py` | CSV 数据可视化 | `python csvToChart.py cpu` |

#### 使用 SoloPi 进行性能测试

1. 下载安装 [SoloPi](https://github.com/alipay/SoloPi)
2. 使用 SoloPi 采集性能数据（内存、FPS、CPU 等）
3. 运行 `python mobilePerf/tools/changeFile.py` 拉取数据
4. 运行 `python mobilePerf/tools/csvToChart.py <type>` 生成图表

### 4. overseaBuild - 海外构建

| 脚本 | 功能 |
|------|------|
| `wechat_notify.py` | 企业微信构建通知 |
| `upload_apks_with_listing.py` | Google Play 应用上传 |
| `query_voided.py` | 查询作废的购买记录 |
| `google_translater.py` | Google 翻译 API 封装 |

## 环境要求

- Python 3.9+
- 依赖包：`pip install -r requirements.txt`

## 快速开始

```bash
# 克隆仓库
git clone <repo-url>
cd qa-perfCode

# 安装依赖
pip install -r requirements.txt

# 运行性能测试
python mobilePerf/tools/testPhoneTime.py --mode cold --package com.example.app --activity .MainActivity
```

## 代码规范

本项目采用现代 Python 开发规范：

- ✅ 全面使用 Type Hints 类型注解
- ✅ 使用 `@dataclass` 定义数据类
- ✅ 使用 `pathlib` 处理文件路径
- ✅ 使用 `argparse` 处理命令行参数
- ✅ 使用 `subprocess.run` 执行系统命令
- ✅ 函数职责分离，代码结构清晰

## 注意事项

- iOS 性能测试方案还在验证中
- 部分工具需要配置 ADB 环境
- Google Play 相关工具需要配置服务账号密钥

