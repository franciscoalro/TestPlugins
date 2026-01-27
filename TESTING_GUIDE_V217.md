# MaxSeries v217 - Testing Guide

## 🎯 Overview

This guide will help you test the performance improvements in MaxSeries v217, including WebView Pool, Adaptive Timeout, and Persistent Cache.

**Build Status:** ✅ BUILD SUCCESSFUL  
**Package Location:** `MaxSeries\build\MaxSeries.cs3`  
**Version:** 217

---

## 📦 Installation

### Method 1: Manual Installation (Recommended for Testing)

1. **Locate the built package:**
   ```
   MaxSeries\build\MaxSeries.cs3
   ```

2. **Install on Cloudstream:**
   - Open Cloudstream app
   - Go to **Settings** → **Extensions**
   - Click **Install from file**
   - Select `MaxSeries.cs3`
   - Wait for installation to complete

3. **Verify installation:**
   - Check that MaxSeries v217 appears in Extensions list
   - Restart Cloudstream if needed

### Method 2: ADB Installation (Advanced)

```powershell
# Connect to device
adb connect <device-ip>:5555

# Install package
adb push MaxSeries\build\MaxSeries.cs3 /sdcard/
# Then install via Cloudstream file picker
```

---

## 🧪 Test Plan

### Test 1: WebView Pool Performance ⚡

**Objective:** Verify WebView reuse is working and improving performance

**Steps:**
1. Open Cloudstream and enable ADB logging (if available)
2. Select any series/movie
3. Choose **PlayerEmbedAPI** as the source
4. **First extraction** - Monitor time
5. Go back and select **same episode again**
6. **Second extraction** - Should be faster

**Expected Logs:**
```
⚡ Adquirindo WebView do pool...
🆕 Criando nova WebView (first time)
⚡ WebView acquired em ~100ms

# Second time:
⚡ Adquirindo WebView do pool...
♻️ Reusando WebView do pool
⚡ WebView acquired em <10ms
```

**Success Criteria:**
- ✅ First load: <2s total
- ✅ Second load: <1s total
- ✅ Logs show "♻️ Reusando WebView do pool"

---

### Test 2: Adaptive Timeout ⏱️

**Objective:** Verify timeout is reduced and retry works

**Steps:**
1. Select an episode with PlayerEmbedAPI
2. **DO NOT CLICK** the play button (let it timeout)
3. Monitor logs for timeout behavior

**Expected Logs:**
```
🔄 Tentativa 1/2 (timeout: 30s)
# ... wait 30 seconds ...
⏱️ Timeout após 30s (tentativa 1)
🔄 Tentando novamente com timeout reduzido...
🔄 Tentativa 2/2 (timeout: 15s)
# ... wait 15 seconds ...
⏱️ Timeout após 15s (tentativa 2)
❌ [MANUAL] Falha após 2 tentativas. Fallback para próximo extractor.
```

**Success Criteria:**
- ✅ First timeout: 30s (not 60s)
- ✅ Retry timeout: 15s
- ✅ Max total: 45s
- ✅ Fallback to next extractor works

---

### Test 3: Persistent Cache 💾

**Objective:** Verify cache persists across app restarts

**Steps:**

#### Part A: Cache PUT
1. Select an episode
2. Choose PlayerEmbedAPI
3. Click play and wait for video to load
4. Monitor logs for cache PUT

**Expected Logs:**
```
✅ Cache persistente inicializado (30min TTL, 100 URLs max)
💾 Cache PUT: PlayerEmbedAPI (2ms) - size: 1/100
```

#### Part B: Cache HIT (Same Session)
1. Go back to episode list
2. Select **same episode again**
3. Choose PlayerEmbedAPI
4. Should load instantly from cache

**Expected Logs:**
```
✅ Cache HIT: PlayerEmbedAPI (1ms, age: 2min, hit rate: 50%)
```

