from selenium.webdriver.common.by import By
import time

def check_privacy_policy(driver) -> dict:
    """
    Verifica a presença e conteúdo da política de privacidade
    """
    policy_info = {
        "found": False,
        "url": None,
        "has_cookie_section": False,
        "has_legal_bases": False,
        "has_categories": False,
        "issues": []
    }
    
    try:
        # Procura por links de política de privacidade
        policy_selectors = [
            "a[href*='privacy']",
            "a[href*='privacidade']",
            "a[href*='politica']",
            "a[href*='policy']",
            "a[href*='cookies']",
            "[class*='privacy']",
            "[class*='privacidade']"
        ]
        
        policy_link = None
        for selector in policy_selectors:
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    policy_link = elements[0]
                    break
            except:
                continue
        
        if policy_link:
            policy_info["found"] = True
            policy_info["url"] = policy_link.get_attribute("href")
            
            # Verifica conteúdo da página de política
            try:
                policy_link.click()
                time.sleep(2) #colocar timer variavel no futuro, isso vai dar problema
                
                page_text = driver.page_source.lower()
                
                if "cookie" in page_text:
                    policy_info["has_cookie_section"] = True
                
                if "base legal" in page_text or "legal basis" in page_text:
                    policy_info["has_legal_bases"] = True
                
                if "categoria" in page_text or "category" in page_text:
                    policy_info["has_categories"] = True
                    
            except:
                pass
        else:
            policy_info["issues"].append(
                "Política de privacidade não encontrada"
            )
            
    except Exception as e:
        policy_info["issues"].append(f"Erro ao verificar política: {str(e)}")
        
    return policy_info
