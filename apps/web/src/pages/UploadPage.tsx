import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import {
  Upload as UploadIcon,
  ArrowRight,
  ArrowLeft,
  CheckCircle2,
  AlertCircle,
  Sparkles,
  RefreshCw,
  Palette
} from 'lucide-react';
import { uploadClothingImage, createClothing, analyzeClothingImage } from '../services/api';
import { ClothingItemCreate } from '../types/clothing';

const CATEGORY_MAP: Record<string, string> = {
  top: '上装',
  bottom: '下装',
  coat: '外套',
  shoes: '鞋履',
  accessory: '配饰',
};

const SUB_CATEGORIES: Record<string, string[]> = {
  top: ['T恤', '衬衫', 'Polo衫', '毛衣', '卫衣', '背心', '针织衫'],
  bottom: ['牛仔裤', '西裤', '休闲裤', '短裤', '裙子', '运动裤'],
  coat: ['夹克', '西装', '风衣', '羽绒服', '开衫', '呢子大衣'],
  shoes: ['运动鞋', '皮鞋', '靴子', '凉鞋', '乐福鞋', '帆布鞋'],
  accessory: ['帽子', '围巾', '包袋', '皮带', '配饰'],
};

const PRESET_COLORS = [
  { name: 'white', label: '白色', hex: '#ffffff', border: true },
  { name: 'black', label: '黑色', hex: '#000000' },
  { name: 'gray', label: '灰色', hex: '#64748b' },
  { name: 'navy', label: '藏青', hex: '#1e3a8a' },
  { name: 'beige', label: '米色', hex: '#f5f5dc', border: true },
  { name: 'khaki', label: '卡其', hex: '#c3b091' },
  { name: 'blue', label: '蓝色', hex: '#2563eb' },
  { name: 'red', label: '红色', hex: '#dc2626' },
  { name: 'green', label: '绿色', hex: '#16a34a' },
  { name: 'brown', label: '棕色', hex: '#78350f' },
];

const STYLE_OPTIONS = [
  { value: 'casual', label: '休闲舒适' },
  { value: 'minimal', label: '质感极简' },
  { value: 'formal', label: '干练正式' },
  { value: 'sporty', label: '活力运动' },
  { value: 'vintage', label: '经典复古' },
  { value: 'street', label: '潮流街头' },
  { value: 'elegant', label: '优雅气质' },
];

const THICKNESS_OPTIONS = [
  { value: 'thin', label: '轻薄 (夏季/单穿)' },
  { value: 'medium', label: '适中 (春秋四季)' },
  { value: 'thick', label: '加厚 (冬季保暖)' },
];

const SEASON_OPTIONS = [
  { value: 'spring', label: '春季' },
  { value: 'summer', label: '夏季' },
  { value: 'autumn', label: '秋季' },
  { value: 'winter', label: '冬季' },
];

// 快捷录入模板
const QUICK_TEMPLATES = [
  {
    name: '经典纯白T恤',
    data: { category: 'top', sub_category: 'T恤', primary_color: 'white', style: 'casual', thickness: 'thin', season: ['spring', 'summer'], temp_min: 20, temp_max: 35 }
  },
  {
    name: '修身深蓝牛仔裤',
    data: { category: 'bottom', sub_category: '牛仔裤', primary_color: 'navy', style: 'casual', thickness: 'medium', season: ['spring', 'autumn', 'winter'], temp_min: 10, temp_max: 25 }
  },
  {
    name: '商务通勤黑西装',
    data: { category: 'coat', sub_category: '西装', primary_color: 'black', style: 'formal', thickness: 'medium', season: ['spring', 'autumn'], temp_min: 12, temp_max: 22 }
  },
  {
    name: '百搭小白鞋',
    data: { category: 'shoes', sub_category: '运动鞋', primary_color: 'white', style: 'casual', thickness: 'medium', season: ['spring', 'summer', 'autumn'], temp_min: 10, temp_max: 32 }
  }
];

