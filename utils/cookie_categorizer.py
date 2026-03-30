def categorize_cookie(cookie_name: str) -> str:
    """
    Categoriza um cookie baseado em seu nome.

    Categorias:
    - essential:    cookies necessários para o funcionamento do site
    - analytics:    cookies de análise de tráfego e comportamento
    - marketing:    cookies de publicidade e rastreamento
    - preferences:  cookies de preferências do usuário
    - unknown:      cookies não identificados
    """
    name = cookie_name.lower()

    # ── Cookies Essenciais ────────────────────────────────────────────────────
    essential_patterns = [
        "session", "sess", "csrf", "xsrf", "auth", "security",
        "token", "sid", "uid", "user_id", "login", "logged",
        "cart", "basket", "checkout", "order", "woocommerce",
        "wordpress", "wp-", "phpsessid", "jsessionid", "asp.net",
        "laravel_session", "remember_token", "consent", "privacy",
        "cookie_notice", "cookieconsent", "cookie_accepted",
        "gdpr", "lgpd", "cc_cookie", "viewed_cookie_policy",
        "euconsent", "borlabs", "cookieyes", "cookielaw",
    ]
    if any(p in name for p in essential_patterns):
        return "essential"

    # ── Cookies de Analytics ──────────────────────────────────────────────────
    analytics_patterns = [
        "_ga", "_gid", "_gat", "_gtm", "gtag",
        "analytics", "mixpanel", "amplitude", "hotjar", "hj",
        "_hjid", "_hjsession", "_hjfirstseen", "_hjincludedinsession",
        "clarity", "_clck", "_clsk", "ms_clarity",
        "heap", "segment", "intercom", "fullstory",
        "crazyegg", "mouseflow", "inspectlet",
        "matomo", "piwik", "_pk_",
        "optimizely", "ab_test", "split_test",
        "newrelic", "nr_", "dynatrace",
        "quantserve", "quantcast", "_qca",
        "chartbeat", "_chartbeat",
    ]
    if any(p in name for p in analytics_patterns):
        return "analytics"

    # ── Cookies de Marketing ──────────────────────────────────────────────────
    marketing_patterns = [
        "_fbp", "_fbc", "fbclid", "facebook", "fb_",
        "google_ads", "gclid", "gcl_au", "_gcl",
        "utm_", "utm", "gads", "adwords",
        "linkedin", "li_", "lidc", "bcookie", "bscookie",
        "twitter", "twid", "ct0",
        "pinterest", "_pin_unauth",
        "snapchat", "sc_",
        "tiktok", "tt_",
        "doubleclick", "__gads", "__gpi",
        "criteo", "cto_", "uid", "uuid",
        "bing", "muid", "_uetsid", "_uetvid",
        "taboola", "t_gid",
        "outbrain", "obuid",
        "adroll", "__ar_",
        "hubspot", "__hs", "hubspotutk",
        "pardot", "visitor_id",
        "marketo", "_mkto_",
        "sailthru",
    ]
    if any(p in name for p in marketing_patterns):
        return "marketing"

    # ── Cookies de Preferências ───────────────────────────────────────────────
    preferences_patterns = [
        "language", "lang", "locale", "idioma",
        "theme", "tema", "dark_mode", "color_scheme",
        "preference", "preferencia", "pref",
        "timezone", "currency", "moeda",
        "font_size", "accessibility",
        "notification", "notificacao",
        "volume", "player",
        "recently_viewed", "wishlist",
        "newsletter", "subscribe",
    ]
    if any(p in name for p in preferences_patterns):
        return "preferences"

    return "unknown"
