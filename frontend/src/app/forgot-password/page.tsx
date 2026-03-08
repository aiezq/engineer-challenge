"use client";

import { useState } from "react";
import { useMutation } from "@apollo/client";
import { REQUEST_RESET_MUTATION } from "@/lib/graphql";
import AuthLayout from "@/components/AuthLayout";
import Link from "next/link";

export default function ForgotPasswordPage() {
    const [email, setEmail] = useState("");
    const [submitted, setSubmitted] = useState(false);

    const [requestReset, { loading, error }] = useMutation(REQUEST_RESET_MUTATION, {
        onCompleted: () => {
            setSubmitted(true);
        }
    });

    const onSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        requestReset({ variables: { email } });
    }

    return (
        <AuthLayout
            footerText="Вспомнили пароль?"
            footerLinkText="Войти"
            footerLinkHref="/login"
        >
            <div className="w-full max-w-sm mx-auto">
                <h1 className="text-3xl font-semibold text-gray-900 mb-4">Восстановление</h1>
                <p className="text-gray-500 text-sm mb-8">
                    Введите ваш E-mail, и мы отправим ссылку для сброса пароля.
                </p>

                {submitted ? (
                    <div className="bg-green-50 text-green-700 p-4 rounded-md text-sm mb-6 border border-green-200">
                        Ссылка для восстановления отправлена на ваш почтовый ящик. Пожалуйста, проверьте почту.
                    </div>
                ) : (
                    <form onSubmit={onSubmit} className="space-y-6">

                        <div className="space-y-4">
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
                                {error && <p className="input-error-text">Произошла ошибка, попробуйте снова</p>}
                            </div>
                        </div>

                        <div className="pt-2">
                            <button type="submit" disabled={loading} className="btn-primary">
                                {loading ? "Отправка..." : "Отправить ссылку"}
                            </button>
                        </div>

                        <div className="text-center mt-4 pt-4">
                            <Link href="/login" className="flex items-center justify-center gap-2 text-sm text-gray-500 hover:text-gray-800 transition-colors">
                                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="m15 18-6-6 6-6" /></svg>
                                Вернуться назад
                            </Link>
                        </div>
                    </form>
                )}
            </div>
        </AuthLayout>
    );
}
