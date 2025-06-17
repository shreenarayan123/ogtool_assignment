from typing import List, Optional
from urllib.parse import urljoin
from playwright.async_api import async_playwright
import requests
from bs4 import BeautifulSoup
import json
import time
import re
from urllib.parse import urljoin, urlparse, parse_qs
from dataclasses import dataclass, asdict
from typing import List, Dict, Optional, Any
import PyPDF2
import io
from pathlib import Path
import logging
from abc import ABC, abstractmethod

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@dataclass
class KnowledgeItem:
    """Standardized knowledge base item"""

    title: str
    content: str
    content_type: str
    team_id: str
    source_url: Optional[str] = None
    author: Optional[str] = ""
    user_id: Optional[str] = ""


@dataclass
class KnowledgeBase:
    """Complete knowledge base structure"""

    team_id: str
    items: List[KnowledgeItem]

    def to_dict(self) -> Dict[str, Any]:
        return {"team_id": self.team_id, "items": [asdict(item) for item in self.items]}


class BaseScraper(ABC):
    """Abstract base class for all scrapers"""

    def __init__(self, team_id: str, delay: float = 1.0):
        self.team_id = team_id
        self.delay = delay
        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            }
        )

    @abstractmethod
    def scrape(self, source: str) -> List[KnowledgeItem]:
        """Scrape content from source and return knowledge items"""
        pass

    def _fetch_page(self, url: str) -> Optional[BeautifulSoup]:
        """Safely fetch and parse a web page"""
        try:
            time.sleep(self.delay)  # Rate limiting
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            return BeautifulSoup(response.content, "html.parser")
        except Exception as e:
            logger.error(f"Failed to fetch {url}: {e}")
            return None

    def _clean_text(self, text: str) -> str:
        """Clean and normalize text content"""

        text = re.sub(r"\s+", " ", text.strip())

        text = re.sub(r"[\u200b-\u200d\ufeff]", "", text)
        return text

    def _extract_author(self, soup: BeautifulSoup) -> str:
        """Extract author from common HTML patterns"""
        author_selectors = [
            'meta[name="author"]',
            ".author",
            ".by-author",
            ".post-author",
            '[rel="author"]',
            ".byline",
        ]

        for selector in author_selectors:
            element = soup.select_one(selector)
            if element:
                if element.name == "meta":
                    return element.get("content", "").strip()
                else:
                    return self._clean_text(element.get_text())
        return ""


