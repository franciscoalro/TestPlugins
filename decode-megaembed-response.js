/**
 * MegaEmbed Response Decoder
 * Decodifica a resposta hexadecimal da API do MegaEmbed
 */

const fs = require('fs');

// Cole aqui a resposta hexadecimal completa
const hexResponse = `29e8fa7760f7ab789fd65337950d914c93a7225c53c8e075dc7a62dc92ee1857d87cab95e670b6e3803bf4e02b292a1ae675449a187a36c368bff3513c29abf3e2d51a83a45a5803e202aa139c8da4d86748a3c311b4fdf793bbd452bbebc4d26411834ad84799e19ad238d21158b5c8912f34457513834a28c840428bc6e8b3fd660a32025ad7fe048787bf01a52a48457daa91108674b64b427f8c6a28fc8e950d40080203480db8fea1b3e3fd0bb85e3c210fdfda2e80ea8cd4f6994887dee2b4ee81ddd1822dc6bd44db917c6c35372f703b54bfd7cd0b81a590f76a63a2187cd683aac3815b8ef1ee98f5c95bc517378709ea527912e81d18b227308fee814f98c29f7c67162f9564cc84319f4a81832dcd82faa9da9b44005293d897e197a2360eae999bce67e33525713fdba6207d40811f99b5777dfb8c365ec9d138c04cf08988dddff4c57b9d03d076368e6d3ebc3ff5dba8b2b8d2709e1803eef422c86def607e4b614c87610b82adf8ca54963c93b9eb4a2085157e199e4efbcdcbf266d85bac033525d253fcc14b2af54a731c9a6beb523369ba0a285e97ac01e1db2b91a771732aa4568a315a78072b05fcae55cf75d8924d638d7592b85d52e2abca387e6a6b4a8059c1d1f64ff912fba0092bca95e6af159a7f5e491a9b7b3b4250ce675ae2d07c727dfff80b6155129ce31d38bd058116e16e997bb4c20f11e03b38d8622d2a078eb5e0f107915f8b9a3cd8f0cdcf1e044dd1072b935e720508732b94eed6e0c246c72ad2d18382101d78595414eb352be2fdce96ffa64b8350413057b9820decb5bc744a67f4b418f8b9173dc1d59fa434450be6016b2aeda6f266f8423d4d9a0532e0cb6f61f6e4946123c2e72dea5ac28a558b62f6e4c46af9924354891d9c2092b2a89cf3192c20725441630e53b35cb28556f41f980d9b3705a19c0e161bbd30cf49e60a27af542cc68dd1dbfba372ede981b9aef36b1a037398d02e08ba2144257019f37822997c84ea4cd7f99015b8492c6728cc80015b356e806f36b1bd01f19f7435d845e877dcee20da79c9290191c94f30b12e4846a56a998c5f2ad270c70195667ffed3b72559aca27cf3fc1a47441029016c741e5f8cea5ca7e1a01d31f5bf9f7b8357103c6e60a3300ef4df67dedf8901852de73e7b05b0041daeadfc4fec69c8e044a125842861a544189a7560d3621f29eb1c4e627af54840172d965a30434e3bf56a49317540975cc030a2ef6cf7c9613366ccf2f6b830f488c9800447a1e9c9d5c31d844aa6eac41ea381ec3ac31d013999af0da85716ca27b464f20e68b8121111d85ca80a991de3d453a706c504ad215480cac6be7ebe2050f067d70762e610cc88dc76737f999e6237f839906369cde3a026c3e17390ebd950becde1c6ff2a71a1b71d7351215235d65a533f32278c40a9c789a57382c825330dab6717686231f6659b32b675a36545e871dfafc9e34bb74c0b07c4a0e5041736979eabca59ee35dfb1d6d0f8761a1dc0ebf03c7320ea95a2a5cca3e0da0c6f72fa674b9c3cb6537494f422a4ab20573bde4399b7f655ff5c3087ab5d7d7b78b2d6b04d7825fefc95c838d08bd4bebca8207d4911b313e1f3f7ae9fc7dc5ae41f5ce2476826406e3442161154c65fe5080abc69cbc25df894e58868e1ca85b8725861bd69ed71ff02c76e459ece6878a8c1c840c9c1c85b842e9e627873fbe9956b86bed57f58dd4023f6b21b706aff58f1fa6344bdc149eaec677cf361f8cf9d50c13faa0c08751bc23fe5cb38ba2f72e5abdc2e76ce44307256f7678672a273eb2ded64d7449a28a43bed74b4d8eebe9ef0a858460cde07745dde6162612f006accaae0f418ecdd7f18836fe5731a887d1b990925dd6b17f7cea2882755af243672c9b426744e25abe31de77a53c81e367fba32d6164f14eaa9df476448da758324e07e018e17467c660b4049b3268f5977686a96bd9dcfe94c53bae494ad7084ad417f437e773b184ebfbb90c70c481be162205cfbc4aef1a35cfca80394729e571b06db0b697ff29118eec35e5386744deca30d7c489e8519cd4fcef699a1b7fce06b2ddfd33f727fc434a8e55a4be0f07bbd466155e17d016da51a06cd91a0a6c04a0b3f69b0b4212d0ed16e4dcdd0916677e7b9fb2b62aad6489ba125af19e08524dd5a7430b758be9ec9558653c63c760d8359589b6f5212fceb1e6ad545c825c4dc1cb27c79e138d25fce12c288c5df6a708071d41f98edab843537c25e5403b060e731429cf773a4214e896127bcdcca2092bb3e3032e88ba2666232c1de1a50833322f708fcf3af776ae2ab6aa717f19fa75b7dbc9a8562e8b4d5307bbff47623045e3c5f74aae340c91257a76372e27b6036385df8fb30ab5262950bbea53633382d922ee4e8ef468145daa67ec8e3c1a6e85c5b02c86b92f5638f78b30185b59eb252c8a0db0e1b91b726672212a745ea91bfa5a148dc782e561405855a98c64f1b7b39640023fbf87c9a6bca41a34e6a291a5b95254a30db90a56024d2824afe7db411ccd3f7a03a2947d510b8530ddef8006e406805c4cdf8357a51c22f9a027149eaaef1a88a522083e91f0cc1ebce6c6ca8d07e2eac835614cd66fca62bfcb32e7a8b07c8d30971b68702de6a28885481ccff817dd84d6c85b0e46406401b133439c62601a2e007d2ccf0ec6c280fffa3b627c2ab78205157277d24f306f4f73601e4d0e6d4f23bac0c1461fdb59784a39f8b52a02a3cf7f4255ef7962433e626e8edd1ec646a0d8aaa6d15035bc9ce59dc7c68273c15c3c7895710d5ab619d54b35dea49114bf96086ed78afe50d3f3b9c16712f3fc211c560cb7ff63f13f030416497724d96b964cee7d187c4633b74acfd40bef4fc59e7fd48c420a771ee183335fa8226419e7cc58908b2c44315a94d395968f98b11427d50a09f4b44dded4c2ab0f134ca34f684f69c0c8e62e60cbb97c3b8910a47666707fc54912f9d0a0c27e7553793cd6ddf0b52f266bbad9b2827c1626555f3556cdd8a4375cd989c2f47e9cf90b34ae41d652b3a4709f70c37ba19492aaa9165dd2789cf5d026a93101d83b39aa13db6982dc6d0a96a67df5c0e3cce43e26738a9e51c4b4fde4d68733b0a981950706554fd9d6b50749456e00cbd1cb4b08204ab1582251327652b14125400e759c7e14bdf0453d2db850c57df18c6e28c5ead013dfc8939343ad5b155832784c99c8178ca8f05906a61cc5baa989aae333caa37345cf167de6de83f63fe27765470e7f85bc49cbbd361da044b160a227dc55c7a9cd5f292801e10562df7f8a7bf0488d761f24a2d69d6cbc0f81e3a1985d33736779ffab7342c74455655f59cfecd0055bbdab035f1c07b22a4689fe9dcb80701e0f95f1a7cf518e6816742a63f6b549bf90c303f9a0861b1ec4fb7ac1ba2414e81236e719c133afbbb27a46b319e4a8c132ed489551fc9e1a8a40de5b5aab1e8316befdb0294aaf484f77a3c43c2ecd3cfaa65131e3c582eee254a0c59b6f4874de4c9d70dbe7b4ac5c0be886ec0e315869436482f37cbdf641f8e66447705b15f38e021199fc6e6f8036b4c2eacabf5d146ad71343cc3b863ba6bd8dc97be2241b3394902d55add9961d00efe225505e547`;

