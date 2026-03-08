import Link from "next/link";

export default function ResetPasswordPage() {
    return (
        <main className="flex min-h-screen flex-col items-center justify-center p-6 relative overflow-hidden">
            <div className="absolute bottom-[20%] left-[10%] w-[40%] h-[40%] rounded-full bg-orbitto-primary/10 blur-[100px]" />

            <div className="z-10 w-full max-w-md animate-in fade-in slide-in-from-bottom-4 duration-700">
                <div className="glass-panel p-8 sm:p-10 w-full space-y-8">

                    <div className="text-center space-y-2">
                        <h1 className="text-3xl font-bold tracking-tight text-white">Create New Password</h1>
                        <p className="text-sm text-slate-400">Please enter your new password below</p>
                    </div>

                    <form className="space-y-6">
                        <div className="space-y-4">
                            <div className="space-y-2">
                                <label className="text-sm font-medium text-slate-300" htmlFor="password">New Password</label>
                                <input
                                    id="password"
                                    type="password"
                                    placeholder="Must be at least 8 characters"
                                    className="input-field"
                                    required
                                />
                            </div>
                            <div className="space-y-2">
                                <label className="text-sm font-medium text-slate-300" htmlFor="confirm_password">Confirm New Password</label>
                                <input
                                    id="confirm_password"
                                    type="password"
                                    placeholder="Confirm your new password"
                                    className="input-field"
                                    required
                                />
                            </div>
                        </div>

                        <button type="submit" className="btn-primary">
                            Set New Password
                        </button>
                    </form>

                </div>
            </div>
        </main>
    );
}
