"""
LGPD Cookie Checker
Verificar se os cookies de um site estão de acordo com as recomendações da ANPD

Recomendações da ANPD para conformidade com LGPD:

Banner de Primeiro Nível:
1. Disponibilizar botão de fácil visualização para rejeitar todos os cookies não necessários
2. Desativar cookies baseados no consentimento por padrão (opt-in)

Banner de Segundo Nível (Política de Cookies):
1. Identificar as bases legais utilizadas por categoria de cookie
2. Classificar os cookies em categorias
3. Permitir consentimento específico por categoria
4. Disponibilizar botão para rejeitar todos os cookies não necessários
"""

import sys
import json
from urllib.parse import urlparse
from core.checker import LGPDCookieChecker
import time  

def main():
    """Função principal"""
    if len(sys.argv) < 2:
        print("Uso: python3 lgpd_cookie_checker.py <URL> [--headless] [--json]")
        print("\nExemplos:")
        print("  python3 lgpd_cookie_checker.py https://exemplo.com.br")
        print("  python3 lgpd_cookie_checker.py https://exemplo.com.br --json")
        sys.exit(1)
    
    url = sys.argv[1]
    output_json = "--json" in sys.argv
    headless = "--no-headless" not in sys.argv
    
    # Valida URL
    try:
        result = urlparse(url)
        if not all([result.scheme, result.netloc]):
            print("Erro: URL inválida")
            sys.exit(1)
    except:
        print("Erro: URL inválida")
        sys.exit(1)
    
    # Executa verificação
    print(f"Iniciando verificação de {url}...")
    checker = LGPDCookieChecker(url, headless=headless)
    results = checker.run()
    
    # Exibe resultados
    if output_json:
        print(json.dumps(results, indent=2, ensure_ascii=False))
    else:
        checker.print_report()
        
        # Salva JSON também
        json_file = f"lgpd_check_{int(time.time())}.json"
        with open(json_file, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        print(f"Relatório JSON salvo em: {json_file}")


if __name__ == "__main__":
    main()