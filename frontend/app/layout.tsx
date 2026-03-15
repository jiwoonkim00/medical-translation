import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "판독문 번역 시스템",
  description: "의료 방사선 판독문 한국어 번역 및 환자 설명 시스템",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="ko">
      <body className="min-h-screen bg-slate-50 antialiased">
        {/* Top Navigation Bar */}
        <nav className="bg-blue-900 text-white shadow-lg">
          <div className="max-w-screen-2xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex items-center justify-between h-16">
              {/* Logo & Title */}
              <div className="flex items-center gap-3">
                <div className="flex items-center justify-center w-9 h-9 bg-blue-700 rounded-lg shadow-inner">
                  <svg
                    className="w-5 h-5 text-blue-100"
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
                </div>
                <div>
                  <h1 className="text-lg font-bold leading-tight tracking-tight">
                    판독문 번역 시스템
                  </h1>
                  <p className="text-blue-300 text-xs leading-tight">
                    Medical Radiology Report Translation
                  </p>
                </div>
              </div>

              {/* Right side info */}
              <div className="hidden sm:flex items-center gap-4">
                <div className="flex items-center gap-2 bg-blue-800 rounded-full px-3 py-1.5">
                  <span className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></span>
                  <span className="text-blue-100 text-xs font-medium">AI 번역 서비스 가동 중</span>
                </div>
                <div className="text-blue-300 text-xs">
                  Claude Sonnet 4.6
                </div>
              </div>
            </div>
          </div>
        </nav>

        {/* Main content */}
        <main className="max-w-screen-2xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          {children}
        </main>

        {/* Footer */}
        <footer className="border-t border-slate-200 bg-white mt-auto">
          <div className="max-w-screen-2xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
            <p className="text-center text-xs text-slate-400">
              본 시스템은 의료 전문가의 검토를 보조하는 도구입니다. 최종 판단은 반드시 의료 전문가가 내려야 합니다.
            </p>
          </div>
        </footer>
      </body>
    </html>
  );
}