#### Part C: Cache Persistence (After Restart)
1. **Close Cloudstream completely** (force stop)
2. **Reopen Cloudstream**
3. Navigate to **same episode**
4. Choose PlayerEmbedAPI
5. Should still load from cache

**Expected Logs:**
```
✅ Cache persistente inicializado (30min TTL, 100 URLs max)
✅ Cache HIT: PlayerEmbedAPI (1ms, age: 5min, hit rate: 67%)
```

**Success Criteria:**
- ✅ Cache PUT logged on first extraction
- ✅ Cache HIT on second extraction (same session)
- ✅ Cache HIT after app restart (persistence)
- ✅ Hit rate increases with usage

---

### Test 4: Cache Expiration ⏰

**Objective:** Verify TTL (30min) works correctly

**Steps:**
1. Extract a video URL (cache PUT)
2. **Wait 31 minutes** ⏰
3. Try to play same video again
4. Should re-extract (cache expired)

**Expected Logs:**
```
⏰ Cache expirado (age: 31min, TTL: 30min)
❌ Cache MISS (1ms) - hit rate: 45%
# ... re-extraction occurs ...
💾 Cache PUT: PlayerEmbedAPI (2ms) - size: 45/100
```

**Success Criteria:**
- ✅ Cache expires after 30 minutes
- ✅ Re-extraction occurs automatically
- ✅ New URL cached for another 30 minutes

---

### Test 5: LRU Eviction 🗑️

**Objective:** Verify LRU removes least accessed entries

**Steps:**
1. Extract 100+ different videos (fill cache)
2. Play some videos multiple times (increase access count)
3. Extract more videos (trigger eviction)
4. Monitor logs for LRU eviction

**Expected Logs:**
```
🗑️ LRU: Removido PlayerEmbedAPI (acessos: 2)
💾 Cache PUT: MegaEmbed (2ms) - size: 100/100
```

**Success Criteria:**
- ✅ Cache never exceeds 100 URLs
- ✅ Least accessed entries removed first
- ✅ Popular content stays cached

---

### Test 6: Hit Rate Tracking 📊

**Objective:** Verify hit rate reaches >60%

**Steps:**
1. Use Cloudstream normally for 30 minutes
2. Watch multiple episodes
3. Rewatch some episodes
4. Monitor hit rate in logs

**Expected Logs:**
```
✅ Cache HIT: MegaEmbed (1ms, age: 15min, hit rate: 65%)
✅ Cache HIT: PlayerEmbedAPI (1ms, age: 8min, hit rate: 68%)
```

**Success Criteria:**
- ✅ Hit rate starts low (~20%)
- ✅ Hit rate increases with usage
- ✅ Hit rate reaches >60% after normal usage

---

## 📱 Monitoring Logs

### Using ADB (Recommended)

```powershell
# Connect to device
adb connect <device-ip>:5555

# Clear old logs
adb logcat -c

# Monitor MaxSeries logs
adb logcat | Select-String "MaxSeries|WebViewPool|PlayerEmbed|Cache|PersistentVideoCache"

# Or save to file
adb logcat > logs_v217_test.txt
```

### Using Cloudstream Built-in Logger

1. Open Cloudstream
2. Go to **Settings** → **Developer**
3. Enable **Debug Logging**
4. Logs will appear in app's log viewer

---

## 🎯 Performance Benchmarks

### Expected Results

| Metric | v216 | v217 | Target |
|--------|------|------|--------|
| **WebView First Load** | 3-5s | <2s | ✅ 40-60% faster |
| **WebView Reuse** | N/A | <10ms | ✅ Instant |
| **Timeout (1st)** | 60s | 30s | ✅ 50% reduction |
| **Timeout (retry)** | N/A | 15s | ✅ New feature |
| **Cache Duration** | 5min | 30min | ✅ 500% increase |
| **Cache Hit Rate** | ~20% | ~60% | ✅ 200% improvement |
| **Cache Persistence** | ❌ | ✅ | ✅ Survives restart |