class InterviewingIOScraper(BaseScraper):
    """Scraper for interviewing.io content"""

    def scrape(self, source: str) -> List[KnowledgeItem]:
        items = []

        if "/blog" in source:
            items.extend(self._scrape_blog())
        elif "/topics#companies" in source:
            items.extend(self._scrape_company_guides())
        elif "/learn#interview-guides" in source:
            items.extend(self._scrape_interview_guides())

        return items

    def _scrape_blog(self) -> List[KnowledgeItem]:
        """Scrape all blog posts from interviewing.io/blog"""
        items = []
        base_url = "https://interviewing.io/blog"

        soup = self._fetch_page(base_url)
        if not soup:
            return items

        post_links = []
        for link in soup.find_all("a", href=True):
            href = link["href"]
            if "/blog/" in href and href != "/blog":
                full_url = urljoin(base_url, href)
                if full_url not in post_links:
                    post_links.append(full_url)

        logger.info(f"Found {len(post_links)} blog posts to scrape")

        for url in post_links:
            item = self._scrape_single_blog_post(url)
            if item:
                items.append(item)

        return items

    def _scrape_single_blog_post(self, url: str) -> Optional[KnowledgeItem]:
        """Scrape a single blog post"""
        soup = self._fetch_page(url)
        if not soup:
            return None

        # Extract title
        title_elem = soup.find("h1") or soup.find("title")
        title = self._clean_text(title_elem.get_text()) if title_elem else "Untitled"

        # Extract content
        content_selectors = [
            "article",
            ".post-content",
            ".content",
            ".entry-content",
            "main",
            ".blog-post",
        ]

        content = ""
        for selector in content_selectors:
            content_elem = soup.select_one(selector)
            if content_elem:
                content = self._html_to_markdown(content_elem)
                break

        if not content:
            content = self._clean_text(soup.get_text())

        author = self._extract_author(soup)

        return KnowledgeItem(
            title=title,
            content=content,
            content_type="blog",
            source_url=url,
            author=author,
            team_id=self.team_id,
        )

    def _scrape_company_guides(self) -> List[KnowledgeItem]:
        """Scrape company interview guides"""
        items = []
        base_url = "https://interviewing.io/topics"

        soup = self._fetch_page(base_url)
        if not soup:
            return items

        # Find company guide links
        guide_links = []
        for link in soup.find_all("a", href=True):
            href = link["href"]
            if "/companies/" in href:
                full_url = urljoin(base_url, href)
                guide_links.append(full_url)

        logger.info(f"Found {len(guide_links)} company guides to scrape")

        for url in guide_links:
            item = self._scrape_guide_page(url, "Company Guide")
            if item:
                items.append(item)

        return items

    def _scrape_interview_guides(self) -> List[KnowledgeItem]:
        """Scrape interview guides"""
        items = []
        base_url = "https://interviewing.io/learn"

        soup = self._fetch_page(base_url)
        if not soup:
            return items

        # Find interview guide links
        guide_links = []
        for link in soup.find_all("a", href=True):
            href = link["href"]
            if "/guides/" in href or "/learn/" in href:
                full_url = urljoin(base_url, href)
                guide_links.append(full_url)

        logger.info(f"Found {len(guide_links)} interview guides to scrape")

        for url in guide_links:
            item = self._scrape_guide_page(url, "Interview Guide")
            if item:
                items.append(item)

        return items

    def _scrape_guide_page(self, url: str, guide_type: str) -> Optional[KnowledgeItem]:
        """Scrape a single guide page"""
        soup = self._fetch_page(url)
        if not soup:
            return None

        # Extract title
        title_elem = soup.find("h1") or soup.find("title")
        title = (
            self._clean_text(title_elem.get_text())
            if title_elem
            else f"Untitled {guide_type}"
        )

        # Extract content
        content_elem = (
            soup.find("main") or soup.find("article") or soup.find(".content")
        )
        if content_elem:
            content = self._html_to_markdown(content_elem)
        else:
            content = self._clean_text(soup.get_text())

        return KnowledgeItem(
            title=title,
            content=content,
            content_type="other",
            source_url=url,
            author="interviewing.io",
            team_id=self.team_id,
        )

    def _html_to_markdown(self, element) -> str:
        """Convert HTML element to markdown"""
        # Simple HTML to markdown conversion
        text = ""
        for child in element.descendants:
            if child.name == "h1":
                text += f"\n# {child.get_text().strip()}\n\n"
            elif child.name == "h2":
                text += f"\n## {child.get_text().strip()}\n\n"
            elif child.name == "h3":
                text += f"\n### {child.get_text().strip()}\n\n"
            elif child.name == "p":
                text += f"{child.get_text().strip()}\n\n"
            elif child.name == "li":
                text += f"- {child.get_text().strip()}\n"
            elif child.name == "code":
                text += f"`{child.get_text().strip()}`"
            elif child.name == "pre":
                text += f"\n```\n{child.get_text().strip()}\n```\n\n"

        return self._clean_text(text)


class NilMamanoScraper(BaseScraper):
    """Scraper for Nil Mamano's DSA blog posts"""

    def scrape(self, source: str) -> List[KnowledgeItem]:
        items = []
        base_url = "https://nilmamano.com/blog/category/dsa"

        soup = self._fetch_page(base_url)
        if not soup:
            return items

        # Find blog post links
        post_links = []
        for link in soup.find_all("a", href=True):
            href = link["href"]
            if "/blog/" in href and href != "/blog/":
                full_url = urljoin(base_url, href)
                post_links.append(full_url)

        logger.info(f"Found {len(post_links)} DSA blog posts to scrape")

        for url in post_links:
            item = self._scrape_single_post(url)
            if item:
                items.append(item)

        return items

    def _scrape_single_post(self, url: str) -> Optional[KnowledgeItem]:
        """Scrape a single blog post"""
        soup = self._fetch_page(url)
        if not soup:
            return None

        # Extract title
        title_elem = soup.find("h1") or soup.find("title")
        title = self._clean_text(title_elem.get_text()) if title_elem else "Untitled"

        # Extract content
        content_elem = soup.find("article") or soup.find(".post-content")
        if content_elem:
            content = self._html_to_markdown(content_elem)
        else:
            content = self._clean_text(soup.get_text())

        return KnowledgeItem(
            title=title,
            content=content,
            content_type="blog",
            source_url=url,
            author="Nil Mamano",
            team_id=self.team_id,
        )

    def _html_to_markdown(self, element) -> str:
        """Convert HTML to markdown with code block support"""
        # Enhanced markdown conversion for technical content
        text = ""
        for child in element.find_all(True):
            if child.name in ["h1", "h2", "h3", "h4", "h5", "h6"]:
                level = int(child.name[1])
                text += f"\n{'#' * level} {child.get_text().strip()}\n\n"
            elif child.name == "p":
                text += f"{child.get_text().strip()}\n\n"
            elif child.name == "pre":
                code_text = child.get_text().strip()
                text += f"\n```\n{code_text}\n```\n\n"
            elif child.name == "code" and child.parent.name != "pre":
                text += f"`{child.get_text().strip()}`"
            elif child.name in ["ul", "ol"]:
                for li in child.find_all("li"):
                    text += f"- {li.get_text().strip()}\n"
                text += "\n"

        return self._clean_text(text)


