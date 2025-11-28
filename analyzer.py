import requests
import time
import re
import json
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

import requests
import time
import re
import json
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse


class WebsiteAnalyzer:
    def __init__(self, yandex_gpt_api_key=None):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        self.yandex_gpt_api_key = 'AQVN2E_gKuTJc_B1jb1gPQK4jAQiEbl5RZtSkmGU'

    def _get_yandex_gpt_fix(self, problem_description, current_code, url):
        """Получение исправления от YandexGPT"""
        if not self.yandex_gpt_api_key:
            return {
                "fixed_code": current_code,
                "explanation": "YandexGPT API ключ не настроен. Для использования AI-исправлений укажите API ключ.",
                "changes": ["Требуется настройка API ключа"],
                "error": "API_KEY_MISSING"
            }

        prompt = f"""КОНТЕКСТ:
        - Анализируемый URL: {url}
        - Выявленная проблема: {problem_description}
        - Текущий проблемный код: {current_code}

        ТРЕБОВАНИЯ К ИСПРАВЛЕНИЮ:
        1. Код должен быть валидным HTML/JSON-LD
        2. Соответствовать стандартам W3C
        3. Учитывать лучшие практики SEO
        4. Быть оптимальным для LLM и поисковых систем

        ФОРМАТ ОТВЕТА - ТОЛЬКО JSON:
        
            "fixed_code": "полный исправленный код",
            "explanation": "краткое объяснение на русском что было исправлено и почему",
            "changes": ["конкретное изменение 1", "конкретное изменение 2", "конкретное изменение 3"]

        ВАЖНО: Верни только JSON объект, без дополнительного текста.
        """

        try:
            # Реальная реализация для YandexGPT API
            headers = {
                'Authorization': f'Api-Key {self.yandex_gpt_api_key}',
                'Content-Type': 'application/json'
            }

            payload = {
                "modelUri": f"gpt://b1g80nc4mkh3lm4s25h7/yandexgpt/latest",
                "completionOptions": {"stream": False, "temperature": 0.1, "maxTokens": "2000"},
                "messages": [
                    {"role": "system", "text": 'Ты - эксперт по SEO оптимизации и веб-разработке. Проанализируй проблему и предложи конкретное исправление.'},
                    {"role": "user", "text": prompt}
                ]
            }

            response = requests.post(
                "https://llm.api.cloud.yandex.net/foundationModels/v1/completion",
            headers = headers,
            json = payload,
            timeout = 30
            )
            response.raise_for_status()
            raw_text = response.json()['result']['alternatives'][0]['message']['text'].replace('```', '')
            return json.loads(raw_text)


        except Exception as e:
            return {
                "fixed_code": current_code,
                "explanation": f"Ошибка при обращении к YandexGPT API: {str(e)}",
                "changes": ["Не удалось получить исправление от AI"],
                "error": "API_CALL_ERROR"
            }

    def analyze_website(self, url):
        """Основной метод анализа сайта"""
        try:
            start_time = time.time()
            response = self.session.get(url, timeout=15)
            response.raise_for_status()
            load_time = time.time() - start_time

            soup = BeautifulSoup(response.content, 'html.parser')

            results = {
                "url": url,
                "load_time": f"{load_time:.2f} сек",
                "semantic_clarity": self._analyze_semantic_clarity(soup),
                "headers": self._analyze_headers(soup),
                "structure": self._analyze_structure(soup),
                "questions": self._analyze_questions(soup),
                "special_content": self._analyze_special_content(soup, url),
                "structured_data": self._analyze_structured_data(soup),
                "author_signals": self._analyze_author_signals(soup),
                "content_sync": self._analyze_content_sync(soup),
                "dates": self._analyze_dates(soup),
                "social_meta": self._analyze_social_meta(soup),
                "canonical": self._analyze_canonical(soup, url),
                "llm_accessibility": self._analyze_llm_accessibility(soup),
                "citation_license": self._analyze_citation_license(soup),
                "eeat": self._analyze_eeat(soup, url, response),
                "validation": self._validate_meta_tags(soup, url)
            }

            results["recommendations"] = self._generate_recommendations(results)

            return results

        except Exception as e:
            print(f"Ошибка анализа сайта: {e}")
            return {"error": str(e)}

    def _analyze_semantic_clarity(self, soup):
        """Анализ семантической ясности"""
        title_tag = soup.find('title')
        meta_description = soup.find('meta', attrs={'name': 'description'})
        h1_tag = soup.find('h1')

        title_text = title_tag.get_text().strip() if title_tag else ""
        description_content = meta_description.get('content', '') if meta_description else ""
        h1_text = h1_tag.get_text().strip() if h1_tag else ""

        title_length = len(title_text)
        desc_length = len(description_content)

        return {
            "title": title_text,
            "title_length": title_length,
            "title_optimal": 50 <= title_length <= 60,
            "description": description_content,
            "description_length": desc_length,
            "description_optimal": 150 <= desc_length <= 160,
            "h1": h1_text,
            "title_h1_match": title_text.lower() == h1_text.lower() if h1_text else False
        }

    def _analyze_headers(self, soup):
        """Анализ заголовков"""
        h1_tags = soup.find_all('h1')
        h2_tags = soup.find_all('h2')
        h3_tags = soup.find_all('h3')

        return {
            "h1_count": len(h1_tags),
            "h1_optimal": len(h1_tags) == 1,
            "h2_count": len(h2_tags),
            "h3_count": len(h3_tags),
            "h1_examples": [h1.get_text().strip() for h1 in h1_tags[:2]],
            "h2_examples": [h2.get_text().strip() for h2 in h2_tags[:2]]
        }

    def _analyze_structure(self, soup):
        """Анализ структурных элементов"""
        ul_lists = soup.find_all('ul')
        ol_lists = soup.find_all('ol')
        tables = soup.find_all('table')
        blockquotes = soup.find_all('blockquote')

        highlighted_blocks = soup.find_all(['div', 'section'],
                                           class_=lambda x: x and any(word in x.lower() for word in
                                                                      ['highlight', 'block', 'quote', 'special',
                                                                       'feature']))

        schemes = soup.find_all('img', alt=lambda x: x and any(word in x.lower() for word in
                                                               ['schema', 'diagram', 'chart', 'scheme']))

        return {
            "lists": len(ul_lists) + len(ol_lists),
            "tables": len(tables),
            "blockquotes": len(blockquotes) + len(highlighted_blocks),
            "schemes": len(schemes),
            "has_structured_content": len(ul_lists) > 0 or len(ol_lists) > 0 or len(tables) > 0
        }

    def _analyze_questions(self, soup):
        """Анализ вопросительных предложений"""
        for script in soup(["script", "style"]):
            script.decompose()

        text = soup.get_text()
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        clean_text = ' '.join(chunk for chunk in chunks if chunk)

        sentences = re.split(r'[.!]', clean_text)
        question_sentences = [s.strip() for s in sentences if '?' in s]

        return {
            "count": len(question_sentences),
            "examples": question_sentences[:3]
        }

    def _analyze_special_content(self, soup, url):
        """Анализ контента особого формата"""
        faq_blocks = len(soup.find_all(class_=lambda x: x and any(word in x.lower() for word in
                                                                  ['faq', 'question', 'accordion'])))
        articles = len(soup.find_all('article'))
        blog_posts = len(soup.find_all(class_=lambda x: x and any(word in x.lower() for word in
                                                                  ['post', 'blog', 'article'])))
        product_cards = len(soup.find_all(class_=lambda x: x and any(word in x.lower() for word in
                                                                     ['product', 'card', 'item', 'goods'])))
        reviews = len(soup.find_all(class_=lambda x: x and any(word in x.lower() for word in
                                                               ['review', 'testimonial', 'feedback'])))
        instructions = len(soup.find_all(class_=lambda x: x and any(word in x.lower() for word in
                                                                    ['instruction', 'manual', 'guide', 'tutorial'])))

        return {
            "faq": faq_blocks,
            "articles": articles + blog_posts,
            "products": product_cards,
            "reviews": reviews,
            "instructions": instructions,
            "has_special_content": faq_blocks > 0 or articles > 0 or product_cards > 0 or reviews > 0
        }

    def _analyze_structured_data(self, soup):
        """Анализ структурированных данных"""
        json_ld_scripts = soup.find_all('script', type='application/ld+json')
        json_ld_types = []

        for script in json_ld_scripts:
            try:
                data = json.loads(script.string)
                if isinstance(data, dict):
                    schema_type = data.get('@type', 'Unknown')
                    json_ld_types.append(schema_type)
            except:
                pass

        og_tags = soup.find_all('meta', attrs={'property': re.compile(r'^og:', re.I)})

        return {
            "json_ld": len(json_ld_scripts),
            "json_ld_types": list(set(json_ld_types)),
            "og_tags": len(og_tags),
            "has_structured_data": len(json_ld_scripts) > 0
        }

    def _analyze_author_signals(self, soup):
        """Анализ авторства"""
        author_meta = soup.find('meta', attrs={'name': 'author'})
        author_elements = len(soup.find_all(class_=lambda x: x and any(word in x.lower() for word in
                                                                       ['author', 'writer', 'byline'])))

        qualification_signals = len(soup.find_all(string=re.compile(
            r'эксперт|специалист|опыт|квалификация|образование', re.I)))

        return {
            "author_meta": author_meta.get('content') if author_meta else None,
            "author_elements": author_elements,
            "qualification_signals": qualification_signals,
            "has_author_signals": author_meta is not None or author_elements > 0
        }

    def _analyze_content_sync(self, soup):
        """Анализ синхронизации контента"""
        title = soup.find('title')
        h1 = soup.find('h1')
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        og_title = soup.find('meta', attrs={'property': 'og:title'})

        title_text = title.get_text().strip() if title else ""
        h1_text = h1.get_text().strip() if h1 else ""
        og_title_text = og_title.get('content') if og_title else ""

        sync_issues = []
        if title and h1 and title_text.lower() != h1_text.lower():
            sync_issues.append("Title и H1 не совпадают")
        if og_title and title and og_title_text != title_text:
            sync_issues.append("og:title и Title не совпадают")

        return {
            "title": title_text,
            "h1": h1_text,
            "meta_description": meta_desc.get('content') if meta_desc else "",
            "og_title": og_title_text,
            "sync_issues": sync_issues,
            "has_all_elements": bool(title and h1 and meta_desc)
        }

    def _analyze_dates(self, soup):
        """Анализ дат"""
        date_published = soup.find('meta', attrs={'property': 'article:published_time'})
        date_modified = soup.find('meta', attrs={'property': 'article:modified_time'})

        json_ld_dates = []
        json_ld_scripts = soup.find_all('script', type='application/ld+json')

        for script in json_ld_scripts:
            try:
                data = json.loads(script.string)
                if isinstance(data, dict):
                    if 'datePublished' in data:
                        json_ld_dates.append(f"published: {data['datePublished']}")
                    if 'dateModified' in data:
                        json_ld_dates.append(f"modified: {data['dateModified']}")
            except:
                pass

        return {
            "date_published": date_published.get('content') if date_published else None,
            "date_modified": date_modified.get('content') if date_modified else None,
            "json_ld_dates": json_ld_dates,
            "has_dates": date_published is not None or date_modified is not None or len(json_ld_dates) > 0
        }

    def _analyze_social_meta(self, soup):
        """Анализ социальных метатегов"""
        og_image = soup.find('meta', attrs={'property': 'og:image'})
        twitter_card = soup.find('meta', attrs={'name': 'twitter:card'})
        og_title = soup.find('meta', attrs={'property': 'og:title'})
        og_description = soup.find('meta', attrs={'property': 'og:description'})

        return {
            "og_image": og_image.get('content') if og_image else None,
            "twitter_card": twitter_card.get('content') if twitter_card else None,
            "og_title": og_title.get('content') if og_title else None,
            "og_description": og_description.get('content') if og_description else None,
            "has_social_meta": og_image is not None or twitter_card is not None
        }

    def _analyze_canonical(self, soup, url):
        """Анализ canonical"""
        canonical = soup.find('link', attrs={'rel': 'canonical'})
        canonical_url = canonical.get('href') if canonical else ""

        is_self_canonical = canonical_url == url or canonical_url == ""

        return {
            "canonical": canonical_url,
            "is_self_canonical": is_self_canonical,
            "has_canonical": canonical is not None
        }

    def _analyze_llm_accessibility(self, soup):
        """Анализ доступности для LLM"""
        robots = soup.find('meta', attrs={'name': 'robots'})
        robots_content = robots.get('content') if robots else ""

        has_max_snippet = 'max-snippet:-1' in robots_content
        has_index_follow = 'index' in robots_content and 'follow' in robots_content

        return {
            "robots_meta": robots_content,
            "max_snippet": has_max_snippet,
            "index_follow": has_index_follow,
            "llm_friendly": 'noindex' not in robots_content.lower() and has_max_snippet
        }

    def _analyze_citation_license(self, soup):
        """Анализ цитируемости"""
        license_signals = len(soup.find_all(string=re.compile(
            r'лицензия|license|авторское|copyright|все права защищены|CC-BY', re.I)))

        return {
            "license_signals": license_signals,
            "has_license": license_signals > 0
        }

    def _analyze_eeat(self, soup, url, response):
        """Анализ EEAT"""
        contact_info = len(soup.find_all(['a', 'div', 'span'],
                                         string=re.compile(r'контакт|contact|телефон|phone|адрес|address', re.I)))
        about_info = len(soup.find_all(['a', 'div'],
                                       string=re.compile(r'о нас|about|компания|company', re.I)))
        privacy_info = len(soup.find_all(['a', 'div'],
                                         string=re.compile(r'политика|privacy|confidential', re.I)))
        has_https = url.startswith('https')

        authoritative_links = len(soup.find_all('a', href=re.compile(
            r'wikipedia\.org|gov\.|edu\.|research', re.I)))

        eeat_score = sum([
            contact_info > 0,
            about_info > 0,
            privacy_info > 0,
            has_https,
            authoritative_links > 0
        ])

        return {
            "https": has_https,
            "contact_info": contact_info > 0,
            "about_page": about_info > 0,
            "privacy_policy": privacy_info > 0,
            "authoritative_links": authoritative_links,
            "eeat_score": eeat_score
        }

    def _validate_meta_tags(self, soup, url):
        """Валидация метатегов"""
        issues = []

        if not soup.find('title'):
            issues.append("Отсутствует тег <title>")
        elif len(soup.find('title').get_text().strip()) < 10:
            issues.append("Title слишком короткий (менее 10 символов)")

        if not soup.find('meta', attrs={'name': 'description'}):
            issues.append("Отсутствует meta description")

        if not soup.find_all('script', type='application/ld+json'):
            issues.append("Отсутствует JSON-LD разметка")

        if not soup.find('meta', attrs={'property': 'og:title'}):
            issues.append("Отсутствует og:title")

        return {
            "issues": issues,
            "issue_count": len(issues)
        }

    def _generate_recommendations(self, results):
        """Генерация рекомендаций с исправлениями от YandexGPT"""
        recommendations = []

        semantic = results["semantic_clarity"]
        headers = results["headers"]
        structured = results["structured_data"]
        author = results["author_signals"]
        dates = results["dates"]
        social = results["social_meta"]
        canonical = results["canonical"]
        eeat = results["eeat"]
        validation = results["validation"]
        llm = results["llm_accessibility"]
        structure = results["structure"]
        special_content = results["special_content"]
        content_sync = results["content_sync"]

        # Анализ Title
        if not semantic["title_optimal"]:
            if semantic["title_length"] < 50:
                gpt_fix = self._get_yandex_gpt_fix(
                    f"Title слишком короткий: {semantic['title_length']} символов вместо рекомендуемых 50-60. Текущий title: '{semantic['title']}'",
                    f"<title>{semantic['title']}</title>",
                    results["url"]
                )
                print(gpt_fix)
                recommendations.append({
                    "type": "warning",
                    "title": "Title слишком короткий",
                    "message": f"Длина Title: {semantic['title_length']} символов (рекомендуется 50-60)",
                    "current_code": f"<title>{semantic['title']}</title>",
                    "fixed_code": gpt_fix["fixed_code"],
                    "explanation": gpt_fix["explanation"],
                    "changes": gpt_fix.get("changes", [])
                    
                })

            elif semantic["title_length"] > 60:
                gpt_fix = self._get_yandex_gpt_fix(
                    f"Title слишком длинный: {semantic['title_length']} символов вместо рекомендуемых 50-60. Текущий title: '{semantic['title']}'",
                    f"<title>{semantic['title']}</title>",
                    results["url"]
                )

                recommendations.append({
                    "type": "warning",
                    "title": "Title слишком длинный",
                    "message": f"Длина Title: {semantic['title_length']} символов (рекомендуется 50-60)",
                    "current_code": f"<title>{semantic['title']}</title>",
                    "fixed_code": gpt_fix["fixed_code"],
                    "explanation": gpt_fix["explanation"],
                    "changes": gpt_fix.get("changes", [])
                    
                })

        # Анализ Description
        if not semantic["description_optimal"]:
            if semantic["description_length"] < 150:
                gpt_fix = self._get_yandex_gpt_fix(
                    f"Meta Description слишком короткий: {semantic['description_length']} символов вместо 150-160. Текущий description: '{semantic['description']}'",
                    f'<meta name="description" content="{semantic["description"]}">',
                    results["url"]
                )
                recommendations.append({
                    "type": "warning",
                    "title": "Meta Description слишком короткий",
                    "message": f"Длина Description: {semantic['description_length']} символов (рекомендуется 150-160)",
                    "current_code": f'<meta name="description" content="{semantic["description"]}">',
                    "fixed_code": gpt_fix["fixed_code"],
                    "explanation": gpt_fix["explanation"],
                    "changes": gpt_fix.get("changes", [])
                    
                })

            elif semantic["description_length"] > 160:
                gpt_fix = self._get_yandex_gpt_fix(
                    f"Meta Description слишком длинный: {semantic['description_length']} символов вместо 150-160. Текущий description: '{semantic['description']}'",
                    f'<meta name="description" content="{semantic["description"]}">',
                    results["url"]
                )
                recommendations.append({
                    "type": "warning",
                    "title": "Meta Description слишком длинный",
                    "message": f"Длина Description: {semantic['description_length']} символов (рекомендуется 150-160)",
                    "current_code": f'<meta name="description" content="{semantic["description"]}">',
                    "fixed_code": gpt_fix["fixed_code"],
                    "explanation": gpt_fix["explanation"],
                    "changes": gpt_fix.get("changes", [])
                    
                })

        # Анализ H1
        if not headers["h1_optimal"]:
            if headers["h1_count"] == 0:
                gpt_fix = self._get_yandex_gpt_fix(
                    "На странице отсутствует H1 заголовок. H1 необходим для SEO и структуры контента.",
                    "<!-- H1 заголовок отсутствует -->",
                    results["url"]
                )
                recommendations.append({
                    "type": "critical",
                    "title": "Отсутствует H1 заголовок",
                    "message": "На странице не найден тег H1",
                    "current_code": "<!-- H1 заголовок отсутствует -->",
                    "fixed_code": gpt_fix["fixed_code"],
                    "explanation": gpt_fix["explanation"],
                    "changes": gpt_fix.get("changes", [])
                    
                })

            elif headers["h1_count"] > 1:
                h1_examples = "\n".join([f"<h1>{h1}</h1>" for h1 in headers["h1_examples"]])
                gpt_fix = self._get_yandex_gpt_fix(
                    f"На странице найдено {headers['h1_count']} H1 заголовков, нужно оставить только один. Примеры текущих H1: {headers['h1_examples']}",
                    h1_examples,
                    results["url"]
                )
                recommendations.append({
                    "type": "warning",
                    "title": "Слишком много H1 заголовков",
                    "message": f"Найдено {headers['h1_count']} H1 тегов (рекомендуется 1)",
                    "current_code": h1_examples,
                    "fixed_code": gpt_fix["fixed_code"],
                    "explanation": gpt_fix["explanation"],
                    "changes": gpt_fix.get("changes", [])
                    
                })
        # Синхронизация Title и H1
        if not semantic["title_h1_match"] and semantic["title"] and semantic["h1"]:
            gpt_fix = self._get_yandex_gpt_fix(
                f"Title и H1 не синхронизированы. Title: '{semantic['title']}', H1: '{semantic['h1']}'. Они должны быть согласованы для лучшего SEO.",
                f"<title>{semantic['title']}</title>\n<h1>{semantic['h1']}</h1>",
                results["url"]
            )
            recommendations.append({
                "type": "warning",
                "title": "Title и H1 не синхронизированы",
                "message": "Заголовок в Title и H1 должны быть согласованы",
                "current_code": f"<title>{semantic['title']}</title>\n<h1>{semantic['h1']}</h1>",
                "fixed_code": gpt_fix["fixed_code"],
                "explanation": gpt_fix["explanation"],
                "changes": gpt_fix.get("changes", [])
                
            })

        # Структурированные данные
        if not structured["has_structured_data"]:
            gpt_fix = self._get_yandex_gpt_fix(
                "Отсутствуют структурированные данные (JSON-LD) для поисковых систем и LLM. JSON-LD помогает поисковым системам лучше понимать контент.",
                "<!-- Структурированные данные отсутствуют -->",
                results["url"]
            )
            recommendations.append({
                "type": "info",
                "title": "Отсутствуют структурированные данные",
                "message": "Не найден JSON-LD или микроразметка Schema.org",
                "current_code": "<!-- Структурированные данные отсутствуют -->",
                "fixed_code": gpt_fix["fixed_code"],
                "explanation": gpt_fix["explanation"],
                "changes": gpt_fix.get("changes", [])
                
            })

        # Авторство
        if not author["has_author_signals"]:
            gpt_fix = self._get_yandex_gpt_fix(
                "Отсутствуют сигналы авторства и экспертизы (EEAT). Необходимо добавить информацию об авторе для повышения доверия.",
                "<!-- Информация об авторе отсутствует -->",
                results["url"]
            )
            recommendations.append({
                "type": "warning",
                "title": "Не указана информация об авторе",
                "message": "Отсутствуют сигналы авторства и экспертизы",
                "current_code": "<!-- Информация об авторе отсутствует -->",
                "fixed_code": gpt_fix["fixed_code"],
                "explanation": gpt_fix["explanation"],
                "changes": gpt_fix.get("changes", [])
                
            })

        # Даты
        if not dates["has_dates"]:
            gpt_fix = self._get_yandex_gpt_fix(
                "Отсутствуют метатеги с датами публикации и обновления. Даты важны для определения актуальности контента.",
                "<!-- Даты публикации и обновления не указаны -->",
                results["url"]
            )
            recommendations.append({
                "type": "info",
                "title": "Не указаны даты публикации",
                "message": "Отсутствуют метатеги с датами публикации и обновления",
                "current_code": "<!-- Даты не указаны -->",
                "fixed_code": gpt_fix["fixed_code"],
                "explanation": gpt_fix["explanation"],
                "changes": gpt_fix.get("changes", [])
                
            })

        # Социальные метатеги
        if not social["has_social_meta"]:
            gpt_fix = self._get_yandex_gpt_fix(
                "Отсутствуют Open Graph теги для социальных сетей. OG теги улучшают отображение при расшаривании в соцсетях.",
                "<!-- Open Graph теги отсутствуют -->",
                results["url"]
            )
            recommendations.append({
                "type": "info",
                "title": "Отсутствуют Open Graph теги",
                "message": "Не найдены метатеги для социальных сетей",
                "current_code": "<!-- Open Graph теги отсутствуют -->",
                "fixed_code": gpt_fix["fixed_code"],
                "explanation": gpt_fix["explanation"],
                "changes": gpt_fix.get("changes", [])
                
            })

        # Canonical
        if not canonical["is_self_canonical"] and canonical["canonical"]:
            gpt_fix = self._get_yandex_gpt_fix(
                f"Canonical URL указывает на другой адрес: {canonical['canonical']} вместо {results['url']}. Canonical должен указывать на текущую страницу.",
                f'<link rel="canonical" href="{canonical["canonical"]}">',
                results["url"]
            )
            recommendations.append({
                "type": "warning",
                "title": "Некорректный canonical URL",
                "message": f"Canonical ссылка указывает на: {canonical['canonical']}",
                "current_code": f'<link rel="canonical" href="{canonical["canonical"]}">',
                "fixed_code": gpt_fix["fixed_code"],
                "explanation": gpt_fix["explanation"],
                "changes": gpt_fix.get("changes", [])
                
            })

        # LLM доступность
        if not llm["llm_friendly"]:
            if 'noindex' in llm["robots_meta"].lower():
                gpt_fix = self._get_yandex_gpt_fix(
                    f"Robots meta тег содержит 'noindex': {llm['robots_meta']}. Это запрещает индексацию страницы поисковыми системами и LLM.",
                    f'<meta name="robots" content="{llm["robots_meta"]}">',
                    results["url"]
                )
                recommendations.append({
                    "type": "critical",
                    "title": "Страница закрыта от индексации",
                    "message": "Robots meta тег содержит noindex",
                    "current_code": f'<meta name="robots" content="{llm["robots_meta"]}">',
                    "fixed_code": gpt_fix["fixed_code"],
                    "explanation": gpt_fix["explanation"],
                    "changes": gpt_fix.get("changes", [])
                    
                })
            elif not llm["max_snippet"]:
                gpt_fix = self._get_yandex_gpt_fix(
                    f"Отсутствует max-snippet:-1 в robots meta теге: {llm['robots_meta']}. max-snippet:-1 разрешает LLM использовать фрагменты контента.",
                    f'<meta name="robots" content="{llm["robots_meta"]}">',
                    results["url"]
                )
                recommendations.append({
                    "type": "info",
                    "title": "Не настроены разрешения для LLM",
                    "message": "Отсутствует max-snippet:-1 в robots meta",
                    "current_code": f'<meta name="robots" content="{llm["robots_meta"]}">',
                    "fixed_code": gpt_fix["fixed_code"],
                    "explanation": gpt_fix["explanation"],
                    "changes": gpt_fix.get("changes", [])
                    
                })

        # Критические ошибки из валидации
        for issue in validation["issues"]:
            if "Title слишком короткий" in issue and semantic["title"]:
                gpt_fix = self._get_yandex_gpt_fix(
                    f"Критическая ошибка: Title слишком короткий ({semantic['title_length']} символов). Минимальная рекомендуемая длина - 10 символов.",
                    f"<title>{semantic['title']}</title>",
                    results["url"]
                )
                recommendations.append({
                    "type": "critical",
                    "title": "Критическая ошибка: Title",
                    "message": issue,
                    "current_code": f"<title>{semantic['title']}</title>",
                    "fixed_code": gpt_fix["fixed_code"],
                    "explanation": gpt_fix["explanation"],
                    "changes": gpt_fix.get("changes", [])
                    
                })
            elif "Отсутствует тег <title>" in issue:
                gpt_fix = self._get_yandex_gpt_fix(
                    "Критическая ошибка: отсутствует тег <title>. Title обязателен для корректной индексации страницы.",
                    "<!-- Title отсутствует -->",
                    results["url"]
                )
                recommendations.append({
                    "type": "critical",
                    "title": "Критическая ошибка: отсутствует Title",
                    "message": issue,
                    "current_code": "<!-- Title отсутствует -->",
                    "fixed_code": gpt_fix["fixed_code"],
                    "explanation": gpt_fix["explanation"],
                    "changes": gpt_fix.get("changes", [])
                    
                })

        return recommendations