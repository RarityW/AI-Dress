import { Link } from 'react-router-dom';

export default function NotFoundPage() {
  return (
    <div className="min-h-[60vh] flex flex-col justify-center items-center px-4 sm:px-6 lg:px-8">
      <div className="text-center max-w-md mx-auto space-y-4">
        <h1 className="text-8xl sm:text-9xl font-black text-brand-600 tracking-tight tabular-nums">404</h1>
        <h2 className="text-2xl sm:text-3xl font-extrabold text-slate-900 tracking-tight">页面未找到</h2>
        <p className="text-sm text-slate-500 text-pretty">抱歉，我们找不到您要访问的页面。该页面可能已被移动或链接已失效。</p>
        <div className="pt-4">
          <Link
            to="/"
            className="inline-flex items-center justify-center px-6 py-3 rounded-xl text-sm font-semibold text-white bg-slate-900 hover:bg-brand-600 shadow-md shadow-slate-900/10 active:scale-95 transition-all"
          >
            返回系统首页
          </Link>
        </div>
      </div>
    </div>
  );
}