console.log('🔓 MegaEmbed Response Decoder\n');
console.log('='.repeat(80));

// 1. Converter HEX para Buffer
console.log('\n📊 Tamanho da resposta HEX:', hexResponse.length, 'caracteres');
console.log('📊 Tamanho em bytes:', hexResponse.length / 2, 'bytes\n');

const buffer = Buffer.from(hexResponse, 'hex');

// 2. Tentar decodificar como UTF-8
console.log('🔍 Tentando decodificar como UTF-8...\n');
const utf8Text = buffer.toString('utf-8');
console.log('Resultado UTF-8:');
console.log(utf8Text.substring(0, 500));
console.log('\n...\n');

// 3. Procurar por padrões de URL
console.log('🔍 Procurando por URLs...\n');
const urlPatterns = [
    /https?:\/\/[^\s"'<>]+\.m3u8[^\s"']*/gi,
    /https?:\/\/[^\s"'<>]+\.mp4[^\s"']*/gi,
    /https?:\/\/[^\s"'<>]+/gi,
];

urlPatterns.forEach((pattern, i) => {
    const matches = utf8Text.match(pattern);
    if (matches) {
        console.log(`Padrão ${i + 1} encontrou ${matches.length} URLs:`);
        matches.forEach(url => console.log(`  - ${url}`));
        console.log('');
    }
});

// 4. Procurar por strings "file", "src", "url"
console.log('🔍 Procurando por chaves JSON...\n');
const jsonKeys = ['"file":', '"src":', '"url":', '"sources":'];
jsonKeys.forEach(key => {
    const index = utf8Text.indexOf(key);
    if (index !== -1) {
        console.log(`✅ Encontrado: ${key} na posição ${index}`);
        console.log(`   Contexto: ${utf8Text.substring(index, index + 200)}\n`);
    }
});

// 5. Tentar parsear como JSON
console.log('🔍 Tentando parsear como JSON...\n');
try {
    const jsonData = JSON.parse(utf8Text);
    console.log('✅ JSON válido!\n');
    console.log(JSON.stringify(jsonData, null, 2));

    // Salvar JSON
    fs.writeFileSync('megaembed-decoded.json', JSON.stringify(jsonData, null, 2));
    console.log('\n💾 JSON salvo em: megaembed-decoded.json');
} catch (e) {
    console.log('❌ Não é JSON válido:', e.message);
}

// 6. Salvar texto decodificado
fs.writeFileSync('megaembed-decoded.txt', utf8Text);
console.log('\n💾 Texto completo salvo em: megaembed-decoded.txt');

// 7. Análise de bytes
console.log('\n📊 Primeiros 100 bytes (hex):');
console.log(hexResponse.substring(0, 200));

console.log('\n📊 Primeiros 100 bytes (ASCII):');
console.log(buffer.toString('ascii', 0, 100));

console.log('\n' + '='.repeat(80));
console.log('✅ Análise completa! Verifique os arquivos gerados.\n');
