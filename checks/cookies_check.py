from utils.cookie_categorizer import categorize_cookie

def check_cookies_storage(driver) -> dict:
    """
    Verifica os cookies armazenados
    """
    cookies_info = {
        "total_cookies": 0,
        "cookies": [],
        "categories": {
            "essential": [],
            "analytics": [],
            "marketing": [],
            "preferences": [],
            "unknown": []
        },
        "issues": []
    }
    
    try:
        # Obtém todos os cookies
        all_cookies = driver.get_cookies()
        cookies_info["total_cookies"] = len(all_cookies)
        
        for cookie in all_cookies:
            cookie_info = {
                "name": cookie.get("name", ""),
                "domain": cookie.get("domain", ""),
                "path": cookie.get("path", ""),
                "secure": cookie.get("secure", False),
                "httpOnly": cookie.get("httpOnly", False),
                "category": categorize_cookie(cookie.get("name", ""))
            }
            
            cookies_info["cookies"].append(cookie_info)
            
            # Classifica o cookie
            category = cookie_info["category"]
            if category in cookies_info["categories"]:
                cookies_info["categories"][category].append(cookie_info["name"])
        
        # Verifica problemas
        if cookies_info["total_cookies"] == 0:
            cookies_info["issues"].append(
                "Nenhum cookie encontrado (pode indicar que o site não usa cookies)"
            )
        
        # Verifica se há cookies sem categoria identificada
        unknown_count = len(cookies_info["categories"]["unknown"])
        if unknown_count > 0:
            cookies_info["issues"].append(
                f"{unknown_count} cookie(s) não categorizado(s) encontrado(s)"
            )
            
    except Exception as e:
        cookies_info["issues"].append(f"Erro ao verificar cookies: {str(e)}")
        
    return cookies_info
