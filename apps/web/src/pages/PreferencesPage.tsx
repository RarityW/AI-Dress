import { useState, useEffect } from 'react';
import { Sliders, Palette, Sparkles, Check, Save, RotateCcw, AlertCircle, Info } from 'lucide-react';
import { preferencesApi } from '../services/api';

const STYLES = [
  { id: 'casual', label: '休闲日常 (Casual)', desc: '舒适随性、基础实穿' },
  { id: 'commute', label: '职场通勤 (Commute)', desc: '干练得体、专业商务' },
  { id: 'minimal', label: '极简静奢 (Minimal)', desc: '低调克制、线条纯粹' },
  { id: 'vintage', label: '复古工装 (Vintage)', desc: '经典做旧、硬朗怀旧' },
  { id: 'streetwear', label: '街头潮牌 (Streetwear)', desc: '个性张扬、宽松廓形' },
  { id: 'sporty', label: '运动轻户外 (Sporty)', desc: '活力轻量、吸湿速干' },
  { id: 'elegant', label: '法式优雅 (Elegant)', desc: '浪漫精致、剪裁考究' },
];

const COLORS = [
  { id: 'black', label: '黑色', hex: '#18181b', light: false },
  { id: 'white', label: '白色', hex: '#f8fafc', light: true },
  { id: 'grey', label: '灰色', hex: '#71717a', light: false },
  { id: 'beige', label: '米色/杏色', hex: '#f5f5dc', light: true },
  { id: 'brown', label: '棕色/大地色', hex: '#78350f', light: false },
  { id: 'navy', label: '藏青/深蓝', hex: '#1e3a8a', light: false },
  { id: 'blue', label: '浅蓝/牛仔蓝', hex: '#3b82f6', light: false },
  { id: 'green', label: '绿色/橄榄绿', hex: '#15803d', light: false },
  { id: 'red', label: '红色/酒红', hex: '#b91c1c', light: false },
  { id: 'yellow', label: '黄色', hex: '#eab308', light: true },
  { id: 'pink', label: '粉色', hex: '#ec4899', light: false },
  { id: 'purple', label: '紫色', hex: '#8b5cf6', light: false },
  { id: 'orange', label: '橙色', hex: '#f97316', light: false },
];

