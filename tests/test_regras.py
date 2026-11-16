from app.domain.enums import AcaoIrrigacao, NivelEstresse
from app.domain.regras import calcular_indice_estresse, classificar_estresse, decidir_irrigacao, litros_por_irrigacao


def test_solo_seco_com_chuva_prevista_aguarda_a_chuva():
    d = decidir_irrigacao(25, 28, 50, 90, 35, 70)
    assert d.acao == AcaoIrrigacao.AGUARDAR_CHUVA


def test_solo_seco_sem_chuva_irriga():
    assert decidir_irrigacao(25, 28, 50, 10, 35, 70).acao == AcaoIrrigacao.IRRIGAR


def test_solo_critico_irriga_mesmo_com_chuva():
    assert decidir_irrigacao(10, 30, 40, 95, 35, 70).acao == AcaoIrrigacao.IRRIGAR


def test_solo_umido_nao_irriga():
    assert decidir_irrigacao(80, 30, 40, 0, 35, 70).acao == AcaoIrrigacao.NAO_IRRIGAR


def test_calor_e_ar_seco_irrigacao_preventiva():
    assert decidir_irrigacao(40, 34, 30, 10, 35, 70).acao == AcaoIrrigacao.IRRIGAR


def test_indice_de_estresse_limites():
    assert calcular_indice_estresse(100, 20, 80, 70) == 0
    assert calcular_indice_estresse(0, 45, 0, 70) == 100
    assert classificar_estresse(75) == NivelEstresse.CRITICO
    assert classificar_estresse(50) == NivelEstresse.ATENCAO
    assert classificar_estresse(10) == NivelEstresse.NORMAL
    assert classificar_estresse(None) == NivelEstresse.SEM_DADOS


def test_litros_por_irrigacao_um_hectare():
    # 1 ha × 5 mm = 50 m³ = 50.000 litros
    assert litros_por_irrigacao(1) == 50_000
