# PlayerEmbedAPI Flow Analysis

## Current Status

After analyzing the PlayerEmbedAPI HTML and JavaScript, I've discovered:

1. **Data Location**: Video data is embedded as base64 in `const datas = "..."`
2. **Decryption Function**: Uses `window.SoTrym()` from `core.bundle.js` or `lite.bundle.js`
3. **Encryption**: AES-CTR with key derived from `user_id:md5_id:slug`
4. **Problem**: Direct decryption attempts failed - the key derivation or algorithm might be more complex

## What We Know

### HTML Structure
```html
<script src="https://iamcdn.net/player-v2/core.bundle.js"></script>
<script>
window.addEventListener("load", ()=> {
  const datas = "eyJzbHVnIjoia0JKTHR4Q0QzIiwibWQ1X2lkIjoyODkzMDY0NywidXNlcl9pZCI6NDgyMTIwLCJtZWRpYSI6IrxI9Fx1MDAwNqtcdTAwMDSDjzb+J9XZMaZPzUFM+JRWpvDkPFTeXHUwMDE4XHUwMDFlr5NTXHUwMDEzY8hcYiRgKN6x4dgvXHUwMDE44ExcdTAwMTI1XHUwMDEwT2prq29UPezjXHUwMDFkVVx1MDAxOCyav1x1MDAxYURcdTAwMDCQqKv3XHUwMDExVolcdTAwMTPqV1x1MDAxNopEXHTf4S9cdTAwMThccoND/VS0cmuE41fgc05BI73aMMBcdTAwMDVcdTAwMTSElVonTvdcdTAwMDZcdTAwMTA2Ul1byu3xeHu3OTdcdTAwMWEyYF5M2FYkXzghXHTLKXzHUz6GytnZvc2SnsFcdTAwMWZUNv/Q7bZcYpnGo1/c/7Sh2lx1MDAxNtc3+ZyeK1x0x1x1MDAxNVxi9cxcdTAwMWVwToaoKziNuKg7T1xmVuxtfybLMjO5RG8hXHUwMDA19+VcdTAwMGWuQKdrYW+CLnnO8Fx1MDAxZY9cdTAwMDBX/XZB8//P0//1XGZbhbQswra8zuGLXqRlVZhKNIOezXpcdTAwMWV3uTyG/D5cdTAwMTdS4o1cdTAwMWUjvFwi+FZr5o/XzLv9IHtv3v9qdEw8i1x1MDAwMGWXaVx1MDAxN3VcdTAwMDTe7ItgIfHEI81cdTAwMTaEhIhF8Xh9enxru9xkqMMnoi1do2W685RoiavFk09OXHUwMDA2aF2rSPHiS+9jSOPNnmlcdTAwMDcw9o6jgVxijeFcdTAwMTWCuVx1MDAxOdeAUCme0+ZcdTAwMTGP0zqqiobRVpu9XHUwMDBmUpxcdTAwMDImyptAX/dGXHUwMDExm8YzwcIy5GRcdTAwMTRnv6X4NbOyXlwiXSl5qNtcdTAwMTbPbLn4oyRu3X2rcFBGc1x1MDAwNOG9aLEpVpdCymOi+Fx1MDAxZUo2S55i8nB0a1xmXHUwMDA1MFOnc6idu+FK1adHOtmYs0dfeIlal1wizYGSgWh8vFx1MDAwM1x1MDAxMre+hT8vXHUwMDAwrLBcYqkmtKfUXyNcdTAwMGaUKFxu59GIjinwvZvZ7cO4XHUwMDAyc1x1MDAxMnmE/zRcdTAwMDRPoLDuXHUwMDE061gjPlx1MDAxNIjnjlwi1/3mXHUwMDFkOkBcdTAwMWZ9oUXKXHUwMDAzaFJcIqXExosqWlxirFx01qRqpdylXHUwMDE56eCsTMPtSVBfJCa2uu1SeVxuwEKPS2aYjD5LM7jxVKNcdTAwMDfwXHUwMDE2XHUwMDE4L8l2XHUwMDA0QoZgSVx1MDAwNcNtNTBcdTAwMDUsxs5POLjU5lx1MDAwN82/Z1x1MDAwMVx0cTTYXHUwMDE3jah/XHUwMDFkwy5L25Z4UVBigqzJk1x1MDAxM7/P2TtKqZyVYdO3lVigfDJcdTAwMTMqbeXSrYAwcOGYU1x1MDAxOLNaXHUwMDE4d6FcdJyBptdK2IVcdTAwMTUqOl+SvOlUcXBcdTAwMTZcdTAwMWG816I23khcdTAwMDPt+tE+LY71WK9cdTAwMTDVw1BSmFx1MDAxOFCf5qdcdTAwMTDAXU9TX+uVXHUwMDBmTEmUupOHg204YS+SXHUwMDA20ednbzsxoP6ykcZZqFReXGYyze1nYJbrKILfXHUwMDFhXHUwMDE1qO2kvyO6PopcdTAwMTUhbVx1MDAxYTtccmXOfFx1MDAwMFx1MDAwNqvKUO733GSU0I3C4cxcYmhcdTAwMTVcdTAwMTSOTlx1MDAwZjRCsbltY37Xc2LWZmho7TDW72V6OchUW1p8+YlcdTAwMTJ7WEK5YmJKZ1IrLVx1MDAwMJS681x1MDAwNVx1MDAwMtl7x1x1MDAxZnb2JFx1MDAwNElcXICn/F5bRLKh3MKMX/KUXGZcdTAwMDOynpA2zzRfi2GBrCpcdTAwMTbGIXRi1+KZVq1+nD3d6lb1uiAnve1cdTAwMTlcdTAwMDaspTym+pye3+WiXHUwMDBmwf5cdTAwMTja57lcdTAwMTJcdTAwMWTG/WmP6CBcdTAwMWJFjlMgbMzhXHUwMDFiJ15JpVx1MDAwMTCtr1x1MDAwNWBImZq4KdrGdmH6g0iBXHUwMDBmVTibhiXTXHUwMDFjJbDm81x0uPjf/fZcdTAwMTgtRspIjG87pUrBIL9cdTAwMTGibrZlr9Js7fZBlttcdTAwMTFItKvAcKSozLiCh965bZWAszVcbqKy/j3QQOozXHUwMDE32M9G03ZLTMi8YzgtX51cdTAwMGLwrYVt6Gks/XzVg+TSXHUwMDE2VaFKO+jbO1x1MDAwNjrD205cbkOZ7ZNcYrbAtu5cdTAwMTOKWKW6NPG+aJBRXHUwMDBmjJpcdTAwMDbiXHUwMDBlyyb3+bB3re74yWhcbpJcdTAwMDPEo0j9wODn3aI0uTSFK0OblC14XHUwMDEyjXLGoFx1MDAwMv45XHUwMDFj7DWOtPauZnXee/XxWGfxeVx1MDAxM6WxrmqXgMFmQerON3fnV1xy9ZNRyPdyXHUwMDExLfXYVZdcdTAwMTF0XHJcdTAwMWZ3XHUwMDFjXHUwMDA3P9iI2C1HXHUwMDE3WLn861xydDNcdTAwMDfW3DpA1dLLsOFFj0FU0EE9tFx1MDAxN75jOzBC/mHuvc1lXCK0q6qMXHRhU28gg+blXkoqhoNFr1ekxlx1MDAxMnpcYlx1MDAwNdSdlyGN3IiKgi3xolx1MDAxNlx1MDAxZVx1MDAxMND26zmMXHUwMDE5JEdcdTAwMWFz93/842pcYjZwibW59FfjubtcdTAwMTToklk4zMjq0JWqWfFWb1wiMlx1MDAwMMPxhOJTXHUwMDFlr7V+yiu0J6DZlVxmw1x1MDAxOVkp+e/cM8+DXHUwMDE4ViW9j6ev59uNYlx1MDAxM2BcdTAwMDBcdTAwMTOoR1x1MDAxMCej+2h7x1x1MDAwMGdWXHUwMDAxV4SHbNFcdTAwMTJ/XHUwMDAws8SpMHDh647BXHUwMDFmjf3zOfNcdTAwMDBcXF9l/vDSh3yRQNOTlIE3dYI0Y1Gn7sR/f8Xyat3f/ybC6ZwkS5eH9uLn9selr9Y2/q5cdTAwMDPWp6L6zO+B+lMryoV+5d8+XHUwMDE1XHUwMDE1O/g1Vfc+xnh81MKtxd6zepKG7ZXvkXYttVx1MDAwMc0q5fyexUmO30FD5W9x6E/i07bsc781XHUwMDE4LDUxXHUwMDA1xVxiXHUwMDFl+ML4uqzYYPtOJsFThb+6pFupXHUwMDA1XHUwMDFkKuG6fYpcblx1MDAxYlx1MDAxY45GxztcclxmsyIsImNvbmZpZyI6eyJwb3N0ZXIiOmZhbHNlLCJwcmV2aWV3IjpmYWxzZSwiaXNEb3dubG9hZCI6dHJ1ZX19";
  if(window.SoTrym)
    return window.SoTrym(JSON.parse(atob(datas)));
  loadScript("https://iamcdn.net/player-v2/lite.bundle.js").then(reload => {
    if(!reload || !window.SoTrym)
      return document.write("Your browser is interfering...");
    return window.SoTrym(JSON.parse(atob(datas)));
  });
});
</script>
```

