import { useState, useEffect } from 'react';
import { useNavigate, useLocation, Link } from 'react-router-dom';
import { Sparkles, Lock, User, Mail, ArrowRight, AlertCircle } from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';

export default function LoginPage() {
  const navigate = useNavigate();
  const location = useLocation();
  const { login, register, isAuthenticated } = useAuth();

  const [isRegister, setIsRegister] = useState(
    () => !!((location.state as any)?.register || (location.state as any)?.isRegister)
  );
  const [account, setAccount] = useState('');
  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');

  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const from = (location.state as any)?.from?.pathname || '/wardrobe';

  // 已登录则重定向
  useEffect(() => {
    if (isAuthenticated) {
      navigate(from, { replace: true });
    }
  }, [isAuthenticated, navigate, from]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    if (isRegister) {
      if (!account.trim() || !password.trim()) {
        setError('请完整设置登录账号与密码');
        return;
      }
      if (account.trim().length < 3) {
        setError('登录账号长度至少需要 3 个字符');
        return;
      }
      if (!email.trim() || !email.includes('@')) {
        setError('请输入有效的电子邮箱地址');
        return;
      }
      if (password.length < 6) {
        setError('密码长度至少需要 6 个字符');
        return;
      }
      if (password !== confirmPassword) {
        setError('两次输入的密码不一致');
        return;
      }
    } else {
      if (!account.trim() || !password.trim()) {
        setError('请输入您的登录账号（或绑定邮箱）与密码');
        return;
      }
    }

    setLoading(true);
    try {
      if (isRegister) {
        // 用户名仅用于显示，未填写时默认使用账号
        const displayName = username.trim() || account.trim();
        await register(account.trim(), email.trim(), password, displayName);
      } else {
        await login(account.trim(), password);
      }
      navigate(from, { replace: true });
    } catch (err: any) {
      const msg = err.response?.data?.message || err.message || '操作失败，请重试';
      setError(msg);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-[75vh] flex items-center justify-center py-6 px-4">
      <div className="w-full max-w-md">
        {/* 卡片包装 */}
        <div className="glass-card bg-white/90 backdrop-blur-xl border border-slate-200/80 rounded-3xl p-8 sm:p-10 shadow-xl shadow-slate-200/50 relative overflow-hidden">
          {/* 装饰光效 */}
          <div className="absolute top-0 right-0 -mr-16 -mt-16 w-48 h-48 bg-gradient-to-br from-brand-400/20 to-indigo-500/20 rounded-full blur-2xl pointer-events-none" />

          {/* Logo 与标语 */}
          <div className="text-center mb-8">
            <div className="inline-flex items-center justify-center w-14 h-14 rounded-2xl bg-gradient-to-tr from-brand-700 via-brand-600 to-indigo-500 text-white shadow-lg shadow-brand-500/30 mb-4">
              <Sparkles className="w-7 h-7" />
            </div>
            <h1 className="text-2xl font-extrabold text-slate-900 tracking-tight">
              {isRegister ? '加入衣见 AI' : '欢迎回到衣见 AI'}
            </h1>
            <p className="text-sm text-slate-500 mt-1">
              {isRegister ? '开启您的专属多模态数字衣橱' : '探索每日最佳场景穿搭方案'}
            </p>
          </div>

          {/* 切换 Tab */}
          <div role="tablist" aria-label="登录注册模式切换" className="flex bg-slate-100/90 p-1 rounded-2xl mb-6">
            <button
              id="tab-login"
              role="tab"
              aria-selected={!isRegister}
              aria-controls="auth-form"
              type="button"
              onClick={() => {
                setIsRegister(false);
                setError(null);
              }}
              className={`flex-1 py-2 text-sm font-bold rounded-xl transition-colors cursor-pointer ${
                !isRegister
                  ? 'bg-white text-slate-900 shadow-sm'
                  : 'text-slate-500 hover:text-slate-900'
              }`}
            >
              登 录
            </button>
            <button
              id="tab-register"
              role="tab"
              aria-selected={isRegister}
              aria-controls="auth-form"
              type="button"
              onClick={() => {
                setIsRegister(true);
                setError(null);
              }}
              className={`flex-1 py-2 text-sm font-bold rounded-xl transition-colors cursor-pointer ${
                isRegister
                  ? 'bg-white text-slate-900 shadow-sm'
                  : 'text-slate-500 hover:text-slate-900'
              }`}
            >
              注 册
            </button>
          </div>

          {/* 错误提示 */}
          {error && (
            <div
              role="alert"
              aria-live="assertive"
              className="mb-5 p-3.5 rounded-2xl bg-rose-50 border border-rose-200/80 flex items-start gap-2.5 text-rose-700 text-xs animate-shake"
            >
              <AlertCircle className="w-4 h-4 shrink-0 mt-0.5" aria-hidden="true" />
              <span>{error}</span>
            </div>
          )}

          {/* 表单 */}
          <form id="auth-form" onSubmit={handleSubmit} className="space-y-4">
            {/* 登录模式：输入账号或邮箱 */}
            {!isRegister ? (
              <div>
                <div className="flex items-center justify-between mb-1.5">
                  <label
                    htmlFor="login-account"
                    className="block text-xs font-bold text-slate-700 uppercase tracking-wider"
                  >
                    登录账号 / 绑定邮箱
                  </label>
                  <span className="text-[11px] text-slate-400 font-normal">
                    用户名仅作展示，不用于登录
                  </span>
                </div>
                <div className="relative">
                  <User className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" aria-hidden="true" />
                  <input
                    id="login-account"
                    type="text"
                    value={account}
                    onChange={(e) => setAccount(e.target.value)}
                    placeholder="请输入专属登录账号或注册邮箱"
                    autoComplete="username"
                    spellCheck={false}
                    required
                    className="w-full pl-10 pr-4 py-2.5 rounded-xl border border-slate-200 bg-white text-sm text-slate-900 placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-brand-500/20 focus:border-brand-500 transition-colors"
                  />
                </div>
              </div>
            ) : (
              <>
                {/* 注册模式 1：登录账号（与密码强关联） */}
                <div>
                  <div className="flex items-center justify-between mb-1.5">
                    <label
                      htmlFor="register-account"
                      className="block text-xs font-bold text-slate-700 uppercase tracking-wider"
                    >
                      专属登录账号
                    </label>
                    <span className="text-[11px] text-brand-600 font-semibold">
                      ★ 与密码关联，用于系统登录
                    </span>
                  </div>
                  <div className="relative">
                    <User className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" aria-hidden="true" />
                    <input
                      id="register-account"
                      type="text"
                      value={account}
                      onChange={(e) => setAccount(e.target.value)}
                      placeholder="设置登录账号（英文/数字，至少3位）"
                      autoComplete="username"
                      spellCheck={false}
                      required
                      className="w-full pl-10 pr-4 py-2.5 rounded-xl border border-slate-200 bg-white text-sm text-slate-900 placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-brand-500/20 focus:border-brand-500 transition-colors"
                    />
                  </div>
                </div>

                {/* 注册模式 2：用户名/昵称（仅用于显示，不作为登录账号） */}
                <div>
                  <div className="flex items-center justify-between mb-1.5">
                    <label
                      htmlFor="register-username"
                      className="block text-xs font-bold text-slate-700 uppercase tracking-wider"
                    >
                      用户昵称 / 姓名
                    </label>
                    <span className="text-[11px] text-slate-400 font-normal">
                      仅在界面展示，不作为登录账号
                    </span>
                  </div>
                  <div className="relative">
                    <User className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" aria-hidden="true" />
                    <input
                      id="register-username"
                      type="text"
                      value={username}
                      onChange={(e) => setUsername(e.target.value)}
                      placeholder="例如：Zhenqi Wang、时尚达人（选填）"
                      spellCheck={false}
                      className="w-full pl-10 pr-4 py-2.5 rounded-xl border border-slate-200 bg-white text-sm text-slate-900 placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-brand-500/20 focus:border-brand-500 transition-colors"
                    />
                  </div>
                </div>

                {/* 注册模式 3：电子邮箱 */}
                <div>
                  <label
                    htmlFor="login-email"
                    className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1.5"
                  >
                    电子邮箱
                  </label>
                  <div className="relative">
                    <Mail className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" aria-hidden="true" />
                    <input
                      id="login-email"
                      type="email"
                      value={email}
                      onChange={(e) => setEmail(e.target.value)}
                      placeholder="name@example.com"
                      autoComplete="email"
                      spellCheck={false}
                      required
                      className="w-full pl-10 pr-4 py-2.5 rounded-xl border border-slate-200 bg-white text-sm text-slate-900 placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-brand-500/20 focus:border-brand-500 transition-colors"
                    />
                  </div>
                </div>
              </>
            )}

            <div>
              <label
                htmlFor="login-password"
                className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1.5"
              >
                密码
              </label>
              <div className="relative">
                <Lock className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" aria-hidden="true" />
                <input
                  id="login-password"
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder={isRegister ? '至少 6 个字符' : '请输入密码'}
                  autoComplete={isRegister ? 'new-password' : 'current-password'}
                  required
                  className="w-full pl-10 pr-4 py-2.5 rounded-xl border border-slate-200 bg-white text-sm text-slate-900 placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-brand-500/20 focus:border-brand-500 transition-colors"
                />
              </div>
            </div>

            {isRegister && (
              <div>
                <label
                  htmlFor="login-confirm-password"
                  className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1.5"
                >
                  确认密码
                </label>
                <div className="relative">
                  <Lock className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" aria-hidden="true" />
                  <input
                    id="login-confirm-password"
                    type="password"
                    value={confirmPassword}
                    onChange={(e) => setConfirmPassword(e.target.value)}
                    placeholder="再次输入以确认密码"
                    autoComplete="new-password"
                    required
                    className="w-full pl-10 pr-4 py-2.5 rounded-xl border border-slate-200 bg-white text-sm text-slate-900 placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-brand-500/20 focus:border-brand-500 transition-colors"
                  />
                </div>
              </div>
            )}

            <button
              type="submit"
              disabled={loading}
              aria-busy={loading}
              className="w-full mt-2 py-3 rounded-xl bg-gradient-to-r from-brand-600 to-indigo-600 hover:from-brand-700 hover:to-indigo-700 text-white font-bold text-sm shadow-md shadow-brand-500/20 active:scale-[0.99] transition-all flex items-center justify-center gap-2 disabled:opacity-70 disabled:cursor-not-allowed cursor-pointer"
            >
              {loading ? (
                <div
                  aria-hidden="true"
                  className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin motion-reduce:animate-none"
                />
              ) : (
                <>
                  <span>{isRegister ? '立即注册并进入' : '立即登录'}</span>
                  <ArrowRight className="w-4 h-4" aria-hidden="true" />
                </>
              )}
            </button>
          </form>

          {/* 底部保底说明 */}
          <div className="mt-6 pt-5 border-t border-slate-100 text-center">
            <p className="text-xs text-slate-400">
              {isRegister ? '已有账户？' : '还没有账号？'}
              <button
                type="button"
                onClick={() => {
                  setIsRegister(!isRegister);
                  setError(null);
                }}
                className="ml-1 text-brand-600 font-bold hover:underline"
              >
                {isRegister ? '点此登录' : '立即免费注册'}
              </button>
            </p>
          </div>
        </div>

        {/* 快捷返回首页 */}
        <div className="text-center mt-4">
          <Link to="/" className="text-xs text-slate-400 hover:text-slate-600 transition-colors">
            ← 返回主页
          </Link>
        </div>
      </div>
    </div>
  );
}
