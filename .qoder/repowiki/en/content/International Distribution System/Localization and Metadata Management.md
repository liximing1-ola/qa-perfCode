# Localization and Metadata Management

<cite>
**Referenced Files in This Document**
- [locale_package.sh](file://overseaBuild/locale_package.sh)
- [build_app.sh](file://overseaBuild/build_app.sh)
- [build_apk.sh](file://overseaBuild/build_apk.sh)
- [build_ipa.sh](file://overseaBuild/build_ipa.sh)
- [google_translater.py](file://overseaBuild/upload_gp/google_translater.py)
- [upload_apks_with_listing.py](file://overseaBuild/upload_gp/upload_apks_with_listing.py)
- [ios_uploader.sh](file://overseaBuild/ios_uploader.sh)
- [wechat_notify.py](file://overseaBuild/wechat_notify.py)
- [git_utils.sh](file://overseaBuild/git_utils.sh)
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
This document describes the localization and metadata management system used to generate localized builds and release notes across multiple regions and languages. It covers:
- The locale_package.sh script for orchestrating multi-region builds
- Automated translation via GoogleTranslater for release notes
- Multi-language release note support for 18+ locales including English variants, Chinese dialects, Arabic, Indonesian, Korean, Malay, Thai, Turkish, and Vietnamese
- Metadata translation workflow, content validation, and character limit enforcement
- Practical examples of locale configuration, translation quality checks, and regional compliance requirements
- Best practices for localization and automated translation workflows

## Project Structure
The localization pipeline spans shell scripts for building Android/iOS artifacts and Python scripts for uploading to stores and translating release notes.

```mermaid
graph TB
LP["locale_package.sh"] --> BA["build_app.sh"]
BA --> APK["build_apk.sh"]
BA --> IPA["build_ipa.sh"]
APK --> GPY["upload_apks_with_listing.py"]
GPY --> GT["google_translater.py"]
IPA --> IOS["ios_uploader.sh"]
BA --> WECHAT["wechat_notify.py"]
BA --> GIT["git_utils.sh"]
```

**Diagram sources**
- [locale_package.sh:1-32](file://overseaBuild/locale_package.sh#L1-L32)
- [build_app.sh:1-97](file://overseaBuild/build_app.sh#L1-L97)
- [build_apk.sh:1-60](file://overseaBuild/build_apk.sh#L1-L60)
- [build_ipa.sh:1-74](file://overseaBuild/build_ipa.sh#L1-L74)
- [upload_apks_with_listing.py:1-198](file://overseaBuild/upload_gp/upload_apks_with_listing.py#L1-L198)
- [google_translater.py:1-38](file://overseaBuild/upload_gp/google_translater.py#L1-L38)
- [ios_uploader.sh:1-81](file://overseaBuild/ios_uploader.sh#L1-L81)
- [wechat_notify.py:1-146](file://overseaBuild/wechat_notify.py#L1-L146)
- [git_utils.sh:1-90](file://overseaBuild/git_utils.sh#L1-L90)

**Section sources**
- [locale_package.sh:1-32](file://overseaBuild/locale_package.sh#L1-L32)
- [build_app.sh:1-97](file://overseaBuild/build_app.sh#L1-L97)

## Core Components
- locale_package.sh: Interactive orchestration script to collect build parameters and invoke build_app.sh with platform, type, version, debug mode, CI number, and release notes.
- build_app.sh: Central build controller that coordinates Android and iOS builds, handles store vs. non-store packaging, and notifies stakeholders.
- build_apk.sh: Flutter-based Android build with flavor banban_locale, optional debug mode, and store bundle generation.
- build_ipa.sh: Flutter-based iOS build with ad-hoc export options and store submission via ios_uploader.sh.
- upload_apks_with_listing.py: Uploads AAB to Google Play, translates release notes into multiple locales, validates lengths, and commits listings.
- google_translater.py: Provides translation service abstraction for release note text.
- ios_uploader.sh: Validates and uploads iOS artifacts to Apple servers.
- wechat_notify.py: Sends build notifications to enterprise WeChat channels.
- git_utils.sh: Utility functions for branch existence checks and safe checkout/pull workflows.

**Section sources**
- [locale_package.sh:1-32](file://overseaBuild/locale_package.sh#L1-L32)
- [build_app.sh:1-97](file://overseaBuild/build_app.sh#L1-L97)
- [build_apk.sh:1-60](file://overseaBuild/build_apk.sh#L1-L60)
- [build_ipa.sh:1-74](file://overseaBuild/build_ipa.sh#L1-L74)
- [upload_apks_with_listing.py:1-198](file://overseaBuild/upload_gp/upload_apks_with_listing.py#L1-L198)
- [google_translater.py:1-38](file://overseaBuild/upload_gp/google_translater.py#L1-L38)
- [ios_uploader.sh:1-81](file://overseaBuild/ios_uploader.sh#L1-L81)
- [wechat_notify.py:1-146](file://overseaBuild/wechat_notify.py#L1-L146)
- [git_utils.sh:1-90](file://overseaBuild/git_utils.sh#L1-L90)

## Architecture Overview
The system integrates user-driven orchestration with automated build and store upload processes. Release notes are translated per locale and validated for length constraints before committing to Google Play.

```mermaid
sequenceDiagram
participant User as "User"
participant LP as "locale_package.sh"
participant BA as "build_app.sh"
participant APK as "build_apk.sh"
participant GPY as "upload_apks_with_listing.py"
participant GT as "google_translater.py"
User->>LP : Provide platform/type/version/debug/CInum/releaseNotes
LP->>BA : Invoke with parameters
BA->>APK : Build Android (debug/release/store)
APK->>GPY : Upload AAB and pass releaseNotes
GPY->>GT : Translate releaseNotes to target locales
GT-->>GPY : Translated texts
GPY->>GPY : Validate length <= 500 per locale
GPY-->>BA : Commit listing updates
BA-->>User : Notify via WeChat
```

**Diagram sources**
- [locale_package.sh:1-32](file://overseaBuild/locale_package.sh#L1-L32)
- [build_app.sh:1-97](file://overseaBuild/build_app.sh#L1-L97)
- [build_apk.sh:1-60](file://overseaBuild/build_apk.sh#L1-L60)
- [upload_apks_with_listing.py:147-193](file://overseaBuild/upload_gp/upload_apks_with_listing.py#L147-L193)
- [google_translater.py:11-21](file://overseaBuild/upload_gp/google_translater.py#L11-L21)

## Detailed Component Analysis

### locale_package.sh
- Purpose: Collects build parameters from the user and invokes build_app.sh with platform, type, version, debug model, CI number, and release notes.
- Inputs: Platform selection (All/Android/iOS), build type (debug/release/store), versionName, versionCode, EnableDebug flag, CI number, and optional releaseNotes.
- Behavior: Maps numeric selections to human-readable values and passes them downstream.

```mermaid
flowchart TD
Start(["Start"]) --> P1["Prompt platform"]
P1 --> P2["Prompt build type"]
P2 --> P3["Prompt versionName/versionCode"]
P3 --> P4["Prompt EnableDebug"]
P4 --> P5{"Build type is store?"}
P5 --> |Yes| P6["Prompt releaseNotes"]
P5 --> |No| P7["Use default releaseNotes"]
P6 --> Call["Call build_app.sh with params"]
P7 --> Call
Call --> End(["End"])
```

**Diagram sources**
- [locale_package.sh:5-31](file://overseaBuild/locale_package.sh#L5-L31)

**Section sources**
- [locale_package.sh:1-32](file://overseaBuild/locale_package.sh#L1-L32)

### build_app.sh
- Purpose: Orchestrates Android and iOS builds, manages store vs. non-store packaging, and sends notifications.
- Key behaviors:
  - Determines platform and executes corresponding build script.
  - For store builds, verifies presence of AAB/APK artifacts before proceeding.
  - Generates changelog from Git history and notifies via WeChat.

```mermaid
flowchart TD
S(["Start"]) --> Detect["Detect platform and type"]
Detect --> Android{"Platform is Android?"}
Android --> |Yes| APKBuild["Run build_apk.sh"]
Android --> |No| iOS{"Platform is iOS?"}
iOS --> |Yes| IPABuild["Run build_ipa.sh"]
iOS --> |No| Both["Run both Android and iOS builds"]
APKBuild --> StoreCheckA{"Type is store?"}
IPABuild --> StoreCheckI{"Type is store?"}
StoreCheckA --> |Yes| VerifyAAB["Verify AAB exists"]
StoreCheckI --> |Yes| VerifyIPA["Verify IPA exists"]
VerifyAAB --> Notify["Send WeChat notification"]
VerifyIPA --> Notify
Both --> Notify
Notify --> E(["End"])
```

**Diagram sources**
- [build_app.sh:39-87](file://overseaBuild/build_app.sh#L39-L87)

**Section sources**
- [build_app.sh:1-97](file://overseaBuild/build_app.sh#L1-L97)

### build_apk.sh
- Purpose: Builds Android artifacts using Flutter with flavor banban_locale and optional debug mode.
- Store flow:
  - Cleans Flutter cache, builds appbundle, renames output, and triggers Google Play upload with release notes.
- Debug/release flows:
  - Builds APK, optionally uploads to a third-party service, and moves artifacts to standardized locations.

```mermaid
flowchart TD
SA(["Start APK build"]) --> Type{"Build type"}
Type --> |debug| FDebug["flutter build apk (profile)"]
Type --> |release| FRel["flutter build apk (release)"]
Type --> |store| FAB["flutter build appbundle"]
FAB --> MoveAAB["Move AAB to outputs/bundle"]
MoveAAB --> GPYCall["Invoke upload_apks_with_listing.py"]
FDebug --> PostDebug["Optional upload and move"]
FRel --> PostRel["Optional upload and move"]
GPYCall --> EndA(["End"])
PostDebug --> EndA
PostRel --> EndA
```

**Diagram sources**
- [build_apk.sh:11-59](file://overseaBuild/build_apk.sh#L11-L59)

**Section sources**
- [build_apk.sh:1-60](file://overseaBuild/build_apk.sh#L1-L60)

### build_ipa.sh
- Purpose: Builds iOS artifacts using Flutter and exports ad-hoc IPAs; store builds are delegated to ios_uploader.sh.
- Includes Firebase Crashlytics symbols upload when available.

```mermaid
flowchart TD
SI(["Start IPA build"]) --> TypeI{"Build type"}
TypeI --> |debug| FIDebug["flutter build ipa (profile)"]
TypeI --> |release| FIRel["flutter build ipa (release)"]
TypeI --> |store| Store["Execute store-specific steps"]
FIDebug --> ExportD["xcodebuild export ad-hoc"]
FIRel --> ExportR["xcodebuild export ad-hoc"]
Store --> IU["Call ios_uploader.sh"]
ExportD --> EndI(["End"])
ExportR --> EndI
IU --> EndI
```

**Diagram sources**
- [build_ipa.sh:40-73](file://overseaBuild/build_ipa.sh#L40-L73)

**Section sources**
- [build_ipa.sh:1-74](file://overseaBuild/build_ipa.sh#L1-L74)

### upload_apks_with_listing.py
- Purpose: Uploads AAB to Google Play, translates release notes into 18+ locales, enforces 500-character limit, and commits listings.
- Supported locales include English variants, Chinese dialects, Arabic, Indonesian, Korean, Malay, Thai, Turkish, and Vietnamese.
- Translation logic:
  - English variants reuse the original release note text.
  - For locales with region codes (e.g., zh-TW), specific target languages are selected.
  - Other locales are translated using the target language code.
- Character limit enforcement: Exits if any translated note exceeds 500 characters.

```mermaid
flowchart TD
UStart(["Upload AAB"]) --> ParseArgs["Parse package, AAB path, draft name, release note"]
ParseArgs --> UploadAAB["Upload AAB to Google Play"]
UploadAAB --> GetVC["Get version code"]
GetVC --> LoopNotes["Iterate supported locales"]
LoopNotes --> Skip{"Already translated?"}
Skip --> |Yes| Next["Next locale"]
Skip --> |No| EnCheck{"Is English variant?"}
EnCheck --> |Yes| AssignEN["Assign original release note"]
EnCheck --> |No| HasDash{"Has region suffix?"}
HasDash --> |Yes| ZHCheck{"Is zh-TW/HK/TW?"}
ZHCheck --> |Yes| TransTW["Translate to zh-TW"]
ZHCheck --> |No| TransLang["Translate to base language"]
HasDash --> |No| TransOther["Translate to target language"]
AssignEN --> LenCheck["Measure length"]
TransTW --> LenCheck
TransLang --> LenCheck
TransOther --> LenCheck
LenCheck --> TooLong{"Length > 500?"}
TooLong --> |Yes| ExitErr["Exit with error"]
TooLong --> |No| SetText["Set translated text"]
SetText --> Next
Next --> Done(["Commit listing with release notes"])
```

**Diagram sources**
- [upload_apks_with_listing.py:147-193](file://overseaBuild/upload_gp/upload_apks_with_listing.py#L147-L193)

**Section sources**
- [upload_apks_with_listing.py:54-73](file://overseaBuild/upload_gp/upload_apks_with_listing.py#L54-L73)
- [upload_apks_with_listing.py:147-193](file://overseaBuild/upload_gp/upload_apks_with_listing.py#L147-L193)

### google_translater.py
- Purpose: Encapsulates translation functionality with a simple interface.
- Methods:
  - translate(text, targetLan): Posts to a configured endpoint and returns translated text if available; otherwise returns the original text.

```mermaid
classDiagram
class GoogleTranslater {
+translate(text, targetLan) string
}
```

**Diagram sources**
- [google_translater.py:11-21](file://overseaBuild/upload_gp/google_translater.py#L11-L21)

**Section sources**
- [google_translater.py:1-38](file://overseaBuild/upload_gp/google_translater.py#L1-L38)

### ios_uploader.sh
- Purpose: Validates and uploads iOS artifacts to Apple servers using Application Loader.
- Functions:
  - validate_and_upload(): Validates the IPA, then uploads if validation succeeds.
  - upload_ipa(): Performs the upload operation.

```mermaid
flowchart TD
VStart(["Validate IPA"]) --> Validate["xcrun altool --validate-app"]
Validate --> Valid{"Validation success?"}
Valid --> |Yes| Upload["xcrun altool --upload-app"]
Valid --> |No| Fail["Report failure"]
Upload --> DoneV(["Done"])
Fail --> DoneV
```

**Diagram sources**
- [ios_uploader.sh:26-45](file://overseaBuild/ios_uploader.sh#L26-L45)

**Section sources**
- [ios_uploader.sh:1-81](file://overseaBuild/ios_uploader.sh#L1-L81)

### wechat_notify.py
- Purpose: Sends build notifications to enterprise WeChat channels with links to download artifacts and contextual information.
- Notifies on build start, completion, and errors, truncating long change logs to a maximum length.

```mermaid
flowchart TD
WNStart(["Receive build args"]) --> TypeN{"Build event type"}
TypeN --> |Start| SendStart["Send start notification"]
TypeN --> |Success| SendSuccess["Send success with links"]
TypeN --> |Error| SendError["Send error markdown"]
SendStart --> EndWN(["End"])
SendSuccess --> EndWN
SendError --> EndWN
```

**Diagram sources**
- [wechat_notify.py:22-145](file://overseaBuild/wechat_notify.py#L22-L145)

**Section sources**
- [wechat_notify.py:1-146](file://overseaBuild/wechat_notify.py#L1-L146)

### git_utils.sh
- Purpose: Utilities for branch existence checks and safe checkout/pull operations, ensuring consistent repository state during builds.

```mermaid
flowchart TD
GStart(["Git Utils"]) --> Local{"Local branch exists?"}
Local --> |Yes| Checkout["Checkout and pull"]
Local --> |No| Remote{"Remote branch exists?"}
Remote --> |Yes| FetchPull["Fetch and checkout"]
Remote --> |No| Error["Report not found"]
Checkout --> EndG(["End"])
FetchPull --> EndG
Error --> EndG
```

**Diagram sources**
- [git_utils.sh:3-90](file://overseaBuild/git_utils.sh#L3-L90)

**Section sources**
- [git_utils.sh:1-90](file://overseaBuild/git_utils.sh#L1-L90)

## Dependency Analysis
- locale_package.sh depends on build_app.sh for execution.
- build_app.sh depends on build_apk.sh and build_ipa.sh for platform-specific builds.
- build_apk.sh depends on upload_apks_with_listing.py for store uploads.
- upload_apks_with_listing.py depends on google_translater.py for translations.
- build_app.sh depends on wechat_notify.py for notifications.
- git_utils.sh supports repository state management across the pipeline.

```mermaid
graph LR
LP["locale_package.sh"] --> BA["build_app.sh"]
BA --> APK["build_apk.sh"]
BA --> IPA["build_ipa.sh"]
APK --> GPY["upload_apks_with_listing.py"]
GPY --> GT["google_translater.py"]
BA --> WECHAT["wechat_notify.py"]
BA --> GIT["git_utils.sh"]
```

**Diagram sources**
- [locale_package.sh:1-32](file://overseaBuild/locale_package.sh#L1-L32)
- [build_app.sh:1-97](file://overseaBuild/build_app.sh#L1-L97)
- [build_apk.sh:1-60](file://overseaBuild/build_apk.sh#L1-L60)
- [build_ipa.sh:1-74](file://overseaBuild/build_ipa.sh#L1-L74)
- [upload_apks_with_listing.py:1-198](file://overseaBuild/upload_gp/upload_apks_with_listing.py#L1-L198)
- [google_translater.py:1-38](file://overseaBuild/upload_gp/google_translater.py#L1-L38)
- [wechat_notify.py:1-146](file://overseaBuild/wechat_notify.py#L1-L146)
- [git_utils.sh:1-90](file://overseaBuild/git_utils.sh#L1-L90)

**Section sources**
- [locale_package.sh:1-32](file://overseaBuild/locale_package.sh#L1-L32)
- [build_app.sh:1-97](file://overseaBuild/build_app.sh#L1-L97)
- [build_apk.sh:1-60](file://overseaBuild/build_apk.sh#L1-L60)
- [build_ipa.sh:1-74](file://overseaBuild/build_ipa.sh#L1-L74)
- [upload_apks_with_listing.py:1-198](file://overseaBuild/upload_gp/upload_apks_with_listing.py#L1-L198)
- [google_translater.py:1-38](file://overseaBuild/upload_gp/google_translater.py#L1-L38)
- [wechat_notify.py:1-146](file://overseaBuild/wechat_notify.py#L1-L146)
- [git_utils.sh:1-90](file://overseaBuild/git_utils.sh#L1-L90)

## Performance Considerations
- Translation throughput: The translation loop iterates over 18+ locales; batching or caching repeated translations could reduce latency.
- Network reliability: The upload process and translation calls depend on external APIs; adding retry logic and timeouts improves robustness.
- Artifact size: Large AAB/APK sizes increase upload time; ensure compression and chunked uploads are optimized.
- Notification payload limits: WeChat message truncation prevents oversized notifications; keep summaries concise.

[No sources needed since this section provides general guidance]

## Troubleshooting Guide
- Build failures:
  - Android store builds require AAB presence; verify outputs and paths.
  - iOS builds require proper provisioning profiles and export options; validate Xcode archive/export steps.
- Translation errors:
  - If translated text is empty, the translation endpoint may be unreachable or invalid; confirm network connectivity and endpoint configuration.
- Length violations:
  - Release notes exceeding 500 characters per locale cause immediate exit; shorten the source note or split content across multiple notes.
- Notifications:
  - If WeChat notifications fail, check webhook URL and payload formatting; ensure message length constraints are respected.

**Section sources**
- [build_app.sh:41-58](file://overseaBuild/build_app.sh#L41-L58)
- [build_ipa.sh:15-35](file://overseaBuild/build_ipa.sh#L15-L35)
- [upload_apks_with_listing.py:166-169](file://overseaBuild/upload_gp/upload_apks_with_listing.py#L166-L169)
- [wechat_notify.py:133-145](file://overseaBuild/wechat_notify.py#L133-L145)

## Conclusion
The localization and metadata management system automates multi-locale builds and release note translation for Google Play and iOS distribution. By integrating user-driven orchestration, robust build scripts, and translation/validation workflows, teams can efficiently manage global releases while enforcing regional compliance and content limits.

[No sources needed since this section summarizes without analyzing specific files]

## Appendices

### Practical Examples

- Locale configuration for release notes:
  - Supported locales include English variants (e.g., en-US, en-GB), Chinese dialects (e.g., zh-CN, zh-TW), and others (e.g., ar, id, ko-KR, ms, th, tr-TR, vi).
  - Ensure the source release note is concise and culturally appropriate before translation.

- Translation quality checks:
  - Validate translated notes for accuracy and tone; consider manual review for critical markets.
  - Monitor translation endpoint availability and handle transient failures gracefully.

- Regional compliance requirements:
  - Respect character limits (<= 500 per locale) for store listings.
  - Adapt content to local idioms and avoid restricted terms; verify platform-specific policies.

[No sources needed since this section provides general guidance]