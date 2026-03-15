"use client";

import { useState, useCallback } from "react";
import TranslationForm from "@/components/TranslationForm";
import ResultPanel from "@/components/ResultPanel";
import CriticalFindingAlert from "@/components/CriticalFindingAlert";
import {
  translateReport,
  ApiError,
  type TranslateRequest,
  type TranslateResponse,
} from "@/lib/api";

// ─── Toast notification ────────────────────────────────────────────────────

interface Toast {
  id: number;
  type: "error" | "warning" | "success";
  message: string;
}

let toastCounter = 0;

function ToastContainer({
  toasts,
  onDismiss,
}: {
  toasts: Toast[];
  onDismiss: (id: number) => void;
}) {
  if (toasts.length === 0) return null;

  const typeConfig = {
    error: {
      bg: "bg-red-600",
      icon: "M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z",
    },
    warning: {
      bg: "bg-amber-500",
      icon: "M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z",
    },
    success: {
      bg: "bg-green-600",
      icon: "M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z",
    },
  };

  return (
    <div className="fixed bottom-6 right-6 z-50 flex flex-col gap-2 max-w-sm w-full">
      {toasts.map((toast) => {
        const cfg = typeConfig[toast.type];
        return (
          <div
            key={toast.id}
            className={`flex items-start gap-3 ${cfg.bg} text-white px-4 py-3 rounded-xl shadow-xl`}
          >
            <svg
              className="w-5 h-5 flex-shrink-0 mt-0.5"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
              strokeWidth={2}
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                d={cfg.icon}
              />
            </svg>
            <p className="text-sm leading-relaxed flex-1">{toast.message}</p>
            <button
              onClick={() => onDismiss(toast.id)}
              className="flex-shrink-0 text-white/70 hover:text-white ml-2 mt-0.5"
              aria-label="알림 닫기"
            >
              <svg
                className="w-4 h-4"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
                strokeWidth={2.5}
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  d="M6 18L18 6M6 6l12 12"
                />
              </svg>
            </button>
          </div>
        );
      })}
    </div>
  );
}

// ─── Main Page ─────────────────────────────────────────────────────────────

