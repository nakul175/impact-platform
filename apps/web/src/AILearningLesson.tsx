import { useState } from "react";
import type { Catalog } from "./AIEnablement";

export function AILearningLesson({
  lesson,
}: {
  lesson: NonNullable<Catalog["learning_paths"][number]["lessons"]>[number];
}) {
  const [answer, setAnswer] = useState<number | null>(null);
  return (
    <details className="ai-lesson">
      <summary>Lesson: {lesson.title}</summary>
      <p>{lesson.lesson}</p>
      <p>
        <strong>Try it:</strong> {lesson.exercise}
      </p>
      <fieldset>
        <legend>{lesson.check.question}</legend>
        {lesson.check.options.map((option, index) => (
          <label className="ai-checkbox" key={index}>
            <input
              type="radio"
              name={"lesson-" + lesson.key}
              checked={answer === index}
              onChange={() => setAnswer(index)}
            />
            {option}
          </label>
        ))}
      </fieldset>
      {answer !== null && (
        <p role="status" className="ai-notice">
          {answer === lesson.check.answer ? "Correct. " : "Try again. "}
          {lesson.check.explanation}
        </p>
      )}
    </details>
  );
}
