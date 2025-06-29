import sys
from pathlib import Path
from types import SimpleNamespace, ModuleType
sys.modules.setdefault('streamlit', ModuleType('streamlit'))
sys.modules['streamlit'].write = lambda *a, **k: None
sys.modules['streamlit'].session_state = {}

def _dummy_dialog(*a, **k):

    def decorator(func):
        return func
    return decorator
sys.modules['streamlit'].dialog = _dummy_dialog
sys.modules['streamlit'].subheader = lambda *a, **k: None
sys.modules['streamlit'].json = lambda *a, **k: None
sys.modules['streamlit'].radio = lambda *a, **k: '👍'
sys.modules['streamlit'].text_area = lambda *a, **k: ''
sys.modules['streamlit'].button = lambda *a, **k: False
sys.modules['streamlit'].success = lambda *a, **k: None
sys.modules['streamlit'].stop = lambda: None
lc_core = ModuleType('langchain_core')
lc_core.pydantic_v1 = ModuleType('pydantic_v1')
lc_core.messages = ModuleType('messages')
import pydantic
lc_core.pydantic_v1.BaseModel = pydantic.BaseModel
lc_core.pydantic_v1.Field = lambda default=None, **kwargs: default

class _Msg:

    def __init__(self, content):
        self.content = content
lc_core.messages.SystemMessage = _Msg
lc_core.messages.HumanMessage = _Msg
sys.modules['langchain_core'] = lc_core
sys.modules['langchain_core.pydantic_v1'] = lc_core.pydantic_v1
sys.modules['langchain_core.messages'] = lc_core.messages
lc_openai = ModuleType('langchain_openai')

class DummyChat:

    def __init__(self, *a, **k):
        pass

    def with_structured_output(self, *a, **k):
        return self

    def invoke(self, *a, **k):
        return SimpleNamespace(content='ok')
lc_openai.ChatOpenAI = DummyChat
sys.modules['langchain_openai'] = lc_openai
root_dir = Path(__file__).resolve().parents[1]
sys.path.append(str(root_dir))
sys.path.append(str(root_dir / 'src'))
from ai.llm_service import LlmService, AIPrompt
from ai.llm_executor import LlmExecutor
from ai.llm_models import TaskChanges

def test_call_openai(monkeypatch):
    monkeypatch.setenv('OPENAI_API_KEY', 'test-key')
    monkeypatch.setattr('ai.llm_service.get_client', lambda: SimpleNamespace())
    dummy_ts = SimpleNamespace(get_active_tasks=lambda uid: [], get_completed_tasks=lambda uid: [], get_deleted_tasks=lambda uid: [])
    monkeypatch.setattr('ai.llm_service.get_task_service', lambda: dummy_ts)
    service = LlmService()
    executor = LlmExecutor(service)
    monkeypatch.setattr(executor, '_first_call', lambda sp, ui, tl: 'content')
    tc = TaskChanges(new_tasks=[], modified_tasks=[])
    monkeypatch.setattr(executor, '_second_call', lambda c1: tc)
    monkeypatch.setattr(executor, '_third_call', lambda uid, r: 'done')
    monkeypatch.setattr('ai.llm_executor.LangChainTracer', lambda: SimpleNamespace())
    result = executor.execute('user', 'prompt', 'input', {}, 'chat1')
    assert result == 'done'

def test_process_chat_records_prompt(monkeypatch):
    monkeypatch.setenv('OPENAI_API_KEY', 'test-key')
    monkeypatch.setattr('ai.llm_executor.LangChainTracer', lambda: SimpleNamespace())
    captured = {}

    def create(coll, data):
        captured['data'] = data
        return 'cid'

    def update(coll, doc_id, data):
        captured['update'] = data
    dummy_db = SimpleNamespace(create=create, update=update)
    monkeypatch.setattr('ai.llm_service.get_client', lambda: dummy_db)
    dummy_ts = SimpleNamespace(get_active_tasks=lambda uid: [], get_completed_tasks=lambda uid: [], get_deleted_tasks=lambda uid: [])
    monkeypatch.setattr('ai.llm_service.get_task_service', lambda: dummy_ts)
    service = LlmService()
    monkeypatch.setattr(service, '_get_system_prompt', lambda: AIPrompt(prompt_name='AI_Tasks', text='t', version=3))
    monkeypatch.setattr(service.executor, 'execute', lambda u, sp, it, tl, cid: TaskChanges(new_tasks=[], modified_tasks=[]))
    service.process_chat('user1', 'hello')
    assert captured['data']['prompt_name'] == 'AI_Tasks'
    assert captured['data']['prompt_version'] == 3
    assert 'Response' in captured['update']
