from typing import List
from urllib.parse import urlparse
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

def find_element_by_text(container, text_patterns: List[str], tag_names: List[str] = None, require_displayed: bool = False) -> bool:
    """
    Procura por elemento contendo texto específico (case-insensitive).
    require_displayed=False porque para auditoria a presença no DOM já é relevante.
    """
    if tag_names is None:
        tag_names = ['button', 'a', 'div', 'span']

    try:
        for tag in tag_names:
            for pattern in text_patterns:
                pat = (pattern or "").strip().lower()
                if not pat:
                    continue

                # Busca case-insensitive via translate
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
                        except:
                            pass
        return False
    except:
        return False

def find_element_by_aria_label(container, aria_patterns: List[str], require_displayed: bool = False) -> bool:
    """
    Procura por elemento com aria-label contendo padrões.
    """
    try:
        for pattern in aria_patterns:
            pat = (pattern or "").strip().lower()
            if not pat:
                continue

            # contains case-insensitive
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
                    except:
                        pass
        return False
    except:
        return False

def find_element_by_class(container, class_patterns: List[str], require_displayed: bool = False) -> bool:
    """
    Procura por elemento contendo fragmentos de classe.
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
                    except:
                        pass
        return False
    except:
        return False
