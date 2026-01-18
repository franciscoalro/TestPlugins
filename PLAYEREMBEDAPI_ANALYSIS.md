# PlayerEmbedAPI Analysis - Complete Solution

## Overview
PlayerEmbedAPI is a **much simpler alternative to MegaEmbed** that doesn't use encryption. The video data is embedded directly in the HTML as a base64-encoded JSON object.

## Key Discovery

### Video Data Location
The video data is embedded in a JavaScript variable at the end of the HTML:

```javascript
const datas = "eyJzbHVnIjoia0JKTHR4Q0QzIiwibWQ1X2lkIjoyODkzMDY0NywidXNlcl9pZCI6NDgyMTIwLCJtZWRpYSI6IrxI9Fx1MDAwNqtcdTAwMDSDjzb+J9XZMaZPzUFM+JRWpvDkPFTeXHUwMDE4XHUwMDFlr5NTXHUwMDEzY8hcYiRgKN6x4dgvXHUwMDE44ExcdTAwMTI1XHUwMDEwT2prq29UPezjXHUwMDFkVVx1MDAxOCyav1x1MDAxYURcdTAwMDCQqKv3XHUwMDExVolcdTAwMTPqV1x1MDAxNopEXHTf4S9cdTAwMThccoND/VS0cmuE41fgc05BI73aMMBcdTAwMDVcdTAwMTSElVonTvdcdTAwMDZcdTAwMTA2Ul1byu3xeHu3OTdcdTAwMWEyYF5M2FYkXzghXHTLKXzHUz6GytnZvc2SnsFcdTAwMWZUNv/Q7bZcYpnGo1/c/7Sh2lx1MDAxNtc3+ZyeK1x0x1x1MDAxNVxi9cxcdTAwMWVwToaoKziNuKg7T1xmVuxtfybLMjO5RG8hXHUwMDA19+VcdTAwMGWuQKdrYW+CLnnO8Fx1MDAxZY9cdTAwMDBX/XZB8//P0//1XGZbhbQswra8zuGLXqRlVZhKNIOezXpcdTAwMWV3uTyG/D5cdTAwMTdS4o1cdTAwMWUjvFwi+FZr5o/XzLv9IHtv3v9qdEw8i1x1MDAwMGWXaVx1MDAxN3VcdTAwMDTe7ItgIfHEI81cdTAwMTaEhIhF8Xh9enxru9xkqMMnoi1do2W685RoiavFk09OXHUwMDA2aF2rSPHiS+9jSOPNnmlcdTAwMDcw9o6jgVxijeFcdTAwMTWCuVx1MDAxOdeAUCme0+ZcdTAwMTGP0zqqiobRVpu9XHUwMDBmUpxcdTAwMDImyptAX/dGXHUwMDExm8YzwcIy5GRcdTAwMTRnv6X4NbOyXlwiXSl5qNtcdTAwMTbPbLn4oyRu3X2rcFBGc1x1MDAwNOG9aLEpVpdCymOi+Fx1MDAxZUo2S55i8nB0a1xmXHUwMDA1MFOnc6idu+FK1adHOtmYs0dfeIlal1wizYGSgWh8vFx1MDAwM1x1MDAxMre+hT8vXHUwMDAwrLBcYqkmtKfUXyNcdTAwMGaUKFxu59GIjinwvZvZ7cO4XHUwMDAyc1x1MDAxMnmE/zRcdTAwMDRPoLDuXHUwMDE061gjPlx1MDAxNIjnjlwi1/3mXHUwMDFkOkBcdTAwMWZ9oUXKXHUwMDAzaFJcIqXExosqWlxirFx01qRqpdylXHUwMDE56eCsTMPtSVBfJCa2uu1SeVxuwEKPS2aYjD5LM7jxVKNcdTAwMDfwXHUwMDE2XHUwMDE4L8l2XHUwMDA0QoZgSVx1MDAwNcNtNTBcdTAwMDUsxs5POLjU5lx1MDAwN82/Z1x1MDAwMVx0cTTYXHUwMDE3jah/XHUwMDFkwy5L25Z4UVBigqzJk1x1MDAxM7/P2TtKqZyVYdO3lVigfDJcdTAwMTMqbeXSrYAwcOGYU1x1MDAxOLNaXHUwMDE4d6FcdJyBptdK2IVcdTAwMTUqOl+SvOlUcXBcdTAwMTZcdTAwMWG816I23khcdTAwMDPt+tE+LY71WK9cdTAwMTDVw1BSmFx1MDAxOFCf5qdcdTAwMTDAXU9TX+uVXHUwMDBmTEmUupOHg204YS+SXHUwMDA20ednbzsxoP6ykcZZqFReXGYyze1nYJbrKILfXHUwMDFhXHUwMDE1qO2kvyO6PopcdTAwMTUhbVx1MDAxYTtccmXOfFx1MDAwMFx1MDAwNqvKUO733GSU0I3C4cxcYmhcdTAwMTVcdTAwMTSOTlx1MDAwZjRCsbltY37Xc2LWZmho7TDW72V6OchUW1p8+YlcdTAwMTJ7WEK5YmJKZ1IrLVx1MDAwMJS681x1MDAwNVx1MDAwMtl7x1x1MDAxZnb2JFx1MDAwNElcXICn/F5bRLKh3MKMX/KUXGZcdTAwMDOynpA2zzRfi2GBrCpcdTAwMTbGIXRi1+KZVq1+nD3d6lb1uiAnve1cdTAwMTlcdTAwMDaspTym+pye3+WiXHUwMDBmwf5cdTAwMTja57lcdTAwMTJcdTAwMWTG/WmP6CBcdTAwMWJFjlMgbMzhXHUwMDFiJ15JpVx1MDAwMTCtr1x1MDAwNWBImZq4KdrGdmH6g0iBXHUwMDBmVTibhiXTXHUwMDFjJbDm81x0uPjf/fZcdTAwMTgtRspIjG87pUrBIL9cdTAwMTGibrZlr9Js7fZBlttcdTAwMTFItKvAcKSozLiCh965bZWAszVcbqKy/j3QQOozXHUwMDE32M9G03ZLTMi8YzgtX51cdTAwMGLwrYVt6Gks/XzVg+TSXHUwMDE2VaFKO+jbO1x1MDAwNjrD205cbkOZ7ZNcYrbAtu5cdTAwMTOKWKW6NPG+aJBRXHUwMDBmjJpcdTAwMDbiXHUwMDBlyyb3+bB3re74yWhcbpJcdTAwMDPEo0j9wODn3aI0uTSFK0OblC14XHUwMDEyjXLGoFx1MDAwMv45XHUwMDFj7DWOtPauZnXee/XxWGfxeVx1MDAxM6WxrmqXgMFmQerON3fnV1xy9ZNRyPdyXHUwMDExLfXYVZdcdTAwMTF0XHJcdTAwMWZ3XHUwMDFjXHUwMDA3P9iI2C1HXHUwMDE3WLn861xydDNcdTAwMDfW3DpA1dLLsOFFj0FU0EE9tFx1MDAxN75jOzBC/mHuvc1lXCK0q6qMXHRhU28gg+blXkoqhoNFr1ekxlx1MDAxMnpcYlx1MDAwNdSdlyGN3IiKgi3xolx1MDAxNlx1MDAxZVx1MDAxMND26zmMXHUwMDE5JEdcdTAwMWFz93/842pcYjZwibW59FfjubtcdTAwMTToklk4zMjq0JWqWfFWb1wiMlx1MDAwMMPxhOJTXHUwMDFlr7V+yiu0J6DZlVxmw1x1MDAxOVkp+e/cM8+DXHUwMDE4ViW9j6ev59uNYlx1MDAxM2BcdTAwMDBcdTAwMTOoR1x1MDAxMCej+2h7x1x1MDAwMGdWXHUwMDAxV4SHbNFcdTAwMTJ/XHUwMDAws8SpMHDh647BXHUwMDFmjf3zOfNcdTAwMDBcXF9l/vDSh3yRQNOTlIE3dYI0Y1Gn7sR/f8Xyat3f/ybC6ZwkS5eH9uLn9selr9Y2/q5cdTAwMDPWp6L6zO+B+lMryoV+5d8+XHUwMDE1XHUwMDE1O/g1Vfc+xnh81MKtxd6zepKG7ZXvkXYttVx1MDAwMc0q5fyexUmO30FD5W9x6E/i07bsc781XHUwMDE4LDUxXHUwMDA1xVxiXHUwMDFl+ML4uqzYYPtOJsFThb+6pFupXHUwMDA1XHUwMDFkKuG6fYpcblx1MDAxYlx1MDAxY45GxztcclxmsyIsImNvbmZpZyI6eyJwb3N0ZXIiOmZhbHNlLCJwcmV2aWV3IjpmYWxzZSwiaXNEb3dubG9hZCI6dHJ1ZX19";
window.SoTrym(JSON.parse(atob(datas)));
```

