import time
import requests
from selenium.webdriver.common.by import By


# Seletores e padrões para encontrar o link da política
_POLICY_SELECTORS = [
    "a[href*='privacy']",
    "a[href*='privacidade']",
    "a[href*='politica']",
    "a[href*='policy']",
    "a[href*='cookies']",
    "a[href*='lgpd']",
    "a[href*='termos']",
    "a[href*='terms']",
    "[class*='privacy']",
    "[class*='privacidade']",
]

_POLICY_TEXT_PATTERNS = [
    "política de privacidade", "política de cookies",
    "privacy policy", "cookie policy",
    "politica de privacidade", "aviso de privacidade",
]

# Palavras-chave para análise do conteúdo da política
_COOKIE_KEYWORDS = ["cookie", "cookies"]
_LEGAL_BASIS_KEYWORDS = [
    "base legal", "legal basis", "fundamento legal",
    "legítimo interesse", "legitimate interest",
    "consentimento", "consent", "obrigação legal",
]
_CATEGORY_KEYWORDS = [
    "categoria", "category", "essencial", "essential",
    "analítico", "analytic", "marketing", "preferência", "preference",
    "funcional", "functional",
]


def check_privacy_policy(driver) -> dict:
    """
    Verifica a presença e qualidade da política de privacidade/cookies.

    Estratégias:
    1. Busca link de política na página atual via seletores CSS
    2. Busca link via texto visível (fallback)
    3. Analisa o conteúdo da política via requests (sem navegar, preservando
       o estado do driver para as demais verificações)
    """
    policy_info = {
        "found": False,
        "url": None,
        "has_cookie_section": False,
        "has_legal_bases": False,
        "has_categories": False,
        "issues": [],
    }

    try:
        policy_url = _find_policy_url(driver)

        if not policy_url:
            policy_info["issues"].append("Política de privacidade não encontrada")
            return policy_info

        policy_info["found"] = True
        policy_info["url"] = policy_url

        # Analisa o conteúdo via requests (não navega no driver)
        page_text = _fetch_page_text(policy_url)

        if page_text:
            text_lower = page_text.lower()

            policy_info["has_cookie_section"] = any(
                kw in text_lower for kw in _COOKIE_KEYWORDS
            )
            policy_info["has_legal_bases"] = any(
                kw in text_lower for kw in _LEGAL_BASIS_KEYWORDS
            )
            policy_info["has_categories"] = any(
                kw in text_lower for kw in _CATEGORY_KEYWORDS
            )

        # Problemas
        if not policy_info["has_cookie_section"]:
            policy_info["issues"].append(
                "Política de privacidade não menciona cookies"
            )
        if not policy_info["has_legal_bases"]:
            policy_info["issues"].append(
                "Bases legais para coleta de dados não especificadas"
            )
        if not policy_info["has_categories"]:
            policy_info["issues"].append(
                "Categorias de cookies não descritas na política"
            )

    except Exception as e:
        policy_info["issues"].append(f"Erro ao verificar política: {str(e)}")

    return policy_info


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

def _find_policy_url(driver) -> str | None:
    """
    Procura o URL da política de privacidade na página atual.
    Retorna o href do primeiro link encontrado, ou None.
    """
    # Estratégia 1: seletores CSS
    for selector in _POLICY_SELECTORS:
        try:
            elements = driver.find_elements(By.CSS_SELECTOR, selector)
            for el in elements:
                href = el.get_attribute("href") or ""
                if href and href.startswith("http"):
                    return href
        except Exception:
            continue

    # Estratégia 2: busca por texto do link via JavaScript
    try:
        url = driver.execute_script("""
            const patterns = arguments[0];
            const links = document.querySelectorAll('a[href]');
            for (const link of links) {
                const text = (link.innerText || '').toLowerCase().trim();
                const href = link.href || '';
                if (!href.startsWith('http')) continue;
                if (patterns.some(p => text.includes(p))) {
                    return href;
                }
            }
            return null;
        """, _POLICY_TEXT_PATTERNS)
        if url:
            return url
    except Exception:
        pass

    # Estratégia 3: busca no footer (onde políticas costumam estar)
    try:
        url = driver.execute_script("""
            const footerSelectors = ['footer', '[class*="footer"]', '[id*="footer"]'];
            for (const sel of footerSelectors) {
                const footer = document.querySelector(sel);
                if (!footer) continue;
                const links = footer.querySelectorAll('a[href]');
                for (const link of links) {
                    const href = link.href || '';
                    const text = (link.innerText || '').toLowerCase();
                    if (!href.startsWith('http')) continue;
                    if (href.includes('privac') || href.includes('policy') ||
                        href.includes('cookie') || href.includes('lgpd') ||
                        text.includes('privac') || text.includes('policy')) {
                        return href;
                    }
                }
            }
            return null;
        """)
        if url:
            return url
    except Exception:
        pass

    return None


def _fetch_page_text(url: str) -> str:
    """
    Baixa o conteúdo HTML da URL via requests e retorna o texto puro.
    """
    try:
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            )
        }
        resp = requests.get(url, headers=headers, timeout=15, allow_redirects=True)
        resp.raise_for_status()

        # Remove tags HTML para obter texto puro
        from html.parser import HTMLParser

        class _TextExtractor(HTMLParser):
            def __init__(self):
                super().__init__()
                self._parts = []
                self._skip = False

            def handle_starttag(self, tag, attrs):
                if tag in ("script", "style", "noscript"):
                    self._skip = True

            def handle_endtag(self, tag):
                if tag in ("script", "style", "noscript"):
                    self._skip = False

            def handle_data(self, data):
                if not self._skip:
                    self._parts.append(data)

            def get_text(self):
                return " ".join(self._parts)

        parser = _TextExtractor()
        parser.feed(resp.text)
        return parser.get_text()

    except Exception:
        return ""
