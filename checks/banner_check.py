from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from utils.dom_finder import find_element_by_text, find_element_by_aria_label, find_element_by_class

def check_first_level_banner(driver) -> dict:
    """
    Verifica o banner de primeiro nível com múltiplas estratégias
    """
    banner_info = {
        "found": False,
        "has_accept_button": False,
        "has_reject_button": False,
        "has_cookie_policy_link": False,
        "text_content": "",
        "issues": []
    }

    try:
        try:
            WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".cc-compliance, .cc-message, [class*='cookie'], [id*='cookie'], [class*='consent'], [id*='consent']"))
            )
        except:
            time.sleep(4)

        # ESTRATÉGIA 1: Procurar por elementos comuns de banner
        banner_selectors = [
            ".cc-window",            # cookieconsent clássico
            ".cc-banner",
            ".cc-compliance",
            ".cc-message",
            "[class*='cookie']",
            "[id*='cookie']",
            "[class*='consent']",
            "[id*='consent']",
            "[class*='cc-']",
            "[class*='compliance']",
            "[role='dialog']",
            "[role='alert']",
            ".cookiebot",
            ".cookie-banner",
            ".cookie-consent",
            "[data-component*='cookie']"
        ]

        banner_element = None
        for selector in banner_selectors:
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    banner_element = elements[0]
                    break
            except:
                continue

        if banner_element:
            banner_info["found"] = True

            try:
                banner_root = banner_element.find_element(
                    By.XPATH,
                    "ancestor-or-self::*[contains(@class,'cc-window') or contains(@class,'cc-banner') or contains(@class,'cc-compliance') or contains(@class,'cookie') or @role='dialog'][1]"
                )
            except:
                banner_root = banner_element

            try:
                banner_info["text_content"] = (banner_root.text or "")[:500]
            except:
                pass

            # DEBUG
            # print("DEBUG cc-deny total:", len(driver.find_elements(By.CSS_SELECTOR, ".cc-deny")))
            # print("DEBUG cc-allow total:", len(driver.find_elements(By.CSS_SELECTOR, ".cc-allow")))

            # ESTRATÉGIA 2: Procurar por botões de rejeição
            reject_patterns = [
                'rejeitar', 
                'recusar', 
                'deny', 
                'reject', 
                'negar', 
                'descartar',
                'deny cookies', 
                'reject all', 
                'recusar tudo', 
                'refuse all',
                'não aceitar', 
                'decline', 
                'refuse', 
                'disallow'
            ]

            has_reject = False
            # 2a: texto
            has_reject = find_element_by_text(banner_root, reject_patterns, tag_names=['button', 'a', 'div', 'span'], require_displayed=False)

            # 2b: aria-label
            if not has_reject:
                has_reject = find_element_by_aria_label(banner_root, reject_patterns, require_displayed=False)

            # 2c: classe
            if not has_reject:
                reject_classes = ['deny', 'reject', 'refuse', 'decline', 'recusar', 'cc-deny']
                has_reject = find_element_by_class(banner_root, reject_classes, require_displayed=False)

            # 2d: fallback GLOBAL
            if not has_reject:
                reject_css = [
                    ".cc-compliance .cc-btn.cc-deny",
                    ".cc-deny",
                    "a[role='button'][aria-label*='deny']",
                    "a.cc-btn.cc-deny",
                ]
                for sel in reject_css:
                    if driver.find_elements(By.CSS_SELECTOR, sel):
                        has_reject = True
                        break

            banner_info["has_reject_button"] = has_reject

            # ESTRATÉGIA 3: Procurar por botões de aceitação
            accept_patterns = [
                'aceitar', 'accept', 'allow', 'permitir', 'concordo',
                'allow cookies', 'accept all', 'aceitar tudo', 'permit all',
                'agree', 'ok', 'continue', 'proceed'
            ]

            has_accept = False
            # 3a: texto
            has_accept = find_element_by_text(banner_root, accept_patterns, tag_names=['button', 'a', 'div', 'span'], require_displayed=False)

            # 3b: aria-label
            if not has_accept:
                has_accept = find_element_by_aria_label(banner_root, accept_patterns, require_displayed=False)

            # 3c: classe
            if not has_accept:
                accept_classes = ['allow', 'accept', 'agree', 'ok', 'aceitar', 'cc-allow']
                has_accept = find_element_by_class(banner_root, accept_classes, require_displayed=False)

            # 3d: fallback GLOBAL
            if not has_accept:
                accept_css = [
                    ".cc-compliance .cc-btn.cc-allow",
                    ".cc-allow",
                    "a[role='button'][aria-label*='allow']",
                    "a.cc-btn.cc-allow",
                ]
                for sel in accept_css:
                    if driver.find_elements(By.CSS_SELECTOR, sel):
                        has_accept = True
                        break

            banner_info["has_accept_button"] = has_accept

            # ESTRATÉGIA 4: Procurar por link de política de cookies
            policy_patterns = [
                'política', 'policy', 'cookies', 'privacidade', 'privacy',
                'termos', 'terms', 'saiba mais', 'learn more', 'mais informações'
            ]

            # 4a banner_root
            try:
                links = banner_root.find_elements(By.TAG_NAME, 'a')
                for link in links:
                    try:
                        link_text = (link.text or "").lower()
                        link_href = (link.get_attribute('href') or "").lower()

                        if any(p.lower() in link_text or p.lower() in link_href for p in policy_patterns):
                            banner_info["has_cookie_policy_link"] = True
                            break
                    except:
                        pass
            except:
                pass

            # 4b fallback global
            if not banner_info["has_cookie_policy_link"]:
                try:
                    links = driver.find_elements(By.TAG_NAME, 'a')
                    for link in links:
                        try:
                            link_text = (link.text or "").lower()
                            link_href = (link.get_attribute('href') or "").lower()
                            if any(p.lower() in link_text or p.lower() in link_href for p in policy_patterns):
                                banner_info["has_cookie_policy_link"] = True
                                break
                        except:
                            pass
                except:
                    pass

            # Possíveis problemas
            if not banner_info["has_reject_button"]:
                banner_info["issues"].append("Botão de rejeição de cookies não encontrado")

            if not banner_info["has_accept_button"]:
                banner_info["issues"].append("Botão de aceitação de cookies não encontrado")

            if not banner_info["has_cookie_policy_link"]:
                banner_info["issues"].append("Link para política de cookies não encontrado")
        else:
            banner_info["issues"].append("Banner de cookies não encontrado no site")

    except Exception as e:
        banner_info["issues"].append(f"Erro ao verificar banner: {str(e)}")

    return banner_info
