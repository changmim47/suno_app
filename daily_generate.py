import json
import os
import random
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")
TIMEZONE = ZoneInfo("Asia/Seoul")

SITUATIONS = ["퇴근길", "새벽 감성", "카페 작업", "여행", "운동", "이별 후", "새로운 시작"]
EMOTIONS = ["따뜻함", "설렘", "쓸쓸함", "몽환적", "희망적", "담담함", "에너지 넘침"]
GENRES = ["K-pop ballad", "Lo-fi pop", "City pop", "Indie folk", "R&B", "Synthwave", "Acoustic pop", "EDM"]
VOCALS = ["여성 보컬", "남성 보컬", "듀엣", "코러스 중심", "없음"]
LANGUAGES = ["한국어", "영어", "일본어", "한국어와 영어 혼합", "가사 없음"]
DURATIONS = ["1분 내외", "2분 내외", "3분 내외", "4분 내외"]
TEXTURES = ["vinyl crackle", "rain ambience", "tape hiss", "analog warmth"]

TAG_GROUPS = {
    "mood": [
        "calm",
        "dreamy",
        "nostalgic",
        "cozy",
        "melancholic",
        "hopeful",
        "uplifting",
        "romantic",
        "energetic",
    ],
    "genre": [
        "lofi",
        "chillhop",
        "city pop",
        "neo soul",
        "synthwave",
        "acoustic pop",
        "indie folk",
        "future bass",
    ],
    "instrument": [
        "piano",
        "electric piano",
        "acoustic guitar",
        "jazz guitar",
        "warm bass",
        "analog synth",
        "strings",
        "saxophone",
    ],
    "groove": [
        "steady 4/4",
        "slow swing",
        "half-time beat",
        "groovy funk",
        "room reverb",
        "tape saturation",
        "city ambience",
        "soft distortion",
    ],
}

PRESETS = [
    {
        "name": "공부용 Lofi",
        "concept": "집중이 필요한 오후, 조용히 흐르는 공부용 로파이",
        "situation": "카페 작업",
        "emotion": "담담함",
        "genre": "Lo-fi pop",
        "vocal": "없음",
        "language": "가사 없음",
        "bpm": 72,
        "tags": ["calm", "lofi", "piano", "warm bass", "steady 4/4", "room reverb"],
    },
    {
        "name": "비오는 날 감성",
        "concept": "비 오는 밤 창가에서 오래된 마음을 정리하는 노래",
        "situation": "새벽 감성",
        "emotion": "쓸쓸함",
        "genre": "City pop",
        "vocal": "여성 보컬",
        "language": "한국어",
        "bpm": 88,
        "tags": ["melancholic", "dreamy", "city pop", "electric piano", "slow swing", "city ambience"],
    },
    {
        "name": "드라이브 Chill",
        "concept": "늦은 밤 도로 위를 부드럽게 달리는 드라이브 음악",
        "situation": "여행",
        "emotion": "희망적",
        "genre": "Synthwave",
        "vocal": "남성 보컬",
        "language": "영어",
        "bpm": 104,
        "tags": ["uplifting", "synthwave", "analog synth", "warm bass", "steady 4/4", "room reverb"],
    },
    {
        "name": "어쿠스틱 새출발",
        "concept": "조용한 아침, 다시 시작하는 마음을 담은 어쿠스틱 팝",
        "situation": "새로운 시작",
        "emotion": "따뜻함",
        "genre": "Acoustic pop",
        "vocal": "여성 보컬",
        "language": "한국어",
        "bpm": 96,
        "tags": ["cozy", "hopeful", "acoustic pop", "acoustic guitar", "strings", "steady 4/4"],
    },
    {
        "name": "몽환 R&B",
        "concept": "새벽 공기처럼 부드럽고 몽환적인 R&B 트랙",
        "situation": "새벽 감성",
        "emotion": "몽환적",
        "genre": "R&B",
        "vocal": "듀엣",
        "language": "한국어와 영어 혼합",
        "bpm": 82,
        "tags": ["dreamy", "romantic", "neo soul", "electric piano", "warm bass", "half-time beat"],
    },
    {
        "name": "운동 EDM",
        "concept": "짧고 강하게 몰입되는 운동용 에너지 트랙",
        "situation": "운동",
        "emotion": "에너지 넘침",
        "genre": "EDM",
        "vocal": "코러스 중심",
        "language": "영어",
        "bpm": 128,
        "tags": ["energetic", "future bass", "analog synth", "soft distortion", "groovy funk", "steady 4/4"],
    },
]

CONCEPT_TEMPLATES = [
    "{situation}에 어울리는 {emotion} 느낌의 {genre} 트랙",
    "{emotion} 감정을 중심으로 전개되는 {duration} {genre} 음악",
    "{situation} 장면을 위한 {bpm} BPM의 {emotion} Suno 곡",
    "오늘의 랜덤 아이디어: {situation}, {emotion}, {genre}",
]


