"""Gera a coleção do Insomnia e roda todas as requisições contra a API local,
registrando as respostas em docs/evidencias/testes-manuais.md.

Uso: com a API rodando (uvicorn) em banco recém-criado + seed:
    python scripts/gerar_evidencias.py
"""
import json, httpx, textwrap
from datetime import datetime, timezone

B = "http://127.0.0.1:8000"
# (pasta, nome, método, caminho, corpo, status esperado)
R = [
 ("0. Status","Health check","GET","/health",None,200),
 ("1. Produtores","Listar produtores","GET","/api/v1/produtores",None,200),
 ("1. Produtores","Filtrar por município","GET","/api/v1/produtores?municipio=Ibiúna",None,200),
 ("1. Produtores","Cadastrar produtor","POST","/api/v1/produtores",{"nome":"Carlos Henrique (simulado)","telefone":"(15) 90000-0010","municipio":"Piedade","uf":"SP"},201),
 ("1. Produtores","Buscar produtor por id","GET","/api/v1/produtores/4",None,200),
 ("1. Produtores","Atualizar produtor","PUT","/api/v1/produtores/4",{"telefone":"(15) 90000-0099"},200),
 ("1. Produtores","ERRO - dados inválidos (422)","POST","/api/v1/produtores",{"nome":"Jo","municipio":"X","uf":"sp"},422),
 ("1. Produtores","ERRO - produtor inexistente (404)","GET","/api/v1/produtores/9999",None,404),
 ("2. Propriedades","Listar propriedades","GET","/api/v1/propriedades",None,200),
 ("2. Propriedades","Cadastrar propriedade","POST","/api/v1/propriedades",{"produtor_id":4,"nome":"Sítio Recanto Verde","municipio":"Piedade","latitude":-23.70,"longitude":-47.41,"area_hectares":3.0,"cultura":"Pimentão","umidade_minima_ideal":35,"umidade_maxima_ideal":70},201),
 ("2. Propriedades","Atualizar propriedade","PUT","/api/v1/propriedades/5",{"cultura":"Pimentão orgânico"},200),
 ("2. Propriedades","ERRO - faixa de umidade inválida (422)","PUT","/api/v1/propriedades/5",{"umidade_minima_ideal":90},422),
 ("3. Dispositivos (ESP32)","Cadastrar dispositivo","POST","/api/v1/dispositivos",{"codigo":"gota-005","propriedade_id":5,"descricao":"Kit ESP32 - Sítio Recanto Verde"},201),
 ("3. Dispositivos (ESP32)","ERRO - código duplicado (409)","POST","/api/v1/dispositivos",{"codigo":"gota-005","propriedade_id":5},409),
 ("3. Dispositivos (ESP32)","Listar dispositivos da propriedade","GET","/api/v1/dispositivos?propriedade_id=5",None,200),
 ("4. Leituras (telemetria do ESP32)","Solo seco + 90% de chuva = AGUARDAR_CHUVA","POST","/api/v1/leituras",{"codigo_dispositivo":"gota-005","umidade_solo":22,"temperatura_ar":30,"umidade_ar":45,"probabilidade_chuva":90,"bomba_ligada":False},201),
 ("4. Leituras (telemetria do ESP32)","Solo seco + sem chuva = IRRIGAR","POST","/api/v1/leituras",{"codigo_dispositivo":"gota-005","umidade_solo":24,"temperatura_ar":31,"umidade_ar":40,"probabilidade_chuva":10,"bomba_ligada":False},201),
 ("4. Leituras (telemetria do ESP32)","Solo crítico = IRRIGAR mesmo com chuva","POST","/api/v1/leituras",{"codigo_dispositivo":"gota-005","umidade_solo":10,"temperatura_ar":36,"umidade_ar":25,"probabilidade_chuva":85,"bomba_ligada":False},201),
 ("4. Leituras (telemetria do ESP32)","Solo úmido = NAO_IRRIGAR","POST","/api/v1/leituras",{"codigo_dispositivo":"gota-005","umidade_solo":72,"temperatura_ar":24,"umidade_ar":70,"probabilidade_chuva":20,"bomba_ligada":True},201),
 ("4. Leituras (telemetria do ESP32)","ERRO - dispositivo não cadastrado (404)","POST","/api/v1/leituras",{"codigo_dispositivo":"gota-999","umidade_solo":50,"temperatura_ar":25,"umidade_ar":50,"probabilidade_chuva":0},404),
 ("4. Leituras (telemetria do ESP32)","ERRO - umidade acima de 100% (422)","POST","/api/v1/leituras",{"codigo_dispositivo":"gota-005","umidade_solo":150,"temperatura_ar":25,"umidade_ar":50,"probabilidade_chuva":0},422),
 ("4. Leituras (telemetria do ESP32)","Histórico de leituras da propriedade","GET","/api/v1/leituras?propriedade_id=5&limite=10",None,200),
 ("5. Recomendações","Registrar decisão da IA (Python)","POST","/api/v1/recomendacoes",{"propriedade_id":5,"acao":"AGUARDAR_CHUVA","origem":"IA","motivo":"Modelo de ML prevê 90% de chuva nas próximas 2h. Não ligar a bomba.","confianca":0.87},201),
 ("5. Recomendações","Última recomendação da propriedade","GET","/api/v1/recomendacoes/ultima/5",None,200),
 ("5. Recomendações","Histórico de recomendações","GET","/api/v1/recomendacoes?propriedade_id=5",None,200),
 ("6. Alertas (app do agricultor)","Alertas não lidos da propriedade","GET","/api/v1/alertas?propriedade_id=5&lido=false",None,200),
 ("6. Alertas (app do agricultor)","Alertas de severidade ALTA","GET","/api/v1/alertas?severidade=ALTA",None,200),
 ("6. Alertas (app do agricultor)","Marcar alerta como lido","PATCH","/api/v1/alertas/1/lido",None,200),
 ("7. Painel regional (C# WinForms)","Estresse hídrico - todas as propriedades","GET","/api/v1/painel/estresse-hidrico",None,200),
 ("7. Painel regional (C# WinForms)","Estresse hídrico - por município","GET","/api/v1/painel/estresse-hidrico?municipio=Piedade",None,200),
 ("8. Limpeza","Remover dispositivo","DELETE","/api/v1/dispositivos/5",None,204),
 ("8. Limpeza","Remover propriedade","DELETE","/api/v1/propriedades/5",None,204),
 ("8. Limpeza","Remover produtor","DELETE","/api/v1/produtores/4",None,204),
]

