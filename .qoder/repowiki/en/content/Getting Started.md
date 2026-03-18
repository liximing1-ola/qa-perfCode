# Getting Started

<cite>
**Referenced Files in This Document**
- [README.md](file://README.md)
- [mobilePerf/run.sh](file://mobilePerf/run.sh)
- [mobilePerf/tools/openPerf.bat](file://mobilePerf/tools/openPerf.bat)
- [mobilePerf/tools/run.sh](file://mobilePerf/tools/run.sh)
- [appBuild/openBuild.bat](file://appBuild/openBuild.bat)
- [mobilePerf/perfCode/common/config.py](file://mobilePerf/perfCode/common/config.py)
- [mobilePerf/perfCode/androidDevice.py](file://mobilePerf/perfCode/androidDevice.py)
- [mobilePerf/perfCode/cpu_top.py](file://mobilePerf/perfCode/cpu_top.py)
- [mobilePerf/perfCode/runFps.py](file://mobilePerf/perfCode/runFps.py)
- [mobilePerf/tools/changeFile.py](file://mobilePerf/tools/changeFile.py)
- [mobilePerf/tools/csvToChart.py](file://mobilePerf/tools/csvToChart.py)
- [ciBuild/sh_pgyer_upload.sh](file://ciBuild/sh_pgyer_upload.sh)
- [overseaBuild/build_apk.sh](file://overseaBuild/build_apk.sh)
</cite>

## Table of Contents
1. [Introduction](#introduction)
2. [Project Structure](#project-structure)
3. [Prerequisites](#prerequisites)
4. [Installation and Setup](#installation-and-setup)
5. [Basic Workflow](#basic-workflow)
6. [Quick Start Examples](#quick-start-examples)
7. [Architecture Overview](#architecture-overview)
8. [Detailed Component Analysis](#detailed-component-analysis)
9. [Dependency Analysis](#dependency-analysis)
10. [Performance Considerations](#performance-considerations)
11. [Troubleshooting Guide](#troubleshooting-guide)
12. [Conclusion](#conclusion)

## Introduction
This guide helps you set up and run the QA Performance Code project for Android performance testing. It covers prerequisites, installation, configuration, and workflows for collecting performance metrics (CPU, memory, FPS, temperature), generating charts, and integrating with CI/CD systems. The project relies on SoloPi for data collection, ADB for device communication, and Python scripts for data processing and chart generation.

## Project Structure
The repository is organized into modules:
- mobilePerf: Performance data collection, processing, and chart generation
- appBuild: Build and packaging utilities for Android and related tasks
- ciBuild: CI/CD helpers for uploading artifacts
- overseaBuild: Overseas build scripts for Android and Google Play integration

```mermaid
graph TB
subgraph "mobilePerf"
MP_Run["run.sh"]
MP_Tools["tools/"]
MP_Mod["perfCode/"]
end
subgraph "appBuild"
AB_Batch["openBuild.bat"]
AB_DaBao["DaBao/"]
AB_Again["againBuild/"]
AB_ChangeImage["changeImage.py"]
end
subgraph "ciBuild"
CI_Script["sh_pgyer_upload.sh"]
CI_Utils["utils/"]
end
subgraph "overseaBuild"
OB_Apk["build_apk.sh"]
OB_App["build_app.sh"]
OB_Ipa["build_ipa.sh"]
OB_Google["upload_gp/"]
end
```

**Diagram sources**
- [mobilePerf/run.sh](file://mobilePerf/run.sh)
- [appBuild/openBuild.bat](file://appBuild/openBuild.bat)
- [ciBuild/sh_pgyer_upload.sh](file://ciBuild/sh_pgyer_upload.sh)
- [overseaBuild/build_apk.sh](file://overseaBuild/build_apk.sh)

**Section sources**
- [README.md](file://README.md)

## Prerequisites
Before starting, ensure the following tools and frameworks are installed and configured:

- Android SDK and ADB
  - Install Android Studio or Android SDK Platform Tools to get ADB.
  - Verify ADB availability via the terminal or command prompt.
  - Enable Developer Options and USB Debugging on the test device.
  - Connect the device via USB and trust the computer if prompted.

- SoloPi framework
  - Download and install the latest SoloPi release.
  - SoloPi writes performance data to a specific path on the device for later retrieval.

- Python environment
  - Install Python 3.x.
  - Install required Python packages used by the scripts:
    - matplotlib
    - numpy
    - pandas (if used indirectly by plotting libraries)
  - Ensure Python and pip are added to PATH.

- Flutter SDK (for Android builds)
  - Install Flutter SDK and configure your environment.
  - Ensure the Android toolchain is set up for building APKs.

- Optional: Google Play uploader dependencies (for overseas builds)
  - Python dependencies for Google Play API uploads (see overseaBuild scripts).

Verification steps:
- Open a terminal/command prompt and run:
  - adb devices
  - python --version
  - flutter doctor
  - soloPi app is installed and running on the device

**Section sources**
- [README.md](file://README.md)
- [mobilePerf/perfCode/androidDevice.py](file://mobilePerf/perfCode/androidDevice.py)
- [mobilePerf/tools/changeFile.py](file://mobilePerf/tools/changeFile.py)

## Installation and Setup
Follow these steps to prepare your environment and project:

1) Install Android SDK and ADB
- Download Android Studio or SDK Platform Tools.
- Add platform-tools to PATH so adb is globally available.
- Connect an Android device via USB and enable Developer Options and USB Debugging.

2) Install SoloPi
- Download the latest SoloPi release and install the APK on the device.
- Launch SoloPi and start a recording session to generate performance data under its records directory.

3) Set up Python environment
- Install Python 3.x and pip.
- Install required packages:
  - matplotlib
  - numpy
- Confirm installation:
  - python --version
  - pip list | grep -E "(matplotlib|numpy)"

4) Configure project paths
- The scripts expect SoloPi output to be at a fixed path on the device storage.
- Ensure the device path matches the scripts’ expectations.

5) Prepare Flutter environment (optional)
- Install Flutter SDK and run flutter doctor to validate setup.
- Required for Android build automation scripts.

6) Verify device connectivity
- Run adb devices and confirm your device appears with a “device” status.

**Section sources**
- [README.md](file://README.md)
- [mobilePerf/perfCode/androidDevice.py](file://mobilePerf/perfCode/androidDevice.py)
- [mobilePerf/tools/changeFile.py](file://mobilePerf/tools/changeFile.py)

## Basic Workflow
This workflow collects performance data, transfers it to your PC, and generates charts for analysis.

```mermaid
sequenceDiagram
participant Dev as "Developer"
participant SoloPi as "SoloPi App"
participant ADB as "ADB Shell"
participant CF as "changeFile.py"
participant CSV as "csvToChart.py"
participant Chart as "Generated Charts"
Dev->>SoloPi : Start recording performance metrics
SoloPi-->>Dev : Writes data to device storage
Dev->>CF : Run changeFile.py to pull data
CF->>ADB : List and pull SoloPi records
ADB-->>CF : Transferred CSV files
CF-->>CSV : Place CSV files under report/
Dev->>CSV : Run csvToChart.py for CPU/MEM/FPS/TEMP
CSV-->>Chart : Save PNG charts under report/
```

**Diagram sources**
- [mobilePerf/tools/changeFile.py](file://mobilePerf/tools/changeFile.py)
- [mobilePerf/tools/csvToChart.py](file://mobilePerf/tools/csvToChart.py)

Step-by-step:
1) Start SoloPi and record metrics on the device.
2) On macOS/Linux, run the convenience script to process data:
   - sh mobilePerf/run.sh
3) On Windows, use the batch launcher:
   - Double-click mobilePerf/tools/openPerf.bat to open the tools directory.
4) Manually run:
   - python mobilePerf/tools/changeFile.py
   - python mobilePerf/tools/csvToChart.py cpu
   - python mobilePerf/tools/csvToChart.py mem
   - python mobilePerf/tools/csvToChart.py fps
   - python mobilePerf/tools/csvToChart.py temp
5) View generated charts under the report/ directory.

**Section sources**
- [README.md](file://README.md)
- [mobilePerf/run.sh](file://mobilePerf/run.sh)
- [mobilePerf/tools/openPerf.bat](file://mobilePerf/tools/openPerf.bat)
- [mobilePerf/tools/run.sh](file://mobilePerf/tools/run.sh)
- [mobilePerf/tools/changeFile.py](file://mobilePerf/tools/changeFile.py)
- [mobilePerf/tools/csvToChart.py](file://mobilePerf/tools/csvToChart.py)

## Quick Start Examples
Common tasks to get you started quickly:

- Performance monitoring setup
  - Install and launch SoloPi on the device.
  - Start a recording session.
  - Use changeFile.py to pull CSV data from the device to your PC.

- Basic APK building
  - Use Flutter to build an APK:
    - flutter build apk --release --flavor your_flavor
  - The overseaBuild script demonstrates automated build and upload flows for CI.

- CI/CD integration
  - Upload artifacts to a distribution service:
    - sh ciBuild/sh_pgyer_upload.sh <path_to_apk_or_ipa>
  - Automated Android builds with optional upload:
    - sh overseaBuild/build_apk.sh debug|release|store <versionName> <versionCode> <debugModel> "<releaseNotes>" <ciNum>

- Device configuration
  - Configure device and package identifiers in the configuration module before running collectors.

**Section sources**
- [README.md](file://README.md)
- [ciBuild/sh_pgyer_upload.sh](file://ciBuild/sh_pgyer_upload.sh)
- [overseaBuild/build_apk.sh](file://overseaBuild/build_apk.sh)
- [mobilePerf/perfCode/common/config.py](file://mobilePerf/perfCode/common/config.py)

## Architecture Overview
The system integrates device-side data capture with local processing and visualization.

```mermaid
graph TB
Dev["Developer PC"]
ADB["ADB"]
SoloPi["SoloPi App"]
CF["changeFile.py"]
CSV["csvToChart.py"]
Charts["PNG Charts"]
Dev --> CF
SoloPi --> ADB
ADB --> CF
CF --> CSV
CSV --> Charts
```

**Diagram sources**
- [mobilePerf/tools/changeFile.py](file://mobilePerf/tools/changeFile.py)
- [mobilePerf/tools/csvToChart.py](file://mobilePerf/tools/csvToChart.py)

## Detailed Component Analysis

### ADB and Device Management
The ADB wrapper handles device discovery, connection, and shell commands. It supports:
- Listing connected devices
- Starting/stopping logcat
- Pulling/pushing files
- Executing shell commands with retries and timeouts

```mermaid
classDiagram
class ADB {
+get_adb_path()
+list_device()
+is_connected(device_id)
+run_shell_cmd(cmd)
+start_logcat(save_dir, process_list, params)
+stop_logcat()
+pull_file(src, dst)
+push_file(src, dst)
}
```

**Diagram sources**
- [mobilePerf/perfCode/androidDevice.py](file://mobilePerf/perfCode/androidDevice.py)

**Section sources**
- [mobilePerf/perfCode/androidDevice.py](file://mobilePerf/perfCode/androidDevice.py)

### Performance Data Collection and Parsing
CPU collector reads device metrics via top and writes CSV data. It parses per-process and device-wide CPU usage, filters outliers, and saves structured data for charting.

```mermaid
flowchart TD
Start(["Start CPU Collection"]) --> Init["Initialize Collector<br/>Set interval and timeout"]
Init --> Loop{"Loop until timeout"}
Loop --> |Run| TopCmd["Execute top command"]
TopCmd --> Parse["Parse CPU usage<br/>per-process and device"]
Parse --> Filter["Filter invalid/outlier values"]
Filter --> Write["Write CSV row"]
Write --> Sleep["Sleep interval"]
Sleep --> Loop
Loop --> |Stop| Stop(["Stop and cleanup"])
```

**Diagram sources**
- [mobilePerf/perfCode/cpu_top.py](file://mobilePerf/perfCode/cpu_top.py)

**Section sources**
- [mobilePerf/perfCode/cpu_top.py](file://mobilePerf/perfCode/cpu_top.py)

### SoloPi Data Transfer and Chart Generation
The pipeline pulls SoloPi-generated CSV files from the device and converts them into charts.

```mermaid
sequenceDiagram
participant CF as "changeFile.py"
participant ADB as "ADB"
participant FS as "Device Storage"
participant CSV as "csvToChart.py"
CF->>ADB : List SoloPi records directory
ADB-->>CF : Record folders
CF->>ADB : Pull selected record folder
ADB-->>CF : CSV files copied locally
CF->>CSV : Invoke chart generation for CPU/MEM/FPS/TEMP
CSV-->>CF : PNG charts saved
```

**Diagram sources**
- [mobilePerf/tools/changeFile.py](file://mobilePerf/tools/changeFile.py)
- [mobilePerf/tools/csvToChart.py](file://mobilePerf/tools/csvToChart.py)

**Section sources**
- [mobilePerf/tools/changeFile.py](file://mobilePerf/tools/changeFile.py)
- [mobilePerf/tools/csvToChart.py](file://mobilePerf/tools/csvToChart.py)

### FPS Automation Script
The FPS script automates gesture input to stress-test UI responsiveness and can be extended to measure frame metrics.

```mermaid
flowchart TD
Start(["Start FPS Test"]) --> GetDev["Detect connected device"]
GetDev --> Loop{"Repeat N times"}
Loop --> |Swipe| SendInput["Send swipe commands"]
SendInput --> Delay["Short delay"]
Delay --> Loop
Loop --> |End| End(["Stop"])
```

**Diagram sources**
- [mobilePerf/perfCode/runFps.py](file://mobilePerf/perfCode/runFps.py)

**Section sources**
- [mobilePerf/perfCode/runFps.py](file://mobilePerf/perfCode/runFps.py)

### Build Automation and CI/CD
Automated build and upload flows for Android and iOS targets.

```mermaid
sequenceDiagram
participant Dev as "Developer/CI"
participant Flutter as "Flutter CLI"
participant Upload as "Distribution API"
participant Store as "Store/GCS"
Dev->>Flutter : Build APK/AppBundle
Flutter-->>Dev : Artifacts in outputs/
Dev->>Upload : Upload artifact
Upload-->>Dev : Upload result
Dev->>Store : Publish to store (optional)
```

**Diagram sources**
- [overseaBuild/build_apk.sh](file://overseaBuild/build_apk.sh)
- [ciBuild/sh_pgyer_upload.sh](file://ciBuild/sh_pgyer_upload.sh)

**Section sources**
- [overseaBuild/build_apk.sh](file://overseaBuild/build_apk.sh)
- [ciBuild/sh_pgyer_upload.sh](file://ciBuild/sh_pgyer_upload.sh)

## Dependency Analysis
High-level dependencies among components:

```mermaid
graph LR
CF["changeFile.py"] --> ADB["ADB Wrapper"]
CSV["csvToChart.py"] --> Report["report/ CSVs"]
CPU["cpu_top.py"] --> ADB
RunSh["mobilePerf/run.sh"] --> CF
RunSh --> CSV
OpenPerf["mobilePerf/tools/openPerf.bat"] --> Tools["tools/"]
OpenBuild["appBuild/openBuild.bat"] --> Build["Build Utilities"]
Pgyer["ciBuild/sh_pgyer_upload.sh"] --> Upload["Distribution API"]
BuildApk["overseaBuild/build_apk.sh"] --> Flutter["Flutter CLI"]
BuildApk --> GPlay["Google Play Upload"]
```

**Diagram sources**
- [mobilePerf/tools/changeFile.py](file://mobilePerf/tools/changeFile.py)
- [mobilePerf/tools/csvToChart.py](file://mobilePerf/tools/csvToChart.py)
- [mobilePerf/perfCode/cpu_top.py](file://mobilePerf/perfCode/cpu_top.py)
- [mobilePerf/run.sh](file://mobilePerf/run.sh)
- [mobilePerf/tools/openPerf.bat](file://mobilePerf/tools/openPerf.bat)
- [appBuild/openBuild.bat](file://appBuild/openBuild.bat)
- [ciBuild/sh_pgyer_upload.sh](file://ciBuild/sh_pgyer_upload.sh)
- [overseaBuild/build_apk.sh](file://overseaBuild/build_apk.sh)

**Section sources**
- [mobilePerf/tools/changeFile.py](file://mobilePerf/tools/changeFile.py)
- [mobilePerf/tools/csvToChart.py](file://mobilePerf/tools/csvToChart.py)
- [mobilePerf/perfCode/cpu_top.py](file://mobilePerf/perfCode/cpu_top.py)
- [mobilePerf/run.sh](file://mobilePerf/run.sh)
- [mobilePerf/tools/openPerf.bat](file://mobilePerf/tools/openPerf.bat)
- [appBuild/openBuild.bat](file://appBuild/openBuild.bat)
- [ciBuild/sh_pgyer_upload.sh](file://ciBuild/sh_pgyer_upload.sh)
- [overseaBuild/build_apk.sh](file://overseaBuild/build_apk.sh)

## Performance Considerations
- Data sampling intervals: Adjust collection intervals to balance accuracy and overhead.
- Device selection: Prefer a single connected device to avoid ambiguity.
- Storage checks: Ensure sufficient device storage to prevent collection interruptions.
- Network conditions: Simulate real-world network scenarios by configuring device Wi-Fi or cellular settings.
- Chart generation: Use filtered data to remove outliers for meaningful trends.

[No sources needed since this section provides general guidance]

## Troubleshooting Guide
Common issues and resolutions:

- ADB not found or device not listed
  - Ensure platform-tools is in PATH and ADB is executable.
  - Reconnect the device and accept USB debugging prompts.
  - Use adb devices to verify connectivity.

- Port conflicts or daemon errors
  - Scripts detect and resolve ADB server issues; restart ADB server if needed.
  - Kill processes occupying the ADB port if necessary.

- SoloPi data path missing
  - Verify SoloPi is installed and writing to the expected device path.
  - Ensure the device path matches the scripts’ expectations.

- CSV parsing errors
  - Confirm CSV encodings and column counts.
  - Validate that the selected CSV is the latest and complete.

- Chart generation failures
  - Ensure matplotlib and numpy are installed.
  - Check that report directories exist and are writable.

**Section sources**
- [mobilePerf/perfCode/androidDevice.py](file://mobilePerf/perfCode/androidDevice.py)
- [mobilePerf/tools/changeFile.py](file://mobilePerf/tools/changeFile.py)
- [mobilePerf/tools/csvToChart.py](file://mobilePerf/tools/csvToChart.py)

## Conclusion
You now have the essentials to set up the QA Performance Code project, connect an Android device, collect performance metrics via SoloPi, transfer and process data locally, and generate actionable charts. Extend the workflows with Flutter builds and CI/CD integrations for automated delivery pipelines.