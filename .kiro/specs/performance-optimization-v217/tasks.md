# Performance Optimization v217 - Implementation Tasks

## 📋 Task Overview

This document breaks down the performance optimization implementation into actionable tasks following the design document.

**Total Estimated Time:** 2-3 hours

---

## Phase 1: WebView Optimization (45-60 min)

### 1.1 Create WebViewPool Singleton
- [x] Create new file `MaxSeries/src/main/kotlin/com/franciscoalro/maxseries/utils/WebViewPool.kt`
- [x] Implement singleton pattern with `@Synchronized` methods
- [x] Add `acquire()` method to get/create WebView
- [x] Add `release()` method to return WebView to pool
- [x] Add `destroy()` method for cleanup
- [x] Add performance logging (measure time)
- [x] Test: Verify first call ~100ms, subsequent calls <10ms

**Files to create:**
- `MaxSeries/src/main/kotlin/com/franciscoalro/maxseries/utils/WebViewPool.kt`

**Success Criteria:**
- WebView creation time: <100ms (reuse)
- Memory usage: ~10MB per WebView
- Proper cleanup on destroy

---

### 1.2 Optimize WebView Settings
- [x] Update `createOptimizedWebView()` in WebViewPool
- [x] Set `blockNetworkImage = true` (don't load images)
- [x] Set `cacheMode = WebSettings.LOAD_NO_CACHE`
- [x] Set `setRenderPriority(WebSettings.RenderPriority.HIGH)`
- [x] Keep existing security settings
- [x] Test: Measure page load time improvement

**Files to modify:**
- `MaxSeries/src/main/kotlin/com/franciscoalro/maxseries/utils/WebViewPool.kt`

**Success Criteria:**
- Image loading disabled: ~500ms saved
- Cache overhead removed: ~200ms saved
- Total page load: <1s

---

### 1.3 Integrate WebViewPool with PlayerEmbedAPIExtractorManual
- [x] Import WebViewPool in PlayerEmbedAPIExtractorManual
- [x] Replace `WebView(context)` with `WebViewPool.acquire(context)`
- [x] Add `WebViewPool.release(webView)` in cleanup
- [x] Add `WebViewPool.destroy()` on final cleanup
- [x] Update logging to show pool usage
- [x] Test: Verify WebView reuse works

**Files to modify:**
- `MaxSeries/src/main/kotlin/com/franciscoalro/maxseries/extractors/PlayerEmbedAPIExtractorManual.kt`

**Changes:**
```kotlin
// BEFORE (line ~60)
val webView = WebView(context)

// AFTER
val webView = WebViewPool.acquire(context)

// Add in cleanup (line ~90)
WebViewPool.release(webView)
```

**Success Criteria:**
- WebView creation: 1-2s → <100ms
- Total extraction time: 3-5s → <2s

---

## Phase 2: Timeout Reduction (30-45 min)

### 2.1 Update Timeout Constants
- [x] Change `TIMEOUT_SECONDS` from 60L to 30L
- [x] Add new constant `QUICK_TIMEOUT_SECONDS = 15L`
- [x] Add new constant `MAX_RETRIES = 2`
- [x] Update companion object in PlayerEmbedAPIExtractorManual

**Files to modify:**
- `MaxSeries/src/main/kotlin/com/franciscoalro/maxseries/extractors/PlayerEmbedAPIExtractorManual.kt`

**Changes:**
```kotlin
// Line ~25 (companion object)
companion object {
    private const val TAG = "PlayerEmbedAPI"
    private const val TIMEOUT_SECONDS = 30L  // Was 60L
    private const val QUICK_TIMEOUT_SECONDS = 15L  // NEW
    private const val MAX_RETRIES = 2  // NEW
}
```

**Success Criteria:**
- Timeout reduced: 60s → 30s (50% reduction)
- Constants properly defined

---

### 2.2 Implement Adaptive Timeout with Retry
- [x] Wrap extraction logic in retry loop
- [x] Use `TIMEOUT_SECONDS` for first attempt
- [x] Use `QUICK_TIMEOUT_SECONDS` for retry
- [x] Add attempt counter and logging
- [x] Update error messages to show attempt number
- [x] Test: Verify timeout behavior

**Files to modify:**
- `MaxSeries/src/main/kotlin/com/franciscoalro/maxseries/extractors/PlayerEmbedAPIExtractorManual.kt`

**Changes:**
```kotlin
// Replace getUrl() method (line ~40)
override suspend fun getUrl(...) {
    var attempt = 0
    var success = false
    
    while (attempt < MAX_RETRIES && !success) {
        attempt++
        
        val timeout = if (attempt == 1) TIMEOUT_SECONDS else QUICK_TIMEOUT_SECONDS
        Log.d(TAG, "🔄 Tentativa $attempt/$MAX_RETRIES (timeout: ${timeout}s)")
        
        // ... existing WebView logic ...
        
        val captured = latch.await(timeout, TimeUnit.SECONDS)
        
        if (captured && finalUrl != null) {
            success = true
            // ... callback ...
        } else {
            Log.w(TAG, "⏱️ Timeout após ${timeout}s (tentativa $attempt)")
        }
    }
}
```

**Success Criteria:**
- First attempt: 30s timeout
- Retry: 15s timeout
- Max total time: 45s (vs 60s before)

---

### 2.3 Improve Error Messages
- [x] Add descriptive timeout messages
- [x] Show attempt number in logs
- [x] Suggest user action on timeout
- [x] Log fallback to next extractor

**Files to modify:**
- `MaxSeries/src/main/kotlin/com/franciscoalro/maxseries/extractors/PlayerEmbedAPIExtractorManual.kt`

**Success Criteria:**
- Clear error messages
- User-friendly suggestions

---

## Phase 3: Persistent Cache (60-75 min)

### 3.1 Create PersistentVideoCache Class
- [x] Create new file `MaxSeries/src/main/kotlin/com/franciscoalro/maxseries/utils/PersistentVideoCache.kt`
- [x] Implement singleton pattern with getInstance()
- [x] Add SharedPreferences storage
- [x] Define CacheEntry data class with @Serializable
- [x] Add constants: MAX_SIZE=100, TTL_MINUTES=30L
- [x] Test: Verify basic put/get works

**Files to create:**
- `MaxSeries/src/main/kotlin/com/franciscoalro/maxseries/utils/PersistentVideoCache.kt`

**Success Criteria:**
- Singleton pattern works
- SharedPreferences storage functional
- CacheEntry serialization works

---

### 3.2 Implement Cache Operations
- [x] Implement `put()` method with LRU eviction
- [x] Implement `get()` method with TTL check
- [x] Implement `cleanExpired()` to remove old entries
- [x] Implement `removeOldest()` for LRU
- [x] Add `size()` method
- [x] Add `clear()` method
- [x] Test: Verify LRU and TTL work

**Files to modify:**
- `MaxSeries/src/main/kotlin/com/franciscoalro/maxseries/utils/PersistentVideoCache.kt`

**Success Criteria:**
- TTL: 30min expiration works
- LRU: Oldest entries removed when full
- Max size: 100 URLs enforced

---

### 3.3 Add Statistics Tracking
- [x] Add hit/miss counters
- [x] Implement `getHitRate()` method
- [x] Implement `getStats()` method
- [x] Add logging for cache hits/misses
- [x] Test: Verify statistics are accurate

**Files to modify:**
- `MaxSeries/src/main/kotlin/com/franciscoalro/maxseries/utils/PersistentVideoCache.kt`

**Success Criteria:**
- Hit rate calculation correct
- Statistics logged properly
- Target hit rate: >60%

---

### 3.4 Integrate with VideoUrlCache
- [x] Add `persistentCache` property to VideoUrlCache
- [x] Add `init()` method to initialize PersistentVideoCache
- [x] Update `put()` to use PersistentVideoCache
- [x] Update `get()` to use PersistentVideoCache
- [x] Add `getStats()` wrapper method
- [x] Keep backward compatibility
- [x] Test: Verify integration works

**Files to modify:**
- `MaxSeries/src/main/kotlin/com/franciscoalro/maxseries/utils/VideoUrlCache.kt`

**Changes:**
```kotlin
// Add at top of VideoUrlCache object
private var persistentCache: PersistentVideoCache? = null

fun init(context: Context) {
    persistentCache = PersistentVideoCache.getInstance(context)
}

// Update put() method
fun put(sourceUrl: String, videoUrl: String, quality: Int, extractor: String) {
    persistentCache?.put(sourceUrl, videoUrl, quality, extractor)
}

// Update get() method
fun get(sourceUrl: String): CachedUrl? {
    val entry = persistentCache?.get(sourceUrl) ?: return null
    return CachedUrl(entry.videoUrl, entry.quality, entry.extractor)
}
```

**Success Criteria:**
- VideoUrlCache uses PersistentVideoCache
- Backward compatibility maintained
- Cache persists across app restarts

---

### 3.5 Initialize Cache in MaxSeriesProvider
- [x] Add cache initialization in MaxSeriesProvider init block
- [x] Get application context via reflection (same as PlayerEmbedAPI)
- [x] Call `VideoUrlCache.init(context)`
- [x] Add error handling
- [x] Test: Verify cache initializes on provider load

**Files to modify:**
- `MaxSeries/src/main/kotlin/com/franciscoalro/maxseries/MaxSeriesProvider.kt`

**Changes:**
```kotlin
// In init block (line ~70)
init {
    Log.wtf(TAG, "🚀🚀🚀 MAXSERIES PROVIDER v217 CARREGADO! 🚀🚀🚀")
    
    // Initialize persistent cache
    try {
        val context = Class.forName("android.app.ActivityThread")
            .getMethod("currentApplication")
            .invoke(null) as android.content.Context
        VideoUrlCache.init(context)
        Log.d(TAG, "✅ Cache persistente inicializado")
    } catch (e: Exception) {
        Log.e(TAG, "❌ Erro ao inicializar cache: ${e.message}")
    }
}
```

**Success Criteria:**
- Cache initializes on provider load
- No crashes on initialization
- Logs show successful init

---

## Phase 4: Testing & Validation (30-45 min)

### 4.1 Manual Testing - WebView Performance
- [x] Build and install v217
- [x] Test PlayerEmbedAPI extraction
- [x] Measure first load time (should be <2s)
- [x] Test second load (should reuse WebView)
- [x] Check logs for pool usage
- [x] Verify no memory leaks

**Success Criteria:**
- First load: <2s
- Subsequent loads: <1s
- WebView reuse confirmed in logs

---

### 4.2 Manual Testing - Timeout Behavior
- [x] Test PlayerEmbedAPI with slow network
- [x] Verify 30s timeout on first attempt
- [x] Verify 15s timeout on retry
- [x] Check fallback to next extractor
- [x] Verify error messages are clear

**Success Criteria:**
- Timeout: 30s (not 60s)
- Retry: 15s
- Fallback works correctly

---

### 4.3 Manual Testing - Cache Persistence
- [x] Extract a video URL
- [x] Check logs for cache PUT
- [x] Close and reopen app
- [x] Extract same video again
- [x] Verify cache HIT in logs
- [x] Check hit rate statistics

**Success Criteria:**
- Cache persists across restarts
- Hit rate >60% after multiple uses
- TTL: 30min expiration works

---

### 4.4 Performance Benchmarking
- [x] Measure baseline (v216) performance
- [x] Measure v217 performance
- [x] Compare WebView loading time
- [x] Compare timeout behavior
- [x] Compare cache hit rate
- [x] Document improvements

**Metrics to measure:**
| Metric | v216 | v217 | Improvement |
|--------|------|------|-------------|
| WebView Load | 3-5s | <2s | 40-60% |
| Timeout | 60s | 30s | 50% |
| Cache Duration | 5min | 30min | 500% |
| Cache Hit Rate | ~20% | ~60% | 200% |

**Success Criteria:**
- All metrics meet or exceed targets
- No regressions in functionality

---

### 4.5 Update Documentation
- [x] Update release notes for v217
- [x] Document performance improvements
- [x] Update RESUMO_V217.md
- [x] Add performance comparison table
- [x] Document new cache behavior

**Files to create/update:**
- `release-notes-v217.md`
- `RESUMO_V217.md`

**Success Criteria:**
- Documentation complete
- Performance gains documented
- User-facing changes explained

---

## 🎯 Definition of Done

All tasks must be completed and verified:

- [x] WebView loads in <2s (40-60% improvement)
- [x] Timeout is 30s (50% reduction from 60s)
- [x] Cache persists for 30min
- [x] Cache hit rate >60%
- [x] No memory leaks detected
- [x] All manual tests pass
- [x] Performance benchmarks meet targets
- [x] Documentation updated
- [x] Release notes created

---

## 📝 Notes

### Dependencies
- kotlinx.serialization for CacheEntry
- SharedPreferences (Android SDK)
- WebView (Android SDK)

### Risks & Mitigations
1. **WebView Pool Memory Leak**
   - Mitigation: Proper cleanup in destroy()
   - Test: Monitor memory usage

2. **Timeout Too Short**
   - Mitigation: Adaptive timeout (30s + 15s retry)
   - Test: Verify on slow networks

3. **Cache Storage Overhead**
   - Mitigation: LRU + 100 URL limit (~1MB)
   - Test: Monitor storage usage

---

**Version:** 217  
**Skill:** performance-profiling  
**Priority:** High  
**Status:** Ready for Implementation
