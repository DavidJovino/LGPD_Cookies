from core.driver import init_driver, close_driver
from checks.banner_check import check_first_level_banner
from checks.cookies_check import check_cookies_storage
from checks.privacy_policy_check import check_privacy_policy
from core.scoring import calculate_conformity_score
from reporting.recommendations import generate_recommendations
from reporting.report_printer import print_report


class LGPDCookieChecker:

    def __init__(self, url: str, headless: bool = True, timeout: int = 30):
        self.url = url
        self.headless = headless
        self.timeout = timeout
        self.driver = None

        self.results = {
            "url": url,
            "status": None,
            "conformity_score": 0,
            "issues": [],
            "recommendations": [],
            "details": {}
        }

    def run(self) -> dict:
        try:
            # 1️⃣ inicia driver
            self.driver = init_driver(
                headless=self.headless,
                timeout=self.timeout
            )

            # 2️⃣ acessa o site
            self.driver.get(self.url)

            # 3️⃣ executa checks
            self.results["details"]["first_level_banner"] = (
                check_first_level_banner(self.driver)
            )

            self.results["details"]["cookies"] = (
                check_cookies_storage(self.driver)
            )

            self.results["details"]["privacy_policy"] = (
                check_privacy_policy(self.driver)
            )

            # 4️⃣ coleta issues
            for check in self.results["details"].values():
                if "issues" in check:
                    self.results["issues"].extend(check["issues"])

            # 5️⃣ score
            self.results["conformity_score"] = calculate_conformity_score(
                self.results
            )

            # 6️⃣ recomendações
            self.results["recommendations"] = generate_recommendations(
                self.results
            )

            # 7️⃣ status
            score = self.results["conformity_score"]
            if score >= 80:
                self.results["status"] = "Conforme"
            elif score >= 60:
                self.results["status"] = "Parcialmente Conforme"
            else:
                self.results["status"] = "Não Conforme"

            return self.results

        finally:
            # 8️⃣ garante fechamento do driver
            close_driver(self.driver)
    
    def print_report(self):
        """Imprime o relatório formatado"""
        print_report(self.results)