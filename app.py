import json
import os

from dotenv import load_dotenv
from flask import Flask, jsonify, render_template, request
from openai import OpenAI

load_dotenv()

app = Flask(__name__)

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")

client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None


def build_user_context(data):
    return {
        "song_concept": data.get("concept", "").strip(),
        "situation": data.get("situation", "").strip(),
        "emotion": data.get("emotion", "").strip(),
        "genre": data.get("genre", "").strip(),
        "vocal": data.get("vocal", "").strip(),
        "language": data.get("language", "").strip(),
        "bpm": data.get("bpm", "").strip(),
        "duration": data.get("duration", "").strip(),
        "sound_tags": data.get("sound_tags", []),
        "sound_texture": data.get("sound_texture", []),
        "extra": data.get("extra", "").strip(),
    }


def should_make_instrumental(context):
    vocal = context.get("vocal", "")
    language = context.get("language", "")
    return vocal == "없음" or language == "가사 없음"


def call_openai(task, data):
    if client is None:
        raise RuntimeError(".env 파일에 OPENAI_API_KEY를 설정해 주세요.")

    context = build_user_context(data)
    instrumental = should_make_instrumental(context)

    system_prompt = """
You are a practical Suno AI music production assistant for a local personal web app.
Generate concise, copy-ready outputs for Suno and YouTube.

Rules:
- Return valid JSON only.
- "style_prompt" must always be written in English.
- If lyrics are requested, write lyrics in the selected language.
- If vocal is "없음" or language is "가사 없음", do not write lyrics. Instead, return a short instrumental guidance message in "lyrics".
- Avoid copyrighted artist imitation. Describe style, arrangement, mood, tempo, vocal type, and production texture instead.
- Keep Suno style prompt compact and useful.
- Make section values directly pasteable.
"""

    task_prompts = {
        "prompt": "Create only the Suno style prompt and a few title/metadata suggestions.",
        "lyrics": "Create Suno-ready lyrics or instrumental guidance, plus useful title/metadata suggestions.",
        "package": "Create the full package: Suno style prompt, lyrics or instrumental guidance, titles, description, tags, and thumbnail copy.",
    }

    schema_note = {
        "style_prompt": "English Suno style prompt",
        "lyrics": "Lyrics in selected language, or instrumental guidance",
        "song_title": "Recommended song title",
        "youtube_title": "YouTube title",
        "youtube_description": "YouTube description",
        "youtube_tags": ["tag1", "tag2", "tag3"],
        "thumbnail_text": "Short thumbnail copy",
    }

    user_prompt = f"""
Task: {task_prompts[task]}

Input:
{json.dumps(context, ensure_ascii=False, indent=2)}

Instrumental mode: {instrumental}

Return this JSON shape:
{json.dumps(schema_note, ensure_ascii=False, indent=2)}
"""

    response = client.chat.completions.create(
        model=OPENAI_MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        response_format={"type": "json_object"},
        temperature=0.8,
    )

    content = response.choices[0].message.content
    result = json.loads(content)

    return {
        "style_prompt": result.get("style_prompt", ""),
        "lyrics": result.get("lyrics", ""),
        "song_title": result.get("song_title", ""),
        "youtube_title": result.get("youtube_title", ""),
        "youtube_description": result.get("youtube_description", ""),
        "youtube_tags": result.get("youtube_tags", []),
        "thumbnail_text": result.get("thumbnail_text", ""),
    }


def generate(task):
    data = request.get_json(silent=True) or {}

    if not data.get("concept", "").strip():
        return jsonify({"error": "곡 컨셉을 입력해 주세요."}), 400

    try:
        return jsonify(call_openai(task, data))
    except RuntimeError as error:
        return jsonify({"error": str(error)}), 500
    except Exception as error:
        return jsonify({"error": f"생성 중 문제가 발생했습니다: {error}"}), 500


@app.get("/")
def index():
    return render_template("index.html")


@app.post("/generate-prompt")
def generate_prompt():
    return generate("prompt")


@app.post("/generate-lyrics")
def generate_lyrics():
    return generate("lyrics")


@app.post("/generate-package")
def generate_package():
    return generate("package")


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
