"use client";

import React, { useEffect } from "react";
import { useQuery } from "@apollo/client";
import { useRouter } from "next/navigation";
import { ME_QUERY } from "@/lib/graphql";

// Mock data generator based on the screenshot
const generateMockData = (bankName: string, bankColor: string) => {
    return [
        { id: 1, profit: "1,04 %", profitColor: "text-green-500", liquidity: "Хорошая ликв.", buyRole: "M", buyAsset: "USDT", buyProvider: bankName, buyProviderColor: bankColor, sellAsset: "USDT", sellProvider: "Binance", arrowType: "dotted", buyAsset2: "BTC", buyProvider2: "Binance", sellAsset2: "BTC", sellProvider2: "ЮMoney", sellProvider2Color: "text-purple-600", sellRole: "T", upArrow: true },
        { id: 2, profit: "1,04 %", profitColor: "text-green-500", liquidity: "Хорошая ликв.", buyRole: "M", buyAsset: "USDT", buyProvider: bankName, buyProviderColor: bankColor, sellAsset: "USDT", sellProvider: "Binance", arrowType: "solid", buyAsset2: "BTC", buyProvider2: "Binance", sellAsset2: "BTC", sellProvider2: "ЮMoney", sellProvider2Color: "text-purple-600", sellRole: "T", upArrow: true },
        { id: 3, profit: "1,78 %", profitColor: "text-green-500", liquidity: "Хорошая ликв.", buyRole: "M", buyAsset: "USDT", buyProvider: bankName, buyProviderColor: bankColor, sellAsset: "USDT", sellProvider: "Binance", arrowType: "solid", buyAsset2: "BUSD", buyProvider2: "Binance", sellAsset2: "BUSD", sellProvider2: "ЮMoney", sellProvider2Color: "text-purple-600", sellRole: "T", upArrow: true },
        { id: 4, profit: "-1,32 %", profitColor: "text-red-500", liquidity: "Хорошая ликв.", buyRole: "M", buyAsset: "USDT", buyProvider: bankName, buyProviderColor: bankColor, sellAsset: "USDT", sellProvider: "Binance", arrowType: "solid", buyAsset2: "BNB", buyProvider2: "Binance", sellAsset2: "BNB", sellProvider2: "ЮMoney", sellProvider2Color: "text-purple-600", sellRole: "T", upArrow: true },
        { id: 5, profit: "1,17 %", profitColor: "text-green-500", liquidity: "Средняя ликв.", buyRole: "M", buyAsset: "USDT", buyProvider: bankName, buyProviderColor: bankColor, sellAsset: "USDT", sellProvider: "Binance", arrowType: "solid", buyAsset2: "ETH", buyProvider2: "Binance", sellAsset2: "ETH", sellProvider2: "ЮMoney", sellProvider2Color: "text-purple-600", sellRole: "T", upArrow: true },
        { id: 6, profit: "-0,45 %", profitColor: "text-red-500", liquidity: "Плохая ликв.", buyRole: "M", buyAsset: "USDT", buyProvider: bankName, buyProviderColor: bankColor, sellAsset: "USDT", sellProvider: "Binance", arrowType: "solid", buyAsset2: "RUB", buyProvider2: "Binance", sellAsset2: "RUB", sellProvider2: "ЮMoney", sellProvider2Color: "text-purple-600", sellRole: "T", upArrow: true },
        { id: 7, profit: "0,27 %", profitColor: "text-green-500", liquidity: "Плохая ликв.", buyRole: "M", buyAsset: "USDT", buyProvider: bankName, buyProviderColor: bankColor, sellAsset: "USDT", sellProvider: "Binance", arrowType: "solid", buyAsset2: "SHIB", buyProvider2: "Binance", sellAsset2: "SHIB", sellProvider2: "ЮMoney", sellProvider2Color: "text-purple-600", sellRole: "T", upArrow: true },
        { id: 8, profit: "0,38 %", profitColor: "text-green-500", liquidity: "Хорошая ликв.", buyRole: "M", buyAsset: "BUSD", buyProvider: bankName, buyProviderColor: bankColor, sellAsset: "BUSD", sellProvider: "Binance", arrowType: "solid", buyAsset2: "USDT", buyProvider2: "Binance", sellAsset2: "USDT", sellProvider2: "ЮMoney", sellProvider2Color: "text-purple-600", sellRole: "T", upArrow: true },
    ];
};

