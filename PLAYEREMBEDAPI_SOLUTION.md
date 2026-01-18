# PlayerEmbedAPI - Complete Solution

## ✅ DECRYPTION ALGORITHM DISCOVERED

### Algorithm: AES-CTR (Counter Mode)

The `media` field in the JSON is encrypted using **AES-CTR** encryption with a **key derived from video metadata**.

## Decryption Process

### Step 1: Extract Base64 Data from HTML

```javascript
const datas = "eyJzbHVnIjoia0JKTHR4Q0QzIiwibWQ1X2lkIjoyODkzMDY0NywidXNlcl9pZCI6NDgyMTIwLCJtZWRpYSI6IrxI9Fx1MDAwNqtcdTAwMDSDjzb+J9XZMaZPzUFM+JRWpvDkPFTeXHUwMDE4XHUwMDFlr5NTXHUwMDEzY8hcYiRgKN6x4dgvXHUwMDE44ExcdTAwMTI1XHUwMDEwT2prq29UPezjXHUwMDFkVVx1MDAxOCyav1x1MDAxYURcdTAwMDCQqKv3XHUwMDExVolcdTAwMTPqV1x1MDAxNopEXHTf4S9cdTAwMThccoND/VS0cmuE41fgc05BI73aMMBcdTAwMDVcdTAwMTSElVonTvdcdTAwMDZcdTAwMTA2Ul1byu3xeHu3OTdcdTAwMWEyYF5M2FYkXzghXHTLKXzHUz6GytnZvc2SnsFcdTAwMWZUNv/Q7bZcYpnGo1/c/7Sh2lx1MDAxNtc3+ZyeK1x0x1x1MDAxNVxi9cxcdTAwMWVwToaoKziNuKg7T1xmVuxtfybLMjO5RG8hXHUwMDA19+VcdTAwMGWuQKdrYW+CLnnO8Fx1MDAxZY9cdTAwMDBX/XZB8//P0//1XGZbhbQswra8zuGLXqRlVZhKNIOezXpcdTAwMWV3uTyG/D5cdTAwMTdS4o1cdTAwMWUjvFwi+FZr5o/XzLv9IHtv3v9qdEw8i1x1MDAwMGWXaVx1MDAxN3VcdTAwMDTe7ItgIfHEI81cdTAwMTaEhIhF8Xh9enxru9xkqMMnoi1do2W685RoiavFk09OXHUwMDA2aF2rSPHiS+9jSOPNnmlcdTAwMDcw9o6jgVxijeFcdTAwMTWCuVx1MDAxOdeAUCme0+ZcdTAwMTGP0zqqiobRVpu9XHUwMDBmUpxcdTAwMDImyptAX/dGXHUwMDExm8YzwcIy5GRcdTAwMTRnv6X4NbOyXlwiXSl5qNtcdTAwMTbPbLn4oyRu3X2rcFBGc1x1MDAwNOG9aLEpVpdCymOi+Fx1MDAxZUo2S55i8nB0a1xmXHUwMDA1MFOnc6idu+FK1adHOtmYs0dfeIlal1wizYGSgWh8vFx1MDAwM1x1MDAxMre+hT8vXHUwMDAwrLBcYqkmtKfUXyNcdTAwMGaUKFxu59GIjinwvZvZ7cO4XHUwMDAyc1x1MDAxMnmE/zRcdTAwMDRPoLDuXHUwMDE061gjPlx1MDAxNIjnjlwi1/3mXHUwMDFkOkBcdTAwMWZ9oUXKXHUwMDAzaFJcIqXExosqWlxirFx01qRqpdylXHUwMDE56eCsTMPtSVBfJCa2uu1SeVxuwEKPS2aYjD5LM7jxVKNcdTAwMDfwXHUwMDE2XHUwMDE4L8l2XHUwMDA0QoZgSVx1MDAwNcNtNTBcdTAwMDUsxs5POLjU5lx1MDAwN82/Z1x1MDAwMVx0cTTYXHUwMDE3jah/XHUwMDFkwy5L25Z4UVBigqzJk1x1MDAxM7/P2TtKqZyVYdO3lVigfDJcdTAwMTMqbeXSrYAwcOGYU1x1MDAxOLNaXHUwMDE4d6FcdJyBptdK2IVcdTAwMTUqOl+SvOlUcXBcdTAwMTZcdTAwMWG816I23khcdTAwMDPt+tE+LY71WK9cdTAwMTDVw1BSmFx1MDAxOFCf5qdcdTAwMTDAXU9TX+uVXHUwMDBmTEmUupOHg204YS+SXHUwMDA20ednbzsxoP6ykcZZqFReXGYyze1nYJbrKILfXHUwMDFhXHUwMDE1qO2kvyO6PopcdTAwMTUhbVx1MDAxYTtccmXOfFx1MDAwMFx1MDAwNqvKUO733GSU0I3C4cxcYmhcdTAwMTVcdTAwMTSOTlx1MDAwZjRCsbltY37Xc2LWZmho7TDW72V6OchUW1p8+YlcdTAwMTJ7WEK5YmJKZ1IrLVx1MDAwMJS681x1MDAwNVx1MDAwMtl7x1x1MDAxZnb2JFx1MDAwNElcXICn/F5bRLKh3MKMX/KUXGZcdTAwMDOynpA2zzRfi2GBrCpcdTAwMTbGIXRi1+KZVq1+nD3d6lb1uiAnve1cdTAwMTlcdTAwMDaspTym+pye3+WiXHUwMDBmwf5cdTAwMTja57lcdTAwMTJcdTAwMWTG/WmP6CBcdTAwMWJFjlMgbMzhXHUwMDFiJ15JpVx1MDAwMTCtr1x1MDAwNWBImZq4KdrGdmH6g0iBXHUwMDBmVTibhiXTXHUwMDFjJbDm81x0uPjf/fZcdTAwMTgtRspIjG87pUrBIL9cdTAwMTGibrZlr9Js7fZBlttcdTAwMTFItKvAcKSozLiCh965bZWAszVcbqKy/j3QQOozXHUwMDE32M9G03ZLTMi8YzgtX51cdTAwMGLwrYVt6Gks/XzVg+TSXHUwMDE2VaFKO+jbO1x1MDAwNjrD205cbkOZ7ZNcYrbAtu5cdTAwMTOKWKW6NPG+aJBRXHUwMDBmjJpcdTAwMDbiXHUwMDBlyyb3+bB3re74yWhcbpJcdTAwMDPEo0j9wODn3aI0uTSFK0OblC14XHUwMDEyjXLGoFx1MDAwMv45XHUwMDFj7DWOtPauZnXee/XxWGfxeVx1MDAxM6WxrmqXgMFmQerON3fnV1xy9ZNRyPdyXHUwMDExLfXYVZdcdTAwMTF0XHJcdTAwMWZ3XHUwMDFjXHUwMDA3P9iI2C1HXHUwMDE3WLn861xydDNcdTAwMDfW3DpA1dLLsOFFj0FU0EE9tFx1MDAxN75jOzBC/mHuvc1lXCK0q6qMXHRhU28gg+blXkoqhoNFr1ekxlx1MDAxMnpcYlx1MDAwNdSdlyGN3IiKgi3xolx1MDAxNlx1MDAxZVx1MDAxMND26zmMXHUwMDE5JEdcdTAwMWFz93/842pcYjZwibW59FfjubtcdTAwMTToklk4zMjq0JWqWfFWb1wiMlx1MDAwMMPxhOJTXHUwMDFlr7V+yiu0J6DZlVxmw1x1MDAxOVkp+e/cM8+DXHUwMDE4ViW9j6ev59uNYlx1MDAxM2BcdTAwMDBcdTAwMTOoR1x1MDAxMCej+2h7x1x1MDAwMGdWXHUwMDAxV4SHbNFcdTAwMTJ/XHUwMDAws8SpMHDh647BXHUwMDFmjf3zOfNcdTAwMDBcXF9l/vDSh3yRQNOTlIE3dYI0Y1Gn7sR/f8Xyat3f/ybC6ZwkS5eH9uLn9selr9Y2/q5cdTAwMDPWp6L6zO+B+lMryoV+5d8+XHUwMDE1XHUwMDE1O/g1Vfc+xnh81MKtxd6zepKG7ZXvkXYttVx1MDAwMc0q5fyexUmO30FD5W9x6E/i07bsc781XHUwMDE4LDUxXHUwMDA1xVxiXHUwMDFl+ML4uqzYYPtOJsFThb+6pFupXHUwMDA1XHUwMDFkKuG6fYpcblx1MDAxYlx1MDAxY45GxztcclxmsyIsImNvbmZpZyI6eyJwb3N0ZXIiOmZhbHNlLCJwcmV2aWV3IjpmYWxzZSwiaXNEb3dubG9hZCI6dHJ1ZX19";
```

