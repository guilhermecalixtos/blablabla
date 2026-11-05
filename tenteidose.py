# ================================================================
# ESTIMATIVA DE DOSE POR RAIOS X EM SILÍCIO
#
# COMPARAÇÃO ENTRE:
#
#   MÉTODO 1 -> Fluência x energia x coeficiente de absorção
#   D = Phi * E * (mu_en / rho)

#   MÉTODO 2 -> Energia efetivamente absorvida em uma espessura t
#   E_abs = E_incidente * [1 - exp(-mu*t)]
#   D = E_abs / m
#
#
# OBJETIVO:
# ----------
# Investigar a dose produzida pelo pulso de raios X descrito no artigo e verificar quais condições são necessárias 
# para obter aproximadamente: 70 krad(Si) = 700 Gy(Si)
#
#
# Pelo o que eu li do ICRU Report 85, a dose absorvida é definida como: D = dE / dm --> a relação entre 
# a energia média absorvida e a massa do material.
# ------------------------
# A partir disso, o conceito de fluência de fótons é introduzido: Phi = dN / dA --> número de fótons por unidade de área.  
# E a partir disso, o conceito de coeficiente de absorção de energia: mu_en/rho --> usado para estimar a dose absorvida em um material.
# e, para fótons, sob as hipóteses apropriadas:
# D ≈ Phi * E * (mu_en/rho)
# 
# A chave para calcular a dose absorvida é o coeficiente de absorção de energia, que depende do material e da energia dos fótons.
# E também os parametros de feixe, como o número de fótons, a energia dos fótons, a duração do pulso e a área do feixe. (Phi e E)
# NIST: mu/rho e mu_en/rho para interação de fótons com o silício.
#
# ================================================================
# Obs: Coloquei as variaveis em ingles por que podia dar conflito com caracteres especiais do português (ç, ã....)
# ================================================================
# 1. BIBLIOTECAS
# ================================================================

import numpy as np
import matplotlib.pyplot as plt


# ================================================================
# 2. CONSTANTES FÍSICAS
# ================================================================

# Carga elementar.

eV_to_J = 1.602176634e-19

# Densidade do silício--> rho_Si = 2.33 g/cm³

rho_Si = 2330.0                       # [kg/m³]

# ================================================================
# 3. PARÂMETROS DO FEIXE
# ================================================================

# Número de fótons por pulso informado no artigo.

N_photons = 2e8                     # [fótons/pulso] 

# Temporização da exposição.
pulse_duration_s = 80e-12 # [s] duração de cada pulso (80 ps)
pulse_period_s = 1.0  # [s] intervalo entre inícios de pulsos --> 1 pulso por segundo
irradiation_time_s = 2.0  # [s] duração total da exposição (Não está no artigo, utilizei somente para o cálculo da dose acumulada)


# Energia dos fótons.

E_photon_keV = 15   # [keV]

# Conversão:

E_photon_J = ( E_photon_keV * 1.0e3* eV_to_J)


# Energia total transportada pelos fótons incidentes--> E_inc = N * E_photon_J

E_incident = (N_photons* E_photon_J)

# O primeiro pulso começa em t=0. Se a exposição terminar durante o último pulso, considera-se a fração do pulso efetivamente aplicada.
if pulse_duration_s <= 0 or pulse_period_s <= 0 or irradiation_time_s < 0:
    raise ValueError(
        "pulse_duration_s e pulse_period_s devem ser positivos; "
        "irradiation_time_s não pode ser negativo."
    )

if pulse_duration_s > pulse_period_s:
    raise ValueError(
        "pulse_duration_s não pode ser maior que pulse_period_s "
        "neste modelo de pulsos não sobrepostos."
    )

N_pulses_total = int(np.ceil(irradiation_time_s / pulse_period_s))
pulse_word = "pulso" if N_pulses_total == 1 else "pulsos"
if N_pulses_total > 0:
    last_pulse_start_s = (N_pulses_total - 1) * pulse_period_s
    last_pulse_fraction = min(1.0,max(0.0, (irradiation_time_s - last_pulse_start_s) / pulse_duration_s))
    N_pulses_equivalent = (N_pulses_total - 1) + last_pulse_fraction
else:
    N_pulses_equivalent = 0.0

pulse_repetition_rate_Hz = 1.0 / pulse_period_s
duty_cycle = pulse_duration_s / pulse_period_s


print("\n====================================================")
print("               PARÂMETROS DO FEIXE")
print("====================================================")

