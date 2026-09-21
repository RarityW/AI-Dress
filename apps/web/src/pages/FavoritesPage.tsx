import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { Bookmark, Sparkles, Trash2, ArrowRight, Calendar, Compass, Layers } from 'lucide-react';
import { outfitsApi } from '../services/api';
import { Outfit } from '../types/auth';

export default function FavoritesPage() {
  const [outfits, setOutfits] = useState<Outfit[]>([]);
  const [loading, setLoading] = useState(true);
  const [deletingId, setDeletingId] = useState<string | null>(null);

  useEffect(() => {
    fetchOutfits();
  }, []);

  const fetchOutfits = async () => {
    try {
      setLoading(true);
      const res = await outfitsApi.list();
      if (res.success && res.data) {
        setOutfits(res.data.items || []);
      }
    } catch (err) {
      console.error('Failed to load outfits:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (id: string) => {
    if (!window.confirm('确定要取消收藏这套穿搭吗？')) return;
    setDeletingId(id);
    try {
      const res = await outfitsApi.delete(id);
      if (res.success) {
        setOutfits((prev) => prev.filter((o) => o.id !== id));
      }
    } catch (err) {
      alert('删除失败，请稍后重试');
    } finally {
      setDeletingId(null);
    }
  };

  return (
    <div className="space-y-8 animate-fadeIn">
      {/* 头部标题区 */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-6 border-b border-slate-200">
        <div>
          <div className="flex items-center gap-2">
            <span className="p-2 rounded-xl bg-amber-50 text-amber-600">
              <Bookmark className="w-5 h-5" />
            </span>
            <h1 className="text-2xl font-extrabold text-slate-900 tracking-tight">我的搭配收藏</h1>
            <span className="text-xs font-bold px-2.5 py-0.5 rounded-full bg-slate-100 text-slate-600">
              共 {outfits.length} 套方案
            </span>
          </div>
          <p className="text-sm text-slate-500 mt-1">
            汇总您在智能推荐中满意的穿搭组合，随时翻阅灵感或出门前快速调取。
          </p>
        </div>

        <Link
          to="/recommend"
          className="inline-flex items-center justify-center gap-2 px-5 py-2.5 rounded-xl bg-brand-600 hover:bg-brand-700 text-white font-bold text-sm shadow-md shadow-brand-500/20 active:scale-95 transition-all"
        >
          <Compass className="w-4 h-4" />
          <span>去生成新推荐</span>
        </Link>
      </div>

      {/* 列表主体 */}
      {loading ? (
        <div className="min-h-[40vh] flex flex-col items-center justify-center">
          <div className="w-8 h-8 border-3 border-brand-500 border-t-transparent rounded-full animate-spin" />
          <span className="text-sm text-slate-500 mt-3">加载收藏搭配中...</span>
        </div>
      ) : outfits.length === 0 ? (
        <div className="text-center py-16 px-4 glass-card rounded-3xl border border-dashed border-slate-300">
          <div className="w-16 h-16 rounded-2xl bg-slate-100 text-slate-400 flex items-center justify-center mx-auto mb-4">
            <Bookmark className="w-8 h-8" />
          </div>
          <h3 className="text-lg font-bold text-slate-800">暂无收藏的穿搭方案</h3>
          <p className="text-xs sm:text-sm text-slate-500 max-w-sm mx-auto mt-1 mb-6">
            您可以在「穿搭推荐」页面中，对系统智能计算得出的心仪方案点击「收藏此搭配」。
          </p>
          <Link
            to="/recommend"
            className="inline-flex items-center gap-2 px-6 py-2.5 rounded-xl bg-slate-900 text-white text-xs font-bold hover:bg-brand-600 transition-colors"
          >
            <span>立即体验穿搭推荐</span>
            <ArrowRight className="w-4 h-4" />
          </Link>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {outfits.map((outfit) => (
            <div
              key={outfit.id}
              className="glass-card bg-white/85 rounded-3xl p-5 border border-slate-200/80 shadow-sm hover:shadow-md transition-all flex flex-col justify-between group"
            >
              <div>
                {/* 顶部标题与操作 */}
                <div className="flex items-start justify-between gap-2 mb-3">
                  <div>
                    <h3 className="font-extrabold text-slate-900 text-base group-hover:text-brand-700 transition-colors">
                      {outfit.name || '未命名搭配'}
                    </h3>
                    <div className="flex items-center gap-2 text-xs text-slate-400 mt-1">
                      {outfit.created_at && (
                        <span className="flex items-center gap-1">
                          <Calendar className="w-3 h-3" />
                          {new Date(outfit.created_at).toLocaleDateString('zh-CN')}
                        </span>
                      )}
                      {outfit.occasion && (
                        <span className="px-2 py-0.5 rounded-md bg-slate-100 text-slate-600 font-medium">
                          {outfit.occasion}
                        </span>
                      )}
                    </div>
                  </div>

                  <button
                    type="button"
                    onClick={() => handleDelete(outfit.id)}
                    disabled={deletingId === outfit.id}
                    className="p-2 rounded-xl text-slate-400 hover:text-rose-600 hover:bg-rose-50 transition-colors cursor-pointer"
                    title="取消收藏"
                  >
                    {deletingId === outfit.id ? (
                      <div className="w-4 h-4 border-2 border-rose-500 border-t-transparent rounded-full animate-spin" />
                    ) : (
                      <Trash2 className="w-4 h-4" />
                    )}
                  </button>
                </div>

                {/* 单品拼图网格 */}
                <div className="grid grid-cols-3 gap-2 my-3">
                  {outfit.items && outfit.items.length > 0 ? (
                    outfit.items.map((it, idx) => (
                      <div
                        key={idx}
                        className="aspect-square rounded-xl bg-slate-100 border border-slate-200/70 overflow-hidden relative group/item"
                      >
                        {it.image_url ? (
                          <img
                            src={it.image_url}
                            alt={it.category || '衣物'}
                            className="w-full h-full object-cover group-hover/item:scale-105 transition-transform"
                            onError={(e) => {
                              (e.target as HTMLElement).style.display = 'none';
                            }}
                          />
                        ) : (
                          <div className="w-full h-full flex items-center justify-center text-slate-300">
                            <Layers className="w-6 h-6" />
                          </div>
                        )}
                        <div className="absolute inset-x-0 bottom-0 bg-black/60 backdrop-blur-xs px-1.5 py-0.5 text-[10px] text-white text-center truncate">
                          {it.category || '单品'}
                        </div>
                      </div>
                    ))
                  ) : (
                    <div className="col-span-3 py-6 text-center text-xs text-slate-400 bg-slate-50 rounded-xl">
                      包含 {outfit.item_ids?.length || 0} 件单品
                    </div>
                  )}
                </div>
              </div>

              {/* 底部评分徽标 */}
              <div className="pt-3 border-t border-slate-100 flex items-center justify-between text-xs">
                <span className="text-slate-500 font-medium">综合推荐指数</span>
                {outfit.overall_score ? (
                  <span className="inline-flex items-center gap-1 font-extrabold text-amber-600 bg-amber-50 border border-amber-200/60 px-2.5 py-0.5 rounded-full">
                    <Sparkles className="w-3 h-3 text-amber-500" />
                    <span>{Math.round(outfit.overall_score)} 分</span>
                  </span>
                ) : (
                  <span className="text-slate-400">已定制</span>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
