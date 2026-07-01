from knowledge import get_question_count, get_categories


def start_ui():
    print("=" * 50)
    print("        AI人工智能基础问答系统")
    print("=" * 50)

    print("\n正在加载知识库...\n")

    question_count = get_question_count()
    category_list = get_categories()

    print(f"✓ 成功加载 {question_count} 条AI基础知识\n")

    print("知识分类：")

    for category in category_list:
        print(f"  • {category}")

    print("\n系统初始化完成！") 