print(f"Número de fótons       = {N_photons:.4e}")
print(f"Energia por fóton      = {E_photon_J:.4e} J")
print(f"Energia total incidente = {E_incident:.4e} J")
print(f"Duração do pulso       = {pulse_duration_s:.4e} s")
print(f"Período entre pulsos   = {pulse_period_s:.4e} s")
print(f"Frequência de repetição = {pulse_repetition_rate_Hz:.4e} Hz")
print(f"Duty cycle             = {duty_cycle:.4e} ({duty_cycle*100:.4e}%)")
print(f"Tempo de irradiação    = {irradiation_time_s:.4e} s")
print(f"Número de {pulse_word:<8} = {N_pulses_total}")


# ================================================================
# 4. DIMENSÃO DO FEIXE
# ================================================================
#
# O artigo considera um feixe com aproximadamente:
# FWHM = 25 micrometros
# Para o modelo gaussiano, vamos considerar:
# FWHM_x = FWHM_y



FWHM = 25.0e-6 # [m]

FWHM_x = FWHM
FWHM_y = FWHM


# ================================================================
# 5. FLUÊNCIA GAUSSIANA
# ================================================================
# distribuição transversal do número de fótons por uma distribuição gaussiana 2D:
# Phi(x,y) = N * 4 ln(2)/pi * FWHM_x * FWHM_y * exp[-4 ln(2) * (x²/FWHM_x² + y²/FWHM_y²)]
# Essa normalização garante que a integral integral Phi(x,y) dx dy = N
# acho que ao integrar a fluência em toda a área transversal, temos o número total de fótons do pulso.
#


def photon_fluence(x, y):

    normalization = (4.0* np.log(2.0)/ (np.pi* FWHM_x* FWHM_y))

    exponent = (-4.0* np.log(2.0) * (x**2 / FWHM_x**2+ y**2 / FWHM_y**2))

    return (N_photons* normalization * np.exp(exponent))


# Fluência no centro do feixe.

Phi_0 = photon_fluence(0.0, 0.0)


print("\n====================================================")
print("                  FLUÊNCIA")
print("====================================================")

print(f"FWHM = {FWHM*1e6:.2f} µm")

print(
    f"Fluência no centro = "
    f"{Phi_0:.4e} fótons/m²"
)


# ================================================================
# 6. COEFICIENTES DO NIST
# ================================================================
#
# A partir do NIST/XCOM precisamos de dois coeficientes:
#
#
# (1) COEFICIENTE MÁSSICO DE ATENUAÇÃO (mu/rho)
# usado para determinar: mu = (mu/rho)*rho
#
#
# (2) COEFICIENTE MÁSSICO DE ABSORÇÃO DE ENERGIA (mu_en/rho)
# usado diretamente na estimativa: D = Phi * E * (mu_en/rho)
# ---------------------------------------------------------------
#
# Os valores abaixo devem ser preenchidos com os valores da tabela do NIST para a condição que oce quer (usei artigo):
#       MATERIAL = Si
#       ENERGIA  = 15 keV



# >>> INSIRA AQUI O VALOR DO NIST <<<

mu_rho_cm2_g = 1.034e01

# >>> INSIRA AQUI O VALOR DO NIST <<<

mu_en_rho_cm2_g = 9.794 


# ================================================================
# 7. CONVERSÃO DOS COEFICIENTES
# ================================================================
#
# Conversão:
#1 cm²/g = 0.1 m²/kg




if (
    mu_rho_cm2_g is None
    or
    mu_en_rho_cm2_g is None
):

    print("\n====================================================")
    print("              FALTA DADO")
    print("====================================================")

    print(
        "\nInsira os valores de:"
    )

    print(
        "mu/rho"
        " e "
        "mu_en/rho"
        " em cm²/g."
    )

    print(
        "\nO script foi encerrado antes "
        "dos cálculos de dose."
    )

    raise SystemExit


mu_rho = (mu_rho_cm2_g * 0.1)


mu_en_rho = (mu_en_rho_cm2_g* 0.1)


# ================================================================
# 8. COEFICIENTE LINEAR DE ATENUAÇÃO
# ================================================================
#
# O coeficiente mássico: mu/rho  [m²/kg]--> Multiplica pela densidade--> mu [1/m]--> mu = (mu/rho)*rho
#


mu = (mu_rho * rho_Si)


print("\n====================================================")
print("             COEFICIENTES DE INTERAÇÃO")
print("====================================================")