class QuillBlogScraper(BaseScraper):
    def scrape(self, source: str) -> List[KnowledgeItem]:
        items = []
        base_url = "https://quill.co/blog"

        post_links = self._extract_links_simple(base_url)

        for url in post_links:
            item = self._scrape_single_post_simple(url)
            if item:
                items.append(item)

        return items

    def _extract_links_simple(self, url: str) -> List[str]:
        """Use requests to extract blog links."""
        post_links = []
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, "html.parser")

            for anchor in soup.find_all("a", href=True):
                href = anchor["href"]
                if "/blog/" in href and href != "/blog/":
                    full_url = urljoin("https://quill.co", href)
                    post_links.append(full_url)

        except Exception as e:
            logger.error(f"Failed to extract links from {url}: {e}")

        return list(set(post_links))

    def _scrape_single_post_simple(self, url: str) -> Optional[KnowledgeItem]:
        """Use requests to fetch a single blog post."""
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, "html.parser")

            title_elem = soup.find("h1") or soup.find("title")
            title = title_elem.get_text(strip=True) if title_elem else "Untitled"

            content_elem = soup.select_one("article") or soup.find("main")
            content = (
                self._clean_text(content_elem.get_text())
                if content_elem
                else self._clean_text(soup.get_text())
            )

            return KnowledgeItem(
                title=title,
                content=content.strip(),
                content_type="blog",
                source_url=url,
                author="Quill Team",
                team_id=self.team_id,
            )

        except Exception as e:
            logger.error(f"Failed to scrape post {url}: {e}")
            return None


class PDFScraper(BaseScraper):
    """Scraper for PDF documents"""

    def scrape(self, source: str) -> List[KnowledgeItem]:
        """Scrape PDF content - source can be file path or URL"""
        try:
            if source.startswith("http"):
                response = self.session.get(source)
                pdf_file = io.BytesIO(response.content)
            else:
                pdf_file = open(source, "rb")

            reader = PyPDF2.PdfReader(pdf_file)

            chapters = []
            current_chapter = 1
            chapter_content = ""
            chapter_title = f"Chapter {current_chapter}"

            for page_num, page in enumerate(reader.pages):
                if current_chapter > 8:
                    break

                text = page.extract_text()
                if "Chapter" in text and current_chapter < 8:
                    if chapter_content:  # Save previous chapter
                        chapters.append(
                            KnowledgeItem(
                                title=chapter_title,
                                content=self._clean_text(chapter_content),
                                content_type="book",
                                source_url=(
                                    source if source.startswith("http") else None
                                ),
                                author="Aline",
                                team_id=self.team_id,
                            )
                        )

                    current_chapter += 1
                    chapter_title = f"Chapter {current_chapter}"
                    chapter_content = text
                else:
                    chapter_content += text

            # Add the last chapter
            if chapter_content and current_chapter <= 8:
                chapters.append(
                    KnowledgeItem(
                        title=chapter_title,
                        content=self._clean_text(chapter_content),
                        content_type="book",
                        source_url=source if source.startswith("http") else None,
                        author="Aline",
                        team_id=self.team_id,
                    )
                )

            if not source.startswith("http"):
                pdf_file.close()

            logger.info(f"Extracted {len(chapters)} chapters from PDF")
            return chapters

        except Exception as e:
            logger.error(f"Failed to process PDF {source}: {e}")
            return []


