from PIL import Image, ImageFilter

def abrir_imagem(caminho):
    return Image.open(caminho)

def aplicar_blur(imagem):
    return imagem.filter(ImageFilter.BLUR)

def salvar_imagem(imagem, caminho):
    imagem.save(caminho)
