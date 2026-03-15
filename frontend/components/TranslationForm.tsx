"use client";

import { useState, useRef, useCallback } from "react";
import type { TranslateRequest, LanguageCode, TranslationMode } from "@/lib/api";
import { SAMPLE_REPORTS } from "@/lib/sampleReports";

interface TranslationFormProps {
  onSubmit: (data: TranslateRequest) => void;
  isLoading: boolean;
}

const LANGUAGE_OPTIONS: { value: LanguageCode; label: string }[] = [
  { value: "auto", label: "자동 감지" },
  { value: "en", label: "영어 (English)" },
  { value: "ko", label: "한국어 (Korean)" },
];

const MODE_OPTIONS: { value: TranslationMode; label: string; desc: string }[] =
  [
    {
      value: "translation_only",
      label: "번역만",
      desc: "텍스트 번역만 수행합니다",
    },
    {
      value: "with_explanation",
      label: "번역 + 설명",
      desc: "번역 및 환자 설명을 포함합니다",
    },
    {
      value: "full",
      label: "전체 분석",
      desc: "번역, 설명, 검증을 모두 수행합니다",
    },
  ];

const MAX_CHARS = 10000;

export default function TranslationForm({
  onSubmit,
  isLoading,
}: TranslationFormProps) {
  const [text, setText] = useState("");
  const [sourceLanguage, setSourceLanguage] = useState<LanguageCode>("auto");
  const [mode, setMode] = useState<TranslationMode>("full");
  const [showSamples, setShowSamples] = useState(false);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const charCount = text.length;
  const isOverLimit = charCount > MAX_CHARS;
  const canSubmit = text.trim().length > 10 && !isOverLimit && !isLoading;

  const handleSubmit = useCallback(
    (e: React.FormEvent) => {
      e.preventDefault();
      if (!canSubmit) return;
      onSubmit({
        text: text.trim(),
        source_language: sourceLanguage,
        target_language: "ko",
        mode,
        include_explanation: mode === "with_explanation" || mode === "full",
        include_validation: mode === "full",
      });
    },
    [canSubmit, text, sourceLanguage, mode, onSubmit]
  );

  const loadSample = useCallback((sampleText: string) => {
    setText(sampleText);
    setSourceLanguage("en");
    setShowSamples(false);
    textareaRef.current?.focus();
  }, []);

  const clearText = useCallback(() => {
    setText("");
    textareaRef.current?.focus();
  }, []);

  return (
    <form onSubmit={handleSubmit} className="flex flex-col h-full gap-4">
      {/* Header row */}
      <div className="flex items-center justify-between">
        <h2 className="text-base font-semibold text-slate-700">판독문 입력</h2>
        <div className="relative">
          <button
            type="button"
            onClick={() => setShowSamples((v) => !v)}
            className="inline-flex items-center gap-1.5 text-xs font-medium text-blue-600 hover:text-blue-800 bg-blue-50 hover:bg-blue-100 px-3 py-1.5 rounded-full transition-colors"
          >
            <svg
              className="w-3.5 h-3.5"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
              strokeWidth={2}
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
              />
            </svg>
            샘플 보고서
          </button>

          {/* Sample dropdown */}
          {showSamples && (
            <div className="absolute right-0 top-full mt-2 w-56 bg-white rounded-xl shadow-xl border border-slate-200 z-20 overflow-hidden">
              <div className="px-3 py-2 border-b border-slate-100">
                <p className="text-xs font-semibold text-slate-500 uppercase tracking-wider">
                  샘플 선택
                </p>
              </div>
              <ul>
                {SAMPLE_REPORTS.map((sample) => (
                  <li key={sample.id}>
                    <button
                      type="button"
                      onClick={() => loadSample(sample.text)}
                      className="w-full text-left px-4 py-3 text-sm text-slate-700 hover:bg-blue-50 hover:text-blue-700 transition-colors flex items-center gap-2"
                    >
                      <span className="text-blue-400">
                        <svg
                          className="w-4 h-4"
                          fill="none"
                          viewBox="0 0 24 24"
                          stroke="currentColor"
                          strokeWidth={2}
                        >
                          <path
                            strokeLinecap="round"
                            strokeLinejoin="round"
                            d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z"
                          />
                        </svg>
                      </span>
                      {sample.title}
                    </button>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      </div>

      {/* Textarea */}
      <div className="relative flex-1 min-h-0">
        <textarea
          ref={textareaRef}
          value={text}
          onChange={(e) => setText(e.target.value)}
          placeholder="방사선 판독문을 여기에 붙여넣으세요...

예시:
FINDINGS:
There is a 1.2 cm solid nodule in the right upper lobe...

IMPRESSION:
1. No pulmonary embolism.
2. Suspicious pulmonary nodule requiring follow-up."
          className={`w-full h-full min-h-[280px] resize-none rounded-xl border p-4 text-sm leading-relaxed font-mono text-slate-800 placeholder-slate-400 focus:outline-none focus:ring-2 transition-colors ${
            isOverLimit
              ? "border-red-300 bg-red-50 focus:ring-red-300"
              : "border-slate-300 bg-white focus:ring-blue-400 focus:border-blue-400"
          }`}
          disabled={isLoading}
          spellCheck={false}
        />

        {/* Clear button */}
        {text.length > 0 && !isLoading && (
          <button
            type="button"
            onClick={clearText}
            aria-label="텍스트 지우기"
            className="absolute top-3 right-3 p-1 rounded-md text-slate-400 hover:text-slate-600 hover:bg-slate-100 transition-colors"
          >
            <svg
              className="w-4 h-4"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
              strokeWidth={2}
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                d="M6 18L18 6M6 6l12 12"
              />
            </svg>
          </button>
        )}
      </div>

      {/* Character count */}
      <div className="flex justify-end">
        <span
          className={`text-xs font-medium tabular-nums ${
            isOverLimit
              ? "text-red-500"
              : charCount > MAX_CHARS * 0.8
              ? "text-amber-500"
              : "text-slate-400"
          }`}
        >
          {charCount.toLocaleString()} / {MAX_CHARS.toLocaleString()}자
        </span>
      </div>

      {/* Options row */}
      <div className="grid grid-cols-2 gap-3">
        {/* Language selector */}
        <div className="flex flex-col gap-1.5">
          <label className="text-xs font-semibold text-slate-500 uppercase tracking-wider">
            원문 언어
          </label>
          <div className="relative">
            <select
              value={sourceLanguage}
              onChange={(e) => setSourceLanguage(e.target.value as LanguageCode)}
              disabled={isLoading}
              className="w-full appearance-none bg-white border border-slate-300 rounded-lg px-3 py-2.5 text-sm text-slate-700 focus:outline-none focus:ring-2 focus:ring-blue-400 focus:border-blue-400 cursor-pointer disabled:opacity-60 disabled:cursor-not-allowed pr-8"
            >
              {LANGUAGE_OPTIONS.map((opt) => (
                <option key={opt.value} value={opt.value}>
                  {opt.label}
                </option>
              ))}
            </select>
            <div className="pointer-events-none absolute inset-y-0 right-2.5 flex items-center">
              <svg
                className="w-4 h-4 text-slate-400"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
                strokeWidth={2}
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  d="M19 9l-7 7-7-7"
                />
              </svg>
            </div>
          </div>
        </div>

        {/* Target language (fixed to Korean) */}
        <div className="flex flex-col gap-1.5">
          <label className="text-xs font-semibold text-slate-500 uppercase tracking-wider">
            번역 언어
          </label>
          <div className="bg-slate-100 border border-slate-200 rounded-lg px-3 py-2.5 text-sm text-slate-500 flex items-center gap-2">
            <svg
              className="w-4 h-4 text-blue-400"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
              strokeWidth={2}
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                d="M3 5h12M9 3v2m1.048 9.5A18.022 18.022 0 016.412 9m6.088 9h7M11 21l5-10 5 10M12.751 5C11.783 10.77 8.07 15.61 3 18.129"
              />
            </svg>
            한국어 (Korean)
          </div>
        </div>
      </div>

      {/* Mode selector */}
      <div className="flex flex-col gap-1.5">
        <label className="text-xs font-semibold text-slate-500 uppercase tracking-wider">
          번역 모드
        </label>
        <div className="grid grid-cols-3 gap-2">
          {MODE_OPTIONS.map((opt) => (
            <button
              key={opt.value}
              type="button"
              onClick={() => setMode(opt.value)}
              disabled={isLoading}
              title={opt.desc}
              className={`relative px-3 py-2.5 rounded-lg text-xs font-medium border transition-all ${
                mode === opt.value
                  ? "bg-blue-600 text-white border-blue-600 shadow-sm shadow-blue-200"
                  : "bg-white text-slate-600 border-slate-300 hover:border-blue-300 hover:text-blue-600"
              } disabled:opacity-50 disabled:cursor-not-allowed`}
            >
              {opt.label}
            </button>
          ))}
        </div>
        <p className="text-xs text-slate-400 pl-0.5">
          {MODE_OPTIONS.find((o) => o.value === mode)?.desc}
        </p>
      </div>

      {/* Submit button */}
      <button
        type="submit"
        disabled={!canSubmit}
        className={`flex items-center justify-center gap-2 w-full py-3 rounded-xl text-sm font-semibold transition-all shadow-sm ${
          canSubmit
            ? "bg-blue-600 hover:bg-blue-700 active:bg-blue-800 text-white shadow-blue-200 hover:shadow-md"
            : "bg-slate-100 text-slate-400 cursor-not-allowed"
        }`}
      >
        {isLoading ? (
          <>
            <svg
              className="w-4 h-4 animate-spin"
              fill="none"
              viewBox="0 0 24 24"
            >
              <circle
                className="opacity-25"
                cx="12"
                cy="12"
                r="10"
                stroke="currentColor"
                strokeWidth="4"
              />
              <path
                className="opacity-75"
                fill="currentColor"
                d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"
              />
            </svg>
            번역 중...
          </>
        ) : (
          <>
            <svg
              className="w-4 h-4"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
              strokeWidth={2}
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                d="M3 5h12M9 3v2m1.048 9.5A18.022 18.022 0 016.412 9m6.088 9h7M11 21l5-10 5 10M12.751 5C11.783 10.77 8.07 15.61 3 18.129"
              />
            </svg>
            번역하기
          </>
        )}
      </button>
    </form>
  );
}
