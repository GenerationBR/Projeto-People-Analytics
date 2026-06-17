"""Ferramentas estatísticas: testes de hipótese, tamanho de efeito, validação de pressupostos."""

import logging
from dataclasses import dataclass
from typing import Optional

import numpy as np
from scipy import stats as scipy_stats

logger = logging.getLogger(__name__)


@dataclass
class TestResult:
    h0: str
    h1: str
    test_name: str
    statistic: float
    p_value: float
    confidence_interval: tuple[float, float]
    effect_size: float
    effect_label: str
    reject_h0: bool
    alpha: float
    interpretation: str
    limitations: list[str]


class StatsTools:
    def __init__(self, alpha: float = 0.05):
        self.alpha = alpha

    def check_normality(self, data: np.ndarray, label: str = "") -> dict:
        """Shapiro-Wilk (n ≤ 5000) ou Kolmogorov-Smirnov."""
        n = len(data)
        if n <= 5000:
            stat, p = scipy_stats.shapiro(data[:5000])
            test = "Shapiro-Wilk"
        else:
            stat, p = scipy_stats.kstest(data, "norm", args=(data.mean(), data.std()))
            test = "Kolmogorov-Smirnov"

        is_normal = p > self.alpha
        logger.info(f"Normalidade {label} [{test}]: stat={stat:.4f}, p={p:.4f} → {'normal' if is_normal else 'não-normal'}")
        return {"test": test, "statistic": float(stat), "p_value": float(p), "is_normal": is_normal}

    def check_homogeneity(self, *groups: np.ndarray) -> dict:
        """Teste de Levene para homocedasticidade."""
        stat, p = scipy_stats.levene(*groups)
        equal_var = p > self.alpha
        logger.info(f"Homogeneidade [Levene]: stat={stat:.4f}, p={p:.4f} → {'iguais' if equal_var else 'diferentes'}")
        return {"statistic": float(stat), "p_value": float(p), "equal_variances": equal_var}

    def cohens_d(self, group1: np.ndarray, group2: np.ndarray) -> tuple[float, str]:
        """Calcula Cohen's d e classifica o tamanho de efeito."""
        n1, n2 = len(group1), len(group2)
        pooled_std = np.sqrt(
            ((n1 - 1) * group1.std(ddof=1) ** 2 + (n2 - 1) * group2.std(ddof=1) ** 2)
            / (n1 + n2 - 2)
        )
        d = (group1.mean() - group2.mean()) / pooled_std if pooled_std > 0 else 0.0
        abs_d = abs(d)
        label = "negligível" if abs_d < 0.2 else "pequeno" if abs_d < 0.5 else "médio" if abs_d < 0.8 else "grande"
        return float(d), label

    def gender_pay_gap_test(
        self,
        salarios_masc: np.ndarray,
        salarios_fem: np.ndarray,
        cargo: str = "",
        regiao: str = "",
    ) -> TestResult:
        """
        Testa se há diferença salarial significativa entre homens e mulheres.
        Escolhe automaticamente t-test de Welch ou Mann-Whitney U.
        """
        h0 = "Não há diferença salarial significativa entre homens e mulheres"
        h1 = "Existe diferença salarial significativa entre homens e mulheres"
        limitations = []

        n_m, n_f = len(salarios_masc), len(salarios_fem)
        logger.info(f"Teste pay gap — cargo='{cargo}' regiao='{regiao}' n_masc={n_m} n_fem={n_f}")

        if n_m < 30 or n_f < 30:
            limitations.append(f"Amostra pequena (Masculino n={n_m}, Feminino n={n_f}). Interpretar com cautela.")

        norm_m = self.check_normality(salarios_masc, "Masculino")
        norm_f = self.check_normality(salarios_fem, "Feminino")
        homog = self.check_homogeneity(salarios_masc, salarios_fem)

        both_normal = norm_m["is_normal"] and norm_f["is_normal"]

        if both_normal:
            # t-test de Welch (não assume variâncias iguais)
            stat, p = scipy_stats.ttest_ind(salarios_masc, salarios_fem, equal_var=not homog["equal_variances"])
            test_name = "t-test de Welch" if not homog["equal_variances"] else "t-test de Student"
            ci = scipy_stats.t.interval(
                1 - self.alpha,
                df=n_m + n_f - 2,
                loc=salarios_masc.mean() - salarios_fem.mean(),
                scale=np.sqrt(salarios_masc.var(ddof=1) / n_m + salarios_fem.var(ddof=1) / n_f),
            )
        else:
            # Mann-Whitney U (não-paramétrico)
            stat, p = scipy_stats.mannwhitneyu(salarios_masc, salarios_fem, alternative="two-sided")
            test_name = "Mann-Whitney U"
            ci = (float("nan"), float("nan"))
            limitations.append("Distribuição não-normal: IC aproximado não disponível para Mann-Whitney.")

        d, effect_label = self.cohens_d(salarios_masc, salarios_fem)
        reject = bool(p < self.alpha)

        gap_pct = (salarios_masc.mean() - salarios_fem.mean()) / salarios_masc.mean() * 100

        interpretation = (
            f"{'Rejeitamos H0' if reject else 'Não rejeitamos H0'} (α={self.alpha}). "
            f"Salário médio masc: R$ {salarios_masc.mean():,.2f} | fem: R$ {salarios_fem.mean():,.2f}. "
            f"Gender Pay Gap: {gap_pct:.1f}%. "
            f"Tamanho de efeito (Cohen's d): {d:.3f} → {effect_label}. "
            f"Significância estatística {'confirma' if reject else 'não confirma'} diferença salarial. "
            "Lembre-se: significância ≠ relevância prática — avalie o contexto."
        )

        return TestResult(
            h0=h0,
            h1=h1,
            test_name=test_name,
            statistic=float(stat),
            p_value=float(p),
            confidence_interval=(float(ci[0]), float(ci[1])),
            effect_size=d,
            effect_label=effect_label,
            reject_h0=reject,
            alpha=self.alpha,
            interpretation=interpretation,
            limitations=limitations,
        )