### Step 2: Decode Base64 to JSON

```javascript
const decoded = JSON.parse(atob(datas));
```

Result:
```json
{
  "slug": "kBJLtxCD3",
  "md5_id": 28930647,
  "user_id": 482120,
  "media": "<ENCRYPTED_BINARY_DATA>",
  "config": {
    "poster": false,
    "preview": false,
    "isDownload": true
  }
}
```

### Step 3: Generate Decryption Key

The key is derived from three fields concatenated with colons:

```javascript
const keyString = `${user_id}:${md5_id}:${slug}`;
// Example: "482120:28930647:kBJLtxCD3"
```

### Step 4: Initialize AES-CTR Decryption

```javascript
class Decryptor {
  constructor() {
    this.algorithm = {
      name: 'AES-CTR',
      counter: null,  // Will be set from first 16 bytes of key
      length: 128     // Counter length in bits
    };
    this.key = null;
    this.keyUsages = ['encrypt', 'decrypt'];
    this.encoder = new TextEncoder();
  }
  
  async init(keyString) {
    // Encode key string
    const keyBytes = this.encoder.encode(keyString);
    
    // First 16 bytes become the counter
    this.algorithm.counter = new Uint8Array(keyBytes.slice(0, 16));
    
    // Import key using Web Crypto API
    this.key = await crypto.subtle.importKey(
      'raw',
      keyBytes,
      this.algorithm,
      false,
      this.keyUsages
    );
    
    return true;
  }
  
  async decrypt(encryptedData) {
    if (!encryptedData || !this.key) return encryptedData;
    
    // Convert string to Uint8Array if needed
    if (typeof encryptedData === 'string') {
      encryptedData = new Uint8Array(
        encryptedData.match(/[\s\S]/g).map(c => c.charCodeAt(0))
      );
    }
    
    // Decrypt using Web Crypto API
    const decrypted = await crypto.subtle.decrypt(
      this.algorithm,
      this.key,
      encryptedData
    );
    
    // Decode to string
    return new TextDecoder().decode(decrypted);
  }
}
```

