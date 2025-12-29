def print_report(results: dict):
    """Imprime relatório formatado"""
    print("\n" + "="*70)
    print("RELATÓRIO DE CONFORMIDADE COM LGPD - COOKIES")
    print("="*70)
    
    print(f"\nURL: {results['url']}")
    print(f"Status: {results.get('status', 'N/A')}")
    print(f"Pontuação de Conformidade: {results['conformity_score']}/100")
    
    # Detalhes do banner
    print("\n" + "-"*70)
    print("BANNER DE PRIMEIRO NÍVEL")
    print("-"*70)
    banner = results["details"]["first_level_banner"]
    print(f"Banner encontrado: {'✓' if banner['found'] else '✗'}")
    print(f"Botão de rejeição: {'✓' if banner['has_reject_button'] else '✗'}")
    print(f"Botão de aceitação: {'✓' if banner['has_accept_button'] else '✗'}")
    print(f"Link para política: {'✓' if banner['has_cookie_policy_link'] else '✗'}")
    
    if banner["issues"]:
        print("\nProblemas encontrados:")
        for issue in banner["issues"]:
            print(f"  • {issue}")
    
    # Detalhes dos cookies
    print("\n" + "-"*70)
    print("ANÁLISE DE COOKIES")
    print("-"*70)
    cookies = results["details"]["cookies"]
    print(f"Total de cookies: {cookies['total_cookies']}")
    
    print("\nCategorização:")
    for category, cookie_list in cookies["categories"].items():
        if cookie_list:
            print(f"  {category.upper()}: {len(cookie_list)} cookie(s)")
            for cookie in cookie_list[:3]:
                print(f"    - {cookie}")
            if len(cookie_list) > 3:
                print(f"    ... e mais {len(cookie_list) - 3}")
    
    if cookies["issues"]:
        print("\nProblemas encontrados:")
        for issue in cookies["issues"]:
            print(f"  • {issue}")
    
    # Detalhes da política
    print("\n" + "-"*70)
    print("POLÍTICA DE PRIVACIDADE")
    print("-"*70)
    policy = results["details"]["privacy_policy"]
    print(f"Política encontrada: {'✓' if policy['found'] else '✗'}")
    if policy["found"]:
        print(f"URL: {policy['url']}")
    print(f"Seção de cookies: {'✓' if policy['has_cookie_section'] else '✗'}")
    print(f"Bases legais especificadas: {'✓' if policy['has_legal_bases'] else '✗'}")
    print(f"Categorias de cookies: {'✓' if policy['has_categories'] else '✗'}")
    
    if policy["issues"]:
        print("\nProblemas encontrados:")
        for issue in policy["issues"]:
            print(f"  • {issue}")
    
    # Recomendações
    if results["recommendations"]:
        print("\n" + "-"*70)
        print("RECOMENDAÇÕES")
        print("-"*70)
        for i, rec in enumerate(results["recommendations"], 1):
            print(f"{i}. {rec}")
    
    print("\n" + "="*70 + "\n")