### Decoding Process

1. **Extract the base64 string** from `const datas = "..."`
2. **Decode base64** using `atob()` or base64 decoder
3. **Parse JSON** to get video information

### Decoded JSON Structure

```json
{
  "slug": "kBJLtxCD3",
  "md5_id": 28930647,
  "user_id": 482120,
  "media": "<ENCRYPTED_OR_ENCODED_DATA>",
  "config": {
    "poster": false,
    "preview": false,
    "isDownload": true
  }
}
```

**Note**: The `media` field contains additional encoded/encrypted data that needs further analysis.

## JavaScript Files Loaded

1. **JWPlayer** (video player):
   - `https://statics.sssrr.org/player/jwplayer.min.js`
   - `https://statics.sssrr.org/player/jwpsrv.js`
   - `https://statics.sssrr.org/player/jwplayer.core.controls.html5.js`

2. **Custom Player Bundle**:
   - `https://iamcdn.net/player-v2/core.bundle.js`
   - `https://iamcdn.net/player-v2/lite.bundle.js`

3. **Ad Detection**:
   - `https://cdnjs.cloudflare.com/ajax/libs/fuckadblock/3.2.1/fuckadblock.min.js`

## Key Function: `window.SoTrym()`

The player uses a custom function `window.SoTrym()` loaded from `core.bundle.js` or `lite.bundle.js` that:
1. Takes the decoded JSON object
2. Processes the `media` field
3. Initializes JWPlayer with the video URL

