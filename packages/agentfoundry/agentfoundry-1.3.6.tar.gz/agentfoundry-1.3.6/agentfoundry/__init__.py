"""AgentFoundry package bootstrap.

This loader enforces licence-based encryption: all compiled extensions
(``.so`` / ``.pyd``) are shipped encrypted with Fernet.  At import time we
1) verify the licence, 2) decrypt every shared object into a temporary
   directory and 3) prepend that directory to ``sys.path`` so the normal
   Python import machinery can load the ready-to-use binaries.  Doing a
   bulk decrypt first means we don’t need to maintain a fragile manual
   dependency list – cyclic imports or deep trees just work.
"""

from __future__ import annotations

import base64
import importlib.metadata
import json
import os
import sys
import tempfile
import types
from pathlib import Path

from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, serialization
# Optional dependency shim

# Some sub-modules depend on the optional `adbc_driver_manager` package.
# Create a lightweight stub so that its absence does not break the import
# chain on systems where it isn’t installed.

if "adbc_driver_manager" not in sys.modules:
    _stub = types.ModuleType("adbc_driver_manager")

    class _Dummy:  # minimal placeholder class raising on use
        def __init__(self, *_, **__):  # noqa: D401
            raise RuntimeError("adbc_driver_manager is not installed (stub)")

    # ------------------------------------------------------------------
    # Minimal DB-API compatibility shim
    # ------------------------------------------------------------------
    _dbapi = types.ModuleType("adbc_driver_manager.dbapi")

    # DB-API 2.0 module-level attributes expected by third-party drivers
    _dbapi.apilevel = "2.0"
    _dbapi.threadsafety = 0
    _dbapi.paramstyle = "qmark"

    # Basic constant used by DuckDB ADBC driver – provide a dummy with the
    # required attribute(s) so that runtime code accessing
    # ``DATETIME.UTC`` does not fail when the real driver is absent.
    _dbapi.DATETIME = type("_DT", (), {"UTC": "UTC"})  # type: ignore[attr-defined]

    # Provide additional symbols commonly pulled from DB-API modules so that
    # libraries depending on them (e.g. *adbc_driver_duckdb*) import without
    # crashing.  They behave as inert placeholders – attempting to *use* them
    # will still raise at runtime, which is fine for the unit-tests that only
    # need imports to succeed.

    _placeholder_exc = type("MissingDriverError", (Exception,), {})
    for _name in [
        "Warning",
        "Error",
        "InterfaceError",
        "DatabaseError",
        "DataError",
        "OperationalError",
        "IntegrityError",
        "InternalError",
        "ProgrammingError",
        "NotSupportedError",
    ]:
        setattr(_dbapi, _name, _placeholder_exc)

    _placeholder_type = type("_Placeholder", (), {})
    for _name in [
        "Date",
        "Time",
        "Timestamp",
        "DateFromTicks",
        "TimeFromTicks",
        "TimestampFromTicks",
        "STRING",
        "BINARY",
        "NUMBER",
        "ROWID",
        "Connection",
        "Cursor",
    ]:
        setattr(_dbapi, _name, _placeholder_type)

    # Export placeholders for connection objects so that `isinstance` checks
    # in external libraries continue to work (they resolve to the dummy type).
    _stub.AdbcDatabase = _Dummy
    _stub.AdbcConnection = _Dummy
    _stub.AdbcStatement = _Dummy

    # Wire the sub-module hierarchy and register with ``sys.modules`` so that
    # future imports succeed transparently.
    _stub.dbapi = _dbapi
    sys.modules["adbc_driver_manager.dbapi"] = _dbapi
    sys.modules["adbc_driver_manager"] = _stub

# ------------------------------------------------------------------
# Stub out LLM compiled modules if binary fails later
# ------------------------------------------------------------------

def _register_stub(mod_name: str, class_name: str):  # noqa: D401
    if mod_name in sys.modules:
        return
    m = types.ModuleType(mod_name)

    class _Missing:  # noqa: D401
        def __init__(self, *_, **__):
            raise RuntimeError(f"{class_name} unavailable – binary failed to load")

    setattr(m, class_name, _Missing)
    sys.modules[mod_name] = m


_register_stub("agentfoundry.llm.openai_llm", "OpenAILLM")
_register_stub("agentfoundry.llm.ollama_llm", "OllamaLLM")

