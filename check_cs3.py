import zipfile
import os

# Verificar MaxSeries.cs3
print('=== Analise do MaxSeries.cs3 ===')
try:
    with zipfile.ZipFile('MaxSeries.cs3', 'r') as zf:
        files = zf.namelist()
        print(f'Total de arquivos no CS3: {len(files)}')
        
        # Verificar conteúdo do classes.jar
        if 'classes.jar' in files:
            print('\n=== Analisando classes.jar ===')
            import io
            classes_jar_data = zf.read('classes.jar')
            
            with zipfile.ZipFile(io.BytesIO(classes_jar_data), 'r') as classes_zf:
                class_files = classes_zf.namelist()
                print(f'Total de arquivos em classes.jar: {len(class_files)}')
                
                # Procurar por arquivos do plugin
                plugin_files = [f for f in class_files if 'MaxSeries' in f or 'Cloudstream' in f]
                print(f'\nArquivos relacionados ao plugin: {len(plugin_files)}')
                for f in plugin_files[:10]:
                    print(f'  {f}')
                
                # Verificar se tem o plugin principal
                main_plugin = [f for f in class_files if 'MaxSeriesPlugin' in f]
                print(f'\nArquivo MaxSeriesPlugin: {main_plugin}')
                
                # Verificar se tem o provider
                provider = [f for f in class_files if 'MaxSeriesProvider' in f]
                print(f'Arquivo MaxSeriesProvider: {provider}')
                
                # Listar alguns arquivos de classe
                print('\nPrimeiros 20 arquivos .class:')
                class_files_list = [f for f in class_files if f.endswith('.class')][:20]
                for f in class_files_list:
                    print(f'  {f}')
                    
        print('\n=== VALIDACAO ===')
        # Verificar se o plugin tem a estrutura necessária
        has_manifest = 'AndroidManifest.xml' in files
        has_classes = 'classes.jar' in files
        
        if has_manifest and has_classes:
            print('✓ Estrutura basica do CS3 esta OK')
            print('✓ Tem AndroidManifest.xml')
            print('✓ Tem classes.jar')
        else:
            print('✗ Estrutura basica incompleta!')
            
except Exception as e:
    print(f'Erro: {e}')
    import traceback
    traceback.print_exc()