export default function HomePage() {
  const [isLoading, setIsLoading] = useState(false);
  const [result, setResult] = useState<TranslateResponse | null>(null);
  const [toasts, setToasts] = useState<Toast[]>([]);

  const addToast = useCallback(
    (type: Toast["type"], message: string, durationMs = 5000) => {
      const id = ++toastCounter;
      setToasts((prev) => [...prev, { id, type, message }]);
      setTimeout(() => {
        setToasts((prev) => prev.filter((t) => t.id !== id));
      }, durationMs);
    },
    []
  );

  const dismissToast = useCallback((id: number) => {
    setToasts((prev) => prev.filter((t) => t.id !== id));
  }, []);

  const handleSubmit = useCallback(
    async (formData: TranslateRequest) => {
      setIsLoading(true);
      setResult(null);

      try {
        const response = await translateReport(formData);
        setResult(response);

        // Show warning toast if critical findings found
        if (response.critical_findings && response.critical_findings.length > 0) {
          addToast(
            "warning",
            `위험 소견 ${response.critical_findings.length}개가 발견되었습니다. 즉각적인 검토가 필요합니다.`,
            8000
          );
        } else {
          addToast("success", "번역이 완료되었습니다.", 3000);
        }
      } catch (err) {
        console.error("Translation error:", err);

        if (err instanceof ApiError) {
          if (err.status === 0 || err.message.includes("fetch")) {
            addToast(
              "error",
              "서버에 연결할 수 없습니다. 백엔드 서버(localhost:8000)가 실행 중인지 확인하세요.",
              8000
            );
          } else if (err.status === 422) {
            addToast(
              "error",
              "입력 데이터 형식이 올바르지 않습니다. 내용을 확인해 주세요.",
              6000
            );
          } else if (err.status >= 500) {
            addToast(
              "error",
              `서버 오류가 발생했습니다 (${err.status}). 잠시 후 다시 시도해 주세요.`,
              6000
            );
          } else {
            addToast("error", `오류: ${err.message}`, 6000);
          }
        } else if (err instanceof TypeError && String(err).includes("fetch")) {
          addToast(
            "error",
            "네트워크 오류: 서버에 연결할 수 없습니다. 백엔드 서버가 실행 중인지 확인하세요.",
            8000
          );
        } else {
          addToast("error", "알 수 없는 오류가 발생했습니다. 다시 시도해 주세요.", 6000);
        }
      } finally {
        setIsLoading(false);
      }
    },
    [addToast]
  );

  return (
    <>
      {/* Page header */}
      <div className="mb-6">
        <h2 className="text-xl font-bold text-slate-800">
          방사선 판독문 번역
        </h2>
        <p className="text-sm text-slate-500 mt-1">
          의료 판독문을 한국어로 번역하고 환자 설명 및 검증을 제공합니다
        </p>
      </div>

      {/* Critical findings banner */}
      {result && result.critical_findings && result.critical_findings.length > 0 && (
        <div className="mb-5">
          <CriticalFindingAlert findings={result.critical_findings} />
        </div>
      )}

      {/* Main two-panel layout */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 items-start">
        {/* Left panel: Input */}
        <div className="bg-white rounded-2xl shadow-sm border border-slate-200 p-6">
          <TranslationForm onSubmit={handleSubmit} isLoading={isLoading} />
        </div>

        {/* Right panel: Results */}
        <div className="bg-white rounded-2xl shadow-sm border border-slate-200 p-6 min-h-[600px] flex flex-col">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-base font-semibold text-slate-700">번역 결과</h2>
            {result && (
              <div className="flex items-center gap-2">
                {result.critical_findings && result.critical_findings.length > 0 ? (
                  <span className="inline-flex items-center gap-1.5 text-xs font-medium text-red-600 bg-red-50 border border-red-200 px-2.5 py-1 rounded-full">
                    <span className="w-1.5 h-1.5 rounded-full bg-red-500 animate-pulse" />
                    위험 소견
                  </span>
                ) : (
                  <span className="inline-flex items-center gap-1.5 text-xs font-medium text-green-600 bg-green-50 border border-green-200 px-2.5 py-1 rounded-full">
                    <span className="w-1.5 h-1.5 rounded-full bg-green-500" />
                    완료
                  </span>
                )}
              </div>
            )}
          </div>
          <div className="flex-1">
            <ResultPanel result={result} isLoading={isLoading} />
          </div>
        </div>
      </div>

      {/* Info cards row */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mt-6">
        <div className="bg-white rounded-xl border border-slate-200 p-4 flex items-start gap-3">
          <div className="w-9 h-9 rounded-lg bg-blue-100 flex items-center justify-center flex-shrink-0">
            <svg
              className="w-5 h-5 text-blue-600"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
              strokeWidth={2}
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                d="M13 10V3L4 14h7v7l9-11h-7z"
              />
            </svg>
          </div>
          <div>
            <p className="text-sm font-semibold text-slate-700">AI 기반 번역</p>
            <p className="text-xs text-slate-400 mt-0.5 leading-relaxed">
              최신 LLM을 활용한 의학 전문 번역
            </p>
          </div>
        </div>

        <div className="bg-white rounded-xl border border-slate-200 p-4 flex items-start gap-3">
          <div className="w-9 h-9 rounded-lg bg-green-100 flex items-center justify-center flex-shrink-0">
            <svg
              className="w-5 h-5 text-green-600"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
              strokeWidth={2}
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z"
              />
            </svg>
          </div>
          <div>
            <p className="text-sm font-semibold text-slate-700">검증 시스템</p>
            <p className="text-xs text-slate-400 mt-0.5 leading-relaxed">
              번역 품질 및 위험 소견 자동 검증
            </p>
          </div>
        </div>

        <div className="bg-white rounded-xl border border-slate-200 p-4 flex items-start gap-3">
          <div className="w-9 h-9 rounded-lg bg-purple-100 flex items-center justify-center flex-shrink-0">
            <svg
              className="w-5 h-5 text-purple-600"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
              strokeWidth={2}
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z"
              />
            </svg>
          </div>
          <div>
            <p className="text-sm font-semibold text-slate-700">환자 친화적 설명</p>
            <p className="text-xs text-slate-400 mt-0.5 leading-relaxed">
              의학 용어를 쉬운 말로 풀어 설명
            </p>
          </div>
        </div>
      </div>

      {/* Toast notifications */}
      <ToastContainer toasts={toasts} onDismiss={dismissToast} />
    </>
  );
}
