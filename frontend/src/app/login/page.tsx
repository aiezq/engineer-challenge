"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import AuthLayout from "@/components/AuthLayout";
import Link from "next/link";

export default function LoginPage() {
    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");
    const [isSubmitting, setIsSubmitting] = useState(false);
    const [error, setError] = useState("");
    const router = useRouter();

    const onSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setError("");
        setIsSubmitting(true);

        try {
            const response = await fetch("/api/auth/login", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({ email, password }),
            });

            const payload = await response.json();
            if (!response.ok) {
                setError(payload.error || "Введены неверные данные");
                return;
            }

            router.replace("/dashboard");
            router.refresh();
        } catch {
            setError("Не удалось выполнить вход");
        } finally {
            setIsSubmitting(false);
        }
    }

    return (
        <AuthLayout
            footerText="Еще не зарегистрированы?"
            footerLinkText="Регистрация"
            footerLinkHref="/register"
        >
            <div className="w-full max-w-sm mx-auto">
                <h1 className="text-3xl font-semibold text-gray-900 mb-8">Войти в систему</h1>

                <form onSubmit={onSubmit} className="space-y-6">

                    <div className="space-y-4">
                        {/* Email Field */}
                        <div className="input-group">
                            <label
                                className={`input-label ${email ? '-translate-y-4 scale-75' : 'translate-y-2 translate-x-1 scale-100'} origin-top-left`}
                                htmlFor="email"
                            >
                                E-mail
                            </label>
                            <input
                                id="email"
                                type="email"
                                value={email}
                                onChange={(e) => setEmail(e.target.value)}
                                placeholder={email ? "" : "Введите e-mail"}
                                className={`input-field ${error ? 'error' : ''}`}
                                required
                            />
                        </div>

                        {/* Password Field */}
                        <div className="input-group">
                            <label
                                className={`input-label ${password ? '-translate-y-4 scale-75' : 'translate-y-2 translate-x-1 scale-100'} origin-top-left`}
                                htmlFor="password"
                            >
                                Пароль
                            </label>
                            <div className="relative">
                                <input
                                    id="password"
                                    type="password"
                                    value={password}
                                    onChange={(e) => setPassword(e.target.value)}
                                    placeholder={password ? "" : "Введите пароль"}
                                    className={`input-field pr-10 ${error ? 'error' : ''}`}
                                    required
                                />
                                {password && (
                                    <button type="button" className="absolute right-0 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600">
                                        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                                            <path d="M12 5C5.63636 5 2 12 2 12C2 12 5.63636 19 12 19C18.3636 19 22 12 22 12C22 12 18.3636 5 12 5Z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                                            <path d="M12 15C13.6569 15 15 13.6569 15 12C15 10.3431 13.6569 9 12 9C10.3431 9 9 10.3431 9 12C9 13.6569 10.3431 15 12 15Z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                                        </svg>
                                    </button>
                                )}
                            </div>
                            {error && <p className="input-error-text">Введены неверные данные</p>}
                        </div>
                    </div>

                    <div className="pt-2">
                        <button type="submit" disabled={isSubmitting} className="btn-primary">
                            {isSubmitting ? "Вход..." : "Войти"}
                        </button>
                    </div>

                    <div className="text-center mt-4">
                        <Link href="/forgot-password" className="text-sm text-orbitto-primary hover:underline font-medium">
                            Забыли пароль?
                        </Link>
                    </div>

                </form>
            </div>
        </AuthLayout>
    );
}
