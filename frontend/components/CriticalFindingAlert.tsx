"use client";

import { useState } from "react";

interface CriticalFindingAlertProps {
  findings: string[];
}

export default function CriticalFindingAlert({
  findings,
}: CriticalFindingAlertProps) {
  const [dismissed, setDismissed] = useState(false);

  if (findings.length === 0 || dismissed) return null;

  return (
    <div
      role="alert"
      aria-live="assertive"
      className="relative flex items-start gap-4 rounded-xl border-2 border-red-300 bg-red-50 px-5 py-4 shadow-md"
    >
      {/* Icon */}
      <div className="flex-shrink-0 mt-0.5">
        <div className="flex items-center justify-center w-9 h-9 rounded-full bg-red-100 ring-2 ring-red-200">
          <svg
            className="w-5 h-5 text-red-600"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
            strokeWidth={2}
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              d="M12 9v3.75m-9.303 3.376c-.866 1.5.217 3.374 1.948 3.374h14.71c1.73 0 2.813-1.874 1.948-3.374L13.949 3.378c-.866-1.5-3.032-1.5-3.898 0L2.697 16.126zM12 15.75h.007v.008H12v-.008z"
            />
          </svg>
        </div>
      </div>

      {/* Content */}
      <div className="flex-1 min-w-0">
        <h3 className="text-sm font-bold text-red-800 mb-1">
          위험 소견 발견 — 즉각적인 주의 필요
        </h3>
        <ul className="space-y-1">
          {findings.map((finding, idx) => (
            <li
              key={idx}
              className="flex items-start gap-2 text-sm text-red-700"
            >
              <span className="mt-1.5 flex-shrink-0 w-1.5 h-1.5 rounded-full bg-red-500" />
              <span>{finding}</span>
            </li>
          ))}
        </ul>
        <p className="mt-2 text-xs text-red-500 font-medium">
          이 결과는 즉각적인 의료 전문가 검토가 필요합니다.
        </p>
      </div>

      {/* Dismiss button */}
      <button
        onClick={() => setDismissed(true)}
        aria-label="알림 닫기"
        className="flex-shrink-0 ml-auto -mt-1 -mr-1 p-1.5 rounded-lg text-red-400 hover:text-red-600 hover:bg-red-100 transition-colors"
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
    </div>
  );
}