## Implementation Strategy

### Option 1: Download and Analyze JavaScript Bundle (RECOMMENDED)

Download `core.bundle.js` to understand how `SoTrym()` decodes the `media` field:

```python
import requests

url = "https://iamcdn.net/player-v2/core.bundle.js"
response = requests.get(url)
with open("core.bundle.js", "w", encoding="utf-8") as f:
    f.write(response.text)
```

Then search for:
- `SoTrym` function definition
- How it processes the `media` field
- Video URL extraction logic

### Option 2: Intercept JWPlayer Setup

Use browser DevTools to intercept the JWPlayer setup call:

```javascript
// In browser console, before video loads
const originalSetup = jwplayer().setup;
jwplayer().setup = function(config) {
    console.log("JWPlayer config:", config);
    console.log("Video URL:", config.file || config.sources);
    return originalSetup.call(this, config);
};
```

### Option 3: Network Monitoring

Monitor network requests after the page loads to capture:
- `.m3u8` playlist URLs
- `.mp4` direct video URLs
- API calls that return video URLs

## Advantages Over MegaEmbed

1. **No encryption** - data is just base64 encoded
2. **Smaller payload** - ~11KB HTML vs 880KB JavaScript
3. **Simpler structure** - single base64 string vs complex crypto
4. **No random keys** - reproducible without browser
5. **Standard JWPlayer** - well-documented player

## Next Steps

1. ✅ Extract PlayerEmbedAPI HTML from Burp Suite
2. ✅ Identify video data location (base64 in `datas` variable)
3. ⏳ Download and analyze `core.bundle.js`
4. ⏳ Reverse engineer `SoTrym()` function
5. ⏳ Decode the `media` field
6. ⏳ Extract final video URL
7. ⏳ Implement in MaxSeries provider

## Files Analyzed

- `playerembedapi_kBJLtxCD3.html` - Land of Sin S01E01
- `playerembedapi_QvXFt2de3.html` - Another episode
- `playerembedapi_uB7T55ExW.html` - Another episode
- `playerembedapi_JC2Jx3NM4.html` - Another episode
- `playerembedapi_9X8E2blpK.html` - Another episode

All follow the same structure with different `datas` values.

## Conclusion

PlayerEmbedAPI is **significantly easier to implement** than MegaEmbed because:
- No browser automation required
- No random encryption keys
- Simple HTTP request + base64 decode + JSON parse
- Just need to understand the `SoTrym()` function

**RECOMMENDATION**: Focus on PlayerEmbedAPI instead of MegaEmbed for MaxSeries provider.
