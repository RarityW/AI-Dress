import { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import {
  BarChart3,
  PieChart,
  TrendingUp,
  Sparkles,
  ShieldCheck,
  AlertTriangle,
  Layers,
  CheckCircle2,
  ArrowRight,
  RefreshCw,
  Palette,
  Shirt,
  Lightbulb,
  Award,
  Calendar,
  Compass,
  AlertCircle
} from 'lucide-react';
import { analyticsApi, importSampleWardrobe } from '../services/api';
import { AnalyticsOverviewResponse, DistributionItem } from '../types/analytics';
import { useAuth } from '../contexts/AuthContext';
import LoadingSpinner from '../components/LoadingSpinner';

export default function AnalyticsPage() {
  const { isAuthenticated } = useAuth();
  const navigate = useNavigate();

  const [data, setData] = useState<AnalyticsOverviewResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [importing, setImporting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchAnalytics = async (isManual = false) => {
    if (isManual) setRefreshing(true);
    else setLoading(true);
    setError(null);

    try {
      const res = await analyticsApi.getOverview();
      if (res.data) {
        setData(res.data);
      } else {
        setError('未能获取衣橱数据洞察');
      }
    } catch (err: any) {
      console.error('获取衣橱分析失败:', err);
      setError(err?.response?.data?.message || '获取分析数据失败，请确认后端服务运行正常');
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  useEffect(() => {
    fetchAnalytics();
  }, [isAuthenticated]);

  const handleImportSample = async () => {
    setImporting(true);
    try {
      await importSampleWardrobe();
      await fetchAnalytics(true);
    } catch (err: any) {
      alert(err?.response?.data?.message || '导入示例单品失败');
    } finally {
      setImporting(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-[70vh] flex flex-col items-center justify-center space-y-4">
        <LoadingSpinner />
        <p className="text-zinc-500 dark:text-zinc-400 text-sm">正在计算衣橱数据与资产诊断...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="max-w-md mx-auto my-16 p-6 bg-rose-50 dark:bg-rose-950/30 border border-rose-200 dark:border-rose-900 rounded-2xl text-center">
        <AlertCircle className="w-10 h-10 text-rose-500 mx-auto mb-3" />
        <h3 className="text-lg font-bold text-rose-800 dark:text-rose-200 mb-1">加载失败</h3>
        <p className="text-sm text-rose-600 dark:text-rose-400 mb-4">{error}</p>
        <button
          onClick={() => fetchAnalytics()}
          className="px-4 py-2 bg-rose-600 text-white rounded-xl text-sm font-medium hover:bg-rose-700"
        >
          重试
        </button>
      </div>
    );
  }

  // 1. 未登录引导软墙
  if (!isAuthenticated) {
    return (
      <div className="max-w-4xl mx-auto px-4 py-16 text-center">
        <div className="bg-white dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 rounded-3xl p-10 md:p-14 shadow-sm">
          <div className="w-16 h-16 mx-auto mb-6 bg-indigo-50 dark:bg-indigo-950/40 text-indigo-600 dark:text-indigo-400 rounded-2xl flex items-center justify-center">
            <BarChart3 className="w-8 h-8" />
          </div>
          <h2 className="text-2xl md:text-3xl font-bold text-zinc-900 dark:text-white tracking-tight mb-3">
            解锁您的衣橱数据洞察大屏
          </h2>
          <p className="text-zinc-600 dark:text-zinc-400 max-w-md mx-auto mb-8 text-sm md:text-base leading-relaxed">
            登录后即可查看个人衣橱的资产结构、品类与色彩谱系分布、挖掘百搭之星与闲置衣物，并获取专属胶囊健康度评估。
          </p>
          <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
            <Link
              to="/login"
              className="w-full sm:w-auto px-8 py-3 bg-zinc-900 dark:bg-white text-white dark:text-zinc-900 font-medium rounded-xl hover:opacity-90 transition-opacity shadow-sm"
            >
              立即登录
            </Link>
            <Link
              to="/login"
              state={{ isRegister: true }}
              className="w-full sm:w-auto px-8 py-3 bg-zinc-100 dark:bg-zinc-800 text-zinc-800 dark:text-zinc-200 font-medium rounded-xl hover:bg-zinc-200 dark:hover:bg-zinc-700 transition-colors"
            >
              注册新账号
            </Link>
          </div>
        </div>
      </div>
    );
  }

  // 2. 空衣橱引导
  if (!data || data.metrics.total_items === 0) {
    return (
      <div className="max-w-4xl mx-auto px-4 py-16 text-center">
        <div className="bg-white dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 rounded-3xl p-10 md:p-14 shadow-sm">
          <div className="w-16 h-16 mx-auto mb-6 bg-amber-50 dark:bg-amber-950/40 text-amber-600 dark:text-amber-400 rounded-2xl flex items-center justify-center">
            <Shirt className="w-8 h-8" />
          </div>
          <h2 className="text-2xl font-bold text-zinc-900 dark:text-white mb-2">
            当前衣橱为空，暂无分析数据
          </h2>
          <p className="text-zinc-600 dark:text-zinc-400 max-w-md mx-auto mb-8 text-sm leading-relaxed">
            您的数字衣橱尚未录入任何服饰。您可以上传自己的衣服，或者一键导入 14 件经典四季体验胶囊，即可瞬间生成全景数据大屏！
          </p>
          <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
            <button
              onClick={handleImportSample}
              disabled={importing}
              className="w-full sm:w-auto px-6 py-3 bg-indigo-600 text-white font-medium rounded-xl hover:bg-indigo-700 transition-colors shadow-sm flex items-center justify-center gap-2"
            >
              {importing ? <RefreshCw className="w-4 h-4 animate-spin" /> : <Sparkles className="w-4 h-4" />}
              一键导入体验示例衣橱 (14件)
            </button>
            <Link
              to="/wardrobe"
              className="w-full sm:w-auto px-6 py-3 bg-zinc-100 dark:bg-zinc-800 text-zinc-800 dark:text-zinc-200 font-medium rounded-xl hover:bg-zinc-200 dark:hover:bg-zinc-700 transition-colors"
            >
              前往衣橱手动上传
            </Link>
          </div>
        </div>
      </div>
    );
  }

  const { metrics, categories, seasons, styles, colors, neutral_ratio, versatile_items, idle_items, diagnosis } = data;

  // 辅助渲染品类环形图数据
  const renderDonutChart = (items: DistributionItem[]) => {
    let cumulative = 0;
    const size = 180;
    const strokeWidth = 24;
    const radius = (size - strokeWidth) / 2;
    const circumference = 2 * Math.PI * radius;

    return (
      <div className="relative flex items-center justify-center">
        <svg width={size} height={size} className="transform -rotate-90">
          <circle
            cx={size / 2}
            cy={size / 2}
            r={radius}
            fill="transparent"
            stroke="currentColor"
            strokeWidth={strokeWidth}
            className="text-zinc-100 dark:text-zinc-800"
          />
          {items.map((it) => {
            const strokeDashoffset = circumference - (circumference * it.percentage) / 100;
            const rotateAngle = (cumulative * 360) / 100;
            cumulative += it.percentage;

            return (
              <circle
                key={it.key}
                cx={size / 2}
                cy={size / 2}
                r={radius}
                fill="transparent"
                stroke={it.color || '#6366F1'}
                strokeWidth={strokeWidth}
                strokeDasharray={circumference}
                strokeDashoffset={strokeDashoffset}
                strokeLinecap="round"
                transform={`rotate(${rotateAngle} ${size / 2} ${size / 2})`}
                className="transition-all duration-700 ease-out hover:opacity-80"
              />
            );
          })}
        </svg>
        <div className="absolute flex flex-col items-center justify-center pointer-events-none">
          <span className="text-2xl font-extrabold text-zinc-900 dark:text-white tracking-tight">
            {metrics.total_items}
          </span>
          <span className="text-xs text-zinc-500 dark:text-zinc-400">总件数</span>
        </div>
      </div>
    );
  };

  return (
    <div className="max-w-6xl mx-auto px-4 py-8 space-y-8">
      {/* 1. 顶部 Header */}
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-4 border-b border-zinc-200 dark:border-zinc-800 pb-6">
        <div>
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full text-xs font-medium bg-indigo-50 dark:bg-indigo-950/40 text-indigo-600 dark:text-indigo-400 mb-2">
            <Compass className="w-3.5 h-3.5" />
            Wardrobe Insights & Analytics
          </div>
          <h1 className="text-2xl md:text-3xl font-extrabold text-zinc-900 dark:text-white tracking-tight">
            衣橱数据洞察大屏
          </h1>
          <p className="text-sm text-zinc-500 dark:text-zinc-400 mt-1">
            基于多模态属性聚合与图计算，深度透视您的资产配置、色彩谱系与利用效率
          </p>
        </div>
        <div className="flex items-center gap-3">
          <button
            onClick={() => fetchAnalytics(true)}
            disabled={refreshing}
            className="inline-flex items-center gap-2 px-4 py-2 text-sm font-medium rounded-xl border border-zinc-200 dark:border-zinc-800 bg-white dark:bg-zinc-900 text-zinc-700 dark:text-zinc-300 hover:bg-zinc-50 dark:hover:bg-zinc-800 transition-colors shadow-sm"
          >
            <RefreshCw className={`w-4 h-4 ${refreshing ? 'animate-spin' : ''}`} />
            刷新数据
          </button>
          <Link
            to="/recommend"
            className="inline-flex items-center gap-2 px-4 py-2 text-sm font-medium rounded-xl bg-indigo-600 text-white hover:bg-indigo-700 transition-colors shadow-sm"
          >
            <Sparkles className="w-4 h-4" />
            生成新搭配
          </Link>
        </div>
      </div>

      {/* 2. 核心指标卡 (4 栏) */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        {/* 卡片 1: 衣物总数 */}
        <div className="bg-white dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 rounded-2xl p-5 shadow-sm">
          <div className="flex items-center justify-between mb-3">
            <span className="text-xs font-semibold uppercase tracking-wider text-zinc-500 dark:text-zinc-400">
              衣橱总资产
            </span>
            <div className="w-8 h-8 rounded-lg bg-indigo-50 dark:bg-indigo-950/40 text-indigo-600 dark:text-indigo-400 flex items-center justify-center">
              <Shirt className="w-4 h-4" />
            </div>
          </div>
          <div className="flex items-baseline gap-2">
            <span className="text-3xl font-black text-zinc-900 dark:text-white tracking-tight">
              {metrics.total_items}
            </span>
            <span className="text-xs text-zinc-500">件精选单品</span>
          </div>
          <div className="mt-3 text-xs text-emerald-600 dark:text-emerald-400 flex items-center gap-1 font-medium">
            <ShieldCheck className="w-3.5 h-3.5" />
            4 大基础品类已全覆盖
          </div>
        </div>

        {/* 卡片 2: 穿搭方案 */}
        <div className="bg-white dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 rounded-2xl p-5 shadow-sm">
          <div className="flex items-center justify-between mb-3">
            <span className="text-xs font-semibold uppercase tracking-wider text-zinc-500 dark:text-zinc-400">
              心仪搭配收藏
            </span>
            <div className="w-8 h-8 rounded-lg bg-sky-50 dark:bg-sky-950/40 text-sky-600 dark:text-sky-400 flex items-center justify-center">
              <Sparkles className="w-4 h-4" />
            </div>
          </div>
          <div className="flex items-baseline gap-2">
            <span className="text-3xl font-black text-zinc-900 dark:text-white tracking-tight">
              {metrics.total_outfits}
            </span>
            <span className="text-xs text-zinc-500">套组合方案</span>
          </div>
          <div className="mt-3 text-xs text-zinc-500 dark:text-zinc-400">
            <Link to="/favorites" className="hover:underline text-sky-600 dark:text-sky-400 flex items-center gap-1">
              查看收藏夹 <ArrowRight className="w-3 h-3" />
            </Link>
          </div>
        </div>

        {/* 卡片 3: 衣橱激活利用率 */}
        <div className="bg-white dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 rounded-2xl p-5 shadow-sm">
          <div className="flex items-center justify-between mb-3">
            <span className="text-xs font-semibold uppercase tracking-wider text-zinc-500 dark:text-zinc-400">
              单品激活利用率
            </span>
            <div className="w-8 h-8 rounded-lg bg-emerald-50 dark:bg-emerald-950/40 text-emerald-600 dark:text-emerald-400 flex items-center justify-center">
              <TrendingUp className="w-4 h-4" />
            </div>
          </div>
          <div className="flex items-baseline gap-2">
            <span className="text-3xl font-black text-zinc-900 dark:text-white tracking-tight">
              {metrics.utilization_rate}%
            </span>
            <span className="text-xs text-zinc-500">已入选搭配</span>
          </div>
          <div className="mt-3 w-full bg-zinc-100 dark:bg-zinc-800 rounded-full h-1.5 overflow-hidden">
            <div
              className="bg-emerald-500 h-full rounded-full transition-all duration-700"
              style={{ width: `${Math.min(100, metrics.utilization_rate)}%` }}
            />
          </div>
        </div>

        {/* 卡片 4: 胶囊衣橱健康度 */}
        <div className="bg-white dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 rounded-2xl p-5 shadow-sm">
          <div className="flex items-center justify-between mb-3">
            <span className="text-xs font-semibold uppercase tracking-wider text-zinc-500 dark:text-zinc-400">
              胶囊衣橱健康度
            </span>
            <div className="w-8 h-8 rounded-lg bg-amber-50 dark:bg-amber-950/40 text-amber-600 dark:text-amber-400 flex items-center justify-center">
              <Award className="w-4 h-4" />
            </div>
          </div>
          <div className="flex items-baseline gap-2">
            <span className="text-3xl font-black text-amber-500 tracking-tight">
              {metrics.capsule_score}
            </span>
            <span className="text-xs font-medium px-2 py-0.5 rounded-full bg-amber-100 dark:bg-amber-950/60 text-amber-700 dark:text-amber-300">
              {metrics.capsule_level}
            </span>
          </div>
          <div className="mt-3 text-xs text-zinc-500 dark:text-zinc-400">
            少而精理念，结构趋于均衡
          </div>
        </div>
      </div>

      {/* 3. 中间栏：品类结构环形图 + 真实色彩谱系调色盘 */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* 左侧：品类分布 */}
        <div className="bg-white dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 rounded-2xl p-6 shadow-sm">
          <div className="flex items-center justify-between mb-6">
            <div className="flex items-center gap-2">
              <PieChart className="w-5 h-5 text-indigo-500" />
              <h2 className="text-lg font-bold text-zinc-900 dark:text-white">品类资产构成</h2>
            </div>
            <span className="text-xs text-zinc-500">推荐黄金比例 4:3:2:2</span>
          </div>

          <div className="flex flex-col sm:flex-row items-center justify-around gap-6">
            {renderDonutChart(categories)}

            <div className="w-full sm:w-auto flex-1 space-y-3">
              {categories.map((cat) => (
                <div key={cat.key} className="flex items-center justify-between text-sm">
                  <div className="flex items-center gap-2.5">
                    <span
                      className="w-3 h-3 rounded-full"
                      style={{ backgroundColor: cat.color || '#6366F1' }}
                    />
                    <span className="font-medium text-zinc-700 dark:text-zinc-300">{cat.label}</span>
                  </div>
                  <div className="flex items-center gap-3">
                    <span className="text-zinc-500 dark:text-zinc-400 text-xs">{cat.count} 件</span>
                    <span className="font-bold text-zinc-900 dark:text-white w-12 text-right">
                      {cat.percentage}%
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* 右侧：色彩分布调色盘 */}
        <div className="bg-white dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 rounded-2xl p-6 shadow-sm">
          <div className="flex items-center justify-between mb-6">
            <div className="flex items-center gap-2">
              <Palette className="w-5 h-5 text-sky-500" />
              <h2 className="text-lg font-bold text-zinc-900 dark:text-white">衣橱色彩谱系</h2>
            </div>
            <div className="flex items-center gap-1.5 text-xs font-semibold px-2.5 py-1 rounded-full bg-indigo-50 dark:bg-indigo-950/40 text-indigo-600 dark:text-indigo-400">
              中性底色占比 {neutral_ratio}%
            </div>
          </div>

          {/* 色彩条带 */}
          <div className="w-full h-5 rounded-full overflow-hidden flex shadow-inner mb-6">
            {colors.map((c) => (
              <div
                key={c.color_name}
                style={{
                  width: `${c.percentage}%`,
                  backgroundColor: c.hex_code === '#FFFFFF' ? '#F1F5F9' : c.hex_code,
                }}
                title={`${c.color_name}: ${c.percentage}%`}
                className="h-full transition-all duration-300 hover:opacity-90"
              />
            ))}
          </div>

          {/* 色彩网格明细 */}
          <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
            {colors.slice(0, 6).map((c) => (
              <div
                key={c.color_name}
                className="flex items-center justify-between p-2.5 rounded-xl bg-zinc-50 dark:bg-zinc-800/60 border border-zinc-100 dark:border-zinc-800"
              >
                <div className="flex items-center gap-2">
                  <span
                    className="w-4 h-4 rounded-full border border-zinc-300 dark:border-zinc-600 shadow-sm"
                    style={{ backgroundColor: c.hex_code }}
                  />
                  <span className="text-xs font-medium text-zinc-800 dark:text-zinc-200">
                    {c.color_name}
                  </span>
                </div>
                <span className="text-xs font-bold text-zinc-500 dark:text-zinc-400">
                  {c.percentage}%
                </span>
              </div>
            ))}
          </div>
          <p className="mt-4 text-xs text-zinc-400 dark:text-zinc-500 text-center">
            {neutral_ratio >= 60
              ? '✨ 您的衣橱以黑/白/灰/卡其等百搭中性色为主，容错率极高，便于日常随性互搭。'
              : '🎨 您的衣橱色彩丰富多样，风格张力强，个性鲜明。'}
          </p>
        </div>
      </div>

      {/* 4. 四季与风格倾向栏 */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* 四季覆盖 */}
        <div className="bg-white dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 rounded-2xl p-6 shadow-sm">
          <div className="flex items-center gap-2 mb-4">
            <Calendar className="w-5 h-5 text-amber-500" />
            <h2 className="text-lg font-bold text-zinc-900 dark:text-white">四季穿搭温区覆盖</h2>
          </div>
          <div className="space-y-4">
            {seasons.map((s) => (
              <div key={s.key} className="space-y-1.5">
                <div className="flex justify-between text-xs font-medium">
                  <span className="text-zinc-700 dark:text-zinc-300">{s.label}</span>
                  <span className="text-zinc-500">{s.count} 件适穿 ({s.percentage}%)</span>
                </div>
                <div className="w-full bg-zinc-100 dark:bg-zinc-800 rounded-full h-2 overflow-hidden">
                  <div
                    className="h-full rounded-full transition-all duration-700"
                    style={{ width: `${s.percentage}%`, backgroundColor: s.color || '#6366F1' }}
                  />
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* 风格画像 */}
        <div className="bg-white dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 rounded-2xl p-6 shadow-sm">
          <div className="flex items-center gap-2 mb-4">
            <Layers className="w-5 h-5 text-indigo-500" />
            <h2 className="text-lg font-bold text-zinc-900 dark:text-white">衣橱风格画像</h2>
          </div>
          <div className="space-y-4">
            {styles.slice(0, 4).map((st) => (
              <div key={st.key} className="space-y-1.5">
                <div className="flex justify-between text-xs font-medium">
                  <span className="text-zinc-700 dark:text-zinc-300">{st.label}</span>
                  <span className="text-zinc-500">{st.count} 件 ({st.percentage}%)</span>
                </div>
                <div className="w-full bg-zinc-100 dark:bg-zinc-800 rounded-full h-2 overflow-hidden">
                  <div
                    className="h-full rounded-full bg-indigo-500 transition-all duration-700"
                    style={{ width: `${st.percentage}%` }}
                  />
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* 5. 🌟 百搭王者 TOP 3 */}
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Award className="w-5 h-5 text-amber-500" />
            <h2 className="text-xl font-bold text-zinc-900 dark:text-white">
              衣橱百搭之星 TOP 3
            </h2>
          </div>
          <span className="text-xs text-zinc-500">基于跨季属性与色彩搭配相容度计算</span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
          {versatile_items.map((item, idx) => (
            <div
              key={item.id}
              className="bg-white dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 rounded-2xl p-4 shadow-sm hover:shadow-md transition-shadow relative overflow-hidden flex flex-col justify-between"
            >
              {/* 排名角标 */}
              <div className="absolute top-3 left-3 z-10 w-7 h-7 rounded-full bg-amber-500 text-white font-black text-xs flex items-center justify-center shadow-md">
                #{idx + 1}
              </div>

              <div>
                <div className="aspect-[4/3] w-full rounded-xl overflow-hidden bg-zinc-100 dark:bg-zinc-800 mb-3 relative">
                  {item.image_url ? (
                    <img
                      src={item.image_url}
                      alt={item.sub_category}
                      className="w-full h-full object-cover"
                    />
                  ) : (
                    <div className="w-full h-full flex items-center justify-center text-zinc-400">
                      <Shirt className="w-10 h-10" />
                    </div>
                  )}
                </div>

                <div className="flex items-center justify-between mb-1">
                  <h3 className="font-bold text-zinc-900 dark:text-white text-base">
                    {item.primary_color} · {item.sub_category}
                  </h3>
                  <div className="flex items-center gap-1 text-amber-500 font-bold text-sm">
                    <Sparkles className="w-3.5 h-3.5" />
                    {item.versatility_score}分
                  </div>
                </div>

                <p className="text-xs text-zinc-500 dark:text-zinc-400 line-clamp-2 mb-3">
                  {item.highlight_reason}
                </p>
              </div>

              <div className="pt-2 border-t border-zinc-100 dark:border-zinc-800 flex items-center justify-between text-xs text-zinc-400">
                <span>被收藏搭配引用</span>
                <span className="font-bold text-indigo-600 dark:text-indigo-400">
                  {item.match_count} 次
                </span>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* 6. ⚠️ 闲置单品唤醒清单 */}
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <AlertTriangle className="w-5 h-5 text-rose-500" />
            <h2 className="text-xl font-bold text-zinc-900 dark:text-white">
              沉睡单品唤醒预警
            </h2>
          </div>
          <span className="text-xs text-zinc-500">少于 1 次收藏搭配引用的边缘衣物</span>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {idle_items.map((item) => (
            <div
              key={item.id}
              className="bg-white dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 rounded-2xl p-4 shadow-sm flex flex-col justify-between"
            >
              <div>
                <div className="aspect-square w-full rounded-xl overflow-hidden bg-zinc-100 dark:bg-zinc-800 mb-3 relative">
                  {item.image_url ? (
                    <img
                      src={item.image_url}
                      alt={item.sub_category}
                      className="w-full h-full object-cover grayscale-[30%]"
                    />
                  ) : (
                    <div className="w-full h-full flex items-center justify-center text-zinc-400">
                      <Shirt className="w-8 h-8" />
                    </div>
                  )}
                  <div className="absolute top-2 right-2 px-2 py-0.5 rounded-md bg-zinc-900/70 text-white text-[10px] backdrop-blur-sm">
                    {item.temp_range}
                  </div>
                </div>

                <h3 className="font-bold text-zinc-800 dark:text-zinc-200 text-sm mb-1">
                  {item.primary_color} · {item.sub_category}
                </h3>
                <p className="text-xs text-zinc-500 dark:text-zinc-400 mb-3 leading-relaxed">
                  💡 {item.revive_suggestion}
                </p>
              </div>

              <button
                onClick={() => navigate('/recommend')}
                className="w-full py-2 bg-zinc-50 dark:bg-zinc-800 hover:bg-indigo-50 dark:hover:bg-indigo-950/40 text-zinc-700 dark:text-zinc-300 hover:text-indigo-600 dark:hover:text-indigo-400 font-medium text-xs rounded-xl transition-colors border border-zinc-200 dark:border-zinc-700 flex items-center justify-center gap-1.5"
              >
                <Sparkles className="w-3.5 h-3.5" />
                为它生成推荐穿搭
              </button>
            </div>
          ))}
        </div>
      </div>

      {/* 7. 💡 AI 衣橱诊断与精炼建议 */}
      <div className="bg-gradient-to-br from-indigo-500/5 via-sky-500/5 to-purple-500/5 border border-indigo-200 dark:border-indigo-900/50 rounded-3xl p-6 md:p-8 shadow-sm">
        <div className="flex items-center gap-2.5 mb-4">
          <div className="w-9 h-9 rounded-xl bg-indigo-600 text-white flex items-center justify-center shadow-md">
            <Lightbulb className="w-5 h-5" />
          </div>
          <div>
            <h2 className="text-xl font-bold text-zinc-900 dark:text-white">
              智能衣橱诊断报告
            </h2>
            <p className="text-xs text-zinc-500 dark:text-zinc-400">
              基于精炼胶囊衣橱理念（Capsule Philosophy）与多模态属性匹配诊断
            </p>
          </div>
        </div>

        <p className="text-sm md:text-base text-zinc-700 dark:text-zinc-300 leading-relaxed mb-6 font-medium">
          {diagnosis.summary}
        </p>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* 优势列表 */}
          <div className="bg-white/80 dark:bg-zinc-900/80 backdrop-blur-sm rounded-2xl p-5 border border-zinc-200 dark:border-zinc-800">
            <h3 className="text-sm font-bold text-emerald-700 dark:text-emerald-400 flex items-center gap-1.5 mb-3">
              <CheckCircle2 className="w-4 h-4" />
              当前结构优势
            </h3>
            <ul className="space-y-2.5 text-xs md:text-sm text-zinc-600 dark:text-zinc-400">
              {diagnosis.strengths.map((st, i) => (
                <li key={i} className="flex items-start gap-2">
                  <span className="text-emerald-500 mt-0.5">•</span>
                  <span>{st}</span>
                </li>
              ))}
            </ul>
          </div>

          {/* 增补与优化建议 */}
          <div className="bg-white/80 dark:bg-zinc-900/80 backdrop-blur-sm rounded-2xl p-5 border border-zinc-200 dark:border-zinc-800">
            <h3 className="text-sm font-bold text-indigo-700 dark:text-indigo-400 flex items-center gap-1.5 mb-3">
              <Sparkles className="w-4 h-4" />
              精炼购衣与优化建议
            </h3>
            <ul className="space-y-2.5 text-xs md:text-sm text-zinc-600 dark:text-zinc-400">
              {diagnosis.purchase_suggestions.map((sug, i) => (
                <li key={i} className="flex items-start gap-2">
                  <span className="text-indigo-500 mt-0.5">•</span>
                  <span>{sug}</span>
                </li>
              ))}
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
}