class SubstackScraper(BaseScraper):
    """Bonus: Substack scraper"""

    def scrape(self, source: str) -> List[KnowledgeItem]:
        items = []

        # Extract substack domain
        parsed_url = urlparse(source)
        base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"

        archive_urls = [f"{base_url}/archive", f"{base_url}/posts", source]

        post_links = []
        for archive_url in archive_urls:
            soup = self._fetch_page(archive_url)
            if soup:
                # Find post links
                for link in soup.find_all("a", href=True):
                    href = link["href"]
                    if "/p/" in href:  # Substack post pattern
                        full_url = urljoin(base_url, href)
                        if full_url not in post_links:
                            post_links.append(full_url)

        logger.info(f"Found {len(post_links)} Substack posts to scrape")

        for url in post_links:
            item = self._scrape_substack_post(url)
            if item:
                items.append(item)

        return items

    def _scrape_substack_post(self, url: str) -> Optional[KnowledgeItem]:
        """Scrape a single Substack post"""
        soup = self._fetch_page(url)
        if not soup:
            return None

        # Extract title
        title_elem = soup.find("h1") or soup.select_one(".post-title")
        title = self._clean_text(title_elem.get_text()) if title_elem else "Untitled"

        # Extract content
        content_elem = soup.select_one(".available-content") or soup.select_one(
            ".post-content"
        )
        if content_elem:
            content = self._html_to_markdown(content_elem)
        else:
            content = self._clean_text(soup.get_text())

        # Extract author
        author_elem = soup.select_one(".byline-name") or soup.select_one(".author")
        author = self._clean_text(author_elem.get_text()) if author_elem else ""

        return KnowledgeItem(
            title=title,
            content=content,
            content_type="blog",
            source_url=url,
            author=author,
            team_id=self.team_id,
        )

    def _html_to_markdown(self, element) -> str:
        """Convert HTML to markdown"""
        text = ""
        for child in element.find_all(
            ["p", "h1", "h2", "h3", "h4", "h5", "h6", "li", "pre", "code"]
        ):
            if child.name in ["h1", "h2", "h3", "h4", "h5", "h6"]:
                level = int(child.name[1])
                text += f"\n{'#' * level} {child.get_text().strip()}\n\n"
            elif child.name == "p":
                text += f"{child.get_text().strip()}\n\n"
            elif child.name == "li":
                text += f"- {child.get_text().strip()}\n"
            elif child.name == "pre":
                text += f"\n```\n{child.get_text().strip()}\n```\n\n"
            elif child.name == "code":
                text += f"`{child.get_text().strip()}`"

        return self._clean_text(text)


class TechnicalKnowledgeScraper:
    """Main scraper orchestrator"""

    def __init__(self, team_id: str = "aline123"):
        self.team_id = team_id
        self.scrapers = {
            "interviewing.io": InterviewingIOScraper(team_id),
            "nilmamano.com": NilMamanoScraper(team_id),
            "pdf": PDFScraper(team_id),
            "substack": SubstackScraper(team_id),
            "quill.co": QuillBlogScraper(team_id),
        }

    def scrape_all_sources(self, sources: List[str]) -> KnowledgeBase:
        """Scrape all specified sources"""
        all_items = []

        for source in sources:
            logger.info(f"Processing source: {source}")

            try:
                if "interviewing.io" in source:
                    items = self.scrapers["interviewing.io"].scrape(source)
                elif "nilmamano.com" in source:
                    items = self.scrapers["nilmamano.com"].scrape(source)
                elif "quill.co" in source:
                    items = self.scrapers["quill.co"].scrape(source)
                elif source.endswith(".pdf"):
                    items = self.scrapers["pdf"].scrape(source)
                elif "substack" in source:
                    items = self.scrapers["substack"].scrape(source)
                else:
                    items = self._generic_scrape(source)

                all_items.extend(items)
                logger.info(f"Extracted {len(items)} items from {source}")

            except Exception as e:
                logger.error(f"Failed to process {source}: {e}")
                continue

        return KnowledgeBase(team_id=self.team_id, items=all_items)

    def _generic_scrape(self, url: str) -> List[KnowledgeItem]:
        """Generic scraper for unknown sites (like quill.co/blog)"""
        scraper = BaseScraper(self.team_id)
        soup = scraper._fetch_page(url)
        if not soup:
            return []

        title_elem = soup.find("h1") or soup.find("title")
        title = (
            scraper._clean_text(title_elem.get_text())
            if title_elem
            else "Unknown Content"
        )
