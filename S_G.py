import numpy as np

# Matrizes de Pauli e Identidade (base de autovetores de S_z)
SIGMA_X = np.array([[0, 1], [1, 0]], dtype=np.complex128)
SIGMA_Y = np.array([[0, -1j], [1j, 0]], dtype=np.complex128)
SIGMA_Z = np.array([[1, 0], [0, -1]], dtype=np.complex128)
IDENTIDADE = np.eye(2, dtype=np.complex128)


def auto_spin(theta_g: float, phi_g: float = 0.0):
    """
    Retorna os autoestados normalizados |+n> e |-n> do operador S_n = (hbar/2)(sigma . n)
    na direção definida pelos ângulos polar (theta_g) e azimutal (phi_g), em graus.

    Convenção:
        |+n> =  cos(theta/2)|+z> + e^(i*phi) sin(theta/2)|-z>
        |-n> = -e^(-i*phi) sin(theta/2)|+z> + cos(theta/2)|-z>
    """
    theta = np.radians(theta_g)
    phi = np.radians(phi_g)

    mais = np.array(
        [np.cos(theta / 2), np.exp(1j * phi) * np.sin(theta / 2)],
        dtype=np.complex128,
    )
    menos = np.array(
        [-np.exp(-1j * phi) * np.sin(theta / 2), np.cos(theta / 2)],
        dtype=np.complex128,
    )
    return mais, menos


def projetores(theta_g: float, phi_g: float = 0.0):
    """Retorna os projetores ortogonais P_+ = |+n><+n| e P_- = |-n><-n|."""
    mais, menos = auto_spin(theta_g, phi_g)
    p_mais = np.outer(mais, np.conj(mais))
    p_menos = np.outer(menos, np.conj(menos))
    return p_mais, p_menos


def matriz_densidade_nao_polarizada() -> np.ndarray:
    """Retorna a matriz densidade de um feixe térmico não polarizado: rho = I / 2."""
    return 0.5 * IDENTIDADE


def P(estado, theta_g: float, phi_g: float = 0.0):
    """
    Calcula as probabilidades teóricas (P_+, P_-) de medição na direção (theta_g, phi_g).
    - Se estado is None: feixe não polarizado (rho = I/2), usando P(±) = Tr(rho P_±).
    - Caso contrário: estado puro |psi>, usando a regra de Born P(±) = |<±n|psi>|^2.
    """
    if estado is None:
        rho = matriz_densidade_nao_polarizada()
        proj_mais, proj_menos = projetores(theta_g, phi_g)
        p_mais = float(np.real(np.trace(rho @ proj_mais)))
        p_menos = float(np.real(np.trace(rho @ proj_menos)))
        return p_mais, p_menos

    mais, menos = auto_spin(theta_g, phi_g)
    amp_mais = np.vdot(mais, estado)
    amp_menos = np.vdot(menos, estado)
    p_mais = float(np.abs(amp_mais) ** 2)
    p_menos = float(np.abs(amp_menos) ** 2)
    return p_mais, p_menos


def incerteza_estatistica(p: float, n: int) -> float:
    """Incerteza padrão aproximada da frequência relativa: sigma_f = sqrt(p(1-p)/N)."""
    if n <= 0:
        return 0.0
    p = float(np.clip(p, 0.0, 1.0))
    return float(np.sqrt(p * (1.0 - p) / n))


def simular_filtro(n_entrada: int, p_mais: float, rng=None):
    """
    Simula a passagem de n_entrada partículas por um analisador de Stern-Gerlach.
    Garante estritamente a conservação: N_+ + N_- = N_entrada.
    """
    if n_entrada <= 0:
        return 0, 0
    if rng is None:
        rng = np.random.default_rng()
    p_mais = float(np.clip(p_mais, 0.0, 1.0))
    n_mais = int(rng.binomial(n_entrada, p_mais))
    n_menos = int(n_entrada - n_mais)
    return n_mais, n_menos


