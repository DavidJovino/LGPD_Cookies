def calculate_conformity_score(results: dict) -> int:
    """
    Calcula uma pontuação de conformidade (0-100)
    """
    score = 0
    max_score = 100
    
    # Banner de primeiro nível
    if results["details"]["first_level_banner"]["found"]:
        score += 15
    if results["details"]["first_level_banner"]["has_reject_button"]:
        score += 15
    if results["details"]["first_level_banner"]["has_accept_button"]:
        score += 10
    
    # Cookies
    cookies_info = results["details"]["cookies"]
    if cookies_info["total_cookies"] > 0:
        score += 10
        
    # Verifica se há cookies categorizados
    categorized = sum(
        len(v) for k, v in cookies_info["categories"].items() if k != "unknown"
    )
    if categorized > 0:
        score += 10
    
    # Política de privacidade
    policy_info = results["details"]["privacy_policy"]
    if policy_info["found"]:
        score += 10
    if policy_info["has_cookie_section"]:
        score += 10
    if policy_info["has_legal_bases"]:
        score += 10
    
    # Penalidades por problemas
    total_issues = len(results["issues"])
    score -= min(total_issues * 5, 20)
    
    return max(0, min(score, max_score))
