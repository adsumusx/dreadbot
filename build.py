#!/usr/bin/env python3
"""
Script de Build para gerar executável do Bot DreadmystDB
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path


def check_pyinstaller():
    """Verifica se PyInstaller está instalado"""
    try:
        import PyInstaller
        return True
    except ImportError:
        return False


def install_pyinstaller():
    """Instala PyInstaller"""
    print("📦 Instalando PyInstaller...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
    print("✅ PyInstaller instalado com sucesso!")


def build_exe():
    """Gera o executável"""
    print("=" * 60)
    print("🔨 Build do Bot DreadmystDB")
    print("=" * 60)
    
    # Verifica PyInstaller
    if not check_pyinstaller():
        print("⚠ PyInstaller não encontrado. Instalando...")
        install_pyinstaller()
    
    # Arquivos necessários
    main_script = "bot_gui.py"
    icon_file = None  # Você pode adicionar um ícone .ico aqui se tiver
    
    # Verifica se o arquivo principal existe
    if not os.path.exists(main_script):
        print(f"❌ Erro: Arquivo '{main_script}' não encontrado!")
        sys.exit(1)
    
    # Comando PyInstaller (usando Python -m pyinstaller para garantir que funciona)
    cmd = [
        sys.executable,  # Usa o Python atual
        "-m", "PyInstaller",
        "--onefile",  # Um único arquivo executável
        "--windowed",  # Sem console (GUI)
        "--name", "DreadmystBot",  # Nome do executável
        "--clean",  # Limpa cache antes de build
        "--noconfirm",  # Não pergunta para sobrescrever
    ]
    
    # Adiciona ícone se existir
    if icon_file and os.path.exists(icon_file):
        cmd.extend(["--icon", icon_file])
    
    # Adiciona arquivos de dados (se necessário)
    # cmd.extend(["--add-data", "config.json;."])  # Windows
    # cmd.extend(["--add-data", "config.json:."])  # Linux/Mac
    
    # Arquivo principal
    cmd.append(main_script)
    
    print(f"\n📝 Comando: {' '.join(cmd)}\n")
    print("⏳ Gerando executável... (isso pode levar alguns minutos)\n")
    
    try:
        # Executa PyInstaller
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        
        # Mostra output se houver
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print(result.stderr)
        
        # Verifica se o executável foi criado
        dist_dir = Path("dist")
        exe_name = "DreadmystBot.exe" if sys.platform == "win32" else "DreadmystBot"
        exe_path = dist_dir / exe_name
        
        if exe_path.exists():
            print("\n" + "=" * 60)
            print("✅ Build concluído com sucesso!")
            print("=" * 60)
            print(f"\n📦 Executável gerado em: {exe_path.absolute()}")
            print(f"📁 Tamanho: {exe_path.stat().st_size / (1024*1024):.2f} MB")
            print("\n💡 Próximos passos:")
            print("   1. Teste o executável")
            print("   2. Gere uma licença com: python keygen.py <dias>")
            print("   3. Distribua o executável e a licença para os clientes")
            print("\n⚠ IMPORTANTE:")
            print("   - O executável precisa do arquivo 'license.key' para funcionar")
            print("   - Cada cliente precisa de uma licença válida")
            print("   - Use keygen.py para gerar licenças com diferentes períodos")
            print("=" * 60)
        else:
            print(f"\n❌ Erro: Executável não encontrado em {exe_path}")
            print("   Verifique os logs acima para mais detalhes.")
            sys.exit(1)
            
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Erro durante o build: {e}")
        if hasattr(e, 'stdout') and e.stdout:
            print(f"\n📋 Output:\n{e.stdout}")
        if hasattr(e, 'stderr') and e.stderr:
            print(f"\n⚠ Erros:\n{e.stderr}")
        sys.exit(1)
    except FileNotFoundError as e:
        print(f"\n❌ Erro: Arquivo ou comando não encontrado: {e}")
        print("   Tente executar: python -m pip install pyinstaller")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Erro inesperado: {e}")
        import traceback
        print(f"\n📋 Traceback completo:")
        traceback.print_exc()
        sys.exit(1)


def clean_build():
    """Limpa arquivos temporários do build"""
    print("\n🧹 Limpando arquivos temporários...")
    
    dirs_to_remove = ["build", "__pycache__"]
    files_to_remove = ["DreadmystBot.spec"]
    
    for dir_name in dirs_to_remove:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
            print(f"   ✓ Removido: {dir_name}/")
    
    for file_name in files_to_remove:
        if os.path.exists(file_name):
            os.remove(file_name)
            print(f"   ✓ Removido: {file_name}")
    
    print("✅ Limpeza concluída!")


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description="Build do Bot DreadmystDB")
    parser.add_argument('--clean', action='store_true', help='Limpa arquivos temporários após o build')
    args = parser.parse_args()
    
    build_exe()
    
    if args.clean:
        clean_build()

