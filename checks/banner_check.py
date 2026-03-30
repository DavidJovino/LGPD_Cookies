from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from utils.dom_finder import (
    find_element_by_text,
    find_element_by_aria_label,
    find_element_by_class,
    find_banner_by_text_content,
)


def check_first_level_banner(driver) -> dict:
    """
    Verifica o banner de primeiro nível com múltiplas estratégias.

    Estratégias em ordem de prioridade:
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
        # Aguarda carregamento inicial
        try:
            WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((
                    By.CSS_SELECTOR,
                    ".cc-compliance, .cc-message, [class*='cookie'], "
                    "[id*='cookie'], [class*='consent'], [id*='consent']",
                ))
            )
        except Exception:
            time.sleep(4)

        # ESTRATÉGIA 1: Seletores CSS semânticos
        css_selectors = [
            ".cc-window", ".cc-banner", ".cc-compliance", ".cc-message",
            "[class*='cookie']", "[id*='cookie']",
            "[class*='consent']", "[id*='consent']",
            "[class*='cc-']", "[class*='compliance']",
            "[role='dialog']", "[role='alert']",
            ".cookiebot", ".cookie-banner", ".cookie-consent",
            "[data-component*='cookie']",
        ]

        banner_element = None
        for selector in css_selectors:
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    banner_element = elements[0]
                    break
            except Exception:
                continue

        # ESTRATÉGIA 2: Elemento fixed com z-index alto (Tailwind / custom)
        if banner_element is None:
            banner_element = _find_banner_by_position(driver)

        # ESTRATÉGIA 3: Busca por texto no DOM
        if banner_element is None:
            banner_element = find_banner_by_text_content(driver)

        # Análise do banner encontrado
        if banner_element:
            banner_info["found"] = True

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
            reject_patterns = [
                "rejeitar", "recusar", "deny", "reject", "negar", "descartar",
                "deny cookies", "reject all", "recusar tudo", "refuse all",
                "não aceitar", "decline", "refuse", "disallow",
                "apenas essenciais", "somente essenciais", "only essential",
            ]

            has_reject = (
                find_element_by_text(banner_root, reject_patterns,
                                     tag_names=["button", "a", "div", "span"],
                                     require_displayed=False)
                or find_element_by_aria_label(banner_root, reject_patterns,
                                              require_displayed=False)
                or find_element_by_class(banner_root,
                                         ["deny", "reject", "refuse",
                                          "decline", "recusar", "cc-deny"],
                                         require_displayed=False)
            )

            if not has_reject:
                for sel in [
                    ".cc-compliance .cc-btn.cc-deny", ".cc-deny",
                    "a[role='button'][aria-label*='deny']", "a.cc-btn.cc-deny",
                    "button[class*='essencial']", "button[class*='essential']",
                ]:
                    if driver.find_elements(By.CSS_SELECTOR, sel):
                        has_reject = True
                        break

            banner_info["has_reject_button"] = has_reject

            # Botão de aceitação
            accept_patterns = [
                "aceitar", "accept", "allow", "permitir", "concordo",
                "allow cookies", "accept all", "aceitar tudo", "permit all",
                "agree", "aceitar todos", "accept all cookies",
            ]

            has_accept = (
                find_element_by_text(banner_root, accept_patterns,
                                     tag_names=["button", "a", "div", "span"],
                                     require_displayed=False)
                or find_element_by_aria_label(banner_root, accept_patterns,
                                              require_displayed=False)
                or find_element_by_class(banner_root,
                                         ["allow", "accept", "agree",
                                          "aceitar", "cc-allow"],
                                         require_displayed=False)
            )

            if not has_accept:
                for sel in [
                    ".cc-compliance .cc-btn.cc-allow", ".cc-allow",
                    "a[role='button'][aria-label*='allow']", "a.cc-btn.cc-allow",
                ]:
                    if driver.find_elements(By.CSS_SELECTOR, sel):
                        has_accept = True
                        break

            banner_info["has_accept_button"] = has_accept

            # Link de política de cookies
            policy_patterns = [
                "política", "policy", "cookies", "privacidade", "privacy",
                "termos", "terms", "saiba mais", "learn more",
                "mais informações",
            ]

            has_policy = False
            try:
                for link in banner_root.find_elements(By.TAG_NAME, "a"):
                    link_text = (link.text or "").lower()
                    link_href = (link.get_attribute("href") or "").lower()
                    if any(p.lower() in link_text or p.lower() in link_href
                           for p in policy_patterns):
                        has_policy = True
                        break
            except Exception:
                pass

            if not has_policy:
                try:
                    for link in driver.find_elements(By.TAG_NAME, "a"):
                        link_text = (link.text or "").lower()
                        link_href = (link.get_attribute("href") or "").lower()
                        if any(p.lower() in link_text or p.lower() in link_href
                               for p in policy_patterns):
                            has_policy = True
                            break
                except Exception:
                    pass

            banner_info["has_cookie_policy_link"] = has_policy

            if not has_reject:
                banner_info["issues"].append(
                    "Botão de rejeição de cookies não encontrado"
                )
            if not has_accept:
                banner_info["issues"].append(
                    "Botão de aceitação de cookies não encontrado"
                )
            if not has_policy:
                banner_info["issues"].append(
                    "Link para política de cookies não encontrado"
                )
        else:
            banner_info["issues"].append(
                "Banner de cookies não encontrado no site"
            )

    except Exception as e:
        banner_info["issues"].append(f"Erro ao verificar banner: {str(e)}")

    return banner_info


def _find_banner_by_position(driver):
    """
    Encontra banners que usam CSS utilitário (Tailwind) sem classe semântica,
    detectando elementos com position:fixed/sticky e z-index alto que contenham
    texto relacionado a cookies/privacidade.
    """
    try:
        candidates = driver.execute_script("""
            const keywords = ['cookie', 'privacidade', 'privacy', 'consent',
                              'consentimento', 'lgpd', 'gdpr', 'valorizamos',
                              'essenciais', 'aceitar', 'rejeitar', 'personalizar'];
            const results = [];
            document.querySelectorAll('*').forEach(el => {
                const style = window.getComputedStyle(el);
                const pos = style.position;
                const z = parseInt(style.zIndex) || 0;
                if ((pos === 'fixed' || pos === 'sticky') && z >= 100) {
                    const text = (el.innerText || '').toLowerCase();
                    if (keywords.some(k => text.includes(k)) && text.length > 20) {
                        results.push(el);
                    }
                }
            });
            return results;
        """)
        if candidates:
            return candidates[0]
    except Exception:
        pass
    return None
