import whisper
import datetime
import re  # Usaremos a biblioteca re (expressões regulares) para manipular o texto

# Função para formatar o tempo no formato de horas, minutos, segundos e milissegundos
def format_time(seconds):
    return str(datetime.timedelta(seconds=seconds))

# Função para remover vírgulas e outras pontuações (ou você pode adaptar para outros sinais)
def remove_punctuation(text):
    # Usando expressão regular para remover as vírgulas (e outros sinais de pontuação)
    return re.sub(r'[^\w\s]', '', text)

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

        # Remover pontuação (como vírgulas, pontos, etc.) do texto
        text_without_punctuation = remove_punctuation(text)

        # Escrever a legenda no formato .srt
        f.write(f"{i+1}\n")
        f.write(f"{start_time} --> {end_time}\n")
        f.write(f"{text_without_punctuation}\n\n")

print("Arquivo .srt gerado com sucesso!")