### Decoded JSON
```json
{
  "slug": "kBJLtxCD3",
  "md5_id": 28930647,
  "user_id": 482120,
  "media": "<BINARY_DATA_2508_BYTES>",
  "config": {
    "poster": false,
    "preview": false,
    "isDownload": true
  }
}
```

## Alternative Approaches

Since direct decryption is failing, we have several options:

### Option 1: Browser Automation (RECOMMENDED)
Use Selenium/Playwright to:
1. Load the PlayerEmbedAPI URL
2. Wait for JWPlayer to initialize
3. Extract video URL from JWPlayer config

**Pros**: Guaranteed to work, no reverse engineering needed
**Cons**: Requires browser automation (but CloudStream supports WebView)

### Option 2: Intercept Network Requests
Monitor network traffic after loading PlayerEmbedAPI to capture:
- JWPlayer setup calls
- Video URL requests (.m3u8 or .mp4)
- API calls that return video URLs

**Pros**: Can discover the actual video URL pattern
**Cons**: Requires browser or network monitoring

### Option 3: Analyze lite.bundle.js
The HTML tries to load `lite.bundle.js` if `core.bundle.js` doesn't define `SoTrym`.
Maybe `lite.bundle.js` has simpler/clearer decryption logic.

**Pros**: Might be easier to understand
**Cons**: Still requires reverse engineering

