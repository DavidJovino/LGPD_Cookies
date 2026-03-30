import time
import requests
from urllib.parse import urlparse
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from utils.cookie_categorizer import categorize_cookie


# ─────────────────────────────────────────────────────────────────────────────
# Palavras-chave para detectar botão de aceitar no banner
# ─────────────────────────────────────────────────────────────────────────────
_ACCEPT_PATTERNS = [
    "aceitar todos", "aceitar", "accept all", "accept", "allow all",
    "allow", "permitir", "concordo", "agree", "ok",
]


def check_cookies_storage(driver) -> dict:
    """
    Verifica os cookies armazenados pelo site com três estratégias:

    1. Cookies via Selenium antes do consentimento (cookies de sessão/essenciais)
    2. Aceita o banner de consentimento e aguarda cookies de analytics/marketing
       serem definidos pelos scripts de terceiros
    3. Cookies via requisição HTTP (requests), que captura cookies enviados
       pelo servidor no cabeçalho Set-Cookie
    """
    cookies_info = {
        "total_cookies": 0,
        "cookies": [],
        "categories": {
            "essential": [],
            "analytics": [],
            "marketing": [],
            "preferences": [],
            "unknown": [],
        },
        "issues": [],
    }

    try:
        current_url = driver.current_url

        # ── ESTRATÉGIA 1: Cookies antes do consentimento ──────────────────────
        pre_consent_cookies = {c["name"]: c for c in driver.get_cookies()}

        # ── ESTRATÉGIA 2: Aceitar banner e aguardar novos cookies ─────────────
        _try_accept_banner(driver)
        time.sleep(3)  # aguarda scripts de terceiros definirem cookies

        post_consent_cookies = {c["name"]: c for c in driver.get_cookies()}

        # Une os dois conjuntos (pós-consentimento prevalece)
        all_selenium_cookies = {**pre_consent_cookies, **post_consent_cookies}

        # ── ESTRATÉGIA 3: Cookies via requisição HTTP (Set-Cookie header) ─────
        http_cookies = _get_http_cookies(current_url)

        # Mescla: Selenium + HTTP (sem duplicar por nome)
        merged = dict(all_selenium_cookies)
        for name, http_c in http_cookies.items():
            if name not in merged:
                merged[name] = http_c

        # ── Processa e categoriza ─────────────────────────────────────────────
        for name, cookie in merged.items():
            category = categorize_cookie(name)
            cookie_info = {
                "name": name,
                "domain": cookie.get("domain", ""),
                "path": cookie.get("path", "/"),
                "secure": cookie.get("secure", False),
                "httpOnly": cookie.get("httpOnly", False),
                "sameSite": cookie.get("sameSite", ""),
                "category": category,
                "source": cookie.get("_source", "selenium"),
            }
            cookies_info["cookies"].append(cookie_info)
            if category in cookies_info["categories"]:
                cookies_info["categories"][category].append(name)

        cookies_info["total_cookies"] = len(cookies_info["cookies"])

        # ── Problemas ─────────────────────────────────────────────────────────
        if cookies_info["total_cookies"] == 0:
            cookies_info["issues"].append(
                "Nenhum cookie encontrado (pode indicar que o site não usa cookies)"
            )

        unknown_count = len(cookies_info["categories"]["unknown"])
        if unknown_count > 0:
            cookies_info["issues"].append(
                f"{unknown_count} cookie(s) não categorizado(s) encontrado(s)"
            )

    except Exception as e:
        cookies_info["issues"].append(f"Erro ao verificar cookies: {str(e)}")

    return cookies_info


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

def _try_accept_banner(driver) -> bool:
    """
    Tenta clicar no botão de aceitar cookies para que os scripts de terceiros
    (Google Analytics, Facebook Pixel, etc.) sejam carregados e definam cookies.
    Retorna True se conseguiu clicar, False caso contrário.
    """
    try:
        # Tenta via JavaScript: busca botão com texto de aceitar
        clicked = driver.execute_script("""
            const patterns = arguments[0];
            const btns = [...document.querySelectorAll('button, a[role="button"], input[type="button"], input[type="submit"]')];
            for (const btn of btns) {
                const text = (btn.innerText || btn.value || '').toLowerCase().trim();
                if (patterns.some(p => text.includes(p))) {
                    btn.click();
                    return true;
                }
            }
            return false;
        """, _ACCEPT_PATTERNS)
        if clicked:
            return True
    except Exception:
        pass

    # Fallback: XPath com texto
    try:
        for pattern in _ACCEPT_PATTERNS:
            xpath = (
                f"//button[contains(translate(normalize-space(.), "
                f"'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '{pattern}')] | "
                f"//a[@role='button' and contains(translate(normalize-space(.), "
                f"'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '{pattern}')]"
            )
            elements = driver.find_elements(By.XPATH, xpath)
            if elements:
                elements[0].click()
                return True
    except Exception:
        pass

    return False


def _get_http_cookies(url: str) -> dict:
    """
    Faz uma requisição HTTP ao site e retorna os cookies definidos pelo
    servidor no cabeçalho Set-Cookie. Útil para capturar cookies HttpOnly
    que não são acessíveis via JavaScript/Selenium.
    """
    result = {}
    try:
        parsed = urlparse(url)
        base_url = f"{parsed.scheme}://{parsed.netloc}"

        session = requests.Session()
        session.headers.update({
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            )
        })
        resp = session.get(base_url, timeout=15, allow_redirects=True)

        for name, value in resp.cookies.items():
            cookie_obj = resp.cookies.get_dict()
            result[name] = {
                "name": name,
                "value": value,
                "domain": parsed.netloc,
                "path": "/",
                "secure": parsed.scheme == "https",
                "httpOnly": False,
                "_source": "http",
            }
    except Exception:
        pass

    return result