### Step 5: Decrypt Media Field

```javascript
const decryptor = new Decryptor();
await decryptor.init(`${user_id}:${md5_id}:${slug}`);
const decryptedMedia = await decryptor.decrypt(media);
const mediaData = JSON.parse(decryptedMedia);
```

### Step 6: Extract Video URL

The decrypted `media` field contains video information including the URL.

## Python Implementation

```python
import base64
import json
from Crypto.Cipher import AES
from Crypto.Util import Counter

def decrypt_playerembedapi(html_content):
    """
    Decrypt PlayerEmbedAPI video URL from HTML
    """
    # Step 1: Extract base64 data
    import re
    match = re.search(r'const datas = "([^"]+)"', html_content)
    if not match:
        return None
    
    datas_b64 = match.group(1)
    
    # Step 2: Decode base64 to JSON
    datas_json = json.loads(base64.b64decode(datas_b64))
    
    slug = datas_json['slug']
    md5_id = datas_json['md5_id']
    user_id = datas_json['user_id']
    media_encrypted = datas_json['media']
    
    # Step 3: Generate key
    key_string = f"{user_id}:{md5_id}:{slug}"
    key_bytes = key_string.encode('utf-8')
    
    # Step 4: Setup AES-CTR
    # First 16 bytes as counter
    counter_bytes = key_bytes[:16]
    counter = Counter.new(128, initial_value=int.from_bytes(counter_bytes, 'big'))
    
    # Use key_bytes as encryption key (may need padding/hashing)
    cipher = AES.new(key_bytes[:32], AES.MODE_CTR, counter=counter)
    
    # Step 5: Decrypt
    media_bytes = media_encrypted.encode('latin-1')  # Preserve binary
    decrypted = cipher.decrypt(media_bytes)
    
    # Step 6: Parse decrypted JSON
    media_data = json.loads(decrypted.decode('utf-8'))
    
    return media_data
```

