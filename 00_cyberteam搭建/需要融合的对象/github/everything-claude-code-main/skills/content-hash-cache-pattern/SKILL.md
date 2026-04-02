# 内容哈希文件缓存模式

使用 SHA-256 内容哈希值作为缓存键来缓存昂贵的文件处理结果（PDF 解析、文本提取、图像分析）。与基于路径的缓存不同，此方法可以在文件移动/重命名后继续存在，并在内容更改时自动失效。

## 何时激活

- 构建文件处理管道（PDF、图像、文本提取）
- 处理成本高，相同文件重复处理
- 需要 `--cache/--no-cache` CLI 选项
- 想要向现有的纯函数添加缓存而不修改它们

## 核心模式

### 1. 基于内容哈希的缓存密钥

使用文件内容（而不是路径）作为缓存键：```python
import hashlib
from pathlib import Path

_HASH_CHUNK_SIZE = 65536  # 64KB chunks for large files

def compute_file_hash(path: Path) -> str:
    """SHA-256 of file contents (chunked for large files)."""
    if not path.is_file():
        raise FileNotFoundError(f"File not found: {path}")
    sha256 = hashlib.sha256()
    with open(path, "rb") as f:
        while True:
            chunk = f.read(_HASH_CHUNK_SIZE)
            if not chunk:
                break
            sha256.update(chunk)
    return sha256.hexdigest()
```**为什么内容散列？** 文件重命名/移动 = 缓存命中。内容改变=自动失效。不需要索引文件。

### 2. 缓存条目的冻结数据类```python
from dataclasses import dataclass

@dataclass(frozen=True, slots=True)
class CacheEntry:
    file_hash: str
    source_path: str
    document: ExtractedDocument  # The cached result
```### 3. 基于文件的缓存存储

每个缓存条目都存储为“{hash}.json”——通过哈希进行 O(1) 查找，不需要索引文件。```python
import json
from typing import Any

def write_cache(cache_dir: Path, entry: CacheEntry) -> None:
    cache_dir.mkdir(parents=True, exist_ok=True)
    cache_file = cache_dir / f"{entry.file_hash}.json"
    data = serialize_entry(entry)
    cache_file.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")

def read_cache(cache_dir: Path, file_hash: str) -> CacheEntry | None:
    cache_file = cache_dir / f"{file_hash}.json"
    if not cache_file.is_file():
        return None
    try:
        raw = cache_file.read_text(encoding="utf-8")
        data = json.loads(raw)
        return deserialize_entry(data)
    except (json.JSONDecodeError, ValueError, KeyError):
        return None  # Treat corruption as cache miss
```### 4. 服务层包装器 (SRP)

保持处理函数的纯粹性。添加缓存作为单独的服务层。```python
def extract_with_cache(
    file_path: Path,
    *,
    cache_enabled: bool = True,
    cache_dir: Path = Path(".cache"),
) -> ExtractedDocument:
    """Service layer: cache check -> extraction -> cache write."""
    if not cache_enabled:
        return extract_text(file_path)  # Pure function, no cache knowledge

    file_hash = compute_file_hash(file_path)

    # Check cache
    cached = read_cache(cache_dir, file_hash)
    if cached is not None:
        logger.info("Cache hit: %s (hash=%s)", file_path.name, file_hash[:12])
        return cached.document

    # Cache miss -> extract -> store
    logger.info("Cache miss: %s (hash=%s)", file_path.name, file_hash[:12])
    doc = extract_text(file_path)
    entry = CacheEntry(file_hash=file_hash, source_path=str(file_path), document=doc)
    write_cache(cache_dir, entry)
    return doc
```## 关键设计决策

|决定|理由|
|----------|------------|
| SHA-256 内容哈希 |路径无关，内容更改时自动失效 |
| `{hash}.json` 文件命名 | O(1) 查找，无需索引文件 |
|服务层包装| SRP：提取保持纯粹，缓存是一个单独的问题 |
|手动 JSON 序列化 |完全控制冻结数据类序列化 |
|腐败返回“无” |优雅降级，下次运行时重新处理 |
| `cache_dir.mkdir(parents=True)` |首次写入时惰性目录创建 |

## 最佳实践

- **散列内容，而不是路径** - 路径改变，内容身份不变
- **散列时分块大文件** — 避免将整个文件加载到内存中
- **保持处理函数纯粹** - 他们应该对缓存一无所知
- **记录缓存命中/未命中**，并带有截断的哈希值以进行调试
- **优雅地处理损坏** - 将无效的缓存条目视为未命中，永远不会崩溃

## 要避免的反模式```python
# BAD: Path-based caching (breaks on file move/rename)
cache = {"/path/to/file.pdf": result}

# BAD: Adding cache logic inside the processing function (SRP violation)
def extract_text(path, *, cache_enabled=False, cache_dir=None):
    if cache_enabled:  # Now this function has two responsibilities
        ...

# BAD: Using dataclasses.asdict() with nested frozen dataclasses
# (can cause issues with complex nested types)
data = dataclasses.asdict(entry)  # Use manual serialization instead
```## 何时使用

- 文件处理管道（PDF解析、OCR、文本提取、图像分析）
- 受益于 `--cache/--no-cache` 选项的 CLI 工具
- 批处理，其中相同的文件在运行中出现
- 向现有纯函数添加缓存而不修改它们

## 何时不使用

- 数据必须始终保持新鲜（实时提要）
- 缓存条目非常大（请考虑流式传输）
- 结果取决于文件内容之外的参数（例如，不同的提取配置）