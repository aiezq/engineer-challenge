import Link from "next/link";

export default function RegisterPage() {
    return (
        <main className="flex min-h-screen flex-col items-center justify-center p-6 relative overflow-hidden">
            <div className="absolute bottom-[-20%] right-[-10%] w-[50%] h-[50%] rounded-full bg-indigo-500/20 blur-[120px]" />

            <div className="z-10 w-full max-w-md animate-in fade-in slide-in-from-bottom-4 duration-700">
                <div className="glass-panel p-8 sm:p-10 w-full space-y-8 relative overflow-hidden">
                    <div className="absolute top-0 right-0 w-full h-1 bg-gradient-to-l from-transparent via-violet-500 to-transparent opacity-50"></div>

                    <div className="text-center space-y-2">
                        <h1 className="text-3xl font-bold tracking-tight text-white">Create an account</h1>
                        <p className="text-sm text-slate-400">Join Orbitto and get started securely</p>
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
                                <label className="text-sm font-medium text-slate-300" htmlFor="password">Password</label>
                                <input
                                    id="password"
                                    type="password"
                                    placeholder="Must be at least 8 characters"
                                    className="input-field"
                                    required
                                />
                            </div>
                            <div className="space-y-2">
                                <label className="text-sm font-medium text-slate-300" htmlFor="confirm_password">Confirm Password</label>
                                <input
                                    id="confirm_password"
                                    type="password"
                                    placeholder="Confirm your password"
                                    className="input-field"
                                    required
                                />
                            </div>
                        </div>

                        <button type="submit" className="btn-primary">
                            Create Account
                        </button>
                    </form>

                    <div className="text-center text-sm text-slate-400">
                        Already have an account?{" "}
                        <Link href="/login" className="font-medium text-orbitto-primary hover:text-violet-400 hover:underline transition-all">
                            Sign in
                        </Link>
                    </div>
                </div>
            </div>
        </main>
    );
}
