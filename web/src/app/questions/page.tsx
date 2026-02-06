import { QuestionForm } from "@/components/QuestionForm";
import { QuestionList } from "@/components/QuestionList";

export const metadata = {
  title: "Philadelphia Crime Explorer | Questions",
  description: "Submit questions and read answered community Q&A about Philadelphia crime patterns.",
};

export default function QuestionsPage() {
  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold">Community Q&A</h1>
      <section className="space-y-3">
        <h2 className="text-xl font-semibold">Ask a Question</h2>
        <QuestionForm />
      </section>
      <section className="space-y-3">
        <h2 className="text-xl font-semibold">Answered Questions</h2>
        <QuestionList />
      </section>
    </div>
  );
}
