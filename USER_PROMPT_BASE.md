 🎯 Prompt Template Recomendado

  Quando você quiser que um agente use as APIs, use este prompt:

  Tarefa: [Sua tarefa aqui]

  IMPORTANTE: Use as APIs Python do ForgeBase (v0.1.3):
  - Leia AI_AGENT_QUICK_START.md para referência rápida
  - Import: from forgebase.dev.api import QualityChecker, ScaffoldGenerator, ComponentDiscovery, TestRunner
  - Todas APIs retornam dataclasses estruturados
  - Use error['code'] para determinar ações de correção
  - Exemplos em examples/ai_agent_usage.py

  Workflow:
  1. Use ComponentDiscovery para entender o código existente
  2. Use ScaffoldGenerator para gerar código novo
  3. Use QualityChecker para verificar qualidade
  4. Use TestRunner para validar testes
