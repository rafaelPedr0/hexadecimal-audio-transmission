import numpy as np
import scipy.io.wavfile as wav
import sounddevice as sd
import time

# --- DADOS DO ALUNO ---
RA_NUMERO = "23005304"
HEX_STR = "15F0878"  # 23005304 em hexadecimal

# --- PARÂMETROS ---
FS = 44100           
DUR_S = 0.35         
GAP_S = 0.10         
THEME_5 = [262, 330, 392, 523, 784] 

def semitone_shift(freq, semitones):
    return freq * (2 ** (semitones / 12))

# 1. TRANSMISSOR: Gera o arquivo WAV (Parte A)
def gerar_arquivo_wav():
    audio_full = []
    for i, ch in enumerate(HEX_STR):
        v = int(ch, 16)
        base = THEME_5[i % 5]
        shift = v - 6
        freq = semitone_shift(base, shift)
        
        t = np.linspace(0, DUR_S, int(FS * DUR_S), endpoint=False)
        onda = np.sin(2 * np.pi * freq * t)
        
        fade = int(0.02 * FS)
        env = np.ones_like(onda)
        env[:fade] = np.linspace(0, 1, fade)
        env[-fade:] = np.linspace(1, 0, fade)
        
        audio_full.append(onda * env)
        audio_full.append(np.zeros(int(FS * GAP_S)))

    sinal = np.concatenate(audio_full)
    # CORREÇÃO AQUI: variável definida como audio_16bit
    audio_16bit = np.int16(sinal * 0.4 * 32767) 
    
    nome = f"{RA_NUMERO}.wav"
    # CORREÇÃO AQUI: usando o nome correto da variável
    wav.write(nome, FS, audio_16bit) 
    print(f"--- PARTE 1: Arquivo {nome} gerado com sucesso! ---")
    return nome

# 2. RECEPTOR: Identifica frequências e decodifica (Parte B)
def decodificar(origem='arquivo', nome_arquivo=None):
    if origem == 'microfone':
        duracao = len(HEX_STR) * (DUR_S + GAP_S) + 0.5
        print(f"--- PARTE B: Gravando por {duracao:.1f}s. Toque o som! ---")
        gravacao = sd.rec(int(duracao * FS), samplerate=FS, channels=1)
        sd.wait()
        data = gravacao.flatten()
        rate = FS
    else:
        rate, data = wav.read(nome_arquivo)
        print(f"--- PARTE B: Lendo do arquivo {nome_arquivo} ---")

    step = int(rate * (DUR_S + GAP_S))
    res = ""
    for i in range(len(HEX_STR)):
        inicio = i * step
        fim = inicio + int(rate * DUR_S)
        segmento = data[inicio:fim]
        if len(segmento) < 100: break
        
        # FFT para identificar frequências (Parte B - identificar frequências)
        fft_data = np.abs(np.fft.rfft(segmento))
        freqs = np.fft.rfftfreq(len(segmento), 1/rate)
        f_detectada = freqs[np.argmax(fft_data)]
        
        base = THEME_5[i % 5]
        v_rec = 12 * np.log2(f_detectada / base) + 6
        res += hex(int(round(v_rec)))[2:].upper()
    return res

if __name__ == "__main__":
    # Passo 1: Criar o WAV
    nome_wav = gerar_arquivo_wav()
    
    # Passo 2: Decodificar (mude para 'microfone' se quiser testar o som externo)
    resultado = decodificar(origem='arquivo', nome_arquivo=nome_wav)
    
    print(f"\nResultado da Comunicação Digital:")
    print(f"Transmitido (Hex): {HEX_STR}")
    print(f"Recebido (Som -> Hex): {resultado}")
    
    if resultado == HEX_STR:
        print("\nSUCESSO: O sistema decodificou corretamente!")