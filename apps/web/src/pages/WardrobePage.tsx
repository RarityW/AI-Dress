import { useState, useEffect, useMemo } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import {
  Shirt,
  Plus,
  Search,
  Thermometer,
  Sparkles,
  ArrowRight,
  AlertCircle
} from 'lucide-react';
import { getClothingList } from '../services/api';
import { ClothingItem } from '../types/clothing';
import LoadingSpinner from '../components/LoadingSpinner';

const CATEGORIES = [
  { label: '全部单品', value: '' },
  { label: '上装', value: 'top' },
  { label: '下装', value: 'bottom' },
  { label: '外套', value: 'coat' },
  { label: '鞋履', value: 'shoes' },
  { label: '配饰', value: 'accessory' },
];

const CATEGORY_ICONS: Record<string, string> = {
  top: '👕',
  bottom: '👖',
  coat: '🧥',
  shoes: '👟',
  accessory: '🧢',
};

const CATEGORY_NAMES: Record<string, string> = {
  top: '上装',
  bottom: '下装',
  coat: '外套',
  shoes: '鞋履',
  accessory: '配饰',
};

export default function WardrobePage() {
  const [items, setItems] = useState<ClothingItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeCategory, setActiveCategory] = useState<string>('');
  const [searchQuery, setSearchQuery] = useState('');
  const navigate = useNavigate();

  const fetchItems = async (category: string) => {
    setLoading(true);
    setError(null);
    try {
      const response = await getClothingList(category ? { category } : {});
      if ((response.success || response.code === 200) && response.data) {
        setItems(response.data.items || []);
      } else {
        setError(response.message || '获取衣橱列表失败');
      }
    } catch (err: any) {
      console.error(err);
      setError('无法连接到后端服务，请确认服务已启动');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchItems(activeCategory);
  }, [activeCategory]);

  // 客户端辅助搜索过滤
  const filteredItems = useMemo(() => {
    if (!searchQuery.trim()) return items;
    const q = searchQuery.toLowerCase();
    return items.filter(
      (item) =>
        item.sub_category.toLowerCase().includes(q) ||
        item.primary_color.toLowerCase().includes(q) ||
        item.style.toLowerCase().includes(q)
    );
  }, [items, searchQuery]);

  // 统计各品类数据
  const categoryCounts = useMemo(() => {
    const counts: Record<string, number> = { total: items.length };
    for (const item of items) {
      counts[item.category] = (counts[item.category] || 0) + 1;
    }
    return counts;
  }, [items]);

  return (
    <div className="space-y-8 pb-16 max-w-7xl mx-auto">
      {/* 头部标题与快捷行动 */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 border-b border-slate-200/80 pb-6">
        <div>
          <h1 className="text-3xl font-extrabold text-slate-900 tracking-tight flex items-center gap-2.5">
            <Shirt className="w-8 h-8 text-brand-600" />
            我的数字衣橱
          </h1>
          <p className="mt-1.5 text-sm text-slate-500">
            数字化收纳你的所有日常穿搭单品，实时掌控衣橱色彩与温区库存。
          </p>
        </div>

        <div className="flex items-center gap-3">
          <Link
            to="/recommend"
            className="inline-flex items-center gap-1.5 px-4 py-2.5 rounded-xl text-sm font-semibold text-brand-700 bg-brand-50 hover:bg-brand-100 transition-colors shadow-sm"
          >
            <Sparkles className="w-4 h-4 text-brand-600" />
            <span>获取穿搭推荐</span>
          </Link>

          <Link
            to="/upload"
            className="inline-flex items-center gap-1.5 px-4 py-2.5 rounded-xl text-sm font-semibold text-white bg-slate-900 hover:bg-brand-600 shadow-md shadow-slate-900/10 transition-all duration-200 active:scale-95"
          >
            <Plus className="w-4 h-4" />
            <span>录入新衣物</span>
          </Link>
        </div>
      </div>

      {/* 筛选与搜索工具条 */}
      <div className="bg-white rounded-2xl border border-slate-200/80 p-4 shadow-soft flex flex-col md:flex-row items-center justify-between gap-4">
        {/* 类别胶囊选项卡 */}
        <div className="flex items-center gap-1.5 overflow-x-auto w-full md:w-auto pb-1 md:pb-0">
          {CATEGORIES.map((cat) => {
            const isActive = activeCategory === cat.value;
            const count = cat.value ? categoryCounts[cat.value] || 0 : categoryCounts.total;
            return (
              <button
                key={cat.value}
                type="button"
                onClick={() => setActiveCategory(cat.value)}
                className={`px-3.5 py-1.5 rounded-xl text-xs sm:text-sm font-semibold whitespace-nowrap transition-all flex items-center gap-1.5 ${
                  isActive
                    ? 'bg-slate-900 text-white shadow-sm'
                    : 'text-slate-600 hover:text-slate-900 hover:bg-slate-100'
                }`}
              >
                <span>{cat.label}</span>
                {count !== undefined && (
                  <span
                    className={`text-[11px] px-1.5 py-0.2 rounded-full font-mono ${
                      isActive ? 'bg-white/20 text-white' : 'bg-slate-200/60 text-slate-600'
                    }`}
                  >
                    {count}
                  </span>
                )}
              </button>
            );
          })}
        </div>

        {/* 搜索框 */}
        <div className="relative w-full md:w-64">
          <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            placeholder="搜索款式、颜色或风格..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-9 pr-4 py-2 text-xs sm:text-sm rounded-xl border border-slate-200 focus:outline-none focus:ring-2 focus:ring-brand-500/30 focus:border-brand-500 transition-all bg-slate-50/50"
          />
        </div>
      </div>

      {/* 主展示区 */}
      {loading ? (
        <div className="py-24 text-center space-y-3">
          <LoadingSpinner />
          <p className="text-sm text-slate-500 font-medium animate-pulse">
            正在加载数字衣橱单品库...
          </p>
        </div>
      ) : error ? (
        <div className="p-8 rounded-2xl bg-red-50 border border-red-200 text-center space-y-3">
          <AlertCircle className="w-8 h-8 text-red-500 mx-auto" />
          <p className="text-sm text-red-700 font-medium">{error}</p>
          <button
            onClick={() => fetchItems(activeCategory)}
            className="text-xs font-semibold text-red-700 underline hover:text-red-900"
          >
            点击重试
          </button>
        </div>
      ) : filteredItems.length === 0 ? (
        <div className="bg-white rounded-3xl border border-slate-200/80 p-12 sm:p-16 text-center space-y-4 shadow-soft">
          <div className="w-16 h-16 rounded-2xl bg-slate-100 flex items-center justify-center mx-auto text-3xl">
            🧥
          </div>
          <div className="max-w-md mx-auto space-y-1">
            <h3 className="text-lg font-bold text-slate-900">
              {searchQuery ? '没有找到符合条件的单品' : '衣橱当前还是空的'}
            </h3>
            <p className="text-xs sm:text-sm text-slate-500">
              {searchQuery
                ? '尝试更换关键词搜索，或清除筛选条件'
                : '录入你的第一件衣物（上装、下装、外套），即刻解锁 AI 智能穿搭推荐！'}
            </p>
          </div>
          <div className="pt-2">
            <Link
              to="/upload"
              className="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl text-sm font-semibold text-white bg-slate-900 hover:bg-brand-600 shadow-md transition-all active:scale-95"
            >
              <Plus className="w-4 h-4" />
              <span>上传第一件衣物</span>
            </Link>
          </div>
        </div>
      ) : (
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-5">
          {filteredItems.map((item) => {
            const categoryName = CATEGORY_NAMES[item.category] || item.category;
            const icon = CATEGORY_ICONS[item.category] || '👗';

            return (
              <div
                key={item.id}
                onClick={() => navigate(`/wardrobe/${item.id}`)}
                className="group bg-white rounded-2xl border border-slate-200/80 shadow-soft overflow-hidden card-interactive cursor-pointer flex flex-col"
              >
                {/* 图片封面 */}
                <div className="aspect-[4/5] bg-slate-100 relative overflow-hidden flex items-center justify-center">
                  {item.image_url ? (
                    <img
                      src={item.image_url}
                      alt={item.sub_category}
                      className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
                    />
                  ) : (
                    <div className="text-5xl opacity-40 group-hover:scale-110 transition-transform">
                      {icon}
                    </div>
                  )}

                  {/* 顶部悬浮品类标签 */}
                  <div className="absolute top-2.5 right-2.5 glass-card px-2 py-0.5 rounded-lg text-[11px] font-bold text-slate-800 shadow-sm">
                    {categoryName}
                  </div>

                  {/* 悬停快捷提示条 */}
                  <div className="absolute inset-x-0 bottom-0 py-2 px-3 bg-gradient-to-t from-black/60 to-transparent opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-between text-white text-xs">
                    <span>查看单品详情</span>
                    <ArrowRight className="w-3.5 h-3.5" />
                  </div>
                </div>

                {/* 卡片信息区 */}
                <div className="p-4 flex-1 flex flex-col justify-between space-y-3">
                  <div>
                    <div className="flex items-start justify-between gap-2">
                      <h3 className="font-bold text-sm text-slate-900 line-clamp-1 group-hover:text-brand-600 transition-colors">
                        {item.sub_category}
                      </h3>
                      {/* 颜色圆点 */}
                      <div className="flex items-center gap-1 shrink-0 pt-0.5" title={`主色调: ${item.primary_color}`}>
                        <span className="w-3 h-3 rounded-full border border-slate-300 shadow-xs" style={{ backgroundColor: item.primary_color }} />
                        <span className="text-[11px] text-slate-400 capitalize">{item.primary_color}</span>
                      </div>
                    </div>

                    {/* 风格与季节标签 */}
                    <div className="flex flex-wrap gap-1 mt-2">
                      <span className="text-[10px] px-2 py-0.5 rounded-md bg-slate-100 text-slate-600 font-medium">
                        {item.style}
                      </span>
                      {Array.isArray(item.season) && item.season.slice(0, 2).map((s) => (
                        <span key={s} className="text-[10px] px-2 py-0.5 rounded-md bg-brand-50 text-brand-700 font-medium">
                          {s}
                        </span>
                      ))}
                    </div>
                  </div>

                  {/* 底部温区信息 */}
                  <div className="pt-2 border-t border-slate-100 flex items-center justify-between text-[11px] text-slate-500">
                    <span className="flex items-center gap-1">
                      <Thermometer className="w-3 h-3 text-amber-500" />
                      <span>{item.temp_min}℃ ~ {item.temp_max}℃</span>
                    </span>
                    <span className="text-slate-400 capitalize">{item.thickness}</span>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
