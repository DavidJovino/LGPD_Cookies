from typing import List
from selenium.webdriver.common.by import By


def find_element_by_text(container, text_patterns: List[str],
                         tag_names: List[str] = None,
                         require_displayed: bool = False) -> bool:
    """
    Procura por elemento contendo texto específico (case-insensitive).
    """
    if tag_names is None:
        tag_names = ['button', 'a', 'div', 'span']
    try:
        for tag in tag_names:
            for pattern in text_patterns:
                pat = (pattern or "").strip().lower()
                if not pat:
                    continue
                xpath = (
                    f".//{tag}[contains(translate(normalize-space(.), "
                    f"'ABCDEFGHIJKLMNOPQRSTUVWXYZÁÀÂÃÄÉÈÊËÍÌÎÏÓÒÔÕÖÚÙÛÜÇ', "
                    f"'abcdefghijklmnopqrstuvwxyzáàâãäéèêëíìîïóòôõöúùûüç'), '{pat}')]"
                )
                elements = container.find_elements(By.XPATH, xpath)
                if elements:
                    if not require_displayed:
                        return True
                    for elem in elements:
                        try:
                            if elem.is_displayed():
                                return True
                        except Exception:
                            pass
        return False
    except Exception:
        return False


def find_element_by_aria_label(container, aria_patterns: List[str],
                                require_displayed: bool = False) -> bool:
    """
    Procura por elemento com aria-label contendo padrões (case-insensitive).
    """
    try:
        for pattern in aria_patterns:
            pat = (pattern or "").strip().lower()
            if not pat:
                continue
            xpath = (
                ".//*[@aria-label and contains(translate(@aria-label, "
                "'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), "
                f"'{pat}')]"
            )
            elements = container.find_elements(By.XPATH, xpath)
            if elements:
                if not require_displayed:
                    return True
                for e in elements:
                    try:
                        if e.is_displayed():
                            return True
                    except Exception:
                        pass
        return False
    except Exception:
        return False


def find_element_by_class(container, class_patterns: List[str],
                           require_displayed: bool = False) -> bool:
    """
    Procura por elemento contendo fragmentos de classe CSS.
    """
    try:
        for pattern in class_patterns:
            pat = (pattern or "").strip()
            if not pat:
                continue
            xpath = f".//*[contains(@class, '{pat}')]"
            elements = container.find_elements(By.XPATH, xpath)
            if elements:
                if not require_displayed:
                    return True
                for e in elements:
                    try:
                        if e.is_displayed():
                            return True
                    except Exception:
                        pass
        return False
    except Exception:
        return False


def find_banner_by_text_content(driver):
    """
    Estratégia de fallback: percorre o DOM procurando por elementos que
    contenham texto típico de banners de cookies/privacidade.

    Útil para banners construídos com Tailwind CSS ou frameworks que não
    utilizam classes semânticas como 'cookie', 'consent', etc.
    """
    keywords = [
        'cookie', 'cookies', 'privacidade', 'privacy', 'consentimento',
        'consent', 'lgpd', 'gdpr', 'valorizamos', 'essenciais',
        'aceitar', 'rejeitar', 'personalizar', 'preferencias de cookies',
    ]

    # Tenta via JavaScript para maior eficiência
    try:
        result = driver.execute_script("""
            const keywords = arguments[0];
            const candidates = [];
            const tags = ['div', 'section', 'aside', 'article', 'footer',
                          'header', 'nav', 'form'];
            tags.forEach(tag => {
                document.querySelectorAll(tag).forEach(el => {
                    const text = (el.innerText || '').toLowerCase();
                    const matchCount = keywords.filter(k => text.includes(k)).length;
                    if (matchCount >= 2 && text.length > 30 && text.length < 2000) {
                        candidates.push({el: el, score: matchCount});
                    }
                });
            });
            if (!candidates.length) return null;
            candidates.sort((a, b) => b.score - a.score);
            return candidates[0].el;
        """, keywords)
        if result:
            return result
    except Exception:
        pass

    # Fallback Python puro
    try:
        for tag in ['div', 'section', 'aside', 'article']:
            for element in driver.find_elements(By.TAG_NAME, tag):
                try:
                    text = (element.text or "").lower()
                    matches = sum(1 for k in keywords if k in text)
                    if matches >= 2 and 30 < len(text) < 2000:
                        return element
                except Exception:
                    continue
    except Exception:
        pass

    return None
