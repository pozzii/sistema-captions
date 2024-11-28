import whisper
import datetime
import re

from moviepy.config import change_settings
from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip

change_settings({"IMAGEMAGICK_BINARY": r"D:\\Program Files\\ImageMagick-7.1.1-Q16-HDRI\\magick.exe"})


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

# Criar um arquivo .srt
with open("H:/cortes videos/pinho/aEditar/0001-legendas.srt", "w", encoding="utf-8") as f:
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

video_path = "H:/cortes videos/pinho/aEditar/0001-cortado.mp4"
output_video_path = "H:/cortes videos/pinho/aEditar/0001-video-legendado.mp4"

# Carregar o vídeo original
video_clip = VideoFileClip(video_path)


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

print("Vídeo legendado criado com sucesso!")
