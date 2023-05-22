import imagehash
from PIL import Image
import os


class ComparadorImagens:
    def __init__(self, caminho_img_nova, caminho_pasta):
        self.caminho_img_nova = caminho_img_nova
        self.caminho_pasta_nova = os.path.dirname(caminho_img_nova)
        self.caminho_pasta_velha = caminho_pasta
        self.im_nova = Image.open(caminho_img_nova)
        self.size = (256, 256)

    def comparar_imagens(self):
        """
        Compara uma imagem com todas as imagens de uma pasta e então exclui a de menor qualidade
        """
        for image_file in os.listdir(self.caminho_pasta_velha):
            # Desconsidera arquivos que não são imagens
            if not image_file.endswith(('.jpg', '.png', '.jpeg')):
                continue

            # Caminho completo do arquivo da imagem
            image_path = os.path.join(self.caminho_pasta_velha, image_file)
            # Abre a imagem da pasta selecionada
            self.im_velha = Image.open(image_path)

            # Redimensiona as imagens para o mesmo tamanho
            self.im_nova.thumbnail(self.size, Image.ANTIALIAS)
            self.im_velha.thumbnail(self.size, Image.ANTIALIAS)

            # Calcula os hashes para as duas imagens
            hash_nova = imagehash.average_hash(self.im_nova)
            hash_velha = imagehash.average_hash(self.im_velha)

            # Compara os hashes das imagens
            if hash_nova == hash_velha:
                print(self.caminho_img_nova,
                      "e", image_file, "são idênticas.")
                # calcula as resoluções das imagens
                resolution_nova = hash_nova.size[0] * hash_nova.size[1]
                resolution_velha = hash_velha.size[0] * hash_velha.size[1]

                # compara as resoluções das imagens para definir qual imagem manter, e a exclui a outra imagem
                if resolution_nova > resolution_velha:
                    hash_velha.close()
                    os.remove('imagem2.png')
                else:
                    hash_nova.close()
                    os.remove('imagem1.jpg')

            else:
                print(self.caminho_img_nova,
                      "e", image_file, "não são idênticas.")

            # Fecha o objeto da imagem de comparação
            self.im_velha.close()

    def __del__(self):
        print('Finalizando programa.')
        self.im_nova.close()