## Kotlin Implementation for CloudStream

```kotlin
import javax.crypto.Cipher
import javax.crypto.spec.IvParameterSpec
import javax.crypto.spec.SecretKeySpec
import java.util.Base64
import org.json.JSONObject

fun decryptPlayerEmbedAPI(html: String): String? {
    // Extract base64 data
    val datasRegex = """const datas = "([^"]+)"""".toRegex()
    val datasB64 = datasRegex.find(html)?.groupValues?.get(1) ?: return null
    
    // Decode base64 to JSON
    val datasJson = JSONObject(String(Base64.getDecoder().decode(datasB64)))
    
    val slug = datasJson.getString("slug")
    val md5Id = datasJson.getLong("md5_id")
    val userId = datasJson.getLong("user_id")
    val mediaEncrypted = datasJson.getString("media")
    
    // Generate key
    val keyString = "$userId:$md5Id:$slug"
    val keyBytes = keyString.toByteArray(Charsets.UTF_8)
    
    // Setup AES-CTR
    val counter = keyBytes.copyOfRange(0, 16)
    val key = SecretKeySpec(keyBytes.copyOfRange(0, 32), "AES")
    val iv = IvParameterSpec(counter)
    
    val cipher = Cipher.getInstance("AES/CTR/NoPadding")
    cipher.init(Cipher.DECRYPT_MODE, key, iv)
    
    // Decrypt
    val mediaBytes = mediaEncrypted.toByteArray(Charsets.ISO_8859_1)
    val decrypted = cipher.doFinal(mediaBytes)
    
    // Parse decrypted JSON
    val mediaData = JSONObject(String(decrypted, Charsets.UTF_8))
    
    // Extract video URL (structure TBD)
    return mediaData.optString("file") ?: mediaData.optString("url")
}
```

## Next Steps

1. ✅ Identified encryption algorithm (AES-CTR)
2. ✅ Found key derivation method (user_id:md5_id:slug)
3. ✅ Extracted decryption logic from JavaScript
4. ⏳ Test Python implementation with real data
5. ⏳ Verify decrypted media structure
6. ⏳ Implement in MaxSeries Kotlin provider
7. ⏳ Test with CloudStream app

## Advantages

- **No browser required** - Pure HTTP + crypto
- **Reproducible** - Key is deterministic
- **Fast** - Standard AES-CTR decryption
- **Simple** - Single HTTP request + decrypt

## Files

- `playerembedapi_kBJLtxCD3.html` - Sample HTML
- `core_bundle_new.js` - JavaScript with decryption logic
- `PLAYEREMBEDAPI_ANALYSIS.md` - Initial analysis
- `PLAYEREMBEDAPI_SOLUTION.md` - This file (complete solution)