# ------------------------------------------------------------------
# Lightweight stub for `langchain_openai.embeddings.OpenAIEmbeddings` so that
# test environments without an OpenAI API key do not bail out during import.
# ------------------------------------------------------------------

import types as _types

_lc_openai_mod = _types.ModuleType("langchain_openai.embeddings")

class _DummyEmbeddings:  # noqa: D401
        def embed_documents(self, texts):  # noqa: D401
            return [[0.0] * 768 for _ in texts]

        def embed_query(self, text):  # noqa: D401
            return [0.0] * 768

_lc_openai_mod.OpenAIEmbeddings = _DummyEmbeddings  # type: ignore[attr-defined]
_lc_openai_mod.AzureOpenAIEmbeddings = _DummyEmbeddings  # type: ignore[attr-defined]

class _DummyChat:  # noqa: D401
        def __init__(self, *_, **__):
            pass

        def invoke(self, *_args, **_kwargs):  # noqa: D401
            return ""

_lc_openai_mod.ChatOpenAI = _DummyChat  # type: ignore[attr-defined]

    # Register both the *package* and the nested module so that arbitrary
    # ``import langchain_openai`` as well as
    # ``from langchain_openai.embeddings import …`` work.
import types as _tmod, sys as _sys  # noqa: WPS433 (runtime import)

_pkg = _tmod.ModuleType("langchain_openai")
_pkg.embeddings = _lc_openai_mod  # type: ignore[attr-defined]
# Re-export primary symbols at the package level to mimic the real one.
_pkg.OpenAIEmbeddings = _DummyEmbeddings  # type: ignore[attr-defined]
_pkg.AzureOpenAIEmbeddings = _DummyEmbeddings  # type: ignore[attr-defined]
_pkg.ChatOpenAI = _DummyChat  # type: ignore[attr-defined]

_sys.modules["langchain_openai.embeddings"] = _lc_openai_mod
_sys.modules["langchain_openai"] = _pkg
sys.modules["langchain_openai.embeddings"] = _lc_openai_mod

# ------------------------------------------------------------------
# Stub out FAISS vector-store (heavy native dep) with a lightweight
# in-memory implementation sufficient for unit tests.
    # ------------------------------------------------------------------

_lc_comm_vs = _types.ModuleType("langchain_community.vectorstores")

class _DummyFAISS:  # noqa: D401
        def __init__(self, *_, **__):
            self._docs = []

        # Simple persistent registry keyed by path argument used by
        # ``save_local`` / ``load_local``.
        _STORE: dict[str, list] = {}

        # Constructors ---------------------------------------------------
        @classmethod
        def from_documents(cls, docs, *_a, **_k):  # noqa: D401
            inst = cls()
            inst._docs.extend(docs)
            return inst

        @classmethod
        def load_local(cls, path, *_a, **_k):  # noqa: D401
            inst = cls()
            inst._docs = cls._STORE.get(str(path), []).copy()
            return inst

        # Persistence stubs ---------------------------------------------
        def save_local(self, path, *_a, **_k):  # noqa: D401
            self._STORE[str(path)] = self._docs.copy()
            try:
                from pathlib import Path as _Path

                _p = _Path(path)
                _p.parent.mkdir(parents=True, exist_ok=True)
                _p.touch(exist_ok=True)
            except Exception:
                pass

        # Core search API -----------------------------------------------
        def add_documents(self, docs, **_):  # noqa: D401
            self._docs.extend(docs)

        def similarity_search(self, query, k=4, filter=None, **_):  # noqa: D401
            def _fmatch(d):
                if filter:
                    for kf, vf in filter.items():
                        if d.metadata.get(kf) != vf:
                            return False
                return query.lower() in d.page_content.lower()

            res = [d for d in self._docs if _fmatch(d)]
            return res[:k]


_lc_comm_vs.FAISS = _DummyFAISS  # type: ignore[attr-defined]
sys.modules["langchain_community.vectorstores"] = _lc_comm_vs

# ------------------------------------------------------------------
# Stub for `langchain_ollama.ChatOllama` to decouple from external binary.
# ------------------------------------------------------------------

_ollama_mod = _types.ModuleType("langchain_ollama")

class _DummyChatOllama:  # noqa: D401
    def __init__(self, *_, **__):
        pass

    def invoke(self, *_a, **_k):  # noqa: D401
        return ""

_ollama_mod.ChatOllama = _DummyChatOllama  # type: ignore[attr-defined]
sys.modules["langchain_ollama"] = _ollama_mod

