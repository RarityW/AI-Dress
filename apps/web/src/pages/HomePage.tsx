import { Link } from 'react-router-dom';
import {
  Shirt,
  Upload,
  Compass,
  ArrowRight,
  Cpu,
  Thermometer,
  Palette,
  CheckCircle2
} from 'lucide-react';

export default function HomePage() {
  return (
    <div className="space-y-20 pb-16">
      {/* 1. 主视觉区 (Hero Section) */}
      <section className="relative pt-6 sm:pt-12 text-center max-w-4xl mx-auto space-y-6">
        {/* 顶部微徽标 */}
        <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-slate-900/5 border border-slate-900/10 text-xs font-semibold text-slate-800 shadow-sm">
          <span className="flex h-2 w-2 rounded-full bg-brand-600 animate-pulse" />
          <span>《人工智能原理》课程项目 · 自主决策与感知解耦架构</span>
        </div>

        {/* 主标与副标 */}
        <h1 className="text-4xl sm:text-6xl font-black text-slate-900 tracking-tight leading-[1.15]">
          让每一件衣物，<br className="hidden sm:inline" />
          都有<span className="bg-clip-text text-transparent bg-gradient-to-r from-brand-600 via-indigo-600 to-purple-600">被看见的美好</span>。
        </h1>

        <p className="text-base sm:text-lg text-slate-600 max-w-2xl mx-auto leading-relaxed">
          告别每日穿搭选择困难。采用多模态视觉大模型提取服装标准化属性，依托自主研发的
          <strong className="text-slate-900 font-semibold">“气温 × 风格 × 场景 × 色彩”</strong>
          多因素运筹评分引擎，秒级输出最懂你的个性化 TOP-K 搭配方案。
        </p>

        {/* 行动按钮群 */}
        <div className="flex flex-col sm:flex-row items-center justify-center gap-3.5 pt-2">
          <Link
            to="/recommend"
            className="w-full sm:w-auto inline-flex items-center justify-center gap-2 px-7 py-3.5 rounded-xl text-sm sm:text-base font-semibold text-white bg-slate-900 hover:bg-brand-600 shadow-lg shadow-slate-900/15 transition-all duration-200 active:scale-95 group"
          >
            <Compass className="w-5 h-5 group-hover:rotate-45 transition-transform" />
            <span>智能生成今日穿搭</span>
            <ArrowRight className="w-4 h-4 ml-0.5 group-hover:translate-x-1 transition-transform" />
          </Link>

          <Link
            to="/wardrobe"
            className="w-full sm:w-auto inline-flex items-center justify-center gap-2 px-6 py-3.5 rounded-xl text-sm sm:text-base font-semibold text-slate-700 bg-white border border-slate-200 hover:border-slate-300 hover:bg-slate-50 shadow-sm transition-all duration-200"
          >
            <Shirt className="w-5 h-5 text-slate-500" />
            <span>浏览数字衣橱</span>
          </Link>
        </div>

        {/* 核心指标微数据条 (Stats Bar) */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 pt-8 max-w-3xl mx-auto">
          <div className="p-4 rounded-2xl bg-white border border-slate-200/80 shadow-soft text-center">
            <div className="text-2xl sm:text-3xl font-black text-slate-900">4-Factor</div>
            <div className="text-xs text-slate-500 font-medium mt-1">多维度加权运筹决策</div>
          </div>
          <div className="p-4 rounded-2xl bg-white border border-slate-200/80 shadow-soft text-center">
            <div className="text-2xl sm:text-3xl font-black text-brand-600">100%</div>
            <div className="text-xs text-slate-500 font-medium mt-1">核心决策算法纯自研</div>
          </div>
          <div className="p-4 rounded-2xl bg-white border border-slate-200/80 shadow-soft text-center">
            <div className="text-2xl sm:text-3xl font-black text-slate-900">TOP-3</div>
            <div className="text-xs text-slate-500 font-medium mt-1">最优方案与理由输出</div>
          </div>
          <div className="p-4 rounded-2xl bg-white border border-slate-200/80 shadow-soft text-center">
            <div className="text-2xl sm:text-3xl font-black text-emerald-600">&lt; 0.3s</div>
            <div className="text-xs text-slate-500 font-medium mt-1">全链路高速运筹响应</div>
          </div>
        </div>
      </section>

      {/* 2. 核心系统三大入口 (Primary Features) */}
      <section className="space-y-6">
        <div className="flex flex-col sm:flex-row sm:items-end justify-between gap-2 border-b border-slate-200/80 pb-4">
          <div>
            <h2 className="text-2xl font-bold text-slate-900 tracking-tight">全景核心功能</h2>
            <p className="text-sm text-slate-500 mt-1">
              打通“拍照上传 → 特征结构化 → 自主运筹算法 → 情境推荐”完整数据链路
            </p>
          </div>
          <span className="text-xs font-semibold text-brand-600 bg-brand-50 px-3 py-1 rounded-full self-start sm:self-auto">
            一站式衣橱中台
          </span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {/* 卡片 1: 数字衣橱 */}
          <Link
            to="/wardrobe"
            className="group block p-7 rounded-2xl bg-white border border-slate-200/80 shadow-soft card-interactive relative overflow-hidden"
          >
            <div className="w-12 h-12 rounded-xl bg-blue-50 text-blue-600 flex items-center justify-center mb-5 group-hover:scale-110 transition-transform">
              <Shirt className="w-6 h-6" />
            </div>
            <div className="flex items-center justify-between mb-2">
              <h3 className="text-lg font-bold text-slate-900 group-hover:text-brand-600 transition-colors">
                我的数字衣橱
              </h3>
              <ArrowRight className="w-4 h-4 text-slate-300 group-hover:text-brand-600 group-hover:translate-x-1 transition-all" />
            </div>
            <p className="text-sm text-slate-500 leading-relaxed mb-4">
              统一收纳与索引你的所有衣物。支持按上装、下装、外套、鞋履分类筛选，实时掌握色彩与温区库存。
            </p>
            <div className="flex items-center gap-2 text-xs font-medium text-slate-400">
              <span className="px-2 py-0.5 rounded bg-slate-100 text-slate-600">多品类筛选</span>
              <span className="px-2 py-0.5 rounded bg-slate-100 text-slate-600">卡片式总览</span>
            </div>
          </Link>

          {/* 卡片 2: 智能录入 */}
          <Link
            to="/upload"
            className="group block p-7 rounded-2xl bg-white border border-slate-200/80 shadow-soft card-interactive relative overflow-hidden"
          >
            <div className="w-12 h-12 rounded-xl bg-purple-50 text-purple-600 flex items-center justify-center mb-5 group-hover:scale-110 transition-transform">
              <Upload className="w-6 h-6" />
            </div>
            <div className="flex items-center justify-between mb-2">
              <h3 className="text-lg font-bold text-slate-900 group-hover:text-brand-600 transition-colors">
                智能衣物录入
              </h3>
              <ArrowRight className="w-4 h-4 text-slate-300 group-hover:text-brand-600 group-hover:translate-x-1 transition-all" />
            </div>
            <p className="text-sm text-slate-500 leading-relaxed mb-4">
              拖拽上传衣物照片，快速完成主色调、子类别、适宜季节与最低/最高温区标签录入，安全保存在本地。
            </p>
            <div className="flex items-center gap-2 text-xs font-medium text-slate-400">
              <span className="px-2 py-0.5 rounded bg-slate-100 text-slate-600">拖拽上传</span>
              <span className="px-2 py-0.5 rounded bg-slate-100 text-slate-600">属性结构化</span>
            </div>
          </Link>

          {/* 卡片 3: 智能推荐 */}
          <Link
            to="/recommend"
            className="group block p-7 rounded-2xl bg-white border border-slate-200/80 shadow-soft card-interactive relative overflow-hidden ring-1 ring-brand-500/20"
          >
            <div className="absolute top-3 right-3">
              <span className="text-[10px] font-extrabold uppercase px-2 py-0.5 rounded-full bg-brand-600 text-white tracking-wider">
                CORE
              </span>
            </div>
            <div className="w-12 h-12 rounded-xl bg-brand-50 text-brand-600 flex items-center justify-center mb-5 group-hover:scale-110 transition-transform">
              <Compass className="w-6 h-6" />
            </div>
            <div className="flex items-center justify-between mb-2">
              <h3 className="text-lg font-bold text-slate-900 group-hover:text-brand-600 transition-colors">
                情境穿搭推荐
              </h3>
              <ArrowRight className="w-4 h-4 text-slate-300 group-hover:text-brand-600 group-hover:translate-x-1 transition-all" />
            </div>
            <p className="text-sm text-slate-500 leading-relaxed mb-4">
              根据外界实时气温、天气状况与活动场景（通勤、约会、上课、运动），运行自研多目标模型输出全局优选。
            </p>
            <div className="flex items-center gap-2 text-xs font-medium text-slate-400">
              <span className="px-2 py-0.5 rounded bg-brand-100 text-brand-700">TOP-K 评分</span>
              <span className="px-2 py-0.5 rounded bg-brand-100 text-brand-700">理由生成</span>
            </div>
          </Link>
        </div>
      </section>

      {/* 3. 算法原理架构解析 (Why Disentangled Architecture?) */}
      <section className="bg-slate-900 text-white rounded-3xl p-8 sm:p-12 relative overflow-hidden shadow-elevated">
        <div className="absolute -right-20 -bottom-20 w-80 h-80 bg-brand-500/10 rounded-full blur-3xl pointer-events-none" />

        <div className="max-w-3xl space-y-4 mb-8">
          <div className="inline-flex items-center gap-2 text-xs font-bold uppercase tracking-wider text-brand-400">
            <Cpu className="w-4 h-4" />
            <span>核心算法理论依据与架构解耦</span>
          </div>
          <h2 className="text-2xl sm:text-3xl font-extrabold tracking-tight">
            大模型负责视觉感知，自主算法负责运筹决策
          </h2>
          <p className="text-sm sm:text-base text-slate-300 leading-relaxed">
            绝不盲目将穿搭决策完全抛给黑盒大模型。我们坚持“感知与决策彻底解耦”的技术路线，
            确保答辩与工程落地具备严谨的数学模型与学术解释力：
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="p-6 rounded-2xl bg-white/5 border border-white/10 space-y-3">
            <div className="flex items-center gap-2 text-amber-400 font-bold text-sm">
              <Thermometer className="w-4 h-4" />
              <span>1. 气象区间硬约束过滤 (Weather Filtering)</span>
            </div>
            <p className="text-xs text-slate-300 leading-relaxed">
              严格排除适宜温区在 [Tmin - 3℃, Tmax + 3℃] 以外的不适单品。
              在区间内通过偏离度高斯/线性衰减计算单品温度契合度 S_weather。
            </p>
          </div>

          <div className="p-6 rounded-2xl bg-white/5 border border-white/10 space-y-3">
            <div className="flex items-center gap-2 text-indigo-400 font-bold text-sm">
              <Palette className="w-4 h-4" />
              <span>2. 经典色彩拓扑美学 (Color Harmony)</span>
            </div>
            <p className="text-xs text-slate-300 leading-relaxed">
              基于中性色池（黑、白、灰、米、藏青）作为基础百搭框架，全身主色控制在 3 种以内，
              单重点色提亮点睛加分，避免多杂色冲突。
            </p>
          </div>
        </div>

        <div className="mt-8 pt-6 border-t border-white/10 flex flex-col sm:flex-row items-center justify-between gap-4 text-xs text-slate-400">
          <div className="flex items-center gap-4">
            <span className="flex items-center gap-1.5"><CheckCircle2 className="w-4 h-4 text-emerald-400" /> 零幻觉库存匹配</span>
            <span className="flex items-center gap-1.5"><CheckCircle2 className="w-4 h-4 text-emerald-400" /> 权重完全可配置</span>
            <span className="flex items-center gap-1.5"><CheckCircle2 className="w-4 h-4 text-emerald-400" /> 100% 规则透明可解释</span>
          </div>
          <Link to="/recommend" className="text-white hover:text-brand-300 font-semibold flex items-center gap-1">
            <span>立即在推荐页体验算法</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </Link>
        </div>
      </section>
    </div>
  );
}
