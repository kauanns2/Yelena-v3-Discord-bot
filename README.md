# Yelena V3

Plataforma modular de IA com identidade, personalidade, memória, raciocínio e segurança arquitetural.

## Arquitetura (16 módulos)

1. **Core & Kernel** — Fundação operacional
2. **Configuration** — Configuração centralizada
3. **Neural Web** — Teia de conexões e sinais
4. **Event Bus** — Comunicação por eventos
5. **Memory System** — Memória dinâmica
6. **Knowledge System** — Conhecimento estruturado
7. **Cognitive Context** — Contexto cognitivo seletivo
8. **Emotion & Affective State** — Estados afetivos
9. **Personality & Behavioral Identity** — Identidade comportamental
10. **Reasoning & Decision** — Raciocínio e decisões
11. **Conversation & Dialogue** — Gestão de conversas
12. **Language & Response Generation** — Geração linguística
13. **Action & Tool Execution** — Execução controlada de ações
14. **Security & Authorization** — Segurança e autorização
15. **Observability & Diagnostics** — Observabilidade
16. **Runtime & Orchestration** — Orquestração do sistema

## Princípio central

Não executar todos os módulos em toda mensagem.
O Runtime combina apenas os sistemas necessários conforme intenção, contexto, complexidade e risco.

### Liberdade vs Controle

```
PENSAR       → livre
ANALISAR     → livre
PLANEJAR     → livre
SUGERIR      → livre
DISCORDAR    → livre

EXECUTAR     → autorização
ACESSAR      → permissão
MODIFICAR    → controle
AÇÃO PERIGOSA → autorização
```

## Status

**Arquitetura principal completa (16/16)**

- [x] Módulos 1–16 implementados na fundação

## Uso rápido

```bash
pip install -r requirements.txt
pytest
```

```python
from app.runtime import YelenaRuntime

rt = YelenaRuntime()
rt.start()

print(rt.process("oi", user_id="kauanns2").text)

rt.stop()
```

## Próximos passos (fora da arquitetura principal)

- FEATURE / EXTENSION / PLUGIN / INTEGRATION
- Discord adapter
- Provider de IA real
- Persistência durável
- Voice
- Testes de integração amplos
