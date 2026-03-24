"""Context Compression System QA Test Script"""

import sys
sys.path.insert(0, '/Users/cyberwiz/Documents/01_Project/Output/CyberTeam-v2.1/modules')

from context.ast import (
    ChainNode, ConversationChain, NodeType, ChainSerializer
)
from context.section_summarizer import (
    SectionSummarizer, Section, SectionType, CompressionLevel
)
from context.qa_summarizer import (
    QAPairSummarizer, QAPair, QAType, AbstractionLevel
)


def test_chain_ast():
    """Test Chain AST structure"""
    print("=" * 60)
    print("Testing Chain AST Structure")
    print("=" * 60)

    # Create a chain
    chain = ConversationChain(max_tokens=100000)

    # Add nodes
    node1 = ChainNode(type=NodeType.USER_MESSAGE, content="Hello, how are you?")
    node2 = ChainNode(type=NodeType.ASSISTANT_MESSAGE, content="I'm doing well, thank you!")
    node3 = ChainNode(type=NodeType.USER_MESSAGE, content="Can you help me with Python?")

    chain.add_node(node1)
    chain.add_node(node2)
    chain.add_node(node3)

    print(f"Total nodes: {len(chain.nodes)}")
    print(f"Head: {chain.head}")
    print(f"Tail: {chain.tail}")
    print(f"Total tokens: {chain.get_total_tokens()}")
    print(f"Message count: {chain.get_message_count()}")

    # Test node sequence
    sequence = chain.get_node_sequence()
    print(f"Node sequence length: {len(sequence)}")

    # Test compression ratio
    ratio = chain.get_compression_ratio()
    print(f"Compression ratio: {ratio:.4f}")

    # Test serialization
    json_str = ChainSerializer.to_json(chain)
    print(f"Serialized length: {len(json_str)}")

    # Test deserialization
    restored = ChainSerializer.from_json(json_str)
    print(f"Restored nodes: {len(restored.nodes)}")

    print("\n[OK] Chain AST Structure Tests Passed")
    return True


def test_section_compression():
    """Test Section Compression Algorithm"""
    print("\n" + "=" * 60)
    print("Testing Section Compression Algorithm")
    print("=" * 60)

    summarizer = SectionSummarizer()

    # Create test content
    content = """这是一个测试分段。
这是第二行内容。
这是第三行内容。
这是第四行内容。
这是第五行内容。
这是第六行内容。
这是第七行内容。
这是第八行内容。
这是第九行内容。
这是第十行内容。"""

    # Detect section type
    section_type = summarizer.detect_section_type(content)
    print(f"Detected section type: {section_type}")

    # Create section
    section = summarizer.create_section_from_content(content, section_type)
    print(f"Section token count: {section.token_count}")

    # Test compression at different levels
    for level in [CompressionLevel.LIGHT, CompressionLevel.MEDIUM, CompressionLevel.AGGRESSIVE]:
        compressed = summarizer.compress(section, level=level)
        stats = summarizer.get_compression_stats(compressed)
        print(f"\nCompression level: {level.value}")
        print(f"  Original tokens: {stats['original_tokens']}")
        print(f"  Compressed tokens: {stats['compressed_tokens']}")
        print(f"  Compression ratio: {stats['compression_ratio']:.2f}")
        print(f"  Space saved: {stats['space_saved_percent']:.1f}%")

    print("\n[OK] Section Compression Tests Passed")
    return True


def test_qa_summarization():
    """Test QA Summarization"""
    print("\n" + "=" * 60)
    print("Testing QA Summarization")
    print("=" * 60)

    summarizer = QAPairSummarizer()

    # Create QA pair
    qa = summarizer.create_qa_pair(
        question="如何读取 /Users/cyberwiz/test.py 文件?",
        answer="使用 Python 的 open() 函数: open('/Users/cyberwiz/test.py', 'r').read()",
        qa_type=QAType.EXPLICIT
    )

    print(f"Original QA token count: {qa.token_count}")
    print(f"Key entities: {qa.key_entities}")

    # Test abstraction
    abstracted = summarizer.abstract(qa, AbstractionLevel.SEMANTIC)
    print(f"Abstracted question: {abstracted.abstracted_question}")

    # Test compression
    compressed = summarizer.compress(qa, keep_entities=True)
    stats = summarizer.get_compression_stats(compressed)
    print(f"\nCompression stats:")
    print(f"  Original tokens: {stats['original_tokens']}")
    print(f"  Compressed tokens: {stats['compressed_tokens']}")
    print(f"  Space saved: {stats['space_saved_percent']:.1f}%")

    print("\n[OK] QA Summarization Tests Passed")
    return True


def test_token_budget():
    """Test Token Budget Management"""
    print("\n" + "=" * 60)
    print("Testing Token Budget Management")
    print("=" * 60)

    # Test with different max_tokens
    for max_tokens in [10000, 50000, 100000]:
        chain = ConversationChain(max_tokens=max_tokens)

        # Add sample content
        for i in range(10):
            node = ChainNode(
                type=NodeType.USER_MESSAGE,
                content=f"这是第 {i+1} 条测试消息 " * 50
            )
            chain.add_node(node)

        total_tokens = chain.get_total_tokens()
        ratio = chain.get_compression_ratio()

        print(f"\nMax tokens: {max_tokens}")
        print(f"Total tokens: {total_tokens}")
        print(f"Usage ratio: {ratio:.4f}")
        print(f"Warning threshold (0.8): {'[WARNING]' if ratio > 0.8 else '[OK]'}")
        print(f"Critical threshold (0.95): {'[CRITICAL]' if ratio > 0.95 else '[OK]'}")

    print("\n[OK] Token Budget Management Tests Passed")
    return True


def main():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("Context Compression System QA Validation")
    print("=" * 60 + "\n")

    results = []

    try:
        results.append(("Chain AST Structure", test_chain_ast()))
    except Exception as e:
        print(f"\n[FAIL] Chain AST Structure: {e}")
        results.append(("Chain AST Structure", False))

    try:
        results.append(("Section Compression", test_section_compression()))
    except Exception as e:
        print(f"\n[FAIL] Section Compression: {e}")
        results.append(("Section Compression", False))

    try:
        results.append(("QA Summarization", test_qa_summarization()))
    except Exception as e:
        print(f"\n[FAIL] QA Summarization: {e}")
        results.append(("QA Summarization", False))

    try:
        results.append(("Token Budget", test_token_budget()))
    except Exception as e:
        print(f"\n[FAIL] Token Budget: {e}")
        results.append(("Token Budget", False))

    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)

    passed = sum(1 for _, r in results if r)
    total = len(results)

    for name, result in results:
        status = "[PASS]" if result else "[FAIL]"
        print(f"{status} {name}")

    print(f"\nTotal: {passed}/{total} passed")

    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
