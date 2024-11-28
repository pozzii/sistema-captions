import os

# Desabilitar o uso do ImageMagick
os.environ["IMAGEMAGICK_BINARY"] = ""
# Verificar se o caminho foi corretamente definido
print("IMAGEMAGICK_BINARY:", os.environ.get("IMAGEMAGICK_BINARY"))
