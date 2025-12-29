def generate_recommendations(results: dict) -> list:
    """Gera recomendações baseadas nos problemas encontrados"""
    recommendations = []
    
    # Recomendações para banner
    if not results["details"]["first_level_banner"]["found"]:
        recommendations.append(
            "Implementar banner de consentimento de cookies visível ao usuário"
        )
    
    if not results["details"]["first_level_banner"]["has_reject_button"]:
        recommendations.append(
            "Adicionar botão de fácil visualização para rejeitar todos os cookies não necessários"
        )
    
    if not results["details"]["first_level_banner"]["has_cookie_policy_link"]:
        recommendations.append(
            "Adicionar link para a política de cookies no banner de consentimento"
        )
    
    # Recomendações para cookies
    cookies_info = results["details"]["cookies"]
    if cookies_info["categories"]["unknown"]:
        recommendations.append(
            f"Categorizar os seguintes cookies: {', '.join(cookies_info['categories']['unknown'][:5])}"
        )
    
    # Recomendações para política
    if not results["details"]["privacy_policy"]["found"]:
        recommendations.append(
            "Criar e disponibilizar uma política de privacidade/cookies clara e acessível"
        )
    
    if not results["details"]["privacy_policy"]["has_legal_bases"]:
        recommendations.append(
            "Especificar as bases legais para coleta de cada categoria de cookie"
        )
    
    if not results["details"]["privacy_policy"]["has_categories"]:
        recommendations.append(
            "Classificar os cookies em categorias (essenciais, análise, marketing, preferências)"
        )
    
    return recommendations
