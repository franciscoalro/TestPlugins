# CloudStream Plugin Repository Comparison Report

## Executive Summary

**ROOT CAUSE IDENTIFIED:** The franciscoalro repository plugins are incorrectly packaged as **Android Library (AAR) format** instead of the **CloudStream plugin format**. This is why CloudStream shows "Plugin not found" error when trying to install.

---

## Repository URLs

### Working Repository (saimuelbr)
- repo.json: https://raw.githubusercontent.com/saimuelbr/saimuelrepo/main/builds/repo.json
- plugins.json: https://raw.githubusercontent.com/saimuelbr/saimuelrepo/main/builds/plugins.json

### Broken Repository (franciscoalro)
- repo.json: https://raw.githubusercontent.com/franciscoalro/CloudstreamRepo/main/builds/repo.json
- plugins.json: https://raw.githubusercontent.com/franciscoalro/CloudstreamRepo/main/builds/plugins.json

---

## 1. repo.json Comparison

### SAIMUEL (Working)
```json
{
  "name": "saimuel repo",
  "iconUrl": "https://raw.githubusercontent.com/saimuelbr/sweettheartt/refs/heads/main/RepoIcon.png",
  "description": "saimuelbr repository",
  "manifestVersion": 1,
  "pluginLists": [
    "https://raw.githubusercontent.com/saimuelbr/saimuelrepo/refs/heads/main/builds/plugins.json"
  ]
}
```

### FRANCISCO (Broken)
```json
{
    "name":  "BRCloudStream Repo",
    "iconUrl":  "https://raw.githubusercontent.com/franciscoalro/CloudstreamRepo/main/icon.png",
    "description":  "RepositÃ³rio brasileiro com filmes, sÃ©ries, animes, doramas, novelas e TV ao vivo",
    "manifestVersion":  1,
    "pluginLists":  [
                        "https://raw.githubusercontent.com/franciscoalro/CloudstreamRepo/refs/heads/main/builds/plugins.json"
                    ]
}
```

**DIFFERENCES:**
- Minor formatting differences (spacing, indentation)
- Character encoding issues in francisco's file ("RepositÃ³rio" instead of "Repositório")
- Both have same `manifestVersion: 1`
- Both have valid `pluginLists` URLs

**VERDICT:** repo.json files are functionally equivalent. NOT the cause of the issue.

---

## 2. plugins.json Comparison

### Key Entry Comparison (NetCine vs MaxSeries)

| Field | SAIMUEL NetCine | FRANCISCO MaxSeries |
|-------|-----------------|---------------------|
| name | "NetCine" | "MaxSeries" |
| internalName | "NetCine" | "MaxSeries" |
| version | 7 | 256 |
| apiVersion | 4 | 1 |
| fileSize | 17609 | 705175 |
| language | "pt-br" | "pt" |
| status | 1 | 1 |
| jarUrl | .../NetCine.jar | .../MaxSeries.jar |
| url | .../NetCine.cs3 | .../MaxSeries.cs3 |

**DIFFERENCES:**
- Language code: "pt-br" vs "pt" (both should work)
- apiVersion: 4 vs 1 (not the root cause)
- fileSize reflects actual file sizes

**VERDICT:** plugins.json entries are correctly formatted. NOT the cause of the issue.

---

## 3. JAR File Comparison

### File Sizes
| Repository | Plugin | File Size |
|------------|--------|-----------|
| saimuelbr | NetCine.jar | 65,047 bytes |
| franciscoalro | MaxSeries.jar | 705,175 bytes |

### Internal Structure - SAIMUEL NetCine.jar
```
Total files: 12
Total size: 62,953 bytes

Structure:
- com/NetCine/ (11 .class files)
- META-INF/NetCine_debug.kotlin_module
```

### Internal Structure - FRANCISCO MaxSeries.jar
```
Total files: 281
Total size: 1,552,147 bytes

Structure:
- com/franciscoalro/maxseries/extractors/ (many .class files)
- com/franciscoalro/maxseries/resolver/ (.class files)
- com/franciscoalro/maxseries/utils/ (.class files)
- META-INF/MaxSeries_release.kotlin_module
```

**NOTE:** Both JAR files are valid Java/Kotlin compiled bytecode. The JAR files themselves are NOT the issue.

---

## 4. .CS3 File Comparison (THE ROOT CAUSE)

### CloudStream Plugin Format (CORRECT)

**SAIMUEL NetCine.cs3 (Working):**
```
Archive contents:
- classes.dex (36,344 bytes) - Android Dalvik Executable
- manifest.json (104 bytes) - Plugin metadata

manifest.json content:
{
  "pluginClassName": "com.NetCine.NetCineProvider",
  "name": "NetCine",
  "version": 1,
  "requiresResources": false
}
```

**LOCAL MaxSeries.cs3 (Working):**
```
Archive contents:
- classes.dex (579,492 bytes) - Android Dalvik Executable
- manifest.json (124 bytes) - Plugin metadata

manifest.json content:
{
  "requiresResources": false,
  "version": 223,
  "pluginClassName": "com.franciscoalro.maxseries.MaxSeriesPlugin",
  "name": "MaxSeries"
}
```