def calcular_teoria_experimento(
    modo_id: int,
    theta1: float,
    feixe1: str = "+",
    theta2: float = 90.0,
    feixe2: str = "+",
    theta3: float = 0.0,
):
    """
    Calcula analiticamente estados, probabilidades condicionais e probabilidades totais
    para os três modos experimentais (1, 2 ou 3 filtros), sem amostragem aleatória.
    """
    # Estágio 1: fonte não polarizada (rho = I/2) -> Filtro 1
    p1_mais, p1_menos = P(None, theta1)
    mais1, menos1 = auto_spin(theta1)
    estado1 = mais1 if feixe1 == "+" else menos1
    p1_sel = p1_mais if feixe1 == "+" else p1_menos

    if modo_id == 1:
        return {
            "modo_id": 1,
            "p1_mais": p1_mais,
            "p1_menos": p1_menos,
            "p_final_mais": p1_mais,
            "p_final_menos": p1_menos,
            "p_total_mais": p1_mais,
            "p_total_menos": p1_menos,
            "theta_anteparo": theta1,
            "nome_final": "Filtro 1",
            "estado1": estado1,
            "estado_entrada": None,
            "delta_theta": None,
        }

    # Estágio 2: |chi_1> -> Filtro 2
    p2_mais, p2_menos = P(estado1, theta2)
    mais2, menos2 = auto_spin(theta2)
    estado2 = mais2 if feixe2 == "+" else menos2
    p2_sel = p2_mais if feixe2 == "+" else p2_menos

    if modo_id == 2:
        delta_theta = abs(theta2 - theta1) if feixe1 == "+" else 180.0 - abs(theta2 - theta1)
        return {
            "modo_id": 2,
            "p1_mais": p1_mais,
            "p1_menos": p1_menos,
            "p1_sel": p1_sel,
            "p2_mais": p2_mais,
            "p2_menos": p2_menos,
            "p_final_mais": p2_mais,
            "p_final_menos": p2_menos,
            # Regra da cadeia: P(a, b) = P(a) * P(b|a)
            "p_total_mais": p1_sel * p2_mais,
            "p_total_menos": p1_sel * p2_menos,
            "theta_anteparo": theta2,
            "nome_final": "Filtro 2",
            "estado1": estado1,
            "estado_entrada": estado1,
            "delta_theta": delta_theta,
        }

    # Estágio 3: |chi_2> -> Filtro 3
    p3_mais, p3_menos = P(estado2, theta3)
    delta_theta = abs(theta3 - theta2) if feixe2 == "+" else 180.0 - abs(theta3 - theta2)

    return {
        "modo_id": 3,
        "p1_mais": p1_mais,
        "p1_menos": p1_menos,
        "p1_sel": p1_sel,
        "p2_mais": p2_mais,
        "p2_menos": p2_menos,
        "p2_sel": p2_sel,
        "p3_mais": p3_mais,
        "p3_menos": p3_menos,
        "p_final_mais": p3_mais,
        "p_final_menos": p3_menos,
        # Regra da cadeia: P(a, b, c) = P(a) * P(b|a) * P(c|a, b)
        "p_total_mais": p1_sel * p2_sel * p3_mais,
        "p_total_menos": p1_sel * p2_sel * p3_menos,
        "theta_anteparo": theta3,
        "nome_final": "Filtro 3",
        "estado1": estado1,
        "estado2": estado2,
        "estado_entrada": estado2,
        "delta_theta": delta_theta,
    }


def simular_experimento(
    n0: int,
    modo_id: int,
    theta1: float,
    feixe1: str = "+",
    theta2: float = 90.0,
    feixe2: str = "+",
    theta3: float = 0.0,
    rng=None,
):
    """
    Executa a simulação estocástica completa em cascata a partir de N_0 átomos
    emitidos pela fonte não polarizada, mantendo conservação em cada analisador.
    """
    if rng is None:
        rng = np.random.default_rng()

    teoria = calcular_teoria_experimento(modo_id, theta1, feixe1, theta2, feixe2, theta3)

    # Filtro 1 recebe N_0 da fonte não polarizada
    n1_mais, n1_menos = simular_filtro(n0, teoria["p1_mais"], rng)

    res = {
        **teoria,
        "n0": n0,
        "n1_mais": n1_mais,
        "n1_menos": n1_menos,
    }

    if modo_id == 1:
        n_ent_final = n0
        n_final_mais, n_final_menos = n1_mais, n1_menos
    else:
        n_ent_2 = n1_mais if feixe1 == "+" else n1_menos
        n_bloq_1 = n0 - n_ent_2
        n2_mais, n2_menos = simular_filtro(n_ent_2, teoria["p2_mais"], rng)
        res.update({
            "n_ent_2": n_ent_2,
            "n_bloq_1": n_bloq_1,
            "n2_mais": n2_mais,
            "n2_menos": n2_menos,
        })

        if modo_id == 2:
            n_ent_final = n_ent_2
            n_final_mais, n_final_menos = n2_mais, n2_menos
        else:
            n_ent_3 = n2_mais if feixe2 == "+" else n2_menos
            n_bloq_2 = n_ent_2 - n_ent_3
            n3_mais, n3_menos = simular_filtro(n_ent_3, teoria["p3_mais"], rng)
            res.update({
                "n_ent_3": n_ent_3,
                "n_bloq_2": n_bloq_2,
                "n3_mais": n3_mais,
                "n3_menos": n3_menos,
            })
            n_ent_final = n_ent_3
            n_final_mais, n_final_menos = n3_mais, n3_menos

    f_mais = (n_final_mais / n_ent_final) if n_ent_final > 0 else 0.0
    f_menos = (n_final_menos / n_ent_final) if n_ent_final > 0 else 0.0

    res.update({
        "n_entrada_final": n_ent_final,
        "n_final_mais": n_final_mais,
        "n_final_menos": n_final_menos,
        "f_mais": f_mais,
        "f_menos": f_menos,
        "desvio_mais": f_mais - teoria["p_final_mais"] if n_ent_final > 0 else 0.0,
        "desvio_menos": f_menos - teoria["p_final_menos"] if n_ent_final > 0 else 0.0,
        "sigma_f": incerteza_estatistica(teoria["p_final_mais"], n_ent_final),
    })
    return res