export default function UploadPage() {
  const navigate = useNavigate();
  const [step, setStep] = useState<1 | 2>(1);
  const [file, setFile] = useState<File | null>(null);
  const [preview, setPreview] = useState<string>('');
  const [uploading, setUploading] = useState(false);
  const [analyzing, setAnalyzing] = useState(false);
  const [aiAnalyzed, setAiAnalyzed] = useState(false);
  const [imageUrl, setImageUrl] = useState('');
  const [error, setError] = useState('');
  const [isDragOver, setIsDragOver] = useState(false);

  const [formData, setFormData] = useState<ClothingItemCreate>({
    category: 'top',
    sub_category: 'T恤',
    primary_color: 'white',
    secondary_color: '',
    style: 'casual',
    thickness: 'thin',
    season: ['spring', 'summer'],
    temp_min: 18,
    temp_max: 30,
  });

  const handleFileSelect = (selected: File) => {
    if (!['image/jpeg', 'image/png', 'image/webp'].includes(selected.type)) {
      setError('仅支持 JPEG, PNG, WEBP 格式图片');
      return;
    }
    if (selected.size > 10 * 1024 * 1024) {
      setError('图片大小不能超过 10MB');
      return;
    }
    setFile(selected);
    setPreview(URL.createObjectURL(selected));
    setError('');
  };

  const handleUploadAndAnalyze = async () => {
    if (!file) return;
    setUploading(true);
    setError('');
    try {
      // 1. 上传图片文件
      const res = await uploadClothingImage(file);
      if ((res.success || res.code === 200) && res.data) {
        const uploadedUrl = res.data.image_url;
        setImageUrl(uploadedUrl);

        // 2. 触发 AI 视觉多模态大模型分析
        setAnalyzing(true);
        try {
          const aiRes = await analyzeClothingImage(uploadedUrl);
          if ((aiRes.success || aiRes.code === 200) && aiRes.data) {
            const d = aiRes.data;
            setFormData({
              category: d.category || 'top',
              sub_category: d.sub_category || '单品',
              primary_color: d.primary_color || 'white',
              secondary_color: d.secondary_color || '',
              style: d.style || 'casual',
              thickness: d.thickness || 'medium',
              season: Array.isArray(d.season) && d.season.length > 0 ? d.season : ['spring', 'autumn'],
              temp_min: d.temp_min ?? 15,
              temp_max: d.temp_max ?? 25,
              raw_vlm_attributes: d.raw_vlm_attributes,
            });
            setAiAnalyzed(true);
          }
        } catch (aiErr) {
          console.warn('AI 视觉分析遇到问题，进入手动核对模式:', aiErr);
        } finally {
          setAnalyzing(false);
        }

        setStep(2);
      } else {
        setError(res.message || '图片上传失败，请检查网络');
      }
    } catch (err: any) {
      console.error(err);
      setError(err?.response?.data?.message || '图片上传网络异常');
    } finally {
      setUploading(false);
    }
  };

  const handleSubmitClothing = async (e: React.FormEvent) => {
    e.preventDefault();
    if (formData.season.length === 0) {
      setError('请至少选择一个适宜季节');
      return;
    }
    setUploading(true);
    setError('');
    try {
      const res = await createClothing({
        ...formData,
        image_url: imageUrl || '',
      });
      if (res.success || res.code === 200) {
        navigate('/wardrobe');
      } else {
        setError(res.message || '录入衣物失败');
      }
    } catch (err: any) {
      console.error(err);
      setError(err?.response?.data?.message || '保存衣物请求失败');
    } finally {
      setUploading(false);
    }
  };

  const handleApplyPreset = (presetData: Partial<ClothingItemCreate>) => {
    setFormData((prev) => ({
      ...prev,
      ...presetData,
    }));
  };

  const toggleSeason = (seasonKey: string) => {
    setFormData((prev) => {
      const exists = prev.season.includes(seasonKey);
      return {
        ...prev,
        season: exists
          ? prev.season.filter((s) => s !== seasonKey)
          : [...prev.season, seasonKey],
      };
    });
  };

  return (
    <div className="max-w-3xl mx-auto space-y-8 pb-16">
      {/* 头部标题区 */}
      <div className="flex items-center justify-between border-b border-slate-200/80 pb-5">
        <div>
          <h1 className="text-3xl font-extrabold text-slate-900 tracking-tight flex items-center gap-2">
            <UploadIcon className="w-8 h-8 text-brand-600" />
            <span>智能衣物录入</span>
          </h1>
          <p className="mt-1 text-sm text-slate-500">
            {step === 1 ? '第一步：选择或拖拽衣物照片上传' : '第二步：核对与标注服装属性，归档到衣橱'}
          </p>
        </div>

        <Link
          to="/wardrobe"
          className="inline-flex items-center gap-1.5 text-sm font-semibold text-slate-600 hover:text-slate-900 px-3.5 py-2 rounded-xl border border-slate-200 hover:bg-slate-50 transition-colors"
        >
          <ArrowLeft className="w-4 h-4" />
          <span>返回衣橱</span>
        </Link>
      </div>

      {/* 步骤条进度指示器 */}
      <div className="flex items-center justify-center gap-3">
        <div className="flex items-center gap-2">
          <div
            className={`w-8 h-8 rounded-full flex items-center justify-center text-xs font-bold ${
              step === 1
                ? 'bg-slate-900 text-white shadow-sm'
                : 'bg-emerald-600 text-white'
            }`}
          >
            {step > 1 ? <CheckCircle2 className="w-5 h-5" /> : '1'}
          </div>
          <span className="text-xs sm:text-sm font-semibold text-slate-800">上传照片</span>
        </div>

        <div className="w-12 sm:w-20 h-0.5 bg-slate-200" />

        <div className="flex items-center gap-2">
          <div
            className={`w-8 h-8 rounded-full flex items-center justify-center text-xs font-bold ${
              step === 2
                ? 'bg-slate-900 text-white shadow-sm'
                : 'bg-slate-100 text-slate-400 border border-slate-200'
            }`}
          >
            2
          </div>
          <span className={`text-xs sm:text-sm font-semibold ${step === 2 ? 'text-slate-800' : 'text-slate-400'}`}>
            属性标定
          </span>
        </div>
      </div>

      {/* 错误提示 */}
      {error && (
        <div className="p-4 rounded-xl bg-red-50 border border-red-200 flex items-center gap-3 text-red-700">
          <AlertCircle className="w-5 h-5 shrink-0" />
          <p className="text-sm font-medium">{error}</p>
        </div>
      )}

      {/* 步骤 1: 图片选择与上传 */}
      {step === 1 && (
        <div className="bg-white rounded-3xl border border-slate-200/80 p-8 shadow-soft space-y-6">
          <div
            onDragOver={(e) => {
              e.preventDefault();
              setIsDragOver(true);
            }}
            onDragLeave={() => setIsDragOver(false)}
            onDrop={(e) => {
              e.preventDefault();
              setIsDragOver(false);
              if (e.dataTransfer.files && e.dataTransfer.files[0]) {
                handleFileSelect(e.dataTransfer.files[0]);
              }
            }}
            className={`relative rounded-2xl border-2 border-dashed p-10 text-center transition-all duration-200 flex flex-col items-center justify-center ${
              isDragOver
                ? 'border-brand-500 bg-brand-50/50'
                : 'border-slate-300 hover:border-slate-400 bg-slate-50/60'
            }`}
          >
            <input
              type="file"
              accept="image/jpeg,image/png,image/webp"
              onChange={(e) => e.target.files?.[0] && handleFileSelect(e.target.files[0])}
              className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
            />

            {preview ? (
              <div className="space-y-4">
                <img
                  src={preview}
                  alt="照片预览"
                  className="max-h-72 w-auto object-contain rounded-xl shadow-md mx-auto"
                />
                <p className="text-xs text-slate-500">点击或重新拖拽可更换照片</p>
              </div>
            ) : (
              <div className="space-y-3">
                <div className="w-14 h-14 rounded-2xl bg-white shadow-sm border border-slate-200 flex items-center justify-center text-slate-400 mx-auto">
                  <UploadIcon className="w-7 h-7 text-brand-600" />
                </div>
                <div className="space-y-1">
                  <p className="text-sm font-semibold text-slate-800">
                    点击或将衣物图片拖拽到此处
                  </p>
                  <p className="text-xs text-slate-400">
                    支持 JPEG、PNG、WEBP 格式，单张图片不超过 10MB
                  </p>
                </div>
              </div>
            )}
          </div>

          {/* 底部按钮 */}
          <div className="flex items-center justify-between pt-2">
            <button
              type="button"
              onClick={() => {
                // 如果用户不想上传真实照片，支持直接跳到步骤 2
                setStep(2);
              }}
              className="text-xs font-semibold text-slate-500 hover:text-slate-800 underline"
            >
              暂不上传照片，直接手动录入属性 →
            </button>

            <button
              type="button"
              onClick={handleUploadAndAnalyze}
              disabled={!file || uploading || analyzing}
              className="inline-flex items-center gap-2 px-6 py-3 rounded-xl text-sm font-semibold text-white bg-slate-900 hover:bg-brand-600 shadow-md transition-all disabled:opacity-40 cursor-pointer active:scale-95"
            >
              {uploading || analyzing ? (
                <>
                  <RefreshCw className="w-4 h-4 animate-spin" />
                  <span>{analyzing ? 'AI 多模态智能识别中...' : '正在上传照片...'}</span>
                </>
              ) : (
                <>
                  <Sparkles className="w-4 h-4 text-amber-300" />
                  <span>上传照片并一键 AI 识别</span>
                  <ArrowRight className="w-4 h-4" />
                </>
              )}
            </button>
          </div>
        </div>
      )}

      {/* 步骤 2: 服装属性核对与标定 */}
      {step === 2 && (
        <form onSubmit={handleSubmitClothing} className="bg-white rounded-3xl border border-slate-200/80 p-8 shadow-soft space-y-8">
          {/* AI 识别成功徽标通知 */}
          {aiAnalyzed && (
            <div className="bg-gradient-to-r from-brand-50 via-indigo-50 to-purple-50 border border-brand-200/80 rounded-2xl p-4 flex items-center justify-between gap-3 shadow-xs">
              <div className="flex items-center gap-2.5 text-xs text-brand-900 font-medium">
                <Sparkles className="w-5 h-5 text-brand-600 shrink-0 animate-pulse" />
                <span>
                  <strong>AI 视觉大模型已自动解析！</strong>
                  已智能识别品类、主色调、面料厚度与适温温区并为您预填表单，请核对确认或根据喜好微调。
                </span>
              </div>
              <span className="text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded-full bg-brand-600 text-white shrink-0">
                AI PARSED
              </span>
            </div>
          )}

          {/* 快捷模板一键填入 */}
          <div className="bg-slate-50 rounded-2xl p-4 border border-slate-200/70 space-y-2.5">
            <div className="flex items-center gap-1.5 text-xs font-bold uppercase tracking-wider text-slate-700">
              <Sparkles className="w-4 h-4 text-brand-600" />
              <span>常用单品一键快捷填入模板：</span>
            </div>
            <div className="flex flex-wrap gap-2">
              {QUICK_TEMPLATES.map((tmpl) => (
                <button
                  key={tmpl.name}
                  type="button"
                  onClick={() => handleApplyPreset(tmpl.data)}
                  className="px-3 py-1.5 rounded-lg bg-white border border-slate-200 hover:border-brand-500 hover:text-brand-600 text-xs font-medium text-slate-700 shadow-xs transition-colors"
                >
                  {tmpl.name}
                </button>
              ))}
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* 品类选择 */}
            <div>
              <label className="block text-sm font-semibold text-slate-800 mb-1.5">
                衣物主品类
              </label>
              <select
                value={formData.category}
                onChange={(e) => {
                  const cat = e.target.value;
                  setFormData({
                    ...formData,
                    category: cat,
                    sub_category: SUB_CATEGORIES[cat]?.[0] || '单品',
                  });
                }}
                className="w-full rounded-xl border-slate-200 border py-2.5 px-3.5 text-sm focus:border-brand-500 focus:ring-brand-500"
              >
                {Object.entries(CATEGORY_MAP).map(([val, label]) => (
                  <option key={val} value={val}>{label}</option>
                ))}
              </select>
            </div>

            {/* 子品类 */}
            <div>
              <label className="block text-sm font-semibold text-slate-800 mb-1.5">
                细分款式
              </label>
              <select
                value={formData.sub_category}
                onChange={(e) => setFormData({ ...formData, sub_category: e.target.value })}
                className="w-full rounded-xl border-slate-200 border py-2.5 px-3.5 text-sm focus:border-brand-500 focus:ring-brand-500"
              >
                {(SUB_CATEGORIES[formData.category] || []).map((sub) => (
                  <option key={sub} value={sub}>{sub}</option>
                ))}
              </select>
            </div>

            {/* 主色调 (色板快速选择) */}
            <div className="md:col-span-2">
              <label className="block text-sm font-semibold text-slate-800 mb-2 flex items-center gap-1.5">
                <Palette className="w-4 h-4 text-brand-600" />
                <span>主色调选择 ({formData.primary_color})</span>
              </label>
              <div className="flex flex-wrap gap-2.5">
                {PRESET_COLORS.map((col) => {
                  const active = formData.primary_color === col.name;
                  return (
                    <button
                      key={col.name}
                      type="button"
                      onClick={() => setFormData({ ...formData, primary_color: col.name })}
                      className={`flex items-center gap-2 px-3 py-1.5 rounded-xl border text-xs font-semibold transition-all ${
                        active
                          ? 'border-slate-900 bg-slate-900 text-white shadow-sm ring-2 ring-slate-900 ring-offset-1'
                          : 'border-slate-200 hover:border-slate-300 text-slate-700 bg-white'
                      }`}
                    >
                      <span
                        className="w-3.5 h-3.5 rounded-full border border-slate-300 shadow-xs"
                        style={{ backgroundColor: col.hex }}
                      />
                      <span>{col.label}</span>
                    </button>
                  );
                })}
              </div>
            </div>

            {/* 风格基调 */}
            <div>
              <label className="block text-sm font-semibold text-slate-800 mb-1.5">
                风格偏向
              </label>
              <select
                value={formData.style}
                onChange={(e) => setFormData({ ...formData, style: e.target.value })}
                className="w-full rounded-xl border-slate-200 border py-2.5 px-3.5 text-sm focus:border-brand-500 focus:ring-brand-500"
              >
                {STYLE_OPTIONS.map((opt) => (
                  <option key={opt.value} value={opt.value}>{opt.label}</option>
                ))}
              </select>
            </div>

            {/* 面料厚度 */}
            <div>
              <label className="block text-sm font-semibold text-slate-800 mb-1.5">
                厚薄程度
              </label>
              <select
                value={formData.thickness}
                onChange={(e) => setFormData({ ...formData, thickness: e.target.value })}
                className="w-full rounded-xl border-slate-200 border py-2.5 px-3.5 text-sm focus:border-brand-500 focus:ring-brand-500"
              >
                {THICKNESS_OPTIONS.map((opt) => (
                  <option key={opt.value} value={opt.value}>{opt.label}</option>
                ))}
              </select>
            </div>

            {/* 适宜季节 (多选切换) */}
            <div className="md:col-span-2">
              <label className="block text-sm font-semibold text-slate-800 mb-2">
                适宜季节（可多选）
              </label>
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-2.5">
                {SEASON_OPTIONS.map((opt) => {
                  const active = formData.season.includes(opt.value);
                  return (
                    <button
                      key={opt.value}
                      type="button"
                      onClick={() => toggleSeason(opt.value)}
                      className={`py-2 px-3 rounded-xl border text-xs font-semibold transition-all ${
                        active
                          ? 'border-brand-600 bg-brand-50 text-brand-700 font-bold ring-1 ring-brand-500'
                          : 'border-slate-200 text-slate-600 bg-white hover:border-slate-300'
                      }`}
                    >
                      {opt.label}
                    </button>
                  );
                })}
              </div>
            </div>

            {/* 最低温度 */}
            <div>
              <label className="block text-sm font-semibold text-slate-800 mb-1.5">
                适宜最低温度 (℃)
              </label>
              <input
                type="number"
                value={formData.temp_min}
                onChange={(e) => setFormData({ ...formData, temp_min: Number(e.target.value) })}
                className="w-full rounded-xl border-slate-200 border py-2.5 px-3.5 text-sm focus:border-brand-500 focus:ring-brand-500"
              />
            </div>

            {/* 最高温度 */}
            <div>
              <label className="block text-sm font-semibold text-slate-800 mb-1.5">
                适宜最高温度 (℃)
              </label>
              <input
                type="number"
                value={formData.temp_max}
                onChange={(e) => setFormData({ ...formData, temp_max: Number(e.target.value) })}
                className="w-full rounded-xl border-slate-200 border py-2.5 px-3.5 text-sm focus:border-brand-500 focus:ring-brand-500"
              />
            </div>
          </div>

          {/* 底部确认提交操作 */}
          <div className="pt-4 border-t border-slate-100 flex items-center justify-between">
            <button
              type="button"
              onClick={() => setStep(1)}
              className="text-xs font-semibold text-slate-600 hover:text-slate-900"
            >
              ← 返回重选照片
            </button>

            <button
              type="submit"
              disabled={uploading}
              className="inline-flex items-center gap-2 px-7 py-3 rounded-xl text-sm font-semibold text-white bg-slate-900 hover:bg-brand-600 shadow-md transition-all disabled:opacity-40 cursor-pointer active:scale-95"
            >
              {uploading ? (
                <>
                  <RefreshCw className="w-4 h-4 animate-spin" />
                  <span>正在存入数字衣橱...</span>
                </>
              ) : (
                <>
                  <CheckCircle2 className="w-4 h-4" />
                  <span>确认保存至我的衣橱</span>
                </>
              )}
            </button>
          </div>
        </form>
      )}
    </div>
  );
}
