import { useState, useEffect } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import {
  ArrowLeft,
  Trash2,
  Thermometer,
  Sparkles,
  Calendar,
  Palette,
  Compass,
  AlertCircle
} from 'lucide-react';
import { getClothingDetail, deleteClothing } from '../services/api';
import { ClothingItem } from '../types/clothing';
import LoadingSpinner from '../components/LoadingSpinner';

const CATEGORY_NAMES: Record<string, string> = {
  top: '上装 (Top)',
  bottom: '下装 (Bottom)',
  coat: '外套 (Coat)',
  shoes: '鞋履 (Shoes)',
  accessory: '配饰 (Accessory)',
};

const CATEGORY_ICONS: Record<string, string> = {
  top: '👕',
  bottom: '👖',
  coat: '🧥',
  shoes: '👟',
  accessory: '🧢',
};

export default function ClothingDetailPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();

  const [item, setItem] = useState<ClothingItem | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [deleting, setDeleting] = useState(false);

  useEffect(() => {
    const fetchDetail = async () => {
      if (!id) return;
      setLoading(true);
      setError(null);
      try {
        const response = await getClothingDetail(id);
        if ((response.success || response.code === 200) && response.data) {
          setItem(response.data);
        } else {
          setError(response.message || '获取衣物详情失败');
        }
      } catch (err: any) {
        console.error(err);
        setError('无法连接服务器获取单品信息');
      } finally {
        setLoading(false);
      }
    };

    fetchDetail();
  }, [id]);

  const handleDelete = async () => {
    if (!id) return;
    if (!window.confirm(`确定要从衣橱中删除这件【${item?.sub_category || '衣物'}】吗？该操作不可撤回。`)) {
      return;
    }

    setDeleting(true);
    try {
      const response = await deleteClothing(id);
      if (response.success || response.code === 200) {
        navigate('/wardrobe');
      } else {
        alert(response.message || '删除失败');
        setDeleting(false);
      }
    } catch (err) {
      alert('网络请求异常，删除未完成');
      setDeleting(false);
    }
  };

  if (loading) {
    return (
      <div className="py-32 text-center space-y-3">
        <LoadingSpinner />
        <p className="text-sm text-slate-500 font-medium animate-pulse">正在加载单品档案...</p>
      </div>
    );
  }

  if (error || !item) {
    return (
      <div className="max-w-md mx-auto py-24 text-center space-y-4">
        <AlertCircle className="w-10 h-10 text-red-500 mx-auto" />
        <h3 className="text-lg font-bold text-slate-900">未找到该单品档案</h3>
        <p className="text-xs text-slate-500">{error || '该衣物可能已被删除或不存在。'}</p>
        <Link
          to="/wardrobe"
          className="inline-flex items-center gap-1.5 px-4 py-2 rounded-xl text-xs font-semibold text-white bg-slate-900 hover:bg-brand-600 transition-colors"
        >
          返回我的衣橱
        </Link>
      </div>
    );
  }

  const categoryLabel = CATEGORY_NAMES[item.category] || item.category;
  const icon = CATEGORY_ICONS[item.category] || '👗';

  return (
    <div className="max-w-4xl mx-auto space-y-8 pb-16">
      {/* 顶部面包屑与操作栏 */}
      <div className="flex items-center justify-between border-b border-slate-200/80 pb-4">
        <button
          onClick={() => navigate('/wardrobe')}
          className="inline-flex items-center gap-1.5 text-xs sm:text-sm font-semibold text-slate-600 hover:text-slate-900 transition-colors cursor-pointer"
        >
          <ArrowLeft className="w-4 h-4" />
          <span>返回衣橱列表</span>
        </button>

        <button
          onClick={handleDelete}
          disabled={deleting}
          className="inline-flex items-center gap-1 px-3 py-1.5 rounded-lg text-xs font-medium text-red-600 hover:text-red-700 hover:bg-red-50 transition-colors disabled:opacity-40 cursor-pointer"
        >
          <Trash2 className="w-3.5 h-3.5" />
          <span>{deleting ? '正在删除...' : '删除单品'}</span>
        </button>
      </div>

      {/* 主商品档案卡片 (Luxury Editorial Showcase) */}
      <div className="bg-white rounded-3xl border border-slate-200/80 shadow-soft overflow-hidden grid grid-cols-1 md:grid-cols-12">
        {/* 左侧大图展示区 (5列) */}
        <div className="md:col-span-5 bg-slate-100/70 p-6 flex items-center justify-center relative min-h-[340px]">
          {item.image_url ? (
            <img
              src={item.image_url}
              alt={item.sub_category}
              className="max-h-96 w-auto object-contain rounded-2xl shadow-md"
            />
          ) : (
            <div className="text-8xl opacity-30">{icon}</div>
          )}

          <div className="absolute top-4 left-4 glass-card px-3 py-1 rounded-full text-xs font-bold text-slate-800 shadow-sm">
            {categoryLabel}
          </div>
        </div>

        {/* 右侧属性详细档案 (7列) */}
        <div className="md:col-span-7 p-6 sm:p-8 flex flex-col justify-between space-y-6">
          <div className="space-y-4">
            <div className="space-y-1">
              <span className="text-xs uppercase tracking-wider font-bold text-brand-600">
                GARMENT SPECIFICATION
              </span>
              <h1 className="text-2xl sm:text-3xl font-black text-slate-900 tracking-tight">
                {item.sub_category}
              </h1>
              <div className="flex items-center gap-1 text-xs text-slate-400">
                <Calendar className="w-3.5 h-3.5" />
                <span>收纳时间：{new Date(item.created_at).toLocaleDateString('zh-CN')}</span>
              </div>
            </div>

            {/* 核心特征网格 */}
            <div className="grid grid-cols-2 gap-4 pt-2">
              {/* 颜色属性 */}
              <div className="p-3.5 rounded-2xl bg-slate-50 border border-slate-100 space-y-1">
                <span className="text-xs text-slate-400 flex items-center gap-1">
                  <Palette className="w-3.5 h-3.5" />
                  主色调
                </span>
                <div className="flex items-center gap-2 pt-0.5">
                  <span
                    className="w-4 h-4 rounded-full border border-slate-300 shadow-xs"
                    style={{ backgroundColor: item.primary_color }}
                  />
                  <span className="text-sm font-bold text-slate-800 capitalize">
                    {item.primary_color}
                  </span>
                </div>
              </div>

              {/* 风格偏向 */}
              <div className="p-3.5 rounded-2xl bg-slate-50 border border-slate-100 space-y-1">
                <span className="text-xs text-slate-400 flex items-center gap-1">
                  <Sparkles className="w-3.5 h-3.5" />
                  风格基调
                </span>
                <div className="text-sm font-bold text-slate-800 capitalize pt-0.5">
                  {item.style}
                </div>
              </div>

              {/* 面料厚度 */}
              <div className="p-3.5 rounded-2xl bg-slate-50 border border-slate-100 space-y-1">
                <span className="text-xs text-slate-400">厚薄程度</span>
                <div className="text-sm font-bold text-slate-800 capitalize">
                  {item.thickness}
                </div>
              </div>

              {/* 适温温区 */}
              <div className="p-3.5 rounded-2xl bg-slate-50 border border-slate-100 space-y-1">
                <span className="text-xs text-slate-400 flex items-center gap-1">
                  <Thermometer className="w-3.5 h-3.5 text-amber-500" />
                  适宜温区
                </span>
                <div className="text-sm font-bold text-slate-800">
                  {item.temp_min}℃ ~ {item.temp_max}℃
                </div>
              </div>
            </div>

            {/* 适宜季节标签 */}
            <div className="space-y-1.5 pt-1">
              <span className="text-xs text-slate-400 font-medium">推荐穿着季节</span>
              <div className="flex flex-wrap gap-2">
                {Array.isArray(item.season) &&
                  item.season.map((s) => (
                    <span
                      key={s}
                      className="px-3 py-1 rounded-xl text-xs font-semibold bg-brand-50 text-brand-700 border border-brand-200/60"
                    >
                      {s === 'spring' ? '春季' : s === 'summer' ? '夏季' : s === 'autumn' ? '秋季' : s === 'winter' ? '冬季' : s}
                    </span>
                  ))}
              </div>
            </div>
          </div>

          {/* 底部行动引导 */}
          <div className="pt-6 border-t border-slate-100 flex items-center justify-between">
            <span className="text-xs text-slate-400">单品 ID: {item.id.slice(0, 8)}...</span>
            <Link
              to="/recommend"
              className="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl text-xs sm:text-sm font-semibold text-white bg-slate-900 hover:bg-brand-600 transition-colors shadow-sm"
            >
              <Compass className="w-4 h-4" />
              <span>使用此单品进行推荐搭配</span>
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}