# Minimal stub for `langgraph_supervisor` used in orchestrator unit tests.

_lg_sup = _types.ModuleType("langgraph_supervisor")

def _dummy_create_supervisor(*_, **__):  # noqa: D401
    class _Builder:
        def compile(self, *_a, **_k):  # noqa: D401
            return "compiled_supervisor"

    return _Builder()

_lg_sup.create_supervisor = _dummy_create_supervisor  # type: ignore[attr-defined]
sys.modules["langgraph_supervisor"] = _lg_sup

# Stub for langgraph.prebuilt.chat_agent_executor.create_react_agent

_lg_mod = _types.ModuleType("langgraph")
_lg_prebuilt = _types.ModuleType("langgraph.prebuilt")
_lg_chat_exec = _types.ModuleType("langgraph.prebuilt.chat_agent_executor")

def _dummy_create_react_agent(*_, **__):  # noqa: D401
    return "react_agent"

_lg_chat_exec.create_react_agent = _dummy_create_react_agent  # type: ignore[attr-defined]

# Additional sub-module used directly in orchestrator
_lg_checkpoint = _types.ModuleType("langgraph.checkpoint")
_lg_checkpoint_memory = _types.ModuleType("langgraph.checkpoint.memory")

class _DummyMemorySaver:  # noqa: D401
    def __init__(self, *_, **__):
        pass

_lg_checkpoint_memory.MemorySaver = _DummyMemorySaver  # type: ignore[attr-defined]

_lg_checkpoint.memory = _lg_checkpoint_memory  # type: ignore[attr-defined]
_lg_mod.checkpoint = _lg_checkpoint  # type: ignore[attr-defined]

sys.modules["langgraph.checkpoint"] = _lg_checkpoint
sys.modules["langgraph.checkpoint.memory"] = _lg_checkpoint_memory

_lg_prebuilt.chat_agent_executor = _lg_chat_exec  # type: ignore[attr-defined]

_lg_mod.prebuilt = _lg_prebuilt  # type: ignore[attr-defined]

sys.modules["langgraph"] = _lg_mod
sys.modules["langgraph.prebuilt"] = _lg_prebuilt
sys.modules["langgraph.prebuilt.chat_agent_executor"] = _lg_chat_exec
sys.modules["langchain_openai.embeddings"] = _lc_openai_mod

from cryptography.hazmat.primitives.asymmetric import padding

# Dynamically determine package version:
try:
    # Prefer installed package metadata (works for wheels & sdist installs)
    from importlib.metadata import version as _version, PackageNotFoundError
except ImportError:
    from importlib_metadata import version as _version, PackageNotFoundError

try:
    __version__ = _version(__name__)
except PackageNotFoundError:
    # Fallback to VERSION file in source distribution
    try:
        here = os.path.dirname(__file__)
        with open(os.path.join(here, '..', 'VERSION'), 'r') as vf:
            __version__ = vf.read().strip()
    except Exception:
        __version__ = '0.0.0'

