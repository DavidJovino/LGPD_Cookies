# 🔍 LGPD Cookie Checker

Um verificador automatizado de conformidade de cookies com a **Lei Geral de Proteção de Dados (LGPD)** brasileira, baseado nas recomendações da **ANPD** (Autoridade Nacional de Proteção de Dados).

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Status: Active](https://img.shields.io/badge/Status-Active-brightgreen.svg)]()

---

## 📋 Sobre o Projeto

O **LGPD Cookie Checker** automatiza a auditoria de conformidade de cookies em websites brasileiros, verificando:

✅ **Banner de Primeiro Nível**
- Presença de banner de consentimento visível
- Botão de rejeição de cookies
- Botão de aceitação de cookies
- Link para política de cookies

✅ **Análise de Cookies**
- Detecção automática de cookies
- Categorização (essenciais, análise, marketing, preferências)
- Identificação de cookies não categorizados

✅ **Política de Privacidade**
- Presença de política de privacidade
- Seção específica sobre cookies
- Especificação de bases legais
- Classificação de categorias de cookies

---

## 🚀 Instalação

### Pré-requisitos
- Python 3.8 ou superior
- pip (gerenciador de pacotes Python)
- Google Chrome instalado (para Selenium)

### Passo 1: Clonar o Repositório

```bash
git clone https://github.com/seu-usuario/lgpd-cookie-checker.git
cd lgpd-cookie-checker
```

### Passo 2: Criar Ambiente Virtual (Recomendado)

```bash
# Linux/macOS
python3 -m venv venv
source venv/bin/activate

# Windows
python -m venv venv
venv\Scripts\activate
```

### Passo 3: Instalar Dependências

```bash
pip install -r requirements.txt
```

---

## 📖 Como Usar

### Uso Básico

```bash
python3 lgpd_cookie_ckecker.py https://seu-site.com.br
```

### Opções Disponíveis

```bash
# Saída em JSON
python3 lgpd_cookie_ckecker.py https://seu-site.com.br --json

# Sem modo headless (ver navegador em ação)
python3 lgpd_cookie_ckecker.py https://seu-site.com.br --no-headless

# Combinações
python3 lgpd_cookie_ckecker.py https://seu-site.com.br --json --no-headless
```

### Exemplo de Saída

```
======================================================================
RELATÓRIO DE CONFORMIDADE COM LGPD - COOKIES
======================================================================

URL: https://morar.com.br
Status: Parcialmente Conforme
Pontuação de Conformidade: 65/100

----------------------------------------------------------------------
BANNER DE PRIMEIRO NÍVEL
----------------------------------------------------------------------
Banner encontrado: ✓
Botão de rejeição: ✓
Botão de aceitação: ✓
Link para política: ✓

----------------------------------------------------------------------
ANÁLISE DE COOKIES
----------------------------------------------------------------------
Total de cookies: 9

Categorização:
  ANALYTICS: 4 cookie(s)
    - _ga
    - _ga_G2DJBY4P6F
    - _gat_UA-61123573-1
  MARKETING: 1 cookie(s)
    - _fbp
  UNKNOWN: 4 cookie(s)
    - _clck
    - _gid
    - _gcl_au

----------------------------------------------------------------------
POLÍTICA DE PRIVACIDADE
----------------------------------------------------------------------
Política encontrada: ✓
URL: https://morar.com.br/politicas-de-privacidade
Seção de cookies: ✗
Bases legais especificadas: ✗
Categorias de cookies: ✗

----------------------------------------------------------------------
RECOMENDAÇÕES
----------------------------------------------------------------------
1. Categorizar os seguintes cookies: _clck, _gid, _gcl_au, _clsk
2. Especificar as bases legais para coleta de cada categoria de cookie
3. Classificar os cookies em categorias (essenciais, análise, marketing, preferências)

======================================================================
Relatório JSON salvo em: lgpd_check_1766407798.json
```

---

## 📊 Pontuação de Conformidade

A pontuação varia de **0 a 100** e é calculada da seguinte forma:

| Aspecto | Pontos | Critério |
|---------|--------|----------|
| **Banner** | 40 | Banner encontrado (15) + Botão rejeição (15) + Botão aceitação (10) |
| **Cookies** | 20 | Cookies detectados (10) + Cookies categorizados (10) |
| **Política** | 30 | Política encontrada (10) + Seção cookies (10) + Bases legais (10) |
| **Penalidades** | -20 | Até -5 pontos por problema encontrado |

### Classificação

- **80-100**: ✅ **Conforme** - Atende às recomendações da ANPD
- **60-79**: ⚠️ **Parcialmente Conforme** - Precisa de melhorias
- **0-59**: ❌ **Não Conforme** - Necessário implementar mudanças

---

## 🏗️ Arquitetura do Projeto

```
lgpd-cookie-checker/
├── lgpd_cookie_ckecker.py          # Arquivo principal
├── core/
│   ├── __init__.py
│   ├── checker.py                  # Classe principal LGPDCookieChecker
│   ├── driver.py                   # Gerenciamento do Selenium
│   └── scoring.py                  # Cálculo de pontuação
├── checks/
│   ├── __init__.py
│   ├── banner_check.py             # Verificação de banner
│   ├── cookies_check.py            # Análise de cookies
│   └── privacy_policy_check.py     # Verificação de política
├── reporting/
│   ├── __init__.py
│   ├── recommendations.py          # Geração de recomendações
│   └── report_printer.py           # Formatação de relatório
├── utils/
│   ├── __init__.py
│   ├── dom_finder.py               # Funções de busca no DOM
│   ├── cookie_categorizer.py       # Categorização de cookies
│   └── validators.py               # Validadores
├── requirements.txt                # Dependências do projeto
├── .gitignore                      # Arquivos ignorados pelo Git
└── README.md                       # Este arquivo
```

---

## 🔧 Estrutura de Módulos

### `core/checker.py`
Classe principal que orquestra toda a verificação:
```python
from core.checker import LGPDCookieChecker

checker = LGPDCookieChecker("https://exemplo.com.br")
results = checker.run()
checker.print_report()
```

### `checks/banner_check.py`
Verifica o banner de consentimento usando múltiplas estratégias:
- Seletores CSS
- Texto visível
- Atributos aria-label
- Classes customizadas

### `checks/cookies_check.py`
Extrai e categoriza cookies:
- Analytics (Google Analytics, Mixpanel, etc)
- Marketing (Facebook, LinkedIn, etc)
- Essenciais (Session, CSRF, etc)
- Preferências (Idioma, Tema, etc)

### `checks/privacy_policy_check.py`
Valida a presença e conteúdo da política de privacidade

### `utils/dom_finder.py`
Funções auxiliares para busca no DOM com múltiplas estratégias

---

## 📝 Recomendações da ANPD

Este projeto segue as recomendações da ANPD para conformidade com LGPD:

### Banner de Primeiro Nível
1. ✅ Disponibilizar botão de fácil visualização para rejeitar todos os cookies não necessários
2. ✅ Desativar cookies baseados no consentimento por padrão (opt-in)

### Banner de Segundo Nível (Política de Cookies)
1. ✅ Identificar as bases legais utilizadas por categoria de cookie
2. ✅ Classificar os cookies em categorias
3. ✅ Permitir consentimento específico por categoria
4. ✅ Disponibilizar botão para rejeitar todos os cookies não necessários

**Referência:** [ANPD - Recomendações sobre Cookies](https://lgpdbrasil.com.br/anpd-recomenda-adequacoes-ao-portal-gov-br-em-relacao-a-pratica-de-coleta-de-cookies/)

---

## 🎯 Casos de Uso

### 1. Auditoria de Conformidade
Verificar se seu website está em conformidade com LGPD:
```bash
python3 lgpd_cookie_ckecker.py https://meu-site.com.br
```

### 2. Monitoramento Contínuo
Integrar em CI/CD pipeline para monitorar conformidade:
```bash
python3 lgpd_cookie_ckecker.py https://meu-site.com.br --json > report.json
```

### 3. Auditoria de Clientes
Verificar conformidade de múltiplos sites:
```bash
for site in site1.com.br site2.com.br site3.com.br; do
  python3 lgpd_cookie_ckecker.py https://$site
done
```

### 4. Desenvolvimento
Testar durante desenvolvimento:
```bash
python3 lgpd_cookie_ckecker.py http://localhost:3000 --no-headless
```

---

## 🔍 Detecção de Banners Suportados

O script detecta automaticamente banners de:

- ✅ **Cookiebot** (Muito comum em sites brasileiros)
- ✅ **Google Consent Mode**
- ✅ **Banners customizados** com classes padrão
- ✅ **Modais com role="dialog"**
- ✅ **Notificações com role="alert"**
- ✅ **Qualquer elemento com "cookie" ou "consent" na classe/ID**

---

## 📊 Saída JSON

O script gera automaticamente um arquivo JSON com todos os dados:

```json
{
  "url": "https://morar.com.br",
  "status": "Parcialmente Conforme",
  "conformity_score": 65,
  "issues": [
    "4 cookie(s) não categorizado(s) encontrado(s)"
  ],
  "recommendations": [
    "Categorizar os seguintes cookies: _clck, _gid, _gcl_au, _clsk",
    "Especificar as bases legais para coleta de cada categoria de cookie"
  ],
  "details": {
    "first_level_banner": {
      "found": true,
      "has_accept_button": true,
      "has_reject_button": true,
      "has_cookie_policy_link": true,
      "issues": []
    },
    "cookies": {
      "total_cookies": 9,
      "categories": {
        "analytics": ["_ga", "_ga_G2DJBY4P6F"],
        "marketing": ["_fbp"],
        "unknown": ["_clck", "_gid"]
      }
    },
    "privacy_policy": {
      "found": true,
      "url": "https://morar.com.br/politicas-de-privacidade",
      "has_cookie_section": false
    }
  }
}
```

---

## 🐛 Troubleshooting

### Erro: "Chrome driver not found"
**Solução:** Instale o ChromeDriver compatível com sua versão do Chrome
```bash
# macOS com Homebrew
brew install chromedriver

# Ou baixe manualmente em: https://chromedriver.chromium.org/
```

### Erro: "Timeout waiting for element"
**Solução:** Aumente o timeout na chamada:
```python
checker = LGPDCookieChecker(url, timeout=60)
```

### Banner não detectado
**Solução:** Execute com `--no-headless` para ver o que está acontecendo:
```bash
python3 lgpd_cookie_ckecker.py https://seu-site.com.br --no-headless
```

---

## 🤝 Contribuindo

Contribuições são bem-vindas! Por favor:

1. Faça um Fork do projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

---

## 📄 Licença

Este projeto está licenciado sob a Licença MIT - veja o arquivo [LICENSE](LICENSE) para detalhes.

---

## 📞 Suporte

Encontrou um problema ou tem uma sugestão?

- 🐛 **Reportar Bug:** [Abrir Issue](https://github.com/seu-usuario/lgpd-cookie-checker/issues)
- 💡 **Sugerir Feature:** [Abrir Discussion](https://github.com/seu-usuario/lgpd-cookie-checker/discussions)
- 📧 **Email:** seu-email@exemplo.com

---

## 🙏 Agradecimentos

- [ANPD](https://www.gov.br/cidadania/pt-br/acesso-a-informacao/lgpd) - Autoridade Nacional de Proteção de Dados
- [Selenium](https://www.selenium.dev/) - Web automation framework
- [BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/) - HTML parsing library

---

## 📚 Referências

- [Lei Geral de Proteção de Dados (LGPD)](http://www.planalto.gov.br/ccivil_03/_ato2015-2018/2018/lei/l13709.htm)
- [Recomendações da ANPD sobre Cookies](https://lgpdbrasil.com.br/anpd-recomenda-adequacoes-ao-portal-gov-br-em-relacao-a-pratica-de-coleta-de-cookies/)
- [Guia de Conformidade LGPD](https://www.gov.br/cidadania/pt-br/acesso-a-informacao/lgpd)

---

**Desenvolvido com ❤️ para conformidade com LGPD**

Última atualização: Dezembro de 2025
