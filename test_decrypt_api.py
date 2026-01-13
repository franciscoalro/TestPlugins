import requests
import json
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
import hashlib
import binascii

print("="*60)
print("TESTE DECRIPTACAO API MEGAEMBED")
print("="*60)

# Resposta encriptada da API
encrypted_hex = "c931f168750146d80637704f6b5ea751035e2f7b78c4591cd75217cb40e825c93f3e253a09ea14c2820bdf4d89377d70ed4857f8b4a570ae03ac2a10877f9571fd951ed3d6e7f64185475991005f42168bc52f4b52e89282c9fc29ad90bc687ffe226a84e0d9b3655a6269b955d0c889d961a1b7f766a1ed24535f0ad270687be0816fc890a8e0fff32c1a3ee3ae1231d8763d334e882fa8adac7a771a0463c34f996b433a97773ea38870d80dc5925e06de0c9d70d464859c8c12a7ea6bffa3ca84c3c6e8b65ef3e8a27f60c3ddef8a894d21b572869ccef9c27878c1375431bcc6e4d66c46f7f09904e13b2f39d7cf9d2539f48d449dd7eb61df241e408494f9144ee59fac668f50777f8f9fa22a627aa8af66048e4b3b76d8ce884e263155b7a9dde5ef00e520d311a9bfd8fa53a2b1e7fa69b7c39e05ba07888135bc0a86453a2e3f2b3ab606ed5d8feb00188ae414cc79b9c7d023a7a4d441edf87d06af7902f1cc2dcdbf1a4ee5fb8410a2a4fcd8d8d5fcb8f2eb08a0fb2323527b14d4e7d9be87daf354c4332c3262d838f9002ab2204a2d251c2e200faf54b1403270589e3522b470e07a65e6c0c42d48ff1973b5f8d79102a1a286c9e1bbaf448a17948f2f89d7bd2f46ee8d87850bc5bb2a6cb45580a859e825adfc0e8581a91a358d15f26fbe24166b5fd50dcb1102e101cc912dbe10a4cce7a2417ec4c01078e4b33b2dd01c84104505b79a3cf3a371ae85d31de10b8293e6771bc62cf3ef5546d404d9dfce286eaed376e2f3bb986648394f406f34eec7cc1a563bfa14afc9fba4b4317097b29e9847c1c6e251e60c4734f29176431c6c371430be7cf7ccfce0662c1f97a3a94d80ac21ce572527ca3ee5da733305a10cdd4ff33a8bcbb0e0082ce17ca5ff6d92bc26414a4e0026561a8b33a176dc00d1045f482be41aefb0e8d282002036906a9fcc6eb6557e8e1a2416b26ade97b08ff4d4e3458fba2002cac94da6706090ec44cad2452310ae932dc40e3718655eb05309f54dfdde3b25c1211bd7f5a1c52295167be9e07c0baf6d9b8a7a4917d1dc4057324c1c4a633222c75b1727445bc7e3b39334be6420a977450c52e1fa91556066ccdca97a561a18538bba5791116a7fe8f274daa0f9dc0372cc98be17a9c73dc0398c804a67ac9f445b19ed4d5e47c87b9a8821c744c42db6adf1cfe47958961e189c3fa1b1600e8b740322fa14e4a8c9890b626a7f804393fce88083da4825aa6e0217171b5f4a52d8bc611b298c58940a19d44746fae94345eb1713cb4b62e8d0a3b1b509df65b4f94cd751ac4cb825fb410d68a74a9d3557281fefadb0c9819f5de24397391e7be590a4ebd0774f76660d6ee8d1af6e54369906c97310d3fff0e8c9ecc9cb97b9d72630614028b656aae9d221f9bb9168f6cbec6df53c2a22f9ba79614863cb3adf018358b21ab6b59787fb984a4cc2ca859ac53f316872cf87f1ec4e6b0e55a59f42cf9d710dbaa26b351dd0352172bd0291f09db15fc9fa80339dd03d98c9d63271bb7da49ff48da9ce8d12b0260a20e3e67093aa290377cfbfc6e6ff20fa60de70ee68288a3286bc134711d92aea89b59513ec64257f59ac5c8dd20cbf1690f338bf4684916344f6d6dcd4d72dd877b25ac5daed18c04196cb8f9eff6eda1b839b66d5afae9b1dc490ac070cf58f51110a3e19bfd384eab4024917d5c1efaa8f1d6b063d2710b2d1061533226f3cd2938f3f81ecd224a15754200a72b09ee57b8fe41fc579529547f0f2e317a2d14611dd363cdbe006a451dda056c6c6a958b5553eeeac7ea86cd4fbf4699cd7af4251c1e301ef69131d24cf56e38de144d139275faed5f74bb5dc8d33b3da3f99292382de4bfbe6d7ff777bc42fa7ac2a9b3cbc93bb1106082949396ff0f81ec6d2bd561b556c13dfb38302871da9023dc1169cdab2922bd6eee5a59caa31e76b9dfd58d46ceb53123b440f32f0df912c139ddca6b3029d2190b9559ab9ca66ddd3ff2734cf5eb292259374de04244ca5947422bfcb797ab5cd0c35d7b8811a9ac42aff9818f3b794e209f01acc3f2ea63de654f55747beabad07c53917954fc2d00de9093dc92df2517ebf02a0cb9c3034e113eb7419f9d059ccf59bb145494f0c8f7cb46101119299214c0c3af3eba528bff2fcf7a7b22d73b6928f9ad98eacb38d8feb0275c8e95c097c0fe38f68ce011f245cf7064e26bbc47be6566f238afe5a923256a5d9bda6ab521c8d8de2c1009e0deea15e5dcdbbdb6ce6de1a49f7c934483079d31b0b576d64d74d307ebad59d237a035f10a1c2767caf9c81e82f02a80b7e3a08ba7b3dabf90c17d14e7a7db4f25a30a5434d989f27b89f82c75e6ba834d5ea6112797cff20adf0d7b0ac2e3df530fb43c1bb50300a3cce8b749185cac63ceacaaea0eddf0d4c0bd2f458e543ddf9e612fa0f52f7685c1b6c441cc5c71f10ba8608c510fb5dd5bfd8a0704ee3284d84950b9ef74dc4c6da6f8c4f5c44ee1eac9c4a9224e2424388a7cc8ad3ee1b2a0cfc301463822e86614de371f02216b30668ee7341f6981f5a60171a51e1f4df25b2c5c8c58d7cce32f7e8fca1a6906542adb0828031248eb6817815eef861ce4a0ce774f47578da5c97404c34fbc79ec0c2cb135859d260e2bf9b1fa83c6b5cff86a70818fd16a50f3cb21f9a2e514825ff6c2401ddfc87cf306c63518f01aa234a433674475f5345e7075b8438763470a038912ecaf664cf3cebdabb467734bba696d1c57c360efbdcf8cb38c459d1c314f306fee95da32d83734bba394a1004694a0da8d960e701372d237c92b6fd5f077045e6dc605597bd0bb95dcf02b451b51d385fe741f3d0b0f2239655c57bdc61215a5e7c1be9b014e4e23c8667b635e807c1f99795a33c0783b547cdbc80d7dcef7329e65f048570e90914a0c83655be24218ef323bf4c4260a57c97a39de4ece0bea64be8af3742c11f39f5e1efd527e740d16fd5b6b59252264f826daba73ba65e78ed40ea55131a85bc2583ba3173ce660338d4fef013b951b931b36da8d8e13ac3c1d8b84d69bb7be0c219ba1ed2b73ee3a081ec9e8f9a9a1cf83c9b6166b3be7c646b2f6b9dd751107660a8ce2dc95fbd700aee6799adfe0d6729ae0f23006ffda0eb86b667cdde725275aac0b040d5bf4f1d2d8701a7cdd303573f598c8348835524c44c7bd6c2963fb380060c5e069a47e1d45dd120992fbdec1f9bcbe39efe9bdb2b3981ba95fd31c23e569c1adc0678cf235a87f32dace59d8a81028bab85fc56154d8536f5c0124c691be99781d1db3307b3d2bcc792c36e4e588045b56b6f7e1b85396074913fbab3147267a98911ff37ca52eb82f76be2be06937f4d4f8fc17c939295d706d1d3776308dcf582514f3a9d3a9a5f72349e095e068833496f5680512e754890c6851248f5ac2ebe3056d9a9e42563029770699199eb3d9d4692bd69134c959e12c26e2f9e956b867f86afedb8c1211f338982f807de634265cadf12b53261686b4c144ef57caad646df1f096ec24512bdaf23ca8601a2c968ecbb403c953f8a19175cc819240c66a473b70a98d86295b8ecb5174302bde4536e9c2674cc561622db1e0f4dab54a2274e697af5a06261dd6e12306cc5f12f99a2d85a796d66"