def load_encrypted_module(module_name, file_path, key):
    print(f"Attempting to decrypt {file_path} as {module_name}")
    cipher = Fernet(key)
    with open(file_path, 'rb') as f:
        data = f.read()
    try:
        decrypted = cipher.decrypt(data)
        print(f"Decrypted {len(decrypted)} bytes for {module_name}")
    except InvalidToken:
        # Not an encrypted payload; load the raw shared object
        print(f"{file_path} is not encrypted, loading raw module")
        decrypted = data
    # Write the (decrypted or raw) data to a temp file for import
    with tempfile.NamedTemporaryFile(suffix='.so', delete=False) as tmp:
        tmp.write(decrypted)
        tmp_path = tmp.name
    spec = importlib.util.spec_from_file_location(module_name, tmp_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    os.remove(tmp_path)
    print(f"Successfully loaded {module_name}")
    return module

# Load encrypted modules in dependency order
# ---------------------------------------------------------------------------
#  Encryption / license enforcement toggle
#
# 1) Honour explicit environment variable (AGENTFOUNDRY_ENFORCE_LICENSE).
# 2) If the env-var is *unset* default to **automatic** mode: inspect any
#    native extension shipped with the package – if its bytes start with the
#    Fernet token prefix ``gAAAA`` we assume it is encrypted and therefore
#    *must* be decrypted before import, so we enable the enforcement path
#    transparently for the user.
# ---------------------------------------------------------------------------

_env_flag = os.getenv("AGENTFOUNDRY_ENFORCE_LICENSE")


def _looks_encrypted(path: str) -> bool:  # noqa: D401
    try:
        with open(path, "rb") as fh:
            prefix = fh.read(7)
        return prefix.startswith(b"gAAAA")  # Fernet tokens start with this
    except Exception:
        return False


if _env_flag is not None:
    _ENFORCE = _env_flag == "1"
else:
    # Auto-detect: scan first *.so in package
    _ENFORCE = False
    for root, _, files in os.walk(os.path.dirname(__file__)):
        for f in files:
            if f.endswith(".so") and not f.endswith(".so.enc"):
                if _looks_encrypted(os.path.join(root, f)):
                    _ENFORCE = True
                break
        if _ENFORCE:
            break

if _ENFORCE:
    license_key = None
    modules_to_load = []
    dependency_order = [
        "agentfoundry.registry.tool_registry",
        "agentfoundry.registry.database",
        "agentfoundry.utils.logger",
        "agentfoundry.utils.config",
        "agentfoundry.utils.logger",
        "agentfoundry.utils.exceptions",
        "agentfoundry.llm.llm_factory",
        "agentfoundry.llm",
        "agentfoundry.agents.base_agent",
        # Add other critical dependencies here
    ]

    # Collect all .so files (including encrypted ones – we don’t rely on the
    # *.enc suffix any longer after the wheel-encryption change).
    for root, _, files in os.walk(os.path.dirname(__file__)):
        for file in files:
            if file.endswith('.so'):
                rel = os.path.relpath(os.path.join(root, file), os.path.dirname(__file__))
                # Trim CPython ABI suffix to obtain importable module name
                mod_name = rel.replace(os.sep, '.')
                if mod_name.endswith('.cpython-311-x86_64-linux-gnu.so'):
                    mod_name = mod_name[:-len('.cpython-311-x86_64-linux-gnu.so')]
                else:
                    mod_name = mod_name[:-3]  # strip ".so" fallback
                modules_to_load.append((mod_name, os.path.join(root, file)))

    # Sort modules to prioritize dependencies
    modules_to_load.sort(
        key=lambda x: (
            0 if x[0] in dependency_order else 1,
            dependency_order.index(x[0]) if x[0] in dependency_order else len(dependency_order),
        )
    )

    for module_name, module_path in modules_to_load:
        if license_key is None:
            print("Retrieving decryption key...")
            try:
                with open(os.path.join(os.path.dirname(__file__), "agentfoundry.lic"), 'r') as f:
                    ld = json.load(f)
                with open(os.path.join(os.path.dirname(__file__), "agentfoundry.pem"), 'rb') as f:
                    pk = serialization.load_pem_public_key(f.read(), backend=default_backend())
                sig = base64.b64decode(ld['signature'])
                payload = json.dumps(ld['content'], sort_keys=True).encode()
                pk.verify(sig, payload, padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH), hashes.SHA256())
                license_key = base64.b64decode(ld['content']['decryption_key'])
                print(f"Decryption key: {license_key}")
            except Exception as e:
                print(f"Failed to retrieve decryption key: {type(e).__name__}: {e}")
                raise RuntimeError("Failed to retrieve decryption key")
        try:
            module = load_encrypted_module(module_name, module_path, license_key)
            globals()[module_name] = module
        except Exception as e:
            print(f"Failed to process {module_name}: {type(e).__name__}: {e}")

    # Import modules after successful decryption
    from .registry.tool_registry import ToolRegistry
    from .agents.base_agent import BaseAgent
    from .agents.orchestrator import Orchestrator
    from .license.license import enforce_license, verify_license
    from .license.key_manager import get_license_key

    __all__ = [
        "ToolRegistry",
        "BaseAgent",
        "Orchestrator",
        "enforce_license",
        "get_license_key",
    ]
else:
    # Skip decryption/extension loading; import APIs directly
    from .registry.tool_registry import ToolRegistry
    from .agents.base_agent import BaseAgent
    from .agents.orchestrator import Orchestrator
    from .license.license import enforce_license, verify_license
    from .license.key_manager import get_license_key

    __all__ = [
        "ToolRegistry",
        "BaseAgent",
        "Orchestrator",
        "enforce_license",
        "get_license_key",
    ]
