import React, { useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import {
  Sparkles,
  Shirt,
  Upload,
  Compass,
  Github,
  Menu,
  X,
  Plus
} from 'lucide-react';
import { cn } from '../lib/utils';

interface NavItem {
  name: string;
  href: string;
  icon: React.ComponentType<{ className?: string }>;
}

const NAV_ITEMS: NavItem[] = [
  { name: '首页', href: '/', icon: Sparkles },
  { name: '数字衣橱', href: '/wardrobe', icon: Shirt },
  { name: '上传衣物', href: '/upload', icon: Upload },
  { name: '穿搭推荐', href: '/recommend', icon: Compass },
];

export default function Layout({ children }: { children: React.ReactNode }) {
  const location = useLocation();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  return (
    <div className="min-h-screen flex flex-col relative overflow-hidden">
      {/* 顶部环境光晕点缀 (Ambient Glow) */}
      <div className="fixed top-0 left-1/4 w-96 h-96 bg-brand-200/30 rounded-full blur-3xl pointer-events-none -z-10 animate-pulse-subtle" />
      <div className="fixed top-32 right-1/4 w-80 h-80 bg-atelier-300/30 rounded-full blur-3xl pointer-events-none -z-10" />

      {/* 悬浮磨砂顶栏 Header */}
      <header className="sticky top-0 z-40 w-full glass-card border-b border-slate-200/70 transition-all">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16 sm:h-20">
            {/* 品牌标识 Logo */}
            <div className="flex items-center gap-3">
              <Link to="/" className="flex items-center gap-2.5 group">
                <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-brand-700 via-brand-600 to-indigo-500 flex items-center justify-center text-white shadow-md shadow-brand-600/20 group-hover:scale-105 transition-transform duration-300">
                  <Sparkles className="w-5 h-5" />
                </div>
                <div>
                  <div className="flex items-center gap-1.5">
                    <span className="text-lg sm:text-xl font-extrabold tracking-tight text-slate-900">
                      衣见 AI
                    </span>
                    <span className="text-[10px] uppercase tracking-wider font-bold px-1.5 py-0.5 rounded bg-slate-900 text-white leading-none">
                      PRO
                    </span>
                  </div>
                  <span className="text-[10px] text-slate-400 font-medium tracking-wider uppercase block">
                    YIJIAN ATELIER
                  </span>
                </div>
              </Link>

              {/* 系统状态小标 */}
              <div className="hidden lg:flex items-center gap-1.5 text-xs text-emerald-700 bg-emerald-50/90 border border-emerald-200/60 px-2.5 py-1 rounded-full ml-4">
                <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-ping" />
                <span className="font-medium">推荐引擎就绪</span>
              </div>
            </div>

            {/* 桌面端胶囊导航栏 */}
            <nav className="hidden md:flex items-center bg-slate-100/80 p-1.5 rounded-2xl border border-slate-200/60">
              {NAV_ITEMS.map((item) => {
                const isActive = location.pathname === item.href || (item.href !== '/' && location.pathname.startsWith(item.href));
                const Icon = item.icon;
                return (
                  <Link
                    key={item.href}
                    to={item.href}
                    className={cn(
                      "flex items-center gap-1.5 px-4 py-2 rounded-xl text-sm font-semibold transition-all duration-200",
                      isActive
                        ? "bg-white text-brand-700 shadow-sm shadow-slate-200"
                        : "text-slate-600 hover:text-slate-900 hover:bg-white/50"
                    )}
                  >
                    <Icon className={cn("w-4 h-4", isActive ? "text-brand-600" : "text-slate-400")} />
                    <span>{item.name}</span>
                  </Link>
                );
              })}
            </nav>

            {/* 桌面端右侧操作区 */}
            <div className="hidden sm:flex items-center gap-3">
              <a
                href="https://github.com/RarityW/AI-Dress"
                target="_blank"
                rel="noreferrer"
                className="w-10 h-10 rounded-xl border border-slate-200 hover:border-slate-300 flex items-center justify-center text-slate-600 hover:text-slate-900 bg-white/80 hover:bg-slate-50 transition-colors shadow-sm"
                title="查看 GitHub 仓库"
              >
                <Github className="w-4 h-4" />
              </a>

              <Link
                to="/upload"
                className="inline-flex items-center gap-1.5 px-4 py-2 rounded-xl text-sm font-semibold text-white bg-slate-900 hover:bg-brand-600 shadow-sm transition-all duration-200 active:scale-95"
              >
                <Plus className="w-4 h-4" />
                <span>录入衣物</span>
              </Link>
            </div>

            {/* 移动端菜单切换按钮 */}
            <div className="flex md:hidden">
              <button
                type="button"
                onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
                className="p-2 rounded-xl text-slate-600 hover:text-slate-900 hover:bg-slate-100 transition-colors"
                aria-label="切换菜单"
              >
                {mobileMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
              </button>
            </div>
          </div>
        </div>

        {/* 移动端抽屉菜单 */}
        {mobileMenuOpen && (
          <div className="md:hidden border-t border-slate-200/80 bg-white/95 backdrop-blur-lg px-4 pt-3 pb-5 space-y-1 animate-fadeIn">
            {NAV_ITEMS.map((item) => {
              const isActive = location.pathname === item.href;
              const Icon = item.icon;
              return (
                <Link
                  key={item.href}
                  to={item.href}
                  onClick={() => setMobileMenuOpen(false)}
                  className={cn(
                    "flex items-center gap-3 px-3.5 py-2.5 rounded-xl text-sm font-semibold transition-colors",
                    isActive
                      ? "bg-brand-50 text-brand-700"
                      : "text-slate-600 hover:bg-slate-50"
                  )}
                >
                  <Icon className={cn("w-4 h-4", isActive ? "text-brand-600" : "text-slate-400")} />
                  <span>{item.name}</span>
                </Link>
              );
            })}
            <div className="pt-3 border-t border-slate-100 flex items-center justify-between">
              <a
                href="https://github.com/RarityW/AI-Dress"
                target="_blank"
                rel="noreferrer"
                className="text-xs text-slate-500 hover:text-slate-800 flex items-center gap-1 py-1"
              >
                <Github className="w-3.5 h-3.5" />
                <span>GitHub 仓库</span>
              </a>
              <span className="text-[11px] text-emerald-600 font-medium flex items-center gap-1">
                <span className="w-1.5 h-1.5 rounded-full bg-emerald-500" />
                系统运行正常
              </span>
            </div>
          </div>
        )}
      </header>

      {/* 页面主视图 */}
      <main className="flex-1 w-full max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 sm:py-10">
        {children}
      </main>

      {/* 上市公司/精品级产品页脚 (Footer) */}
      <footer className="border-t border-slate-200/80 bg-white/60 backdrop-blur-md mt-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-8 mb-10">
            {/* 项目品牌 */}
            <div className="space-y-3 md:col-span-2">
              <div className="flex items-center gap-2">
                <div className="w-7 h-7 rounded-lg bg-slate-900 flex items-center justify-center text-white">
                  <Sparkles className="w-3.5 h-3.5" />
                </div>
                <span className="font-bold text-slate-900 tracking-tight">衣见 AI · YIJIAN AI</span>
              </div>
              <p className="text-xs sm:text-sm text-slate-500 leading-relaxed max-w-md">
                基于多模态视觉感知与自主运筹优化算法的新一代智能穿搭决策系统。
                感知层理解服装多模态特征，决策层自主求解穿搭全局最优。
              </p>
              <div className="flex flex-wrap gap-2 pt-1">
                <span className="text-[11px] px-2.5 py-0.5 rounded-full bg-slate-100 text-slate-600 border border-slate-200/60 font-medium">
                  FastAPI 0.110+
                </span>
                <span className="text-[11px] px-2.5 py-0.5 rounded-full bg-slate-100 text-slate-600 border border-slate-200/60 font-medium">
                  React 18 · TypeScript
                </span>
                <span className="text-[11px] px-2.5 py-0.5 rounded-full bg-slate-100 text-slate-600 border border-slate-200/60 font-medium">
                  自研多目标打分模型
                </span>
              </div>
            </div>

            {/* 功能导航 */}
            <div>
              <h4 className="text-xs font-bold uppercase tracking-wider text-slate-900 mb-3">系统导航</h4>
              <ul className="space-y-2 text-xs sm:text-sm text-slate-500">
                <li><Link to="/wardrobe" className="hover:text-brand-600 transition-colors">我的数字衣橱</Link></li>
                <li><Link to="/upload" className="hover:text-brand-600 transition-colors">智能衣物录入</Link></li>
                <li><Link to="/recommend" className="hover:text-brand-600 transition-colors">情境穿搭推荐</Link></li>
                <li><a href="http://127.0.0.1:8000/docs" target="_blank" rel="noreferrer" className="hover:text-brand-600 transition-colors">OpenAPI 交互控制台</a></li>
              </ul>
            </div>

            {/* 开源致谢与合规 */}
            <div>
              <h4 className="text-xs font-bold uppercase tracking-wider text-slate-900 mb-3">开源与版权</h4>
              <p className="text-xs text-slate-500 leading-relaxed mb-2">
                本项目受开源项目 <a href="https://github.com/tandpfun/wardrobe" target="_blank" rel="noreferrer" className="text-slate-800 underline hover:text-brand-600">tandpfun/wardrobe</a> 启发，遵循 MIT 许可证。
              </p>
              <div className="text-[11px] text-slate-400">
                Copyright © 2026 YIJIAN AI Team.
              </div>
            </div>
          </div>

          <div className="border-t border-slate-100 pt-6 flex flex-col sm:flex-row items-center justify-between text-xs text-slate-400 gap-3">
            <div>
              团队精研合作 · 项目主理人：Zhenqi Wang
            </div>
            <div className="flex items-center gap-4">
              <a href="https://github.com/RarityW/AI-Dress" target="_blank" rel="noreferrer" className="hover:text-slate-600">GitHub 源码</a>
              <span>·</span>
              <span>MIT License</span>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}
