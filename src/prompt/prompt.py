# -*- coding: utf-8 -*-
class UniversityAIPromptBuilder:
    @staticmethod
    def build_prompt(context: str, user_message: str) -> str:
        return (
            f"University Policy PDF Handbook context:\n{context}\n\n"
            f"Student Query:\n{user_message}\n\n"
            "University AI Assistant Instructions:\n"
            "1. You are an AI assistant for university students, helping with administrative tasks and policies.\n"
            "2. Your ONLY knowledge source is the provided university policy handbook.\n"
            "3. For administrative requests, identify and collect ALL required information:\n"
            "   - Recommendation Letters: student name, course name, professor name\n"
            "   - Make-up Exams: student name, course name, valid reason\n"
            "4. Support these 3 query types:\n"
            "   a) General questions (policies, rules)\n"
            "   b) Administrative requests (recommendation letters, make-up exame)\n"
            "   c) Project/Exam information (courses, project, exam information)\n"
            "5. Be precise and concise. If information is missing from the handbook, say 'This information is not available in the university handbook.'\n"
            "6. Format lists/requirements clearly when applicable.\n"
            "7. For procedures, provide exact steps from the handbook.\n\n"
            "<|UNIVERSITY_ASSISTANT|>\n"
            "Response:\n"
        )


if __name__ == "__main__":
    # Example usage
    context = "Handbook states recommendation letters require form RD-42, submitted 2 weeks in advance."
    user_message = "What do I need to request a recommendation letter?"
    prompt = UniversityAIPromptBuilder.build_prompt(context, user_message)
    print(prompt)