def random_context():
    use_preset = random.random() < 0.55

    if use_preset:
        preset = random.choice(PRESETS)
        context = {
            "song_concept": preset["concept"],
            "situation": preset["situation"],
            "emotion": preset["emotion"],
            "genre": preset["genre"],
            "vocal": preset["vocal"],
            "language": preset["language"],
            "bpm": str(preset["bpm"]),
            "duration": random.choice(DURATIONS),
            "sound_tags": random.sample(preset["tags"], k=min(len(preset["tags"]), random.randint(4, 6))),
            "sound_texture": random.sample(TEXTURES, k=random.randint(0, 2)),
            "extra": f"프리셋 기반 자동 생성: {preset['name']}",
        }
    else:
        situation = random.choice(SITUATIONS)
        emotion = random.choice(EMOTIONS)
        genre = random.choice(GENRES)
        bpm = random.randint(64, 138)
        duration = random.choice(DURATIONS)
        language = random.choice(LANGUAGES)
        vocal = "없음" if language == "가사 없음" else random.choice(VOCALS)
        tags = []

        for group_tags in TAG_GROUPS.values():
            tags.extend(random.sample(group_tags, k=random.randint(1, 2)))

        concept = random.choice(CONCEPT_TEMPLATES).format(
            situation=situation,
            emotion=emotion,
            genre=genre,
            bpm=bpm,
            duration=duration,
        )
        context = {
            "song_concept": concept,
            "situation": situation,
            "emotion": emotion,
            "genre": genre,
            "vocal": vocal,
            "language": language,
            "bpm": str(bpm),
            "duration": duration,
            "sound_tags": random.sample(tags, k=min(len(tags), random.randint(5, 8))),
            "sound_texture": random.sample(TEXTURES, k=random.randint(0, 3)),
            "extra": "GitHub Actions daily random generation",
        }

    if context["vocal"] == "없음":
        context["language"] = "가사 없음"

    return context


def generate_package(context):
    if not OPENAI_API_KEY:
        raise RuntimeError("OPENAI_API_KEY is missing.")

    client = OpenAI(api_key=OPENAI_API_KEY)
    instrumental = context["vocal"] == "없음" or context["language"] == "가사 없음"

    response = client.chat.completions.create(
        model=OPENAI_MODEL,
        messages=[
            {
                "role": "system",
                "content": """
You are a practical Suno AI music production assistant.
Return valid JSON only.
The style_prompt must be in English.
Lyrics must be in the selected language.
If instrumental mode is true, do not write lyrics. Return short instrumental guidance in lyrics.
Avoid copyrighted artist imitation.
Make every value copy-ready.
""",
            },
            {
                "role": "user",
                "content": f"""
Create a full daily Suno package.

Input:
{json.dumps(context, ensure_ascii=False, indent=2)}

Instrumental mode: {instrumental}

Return this JSON shape:
{{
  "style_prompt": "English Suno style prompt",
  "lyrics": "Lyrics or instrumental guidance",
  "song_title": "Recommended song title",
  "youtube_title": "YouTube title",
  "youtube_description": "YouTube description",
  "youtube_tags": ["tag1", "tag2", "tag3"],
  "thumbnail_text": "Short thumbnail copy"
}}
""",
            },
        ],
        response_format={"type": "json_object"},
        temperature=0.9,
    )

    return json.loads(response.choices[0].message.content)


def write_markdown(context, result):
    now = datetime.now(TIMEZONE)
    output_dir = Path("outputs")
    output_dir.mkdir(exist_ok=True)
    path = output_dir / f"{now:%Y-%m-%d}.md"

    tags = result.get("youtube_tags", [])
    tag_text = " ".join(f"#{str(tag).lstrip('#')}" for tag in tags)

    markdown = f"""# Daily Suno Package - {now:%Y-%m-%d}

## Random Input

```json
{json.dumps(context, ensure_ascii=False, indent=2)}
```

## Suno Style Prompt

{result.get("style_prompt", "")}

## Suno Lyrics

{result.get("lyrics", "")}

## 추천 곡 제목

{result.get("song_title", "")}

## 유튜브 제목

{result.get("youtube_title", "")}

## 유튜브 설명

{result.get("youtube_description", "")}

## 유튜브 태그

{tag_text}

## 썸네일 문구

{result.get("thumbnail_text", "")}
"""

    path.write_text(markdown, encoding="utf-8")
    print(f"Wrote {path}")


def main():
    context = random_context()
    result = generate_package(context)
    write_markdown(context, result)


if __name__ == "__main__":
    main()
