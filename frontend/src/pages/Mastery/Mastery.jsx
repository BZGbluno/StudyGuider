import React, { useState, useRef, useEffect, useCallback } from "react";
import { useParams } from "react-router-dom";
import { FaMicrophone } from "react-icons/fa";
import { supabase } from "../../services/supabaseClient";

export default function Mastery() {
  const { bookId, chapterId } = useParams();
  const [status, setStatus] = useState("Not connected");
  const [isConnecting, setIsConnecting] = useState(false);
  const [transcripts, setTranscripts] = useState([]);
  const [isPressing, setIsPressing] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [isSpeaking, setIsSpeaking] = useState(false);

  const audioRef = useRef(null);
  const pcRef = useRef(null);
  const dcRef = useRef(null);
  const micTrackRef = useRef(null);
  const pressingRef = useRef(false);
  const transcriptEndRef = useRef(null);
  const [metadata, setMetadata] = useState({ book: "", chapter: "" });

  useEffect(() => {
    async function fetchMetadata() {
      try {
        const session = await supabase.auth.getSession();
        console.log("SESSION:", session);
        const token = session.data.session.access_token;
        console.log("TOKEN:", token);

        if (!token) {
          console.error("No active session found");
          return;
        }

        const res = await fetch(
          `http://localhost:8000/api/getMetadata/${bookId}/${chapterId}`,
          { headers: { Authorization: `Bearer ${token}` } },
        );

        if (res.ok) {
          const data = await res.json();

          setMetadata({
            book: data.textbookTitle,
            chapter: data.chapterTitle,
          });
        }
      } catch (err) {
        console.error("Failed to load metadata:", err);
      }
    }
    if (bookId && chapterId) {
      fetchMetadata();
    }
  }, [bookId, chapterId]);

  console.log("TEXTBOOK NAME: ", metadata.book);
  console.log("CHAPTER NAME: ", metadata.chapter);

  useEffect(() => {
    return () => {
      if (pcRef.current) pcRef.current.close();
      if (dcRef.current) dcRef.current.close();
    };
  }, []);

  // allows for pulsating animation: listens to audio buffer and isSpeaking state follows
  useEffect(() => {
    const audio = audioRef.current;
    if (!audio) return;

    let animFrame = null;
    let audioCtx = null;
    let analyser = null;
    let source = null;

    const handleTrack = () => {
      if (!audio.srcObject) return;

      audioCtx = new AudioContext();
      analyser = audioCtx.createAnalyser();
      analyser.fftSize = 256;
      source = audioCtx.createMediaStreamSource(audio.srcObject);
      source.connect(analyser);

      const data = new Uint8Array(analyser.frequencyBinCount);

      const check = () => {
        analyser.getByteFrequencyData(data);
        const avg = data.reduce((a, b) => a + b, 0) / data.length;
        setIsSpeaking(avg > 5); // tweak threshold if needed
        animFrame = requestAnimationFrame(check);
      };

      check();
    };

    audio.addEventListener("play", handleTrack);

    return () => {
      audio.removeEventListener("play", handleTrack);
      cancelAnimationFrame(animFrame);
      audioCtx?.close();
    };
  }, []);

  useEffect(() => {
    transcriptEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [transcripts]);

  const getToken = async () => {
    const res = await fetch("http://localhost:8000/api/session");
    const data = await res.json();
    return data.client_secret.value;
  };

  const startSession = async () => {
    try {
      setIsConnecting(true);
      setStatus("Connecting...");

      const token = await getToken();
      const pc = new RTCPeerConnection();
      pcRef.current = pc;

      const dc = pc.createDataChannel("oai-events");
      dcRef.current = dc;

      // Request mic but start muted
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      stream.getTracks().forEach((track) => {
        track.enabled = false; // muted until PTT pressed
        micTrackRef.current = track;
        pc.addTrack(track, stream);
      });

      pc.ontrack = (e) => {
        if (audioRef.current) {
          audioRef.current.srcObject = e.streams[0];
        }
      };

      dc.onopen = () => {
        setStatus("Connected");
        setIsConnecting(false);

        dc.send(
          JSON.stringify({
            type: "session.update",
            session: {
              input_audio_transcription: { model: "whisper-1" },
              // No turn_detection → manual PTT commit controls when audio ends
              turn_detection: null,
            },
          }),
        );
      };

      dc.onmessage = async (e) => {
        const event = JSON.parse(e.data);
        console.log("FULL EVENT:", event);

        if (
          event.type === "conversation.item.input_audio_transcription.completed"
        ) {
          const userText = event.transcript;
          if (!userText?.trim()) {
            setIsProcessing(false);
            return;
          }

          setTranscripts((prev) => [...prev, { role: "user", text: userText }]);

          let chunks = [];
          try {
            const res = await fetch("http://localhost:8000/api/context", {
              method: "POST",
              headers: { "Content-Type": "application/json" },
              body: JSON.stringify({
                transcript: userText,
                chapter: chapterId,
                textbook: bookId,
              }),
            });

            if (!res.ok) {
              // This will print the exact Pydantic validation error to your browser console
              const errorDetails = await res.json();
              console.error(
                "FastAPI 422 Error:",
                JSON.stringify(errorDetails, null, 2),
              );
            }
            const data = await res.json();
            chunks = data.response;
          } catch (err) {
            console.error("Context fetch failed:", err);
          }

          dc.send(
            JSON.stringify({
              type: "response.create",
              response: {
                modalities: ["audio", "text"],
                input: [
                  {
                    type: "message",
                    role: "user",
                    content: [
                      {
                        type: "input_text",
                        text: `Current Textbook: ${metadata.book} Current Chapter: ${metadata.chapter}`,
                      },
                      {
                        type: "input_text",
                        text: `User query: ${userText}`,
                      },
                      {
                        type: "input_text",
                        text: `Relevant Context: ${chunks}`,
                      },
                      {
                        type: "input_text",
                        text: "Only use the given context if it is relevant to the current conversation. If it is not, reference previous conversion points.",
                      },
                    ],
                  },
                ],
              },
            }),
          );
        }

        if (event.type === "response.audio_transcript.done") {
          setTranscripts((prev) => [
            ...prev,
            { role: "assistant", text: event.transcript },
          ]);
          setIsProcessing(false);
        }
      };

      // SDP handshake
      const offer = await pc.createOffer();
      await pc.setLocalDescription(offer);

      const sdpRes = await fetch(
        "https://api.openai.com/v1/realtime?model=gpt-4o-realtime-preview",
        {
          method: "POST",
          headers: {
            Authorization: `Bearer ${token}`,
            "Content-Type": "application/sdp",
          },
          body: offer.sdp,
        },
      );

      await pc.setRemoteDescription({
        type: "answer",
        sdp: await sdpRes.text(),
      });
    } catch (err) {
      console.error("startSession failed:", err);
      setStatus("Error");
      setIsConnecting(false);
    }
  };

  const handlePTTStart = useCallback(
    (e) => {
      e.preventDefault();
      if (status !== "Connected" || isProcessing || pressingRef.current) return;
      pressingRef.current = true;
      setIsPressing(true);

      // Unmute mic + clear any leftover audio buffer
      if (micTrackRef.current) micTrackRef.current.enabled = true;
      dcRef.current?.send(JSON.stringify({ type: "input_audio_buffer.clear" }));
    },
    [status, isProcessing],
  );

  const handlePTTEnd = useCallback((e) => {
    e.preventDefault();
    if (!pressingRef.current) return;
    pressingRef.current = false;
    setIsPressing(false);
    setIsProcessing(true);

    // Mute mic again and commit what was recorded
    if (micTrackRef.current) micTrackRef.current.enabled = false;
    dcRef.current?.send(JSON.stringify({ type: "input_audio_buffer.commit" }));

    // Fallback: reset processing state after 30 seconds if no response
    setTimeout(() => {
      setIsProcessing(false);
    }, 30000);
  }, []);

  // Keyboard shortcut: Space bar
  useEffect(() => {
    const onKeyDown = (e) => {
      if (e.code === "Space" && e.target === document.body) {
        e.preventDefault();
        handlePTTStart(e);
      }
    };
    const onKeyUp = (e) => {
      if (e.code === "Space") {
        e.preventDefault();
        handlePTTEnd(e);
      }
    };
    window.addEventListener("keydown", onKeyDown);
    window.addEventListener("keyup", onKeyUp);
    return () => {
      window.removeEventListener("keydown", onKeyDown);
      window.removeEventListener("keyup", onKeyUp);
    };
  }, [handlePTTStart, handlePTTEnd]);

  const getStatusColor = () => {
    switch (status) {
      case "Connected":
        return "text-[#4caf50]";
      case "Error":
        return "text-[#f44336]";
      case "Connecting...":
        return "text-[#ff9800]";
      default:
        return "text-[#888]";
    }
  };

  const pttLabel = isPressing
    ? "Recording…"
    : isProcessing
      ? "Processing…"
      : "Hold to talk";

  return (
    <div className="h-full overflow-y-auto border border-neutral-800 bg-[#0a0a0f] text-slate-100 p-8 rounded-3xl flex flex-col">
      {/* Header row */}
      <div className="flex gap-3 items-center">
        <button
          onClick={startSession}
          disabled={isConnecting || status === "Connected"}
          className="px-5 py-2 rounded-lg border border-[#444] bg-[#2a2a2a] text-[#eee] text-[0.95rem] transition-colors hover:bg-[#333] disabled:opacity-40 disabled:cursor-not-allowed select-none"
        >
          {status === "Connected" ? "Connected" : "Connect"}
        </button>
        <span
          className={`text-sm px-2.5 py-1 rounded-md bg-[#2a2a2a] ${getStatusColor()}`}
        >
          {status}
        </span>
      </div>

      {/* PTT Button */}
      <div className="flex flex-col items-center gap-3 my-6">
        <div className="relative flex items-center justify-center">
          {isSpeaking && (
            <span className="absolute w-24 h-24 !rounded-full bg-[#8b5cf6] opacity-20 animate-ping" />
          )}
          <button
            onMouseDown={handlePTTStart}
            onMouseUp={handlePTTEnd}
            onMouseLeave={(e) => {
              if (pressingRef.current) handlePTTEnd(e);
            }}
            onTouchStart={handlePTTStart}
            onTouchEnd={handlePTTEnd}
            disabled={status !== "Connected" || isProcessing}
            className={`
              w-24 h-24 !rounded-full border-2 flex items-center justify-center
              select-none transition-all duration-150 text-2xl
              disabled:opacity-30 disabled:cursor-not-allowed
              ${
                isPressing
                  ? "bg-[#1e3a5f] border-[#378ADD] scale-95 shadow-[0_0_0_6px_rgba(55,138,221,0.15)]"
                  : isProcessing
                    ? "bg-[#1a2a1a] border-[#4caf50] animate-pulse"
                    : "bg-[#1a1a1a] border-[#444] hover:border-[#666] hover:bg-[#222] active:scale-95"
              }
            `}
            aria-label="Push to talk"
          >
            {/* Mic icon via inline SVG */}
            <FaMicrophone
              size={32}
              color={isPressing ? "#90caf9" : isProcessing ? "#a5d6a7" : "#888"}
            />
          </button>
        </div>

        <div className="text-sm text-[#555] text-center leading-tight">
          <span
            className={
              isPressing
                ? "text-[#90caf9]"
                : isProcessing
                  ? "text-[#a5d6a7]"
                  : ""
            }
          >
            {pttLabel}
          </span>
          {!isPressing && !isProcessing && (
            <span className="block text-xs text-[#444] mt-0.5">
              or hold{" "}
              <kbd className="px-1 py-0.5 rounded bg-[#2a2a2a] border border-[#444] font-mono text-[10px] text-[#666]">
                Space
              </kbd>
            </span>
          )}
        </div>
      </div>

      {/* Transcript Panel */}
      <div className="flex flex-col flex-1">
        <div className="bg-[#242424] border border-[#333] rounded-xl p-4 h-[340px] flex flex-col">
          <h2 className="text-sm font-medium text-[#888] uppercase tracking-wide mb-3 border-b border-[#333] pb-2">
            Transcript
          </h2>
          <div className="flex-1 overflow-y-auto text-sm leading-relaxed pr-2">
            {transcripts.length === 0 && (
              <p className="text-[#444] text-sm italic">
                Connect and hold the button to start speaking.
              </p>
            )}
            {transcripts.map((t, i) => (
              <div
                key={i}
                className={`mb-3 px-3 py-2 rounded-md ${
                  t.role === "user"
                    ? "bg-[#1e3a5f] text-[#90caf9]"
                    : "bg-[#1e3a2f] text-[#a5d6a7]"
                }`}
              >
                <div className="text-xs font-semibold opacity-70 mb-0.5 uppercase">
                  {t.role}
                </div>
                <div>{t.text}</div>
              </div>
            ))}
            <div ref={transcriptEndRef} />
          </div>
        </div>
      </div>

      <audio ref={audioRef} autoPlay className="hidden" />
    </div>
  );
}
