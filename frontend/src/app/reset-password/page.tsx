"use client";

import { useMemo, useState } from "react";
import { useMutation, useQuery } from "@apollo/client";
import { RESET_PASSWORD_MUTATION, VALIDATE_RESET_TOKEN_QUERY } from "@/lib/graphql";
import { useRouter, useSearchParams } from "next/navigation";
import AuthLayout from "@/components/AuthLayout";

export default function ResetPasswordPage() {
    const [password, setPassword] = useState("");
    const [confirmPassword, setConfirmPassword] = useState("");
    const router = useRouter();
    const searchParams = useSearchParams();
    const token = searchParams.get("token") ?? "";

    const [resetPassword, { loading, error: gqlError }] = useMutation(RESET_PASSWORD_MUTATION, {
        onCompleted: () => {
            router.push("/login?reset=success");
        }
    });
    const { data, loading: tokenLoading } = useQuery(VALIDATE_RESET_TOKEN_QUERY, {
        variables: { token },
        skip: !token,
        fetchPolicy: "network-only",
    });

    const [validationError, setValidationError] = useState("");
    const tokenError = useMemo(() => {
        if (!token) {
            return "Ссылка для сброса пароля неполная";
        }
        if (!tokenLoading && data?.validateResetToken === false) {
            return "Неверный или просроченный токен";
        }
        return "";
    }, [data?.validateResetToken, token, tokenLoading]);

    const onSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        setValidationError("");
        if (tokenError) {
            setValidationError(tokenError);
            return;
        }
        if (password !== confirmPassword) {
            setValidationError("Пароли не совпадают");
            return;
        }
        resetPassword({ variables: { token, newPassword: password } });
    }

    const errorMessage = validationError || tokenError || (gqlError ? "Неверный или просроченный токен" : "");

    return (
        <AuthLayout
            footerText="Вспомнили пароль?"
            footerLinkText="Войти"
            footerLinkHref="/login"
        >
            <div className="w-full max-w-sm mx-auto">
                <h1 className="text-3xl font-semibold text-gray-900 mb-8">Новый пароль</h1>

                <form onSubmit={onSubmit} className="space-y-6">

                    <div className="space-y-4">
                        <div className="input-group">
                            <label
                                className={`input-label ${password ? '-translate-y-4 scale-75' : 'translate-y-2 translate-x-1 scale-100'} origin-top-left`}
                                htmlFor="password"
                            >
                                Новый пароль
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
                            </div>
                        </div>

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
                                    className={`input-field pr-10 ${errorMessage ? 'error' : ''}`}
                                    required
                                />
                            </div>
                            {errorMessage && <p className="input-error-text">{errorMessage}</p>}
                        </div>
                    </div>

                    <div className="pt-2">
                        <button type="submit" disabled={loading || tokenLoading || Boolean(tokenError)} className="btn-primary">
                            {loading ? "Сохранение..." : "Сохранить и войти"}
                        </button>
                    </div>
                </form>
            </div>
        </AuthLayout>
    );
}
