def calculate_scores(questions, user_answers):
    questions_score = []
    total_score = 0
    for question in questions:
        if question.single_correct_answer:
            check_user_true_answers = 0
            for answer in question.answers:
                if user_answers[answer.id]:
                    check_user_true_answers += 1
            score = -100
            if check_user_true_answers > 1:
                raise ValueError(
                    "Only one correct answer is allowed for a single "
                    "correct answer question")
            elif check_user_true_answers == 0:
                score = 0
            else:
                for answer in question.answers:
                    if answer.is_correct and user_answers[answer.id]:
                        score = 100
                        break
            questions_score.append(
                {"question_id": question.id, 'score': score}
            )
            total_score += score
        else:
            count_corrects = 0
            count_wrongs = 0
            for answer in question.answers:
                if answer.is_correct:
                    count_corrects += 1
                else:
                    count_wrongs += 1
            user_corrects = 0
            user_wrongs = 0
            for answer in question.answers:
                if answer.is_correct and user_answers[answer.id]:
                    user_corrects += 1
                elif not answer.is_correct and user_answers[answer.id]:
                    user_wrongs += 1

            question_score = 0
            question_score += user_corrects * 100 / count_corrects
            if count_wrongs:
                question_score -= user_wrongs * 100 / count_wrongs
            question_score = int(question_score)

            questions_score.append(
                {"question_id": question.id, 'score': question_score}
            )
            total_score += question_score

    quiz_score = int(total_score / len(questions))
    return questions_score, quiz_score
