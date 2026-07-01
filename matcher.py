"""
matcher.py
关键词匹配模块
"""

from knowledge import knowledge, question_keywords


def find_answer(user_question):
    """
    根据用户输入的问题进行关键词匹配
    """

    # 用户输入转换成关键词集合
    user_keywords = set(user_question.replace("？", "")
                                      .replace("?", "")
                                      .split())

    best_question = None
    best_score = 0

    # 遍历知识库
    for question, keywords in question_keywords.items():

        score = len(user_keywords & keywords)

        if score > best_score:
            best_score = score
            best_question = question

    if best_question:
        return knowledge[best_question]

    return "抱歉，未找到相关答案，请尝试其他问题。"