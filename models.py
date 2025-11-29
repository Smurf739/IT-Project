import requests
import re
import json

YANDEX_API_KEY = "AQVN2E_gKuTJc_B1jb1gPQK4jAQiEbl5RZtSkmGU"
YANDEX_FOLDER_ID = "b1g80nc4mkh3lm4s25h7"

def fetch_geo_analysis(url: str):
    prompta = (
        "Ты — строгий аналитик GEO (Generative Engine Optimization). "
        "ТВОЯ ЗАДАЧА: проанализировать сайт и вернуть ТОЛЬКО ЧИСТЫЙ JSON без markdown. Все рекомендации писать НА РУССКОМ ЯЗЫКЕ! "
        "СЛЕДУЙ ПРАВИЛАМ:\n"
        "1. Оценка (поле 'score') — ТОЛЬКО целое число от 1 до 10.\n"
        "2. Поле 'value' — ТОЛЬКО одно из: 'Poor', 'Fair', 'Good', 'Very Good', 'Excellent'.\n"
        "3. Соответствие ОБЯЗАТЕЛЬНО:\n"
        "   - 'Poor' → score 1–3\n"
        "   - 'Fair' → score 4–5\n"
        "   - 'Good' → score 6–7\n"
        "   - 'Very Good' → score 8–9\n"
        "   - 'Excellent' → score 10\n"
        "4. НИКАКИХ отклонений. НИКАКИХ пояснений. ТОЛЬКО JSON.\n"
        "Формат ответа:\n"
        "{\n"
        "  \"metrics\": [\n"
        "    {\"name\": \"AI_Visibility_Score\", \"value\": \"Excellent\", \"score\": 10, \"explanation\": \"...\"},\n"
        "    {\"name\": \"Source_Citations\", \"value\": \"Excellent\", \"score\": 10, \"explanation\": \"...\"},\n"
        "    {\"name\": \"Brand_Mentions_in_LLMs\", \"value\": \"Good\", \"score\": 7, \"explanation\": \"...\"},\n"
        "    {\"name\": \"Zero_Click_Presence_Rate\", \"value\": \"Fair\", \"score\": 5, \"explanation\": \"...\"},\n"
        "    {\"name\": \"Content_Freshness_Index\", \"value\": \"Good\", \"score\": 6, \"explanation\": \"...\"},\n"
        "    {\"name\": \"Answer_Relevance_Score\", \"value\": \"Excellent\", \"score\": 10, \"explanation\": \"...\"}\n"
        "  ],\n"
        "  \"overall\": {\n"
        "    \"value\": \"Good\",\n"
        "    \"score\": 7,\n"
        "    \"recommendations\": \"...\"\n"
        "  }\n"
        "}"
    )

    payload = {
        "modelUri": f"gpt://{YANDEX_FOLDER_ID}/yandexgpt/latest",
        "completionOptions": {"stream": False, "temperature": 0.1, "maxTokens": "2000"},
        "messages": [
            {"role": "system", "text": prompta},
            {"role": "user", "text": url.strip()}
        ]
    }

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Api-Key {YANDEX_API_KEY}"
    }

    response = requests.post(
        "https://llm.api.cloud.yandex.net/foundationModels/v1/completion",
        headers=headers,
        json=payload,
        timeout=30
    )
    response.raise_for_status()
    raw_text = response.json()["result"]["alternatives"][0]["message"]["text"]

    cleaned = re.sub(r"^```(?:json)?\s*|\s*```$", "", raw_text.strip(), flags=re.DOTALL)


    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", cleaned, re.DOTALL)
        if match:
            return json.loads(match.group())
        else:
            return {"metrics": [], "overall": {}}