# Converter hex para bytes
encrypted_data = bytes.fromhex(encrypted_hex)
print(f"\nDados encriptados: {len(encrypted_data)} bytes")

# Tentar diferentes chaves conhecidas do MegaEmbed
keys_to_try = [
    "3wnuij",  # video ID
    "megaembed",
    "megaembedlink",
    "playerthree",
    "playerthree.online",
    "megaembed.link",
]

def try_aes_decrypt(data, key_str, mode='CBC'):
    """Tenta decriptar com AES"""
    try:
        # Derivar chave de 32 bytes (AES-256)
        key = hashlib.sha256(key_str.encode()).digest()
        
        if mode == 'CBC':
            # IV são os primeiros 16 bytes
            iv = data[:16]
            ciphertext = data[16:]
            cipher = AES.new(key, AES.MODE_CBC, iv)
        else:
            cipher = AES.new(key, AES.MODE_ECB)
            ciphertext = data
            
        decrypted = cipher.decrypt(ciphertext)
        
        # Tentar unpad
        try:
            decrypted = unpad(decrypted, AES.block_size)
        except:
            pass
            
        # Verificar se é texto válido
        text = decrypted.decode('utf-8', errors='ignore')
        if '{' in text or 'http' in text or 'm3u8' in text:
            return text
    except Exception as e:
        pass
    return None

