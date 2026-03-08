import Link from "next/link";

export default function ForgotPasswordPage() {
    return (
        <main className="flex min-h-screen flex-col items-center justify-center p-6 relative overflow-hidden">
            <div className="absolute top-[20%] right-[10%] w-[40%] h-[40%] rounded-full bg-slate-500/10 blur-[100px]" />

            <div className="z-10 w-full max-w-md animate-in fade-in slide-in-from-bottom-4 duration-700">
                <div className="glass-panel p-8 sm:p-10 w-full space-y-8">

                    <div className="text-center space-y-2">
                        <h1 className="text-3xl font-bold tracking-tight text-white">Reset Password</h1>
                        <p className="text-sm text-slate-400">Enter your email and we'll send you a reset link</p>
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
                        </div>

                        <button type="submit" className="btn-primary">
                            Send Reset Link
                        </button>
                    </form>

                    <div className="text-center text-sm text-slate-400 flex flex-col items-center gap-2">
                        <Link href="/login" className="font-medium text-slate-300 hover:text-white transition-all flex items-center gap-1">
                            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="lucide lucide-arrow-left"><path d="m12 19-7-7 7-7" /><path d="M19 12H5" /></svg>
                            Back to log in
                        </Link>
                    </div>
                </div>
            </div>
        </main>
    );
}
