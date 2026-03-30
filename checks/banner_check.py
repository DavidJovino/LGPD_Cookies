import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from utils.dom_finder import (
    find_element_by_text,
    find_element_by_aria_label,
    find_element_by_class,
    find_banner_by_text_content,
)

# ─────────────────────────────────────────────────────────────────────────────
# Padrões de texto para botões
# ─────────────────────────────────────────────────────────────────────────────
_REJECT_PATTERNS = [
    "rejeitar", "recusar", "deny", "reject", "negar", "descartar",
    "deny cookies", "reject all", "recusar tudo", "refuse all",
    "não aceitar", "decline", "refuse", "disallow",
    "apenas essenciais", "somente essenciais", "only essential",
    "essential only", "necessários apenas",
]

_ACCEPT_PATTERNS = [
    "aceitar todos", "aceitar", "accept all", "accept", "allow all",
    "allow", "permitir", "concordo", "agree", "ok",
    "aceitar cookies", "allow cookies",
]

_POLICY_PATTERNS = [
    "política", "policy", "privacidade", "privacy", "cookies",
    "saiba mais", "learn more", "leia mais", "read more",
    "termos", "terms",
]

# Seletores CSS semânticos (Estratégia 1)
_CSS_SELECTORS = [
    ".cc-window", ".cc-banner", ".cc-compliance", ".cc-message",
    "[class*='cookie']", "[id*='cookie']",
    "[class*='consent']", "[id*='consent']",
    "[class*='cc-']", "[class*='compliance']",
    "[role='dialog']", "[role='alert']",
    ".cookiebot", ".cookie-banner", ".cookie-consent",
    "[data-component*='cookie']", "[id*='gdpr']", "[class*='gdpr']",
    "[id*='lgpd']", "[class*='lgpd']",
    "[id*='privacy']", "[class*='privacy-banner']",
]


def check_first_level_banner(driver) -> dict:
    """
    Verifica o banner de primeiro nível com múltiplas estratégias:
      1. Seletores CSS semânticos (cookieconsent, cc-, consent, cookie…)
      2. z-index alto + posição fixed (banners Tailwind/custom sem classe semântica)
      3. Busca por texto no DOM (título/corpo do banner)
    """
    banner_info = {
        "found": False,
        "has_accept_button": False,
        "has_reject_button": False,
        "has_cookie_policy_link": False,
        "text_content": "",
        "issues": [],
    }

    try:
        # Aguarda carregamento inicial da página
        try:
            WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "body"))
            )
        except Exception:
            pass
        time.sleep(4)

        banner_element = None

        # ── ESTRATÉGIA 1: Seletores CSS semânticos ────────────────────────────
        for selector in _CSS_SELECTORS:
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    banner_element = elements[0]
                    break
            except Exception:
                continue

        # ── ESTRATÉGIA 2: Elemento fixed/sticky com z-index alto ──────────────
        # CORREÇÃO: usa XPath gerado pelo JS em vez de retornar o elemento
        if banner_element is None:
            banner_element = _find_banner_by_position(driver)

        # ── ESTRATÉGIA 3: Busca por texto no DOM ──────────────────────────────
        if banner_element is None:
            banner_element = find_banner_by_text_content(driver)

        # ── Análise do banner encontrado ──────────────────────────────────────
        if banner_element:
            banner_info["found"] = True

            # Tenta subir para o container raiz do banner
            try:
                banner_root = banner_element.find_element(
                    By.XPATH,
                    "ancestor-or-self::*["
                    "contains(@class,'cc-window') or "
                    "contains(@class,'cc-banner') or "
                    "contains(@class,'cc-compliance') or "
                    "contains(@class,'cookie') or "
                    "@role='dialog'"
                    "][1]",
                )
            except Exception:
                banner_root = banner_element

            try:
                banner_info["text_content"] = (banner_root.text or "")[:500]
            except Exception:
                pass

            # Botão de rejeição
            banner_info["has_reject_button"] = _has_button(
                driver, banner_root, _REJECT_PATTERNS
            )

            # Botão de aceitação
            banner_info["has_accept_button"] = _has_button(
                driver, banner_root, _ACCEPT_PATTERNS
            )

            # Link para política de cookies
            banner_info["has_cookie_policy_link"] = _has_policy_link(
                driver, banner_root
            )

        # ── Problemas ─────────────────────────────────────────────────────────
        if not banner_info["found"]:
            banner_info["issues"].append("Banner de cookies não encontrado no site")
        if not banner_info["has_reject_button"]:
            banner_info["issues"].append("Botão de rejeição de cookies não encontrado")
        if not banner_info["has_accept_button"]:
            banner_info["issues"].append("Botão de aceitação de cookies não encontrado")
        if not banner_info["has_cookie_policy_link"]:
            banner_info["issues"].append("Link para política de cookies não encontrado")

    except Exception as e:
        banner_info["issues"].append(f"Erro ao verificar banner: {str(e)}")

    return banner_info