print("\nTentando decriptar com diferentes chaves...")

for key in keys_to_try:
    for mode in ['CBC', 'ECB']:
        result = try_aes_decrypt(encrypted_data, key, mode)
        if result:
            print(f"\n[SUCESSO] Chave: {key}, Modo: {mode}")
            print(f"Resultado: {result[:500]}...")
            break
    
    # Tentar com MD5 da chave
    key_md5 = hashlib.md5(key.encode()).hexdigest()
    for mode in ['CBC', 'ECB']:
        result = try_aes_decrypt(encrypted_data, key_md5, mode)
        if result:
            print(f"\n[SUCESSO] Chave MD5: {key_md5}, Modo: {mode}")
            print(f"Resultado: {result[:500]}...")
            break

# Tentar XOR simples
print("\nTentando XOR...")
for key in keys_to_try:
    key_bytes = key.encode() * (len(encrypted_data) // len(key) + 1)
    xored = bytes([a ^ b for a, b in zip(encrypted_data, key_bytes)])
    text = xored.decode('utf-8', errors='ignore')
    if '{' in text[:100] or 'http' in text[:100]:
        print(f"\n[SUCESSO XOR] Chave: {key}")
        print(f"Resultado: {text[:500]}...")
        break

print("\n" + "="*60)
print("Proximo passo: analisar o JS index-CQ0L9dOW.js")
print("="*60)
