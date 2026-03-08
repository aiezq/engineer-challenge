"use client";

import Link from "next/link";

export default function Home() {
  return (
    <div className="flex min-h-screen w-full bg-white text-gray-900 overflow-hidden font-sans">

      {/* Left Pane - Content */}
      <div className="w-full lg:w-1/2 flex flex-col justify-between bg-white relative z-10 p-8 sm:p-16 lg:p-24 shadow-[20px_0_30px_rgba(0,0,0,0.02)]">

        {/* Header Logo */}
        <div className="flex items-center gap-2 font-bold text-lg tracking-[0.3em] text-gray-800 mb-16">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" className="text-gray-900 stroke-current stroke-2">
            <path d="M12 22C17.5228 22 22 17.5228 22 12C22 6.47715 17.5228 2 12 2C6.47715 2 2 6.47715 2 12" strokeLinecap="round" strokeLinejoin="round" />
            <path d="M12 8A4 4 0 1 0 12 16A4 4 0 0 0 12 8Z" strokeDasharray="3 3" />
          </svg>
          ORBITTO
        </div>

        <div className="flex-1 flex flex-col justify-center animate-in fade-in slide-in-from-bottom-8 duration-700 max-w-xl">
          <h1 className="text-5xl md:text-6xl font-bold tracking-tight text-gray-900 leading-[1.1] mb-6">
            Платформа <br />
            <span className="text-[#3b82f6]">Аутентификации</span>
          </h1>

          <p className="text-lg text-gray-500 mb-12">
            Современный сервис аутентификации, построенный с использованием Next.js (Фронтенд) и Python/FastAPI (Бекенд/GraphQL). Реализует принципы DDD, CQRS и IaC.
          </p>

          <div className="flex flex-col sm:flex-row gap-4">
            <Link href="/login" className="btn-primary !px-8 !py-4 text-base shadow-[0_4px_14px_0_rgba(59,130,246,0.39)] hover:shadow-[0_6px_20px_rgba(59,130,246,0.23)]">
              Войти в систему
            </Link>
            <Link href="/register" className="inline-flex justify-center items-center px-8 py-4 border border-gray-200 text-gray-700 bg-white hover:bg-gray-50 hover:text-gray-900 rounded-md font-medium transition-colors">
              Регистрация
            </Link>
          </div>
        </div>
      </div>

      {/* Right Pane - Illustration */}
      <div className="hidden lg:flex flex-1 items-center justify-center relative bg-[#edf1f8] overflow-hidden">

        {/* Large frosted glass sphere */}
        <div className="relative w-[600px] h-[600px] rounded-full z-10 border border-white/40 shadow-[-10px_-10px_30px_rgba(255,255,255,0.8),10px_10px_30px_rgba(0,0,0,0.05)] bg-white/20 backdrop-blur-xl flex items-center justify-center">

          <div className="absolute inset-2 rounded-full border border-white/20"></div>

          {/* Spheres */}
          <div className="absolute top-[-10px] right-[40px] w-24 h-24 rounded-full bg-gradient-to-br from-[#8aafff] via-[#4d6bfe] to-[#2c4df7] shadow-[inset_-5px_-5px_15px_rgba(0,0,0,0.2),inset_5px_5px_15px_rgba(255,255,255,0.4),0_10px_20px_rgba(77,107,254,0.3)] z-0 transform translate-x-1/2 -translate-y-1/2 animate-bounce flex"></div>

          <div className="absolute top-[40%] left-[-20px] w-20 h-20 rounded-full bg-gradient-to-br from-[#8aafff] via-[#4d6bfe] to-[#2c4df7] shadow-[inset_-5px_-5px_15px_rgba(0,0,0,0.2),inset_5px_5px_15px_rgba(255,255,255,0.4),0_10px_20px_rgba(77,107,254,0.3)] z-20 transform -translate-x-1/2 -translate-y-1/2 animate-pulse flex"></div>

          <div className="absolute bottom-[20px] right-[60px] w-28 h-28 rounded-full bg-gradient-to-br from-[#8aafff] via-[#4d6bfe] to-[#2c4df7] shadow-[inset_-5px_-5px_15px_rgba(0,0,0,0.2),inset_5px_5px_15px_rgba(255,255,255,0.4),0_10px_20px_rgba(77,107,254,0.3)] z-20 transform translate-x-1/2 translate-y-1/2"></div>
        </div>
      </div>
    </div>
  );
}