# ─────────────────────────────────────────────────────────────────────────────
# Helpers internos
# ─────────────────────────────────────────────────────────────────────────────

def _find_banner_by_position(driver):
    """
    Detecta banners que usam CSS utilitário (Tailwind) sem classe semântica,
    buscando elementos com position:fixed/sticky e z-index >= 100 que contenham
    texto relacionado a cookies/privacidade.

    CORREÇÃO: em vez de retornar o elemento WebDriver via execute_script
    (que falha quando o elemento não tem id), usa o índice do elemento no
    array querySelectorAll para localizá-lo depois via XPath/CSS.
    """
    keywords = [
        'cookie', 'privacidade', 'privacy', 'consent', 'consentimento',
        'lgpd', 'gdpr', 'valorizamos', 'essenciais', 'aceitar',
        'rejeitar', 'personalizar',
    ]
    try:
        # Retorna informações do elemento (não o elemento em si)
        info = driver.execute_script("""
            const keywords = arguments[0];
            const all = document.querySelectorAll('*');
            for (let i = 0; i < all.length; i++) {
                const el = all[i];
                const style = window.getComputedStyle(el);
                const pos = style.position;
                const z = parseInt(style.zIndex) || 0;
                if ((pos === 'fixed' || pos === 'sticky') && z >= 100) {
                    const text = (el.innerText || '').toLowerCase();
                    if (keywords.some(k => text.includes(k)) && text.length > 20) {
                        // Retorna seletor único para o elemento
                        const id = el.id ? '#' + el.id : null;
                        const cls = el.className && typeof el.className === 'string'
                            ? el.className.trim().split(/\\s+/).slice(0, 3).join('.')
                            : null;
                        return {
                            tag: el.tagName.toLowerCase(),
                            id: id,
                            cls: cls,
                            text_preview: text.substring(0, 80)
                        };
                    }
                }
            }
            return null;
        """, keywords)

        if not info:
            return None

        # Localiza o elemento via Selenium usando as informações retornadas
        tag = info.get("tag", "*")
        el_id = info.get("id")
        cls = info.get("cls", "")

        # Tenta por ID primeiro
        if el_id:
            els = driver.find_elements(By.CSS_SELECTOR, el_id)
            if els:
                return els[0]

        # Tenta por tag + primeiras classes
        if cls:
            selector = f"{tag}.{cls}".replace(" ", ".")
            try:
                els = driver.find_elements(By.CSS_SELECTOR, selector)
                if els:
                    return els[0]
            except Exception:
                pass

        # Fallback: XPath por texto parcial
        text_preview = info.get("text_preview", "")
        if text_preview:
            first_word = text_preview.strip().split()[0] if text_preview.strip() else ""
            if first_word:
                xpath = (
                    f"//{tag}[contains(translate(normalize-space(.), "
                    f"'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), "
                    f"'{first_word}')]"
                )
                els = driver.find_elements(By.XPATH, xpath)
                if els:
                    return els[0]

    except Exception:
        pass

    return None


def _has_button(driver, container, patterns: list) -> bool:
    """
    Verifica se existe um botão com texto correspondente aos padrões,
    buscando tanto no container quanto no documento inteiro como fallback.
    """
    # Busca no container
    if find_element_by_text(container, patterns, tag_names=["button", "a", "input", "div", "span"]):
        return True
    if find_element_by_aria_label(container, patterns):
        return True

    # Fallback: busca no documento inteiro via JavaScript
    try:
        found = driver.execute_script("""
            const patterns = arguments[0];
            const btns = document.querySelectorAll(
                'button, a[role="button"], input[type="button"], input[type="submit"]'
            );
            for (const btn of btns) {
                const text = (btn.innerText || btn.value || '').toLowerCase().trim();
                const aria = (btn.getAttribute('aria-label') || '').toLowerCase();
                if (patterns.some(p => text.includes(p) || aria.includes(p))) {
                    return true;
                }
            }
            return false;
        """, patterns)
        if found:
            return True
    except Exception:
        pass

    return False


def _has_policy_link(driver, container) -> bool:
    """
    Verifica se existe link para política de cookies/privacidade.
    """
    # Busca no container
    if find_element_by_text(container, _POLICY_PATTERNS, tag_names=["a"]):
        return True
    if find_element_by_aria_label(container, _POLICY_PATTERNS):
        return True

    # Fallback: busca no documento inteiro
    try:
        found = driver.execute_script("""
            const patterns = arguments[0];
            const links = document.querySelectorAll('a[href]');
            for (const link of links) {
                const text = (link.innerText || '').toLowerCase().trim();
                const href = (link.href || '').toLowerCase();
                const aria = (link.getAttribute('aria-label') || '').toLowerCase();
                if (patterns.some(p =>
                    text.includes(p) || href.includes(p) || aria.includes(p)
                )) {
                    return true;
                }
            }
            return false;
        """, _POLICY_PATTERNS)
        if found:
            return True
    except Exception:
        pass

    return False
