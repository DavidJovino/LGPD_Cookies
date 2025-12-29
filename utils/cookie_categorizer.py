def categorize_cookie(cookie_name: str) -> str:
    """Categoriza um cookie baseado em seu nome"""
    cookie_name_lower = cookie_name.lower()
    
    # Cookies essenciais
    essential_keywords = ["session", "csrf", "auth", "security", "token", "sid"]
    if any(keyword in cookie_name_lower for keyword in essential_keywords):
        return "essential"
    
    # Cookies de análise
    analytics_keywords = ["ga", "analytics", "gtag", "mixpanel", "amplitude", "hotjar"]
    if any(keyword in cookie_name_lower for keyword in analytics_keywords):
        return "analytics"
    
    # Cookies de marketing
    marketing_keywords = ["facebook", "fbp", "fbq", "google_ads", "gclid", "utm", "linkedin"]
    if any(keyword in cookie_name_lower for keyword in marketing_keywords):
        return "marketing"
    
    # Cookies de preferências
    preferences_keywords = ["language", "theme", "preference", "idioma", "tema", "locale"]
    if any(keyword in cookie_name_lower for keyword in preferences_keywords):
        return "preferences"
    
    return "unknown"
