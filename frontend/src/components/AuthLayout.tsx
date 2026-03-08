"use client";

import Link from "next/link";
import React from "react";

interface AuthLayoutProps {
    children: React.ReactNode;
    footerText?: string;
    footerLinkText?: string;
    footerLinkHref?: string;
}

export default function AuthLayout({ children, footerText, footerLinkText, footerLinkHref }: AuthLayoutProps) {
    return (
        <div className="flex min-h-screen w-full bg-white text-gray-900 overflow-hidden font-sans">

            {/* Left Pane - Form */}
            <div className="w-full lg:w-[480px] flex flex-col justify-between border-r border-gray-100 bg-white relative z-10 shadow-[20px_0_30px_rgba(0,0,0,0.02)]">

                {/* Header Logo */}
                <div className="pt-8 px-8 sm:px-12">
                    <div className="flex items-center gap-2 font-bold text-lg tracking-[0.3em] text-gray-800">
                        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" className="text-gray-900 stroke-current stroke-2">
                            <path d="M12 22C17.5228 22 22 17.5228 22 12C22 6.47715 17.5228 2 12 2C6.47715 2 2 6.47715 2 12" strokeLinecap="round" strokeLinejoin="round" />
                            <path d="M12 8A4 4 0 1 0 12 16A4 4 0 0 0 12 8Z" strokeDasharray="3 3" />
                        </svg>
                        ORBITTO
                    </div>
                </div>

                {/* Main Form Content */}
                <div className="flex-1 flex flex-col justify-center px-8 sm:px-12 py-12">
                    {children}
                </div>

                {/* Footer */}
                {footerText && footerLinkHref && (
                    <div className="border-t border-gray-100 p-6 text-center text-sm text-gray-500">
                        {footerText}{" "}
                        <Link href={footerLinkHref} className="text-[#3b82f6] font-medium hover:underline">
                            {footerLinkText}
                        </Link>
                    </div>
                )}
            </div>

            {/* Right Pane - Illustration */}
            <div className="hidden lg:flex flex-1 items-center justify-center relative bg-[#edf1f8] overflow-hidden">

                {/* Large frosted glass sphere */}
                <div className="relative w-[500px] h-[500px] rounded-full z-10 border border-white/40 shadow-[-10px_-10px_30px_rgba(255,255,255,0.8),10px_10px_30px_rgba(0,0,0,0.05)] bg-white/20 backdrop-blur-xl flex items-center justify-center">

                    {/* Inner soft glow */}
                    <div className="absolute inset-2 rounded-full border border-white/20"></div>

                    {/* Small Blue Sphere 1 (Top Right) */}
                    <div className="absolute top-[-10px] right-[40px] w-20 h-20 rounded-full bg-gradient-to-br from-[#8aafff] via-[#4d6bfe] to-[#2c4df7] shadow-[inset_-5px_-5px_15px_rgba(0,0,0,0.2),inset_5px_5px_15px_rgba(255,255,255,0.4),0_10px_20px_rgba(77,107,254,0.3)] z-0 transform translate-x-1/2 -translate-y-1/2"></div>

                    {/* Small Blue Sphere 2 (Middle Left) */}
                    <div className="absolute top-[40%] left-[-20px] w-16 h-16 rounded-full bg-gradient-to-br from-[#8aafff] via-[#4d6bfe] to-[#2c4df7] shadow-[inset_-5px_-5px_15px_rgba(0,0,0,0.2),inset_5px_5px_15px_rgba(255,255,255,0.4),0_10px_20px_rgba(77,107,254,0.3)] z-20 transform -translate-x-1/2 -translate-y-1/2"></div>

                    {/* Small Blue Sphere 3 (Bottom Right) */}
                    <div className="absolute bottom-[20px] right-[60px] w-24 h-24 rounded-full bg-gradient-to-br from-[#8aafff] via-[#4d6bfe] to-[#2c4df7] shadow-[inset_-5px_-5px_15px_rgba(0,0,0,0.2),inset_5px_5px_15px_rgba(255,255,255,0.4),0_10px_20px_rgba(77,107,254,0.3)] z-20 transform translate-x-1/2 translate-y-1/2"></div>

                </div>

            </div>

        </div>
    );
}