print(
    f"mu/rho = "
    f"{mu_rho:.5e} m²/kg"
)

print(
    f"mu_en/rho = "
    f"{mu_en_rho:.5e} m²/kg"
)

print(
    f"mu = "
    f"{mu:.5e} 1/m"
)


# ================================================================
# 9. COMPRIMENTO DE ATENUAÇÃO
# ================================================================
#
# Uma quantidade útil para interpretar fisicamente o resultado é o comprimento de atenuação:
# L = 1/mu
# Depois de percorrer essa distância: I/I0 = exp(-1) = 0.368 Portanto, aproximadamente 63.2% da intensidade inicial sofreu 
# interação segundo a lei de atenuação primária.
#
attenuation_length = 1.0 / mu


print("\n====================================================")
print("          COMPRIMENTO DE ATENUAÇÃO")
print("====================================================")

print(
    f"L = 1/mu = "
    f"{attenuation_length*1e6:.3f} µm"
)


# ================================================================
# 10. MÉTODO 1 — DOSE USANDO mu_en/rho
# ================================================================
#
# A primeira estimativa é: D = Phi * E * (mu_en/rho) --> calcular essa dose no centro do feixe.
#
#
# Unidades:
# Phi  --> fótons/m² / E --> J/fóton / mu_en/rho --> m²/kg

# Logo:fótons/m² *J/fóton * m²/kg= J/kg = Gy


D_method1_Gy = (Phi_0* E_photon_J* mu_en_rho)


D_method1_krad = (D_method1_Gy/ 10.0)

# Para pulsos iguais no mesmo ponto, as doses se somam linearmente.
# Este cálculo não inclui efeitos de annealing durante a exposição.
D_TID_method1_Gy = N_pulses_equivalent * D_method1_Gy
D_TID_method1_krad = D_TID_method1_Gy / 10.0
D_rate_during_pulse_Gy_s = D_method1_Gy / pulse_duration_s
D_rate_average_Gy_s = (
    D_TID_method1_Gy / irradiation_time_s
    if irradiation_time_s > 0
    else 0.0
)


print("\n====================================================")
print("        MÉTODO 1 — ICRU / mu_en")
print("====================================================")

print(
f"Dose no centro = "
    f"{D_method1_Gy:.5e} Gy"
)

print(
    f"Dose no centro = "
    f"{D_method1_krad:.5e} krad(Si)"
)

print(
    f"Dose acumulada no centro ({N_pulses_total} {pulse_word}) = "
    f"{D_TID_method1_Gy:.5e} Gy "
    f"({D_TID_method1_krad:.5e} krad(Si))"
)

print(
    f"Taxa de dose média na exposição = "
    f"{D_rate_average_Gy_s:.5e} Gy/s"
)



# ================================================================
# 11. DOSE REPORTADA PELO ARTIGO
# ================================================================
#
# O artigo reporta aproximadamente: 70 krad(Si) --> 70 krad = 700 Gy
#


D_target_krad = 70.0

D_target_Gy = (D_target_krad* 10.0)


print("\n====================================================")
print("             VALOR DE REFERÊNCIA")
print("====================================================")

print(
    f"Dose do artigo = "
    f"{D_target_Gy:.2f} Gy"
)

print(
    f"Dose do artigo = "
    f"{D_target_krad:.2f} krad(Si)"
)


# ================================================================
# 12. MÉTODO 2 — ENERGIA ABSORVIDA
# ================================================================
#
# Agora vamos considerar explicitamente uma camada de silício de espessura t.
#
#
# Pela lei de Beer-Lambert: I(t) = I0 * exp(-mu*t) --> A fração do feixe primário que interage dentro da espessura t é: f = 1 - exp(-mu*t)
# Assim, uma primeira estimativa da energia depositada seria --> E_abs =E_incidente *[1 - exp(-mu*t)]
#
# acho que isso é uma estimativa de absorção/remoção do feixe primário. 
# Ela não é rigorosamente equivalente ao formalismo de mu_en/rho do ICRU, pois não descreve explicitamente o transporte
# dos elétrons secundários. Por isso que quis comparar os dois métodos.
#


def absorbed_energy(t):

    fraction_absorbed = (1.0-np.exp(-mu * t))

    E_abs = (E_incident* fraction_absorbed)

    return E_abs


