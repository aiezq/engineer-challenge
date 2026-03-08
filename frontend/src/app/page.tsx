import Link from "next/link";

export default function Home() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-6 md:p-24 relative overflow-hidden">
      {/* Decorative background elements */}
      <div className="absolute top-[-10%] left-[-10%] w-[40%] h-[40%] rounded-full bg-orbitto-primary/20 blur-[120px]" />
      <div className="absolute bottom-[-10%] right-[-10%] w-[40%] h-[40%] rounded-full bg-indigo-500/20 blur-[120px]" />

      <div className="z-10 flex flex-col items-center max-w-3xl text-center space-y-8 animate-in fade-in slide-in-from-bottom-8 duration-1000">
        <div className="inline-flex items-center justify-center p-3 mb-4 rounded-full bg-white/5 border border-white/10 backdrop-blur-md">
          <span className="text-sm font-medium tracking-wide text-indigo-300">Orbitto Authentication System</span>
        </div>

        <h1 className="text-5xl md:text-7xl font-extrabold tracking-tight text-transparent bg-clip-text bg-gradient-to-r from-white to-slate-400">
          Secure, Modern <br /> <span className="text-orbitto-primary">Identity Platform</span>
        </h1>

        <p className="text-xl text-slate-400 max-w-2xl leading-relaxed">
          A demonstration of DDD, CQRS, and IaC architectures bundled with an ultra-premium Next.js frontend experience.
        </p>

        <div className="flex flex-col sm:flex-row gap-4 mt-8 w-full sm:w-auto">
          <Link href="/login" className="glass-panel px-8 py-4 text-center font-semibold text-white hover:bg-white/10 transition-all border-orbitto-primary/30 hover:border-orbitto-primary shadow-[0_0_20px_rgba(99,102,241,0.2)] hover:shadow-[0_0_30px_rgba(99,102,241,0.4)]">
            Sign In to Account
          </Link>
          <Link href="/register" className="glass-panel px-8 py-4 text-center font-semibold text-slate-300 hover:text-white hover:bg-white/5 transition-all">
            Create an Account
          </Link>
        </div>
      </div>
    </main>
  );
}
