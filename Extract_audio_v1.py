from moviepy.editor import VideoFileClip
import os
import subprocess
import re

def convert_video_to_9_16(input_video_path, output_video_path):
    # Verifica se o arquivo de entrada existe
    if not os.path.isfile(input_video_path):
        print(f"Erro: o arquivo {input_video_path} não foi encontrado.")
        return

    # Comando FFmpeg para obter as informações do vídeo
    probe_command = [
        'ffmpeg', '-i', input_video_path
    ]

    try:
        # Executa o comando para obter as informações do vídeo
        result = subprocess.run(probe_command, stderr=subprocess.PIPE, stdout=subprocess.PIPE, text=True)
        # Extraímos a saída de erro (stderr), que contém as informações sobre o vídeo
        video_info = result.stderr

        # Expressão regular para encontrar a resolução (exemplo: 1920x1080)
        resolution_match = re.search(r'(\d{2,4})x(\d{2,4})', video_info)

        if resolution_match:
            width, height = map(int, resolution_match.groups())
            print(f"Resolução do vídeo: {width}x{height}")
        else:
            print("Erro: Não foi possível encontrar a resolução do vídeo.")
            return

        # Ajusta o corte com base nas dimensões do vídeo
        if width > height:  # Caso o vídeo seja mais largo que alto
            crop_width = height  # Corte a largura para igualar à altura (para manter 9:16)
            crop_x = (width - crop_width) // 2  # Corte no centro
            crop_filter = f'crop={crop_width}:{height}:{crop_x}:0'
        else:
            print("Erro: O vídeo precisa ser mais largo que alto para conversão para 9:16.")
            return

        # Comando FFmpeg para converter o vídeo para o formato 9:16
        # Ajustamos o filtro de escala para garantir que o vídeo preencha completamente a altura de 1920 pixels
        command = [
            'ffmpeg', '-i', input_video_path,
            '-vf', f'{crop_filter},scale=-1:1920',  # Ajusta a largura proporcionalmente à altura de 1920
            '-preset', 'fast',
            output_video_path
        ]

        # Executa o comando FFmpeg
        subprocess.run(command, check=True)
        print(f"Vídeo convertido com sucesso! Salvo em {output_video_path}")

    except subprocess.CalledProcessError as e:
        print(f"Erro ao converter o vídeo: {e}")
    except Exception as e:
        print(f"Ocorreu um erro: {e}")


# Exemplo de uso
input_video = "H:/cortes videos/pinho/aEditar/0001.mp4"
output_video = "H:/cortes videos/pinho/aEditar/0001-9x16.mp4"

convert_video_to_9_16(input_video, output_video)

# Carregar o vídeo
video = VideoFileClip("H:/cortes videos/pinho/aEditar/0001.mp4")

# Extrair o áudio do vídeo
audio = video.audio

# Salvar o áudio em um arquivo (por exemplo, em formato .mp3)
audio.write_audiofile("H:/cortes videos/pinho/aEditar/0001-audio.mp3")