export default function PreferencesPage() {
  const [preferredStyles, setPreferredStyles] = useState<string[]>([]);
  const [avoidedColors, setAvoidedColors] = useState<string[]>([]);
  const [weights, setWeights] = useState({
    weather: 0.35,
    style: 0.25,
    scene: 0.20,
    color: 0.15,
  });

  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState<{ text: string; type: 'success' | 'error' } | null>(null);

  useEffect(() => {
    fetchPreferences();
  }, []);

  const fetchPreferences = async () => {
    try {
      setLoading(true);
      const res = await preferencesApi.get();
      if (res.success && res.data) {
        setPreferredStyles(res.data.preferred_styles || []);
        setAvoidedColors(res.data.avoided_colors || []);
        if (res.data.custom_weights && Object.keys(res.data.custom_weights).length > 0) {
          setWeights({
            weather: res.data.custom_weights.weather ?? 0.35,
            style: res.data.custom_weights.style ?? 0.25,
            scene: res.data.custom_weights.scene ?? 0.20,
            color: res.data.custom_weights.color ?? 0.15,
          });
        }
      }
    } catch {
      setMessage({ text: '加载偏好失败，已使用默认配置', type: 'error' });
    } finally {
      setLoading(false);
    }
  };

  const toggleStyle = (id: string) => {
    setPreferredStyles((prev) =>
      prev.includes(id) ? prev.filter((s) => s !== id) : [...prev, id]
    );
  };

  const toggleColor = (id: string) => {
    setAvoidedColors((prev) =>
      prev.includes(id) ? prev.filter((c) => c !== id) : [...prev, id]
    );
  };

  const handleWeightChange = (key: keyof typeof weights, val: number) => {
    setWeights((prev) => ({
      ...prev,
      [key]: val,
    }));
  };

  const resetWeights = () => {
    setWeights({
      weather: 0.35,
      style: 0.25,
      scene: 0.20,
      color: 0.15,
    });
  };

  const handleSave = async () => {
    setSaving(true);
    setMessage(null);
    try {
      const res = await preferencesApi.update({
        preferred_styles: preferredStyles,
        avoided_colors: avoidedColors,
        custom_weights: weights,
      });
      if (res.success) {
        setMessage({ text: '个性化穿搭偏好已成功保存！推荐引擎将立即生效。', type: 'success' });
        setTimeout(() => setMessage(null), 4000);
      } else {
        setMessage({ text: res.message || '保存失败', type: 'error' });
      }
    } catch (err: any) {
      setMessage({ text: err.message || '保存发生异常', type: 'error' });
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-[50vh] flex flex-col items-center justify-center">
        <div className="w-8 h-8 border-3 border-brand-500 border-t-transparent rounded-full animate-spin" />
        <span className="text-sm text-slate-500 mt-3">加载个性化偏好配置中...</span>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto space-y-8 animate-fadeIn">
      {/* 头部导航区域 */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-6 border-b border-slate-200">
        <div>
          <div className="flex items-center gap-2">
            <span className="p-2 rounded-xl bg-brand-50 text-brand-600">
              <Sliders className="w-5 h-5" />
            </span>
            <h1 className="text-2xl font-extrabold text-slate-900 tracking-tight">个性化偏好设定</h1>
          </div>
          <p className="text-sm text-slate-500 mt-1">
            定制您的风格偏好、回避色彩与自主推荐算法权重，让穿搭决策更加贴合您的个人品味。
          </p>
        </div>

        <button
          type="button"
          onClick={handleSave}
          disabled={saving}
          className="inline-flex items-center justify-center gap-2 px-6 py-2.5 rounded-xl bg-slate-900 hover:bg-brand-600 text-white font-bold text-sm shadow-md shadow-slate-900/10 active:scale-95 transition-all disabled:opacity-50 cursor-pointer"
        >
          {saving ? (
            <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
          ) : (
            <>
              <Save className="w-4 h-4" />
              <span>保存配置</span>
            </>
          )}
        </button>
      </div>

      {/* 提示通知 */}
      {message && (
        <div
          className={`p-4 rounded-2xl border flex items-center gap-3 text-sm animate-fadeIn ${
            message.type === 'success'
              ? 'bg-emerald-50 border-emerald-200 text-emerald-800'
              : 'bg-rose-50 border-rose-200 text-rose-800'
          }`}
        >
          {message.type === 'success' ? (
            <Check className="w-5 h-5 text-emerald-600 shrink-0" />
          ) : (
            <AlertCircle className="w-5 h-5 text-rose-600 shrink-0" />
          )}
          <span>{message.text}</span>
        </div>
      )}

      {/* 模块 1：偏好风格 (Preferred Styles) */}
      <section className="bg-white/80 backdrop-blur-md rounded-3xl p-6 sm:p-8 border border-slate-200/80 shadow-sm space-y-4">
        <div className="flex items-center gap-2">
          <Sparkles className="w-5 h-5 text-brand-600" />
          <h2 className="text-lg font-bold text-slate-900">常选偏好风格</h2>
        </div>
        <p className="text-xs text-slate-500">
          选中的风格将在推荐匹配时获得加分加权优先展示（可多选）：
        </p>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3 pt-2">
          {STYLES.map((st) => {
            const isSelected = preferredStyles.includes(st.id);
            return (
              <button
                key={st.id}
                type="button"
                onClick={() => toggleStyle(st.id)}
                className={`p-3.5 rounded-2xl border text-left transition-all flex items-start justify-between cursor-pointer ${
                  isSelected
                    ? 'bg-brand-50/80 border-brand-300 ring-2 ring-brand-500/20 shadow-sm'
                    : 'bg-slate-50/60 border-slate-200/70 hover:bg-slate-100/80'
                }`}
              >
                <div>
                  <div className="text-sm font-bold text-slate-900">{st.label}</div>
                  <div className="text-xs text-slate-400 mt-0.5">{st.desc}</div>
                </div>
                <div
                  className={`w-5 h-5 rounded-full border flex items-center justify-center shrink-0 mt-0.5 transition-colors ${
                    isSelected ? 'bg-brand-600 border-brand-600 text-white' : 'border-slate-300'
                  }`}
                >
                  {isSelected && <Check className="w-3 h-3 stroke-[3]" />}
                </div>
              </button>
            );
          })}
        </div>
      </section>

      {/* 模块 2：回避色彩 (Avoided Colors) */}
      <section className="bg-white/80 backdrop-blur-md rounded-3xl p-6 sm:p-8 border border-slate-200/80 shadow-sm space-y-4">
        <div className="flex items-center gap-2">
          <Palette className="w-5 h-5 text-indigo-600" />
          <h2 className="text-lg font-bold text-slate-900">回避色彩过滤</h2>
        </div>
        <p className="text-xs text-slate-500">
          勾选您不希望出现在推荐方案中的颜色，推荐引擎将对包含此类色彩的单品执行降权惩罚：
        </p>

        <div className="flex flex-wrap gap-2.5 pt-2">
          {COLORS.map((col) => {
            const isAvoided = avoidedColors.includes(col.id);
            return (
              <button
                key={col.id}
                type="button"
                onClick={() => toggleColor(col.id)}
                className={`inline-flex items-center gap-2 px-3.5 py-2 rounded-xl text-xs font-bold border transition-all cursor-pointer ${
                  isAvoided
                    ? 'bg-rose-50 border-rose-300 text-rose-700 shadow-sm ring-2 ring-rose-500/20'
                    : 'bg-slate-50/80 border-slate-200 text-slate-700 hover:bg-slate-100'
                }`}
              >
                <span
                  className="w-3.5 h-3.5 rounded-full border border-black/10 shrink-0 shadow-inner"
                  style={{ backgroundColor: col.hex }}
                />
                <span>{col.label}</span>
                {isAvoided && <span className="text-[10px] text-rose-500 font-extrabold">✕ 避开</span>}
              </button>
            );
          })}
        </div>
      </section>

      {/* 模块 3：自定义运筹权重 (Custom Weights) */}
      <section className="bg-white/80 backdrop-blur-md rounded-3xl p-6 sm:p-8 border border-slate-200/80 shadow-sm space-y-5">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Sliders className="w-5 h-5 text-emerald-600" />
            <h2 className="text-lg font-bold text-slate-900">多目标决策打分权重</h2>
          </div>
          <button
            type="button"
            onClick={resetWeights}
            className="text-xs text-slate-400 hover:text-slate-600 flex items-center gap-1 cursor-pointer"
          >
            <RotateCcw className="w-3.5 h-3.5" />
            <span>恢复默认</span>
          </button>
        </div>

        <div className="p-3.5 rounded-2xl bg-amber-50/70 border border-amber-200/60 text-xs text-amber-800 flex items-start gap-2.5">
          <Info className="w-4 h-4 shrink-0 mt-0.5 text-amber-600" />
          <span>
            系统将在打分时自动将以下 4 个因子的权重执行线性归一化（使权重总和恒为 100%）。您可以自由提升更看重的考量维度。
          </span>
        </div>

        <div className="space-y-5 pt-2">
          {/* 气象舒适度 */}
          <div>
            <div className="flex justify-between text-xs font-bold text-slate-700 mb-1.5">
              <span>气温与体感适应度 (Weather)</span>
              <span className="text-brand-600 font-extrabold">{Math.round(weights.weather * 100)}%</span>
            </div>
            <input
              type="range"
              min="0.05"
              max="0.8"
              step="0.05"
              value={weights.weather}
              onChange={(e) => handleWeightChange('weather', parseFloat(e.target.value))}
              className="w-full accent-brand-600 h-2 bg-slate-100 rounded-lg cursor-pointer"
            />
          </div>

          {/* 风格相容性 */}
          <div>
            <div className="flex justify-between text-xs font-bold text-slate-700 mb-1.5">
              <span>目标风格匹配度 (Style)</span>
              <span className="text-brand-600 font-extrabold">{Math.round(weights.style * 100)}%</span>
            </div>
            <input
              type="range"
              min="0.05"
              max="0.8"
              step="0.05"
              value={weights.style}
              onChange={(e) => handleWeightChange('style', parseFloat(e.target.value))}
              className="w-full accent-brand-600 h-2 bg-slate-100 rounded-lg cursor-pointer"
            />
          </div>

          {/* 场景契合度 */}
          <div>
            <div className="flex justify-between text-xs font-bold text-slate-700 mb-1.5">
              <span>场景规范契合度 (Scene)</span>
              <span className="text-brand-600 font-extrabold">{Math.round(weights.scene * 100)}%</span>
            </div>
            <input
              type="range"
              min="0.05"
              max="0.8"
              step="0.05"
              value={weights.scene}
              onChange={(e) => handleWeightChange('scene', parseFloat(e.target.value))}
              className="w-full accent-brand-600 h-2 bg-slate-100 rounded-lg cursor-pointer"
            />
          </div>

          {/* 色彩美学协调 */}
          <div>
            <div className="flex justify-between text-xs font-bold text-slate-700 mb-1.5">
              <span>色彩搭配协调度 (Color)</span>
              <span className="text-brand-600 font-extrabold">{Math.round(weights.color * 100)}%</span>
            </div>
            <input
              type="range"
              min="0.05"
              max="0.8"
              step="0.05"
              value={weights.color}
              onChange={(e) => handleWeightChange('color', parseFloat(e.target.value))}
              className="w-full accent-brand-600 h-2 bg-slate-100 rounded-lg cursor-pointer"
            />
          </div>
        </div>
      </section>

      {/* 底部保存按钮 */}
      <div className="text-center pt-2">
        <button
          type="button"
          onClick={handleSave}
          disabled={saving}
          className="px-8 py-3 rounded-2xl bg-gradient-to-r from-brand-600 to-indigo-600 hover:from-brand-700 hover:to-indigo-700 text-white font-bold text-sm shadow-lg shadow-brand-500/20 active:scale-95 transition-all disabled:opacity-50 cursor-pointer"
        >
          {saving ? '保存中...' : '保存个性化偏好'}
        </button>
      </div>
    </div>
  );
}
