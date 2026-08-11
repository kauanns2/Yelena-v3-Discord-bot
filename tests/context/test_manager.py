"""Testes do Context Manager."""

from app.context import ContextManager
from app.context.models.query import ContextQuery
from app.context.constants import ContextItemSource
from app.memory import MemoryManager
from app.knowledge import KnowledgeManager


def test_build_with_situation_only():
    ctx = ContextManager()
    ctx.start()
    result = ctx.build_from_text("oi")
    assert result.item_count >= 1
    assert any(i.source == ContextItemSource.SYSTEM for i in result.items)


def test_build_with_memory():
    memory = MemoryManager()
    memory.start()
    memory.create("Usuário está preocupado com o projeto Yelena", importance=0.9)

    ctx = ContextManager(memory_manager=memory)
    ctx.start()
    result = ctx.build_from_text("projeto")
    sources = {i.source for i in result.items}
    assert ContextItemSource.MEMORY in sources or ContextItemSource.SYSTEM in sources


def test_budget_respected():
    ctx = ContextManager()
    query = ContextQuery(situation="teste de budget", token_budget=50, max_items=5)
    result = ctx.build(query)
    assert result.tokens_used <= result.token_budget


def test_dedup():
    from app.context.builder import ContextBuilder
    from app.context.models.context import ContextItem
    from app.context.constants import ContextItemSource

    builder = ContextBuilder()
    items = [
        ContextItem(content="mesmo texto", source=ContextItemSource.MEMORY, relevance=0.8),
        ContextItem(content="mesmo texto", source=ContextItemSource.KNOWLEDGE, relevance=0.7),
        ContextItem(content="outro texto", source=ContextItemSource.MEMORY, relevance=0.6),
    ]
    query = ContextQuery(situation="x", min_relevance=0.1)
    result = builder.build(query, items)
    contents = [i.content for i in result.items]
    assert contents.count("mesmo texto") == 1