### Option 4: Find API Endpoint
PlayerEmbedAPI might have a backend API that returns video URLs directly.
Look for patterns like:
- `/api/video?id=...`
- `/api/player?v=...`
- `/sora/...` (we saw these in earlier analysis)

**Pros**: Clean HTTP-only solution
**Cons**: API might not exist or might be protected

## Recommendation

**Use Browser Automation (Option 1)** because:

1. **CloudStream already supports WebView** - MaxSeries can use it
2. **No complex reverse engineering** - Let the browser do the work
3. **Future-proof** - Works even if encryption changes
4. **Proven approach** - MegaEmbed analysis showed this is the reliable way

## Next Steps

1. Create a Playwright/Selenium script to:
   - Load PlayerEmbedAPI URL
   - Wait for video player
   - Extract video URL from JWPlayer
   
2. Test with multiple videos to confirm pattern

3. Implement in MaxSeries provider using WebView

4. Fall back to other players if PlayerEmbedAPI fails

## Files Created

- `PLAYEREMBEDAPI_ANALYSIS.md` - Initial analysis
- `PLAYEREMBEDAPI_SOLUTION.md` - Attempted decryption solution
- `playerembedapi_*.html` - 5 sample HTML files
- `core_bundle_new.js` - JavaScript bundle (211KB)
- `test-playerembedapi-decrypt-v2.py` - Decryption test (failed)
- `PLAYEREMBEDAPI_FLOW_ANALYSIS.md` - This file
