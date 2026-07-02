"""
matcher.py
核心问答匹配逻辑 (算法优化版)
"""
from knowledge import question_keywords, knowledge, categories

def find_answer(user_question):
    """
    高级匹配算法：计算 交集数量 / 该标准问题关键词总数
    返回：答案, 命中的关键词, 匹配的标准问题, 匹配度百分比, 所属分类
    """
    best_question = None
    best_rate = 0.0
    matched_words = []
    matched_category = "未分类"

    for question, keywords in question_keywords.items():
        if not keywords:
            continue
        
        # 提取当前问题中用户输入的交集关键词
        current_match = [word for word in keywords if word.lower() in user_question.lower()]
        
        # 🔍 核心算法优化：交集数量 / 该标准问题的关键词总数
        match_rate = len(current_match) / len(keywords)

        # 找出匹配度最高的问题
        if match_rate > best_rate:
            best_rate = match_rate
            best_question = question
            matched_words = current_match

    # 如果有匹配到结果
    if best_question and best_rate > 0.0:
        # 反查该问题属于哪个知识分类
        for cat_name, q_list in categories.items():
            if best_question in q_list:
                matched_category = cat_name
                break
        
        return knowledge[best_question], matched_words, best_question, best_rate, matched_category

    return "抱歉，未找到相关答案，请尝试使用更准确的关键词描述您的问题。", [], None, 0.0, "未分类"