import { useEffect, useState } from "react";
import { useParams, useNavigate, useLocation } from "react-router-dom";
import { supabase } from "../../services/supabaseClient";
import Flashcard from "../../components/Flashcard";
import { apiUrl } from "../../config/api";

const flashcardCache = new Map();
const FLASHCARD_COUNT = 10;

async function fetchFlashcards(bookId, chapterId) {
  const { data: sessionData } = await supabase.auth.getSession();
  const token = sessionData.session?.access_token;
  if (!token) throw new Error("Not authenticated");

  const res = await fetch(apiUrl("/api/generateFlashCard"), {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify({
      textbook_id: bookId,
      chapter_number: parseInt(chapterId, 10),
      count: FLASHCARD_COUNT,
    }),
  });

  if (!res.ok) {
    let detail = res.statusText;
    try {
      const body = await res.json();
      if (body?.detail) detail = body.detail;
    } catch (_) {
      // body wasn't JSON; keep statusText
    }
    throw new Error(detail || `HTTP ${res.status}`);
  }

  const data = await res.json();
  return data.response ?? [];
}

export default function Reinforce({
  type = "flashcards",
  showResults = false,
}) {
  const { bookId, chapterId } = useParams();
  const navigate = useNavigate();
  const location = useLocation();

  const [items, setItems] = useState([]);
  const [index, setIndex] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const shuffleToken = location.state?.shuffleToken ?? null;

  useEffect(() => {
    let isMounted = true;
    const cacheKey = `${bookId}:${chapterId}`;
    setIndex(0);
    setError(null);

    async function load() {
      let cards = flashcardCache.get(cacheKey);
      if (!cards) {
        setLoading(true);
        setItems([]);
        try {
          cards = await fetchFlashcards(bookId, chapterId);
          flashcardCache.set(cacheKey, cards);
        } catch (err) {
          if (!isMounted) return;
          setError(err.message || "Failed to load flashcards");
          setLoading(false);
          return;
        }
      }

      if (!isMounted) return;
      const prepared =
        type === "flashcards" && !showResults && shuffleToken
          ? shuffleDeck(cards)
          : cards;
      setItems(prepared);
      setLoading(false);
    }

    load();
    return () => {
      isMounted = false;
    };
  }, [bookId, chapterId, type, shuffleToken, showResults]);

  const done = !loading && items.length > 0 && index >= items.length;
  const baseRoute = `/books/${bookId}/chapters/${chapterId}/reinforce/${type}`;
  const resultsRoute = `${baseRoute}/results`;

  useEffect(() => {
    if (done) navigate(resultsRoute, { replace: true });
  }, [done, navigate, resultsRoute]);

  if (showResults) {
    return (
      <div className="mx-auto">
        {loading ? (
          <p className="text-slate-500">Loading flashcards…</p>
        ) : error ? (
          <p className="text-red-400">Failed to load flashcards: {error}</p>
        ) : items.length === 0 ? (
          <p className="text-slate-500">
            No flashcards are available for this chapter yet.
          </p>
        ) : (
          <>
            <p className="text-slate-600 mb-3">
              Review every card below, then choose to reshuffle or run through
              the deck again.
            </p>
            <div className="w-full max-w-2xl border border-neutral-800 rounded-xl p-4 max-h-96 overflow-y-auto space-y-4">
              {items.map((cardItem) => (
                <article
                  key={cardItem.id ?? cardItem.front}
                  className="p-4 rounded-lg bg-[#1a1a1a] border border-neutral-800"
                >
                  <p className="text-xs tracking-wide mb-1">Question</p>
                  <p className="font-medium mb-3">{cardItem.front}</p>
                  <p className="text-xs tracking-wide mb-1">Answer</p>
                  <p className="">{cardItem.back}</p>
                </article>
              ))}
            </div>
            <div className="flex gap-3 mt-4 justify-center">
              <button
                className="px-4 py-2 rounded bg-indigo-600 text-white hover:bg-indigo-500"
                onClick={() => navigate(baseRoute, { replace: true })}
              >
                Try Again
              </button>
              <button
                className="px-4 py-2 rounded bg-indigo-600 text-white hover:bg-indigo-500"
                onClick={() =>
                  navigate(baseRoute, {
                    replace: true,
                    state: { shuffleToken: Date.now() },
                  })
                }
              >
                Reshuffle Cards
              </button>
            </div>
          </>
        )}
      </div>
    );
  }

  if (done) {
    return null;
  }

  const card = items[index];
  const arrowButtonClass =
    "p-3 rounded-full border border-slate-200 text-2xl text-slate-700 transition disabled:opacity-40 disabled:cursor-not-allowed hover:bg-slate-50 focus-visible:outline focus-visible:outline-2 focus-visible:outline-indigo-500";

  const goPrevious = () => setIndex((i) => Math.max(i - 1, 0));
  const goNext = () => {
    if (!items.length) return;
    setIndex((i) => i + 1);
  };

  return (
    <div className="flex flex-col items-center gap-4">
      {loading ? (
        <div className="w-full max-w-lg border border-dashed border-slate-200 rounded-xl p-8 text-center text-slate-500">
          Generating flashcards…
        </div>
      ) : error ? (
        <div className="w-full max-w-lg border border-red-400 rounded-xl p-8 text-center text-red-400">
          Failed to load flashcards: {error}
        </div>
      ) : items.length === 0 ? (
        <div className="w-full max-w-lg border border-slate-200 rounded-xl p-8 text-center text-slate-500">
          No flashcards are available for this chapter yet.
        </div>
      ) : (
        <>
          <div className="flex items-center justify-center gap-5 w-full">
            <button
              type="button"
              className={arrowButtonClass}
              onClick={goPrevious}
              disabled={index === 0}
              aria-label="Previous flashcard"
            >
              <span aria-hidden="true">&larr;</span>
            </button>
            <Flashcard
              front={card?.front}
              back={card?.back}
              cardId={card?.id ?? index}
            />
            <button
              type="button"
              className={arrowButtonClass}
              onClick={goNext}
              disabled={!items.length}
              aria-label="Next flashcard"
            >
              <span aria-hidden="true">&rarr;</span>
            </button>
          </div>
          <p className="text-sm text-slate-500">
            Card {Math.min(index + 1, items.length)} of {items.length}
          </p>
          <p className="text-xs text-slate-400">
            Click the card to flip and reveal the answer.
          </p>
        </>
      )}
    </div>
  );
}

function shuffleDeck(list) {
  const arr = [...list];
  for (let i = arr.length - 1; i > 0; i -= 1) {
    const j = Math.floor(Math.random() * (i + 1));
    [arr[i], arr[j]] = [arr[j], arr[i]];
  }
  return arr;
}
