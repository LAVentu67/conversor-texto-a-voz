from flask import Flask, request, render_template_string, send_file
from gtts import gTTS
import os
import uuid # Usaremos esto para nombres de archivo únicos

app = Flask(__name__)
AUDIO_FOLDER = 'audio'
os.makedirs(AUDIO_FOLDER, exist_ok=True)

# HTML + CSS con el nuevo diseño Formal (Blanco, Negro, Gris)
HTML_PAGE = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>LGA - Conversor de Texto a Voz</title>
    
    <!-- Tipografía (se mantiene Poppins por su claridad) -->
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600&display=swap" rel="stylesheet">
    
    <!-- Iconos -->
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.2/css/all.min.css">

    <style>
        /* --- ESTILOS GENERALES Y PALETA DE COLORES --- */
        :root {
            --color-background: #f4f7f9; /* Gris muy claro para el fondo */
            --color-surface: #ffffff;    /* Blanco para el contenedor principal */
            --color-text-primary: #1a1a1a; /* Negro suave para textos principales */
            --color-text-secondary: #666666;/* Gris para textos secundarios y placeholders */
            --color-border: #e0e0e0;      /* Gris claro para bordes */
            --color-primary: #2c3e50;     /* Gris oscuro/azulado para el botón */
            --color-primary-hover: #34495e;/* Tono más claro para el hover del botón */
        }

        body {
            font-family: 'Poppins', sans-serif;
            background-color: var(--color-background);
            color: var(--color-text-primary);
            display: flex;
            align-items: center;
            justify-content: center;
            min-height: 100vh;
            margin: 0;
            padding: 20px;
            box-sizing: border-box;
        }

        /* --- CONTENEDOR PRINCIPAL --- */
        .container {
            width: 100%;
            max-width: 550px;
            background-color: var(--color-surface);
            border: 1px solid var(--color-border);
            border-radius: 12px; /* Bordes menos pronunciados */
            padding: 40px;
            /* Sombra sutil para un efecto de elevación profesional */
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.07);
            text-align: center;
            animation: fadeIn 0.6s ease-out;
        }

        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(-15px); }
            to { opacity: 1; transform: translateY(0); }
        }

        /* --- TÍTULO --- */
        h2 {
            font-weight: 600;
            font-size: 1.7rem; /* Ligeramente más pequeño para formalidad */
            margin-top: 0;
            margin-bottom: 30px;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 12px;
            color: var(--color-text-primary);
        }
        
        h2 .fa-microphone-lines {
            color: var(--color-primary);
        }

        /* --- ÁREA DE TEXTO --- */
        textarea {
            width: 100%;
            height: 130px;
            background-color: #fcfcfc;
            border: 1px solid var(--color-border);
            border-radius: 8px;
            padding: 15px;
            resize: vertical; /* Permite redimensionar verticalmente */
            color: var(--color-text-primary);
            font-family: 'Poppins', sans-serif;
            font-size: 1rem;
            transition: border-color 0.3s, box-shadow 0.3s;
            box-sizing: border-box;
        }

        textarea::placeholder {
            color: var(--color-text-secondary);
        }

        textarea:focus {
            outline: none;
            border-color: var(--color-primary);
            box-shadow: 0 0 0 3px rgba(44, 62, 80, 0.1); /* Sombra de foco sutil */
        }

        /* --- BOTÓN DE ACCIÓN --- */
        button {
            margin-top: 20px;
            padding: 12px 30px;
            background-color: var(--color-primary);
            color: var(--color-surface);
            border: none;
            border-radius: 8px;
            cursor: pointer;
            font-family: 'Poppins', sans-serif;
            font-weight: 500;
            font-size: 1rem;
            transition: background-color 0.2s;
            display: inline-flex;
            align-items: center;
            gap: 10px;
        }

        button:hover {
            background-color: var(--color-primary-hover);
        }

        /* --- SECCIÓN DE RESULTADOS --- */
        .result-container {
            margin-top: 35px;
            padding-top: 25px;
            border-top: 1px solid var(--color-border);
            text-align: left;
        }

        .result-container h3 {
            margin-top: 0;
            margin-bottom: 15px;
            font-weight: 500;
            font-size: 1.1rem;
            color: var(--color-text-primary);
        }
        
        /* Contenedor para el texto generado (opcional, si se quiere mostrar) */
        .result-container p {
            background-color: var(--color-background); /* Fondo gris claro para diferenciar */
            padding: 15px;
            border-radius: 8px;
            border: 1px solid var(--color-border);
            word-wrap: break-word;
            color: var(--color-text-secondary);
        }

        /* --- REPRODUCTOR DE AUDIO --- */
        audio {
            margin-top: 15px;
            width: 100%;
            /* Estilo para los controles de audio en Chrome/Safari */
            accent-color: var(--color-primary); 
        }

    </style>
</head>
<body>

    <div class="container">
        <h2>
            <i class="fa-solid fa-microphone-lines"></i>
            LGA - Conversor de Texto a Voz
        </h2>
        
        <form method="POST">
            <!-- Rellena el textarea con el texto enviado -->
            <textarea name="texto" placeholder="Escribe tu texto aquí..." required>{% if texto %}{{ texto }}{% endif %}</textarea>
            <br>
            <button type="submit">
                <i class="fa-solid fa-play"></i>
                Generar Audio
            </button>
        </form>
        
        <!-- Bloque de resultados (se muestra si se generó un audio) -->
        {% if audio_filename %}
        <div class="result-container">
            <h3>Tu audio está listo:</h3>
            <!-- El texto ya se muestra arriba, así que este <p> es opcional -->
            <!-- <p>{{ texto }}</p> -->
            <audio controls autoplay>
                <!-- Conectado a la ruta de Flask -->
                <source src="{{ url_for('audio', filename=audio_filename) }}" type="audio/mpeg">
                Tu navegador no soporta el elemento de audio.
            </audio>
        </div>
        {% endif %}
    </div>

</body>
</html>
"""

@app.route('/', methods=['GET', 'POST'])
def index():
    texto = None
    audio_filename = None
    if request.method == 'POST':
        texto = request.form['texto']
        if texto:
            tts = gTTS(text=texto, lang='es')
            # Genera un nombre de archivo único para evitar sobrescribir
            audio_filename = f"audio_{uuid.uuid4()}.mp3"
            audio_path = os.path.join(AUDIO_FOLDER, audio_filename)
            tts.save(audio_path)
            
    # El texto se pasa de vuelta para rellenar el textarea
    return render_template_string(HTML_PAGE, texto=texto, audio_filename=audio_filename)

@app.route('/audio/<filename>')
def audio(filename):
    # Validar que el archivo solicitado esté en la carpeta de audio
    # (medida de seguridad simple)
    safe_path = os.path.join(AUDIO_FOLDER, filename)
    if not os.path.isfile(safe_path):
        return "Archivo no encontrado", 404
        
    return send_file(safe_path, mimetype='audio/mpeg')

if __name__ == '__main__':
    app.run(debug=True)

