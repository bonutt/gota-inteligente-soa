# Registro de uso de IA (prompts)

Conforme os combinados da Global Solution, a IA foi usada como **copiloto**: para gerar uma primeira versão do código, revisar e explicar. A equipe revisou o resultado e sabe explicar cada parte.

**Ferramenta:** Claude (Anthropic)

## Prompts utilizados

1. Envio do documento da GS (CitizenTech, 3º ano de Engenharia de Software) e da ideia da equipe (Gota Inteligente: ESP32 com sensor de solo, IA em Python, app React Native e painel C# WinForms), pedindo o desenvolvimento da entrega de **Arquitetura Orientada a Serviços (SOA) e Web Services**.
2. Requisitos tirados do enunciado e passados à IA: estruturação do domínio, conexão com banco de dados, migrações, chamadas a APIs REST e testes manuais com Insomnia; README com instruções de execução, descrição da solução e nomes dos integrantes.
3. Pedido para que a API se integrasse com as outras disciplinas: endpoint de telemetria para o ESP32, endpoint para a IA registrar recomendações, alertas para o app e um endpoint de painel regional para o WinForms.

## O que foi revisado pela equipe

- [ ] Regras de irrigação e limites (70% de chuva, 15% de solo crítico, faixas por cultura)
- [ ] Modelo de dados e migrações
- [ ] Execução da coleção do Insomnia na máquina da equipe
- [ ] Leitura e entendimento de cada camada (domain, services, routes)
