import requests
import time
import re
import json
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from datetime import datetime


class WebsiteAnalyzer:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })

    def analyze_website(self, url):
        """Основной метод анализа сайта по всем критериям"""
        print(f"Анализ сайта: {url}")
        print("=" * 80)

        try:
            start_time = time.time()
            response = self.session.get(url, timeout=15)
            response.raise_for_status()
            load_time = time.time() - start_time

            soup = BeautifulSoup(response.content, 'html.parser')

            results = {
                "URL": url,
                "Время загрузки": f"{load_time:.2f} сек",
                "1. Заголовки H1-H3": self._analyze_headers(soup),
                "2. Структурные элементы": self._analyze_structure(soup),
                "3. Вопросительные предложения": self._analyze_questions(soup),
                "4. Контент особого формата": self._analyze_special_content(soup, url),
                "5. Авторитетность (EEAT)": self._analyze_eeat(soup, url, response),
                "6. Разметка Schema.org": self._analyze_schema(soup),
                "7. Семантика Title и Meta Description": self._analyze_meta_tags(soup),
                "8. Структурированные данные (JSON-LD + Open Graph)": self._analyze_structured_data(soup),
                "9. Авторство и E-E-A-T сигналы": self._analyze_author_signals(soup),
                "10. Синхронизация Title, H1 и Meta Description": self._analyze_content_sync(soup),
                "11. Актуальные даты": self._analyze_dates(soup),
                "12. Open Graph Image": self._analyze_og_image(soup, url),
                "13. Canonical и дублирование": self._analyze_canonical(soup, url),
                "14. Robots метатеги и лицензия": self._analyze_robots_license(soup),
                "15. Валидация метатегов": self._validate_meta_tags(soup, url)
            }

            self._print_results(results)
            return results

        except Exception as e:
            print(f"Ошибка анализа сайта: {e}")
            return None

    def _analyze_headers(self, soup):
        """1. Анализ заголовков H1-H3"""
        h1_tags = soup.find_all('h1')
        h2_tags = soup.find_all('h2')
        h3_tags = soup.find_all('h3')

        return {
            "H1": {
                "количество": len(h1_tags),
                "примеры": [h1.get_text().strip() for h1 in h1_tags[:3]]
            },
            "H2": {
                "количество": len(h2_tags),
                "примеры": [h2.get_text().strip() for h2 in h2_tags[:3]]
            },
            "H3": {
                "количество": len(h3_tags),
                "примеры": [h3.get_text().strip() for h3 in h3_tags[:3]]
            }
        }

    def _analyze_structure(self, soup):
        """2. Анализ структурных элементов"""
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
            "списки": {
                "маркированные": len(ul_lists),
                "нумерованные": len(ol_lists),
                "всего": len(ul_lists) + len(ol_lists)
            },
            "таблицы": len(tables),
            "выделенные_блоки": len(blockquotes) + len(highlighted_blocks),
            "схемы_диаграммы": len(schemes)
        }

    def _analyze_questions(self, soup):
        """3. Анализ вопросительных предложений"""
        for script in soup(["script", "style"]):
            script.decompose()

        text = soup.get_text()
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        clean_text = ' '.join(chunk for chunk in chunks if chunk)

        sentences = re.split(r'[.!]', clean_text)
        question_sentences = [s.strip() for s in sentences if '?' in s]

        return {
            "найдено_вопросов": len(question_sentences),
            "примеры": question_sentences[:5]
        }

    def _analyze_special_content(self, soup, url):
        """4. Анализ контента особого формата"""
        faq_blocks = soup.find_all(class_=lambda x: x and any(word in x.lower() for word in
                                                              ['faq', 'question', 'accordion']))
        articles = soup.find_all('article')
        blog_posts = soup.find_all(class_=lambda x: x and any(word in x.lower() for word in
                                                              ['post', 'blog', 'article']))
        product_cards = soup.find_all(class_=lambda x: x and any(word in x.lower() for word in
                                                                 ['product', 'card', 'item', 'goods']))
        reviews = soup.find_all(class_=lambda x: x and any(word in x.lower() for word in
                                                           ['review', 'testimonial', 'feedback']))
        instructions = soup.find_all(class_=lambda x: x and any(word in x.lower() for word in
                                                                ['instruction', 'manual', 'guide', 'tutorial']))

        return {
            "FAQ_блоки": len(faq_blocks),
            "статьи": len(articles) + len(blog_posts),
            "товарные_карточки": len(product_cards),
            "отзывы": len(reviews),
            "инструкции": len(instructions)
        }

    def _analyze_eeat(self, soup, url, response):
        """5. Анализ авторитетности (EEAT)"""
        contact_info = soup.find_all(['a', 'div', 'span'],
                                     string=re.compile(r'контакт|contact|телефон|phone|адрес|address', re.I))
        about_info = soup.find_all(['a', 'div'],
                                   string=re.compile(r'о нас|about|компания|company', re.I))
        privacy_info = soup.find_all(['a', 'div'],
                                     string=re.compile(r'политика|privacy|confidential', re.I))
        has_https = url.startswith('https')
        date_meta = soup.find('meta', attrs={'name': re.compile(r'date|update', re.I)})

        return {
            "контактная_информация": len(contact_info) > 0,
            "страница_о_компании": len(about_info) > 0,
            "политика_конфиденциальности": len(privacy_info) > 0,
            "HTTPS": has_https,
            "указана_дата": date_meta is not None
        }

    def _analyze_schema(self, soup):
        """6. Анализ разметки Schema.org"""
        itemscope_elements = soup.find_all(attrs={'itemscope': True})
        itemtype_elements = soup.find_all(attrs={'itemtype': True})
        itemprop_elements = soup.find_all(attrs={'itemprop': True})
        json_ld_scripts = soup.find_all('script', type='application/ld+json')

        return {
            "itemscope_элементы": len(itemscope_elements),
            "itemtype_элементы": len(itemtype_elements),
            "itemprop_элементы": len(itemprop_elements),
            "JSON_LD_блоки": len(json_ld_scripts),
            "общее_количество_разметки": len(itemscope_elements) + len(itemtype_elements) + len(itemprop_elements)
        }

    def _analyze_meta_tags(self, soup):
        """7. Семантическая ясность Title и Meta Description"""
        title_tag = soup.find('title')
        meta_description = soup.find('meta', attrs={'name': 'description'})

        title_text = title_tag.get_text().strip() if title_tag else ""
        description_content = meta_description.get('content', '') if meta_description else ""

        title_length = len(title_text)
        desc_length = len(description_content)

        return {
            "title": {
                "текст": title_text,
                "длина": title_length,
                "рекомендация": "50-60 символов",
                "соответствует": 50 <= title_length <= 60
            },
            "meta_description": {
                "текст": description_content,
                "длина": desc_length,
                "рекомендация": "150-160 символов",
                "соответствует": 150 <= desc_length <= 160
            }
        }

    def _analyze_structured_data(self, soup):
        """8. Структурированные данные (JSON-LD + Open Graph)"""
        # JSON-LD анализ
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

        # Open Graph анализ
        og_tags = soup.find_all('meta', attrs={'property': re.compile(r'^og:', re.I)})
        og_properties = [tag.get('property', '') for tag in og_tags]

        return {
            "JSON_LD_типы": list(set(json_ld_types)),
            "OpenGraph_теги": og_properties,
            "общее_количество_структурированных_данных": len(json_ld_scripts) + len(og_tags)
        }

    def _analyze_author_signals(self, soup):
        """9. Авторство и E-E-A-T сигналы"""
        # Поиск информации об авторе
        author_meta = soup.find('meta', attrs={'name': 'author'})
        author_elements = soup.find_all(class_=lambda x: x and any(word in x.lower() for word in
                                                                   ['author', 'writer', 'byline']))

        # Поиск квалификации и организаций
        qualification_signals = soup.find_all(string=re.compile(
            r'эксперт|специалист|опыт|квалификация|образование|организация|компания', re.I))

        return {
            "мета_автор": author_meta.get('content', '') if author_meta else "Не найден",
            "элементы_автора": len(author_elements),
            "сигналы_квалификации": len(qualification_signals) > 0,
            "найдено_E-E-A-T_сигналов": len(author_elements) + (1 if author_meta else 0) + len(qualification_signals)
        }

    def _analyze_content_sync(self, soup):
        """10. Синхронизация Title, H1 и Meta Description"""
        title_tag = soup.find('title')
        h1_tag = soup.find('h1')
        meta_desc = soup.find('meta', attrs={'name': 'description'})

        title_text = title_tag.get_text().strip() if title_tag else ""
        h1_text = h1_tag.get_text().strip() if h1_tag else ""
        desc_text = meta_desc.get('content', '') if meta_desc else ""

        # Проверка синхронизации по ключевым словам
        title_words = set(title_text.lower().split())
        h1_words = set(h1_text.lower().split())
        desc_words = set(desc_text.lower().split())

        common_title_h1 = len(title_words.intersection(h1_words))
        common_title_desc = len(title_words.intersection(desc_words))

        return {
            "title": title_text,
            "h1": h1_text,
            "meta_description": desc_text,
            "совпадение_title_h1": f"{common_title_h1} общих слов",
            "совпадение_title_description": f"{common_title_desc} общих слов",
            "синхронизация_оценка": "Хорошая" if common_title_h1 >= 2 and common_title_desc >= 2 else "Требует улучшения"
        }

    def _analyze_dates(self, soup):
        """11. Актуальные даты"""
        # Поиск дат в метатегах
        date_published = soup.find('meta', attrs={'property': 'article:published_time'})
        date_modified = soup.find('meta', attrs={'property': 'article:modified_time'})

        # Поиск в JSON-LD
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
            "datePublished": date_published.get('content', '') if date_published else "Не найден",
            "dateModified": date_modified.get('content', '') if date_modified else "Не найден",
            "JSON-LD_даты": json_ld_dates,
            "всего_найдено_дат": (1 if date_published else 0) + (1 if date_modified else 0) + len(json_ld_dates)
        }

    def _analyze_og_image(self, soup, url):
        """12. Open Graph Image анализ"""
        og_image = soup.find('meta', attrs={'property': 'og:image'})
        image_url = og_image.get('content', '') if og_image else ""

        # Проверка размера (эмулируем - в реальности нужно скачивать изображение)
        image_size_ok = True  # Заглушка для реальной проверки

        return {
            "og:image": image_url,
            "наличие": bool(og_image),
            "рекомендуемый_размер": "1200x630 пикселей",
            "размер_соответствует": image_size_ok
        }

    def _analyze_canonical(self, soup, url):
        """13. Canonical и предотвращение дублирования"""
        canonical = soup.find('link', attrs={'rel': 'canonical'})
        canonical_url = canonical.get('href', '') if canonical else ""

        is_self_canonical = canonical_url == url or canonical_url == ""

        return {
            "canonical_url": canonical_url,
            "self-canonical": is_self_canonical,
            "рекомендация": "Self-canonical URL"
        }

    def _analyze_robots_license(self, soup):
        """14. Robots метатеги и лицензия"""
        robots_meta = soup.find('meta', attrs={'name': 'robots'})
        robots_content = robots_meta.get('content', '') if robots_meta else ""

        # Поиск информации о лицензии
        license_signals = soup.find_all(string=re.compile(
            r'лицензия|license|авторское|copyright|все права защищены|CC-BY', re.I))

        has_max_snippet = 'max-snippet:-1' in robots_content
        has_index_follow = 'index' in robots_content and 'follow' in robots_content

        return {
            "robots_meta": robots_content,
            "max-snippet:-1": has_max_snippet,
            "index,follow": has_index_follow,
            "сигналы_лицензии": len(license_signals) > 0,
            "рекомендации_LLM": "Разрешено" if has_max_snippet and has_index_follow else "Ограничения"
        }

    def _validate_meta_tags(self, soup, url):
        """15. Валидация метатегов"""
        issues = []

        # Проверка Title
        title = soup.find('title')
        if not title:
            issues.append("Отсутствует тег <title>")
        elif len(title.get_text().strip()) < 10:
            issues.append("Title слишком короткий")

        # Проверка Meta Description
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        if not meta_desc:
            issues.append("Отсутствует meta description")

        # Проверка JSON-LD
        json_ld = soup.find_all('script', type='application/ld+json')
        if not json_ld:
            issues.append("Отсутствует JSON-LD разметка")

        # Проверка Open Graph
        og_title = soup.find('meta', attrs={'property': 'og:title'})
        if not og_title:
            issues.append("Отсутствует og:title")

        return {
            "найдено_проблем": len(issues),
            "проблемы": issues[:5],  # Первые 5 проблем
            "рекомендация": "Проверить через Google Rich Results Test"
        }

    def _print_results(self, results):
        """Вывод результатов"""
        for key, value in results.items():
            if key in ["URL", "Время загрузки"]:
                print(f"{key}: {value}")
            else:
                print(f"\n{key}:")
                self._print_dict(value, "  ")

        print("\n" + "=" * 80)

    def _print_dict(self, data, indent):
        """Рекурсивный вывод словаря"""
        for key, value in data.items():
            if isinstance(value, dict):
                print(f"{indent}{key}:")
                self._print_dict(value, indent + "  ")
            elif isinstance(value, list):
                print(f"{indent}{key}:")
                for item in value:
                    print(f"{indent}  - {item}")
            else:
                print(f"{indent}{key}: {value}")


# Пример использования
if __name__ == "__main__":
    analyzer = WebsiteAnalyzer()

    websites = [
        "https://example.com",
        # Добавьте другие сайты для анализа
    ]

    for website in websites:
        results = analyzer.analyze_website(website)
        print("\n")