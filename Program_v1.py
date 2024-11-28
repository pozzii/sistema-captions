import whisper
import datetime
from moviepy.config import change_settings
from moviepy.editor import  TextClip, CompositeVideoClip

change_settings({"IMAGEMAGICK_BINARY": r"D:\\Program Files\\ImageMagick-7.1.1-Q16-HDRI\\magick.exe"})

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
            'ffmpeg', '-loglevel', 'quiet', '-i', input_video_path,
            '-vf', f'{crop_filter},scale=-1:1920',  # Ajusta a largura proporcionalmente à altura de 1920
            '-preset', 'fast', output_video_path
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
output_video = "H:/cortes videos/pinho/aEditar/0001-cortado.mp4"

convert_video_to_9_16(input_video, output_video)

# Carregar o vídeo
video = VideoFileClip("H:/cortes videos/pinho/aEditar/0001.mp4")

# Extrair o áudio do vídeo
audio = video.audio

path_audio_file = "H:/cortes videos/pinho/aEditar/0001-audio.mp3"

# Salvar o áudio em um arquivo (por exemplo, em formato .mp3)
audio.write_audiofile(path_audio_file)

# Função para formatar o tempo no formato de horas, minutos, segundos e milissegundos
def format_time(seconds):
    return str(datetime.timedelta(seconds=seconds))

# Função para remover vírgulas e outras pontuações
def remove_punctuation(text):
    return re.sub(r'[^\w\s]', '', text)

# Função para dividir o texto em blocos de no máximo 5 palavras
def split_text_into_chunks(text, max_words=5):
    words = text.split()
    return [' '.join(words[i:i+max_words]) for i in range(0, len(words), max_words)]

# Carregar o modelo Whisper
model = whisper.load_model("base")  # ou "small", "medium", "large" dependendo da sua máquina

# Carregar o arquivo de áudio e realizar a transcrição
result = model.transcribe("H:/cortes videos/pinho/aEditar/0001-audio.mp3")

# Obter a lista de segmentos (os momentos em que as falas começam e terminam)
segments = result["segments"]

path_srt_file = f"H:/cortes videos/pinho/aEditar/0001-legendas.srt"


# Criar um arquivo .srt
with open(path_srt_file, "w", encoding="utf-8") as f:
    for i, segment in enumerate(segments):
        start_time = format_time(segment["start"])  # Tempo de início
        end_time = format_time(segment["end"])  # Tempo de fim
        text = segment["text"]  # Texto transcrito

        # Remover pontuação do texto
        text_without_punctuation = remove_punctuation(text)

        # Dividir o texto em partes menores, de no máximo 5 palavras
        chunks = split_text_into_chunks(text_without_punctuation, max_words=5)

        for j, chunk in enumerate(chunks):
            # Escrever cada parte do texto no arquivo .srt
            f.write(f"{i+1}.{j+1}\n")
            f.write(f"{start_time} --> {end_time}\n")
            f.write(f"{chunk}\n\n")

print("Arquivo .srt gerado com sucesso!")

output_video_path = "H:/cortes videos/pinho/aEditar/0001-video-legendado.mp4"

# Carregar o vídeo original
video_clip = VideoFileClip(output_video)


# Criar as legendas para o vídeo
subtitles = []
for segment in segments:
    start_time = segment["start"]
    end_time = segment["end"]
    text = remove_punctuation(segment["text"])

    # Dividir o texto em partes de no máximo 5 palavras+
    chunks = split_text_into_chunks(text, max_words=5)

    # Adicionar uma legenda para cada parte do texto
    for i, chunk in enumerate(chunks):
        subtitle = TextClip(chunk, fontsize=85, color='yellow', method='label', font='fonts/Montserrat-Black.ttf')
        subtitle = subtitle.set_position(("center", 'bottom')).set_duration((end_time - start_time) / len(chunks)).set_start(start_time + (i * (end_time - start_time) / len(chunks)))
        subtitles.append(subtitle)

# Combinar vídeo e legendas
final_video = CompositeVideoClip([video_clip] + subtitles)

# Escrever o vídeo final
final_video.write_videofile(output_video_path, codec='libx264', fps=24)

# Apagar arquivos temporários após o processamento
os.remove(path_audio_file)  # Apagar o arquivo de áudio
os.remove(path_srt_file)    # Apagar o arquivo .srt
os.remove(output_video)  # Apagar o vídeo cortado, se necessário

print("Vídeo legendado criado com sucesso!")
