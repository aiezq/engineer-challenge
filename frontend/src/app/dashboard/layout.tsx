import Link from "next/link";
import { ReactNode } from "react";
import { cookies } from "next/headers";
import { redirect } from "next/navigation";
import { ACCESS_TOKEN_COOKIE } from "@/lib/server/backend";

export default async function DashboardLayout({ children }: { children: ReactNode }) {
    const cookieStore = await cookies();
    if (!cookieStore.get(ACCESS_TOKEN_COOKIE)?.value) {
        redirect("/login");
    }

    const navItems = [
        { name: "Внутри биржи", href: "/dashboard", active: true },
        { name: "Между биржами", href: "#", active: false },
        { name: "DEX-арбитраж", href: "#", active: false },
    ];

    return (
        <div className="flex h-screen bg-[#f8f9fc] font-sans text-gray-900 overflow-hidden">

            {/* Sidebar */}
            <aside className="w-[260px] bg-white border-r border-[#eaecf0] flex flex-col justify-between shrink-0 h-full">
                <div>
                    {/* Logo */}
                    <div className="h-[72px] flex items-center px-6">
                        <Link href="/" className="flex items-center gap-2 font-bold text-lg tracking-[0.25em] text-[#111827]">
                            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" className="text-gray-900 stroke-current stroke-2">
                                <path d="M12 22C17.5228 22 22 17.5228 22 12C22 6.47715 17.5228 2 12 2C6.47715 2 2 6.47715 2 12" strokeLinecap="round" strokeLinejoin="round" />
                                <path d="M12 8A4 4 0 1 0 12 16A4 4 0 0 0 12 8Z" strokeDasharray="3 3" />
                            </svg>
                            ORBITTO
                        </Link>
                    </div>

                    {/* Navigation */}
                    <nav className="mt-4 flex flex-col gap-1">
                        {navItems.map((item, idx) => (
                            <Link
                                key={idx}
                                href={item.href}
                                className={`flex items-center gap-3 px-6 py-3 border-l-[3px] transition-colors ${item.active
                                    ? "border-[#3b82f6] text-[#3b82f6] bg-[#f0f7ff]/50 font-medium"
                                    : "border-transparent text-[#667085] hover:bg-gray-50 hover:text-gray-900"
                                    }`}
                            >
                                {item.active ? (
                                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                                        <circle cx="12" cy="12" r="7" stroke="currentColor" strokeWidth="2.5" />
                                        <circle cx="12" cy="12" r="3" fill="currentColor" />
                                    </svg>
                                ) : (
                                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                                        <path d="M8 7h8M8 12h8M8 17h8M4 7h2M4 12h2M4 17h2" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
                                    </svg>
                                )}
                                {item.name}
                            </Link>
                        ))}
                    </nav>
                </div>

                {/* Bottom actions */}
                <div className="mb-6 px-6">
                    <Link href="#" className="flex items-center gap-3 text-[#667085] hover:text-gray-900 font-medium py-2">
                        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                            <polygon points="3 11 22 2 13 21 11 13 3 11" />
                        </svg>
                        Помощь
                    </Link>
                </div>
            </aside>

            {/* Main Content Area */}
            <main className="flex-1 flex flex-col h-full overflow-hidden">
                {children}
            </main>

        </div>
    );
}