# ================================================================
# 13. MASSA DE SILÍCIO
# ================================================================
#
# Para transformar energia em dose precisamos da massa:
#
#
#       D = E_abs / m
#
#
# A massa de uma camada uniforme é: m = rho * V ; e V = A*t --> m = rho*A*t
#
# qual área A deve ser considerada?
#
#
# Não sei então vamos considerar duas possibilidades kk:
#
#
# A) Área equivalente baseada no FWHM
#
# B) Área efetiva contendo uma determinada fração da energia
#
#
# Primeiro faremos uma aproximação usando:
#
#       A = pi*(FWHM/2)^2
#
#


A_FWHM = (np.pi* (FWHM / 2.0)**2)


print("\n====================================================")
print("                 ÁREA")
print("====================================================")

print(
    f"Área circular baseada no FWHM = "
    f"{A_FWHM:.5e} m²"
)


# ================================================================
# 14. FUNÇÃO PARA CALCULAR DOSE DO MÉTODO 2
# ================================================================


def dose_method2(t):

    # Energia absorvida na espessura t.

    E_abs = absorbed_energy(t)

    # Volume da camada.

    volume = (A_FWHM* t)

    # Massa correspondente.

    mass = (rho_Si* volume)

    # Dose:D = E_abs/m

    D = (E_abs/ mass)
    return D


# ================================================================
# 15. VARREDURA DE ESPESSURA
# ================================================================
#
#  queria saber qual que é a espessura efetiva seria necessária para que o cálculo fornecesse 700 Gy?
#
#
# Variar de 0.01 µm em 0.01 µm até 1000 em escala logarítmica.

thicknesses = np.logspace( -8,-3,500)


dose_method2_values = np.array(
    [
        dose_method2(t)
        for t in thicknesses
    ]
)


# ================================================================
# 16. ENCONTRANDO A ESPESSURA QUE MAIS SE APROXIMA DE 700 Gy
# ================================================================


index_best = np.argmin(np.abs(dose_method2_values-D_target_Gy))

t_best = (thicknesses[index_best])


D_best = (dose_method2_values[index_best])

# D_best corresponde a um pulso; escale pelo número equivalente de pulsos.
D_TID_method2_Gy = N_pulses_equivalent * D_best
D_TID_method2_krad = D_TID_method2_Gy / 10.0


# Massa correspondente.

mass_best = (rho_Si* A_FWHM* t_best)


# Energia absorvida correspondente.

E_abs_best = (absorbed_energy(t_best))


print("\n====================================================")
print("        ESPESSURA EFETIVA PARA 700 Gy")
print("====================================================")

print(
    f"Espessura = "
    f"{t_best*1e6:.5e} µm"
)

print(
    f"Dose calculada = "
    f"{D_best:.5e} Gy"
)

print(
    f"Massa efetiva = "
    f"{mass_best:.5e} kg"
)

print(
    f"Massa efetiva = "
    f"{mass_best*1e9:.5e} mg"
)

print(
    f"Energia absorvida = "
    f"{E_abs_best:.5e} J"
)


# ================================================================
# 17. FRAÇÃO DA ENERGIA ABSORVIDA
# ================================================================
#
# Calculamos quanto da energia incidente foi absorvida/interagiu na espessura encontrada: f = 1 - exp(-mu*t)
#


fraction_best = (1.0-np.exp(-mu * t_best))


print(
    f"Fração absorvida = "
    f"{fraction_best*100:.5e} %"
)


# ================================================================
# 18. MASSA NECESSÁRIA PARA 700 Gy
# ================================================================
#
# Outra maneira interessante de olhar para o problema: D = E_abs/m --> m = E_abs/D
# Com energia absorvida --> massa necessária para produzir 700 Gy.
#
# Como limite superior, podemos imaginar que toda a energia do
# pulso fosse depositada:
#
# m = E_incidente / D_target


mass_if_all_energy_absorbed = (E_incident/ D_target_Gy)


print("\n====================================================")
print("       MASSA SE TODA ENERGIA FOSSE ABSORVIDA")
print("====================================================")

print(
    f"Massa equivalente = "
    f"{mass_if_all_energy_absorbed:.5e} kg"
)

print(
    f"Massa equivalente = "
    f"{mass_if_all_energy_absorbed*1e9:.5e} mg"
)


# ================================================================
# 19. VOLUME EQUIVALENTE
# ================================================================
#
# Usando: m = rho*V --> V = m/rho


volume_equivalent = (mass_if_all_energy_absorbed/rho_Si)


print(
    f"Volume equivalente = "
    f"{volume_equivalent:.5e} m³"
)


