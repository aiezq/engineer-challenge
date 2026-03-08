import Link from "next/link";

export default function LoginPage() {
    return (
        <main className="flex min-h-screen flex-col items-center justify-center p-6 relative overflow-hidden">
            <div className="absolute top-[-20%] left-[-10%] w-[50%] h-[50%] rounded-full bg-orbitto-primary/20 blur-[120px]" />

            <div className="z-10 w-full max-w-md animate-in fade-in slide-in-from-bottom-4 duration-700">
                <div className="glass-panel p-8 sm:p-10 w-full space-y-8 relative overflow-hidden">
                    <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-transparent via-orbitto-primary to-transparent opacity-50"></div>

                    <div className="text-center space-y-2">
                        <h1 className="text-3xl font-bold tracking-tight text-white">Welcome back</h1>
                        <p className="text-sm text-slate-400">Enter your credentials to access your account</p>
                    </div>

                    <form className="space-y-6">
                        <div className="space-y-4">
                            <div className="space-y-2">
                                <label className="text-sm font-medium text-slate-300" htmlFor="email">Email</label>
                                <input
                                    id="email"
                                    type="email"
                                    placeholder="name@example.com"
                                    className="input-field"
                                    required
                                />
                            </div>

                            <div className="space-y-2">
                                <div className="flex items-center justify-between">
                                    <label className="text-sm font-medium text-slate-300" htmlFor="password">Password</label>
                                    <Link href="/forgot-password" className="text-xs text-orbitto-primary hover:text-orbitto-primary-hover hover:underline transition-all">
                                        Forgot password?
                                    </Link>
                                </div>
                                <input
                                    id="password"
                                    type="password"
                                    placeholder="••••••••"
                                    className="input-field"
                                    required
                                />
                            </div>
                        </div>

                        <button type="submit" className="btn-primary">
                            Sign In
                        </button>
                    </form>

                    <div className="text-center text-sm text-slate-400">
                        Don't have an account?{" "}
                        <Link href="/register" className="font-medium text-orbitto-primary hover:text-orbitto-primary-hover hover:underline transition-all">
                            Sign up
                        </Link>
                    </div>
                </div>
            </div>
        </main>
    );
}
