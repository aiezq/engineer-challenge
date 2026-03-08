"use client";

import React from "react";

interface CenteredAuthLayoutProps {
    children: React.ReactNode;
}

export default function CenteredAuthLayout({ children }: CenteredAuthLayoutProps) {
    return (
        <div className="flex min-h-screen w-full bg-white text-gray-900 overflow-hidden font-sans relative">

            {/* Header Logo - Top Left */}
            <div className="absolute top-8 left-8 sm:left-12 flex items-center gap-2 font-bold text-lg tracking-[0.3em] text-gray-800 z-50">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" className="text-gray-900 stroke-current stroke-2">
                    <path d="M12 22C17.5228 22 22 17.5228 22 12C22 6.47715 17.5228 2 12 2C6.47715 2 2 6.47715 2 12" strokeLinecap="round" strokeLinejoin="round" />
                    <path d="M12 8A4 4 0 1 0 12 16A4 4 0 0 0 12 8Z" strokeDasharray="3 3" />
                </svg>
                ORBITTO
            </div>

            {/* Main Content Centered */}
            <div className="flex-1 flex flex-col justify-center items-center px-6">
                {children}
            </div>

        </div>
    );
}
