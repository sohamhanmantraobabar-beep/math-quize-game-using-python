import { useCallback, useEffect, useState } from "react";
import { Header, Footer } from "./components/Chrome";
import { WelcomeScreen } from "./components/WelcomeScreen";
import { QuizScreen } from "./components/QuizScreen";
import { ResultsScreen } from "./components/ResultsScreen";
import { ProjectModal } from "./components/ProjectModal";
import {
  TOTAL_QUESTIONS,
  type AnswerRecord,
  type CategoryKey,
  type DifficultyKey,
  type Question,
  type QuizResult,
} from "./game/config";
import { generateQuiz, percentage } from "./game/engine";

type Screen = "home" | "quiz" | "results";

const BEST_SCORE_KEY = "math-quiz-game-best-score";

interface BestScore {
  score: number;
  total: number;
}

function readBestScore(): BestScore | null {
  try {
    const raw = window.localStorage.getItem(BEST_SCORE_KEY);
    if (!raw) return null;
    const parsed: unknown = JSON.parse(raw);
    if (
      typeof parsed === "object" &&
      parsed !== null &&
      "score" in parsed &&
      "total" in parsed &&
      typeof (parsed as BestScore).score === "number" &&
      typeof (parsed as BestScore).total === "number"
    ) {
      return parsed as BestScore;
    }
  } catch {
    // A blocked storage API should never prevent the quiz from running.
  }
  return null;
}

function Background() {
  return (
    <div aria-hidden="true" className="pointer-events-none fixed inset-0 overflow-hidden">
      <div className="absolute -right-[18%] -top-[32%] h-[760px] w-[760px] rounded-full bg-[radial-gradient(circle,rgba(114,81,219,0.28),rgba(62,40,130,0.08)_48%,transparent_68%)] blur-[20px]" />
      <div className="absolute -bottom-[24%] -left-[20%] h-[680px] w-[680px] rounded-full bg-[radial-gradient(circle,rgba(201,245,107,0.075),transparent_65%)] blur-[10px]" />
      <div className="absolute left-[47%] top-[32%] h-[380px] w-[380px] rounded-full bg-[radial-gradient(circle,rgba(255,156,141,0.06),transparent_65%)]" />
      <div className="absolute inset-x-0 top-0 h-[420px] bg-gradient-to-b from-white/[0.015] to-transparent" />
      <div className="absolute inset-0 opacity-[0.16] [mask-image:linear-gradient(to_bottom,black,transparent_42%)] bg-dot-grid" />
      <div className="absolute inset-x-0 top-0 h-px bg-gradient-to-r from-transparent via-white/20 to-transparent" />
    </div>
  );
}

export default function App() {
  const [screen, setScreen] = useState<Screen>("home");
  const [category, setCategory] = useState<CategoryKey>("mixed");
  const [difficulty, setDifficulty] = useState<DifficultyKey>("medium");
  const [questions, setQuestions] = useState<Question[]>([]);
  const [result, setResult] = useState<QuizResult | null>(null);
  const [bestScore, setBestScore] = useState<BestScore | null>(readBestScore);
  const [isNewBest, setIsNewBest] = useState(false);
  const [isProjectOpen, setIsProjectOpen] = useState(false);

  useEffect(() => {
    window.scrollTo({ top: 0, behavior: "auto" });
  }, [screen]);

  const startRound = useCallback(
    (selectedCategory: CategoryKey, selectedDifficulty: DifficultyKey) => {
      setQuestions(generateQuiz(selectedCategory, selectedDifficulty));
      setResult(null);
      setIsNewBest(false);
      setScreen("quiz");
    },
    [],
  );

  function handleStart() {
    startRound(category, difficulty);
  }

  function handleFinish(answers: AnswerRecord[]) {
    const score = answers.filter((answer) => answer.isCorrect).length;
    const nextResult: QuizResult = {
      score,
      total: TOTAL_QUESTIONS,
      percentage: percentage(score, TOTAL_QUESTIONS),
      answers,
      category,
      difficulty,
    };

    const previousBest = bestScore;
    const beatsBest = previousBest === null || score > previousBest.score;
    if (beatsBest) {
      const nextBest = { score, total: TOTAL_QUESTIONS };
      setBestScore(nextBest);
      try {
        window.localStorage.setItem(BEST_SCORE_KEY, JSON.stringify(nextBest));
      } catch {
        // The game still works when storage is unavailable.
      }
    }

    setIsNewBest(beatsBest && score > 0);
    setResult(nextResult);
    setScreen("results");
  }

  function handlePlayAgain() {
    startRound(category, difficulty);
  }

  function handleChangeSetup() {
    setResult(null);
    setQuestions([]);
    setScreen("home");
  }

  function handleHome() {
    setScreen("home");
    setQuestions([]);
    setResult(null);
  }

  function handleHowItWorks() {
    setScreen("home");
    window.setTimeout(() => {
      document.getElementById("how-it-works")?.scrollIntoView({
        behavior: "smooth",
        block: "start",
      });
    }, 90);
  }

  return (
    <div className="relative flex min-h-screen flex-col overflow-x-hidden bg-ink text-white">
      <Background />

      <Header
        onHome={handleHome}
        onHowItWorks={handleHowItWorks}
        onProject={() => setIsProjectOpen(true)}
        inGame={screen === "quiz"}
      />

      <div className="flex flex-1 flex-col">
        {screen === "home" && (
          <WelcomeScreen
            category={category}
            difficulty={difficulty}
            bestScore={bestScore}
            onCategoryChange={setCategory}
            onDifficultyChange={setDifficulty}
            onStart={handleStart}
            onProject={() => setIsProjectOpen(true)}
          />
        )}

        {screen === "quiz" && questions.length > 0 && (
          <QuizScreen
            category={category}
            difficulty={difficulty}
            questions={questions}
            onFinish={handleFinish}
            onQuit={handleHome}
          />
        )}

        {screen === "results" && result && (
          <ResultsScreen
            result={result}
            bestScore={bestScore}
            isNewBest={isNewBest}
            onPlayAgain={handlePlayAgain}
            onChangeSetup={handleChangeSetup}
            onHome={handleHome}
            onProject={() => setIsProjectOpen(true)}
          />
        )}
      </div>

      {screen !== "quiz" && (
        <Footer onProject={() => setIsProjectOpen(true)} onHome={handleHome} />
      )}

      {isProjectOpen && <ProjectModal onClose={() => setIsProjectOpen(false)} />}
    </div>
  );
}
