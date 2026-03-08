"use client";

import { useState } from "react";
import { useMutation } from "@apollo/client";
import { REGISTER_MUTATION } from "@/lib/graphql";
import { useRouter } from "next/navigation";
import AuthLayout from "@/components/AuthLayout";
import Link from "next/link";

const PASSWORD_HINT =
    "Минимум 12 символов, по одной заглавной, строчной букве и цифре, без пробелов по краям.";

function getRegisterErrorMessage(message: string | undefined): string {
    if (!message) {
        return "";
    }
    if (message.includes("already exists")) {
        return "Этот e-mail уже зарегистрирован";
    }
    if (message.includes("Invalid email")) {
        return "Введите корректный e-mail";
    }
    if (message.includes("at least 12 characters")) {
        return "Пароль должен быть не короче 12 символов";
    }
    if (message.includes("uppercase")) {
        return "Пароль должен содержать хотя бы одну заглавную букву";
    }
    if (message.includes("lowercase")) {
        return "Пароль должен содержать хотя бы одну строчную букву";
    }
    if (message.includes("digit")) {
        return "Пароль должен содержать хотя бы одну цифру";
    }
    if (message.includes("longer than 72")) {
        return "Пароль не должен быть длиннее 72 символов";
    }
    if (message.includes("whitespace")) {
        return "Пароль не должен начинаться или заканчиваться пробелом";
    }
    return "Не удалось завершить регистрацию, попробуйте еще раз";
}

export default function RegisterPage() {
    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");
    const [confirmPassword, setConfirmPassword] = useState("");
    const router = useRouter();

    const [register, { loading, error: gqlError }] = useMutation(REGISTER_MUTATION, {
        onCompleted: () => {
            router.push("/login");
        }
    });

    const [validationError, setValidationError] = useState("");

    const onSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        setValidationError("");
        if (password !== confirmPassword) {
            setValidationError("Пароли не совпадают");
            return;
        }
        if (password !== password.trim()) {
            setValidationError("Пароль не должен начинаться или заканчиваться пробелом");
            return;
        }
        register({ variables: { email, password } });
    }

    const errorMessage = validationError
        || getRegisterErrorMessage(gqlError?.message);

    return (
        <AuthLayout
            footerText="Уже есть аккаунт?"
            footerLinkText="Войти"
            footerLinkHref="/login"
        >
            <div className="w-full max-w-sm mx-auto">
                <h1 className="text-3xl font-semibold text-gray-900 mb-8">Регистрация в системе</h1>

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
                                className={`input-field ${errorMessage ? 'error' : ''}`}
                                required
                            />
                            {errorMessage && <p className="input-error-text">{errorMessage}</p>}
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
                                    className={`input-field pr-10 ${errorMessage ? 'error' : ''}`}
                                    required
                                />
                                {password && (
                                    <button type="button" className="absolute right-0 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600">
                                        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M12 5C5.63636 5 2 12 2 12C2 12 5.63636 19 12 19C18.3636 19 22 12 22 12C22 12 18.3636 5 12 5Z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" /><path d="M12 15C13.6569 15 15 13.6569 15 12C15 10.3431 13.6569 9 12 9C10.3431 9 9 10.3431 9 12C9 13.6569 10.3431 15 12 15Z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" /></svg>
                                    </button>
                                )}
                            </div>
                            <p className="mt-2 text-xs text-gray-400">{PASSWORD_HINT}</p>
                        </div>

                        {/* Confirm Password Field */}
                        <div className="input-group">
                            <label
                                className={`input-label ${confirmPassword ? '-translate-y-4 scale-75' : 'translate-y-2 translate-x-1 scale-100'} origin-top-left`}
                                htmlFor="confirm_password"
                            >
                                Повторите пароль
                            </label>
                            <div className="relative">
                                <input
                                    id="confirm_password"
                                    type="password"
                                    value={confirmPassword}
                                    onChange={(e) => setConfirmPassword(e.target.value)}
                                    placeholder={confirmPassword ? "" : "Повторите пароль"}
                                    className={`input-field pr-10 ${validationError ? 'error' : ''}`}
                                    required
                                />
                                {confirmPassword && (
                                    <button type="button" className="absolute right-0 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600">
                                        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M12 5C5.63636 5 2 12 2 12C2 12 5.63636 19 12 19C18.3636 19 22 12 22 12C22 12 18.3636 5 12 5Z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" /><path d="M12 15C13.6569 15 15 13.6569 15 12C15 10.3431 13.6569 9 12 9C10.3431 9 9 10.3431 9 12C9 13.6569 10.3431 15 12 15Z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" /></svg>
                                    </button>
                                )}
                            </div>
                            {validationError && <p className="input-error-text">{validationError}</p>}
                        </div>
                    </div>

                    <div className="pt-2">
                        <button type="submit" disabled={loading} className="btn-primary">
                            {loading ? "Регистрация..." : "Зарегистрироваться"}
                        </button>
                    </div>

                    <div className="text-center text-xs text-gray-400 mt-6 px-4">
                        Зарегистрировавшись пользователь принимает условия <Link href="#" className="underline">договора оферты</Link> и <Link href="#" className="underline">политики конфиденциальности</Link>
                    </div>

                </form>
            </div>
        </AuthLayout>
    );
}