def executar_testes_validacao():
    """Valida os Casos A a F da especificação física e a conservação de partículas."""
    tol = 1e-12
    z_mais, _ = auto_spin(0)

    # Caso A — Analisadores paralelos (Delta theta = 0°)
    p_p, p_m = P(z_mais, 0)
    assert abs(p_p - 1.0) < tol and abs(p_m - 0.0) < tol, "Falha no Caso A"

    # Caso B — Analisadores perpendiculares (Delta theta = 90°)
    p_p, p_m = P(z_mais, 90)
    assert abs(p_p - 0.5) < tol and abs(p_m - 0.5) < tol, "Falha no Caso B"

    # Caso C — Analisadores antiparalelos (Delta theta = 180°)
    p_p, p_m = P(z_mais, 180)
    assert abs(p_p - 0.0) < tol and abs(p_m - 1.0) < tol, "Falha no Caso C"

    # Caso D — Sequência z -> x -> z (3 analisadores)
    t3 = calcular_teoria_experimento(3, theta1=0, feixe1="+", theta2=90, feixe2="+", theta3=0)
    assert abs(t3["p_final_mais"] - 0.5) < tol and abs(t3["p_final_menos"] - 0.5) < tol, "Falha no Caso D (condicional)"
    assert abs(t3["p_total_mais"] - 0.125) < tol, "Falha no Caso D (regra da cadeia: 1/2 * 1/2 * 1/2 = 1/8)"

    # Caso E — Fonte não polarizada (rho = I/2) em qualquer ângulo
    for ang in (0, 37, 90, 143, 180):
        p_p, p_m = P(None, ang)
        assert abs(p_p - 0.5) < tol and abs(p_m - 0.5) < tol, f"Falha no Caso E em {ang}°"

    # Caso F — Normalização, ortogonalidade e completeza dos projetores
    for ang in (0, 45, 90, 135, 180):
        m, n = auto_spin(ang)
        assert abs(np.vdot(m, m) - 1.0) < tol, "Falha na normalização |+n>"
        assert abs(np.vdot(n, n) - 1.0) < tol, "Falha na normalização |-n>"
        assert abs(np.vdot(m, n)) < tol, "Falha na ortogonalidade <+n|-n>"
        pm, pn = projetores(ang)
        assert np.allclose(pm @ pm, pm, atol=tol), "Falha idempotência P_+"
        assert np.allclose(pn @ pn, pn, atol=tol), "Falha idempotência P_-"
        assert np.allclose(pm @ pn, np.zeros((2, 2)), atol=tol), "Falha ortogonalidade P_+ P_-"
        assert np.allclose(pm + pn, IDENTIDADE, atol=tol), "Falha completeza P_+ + P_- = I"

    # Conservação de partículas nos 3 modos
    rng = np.random.default_rng(42)
    for m_id in (1, 2, 3):
        sim = simular_experimento(1000, m_id, 0, "+", 90, "+", 0, rng=rng)
        assert sim["n1_mais"] + sim["n1_menos"] == 1000
        assert sim["n_final_mais"] + sim["n_final_menos"] == sim["n_entrada_final"]

    print("Todos os testes físicos e matemáticos (Casos A–F + conservação) passaram com sucesso!")


if __name__ == "__main__":
    executar_testes_validacao()