const mockGroups = [
    { title: "ТИНЬКОФФ - ЮMONEY", items: generateMockData("Тинькофф", "text-amber-500") },
    { title: "РОСБАНК - ЮMONEY", items: generateMockData("Росбанк", "text-red-600") },
];

export default function DashboardPage() {
    const router = useRouter();
    const { data, loading, error } = useQuery(ME_QUERY, {
        fetchPolicy: "network-only",
    });

    useEffect(() => {
        if (error) {
            router.replace("/login");
        }
    }, [error, router]);

    const handleLogout = async () => {
        await fetch("/api/auth/logout", { method: "POST" });
        router.replace("/login");
        router.refresh();
    };

    if (loading) {
        return (
            <div className="flex flex-1 items-center justify-center bg-[#f8f9fc] text-sm text-gray-500">
                Загружаем данные аккаунта...
            </div>
        );
    }

    if (!data?.me) {
        return null;
    }

    return (
        <div className="flex-1 overflow-y-auto bg-[#f8f9fc]">

            {/* Top Header */}
            <header className="flex items-center justify-between px-8 py-4 bg-[#f8f9fc]">
                <div className="flex items-center gap-2 text-sm text-[#3b82f6] bg-[#f0f7ff] px-3 py-1.5 rounded-full font-medium cursor-pointer">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                        <polyline points="23 4 23 10 17 10"></polyline>
                        <path d="M20.49 15a9 9 0 1 1-2.12-9.36L23 10"></path>
                    </svg>
                    Обновлено только что
                </div>

                <div className="flex items-center gap-4">
                    <button className="bg-[#eef4ff] text-[#3b82f6] font-medium text-sm px-4 py-2 rounded-full">
                        Pro-версия
                    </button>
                    <div className="relative group">
                        <div className="flex items-center gap-2 cursor-pointer pb-2 -mb-2">
                            <div className="w-8 h-8 bg-gray-200 rounded-full flex items-center justify-center text-gray-500">
                                <span className="text-xs font-semibold uppercase">{data.me.email[0]}</span>
                            </div>
                            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="text-gray-400 group-hover:rotate-180 transition-transform duration-200"><path d="m6 9 6 6 6-6" /></svg>
                        </div>

                        {/* Dropdown Menu */}
                        <div className="absolute right-0 top-full pt-1 opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-200 z-50">
                            <div className="w-48 bg-white border border-gray-100 rounded-lg shadow-lg py-1 overflow-hidden">
                                <div className="px-4 py-3 text-xs text-gray-500 border-b border-gray-100">
                                    {data.me.email}
                                </div>
                                <button
                                    onClick={handleLogout}
                                    className="w-full text-left px-4 py-2.5 text-sm text-red-600 hover:bg-red-50 flex items-center gap-2 transition-colors"
                                >
                                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4" /><polyline points="16 17 21 12 16 7" /><line x1="21" x2="9" y1="12" y2="12" /></svg>
                                    Выйти из аккаунта
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            </header>

            {/* Tabs and Sort */}
            <div className="px-8 border-b border-gray-200 bg-[#f8f9fc] flex items-center justify-between">
                <div className="flex items-center gap-8 text-sm font-medium text-gray-400">
                    <button className="py-4 hover:text-gray-900 transition-colors">Taker-Taker</button>
                    <button className="py-4 text-gray-900 border-b-2 border-gray-900">Taker-Maker</button>
                    <button className="py-4 hover:text-gray-900 transition-colors">Maker-Taker</button>
                    <button className="py-4 hover:text-gray-900 transition-colors">Maker-Maker</button>
                </div>

                <button className="flex items-center gap-1 text-sm font-medium text-gray-700 hover:text-gray-900 py-4">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="m6 9 6 6 6-6" /></svg>
                    По порядку
                </button>
            </div>

            {/* Filters */}
            <div className="px-8 py-4 flex gap-3">
                {['Сумма', 'Спред', 'Способ пополнения', 'Токен'].map((filter) => (
                    <button key={filter} className="flex items-center gap-2 px-4 py-2 bg-gray-100 rounded-md text-sm font-medium text-gray-700 hover:bg-gray-200 transition-colors">
                        {filter}
                        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="text-gray-500"><path d="m6 9 6 6 6-6" /></svg>
                    </button>
                ))}
            </div>

            {/* Main List Content */}
            <div className="px-8 pb-12">
                {mockGroups.map((group, gIdx) => (
                    <div key={gIdx} className="mb-8">
                        <h2 className="text-xs font-semibold text-gray-400 mb-4 uppercase tracking-wider">{group.title}</h2>

                        <div className="flex flex-col gap-2">
                            {group.items.map((row) => (
                                <div key={row.id} className="bg-white rounded-lg p-4 flex items-center shadow-sm border border-gray-100 text-sm">

                                    {/* Profit & Liquidity */}
                                    <div className="w-[120px] shrink-0">
                                        <div className={`font-medium ${row.profitColor}`}>{row.profit}</div>
                                        <div className="text-xs text-gray-400 mt-0.5">{row.liquidity}</div>
                                    </div>

                                    {/* Buy Role Icon */}
                                    <div className="w-[40px] shrink-0 flex flex-col items-center">
                                        <div className="w-6 h-6 rounded-full bg-gray-100 border border-gray-200 flex items-center justify-center text-[10px] font-bold text-gray-500 relative">
                                            <svg className="absolute -bottom-1 -right-1 w-3 h-3 text-gray-400 bg-white rounded-full" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3"><path d="m19 12-7 7-7-7" /></svg>
                                            {row.buyRole}
                                        </div>
                                    </div>

                                    {/* Buy Asset Context */}
                                    <div className="flex-1 grid grid-cols-[1fr_auto_1fr] items-center gap-4 pl-4 pr-12">

                                        {/* Part 1: Buy */}
                                        <div className="flex flex-col items-start min-w-[100px]">
                                            <span className="font-semibold text-gray-900">{row.buyAsset}</span>
                                            <span className={`text-xs ${row.buyProviderColor} mt-0.5`}>{row.buyProvider}</span>
                                        </div>

                                        {/* Dotted separator */}
                                        <div className="flex-1 flex items-center justify-center text-gray-300 px-4 min-w-[80px]">
                                            ------------------
                                        </div>

                                        {/* Part 1: Sell/Transfer */}
                                        <div className="flex flex-col items-end text-right min-w-[100px]">
                                            <span className="font-semibold text-gray-900">{row.sellAsset}</span>
                                            <span className="text-xs text-gray-400 mt-0.5">{row.sellProvider}</span>
                                        </div>

                                    </div>

                                    {/* Connection Arrow */}
                                    <div className="w-[40px] shrink-0 flex justify-center text-gray-400">
                                        {row.arrowType === "solid" ? (
                                            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M5 12h14M12 5l7 7-7 7" /></svg>
                                        ) : (
                                            <span className="text-gray-300">...</span>
                                        )}
                                    </div>

                                    {/* Sell Asset Context */}
                                    <div className="flex-1 grid grid-cols-[1fr_auto_1fr] items-center gap-4 pl-8 pr-8">

                                        {/* Part 2: Buy */}
                                        <div className="flex flex-col items-start min-w-[100px]">
                                            <span className="font-semibold text-gray-900">{row.buyAsset2}</span>
                                            <span className="text-xs text-gray-400 mt-0.5">{row.buyProvider2}</span>
                                        </div>

                                        {/* Dotted separator */}
                                        <div className="flex-1 flex items-center justify-center text-gray-300 px-4 min-w-[80px]">
                                            ------------------
                                        </div>

                                        {/* Part 2: Final Sell */}
                                        <div className="flex flex-col items-end text-right min-w-[100px]">
                                            <span className="font-semibold text-gray-900">{row.sellAsset2}</span>
                                            <span className={`text-xs ${row.sellProvider2Color} mt-0.5`}>{row.sellProvider2}</span>
                                        </div>

                                    </div>

                                    {/* Sell Role Icon */}
                                    <div className="w-[40px] shrink-0 flex flex-col items-center">
                                        <div className="w-6 h-6 rounded-full bg-gray-100 border border-gray-200 flex items-center justify-center text-[10px] font-bold text-gray-500 relative">
                                            <svg className="absolute -top-1 -right-1 w-3 h-3 text-gray-400 bg-white rounded-full" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3"><path d="m5 12 7-7 7 7" /></svg>
                                            {row.sellRole}
                                        </div>
                                    </div>

                                </div>
                            ))}
                        </div>

                        {/* Show More Button */}
                        <button className="w-full mt-2 py-3 bg-gray-200/60 hover:bg-gray-200 text-gray-700 text-sm font-medium rounded-lg transition-colors flex items-center justify-center gap-2">
                            Показать всё
                            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="m6 9 6 6 6-6" /></svg>
                        </button>

                    </div>
                ))}
            </div>

        </div>
    );
}