### Android Library Format (INCORRECT)

**FRANCISCO MaxSeries.cs3 (Broken):**
```
Archive contents:
- AndroidManifest.xml (214 bytes) - Android library manifest
- classes.jar (705,175 bytes) - Java classes in JAR format (NOT DEX!)
- R.txt (0 bytes) - Android resources
- META-INF/com/android/build/gradle/aar-metadata.properties (156 bytes)

aar-metadata.properties content:
aarFormatVersion=1.0
aarMetadataVersion=1.0
minCompileSdk=1
minCompileSdkExtension=0
minAndroidGradlePluginVersion=1.0.0
coreLibraryDesugaringEnabled=false
```

**FRANCISCO AnimesOnlineCC.cs3 (Also Broken):**
```
Archive contents:
- AndroidManifest.xml (204 bytes)
- classes.jar (28,951 bytes)
- R.txt (0 bytes)
- META-INF/com/android/build/gradle/aar-metadata.properties (156 bytes)

NO manifest.json!
```

**FRANCISCO PobreFlix.cs3 (Also Broken):**
```
Archive contents:
- AndroidManifest.xml (204 bytes)
- classes.jar (35,241 bytes)
- R.txt (0 bytes)
- META-INF/com/android/build/gradle/aar-metadata.properties (156 bytes)

NO manifest.json!
```

---

## 5. Critical Differences Summary

| Aspect | Working (saimuelbr) | Broken (franciscoalro) |
|--------|---------------------|------------------------|
| **File Format** | CloudStream Plugin | Android Library (AAR) |
| **Main bytecode** | classes.dex | classes.jar |
| **Metadata file** | manifest.json | AndroidManifest.xml |
| **Plugin metadata** | Present in manifest.json | MISSING |
| **Format detected** | DEX (dex\n magic) | JAR (PK magic) |
| **CloudStream loads?** | YES | NO - "Plugin not found" |

---

## 6. Technical Explanation

### How CloudStream Loads Plugins

1. CloudStream downloads the `.cs3` file
2. It opens the ZIP archive
3. It looks for `manifest.json` at the root level
4. It parses `manifest.json` to get:
   - `pluginClassName`: The main plugin entry point class
   - `name`: Plugin display name
   - `version`: Plugin version
   - `requiresResources`: Whether resources are needed
5. It loads `classes.dex` which contains the compiled Dalvik bytecode
6. It instantiates the plugin class and registers it

### Why Francisco's Plugins Fail

1. CloudStream downloads the `.cs3` file
2. It opens the ZIP archive
3. It looks for `manifest.json` at the root level
4. **FAIL:** `manifest.json` is NOT present
5. CloudStream cannot determine the plugin class name
6. **ERROR:** "Plugin not found"

Additionally, even if there was a manifest.json:
- `classes.jar` contains JVM bytecode (for desktop Java)
- CloudStream/Android needs `classes.dex` (Dalvik bytecode for Android)
- These are completely different formats

---

## 7. How to Fix

The build process needs to be corrected to generate CloudStream plugin format instead of Android Library format.

### Current Build (Wrong)
```kotlin
// build.gradle.kts is likely producing:
// - Android Library (AAR) 
// - Contains classes.jar
// - Contains AndroidManifest.xml
```

### Correct Build
```kotlin
// Should produce:
// - CloudStream Plugin (CS3)
// - Contains classes.dex (converted from .class files)
// - Contains manifest.json
```

### Fix Steps

1. **Update build.gradle.kts:**
   - Change from `com.android.library` to appropriate plugin configuration
   - Add dexing step to convert .class files to .dex
   - Generate manifest.json during build

2. **Alternative workaround:**
   - Extract classes.jar from the .cs3
   - Convert classes.jar to classes.dex using dx/d8 tool
   - Create manifest.json manually
   - Repackage as .cs3

3. **Use correct build configuration:**
   Reference the saimuelbr repository's build configuration as a working example.

---

## 8. Additional Observations

### File Size Discrepancy
- plugins.json says MaxSeries fileSize: 705,175
- Actual MaxSeries.cs3 file size: 653,406
- Actual classes.jar inside: 705,175
- The fileSize in plugins.json refers to the classes.jar, not the .cs3 file itself

### Naming Confusion
- Both .jar and .cs3 files exist
- The .cs3 is what CloudStream actually downloads and installs
- The .jar might be an intermediate build artifact
- For saimuelbr: .jar files are simple class containers
- For franciscoalro: .jar files contain the actual code, .cs3 files wrap them as AAR

### Character Encoding
- franciscoalro's files have encoding issues ("RepositÃ³rio" instead of "Repositório")
- This suggests Windows-1252 / UTF-8 mismatch in the build process

---

## Conclusion

**The franciscoalro repository plugins are completely non-functional in CloudStream because they are packaged as Android Library (AAR) format instead of CloudStream plugin format.**

The fix requires changing the build configuration to:
1. Generate `classes.dex` instead of `classes.jar`
2. Include `manifest.json` at the root level
3. Remove Android-specific files (AndroidManifest.xml, R.txt, aar-metadata.properties)

This is a build configuration issue, not a code issue. The Kotlin source code is likely fine - it's just being packaged incorrectly.