# ================================================================
# 20. GRÁFICO — DOSE x ESPESSURA
# ================================================================


plt.figure(figsize=(8, 6))

plt.loglog(thicknesses * 1e6,dose_method2_values)

plt.axhline(D_target_Gy,linestyle="--",label="70 krad(Si) = 700 Gy")

plt.axvline(t_best * 1e6,linestyle="--",label=f"t = {t_best*1e6:.3g} µm")

plt.xlabel("Espessura de Si [um]")

plt.ylabel("Dose [Gy(Si)]")

plt.title("Dose estimada em função da espessura de Si")

plt.grid(True,which="both")

plt.legend()

plt.tight_layout()


# ================================================================
# 21. DISTRIBUIÇÃO GAUSSIANA DA DOSE
# ================================================================
#
# Tentei calcular a dose pelo MÉTODO 1 em toda a seção transversal pra ver msm.
# O valor máximo deve ocorrer no centro.


n_points = 1001


x = np.linspace(-3.0 * FWHM,3.0 * FWHM,n_points)


y = np.linspace(-3.0 * FWHM,3.0 * FWHM,n_points)


X, Y = np.meshgrid(x,y)


Phi_xy = photon_fluence(X,Y)


# ================================================================
# 22. DISTRIBUIÇÃO TRANSVERSAL DO FEIXE
# ================================================================


plt.figure(figsize=(8, 6))

plt.contourf(X * 1e6,Y * 1e6,Phi_xy,levels=50)

plt.xlabel("x [µm]")

plt.ylabel("y [μm]")

plt.title("Distribuição transversal do feixe (fluência de fótons)")

plt.colorbar(label="Fluência [fótons/m² por pulso]")

plt.axis("equal")

plt.tight_layout()


# Dose pelo método 1.

D_xy = (Phi_xy* E_photon_J* mu_en_rho)
D_TID_xy = N_pulses_equivalent * D_xy


# ================================================================
# 23. PLOT DA DISTRIBUIÇÃO DE DOSE
# ================================================================


plt.figure(figsize=(8, 6))

plt.contourf(X * 1e6,Y * 1e6,D_xy,levels=50)

plt.xlabel("x [µm]")

plt.ylabel("y [µm]")

plt.title("Distribuição transversal da dose por pulso")

plt.colorbar(label="Dose por pulso [Gy(Si)]")

plt.axis("equal")

plt.tight_layout()


# ================================================================
# 24. DISTRIBUIÇÃO TRANSVERSAL DA DOSE ACUMULADA (TID)
# ================================================================


plt.figure(figsize=(8, 6))

plt.contourf(X * 1e6,Y * 1e6,D_TID_xy,levels=50)

plt.xlabel("x [µm]")

plt.ylabel("y [µm]")

plt.title(f"Dose acumulada (TID) para {N_pulses_total} {pulse_word}")

plt.colorbar(
    label="Dose acumulada [Gy(Si)]"
)

plt.axis("equal")

plt.tight_layout()


# ================================================================
# 25. COMPARAÇÃO ENTRE MÉTODOS
# ================================================================
#
# principais resultados.
#


print("\n")
print("====================================================")
print("                  RESUMO")
print("====================================================")

print(
    f"Dose alvo do artigo:"
    f" {D_target_krad:.2f} krad(Si)"
)

print(
    f"                         "
    f"= {D_target_Gy:.2f} Gy"
)

print(
    f"\nMétodo 1:"
)

print(f"  D = Phi*E*(mu_en/rho)")

print(
    f"  D = {D_method1_Gy:.5e} Gy"
)

print(
    f"  D = {D_method1_krad:.5e} krad(Si)"
)

print(
    f"  TID após {N_pulses_total} {pulse_word} = "
    f"{D_TID_method1_Gy:.5e} Gy "
    f"({D_TID_method1_krad:.5e} krad(Si))"
)

print(
    f"\nMétodo 2:"
)

print(
    f"  Espessura que mais se aproxima:"
)

print(
    f"  t = {t_best*1e6:.5e} µm"
)

print(
    f"  D = {D_best:.5e} Gy"
)

print(
    f"  m = {mass_best:.5e} kg"
)

print(
    f"  E_abs = {E_abs_best:.5e} J"
)

print(
    f"  TID após {N_pulses_total} {pulse_word} = "
    f"{D_TID_method2_Gy:.5e} Gy "
    f"({D_TID_method2_krad:.5e} krad(Si))"
)

print(
    "\n===================================================="
)

plt.show()