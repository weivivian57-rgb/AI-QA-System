from knowledge import knowledge, question_keywords


def find_answer(user_question):

    best_question = None

    best_score = 0

    for question, keywords in question_keywords.items():

        score = 0

        for word in keywords:

            if word.lower() in user_question.lower():

                score += 1

        if score > best_score:

            best_score = score

            best_question = question

    if best_question:

        return knowledge[best_question]

    return "抱歉，未找到相关答案，请尝试其他问题。"