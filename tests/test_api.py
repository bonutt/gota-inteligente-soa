def test_health(client):
    assert client.get("/health").json()["status"] == "ok"


def test_crud_produtor(client):
    r = client.post("/api/v1/produtores", json={"nome": "João", "municipio": "Piedade", "uf": "SP"})
    assert r.status_code == 201
    pid = r.json()["id"]
    assert client.put(f"/api/v1/produtores/{pid}", json={"telefone": "(15) 90000-0000"}).json()["telefone"]
    assert client.get("/api/v1/produtores", params={"municipio": "Piedade"}).json()[0]["id"] == pid
    assert client.delete(f"/api/v1/produtores/{pid}").status_code == 204
    assert client.get(f"/api/v1/produtores/{pid}").status_code == 404


def test_validacao_de_entrada(client):
    r = client.post("/api/v1/produtores", json={"nome": "Jo", "municipio": "X", "uf": "sp"})
    assert r.status_code == 422


def test_faixa_de_umidade_invalida(client, cenario):
    r = client.put(f"/api/v1/propriedades/{cenario['propriedade']['id']}",
                   json={"umidade_minima_ideal": 90})
    assert r.status_code == 422


def test_codigo_de_dispositivo_duplicado(client, cenario):
    r = client.post("/api/v1/dispositivos", json={"codigo": "gota-teste",
                                                   "propriedade_id": cenario["propriedade"]["id"]})
    assert r.status_code == 409


def test_leitura_com_chuva_desliga_bomba_e_gera_alerta(client, cenario):
    r = client.post("/api/v1/leituras", json={
        "codigo_dispositivo": "gota-teste", "umidade_solo": 22, "temperatura_ar": 30,
        "umidade_ar": 45, "probabilidade_chuva": 90})
    assert r.status_code == 201
    corpo = r.json()
    assert corpo["ligar_bomba"] is False
    assert corpo["recomendacao"]["acao"] == "AGUARDAR_CHUVA"
    assert any(a["tipo"] == "CHUVA_PREVISTA" for a in corpo["alertas_gerados"])

    alertas = client.get("/api/v1/alertas", params={"lido": False}).json()
    assert client.patch(f"/api/v1/alertas/{alertas[0]['id']}/lido").json()["lido"] is True


def test_leitura_de_dispositivo_inexistente(client):
    r = client.post("/api/v1/leituras", json={
        "codigo_dispositivo": "nao-existe", "umidade_solo": 50, "temperatura_ar": 25,
        "umidade_ar": 50, "probabilidade_chuva": 0})
    assert r.status_code == 404


def test_dispositivo_desativado_nao_aceita_leitura(client, cenario):
    client.patch(f"/api/v1/dispositivos/{cenario['dispositivo']['id']}", json={"ativo": False})
    r = client.post("/api/v1/leituras", json={
        "codigo_dispositivo": "gota-teste", "umidade_solo": 50, "temperatura_ar": 25,
        "umidade_ar": 50, "probabilidade_chuva": 0})
    assert r.status_code == 422


def test_recomendacao_da_ia_vira_a_ultima(client, cenario):
    pid = cenario["propriedade"]["id"]
    r = client.post("/api/v1/recomendacoes", json={
        "propriedade_id": pid, "acao": "AGUARDAR_CHUVA", "origem": "IA",
        "motivo": "Modelo prevê chuva em 2h", "confianca": 0.9})
    assert r.status_code == 201
    ultima = client.get(f"/api/v1/recomendacoes/ultima/{pid}").json()
    assert ultima["origem"] == "IA"


def test_painel_regional(client, cenario):
    client.post("/api/v1/leituras", json={
        "codigo_dispositivo": "gota-teste", "umidade_solo": 10, "temperatura_ar": 38,
        "umidade_ar": 20, "probabilidade_chuva": 0})
    painel = client.get("/api/v1/painel/estresse-hidrico", params={"municipio": "Ibiúna"}).json()
    assert painel["resumo"]["total_propriedades"] == 1
    assert painel["resumo"]["propriedades_criticas"] == 1
    assert painel["propriedades"][0]["nivel_estresse"] == "CRITICO"