# ---------- Insomnia v4 export ----------
res = [{"_id":"wrk_gota","_type":"workspace","name":"Gota Inteligente API","description":"Testes manuais da API da Gota Inteligente (FIAP GS 2026.2 - SOA)","scope":"collection"},
       {"_id":"env_base","_type":"environment","parentId":"wrk_gota","name":"Base Environment","data":{}},
       {"_id":"env_local","_type":"environment","parentId":"env_base","name":"Local","data":{"base_url":"http://localhost:8000"}}]
pastas = {}
for i,(pasta,nome,met,cam,corpo,st) in enumerate(R):
    if pasta not in pastas:
        pid=f"fld_{len(pastas)}"; pastas[pasta]=pid
        res.append({"_id":pid,"_type":"request_group","parentId":"wrk_gota","name":pasta,"metaSortKey":len(pastas)})
    req={"_id":f"req_{i:02d}","_type":"request","parentId":pastas[pasta],"name":nome,"method":met,
         "url":"{{ _.base_url }}"+cam,"metaSortKey":i,"description":f"Status esperado: {st}",
         "headers":[],"body":{}}
    if corpo is not None:
        req["headers"]=[{"name":"Content-Type","value":"application/json"}]
        req["body"]={"mimeType":"application/json","text":json.dumps(corpo,ensure_ascii=False,indent=2)}
    res.append(req)
exp={"_type":"export","__export_format":4,"__export_date":datetime.now(timezone.utc).isoformat(),"__export_source":"gota-inteligente","resources":res}
json.dump(exp,open("insomnia/gota-inteligente-insomnia.json","w"),ensure_ascii=False,indent=2)

# ---------- Execução real + evidências ----------
linhas=["# Evidências dos testes manuais","",
 "Execução da coleção `insomnia/gota-inteligente-insomnia.json`, na ordem, contra a API rodando localmente",
 "com o banco criado pelas migrações (`alembic upgrade head`) e populado pelo seed (`python -m scripts.seed`).","",
 f"Data da execução: {datetime.now().strftime('%d/%m/%Y %H:%M')}","",
 "| # | Pasta | Requisição | Esperado | Obtido | OK |","|---|---|---|---|---|---|"]
detalhes=[]; ok_total=0
with httpx.Client(base_url=B) as c:
    for i,(pasta,nome,met,cam,corpo,st) in enumerate(R):
        r=c.request(met,cam,json=corpo)
        ok=r.status_code==st; ok_total+=ok
        linhas.append(f"| {i+1} | {pasta} | {met} `{cam}` — {nome} | {st} | {r.status_code} | {'✅' if ok else '❌'} |")
        try: txt=json.dumps(r.json(),ensure_ascii=False,indent=2)
        except Exception: txt="(sem corpo)"
        if txt.count("\n")>45: txt="\n".join(txt.split("\n")[:45])+"\n  ... (resposta cortada)"
        d=[f"### {i+1}. {nome}",f"`{met} {cam}` → **{r.status_code}**",""]
        if corpo is not None: d+=["Corpo enviado:","```json",json.dumps(corpo,ensure_ascii=False,indent=2),"```"]
        d+=["Resposta:","```json",txt,"```",""]
        detalhes+=d
linhas+=["",f"**Resultado: {ok_total}/{len(R)} requisições com o status esperado.**","","---","","## Detalhe de cada requisição",""]+detalhes
open("docs/evidencias/testes-manuais.md","w").write("\n".join(linhas))
print(ok_total,"/",len(R))