---

## 🐛 Troubleshooting

### Issue: WebView not reusing

**Symptoms:**
- Always shows "🆕 Criando nova WebView"
- Never shows "♻️ Reusando WebView do pool"

**Solutions:**
1. Check if `WebViewPool.release()` is being called
2. Look for "🔓 Liberando WebView de volta ao pool" in logs
3. Verify no crashes during extraction

### Issue: Cache not persisting

**Symptoms:**
- Cache lost after app restart
- Always shows "❌ Cache MISS" after restart

**Solutions:**
1. Check for "✅ Cache persistente inicializado" on app start
2. Verify SharedPreferences permissions
3. Check for initialization errors in logs
4. Fallback to memory cache should still work

### Issue: Timeout too short

**Symptoms:**
- Timeout before user can click
- Frequent "⏱️ Timeout após 30s" messages

**Solutions:**
1. 30s should be sufficient for most cases
2. Retry gives additional 15s (total 45s)
3. Fallback to other extractors works automatically
4. If persistent issue, may need to adjust timeout constants

### Issue: Low hit rate

**Symptoms:**
- Hit rate stays below 60%
- Many "❌ Cache MISS" messages

**Solutions:**
1. Normal at first (cache is empty)
2. Hit rate increases with usage
3. Watch same content multiple times
4. Wait for cache to populate (30min TTL)

---

## 📊 Test Results Template

Use this template to record your test results:

```markdown
# MaxSeries v217 Test Results

**Date:** [Date]
**Device:** [Device Model]
**Android Version:** [Version]
**Cloudstream Version:** [Version]

## Test 1: WebView Pool
- [ ] First load: <2s
- [ ] Second load: <1s
- [ ] Logs show WebView reuse
- **Notes:** 

## Test 2: Adaptive Timeout
- [ ] First timeout: 30s
- [ ] Retry timeout: 15s
- [ ] Fallback works
- **Notes:** 

## Test 3: Persistent Cache
- [ ] Cache PUT works
- [ ] Cache HIT (same session)
- [ ] Cache HIT (after restart)
- **Notes:** 

## Test 4: Cache Expiration
- [ ] Cache expires after 30min
- [ ] Re-extraction works
- **Notes:** 

## Test 5: LRU Eviction
- [ ] Max 100 URLs enforced
- [ ] Least accessed removed
- **Notes:** 

## Test 6: Hit Rate
- [ ] Hit rate increases with usage
- [ ] Reaches >60%
- **Notes:** 

## Overall Performance
- WebView loading: [time]
- Cache hit rate: [percentage]
- User experience: [rating 1-5]

## Issues Found
[List any issues]

## Recommendations
[Any suggestions]
```

---

## 🎉 Success Criteria Summary

All tests should pass with these criteria:

- ✅ WebView loads in <2s (40-60% improvement)
- ✅ WebView reuse confirmed in logs
- ✅ Timeout is 30s (50% reduction from 60s)
- ✅ Retry timeout is 15s
- ✅ Cache persists for 30min
- ✅ Cache survives app restart
- ✅ Cache hit rate >60% after usage
- ✅ LRU eviction works correctly
- ✅ No memory leaks detected
- ✅ No crashes or errors

---

## 📞 Support

If you encounter any issues during testing:

1. **Check logs** for error messages
2. **Verify build** is v217
3. **Restart app** and try again
4. **Report issues** with logs attached

**GitHub Issues:** https://github.com/franciscoalro/TestPlugins/issues

---

## 📝 Next Steps After Testing

1. **Document results** using template above
2. **Report any issues** found
3. **Validate performance** improvements
4. **Deploy to production** if all tests pass

---

**Version:** 217  
**Build Date:** 27 Jan 2026  
**Status:** ✅ Ready for Testing

🎬 **Happy Testing!** ⚡
