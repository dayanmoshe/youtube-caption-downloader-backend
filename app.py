# app.py

from flask import Flask, request, send_file, jsonify
from flask_cors import CORS
import os
import io
from youtube_transcript_api import YouTubeTranscriptApi, NoTranscriptFound, TranscriptsDisabled

app = Flask(__name__)

CORS(app, resources={r"/*": {"origins": "https://dayanmoshe.github.io/youtube-caption-downloader-frontend/"}}) # Permite ualquer origem por enquanto!

@app.route('/download_transcript', methods=['POST'])
def download_transcript():
    if not request.is_json:
        return jsonify({"error": "Requisição deve ser JSON."}), 400

    data = request.get_json()
    youtube_url = data.get('youtube_url')

    if not youtube_url:
        return jsonify({"error": "URL do YouTube não fornecida."}), 400

    try:
        if "v=" in youtube_url:
            video_id = youtube_url.split("v=")[1].split("&")[0]
        elif "youtu.be/" in youtube_url:
            video_id = youtube_url.split("youtu.be/")[1].split("?")[0]
        else:
            return jsonify({"error": "URL do YouTube inválida ou não reconhecida."}), 400

        transcript_list = YouTubeTranscriptApi.get_transcript(video_id, languages=['pt', 'en'])

        transcript_text = ""
        for segment in transcript_list:
            transcript_text += segment['text'] + "\n"

        buffer = io.BytesIO(transcript_text.encode('utf-8'))
        buffer.seek(0)

        return send_file(
            buffer,
            mimetype='text/plain',
            as_attachment=True,
            download_name=f'legenda_{video_id}.txt'
        )

    except NoTranscriptFound:
        return jsonify({"error": "Legenda não encontrada ou não disponível para este vídeo. Pode estar desativada ou não haver legenda no idioma solicitado."}), 404
    except TranscriptsDisabled:
        return jsonify({"error": "Legendas desativadas para este vídeo."}), 403
    except Exception as e:
        print(f"Erro interno: {e}")
        return jsonify({"error": f"Ocorreu um erro inesperado ao processar a requisição: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)