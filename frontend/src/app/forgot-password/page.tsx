"use client";

import { useState } from "react";
import { useMutation } from "@apollo/client";
import { REQUEST_RESET_MUTATION } from "@/lib/graphql";
import CenteredAuthLayout from "@/components/CenteredAuthLayout";
import Link from "next/link";
import { useRouter } from "next/navigation";

export default function ForgotPasswordPage() {
    const [email, setEmail] = useState("");
    const [submitted, setSubmitted] = useState(false);
    const router = useRouter();

    const [requestReset, { loading, error }] = useMutation(REQUEST_RESET_MUTATION, {
        onCompleted: () => {
            setSubmitted(true);
        }
    });

    const onSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        requestReset({ variables: { email } });
    }

    const errorMessage = error ? "Не удалось отправить письмо, попробуйте снова" : "";

    if (submitted) {
        return (
            <CenteredAuthLayout>
                <div className="w-full max-w-md mx-auto text-center animate-in fade-in zoom-in-95 duration-500">
                    <h1 className="text-3xl font-medium text-gray-900 mb-6">Проверьте свою почту</h1>
                    <p className="text-gray-400 text-sm mb-12">
                        Мы отправили на почту письмо с ссылкой для восстановления пароля
                    </p>

                    <button
                        onClick={() => router.push('/login')}
                        className="w-full bg-[#f0f7ff] text-[#3b82f6] hover:bg-[#e0efff] py-4 rounded-md font-medium transition-colors"
                    >
                        Назад в авторизацию
                    </button>
                </div>
            </CenteredAuthLayout>
        );
    }

    return (
        <CenteredAuthLayout>
            <div className="w-full max-w-md mx-auto animate-in fade-in slide-in-from-bottom-4 duration-500">

                <div className="flex items-center gap-4 mb-2">
                    <Link href="/login" className="text-gray-900 hover:text-gray-600 transition-colors">
                        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                            <path d="m15 18-6-6 6-6" />
                        </svg>
                    </Link>
                    <h1 className="text-[28px] font-medium text-[#111827]">Восстановление пароля</h1>
                </div>

                <p className="text-[#9ca3af] text-sm mb-10 pl-10">
                    Укажите адрес почты на который был зарегистрирован аккаунт
                </p>

                <form onSubmit={onSubmit} className="space-y-8">

                    <div className="input-group pt-4">
                        <label
                            className={`input-label ${email ? '-translate-y-4 scale-75' : 'translate-y-2 translate-x-0 scale-100'} origin-top-left`}
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
                            className={`input-field ${errorMessage ? 'error' : ''} !text-base !pb-2`}
                            required
                        />
                        {errorMessage && <p className="input-error-text mt-2">{errorMessage}</p>}
                    </div>

                    <div className="pt-4">
                        <button
                            type="submit"
                            disabled={loading}
                            className="w-full bg-[#f0f7ff] text-[#3b82f6] hover:bg-[#e0efff] disabled:opacity-70 py-4 rounded-md font-medium transition-colors"
                        >
                            {loading ? "Отправка..." : "Восстановить пароль"}
                        </button>
                    </div>

                </form>
            </div>
        </CenteredAuthLayout>
    );
}
