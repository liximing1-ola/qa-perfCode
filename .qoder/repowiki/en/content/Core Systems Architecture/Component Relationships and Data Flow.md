# Component Relationships and Data Flow

<cite>
**Referenced Files in This Document**
- [README.md](file://README.md)
- [androidDevice.py](file://mobilePerf/perfCode/androidDevice.py)
- [basemonitor.py](file://mobilePerf/perfCode/common/basemonitor.py)
- [config.py](file://mobilePerf/perfCode/common/config.py)
- [log.py](file://mobilePerf/perfCode/common/log.py)
- [utils.py](file://mobilePerf/perfCode/common/utils.py)
- [cpu_top.py](file://mobilePerf/perfCode/cpu_top.py)
- [logcat.py](file://mobilePerf/perfCode/logcat.py)
- [globaldata.py](file://mobilePerf/perfCode/globaldata.py)
- [runFps.py](file://mobilePerf/perfCode/runFps.py)
- [run.sh](file://mobilePerf/run.sh)
- [openPerf.bat](file://mobilePerf/tools/openPerf.bat)
- [batchChannelV2.py](file://appBuild/DaBao/batchChannelV2.py)
- [openBuild.bat](file://appBuild/openBuild.bat)
- [upload_pgyer.py](file://ciBuild/utils/upload_pgyer.py)
- [sh_pgyer_upload.sh](file://ciBuild/sh_pgyer_upload.sh)
</cite>

## Table of Contents
1. [Introduction](#introduction)
2. [Project Structure](#project-structure)
3. [Core Components](#core-components)
4. [Architecture Overview](#architecture-overview)
5. [Detailed Component Analysis](#detailed-component-analysis)
6. [Dependency Analysis](#dependency-analysis)
7. [Performance Considerations](#performance-considerations)
8. [Troubleshooting Guide](#troubleshooting-guide)
9. [Conclusion](#conclusion)
10. [Appendices](#appendices)

## Introduction
This document describes how performance monitoring, build automation, and CI/CD integration components interact within the repository. It focuses on component relationships, data flow patterns, inter-component communication protocols, shared resources management, and lifecycle management. It also documents how APK build tools, performance data collection, and distribution systems coordinate, and how errors propagate through the system.

## Project Structure
The repository is organized into three primary areas:
- mobilePerf: performance data acquisition, parsing, and reporting
- appBuild: APK build and packaging utilities (including channel packaging)
- ciBuild: CI/CD upload utilities for distribution platforms

```mermaid
graph TB
subgraph "mobilePerf"
MP_Common["common<br/>config, utils, log, basemonitor"]
MP_Dev["androidDevice.py<br/>ADB wrapper"]
MP_CPU["cpu_top.py<br/>CPU collector"]
MP_LCAT["logcat.py<br/>Logcat monitor"]
MP_GD["globaldata.py<br/>RuntimeData"]
MP_Run["run.sh<br/>orchestration"]
MP_Tools["tools<br/>openPerf.bat, changeFile.py, csvToChart.py"]
end
subgraph "appBuild"
AB_DB["DaBao<br/>batchChannelV2.py"]
AB_Open["openBuild.bat"]
end
subgraph "ciBuild"
CI_Py["utils/upload_pgyer.py"]
CI_Sh["sh_pgyer_upload.sh"]
end
MP_Common --> MP_Dev
MP_Dev --> MP_CPU
MP_Dev --> MP_LCAT
MP_CPU --> MP_Run
MP_LCAT --> MP_Run
MP_Run --> MP_Tools
AB_DB --> CI_Py
AB_DB --> CI_Sh
CI_Py --> CI_Sh
```

**Diagram sources**
- [androidDevice.py:18-120](file://mobilePerf/perfCode/androidDevice.py#L18-L120)
- [cpu_top.py:206-383](file://mobilePerf/perfCode/cpu_top.py#L206-L383)
- [logcat.py:17-116](file://mobilePerf/perfCode/logcat.py#L17-L116)
- [run.sh:1-29](file://mobilePerf/run.sh#L1-L29)
- [batchChannelV2.py:21-70](file://appBuild/DaBao/batchChannelV2.py#L21-L70)
- [upload_pgyer.py:43-86](file://ciBuild/utils/upload_pgyer.py#L43-L86)
- [sh_pgyer_upload.sh:55-86](file://ciBuild/sh_pgyer_upload.sh#L55-L86)

**Section sources**
- [README.md:1-37](file://README.md#L1-L37)
- [openBuild.bat:1-23](file://appBuild/openBuild.bat#L1-L23)

## Core Components
- ADB wrapper: Provides device connectivity, command execution, logcat streaming, and file operations.
- Monitor base: Defines the contract for performance monitors (start, stop, save, clear).
- CPU monitor: Collects CPU metrics via top, writes CSV, and supports multi-package aggregation.
- Logcat monitor: Streams and parses logcat, extracts launch time metrics, and optionally captures stacks on exceptions.
- Global runtime data: Shared state for paths, packages, and synchronization primitives.
- Build tools: Channel packaging via Walle CLI and batch operations.
- Distribution utilities: Upload to distribution platforms via Python and Shell scripts.

**Section sources**
- [androidDevice.py:18-120](file://mobilePerf/perfCode/androidDevice.py#L18-L120)
- [basemonitor.py:7-34](file://mobilePerf/perfCode/common/basemonitor.py#L7-L34)
- [cpu_top.py:206-383](file://mobilePerf/perfCode/cpu_top.py#L206-L383)
- [logcat.py:17-116](file://mobilePerf/perfCode/logcat.py#L17-L116)
- [globaldata.py:6-14](file://mobilePerf/perfCode/globaldata.py#L6-L14)
- [batchChannelV2.py:21-70](file://appBuild/DaBao/batchChannelV2.py#L21-L70)
- [upload_pgyer.py:43-86](file://ciBuild/utils/upload_pgyer.py#L43-L86)
- [sh_pgyer_upload.sh:55-86](file://ciBuild/sh_pgyer_upload.sh#L55-L86)

## Architecture Overview
The system follows a layered architecture:
- Device abstraction layer (ADB)
- Data collection layer (CPU, Logcat)
- Orchestration layer (scripts and batch tools)
- Distribution layer (CI/CD upload utilities)

```mermaid
graph TB
Dev["Physical Device"]
ADB["ADB Wrapper<br/>androidDevice.py"]
MonBase["Monitor Base<br/>basemonitor.py"]
CPU["CPU Collector<br/>cpu_top.py"]
LCAT["Logcat Monitor<br/>logcat.py"]
RTD["RuntimeData<br/>globaldata.py"]
CFG["Config<br/>config.py"]
LOG["Logger<br/>log.py"]
UTL["Utils<br/>utils.py"]
RUN["Orchestration<br/>run.sh"]
TOOLS["Tools<br/>openPerf.bat"]
WALLE["Walle CLI<br/>batchChannelV2.py"]
PY_UP["Py Upload<br/>upload_pgyer.py"]
SH_UP["Shell Upload<br/>sh_pgyer_upload.sh"]
Dev --> ADB
ADB --> CPU
ADB --> LCAT
CPU --> RTD
LCAT --> RTD
CPU --> RUN
LCAT --> RUN
RUN --> TOOLS
CFG --> CPU
CFG --> LCAT
LOG --> CPU
LOG --> LCAT
UTL --> CPU
UTL --> LCAT
WALLE --> PY_UP
WALLE --> SH_UP
PY_UP --> SH_UP
```

**Diagram sources**
- [androidDevice.py:18-120](file://mobilePerf/perfCode/androidDevice.py#L18-L120)
- [cpu_top.py:206-383](file://mobilePerf/perfCode/cpu_top.py#L206-L383)
- [logcat.py:17-116](file://mobilePerf/perfCode/logcat.py#L17-L116)
- [globaldata.py:6-14](file://mobilePerf/perfCode/globaldata.py#L6-L14)
- [config.py:3-20](file://mobilePerf/perfCode/common/config.py#L3-L20)
- [log.py:22-75](file://mobilePerf/perfCode/common/log.py#L22-L75)
- [utils.py:10-156](file://mobilePerf/perfCode/common/utils.py#L10-L156)
- [run.sh:1-29](file://mobilePerf/run.sh#L1-L29)
- [openPerf.bat:1-7](file://mobilePerf/tools/openPerf.bat#L1-L7)
- [batchChannelV2.py:21-70](file://appBuild/DaBao/batchChannelV2.py#L21-L70)
- [upload_pgyer.py:43-86](file://ciBuild/utils/upload_pgyer.py#L43-L86)
- [sh_pgyer_upload.sh:55-86](file://ciBuild/sh_pgyer_upload.sh#L55-L86)

## Detailed Component Analysis

### ADB Wrapper and Device Lifecycle
The ADB wrapper encapsulates device discovery, connection health, and command execution. It manages retries, timeouts, and OS-specific paths for the adb binary. It also starts/stops logcat streams and performs file operations on the device.

```mermaid
classDiagram
class ADB {
+DEVICEID
+get_adb_path()
+is_connected(device_id) bool
+list_device() list
+recover() void
+checkAdbNormal() bool
+kill_server() void
+start_server() void
+killOccupy5037Process() void
+run_adb_cmd(cmd, *argv, **kwds) str|Popen
+run_shell_cmd(cmd, **kwds) str
+start_logcat(save_dir, process_list, params) void
+stop_logcat() void
+wait_for_device(timeout) bool
+bugreport(save_path) str
+push_file(src_path, dst_path) str
+pull_file(src_path, dst_path) str
+screencap_out(pc_save_path) str
+screencap(save_path) str
+delete_file(file_path) void
+delete_folder(folder_path) void
+is_exist(path) bool
+mkdir(folder_path) void
+list_dir(dir_path) list
+list_dir_between_time(dir_path, start, end) list
+is_overtime_days(filepath, days) bool
+start_activity(activity_name, action, data_uri, extra, wait) dict
+get_focus_activity() str
+get_foreground_process() str
+get_current_activity() str
+get_pid_from_pck(package_name) int
+get_pckinfo_from_ps(packagename) list
+get_process_stack(package, save_path) str
+get_process_stack_from_pid(pid, save_path) str
+dumpheap(package, save_path) void
+dump_native_heap(package, save_path) void
+clear_data(packagename) str
+stop_package(packagename) str
+input(string) str
+ping(address, count) str
+get_system_version() str
}
```

**Diagram sources**
- [androidDevice.py:18-800](file://mobilePerf/perfCode/androidDevice.py#L18-L800)

**Section sources**
- [androidDevice.py:18-120](file://mobilePerf/perfCode/androidDevice.py#L18-L120)
- [androidDevice.py:177-293](file://mobilePerf/perfCode/androidDevice.py#L177-L293)
- [androidDevice.py:389-422](file://mobilePerf/perfCode/androidDevice.py#L389-L422)

### Monitor Base and Extension Contracts
The monitor base defines a common interface for data collectors. Subclasses implement start, stop, and save semantics.

```mermaid
classDiagram
class Monitor {
+start() void
+stop() void
+save() void
+clear() void
}
class LogcatMonitor {
+start() void
+stop() void
+add_log_handle(handle) void
+remove_log_handle(handle) void
+handle_exception(log_line) void
}
Monitor <|-- LogcatMonitor
```

**Diagram sources**
- [basemonitor.py:7-34](file://mobilePerf/perfCode/common/basemonitor.py#L7-L34)
- [logcat.py:17-116](file://mobilePerf/perfCode/logcat.py#L17-L116)

**Section sources**
- [basemonitor.py:7-34](file://mobilePerf/perfCode/common/basemonitor.py#L7-L34)
- [logcat.py:17-116](file://mobilePerf/perfCode/logcat.py#L17-L116)

### CPU Data Collection Workflow
CPU metrics are collected periodically via top, parsed, aggregated, and written to CSV. The monitor coordinates timing and persistence.

```mermaid
sequenceDiagram
participant Orchestrator as "Orchestrator<br/>run.sh"
participant CPU as "CpuMonitor<br/>cpu_top.py"
participant Coll as "CpuCollector<br/>cpu_top.py"
participant Dev as "ADB<br/>androidDevice.py"
participant FS as "Filesystem<br/>CSV"
Orchestrator->>CPU : start(startTime)
CPU->>Coll : start(startTime)
loop Every interval
Coll->>Dev : run_shell_cmd(top -b/-n ...)
Dev-->>Coll : raw output
Coll->>Coll : parse and aggregate
Coll->>FS : append CSV row
end
Orchestrator->>CPU : stop()
CPU->>Coll : stop()
Coll->>Dev : terminate top if running
```

**Diagram sources**
- [cpu_top.py:240-347](file://mobilePerf/perfCode/cpu_top.py#L240-L347)
- [androidDevice.py:276-293](file://mobilePerf/perfCode/androidDevice.py#L276-L293)

**Section sources**
- [cpu_top.py:206-383](file://mobilePerf/perfCode/cpu_top.py#L206-L383)
- [androidDevice.py:276-293](file://mobilePerf/perfCode/androidDevice.py#L276-L293)

### Logcat Parsing and Launch Metrics
Logcat monitor subscribes to real-time logs, extracts launch time metrics, and optionally writes exception logs and stacks.

```mermaid
sequenceDiagram
participant LCM as "LogcatMonitor<br/>logcat.py"
participant Dev as "ADB<br/>androidDevice.py"
participant RTD as "RuntimeData<br/>globaldata.py"
participant FS as "Filesystem<br/>CSV/log"
LCM->>Dev : start_logcat(save_dir, params="-b all")
Dev-->>LCM : logcat stream
LCM->>LCM : handle_launchTime(log_line)
LCM->>FS : write launch_logcat.csv
LCM->>LCM : handle_exception(log_line)
alt exception matched
LCM->>RTD : read old_pid
LCM->>Dev : get_process_stack_from_pid(pid, path)
Dev-->>LCM : stack content
LCM->>FS : write process_stack_*.log
end
LCM->>Dev : stop_logcat()
```

**Diagram sources**
- [logcat.py:32-116](file://mobilePerf/perfCode/logcat.py#L32-L116)
- [androidDevice.py:389-422](file://mobilePerf/perfCode/androidDevice.py#L389-L422)
- [globaldata.py:6-14](file://mobilePerf/perfCode/globaldata.py#L6-L14)

**Section sources**
- [logcat.py:17-216](file://mobilePerf/perfCode/logcat.py#L17-L216)
- [globaldata.py:6-14](file://mobilePerf/perfCode/globaldata.py#L6-L14)

### Build Automation and Channel Packaging
Channel packaging uses Walle CLI to modify APK metadata. The script supports single, multiple, and sequential channels and renames outputs accordingly.

```mermaid
flowchart TD
Start(["Start"]) --> ParseArgs["Parse CLI args"]
ParseArgs --> Mode{"Mode?"}
Mode --> |Show| Show["Show channel info"]
Mode --> |Single/Multi| GenNames["Generate channel names"]
Mode --> |Seq| GenSeq["Generate sequence names"]
Mode --> |Config| ReadCfg["Read config file"]
GenNames --> Pack["Run Walle batch per channel"]
GenSeq --> Pack
ReadCfg --> Pack
Pack --> Rename["Rename output APK"]
Rename --> Done(["Done"])
Show --> Done
```

**Diagram sources**
- [batchChannelV2.py:21-116](file://appBuild/DaBao/batchChannelV2.py#L21-L116)

**Section sources**
- [batchChannelV2.py:21-120](file://appBuild/DaBao/batchChannelV2.py#L21-L120)
- [openBuild.bat:1-23](file://appBuild/openBuild.bat#L1-L23)

### CI/CD Upload Integration
Two upload paths are provided: a Python module and a shell script. Both obtain an upload token, upload the artifact, and poll for completion.

```mermaid
sequenceDiagram
participant Py as "upload_pgyer.py"
participant Sh as "sh_pgyer_upload.sh"
participant API as "Pgyer API"
Py->>API : getCOSToken(api_key, install_type, password)
API-->>Py : {endpoint, params, key}
Py->>API : POST file with params
API-->>Py : 204
Py->>API : GET buildInfo(key)
API-->>Py : code==0
Sh->>API : curl getCOSToken(...)
API-->>Sh : JSON with endpoint/key/signature
Sh->>API : curl -F file=@path endpoint
API-->>Sh : 204
loop Poll
Sh->>API : GET buildInfo(_api_key, buildKey)
API-->>Sh : code==0 or still processing
end
```

**Diagram sources**
- [upload_pgyer.py:43-108](file://ciBuild/utils/upload_pgyer.py#L43-L108)
- [sh_pgyer_upload.sh:55-103](file://ciBuild/sh_pgyer_upload.sh#L55-L103)

**Section sources**
- [upload_pgyer.py:43-108](file://ciBuild/utils/upload_pgyer.py#L43-L108)
- [sh_pgyer_upload.sh:55-103](file://ciBuild/sh_pgyer_upload.sh#L55-L103)

### Orchestration and Reporting
The orchestration script coordinates pulling performance data and generating charts. Tools assist in local data preparation and visualization.

```mermaid
sequenceDiagram
participant User as "User"
participant Run as "run.sh"
participant Tool1 as "changeFile.py"
participant Tool2 as "csvToChart.py"
participant Tools as "tools/openPerf.bat"
User->>Run : execute
Run->>Tool1 : pull and prepare data
Run->>Tool2 : generate CPU/FPS/MEM/TEMP charts
User->>Tools : manual selection and execution
```

**Diagram sources**
- [run.sh:1-29](file://mobilePerf/run.sh#L1-L29)
- [openPerf.bat:1-7](file://mobilePerf/tools/openPerf.bat#L1-L7)

**Section sources**
- [run.sh:1-29](file://mobilePerf/run.sh#L1-L29)
- [openPerf.bat:1-7](file://mobilePerf/tools/openPerf.bat#L1-L7)

## Dependency Analysis
- Device layer depends on platform-specific adb availability and handles retries and timeouts.
- Monitors depend on ADB for data and on RuntimeData for persistent paths.
- Config and logging are shared across components.
- Build tools depend on external Walle CLI and Java runtime.
- Distribution utilities depend on network connectivity and remote APIs.

```mermaid
graph LR
CFG["config.py"] --> CPU["cpu_top.py"]
CFG --> LCAT["logcat.py"]
LOG["log.py"] --> CPU
LOG --> LCAT
UTL["utils.py"] --> CPU
UTL --> LCAT
GD["globaldata.py"] --> CPU
GD --> LCAT
ADB["androidDevice.py"] --> CPU
ADB --> LCAT
WALLE["batchChannelV2.py"] --> PY_UP["upload_pgyer.py"]
WALLE --> SH_UP["sh_pgyer_upload.sh"]
PY_UP --> SH_UP
```

**Diagram sources**
- [config.py:3-20](file://mobilePerf/perfCode/common/config.py#L3-L20)
- [log.py:22-75](file://mobilePerf/perfCode/common/log.py#L22-L75)
- [utils.py:10-156](file://mobilePerf/perfCode/common/utils.py#L10-L156)
- [globaldata.py:6-14](file://mobilePerf/perfCode/globaldata.py#L6-L14)
- [androidDevice.py:18-120](file://mobilePerf/perfCode/androidDevice.py#L18-L120)
- [cpu_top.py:206-383](file://mobilePerf/perfCode/cpu_top.py#L206-L383)
- [logcat.py:17-116](file://mobilePerf/perfCode/logcat.py#L17-L116)
- [batchChannelV2.py:21-70](file://appBuild/DaBao/batchChannelV2.py#L21-L70)
- [upload_pgyer.py:43-86](file://ciBuild/utils/upload_pgyer.py#L43-L86)
- [sh_pgyer_upload.sh:55-86](file://ciBuild/sh_pgyer_upload.sh#L55-L86)

**Section sources**
- [androidDevice.py:18-120](file://mobilePerf/perfCode/androidDevice.py#L18-L120)
- [cpu_top.py:206-383](file://mobilePerf/perfCode/cpu_top.py#L206-L383)
- [logcat.py:17-116](file://mobilePerf/perfCode/logcat.py#L17-L116)
- [batchChannelV2.py:21-70](file://appBuild/DaBao/batchChannelV2.py#L21-L70)
- [upload_pgyer.py:43-86](file://ciBuild/utils/upload_pgyer.py#L43-L86)
- [sh_pgyer_upload.sh:55-86](file://ciBuild/sh_pgyer_upload.sh#L55-L86)

## Performance Considerations
- CPU sampling frequency and intervals impact overhead; tune interval and timeout parameters to balance accuracy and load.
- Logcat buffering and file rotation prevent unbounded growth; ensure storage capacity and cleanup policies are adequate.
- ADB retries and timeouts mitigate transient failures; avoid excessive retry counts to prevent long stalls.
- CSV writing is batched; consider flushing strategies and disk I/O limits during extended runs.
- Network uploads in CI/CD are asynchronous; implement backoff and polling to reduce API pressure.

[No sources needed since this section provides general guidance]

## Troubleshooting Guide
Common failure modes and mitigations:
- ADB connectivity issues: device not found, offline, or port conflicts. The ADB wrapper recovers by killing/restarting the server and clearing conflicting processes.
- Command failures: ADB commands return non-zero exit codes; the wrapper logs errors and returns empty strings to signal failure.
- Logcat parsing: malformed lines are handled gracefully; ensure buffer parameters and filters are appropriate for the target device.
- Upload failures: Token retrieval or upload status checks may fail; scripts poll until completion or return explicit HTTP codes.

**Section sources**
- [androidDevice.py:121-176](file://mobilePerf/perfCode/androidDevice.py#L121-L176)
- [androidDevice.py:236-274](file://mobilePerf/perfCode/androidDevice.py#L236-L274)
- [logcat.py:85-116](file://mobilePerf/perfCode/logcat.py#L85-L116)
- [upload_pgyer.py:39-86](file://ciBuild/utils/upload_pgyer.py#L39-L86)
- [sh_pgyer_upload.sh:64-86](file://ciBuild/sh_pgyer_upload.sh#L64-L86)

## Conclusion
The repository integrates device-level data collection, build tooling, and distribution utilities into a cohesive pipeline. Clear separation of concerns, shared configuration/logging, and robust error handling enable reliable performance monitoring and automated delivery. Extending the system involves adding new monitors that adhere to the base interface, integrating additional distribution endpoints, and refining orchestration scripts.

[No sources needed since this section summarizes without analyzing specific files]

## Appendices

### Component Lifecycle Management
- Initialization: Monitors construct device connections and allocate resources (threads, file handles).
- Running: Monitors collect data at configured intervals, persisting to CSV or logs.
- Shutdown: Monitors stop threads, terminate subprocesses, and flush buffers.
- Cleanup: ADB wrapper ensures logcat processes are terminated and temporary artifacts are removed.

**Section sources**
- [cpu_top.py:249-263](file://mobilePerf/perfCode/cpu_top.py#L249-L263)
- [logcat.py:48-69](file://mobilePerf/perfCode/logcat.py#L48-L69)
- [androidDevice.py:414-422](file://mobilePerf/perfCode/androidDevice.py#L414-L422)

### Graceful Degradation Scenarios
- Device unavailable: ADB wrapper retries and falls back to safe defaults; collection loops skip missing data.
- API throttling: CI/CD upload scripts implement polling and backoff; continue after transient errors.
- Storage exhaustion: Log and CSV writers enforce size limits and rotation; ensure sufficient disk space.

**Section sources**
- [androidDevice.py:284-292](file://mobilePerf/perfCode/androidDevice.py#L284-L292)
- [cpu_top.py:277-280](file://mobilePerf/perfCode/cpu_top.py#L277-L280)
- [upload_pgyer.py:92-107](file://ciBuild/utils/upload_pgyer.py#L92-L107)