import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import {
  Sparkles,
  Thermometer,
  CloudSun,
  Palette,
  Briefcase,
  Star,
  RefreshCw,
  Plus,
  AlertCircle,
  Award,
  MapPin,
  CheckCircle2,
  Wind,
  Droplets,
  Camera,
  Bookmark,
  Check,
  Download,
  Lock,
  ArrowRight,
  Maximize2,
  X,
  Zap,
} from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';
import { getRecommendations, submitRecommendationFeedback, getWeather, generateTryOn, outfitsApi, modelsApi } from '../services/api';
import { OutfitRecommendation, RecommendationResponse, PresetModel } from '../types/clothing';
import LoadingSpinner from '../components/LoadingSpinner';


const SCENES = [
  { key: 'daily', label: '日常休闲', desc: '舒适百搭，随性自在' },
  { key: 'class', label: '校园上课', desc: '青春活力，低调舒适' },
  { key: 'work', label: '通勤职场', desc: '干练得体，利落专业' },
  { key: 'interview', label: '求职面试', desc: '正式庄重，沉稳自信' },
  { key: 'date', label: '外出约会', desc: '精致浪漫，优雅吸睛' },
  { key: 'sports', label: '运动健身', desc: '吸汗透气，灵动轻便' },
  { key: 'party', label: '聚会社交', desc: '个性潮流，成为焦点' },
];

const STYLES = [
  { key: 'casual', label: '休闲舒适' },
  { key: 'minimal', label: '质感极简' },
  { key: 'formal', label: '干练正式' },
  { key: 'sporty', label: '活力运动' },
  { key: 'street', label: '潮流街头' },
  { key: 'vintage', label: '经典复古' },
  { key: 'elegant', label: '优雅气质' },
];

const CITIES = [
  '北京', '上海', '广州', '深圳', '杭州', '成都', '武汉', '南京', '西安',
  '重庆', '天津', '苏州', '长沙', '青岛', '厦门', '合肥', '福州', '昆明',
  '大连', '哈尔滨', '济南', '沈阳', '长春', '南昌', '郑州', '贵阳', '南宁',
  '海口', '三亚', '乌鲁木齐', '兰州', '银川', '西宁', '呼和浩特', '拉萨',
  '香港', '澳门', '台北'
];

export default function RecommendPage() {
  const { isAuthenticated } = useAuth();
  const [city, setCity] = useState('北京');
  const [temperature, setTemperature] = useState<number>(20);
  const [weatherCondition, setWeatherCondition] = useState('晴');
  const [scene, setScene] = useState('daily');
  const [targetStyle, setTargetStyle] = useState('casual');

  // 实时天气拉取与同步状态
  const [weatherLoading, setWeatherLoading] = useState(false);
  const [weatherInfo, setWeatherInfo] = useState<{
    temperature: number;
    condition: string;
    condition_code: string;
    humidity?: number;
    wind_speed?: number;
    feels_like?: number;
    source: string;
  } | null>(null);

  const fetchWeather = async (targetCity: string) => {
    setWeatherLoading(true);
    try {
      const resp = await getWeather(targetCity);
      if ((resp.success || (resp as any).code === 200) && resp.data) {
        const w = resp.data;
        setWeatherInfo(w);
        if (typeof w.temperature === 'number') {
          setTemperature(Math.round(w.temperature));
        }
        if (w.condition) {
          const text = w.condition;
          if (text.includes('雨')) {
            setWeatherCondition('小雨');
          } else if (text.includes('阴')) {
            setWeatherCondition('阴');
          } else if (text.includes('多云') || text.includes('云')) {
            setWeatherCondition('多云');
          } else if (text.includes('雪')) {
            setWeatherCondition('小雪');
          } else if (text.includes('风')) {
            setWeatherCondition('大风');
          } else {
            setWeatherCondition('晴');
          }
        }
      }
    } catch (err) {
      console.warn('获取城市天气失败，保留默认预设:', err);
    } finally {
      setWeatherLoading(false);
    }
  };

  useEffect(() => {
    if (isAuthenticated) {
      fetchWeather(city);
    }
  }, [city, isAuthenticated]);

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<RecommendationResponse | null>(null);
  const [feedbackRating, setFeedbackRating] = useState<number | null>(null);
  const [feedbackSuccess, setFeedbackSuccess] = useState(false);

  const handleRecommend = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    setLoading(true);
    setError(null);
    setFeedbackRating(null);
    setFeedbackSuccess(false);

    try {
      const resp = await getRecommendations({
        city,
        temperature: Number(temperature),
        weather_condition: weatherCondition,
        scene,
        target_style: targetStyle,
        top_k: 3,
      });

      if (resp.success && resp.data) {
        setResult(resp.data);
      } else {
        setError(resp.message || '获取推荐方案失败，请重试');
      }
    } catch (err: any) {
      console.error(err);
      setError(err?.response?.data?.message || '连接服务器失败，请确保后端服务正常运行');
    } finally {
      setLoading(false);
    }
  };

  const handleRate = async (rating: number) => {
    if (!result?.record_id) return;
    try {
      setFeedbackRating(rating);
      await submitRecommendationFeedback(result.record_id, rating);
      setFeedbackSuccess(true);
    } catch (err) {
      console.error(err);
    }
  };

  // 预设模特图与生图引擎状态
  const [presetModels, setPresetModels] = useState<PresetModel[]>([]);
  const [selectedModelId, setSelectedModelId] = useState<string>('female_1');
  const [selectedEngine, setSelectedEngine] = useState<'qwen' | 'aitryon'>('qwen');
  const [modelGenderFilter, setModelGenderFilter] = useState<'all' | 'female' | 'male'>('all');
  const [previewImageUrl, setPreviewImageUrl] = useState<string | null>(null);

  // 监听 Escape 键快速关闭大图预览模态框
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape' && previewImageUrl) {
        setPreviewImageUrl(null);
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [previewImageUrl]);

  // 加载预设模特列表
  useEffect(() => {
    if (!isAuthenticated) return;
    modelsApi.getPresets().then((resp) => {
      if (resp.success && resp.data && resp.data.length > 0) {
        setPresetModels(resp.data);
      }
    }).catch(() => {
      // 加载失败时使用默认 fallback 列表 (8 位模特)
      setPresetModels([
        { id: 'male_1', label: '小轩 (男模 · 阳光俊朗)', gender: 'male', thumbnail: '/uploads/models/official_model_16.jpg', full_url: '/uploads/models/official_model_16.jpg' },
        { id: 'female_1', label: '雅琪 (女模 · 优雅知性)', gender: 'female', thumbnail: '/uploads/models/official_model_6.jpg', full_url: '/uploads/models/official_model_6.jpg' },
        { id: 'male_2', label: '易峰 (男模 · 商务沉稳)', gender: 'male', thumbnail: '/uploads/models/official_model_3.jpg', full_url: '/uploads/models/official_model_3.jpg' },
        { id: 'female_2', label: '柔依 (女模 · 清新甜美)', gender: 'female', thumbnail: '/uploads/models/official_model_1.jpg', full_url: '/uploads/models/official_model_1.jpg' },
        { id: 'male_3', label: 'Simon (男模 · 混血高级)', gender: 'male', thumbnail: '/uploads/models/official_model_4.jpg', full_url: '/uploads/models/official_model_4.jpg' },
        { id: 'female_3', label: '诗涵 (女模 · 都市摩登)', gender: 'female', thumbnail: '/uploads/models/official_model_2.jpg', full_url: '/uploads/models/official_model_2.jpg' },
        { id: 'male_4', label: '宇航 (男模 · 潮酷街头)', gender: 'male', thumbnail: '/uploads/models/official_model_8.jpg', full_url: '/uploads/models/official_model_8.jpg' },
        { id: 'female_4', label: '语晴 (女模 · 元气日常)', gender: 'female', thumbnail: '/uploads/models/official_model_5.jpg', full_url: '/uploads/models/official_model_5.jpg' },
      ]);
    });
  }, [isAuthenticated]);

  // AI 模特试穿生图状态
  const [tryOnLoading, setTryOnLoading] = useState<Record<string, boolean>>({});
  const [tryOnImages, setTryOnImages] = useState<Record<string, string>>({});
  const [tryOnError, setTryOnError] = useState<Record<string, string>>({});
  const [tryOnSource, setTryOnSource] = useState<Record<string, string>>({});
  const [tryOnEngine, setTryOnEngine] = useState<Record<string, string>>({});

  const handleGenerateTryOn = async (outfit: OutfitRecommendation, engineOverride?: 'qwen' | 'aitryon') => {
    const outfitId = outfit.outfit_id;
    const engineToUse = engineOverride || selectedEngine;
    setTryOnLoading((prev) => ({ ...prev, [outfitId]: true }));
    setTryOnError((prev) => ({ ...prev, [outfitId]: '' }));

    try {
      const resp = await generateTryOn({
        outfit_id: outfitId,
        items: outfit.items.map((i) => ({
          category: i.category,
          sub_category: i.sub_category,
          primary_color: i.primary_color,
          material: (i as any).material,
          image_url: i.image_url,
        })),
        model_id: selectedModelId,
        scene,
        target_style: targetStyle,
        engine: engineToUse,
      });

      if ((resp.success || (resp as any).code === 200) && resp.data?.image_url) {
        setTryOnImages((prev) => ({ ...prev, [outfitId]: resp.data.image_url }));
        setTryOnSource((prev) => ({ ...prev, [outfitId]: resp.data.source || '' }));
        setTryOnEngine((prev) => ({ ...prev, [outfitId]: resp.data.engine || engineToUse }));
        if (resp.data.source === 'error') {
          setTryOnError((prev) => ({ ...prev, [outfitId]: resp.data?.error || '生成失败，请重试' }));
        }
      } else {
        setTryOnError((prev) => ({ ...prev, [outfitId]: resp.data?.error || resp.message || '生成试穿效果失败，请重试' }));
      }
    } catch (err: any) {
      console.error('生图/试穿异常:', err);
      setTryOnError((prev) => ({
        ...prev,
        [outfitId]: err?.response?.data?.message || '生图服务超时或网络异常，请重试',
      }));
    } finally {
      setTryOnLoading((prev) => ({ ...prev, [outfitId]: false }));
    }
  };


  // 搭配收藏状态
  const [savingOutfit, setSavingOutfit] = useState<Record<string, boolean>>({});
  const [savedOutfits, setSavedOutfits] = useState<Record<string, boolean>>({});

  const handleSaveOutfit = async (outfit: OutfitRecommendation) => {
    const outfitId = outfit.outfit_id;
    setSavingOutfit((prev) => ({ ...prev, [outfitId]: true }));
    try {
      const sceneObj = SCENES.find((s) => s.key === scene);
      const styleObj = STYLES.find((s) => s.key === targetStyle);
      const name = `${sceneObj?.label || '精选'} · ${styleObj?.label || '优雅'}穿搭`;
      const res = await outfitsApi.create({
        name,
        occasion: sceneObj?.label || scene,
        item_ids: outfit.items.map((i) => i.id),
        overall_score: outfit.scores.overall_score,
      });
      if (res.success) {
        setSavedOutfits((prev) => ({ ...prev, [outfitId]: true }));
      } else {
        alert(res.message || '收藏失败');
      }
    } catch (err: any) {
      alert(err.message || '收藏失败，请先登录');
    } finally {
      setSavingOutfit((prev) => ({ ...prev, [outfitId]: false }));
    }
  };

  // 未登录拦截引导卡片（软墙）
  if (!isAuthenticated) {
    return (
      <div className="max-w-4xl mx-auto py-10 px-4 animate-fadeIn">
        <div className="glass-card bg-white/90 backdrop-blur-xl rounded-3xl p-8 sm:p-14 border border-slate-200/80 shadow-xl text-center relative overflow-hidden">
          <div className="absolute top-0 right-0 -mr-20 -mt-20 w-64 h-64 bg-gradient-to-br from-purple-400/20 to-indigo-500/20 rounded-full blur-3xl pointer-events-none" />
          <div className="absolute bottom-0 left-0 -ml-20 -mb-20 w-64 h-64 bg-gradient-to-tr from-brand-400/20 to-pink-300/20 rounded-full blur-3xl pointer-events-none" />

          <div className="w-16 h-16 rounded-3xl bg-gradient-to-tr from-purple-600 via-indigo-600 to-brand-500 text-white flex items-center justify-center mx-auto mb-5 shadow-lg shadow-purple-500/25">
            <Lock className="w-8 h-8" />
          </div>

          <h2 className="text-2xl sm:text-3xl font-extrabold text-slate-900 tracking-tight">
            登录解锁 AI 智能穿搭推荐系统
          </h2>
          <p className="text-sm sm:text-base text-slate-500 max-w-lg mx-auto mt-3 leading-relaxed">
            衣见 AI 智能推荐深度依托您的专属私密衣橱资产、个人着装偏好以及 38 城实时微气象感知。登录或注册后即可体验多目标算法自主决策与真人模特虚拟试穿！
          </p>

          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 my-8 max-w-2xl mx-auto text-left">
            <div className="p-4 rounded-2xl bg-slate-50/80 border border-slate-200/60">
              <div className="text-xl mb-1.5">👗</div>
              <div className="text-xs font-bold text-slate-900">私享衣橱匹配</div>
              <div className="text-[11px] text-slate-500 mt-1">100% 调取您衣橱中的真实单品，绝不凭空捏造</div>
            </div>
            <div className="p-4 rounded-2xl bg-slate-50/80 border border-slate-200/60">
              <div className="text-xl mb-1.5">🌦️</div>
              <div className="text-xs font-bold text-slate-900">38 城气象微感知</div>
              <div className="text-[11px] text-slate-500 mt-1">精准拟合温湿度、温区与出行场景需求</div>
            </div>
            <div className="p-4 rounded-2xl bg-slate-50/80 border border-slate-200/60">
              <div className="text-xl mb-1.5">✨</div>
              <div className="text-xs font-bold text-slate-900">真人模特虚拟试穿</div>
              <div className="text-[11px] text-slate-500 mt-1">官方 OutfitAnyone 驱动，真实模特上身大片</div>
            </div>
          </div>

          <div className="flex flex-col sm:flex-row items-center justify-center gap-3.5">
            <Link
              to="/login"
              state={{ from: { pathname: '/recommend' } }}
              className="w-full sm:w-auto inline-flex items-center justify-center gap-2 px-8 py-3.5 rounded-xl bg-slate-900 hover:bg-purple-600 text-white text-sm font-bold shadow-md transition-all active:scale-95 cursor-pointer"
            >
              <span>立即登录</span>
              <ArrowRight className="w-4 h-4" />
            </Link>
            <Link
              to="/login"
              state={{ register: true, isRegister: true, from: { pathname: '/recommend' } }}
              className="w-full sm:w-auto inline-flex items-center justify-center gap-2 px-8 py-3.5 rounded-xl bg-slate-100 hover:bg-slate-200 text-slate-800 text-sm font-semibold transition-all active:scale-95 cursor-pointer"
            >
              <span>注册新账号</span>
            </Link>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-5xl mx-auto space-y-10 pb-16">
      {/* 头部介绍 */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 border-b border-gray-200 pb-5">
        <div>
          <h1 className="text-3xl font-extrabold text-gray-900 tracking-tight flex items-center gap-2">
            <Sparkles className="h-8 w-8 text-brand-600 animate-pulse" />
            AI 智能穿搭推荐
          </h1>
          <p className="mt-2 text-sm text-gray-600">
            基于多目标加权运筹算法（气温 × 风格 × 场景 × 色彩搭配），在您的个人数字衣橱中计算全局最优解。
          </p>
        </div>
        <Link
          to="/wardrobe"
          className="inline-flex items-center gap-1.5 text-sm font-medium text-brand-600 hover:text-brand-700 bg-brand-50 px-4 py-2 rounded-lg transition-colors self-start sm:self-auto"
        >
          <Plus className="h-4 w-4" />
          管理数字衣橱
        </Link>
      </div>

      {/* 参数输入面板 */}
      <div className="bg-white shadow-sm rounded-2xl border border-gray-200/80 p-6 sm:p-8">
        <form onSubmit={handleRecommend} className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {/* 城市选择 */}
            <div>
              <label className="block text-sm font-semibold text-gray-800 mb-1.5">
                目的城市
              </label>
              <select
                value={city}
                onChange={(e) => setCity(e.target.value)}
                className="w-full rounded-lg border-gray-300 shadow-sm focus:border-brand-500 focus:ring-brand-500 text-sm py-2 px-3 border"
              >
                {CITIES.map((c) => (
                  <option key={c} value={c}>{c}</option>
                ))}
              </select>
            </div>

            {/* 当前温度输入 */}
            <div>
              <label className="block text-sm font-semibold text-gray-800 mb-1.5 flex items-center justify-between">
                <span className="flex items-center gap-1">
                  <Thermometer className="h-4 w-4 text-orange-500" />
                  外部温度 ({temperature}℃)
                </span>
                <span className="text-xs text-gray-400 font-normal">可滑动调节</span>
              </label>
              <div className="flex items-center gap-3">
                <input
                  type="range"
                  min="-10"
                  max="38"
                  value={temperature}
                  onChange={(e) => setTemperature(Number(e.target.value))}
                  className="w-full accent-brand-600 cursor-pointer"
                />
                <span className="w-12 text-center text-sm font-bold text-gray-700 bg-gray-100 rounded py-1 px-1.5">
                  {temperature}℃
                </span>
              </div>
            </div>

            {/* 天气状况 */}
            <div>
              <label className="block text-sm font-semibold text-gray-800 mb-1.5 flex items-center gap-1">
                <CloudSun className="h-4 w-4 text-blue-500" />
                天气状况
              </label>
              <select
                value={weatherCondition}
                onChange={(e) => setWeatherCondition(e.target.value)}
                className="w-full rounded-lg border-gray-300 shadow-sm focus:border-brand-500 focus:ring-brand-500 text-sm py-2 px-3 border"
              >
                <option value="晴">晴朗少云 ☀️</option>
                <option value="多云">多云天气 ⛅</option>
                <option value="阴">阴天微凉 ☁️</option>
                <option value="小雨">阴雨有雨 🌧️</option>
                <option value="大风">大风降温 💨</option>
                <option value="小雪">降雪微寒 ❄️</option>
              </select>
            </div>
          </div>

          {/* 实时天气同步状态提示条 */}
          <div className="bg-blue-50/60 rounded-xl p-3 sm:p-4 border border-blue-100 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 text-xs">
            <div className="flex items-center gap-2 text-blue-900">
              {weatherLoading ? (
                <>
                  <RefreshCw className="h-4 w-4 text-blue-600 animate-spin shrink-0" />
                  <span className="font-medium">正在获取「{city}」实时气象数据...</span>
                </>
              ) : weatherInfo ? (
                <>
                  <CheckCircle2 className="h-4 w-4 text-emerald-600 shrink-0" />
                  <div>
                    <span className="font-semibold text-gray-800">
                      已同步「{city}」实时气温：{weatherInfo.temperature}℃ ({weatherInfo.condition})
                    </span>
                    <span className="text-gray-500 ml-2 hidden sm:inline-flex items-center gap-2.5">
                      <span>体感 {weatherInfo.feels_like ?? weatherInfo.temperature}℃</span>
                      <span className="inline-flex items-center gap-1">
                        <Droplets className="h-3 w-3 text-blue-500" />
                        {weatherInfo.humidity ?? 50}%
                      </span>
                      <span className="inline-flex items-center gap-1">
                        <Wind className="h-3 w-3 text-cyan-500" />
                        {weatherInfo.wind_speed ?? 10}km/h
                      </span>
                    </span>
                  </div>
                </>
              ) : (
                <>
                  <MapPin className="h-4 w-4 text-blue-500 shrink-0" />
                  <span className="text-gray-600">选择城市即可自动联网获取当地今日实时气温与天气。</span>
                </>
              )}
            </div>

            <div className="flex items-center gap-3 shrink-0 self-end sm:self-auto">
              <span className="text-gray-400 text-[11px] hidden md:inline">
                支持手动拖拽上方滑块微调
              </span>
              <button
                type="button"
                onClick={() => fetchWeather(city)}
                disabled={weatherLoading}
                className="inline-flex items-center gap-1 px-2.5 py-1 rounded-lg bg-white border border-blue-200 text-blue-700 hover:bg-blue-50 transition-colors font-medium cursor-pointer disabled:opacity-50"
              >
                <RefreshCw className={`h-3 w-3 ${weatherLoading ? 'animate-spin' : ''}`} />
                刷新天气
              </button>
            </div>
          </div>

          {/* 场景选择 (卡片单选) */}
          <div>
            <label className="block text-sm font-semibold text-gray-800 mb-2.5 flex items-center gap-1.5">
              <Briefcase className="h-4 w-4 text-brand-600" />
              穿搭场景需求
            </label>
            <div className="grid grid-cols-2 sm:grid-cols-4 md:grid-cols-7 gap-2.5">
              {SCENES.map((s) => {
                const active = scene === s.key;
                return (
                  <button
                    key={s.key}
                    type="button"
                    onClick={() => setScene(s.key)}
                    className={`py-2 px-3 rounded-xl border text-center transition-all ${
                      active
                        ? 'border-brand-600 bg-brand-50/80 text-brand-700 font-semibold shadow-sm ring-1 ring-brand-500'
                        : 'border-gray-200 hover:border-gray-300 text-gray-600 bg-white'
                    }`}
                  >
                    <div className="text-sm">{s.label}</div>
                  </button>
                );
              })}
            </div>
          </div>

          {/* 风格偏好 */}
          <div>
            <label className="block text-sm font-semibold text-gray-800 mb-2.5 flex items-center gap-1.5">
              <Palette className="h-4 w-4 text-brand-600" />
              偏好风格基调
            </label>
            <div className="flex flex-wrap gap-2">
              {STYLES.map((st) => {
                const active = targetStyle === st.key;
                return (
                  <button
                    key={st.key}
                    type="button"
                    onClick={() => setTargetStyle(st.key)}
                    className={`px-4 py-2 rounded-full text-xs font-medium transition-all ${
                      active
                        ? 'bg-brand-600 text-white shadow-sm ring-2 ring-offset-1 ring-brand-500'
                        : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                    }`}
                  >
                    {st.label}
                  </button>
                );
              })}
            </div>
          </div>

          {/* AI 生图引擎与出镜模特配置 */}
          <div className="space-y-4 pt-4 border-t border-gray-100">
            {/* 引擎切换器 */}
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <Zap className="h-4 w-4 text-amber-500" />
                  <span className="text-sm font-semibold text-gray-800">AI 视觉生成引擎</span>
                </div>
                <span className="text-xs text-purple-700 font-medium bg-purple-50 px-2.5 py-0.5 rounded-full border border-purple-100">
                  {selectedEngine === 'qwen' ? '🌟 通义千问 Qwen 旗舰大片' : '👗 OutfitAnyone 1:1 像素试衣'}
                </span>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                <button
                  type="button"
                  aria-pressed={selectedEngine === 'qwen'}
                  onClick={() => setSelectedEngine('qwen')}
                  className={`p-3.5 rounded-2xl border-2 text-left transition-colors cursor-pointer ${
                    selectedEngine === 'qwen'
                      ? 'border-purple-600 bg-purple-50/50 shadow-sm ring-1 ring-purple-300'
                      : 'border-gray-200 bg-white hover:border-gray-300'
                  }`}
                >
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-bold text-gray-900 flex items-center gap-1.5">
                      <span aria-hidden="true">🌟</span>
                      <span>阿里 Qwen 真实人像大片</span>
                    </span>
                    <span className="text-[10px] font-bold text-white bg-gradient-to-r from-purple-600 to-indigo-600 px-2 py-0.5 rounded-full">
                      推荐
                    </span>
                  </div>
                  <p className="text-[11px] text-gray-500 mt-1.5 leading-relaxed">
                    超真实自然人脸、微表情与发丝级细节，单反景深与场景光影融合，极致逼真人像写真。
                  </p>
                </button>

                <button
                  type="button"
                  aria-pressed={selectedEngine === 'aitryon'}
                  onClick={() => setSelectedEngine('aitryon')}
                  className={`p-3.5 rounded-2xl border-2 text-left transition-colors cursor-pointer ${
                    selectedEngine === 'aitryon'
                      ? 'border-purple-600 bg-purple-50/50 shadow-sm ring-1 ring-purple-300'
                      : 'border-gray-200 bg-white hover:border-gray-300'
                  }`}
                >
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-bold text-gray-900 flex items-center gap-1.5">
                      <span aria-hidden="true">👗</span>
                      <span>OutfitAnyone Plus 1:1 像素试衣</span>
                    </span>
                    <span className="text-[10px] font-medium text-purple-700 bg-purple-100 px-2 py-0.5 rounded-full">
                      高保真
                    </span>
                  </div>
                  <p className="text-[11px] text-gray-500 mt-1.5 leading-relaxed">
                    将用户上传的平铺衣物图片剪裁与纹理，1:1 精确贴合至选定模特身姿。
                  </p>
                </button>
              </div>
            </div>

            {/* 模特选择 */}
            <div className="space-y-2.5">
              <div className="flex items-center justify-between flex-wrap gap-2">
                <div className="flex items-center gap-2">
                  <Camera className="h-4 w-4 text-purple-600" aria-hidden="true" />
                  <span className="text-sm font-semibold text-gray-800">选择出镜模特</span>
                </div>
                {/* 性别筛选 */}
                <div role="tablist" aria-label="模特性别筛选" className="flex items-center gap-1 bg-gray-100 p-0.5 rounded-lg text-xs">
                  <button
                    type="button"
                    role="tab"
                    aria-selected={modelGenderFilter === 'all'}
                    onClick={() => setModelGenderFilter('all')}
                    className={`px-2.5 py-1 rounded-md font-medium transition-colors cursor-pointer ${
                      modelGenderFilter === 'all' ? 'bg-white text-gray-900 shadow-sm' : 'text-gray-500 hover:text-gray-700'
                    }`}
                  >
                    全部 ({presetModels.length})
                  </button>
                  <button
                    type="button"
                    role="tab"
                    aria-selected={modelGenderFilter === 'female'}
                    onClick={() => setModelGenderFilter('female')}
                    className={`px-2.5 py-1 rounded-md font-medium transition-colors cursor-pointer ${
                      modelGenderFilter === 'female' ? 'bg-white text-purple-700 shadow-sm' : 'text-gray-500 hover:text-gray-700'
                    }`}
                  >
                    👩 女模 ({presetModels.filter(m => m.gender === 'female').length})
                  </button>
                  <button
                    type="button"
                    role="tab"
                    aria-selected={modelGenderFilter === 'male'}
                    onClick={() => setModelGenderFilter('male')}
                    className={`px-2.5 py-1 rounded-md font-medium transition-colors cursor-pointer ${
                      modelGenderFilter === 'male' ? 'bg-white text-blue-700 shadow-sm' : 'text-gray-500 hover:text-gray-700'
                    }`}
                  >
                    👨 男模 ({presetModels.filter(m => m.gender === 'male').length})
                  </button>
                </div>
              </div>

              {/* 模特卡片网格 */}
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 max-h-72 overflow-y-auto pr-1">
                {(presetModels.filter((m) => modelGenderFilter === 'all' || m.gender === modelGenderFilter)).map((model) => (
                  <button
                    key={model.id}
                    type="button"
                    aria-pressed={selectedModelId === model.id}
                    aria-label={`选择出镜模特: ${model.label}`}
                    onClick={() => setSelectedModelId(model.id)}
                    className={`relative rounded-xl overflow-hidden border-2 transition-all cursor-pointer aspect-[3/4] group focus-visible:ring-2 focus-visible:ring-purple-500 focus-visible:outline-none ${
                      selectedModelId === model.id
                        ? 'border-purple-600 ring-2 ring-purple-300 ring-offset-1 shadow-md'
                        : 'border-gray-200 hover:border-purple-300'
                    }`}
                  >
                    <img
                      src={model.thumbnail}
                      alt={model.label}
                      loading="lazy"
                      decoding="async"
                      className="w-full h-full object-cover object-top group-hover:scale-105 transition-transform duration-300 motion-reduce:transition-none"
                    />
                    <div className="absolute inset-x-0 bottom-0 bg-gradient-to-t from-black/85 via-black/40 to-transparent pt-6 pb-2 px-2">
                      <div className="text-white text-[11px] font-bold text-center leading-tight truncate">
                        {model.label}
                      </div>
                    </div>
                    {selectedModelId === model.id && (
                      <div className="absolute top-1.5 right-1.5 w-5 h-5 bg-purple-600 rounded-full flex items-center justify-center shadow">
                        <Check className="w-3 h-3 text-white" aria-hidden="true" />
                      </div>
                    )}
                  </button>
                ))}
              </div>
            </div>
          </div>

          {/* 提交按钮 */}
          <div className="pt-2 flex justify-end">
            <button
              type="submit"
              disabled={loading}
              className="inline-flex items-center justify-center gap-2 px-6 py-3 rounded-xl text-base font-semibold text-white bg-brand-600 hover:bg-brand-700 shadow-md shadow-brand-500/20 active:scale-[0.98] transition-all disabled:opacity-50 cursor-pointer"
            >
              {loading ? (
                <>
                  <RefreshCw className="h-5 w-5 animate-spin" />
                  推荐算法正在计算候选穿搭...
                </>
              ) : (
                <>
                  <Sparkles className="h-5 w-5" />
                  智能生成推荐方案
                </>
              )}
            </button>
          </div>
        </form>
      </div>

      {/* 错误提示 */}
      {error && (
        <div className="rounded-xl bg-red-50 border border-red-200 p-4 text-red-700 flex items-center gap-3">
          <AlertCircle className="h-5 w-5 shrink-0" />
          <p className="text-sm font-medium">{error}</p>
        </div>
      )}

      {/* 加载动效 */}
      {loading && (
        <div className="py-16 text-center space-y-4 bg-white/50 rounded-2xl border border-gray-100">
          <LoadingSpinner />
          <p className="text-sm text-gray-500 font-medium animate-pulse">
            正在从您的衣橱检索候选单品，并进行多维度综合评分...
          </p>
        </div>
      )}

      {/* 推荐结果展示 */}
      {!loading && result && (
        <div className="space-y-8">
          <div className="flex items-center justify-between">
            <h2 className="text-xl font-bold text-gray-900 flex items-center gap-2">
              <Award className="h-6 w-6 text-brand-600" />
              为您精选的 TOP-{result.recommendations.length} 穿搭方案
            </h2>
            <span className="text-xs text-gray-500 bg-gray-100 px-3 py-1 rounded-full">
              检索衣橱候选库: {result.total_candidates} 件单品
            </span>
          </div>

          {result.recommendations.length === 0 ? (
            <div className="bg-white rounded-2xl p-12 text-center border border-gray-200 space-y-4">
              <div className="w-16 h-16 bg-amber-50 text-amber-500 rounded-full flex items-center justify-center mx-auto text-2xl">
                ⚠️
              </div>
              <h3 className="text-lg font-semibold text-gray-800">未找到完全契合的穿搭组合</h3>
              <p className="text-sm text-gray-500 max-w-md mx-auto">
                可能由于衣橱内单品数量过少或缺乏上装/下装。建议您多上传几件不同季节与风格的衣物以扩充推荐候选池！
              </p>
              <div className="pt-2">
                <Link
                  to="/upload"
                  className="inline-flex items-center gap-2 px-5 py-2.5 bg-brand-600 text-white rounded-xl text-sm font-medium hover:bg-brand-700 transition-colors shadow-sm"
                >
                  <Plus className="h-4 w-4" />
                  去上传衣物
                </Link>
              </div>
            </div>
          ) : (
            <div className="space-y-6">
              {result.recommendations.map((outfit: OutfitRecommendation, idx: number) => {
                const rankLabels = ['🥇 首选推荐', '🥈 备选搭配', '🥉 风格之选'];
                return (
                  <div
                    key={outfit.outfit_id}
                    className="bg-white rounded-2xl border border-gray-200 shadow-sm overflow-hidden hover:shadow-md transition-shadow"
                  >
                    {/* 卡片头部 */}
                    <div className="bg-gradient-to-r from-gray-50 to-white px-6 py-4 border-b border-gray-100 flex flex-wrap items-center justify-between gap-3">
                      <div className="flex items-center gap-3">
                        <span className="text-sm font-bold text-brand-700 bg-brand-100/70 px-3 py-1 rounded-full">
                          {rankLabels[idx] || `方案 ${idx + 1}`}
                        </span>
                        <span className="text-xs text-gray-400">ID: {outfit.outfit_id}</span>
                      </div>
                      <div className="flex items-center gap-3">
                        <button
                          type="button"
                          onClick={() => handleSaveOutfit(outfit)}
                          disabled={savingOutfit[outfit.outfit_id] || savedOutfits[outfit.outfit_id]}
                          className={`inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs font-bold transition-all cursor-pointer ${
                            savedOutfits[outfit.outfit_id]
                              ? 'bg-amber-100 text-amber-800 border border-amber-300'
                              : 'bg-slate-100 text-slate-700 hover:bg-amber-50 hover:text-amber-700 hover:border-amber-200 border border-slate-200'
                          }`}
                        >
                          {savedOutfits[outfit.outfit_id] ? (
                            <>
                              <Check className="w-3.5 h-3.5 text-amber-600" />
                              <span>已收藏</span>
                            </>
                          ) : savingOutfit[outfit.outfit_id] ? (
                            <div className="w-3.5 h-3.5 border-2 border-amber-600 border-t-transparent rounded-full animate-spin" />
                          ) : (
                            <>
                              <Bookmark className="w-3.5 h-3.5" />
                              <span>收藏此搭配</span>
                            </>
                          )}
                        </button>
                        <div className="h-6 w-px bg-slate-200" />
                        <div className="flex items-center gap-2">
                          <span className="text-xs text-gray-500">综合匹配指数</span>
                          <div className="text-xl font-extrabold text-brand-600">
                            {outfit.scores.overall_score}%
                          </div>
                        </div>
                      </div>
                    </div>

                    <div className="p-6 space-y-6">
                      {/* 单品网格 */}
                      <div>
                        <div className="text-xs font-semibold uppercase tracking-wider text-gray-400 mb-3">
                          搭配单品清单 ({outfit.items.length} 件)
                        </div>
                        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
                          {outfit.items.map((item) => (
                            <div
                              key={item.id}
                              className="group bg-gray-50 rounded-xl p-3 border border-gray-100 flex flex-col items-center text-center transition-all hover:bg-white hover:border-brand-300"
                            >
                              <div className="w-full aspect-square bg-white rounded-lg overflow-hidden border border-gray-200/60 mb-2.5 flex items-center justify-center">
                                {item.image_url ? (
                                  <img
                                    src={item.image_url}
                                    alt={item.sub_category}
                                    className="w-full h-full object-cover group-hover:scale-105 transition-transform"
                                  />
                                ) : (
                                  <span className="text-3xl text-gray-300">
                                    {item.category === 'top' ? '👕' : item.category === 'bottom' ? '👖' : item.category === 'coat' ? '🧥' : '👟'}
                                  </span>
                                )}
                              </div>
                              <div className="font-semibold text-xs text-gray-800 line-clamp-1">
                                {item.primary_color} {item.sub_category}
                              </div>
                              <div className="text-[11px] text-gray-500 mt-0.5">
                                {item.temp_min}℃ ~ {item.temp_max}℃
                              </div>
                            </div>
                          ))}
                        </div>
                      </div>

                      {/* 评分维度条形拆解 */}
                      <div className="bg-gray-50/70 rounded-xl p-4 border border-gray-100">
                        <div className="text-xs font-semibold text-gray-500 mb-3">
                          算法评分维度细分
                        </div>
                        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
                          <div>
                            <div className="flex justify-between text-xs text-gray-600 mb-1">
                              <span>气温契合度</span>
                              <span className="font-bold text-gray-800">{outfit.scores.weather_score}%</span>
                            </div>
                            <div className="w-full bg-gray-200 rounded-full h-2 overflow-hidden">
                              <div
                                className="bg-blue-500 h-2 rounded-full"
                                style={{ width: `${outfit.scores.weather_score}%` }}
                              />
                            </div>
                          </div>
                          <div>
                            <div className="flex justify-between text-xs text-gray-600 mb-1">
                              <span>风格契合度</span>
                              <span className="font-bold text-gray-800">{outfit.scores.style_score}%</span>
                            </div>
                            <div className="w-full bg-gray-200 rounded-full h-2 overflow-hidden">
                              <div
                                className="bg-purple-500 h-2 rounded-full"
                                style={{ width: `${outfit.scores.style_score}%` }}
                              />
                            </div>
                          </div>
                          <div>
                            <div className="flex justify-between text-xs text-gray-600 mb-1">
                              <span>场景适宜度</span>
                              <span className="font-bold text-gray-800">{outfit.scores.scene_score}%</span>
                            </div>
                            <div className="w-full bg-gray-200 rounded-full h-2 overflow-hidden">
                              <div
                                className="bg-emerald-500 h-2 rounded-full"
                                style={{ width: `${outfit.scores.scene_score}%` }}
                              />
                            </div>
                          </div>
                          <div>
                            <div className="flex justify-between text-xs text-gray-600 mb-1">
                              <span>色彩协调度</span>
                              <span className="font-bold text-gray-800">{outfit.scores.color_score}%</span>
                            </div>
                            <div className="w-full bg-gray-200 rounded-full h-2 overflow-hidden">
                              <div
                                className="bg-amber-500 h-2 rounded-full"
                                style={{ width: `${outfit.scores.color_score}%` }}
                              />
                            </div>
                          </div>
                        </div>
                      </div>

                      {/* 推荐理由气泡 */}
                      <div className="bg-brand-50/50 rounded-xl p-4 border border-brand-100/60 flex items-start gap-3">
                        <Sparkles className="h-5 w-5 text-brand-600 shrink-0 mt-0.5" />
                        <p className="text-sm text-gray-700 leading-relaxed">
                          {outfit.reason}
                        </p>
                      </div>

                      {/* AI 模特试穿与时尚生图可视化区域 */}
                      <div className="pt-2 border-t border-gray-100">
                        {tryOnImages[outfit.outfit_id] ? (
                          <div className="bg-gradient-to-b from-purple-50/40 via-white to-slate-50/50 rounded-2xl p-5 border border-purple-100/80 space-y-4 shadow-sm">
                            <div className="flex flex-wrap items-center justify-between gap-3">
                              <div className="flex items-center gap-2">
                                <Sparkles className="h-4 w-4 text-purple-600" />
                                <span className="text-sm font-bold text-gray-900">
                                  AI 穿搭上身效果
                                </span>
                                {(tryOnEngine[outfit.outfit_id] === 'qwen' || tryOnSource[outfit.outfit_id] === 'qwen-image-plus') && (
                                  <span className="text-[11px] font-bold text-purple-700 bg-gradient-to-r from-purple-100 to-indigo-100 border border-purple-200 px-2.5 py-0.5 rounded-full flex items-center gap-1 shadow-xs">
                                    <span>🌟</span>
                                    <span>阿里 Qwen 真实时尚大片</span>
                                  </span>
                                )}
                                {(tryOnEngine[outfit.outfit_id] === 'aitryon' || tryOnSource[outfit.outfit_id] === 'aitryon-plus' || tryOnSource[outfit.outfit_id] === 'aitryon') && (
                                  <span className="text-[11px] font-bold text-indigo-700 bg-indigo-100 border border-indigo-200 px-2.5 py-0.5 rounded-full flex items-center gap-1 shadow-xs">
                                    <span>👗</span>
                                    <span>OutfitAnyone 1:1 试衣</span>
                                  </span>
                                )}
                                {tryOnSource[outfit.outfit_id] === 'cache' && (
                                  <span className="text-[11px] font-semibold text-emerald-700 bg-emerald-100 px-2 py-0.5 rounded-full">
                                    已缓存
                                  </span>
                                )}
                              </div>

                              <div className="flex items-center gap-2">
                                <button
                                  type="button"
                                  onClick={() => setPreviewImageUrl(tryOnImages[outfit.outfit_id])}
                                  className="text-xs text-purple-700 bg-purple-50 hover:bg-purple-100 border border-purple-200 px-2.5 py-1.5 rounded-lg font-semibold inline-flex items-center gap-1 transition-all cursor-pointer"
                                >
                                  <Maximize2 className="h-3 w-3" />
                                  高清全屏
                                </button>
                                <a
                                  href={tryOnImages[outfit.outfit_id]}
                                  download={`yijian_outfit_${outfit.outfit_id}.png`}
                                  target="_blank"
                                  rel="noopener noreferrer"
                                  className="text-xs text-gray-600 hover:text-gray-900 bg-gray-100 hover:bg-gray-200 px-2.5 py-1.5 rounded-lg font-medium inline-flex items-center gap-1 transition-all"
                                >
                                  <Download className="h-3 w-3" />
                                  下载
                                </a>
                                <div className="flex items-center gap-1">
                                  <button
                                    type="button"
                                    onClick={() => handleGenerateTryOn(outfit, 'qwen')}
                                    disabled={tryOnLoading[outfit.outfit_id]}
                                    title="使用阿里 Qwen 重新生成超真实人像大片"
                                    className="text-xs text-brand-600 hover:text-brand-800 bg-brand-50 hover:bg-brand-100 px-2.5 py-1.5 rounded-lg font-medium inline-flex items-center gap-1 cursor-pointer disabled:opacity-50 transition-all"
                                  >
                                    <RefreshCw className={`h-3 w-3 ${tryOnLoading[outfit.outfit_id] ? 'animate-spin' : ''}`} />
                                    <span>Qwen 生图</span>
                                  </button>
                                  <button
                                    type="button"
                                    onClick={() => handleGenerateTryOn(outfit, 'aitryon')}
                                    disabled={tryOnLoading[outfit.outfit_id]}
                                    title="使用 OutfitAnyone Plus 进行 1:1 像素贴合试衣"
                                    className="text-xs text-indigo-600 hover:text-indigo-800 bg-indigo-50 hover:bg-indigo-100 px-2.5 py-1.5 rounded-lg font-medium inline-flex items-center gap-1 cursor-pointer disabled:opacity-50 transition-all"
                                  >
                                    <RefreshCw className={`h-3 w-3 ${tryOnLoading[outfit.outfit_id] ? 'animate-spin' : ''}`} />
                                    <span>1:1 试衣</span>
                                  </button>
                                </div>
                              </div>
                            </div>

                            {/* 图片展示卡片（点击可全屏） */}
                            <div
                              onClick={() => setPreviewImageUrl(tryOnImages[outfit.outfit_id])}
                              className="relative rounded-2xl overflow-hidden max-w-sm mx-auto shadow-lg border border-purple-100 aspect-square bg-gray-100 group cursor-zoom-in"
                            >
                              <img
                                src={tryOnImages[outfit.outfit_id]}
                                alt="虚拟试穿效果"
                                className="w-full h-full object-cover transition-transform duration-500 group-hover:scale-105"
                              />
                              <div className="absolute inset-0 bg-black/30 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center gap-2 text-white font-bold text-xs">
                                <Maximize2 className="w-4 h-4" />
                                <span>点击查看高清原图</span>
                              </div>
                            </div>

                            {tryOnError[outfit.outfit_id] && (
                              <p className="text-xs text-amber-600 text-center bg-amber-50 rounded-lg px-3 py-2">
                                ℹ️ {tryOnError[outfit.outfit_id]}
                              </p>
                            )}
                            <p className="text-center text-xs text-gray-400 leading-relaxed">
                              {tryOnEngine[outfit.outfit_id] === 'qwen' || tryOnSource[outfit.outfit_id] === 'qwen-image-plus'
                                ? '由阿里通义千问 Qwen-Image-Plus 生图旗舰大模型智能合成 · 真实五官与发丝级光影，场景深度融合'
                                : '由阿里云百炼 OutfitAnyone Plus 试衣模型智能合成 · 1:1 真实衣物像素贴合'}
                            </p>
                          </div>
                        ) : tryOnLoading[outfit.outfit_id] ? (
                          <div className="bg-gradient-to-br from-purple-50/80 via-indigo-50/50 to-white rounded-2xl p-8 border border-purple-200/80 text-center space-y-3.5 shadow-sm">
                            <div className="inline-flex p-3.5 rounded-2xl bg-gradient-to-tr from-purple-600 to-indigo-600 text-white shadow-md shadow-purple-500/20 animate-pulse">
                              <Sparkles className="h-6 w-6 animate-spin" />
                            </div>
                            <div className="text-base font-extrabold text-slate-900">
                              {selectedEngine === 'qwen' ? '🌟 阿里通义千问正在渲染超真实时尚大片...' : '👗 OutfitAnyone 正在进行 1:1 像素贴合试穿...'}
                            </div>
                            <p className="text-xs text-slate-600 max-w-md mx-auto leading-relaxed">
                              {selectedEngine === 'qwen'
                                ? '正在结合单品色彩面料、真实天气与场景光影，生成自然五官与大师级单反人像（预计 6~12 秒）'
                                : '正在将您衣橱中的真实单品像素级迁移贴合至模特身姿（预计 10~20 秒）'}
                            </p>
                          </div>
                        ) : (
                          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 bg-gradient-to-r from-purple-50/80 via-indigo-50/60 to-purple-50/80 rounded-2xl p-4 border border-purple-100 shadow-xs">
                            <div className="text-xs text-purple-900 flex items-center gap-2 font-medium">
                              <Sparkles className="h-4 w-4 text-purple-600 shrink-0" />
                              <span>想看看这套穿搭在模特身上的真实上身效果？点击一键生成</span>
                            </div>
                            <div className="flex items-center gap-2">
                              <button
                                type="button"
                                onClick={() => handleGenerateTryOn(outfit, 'qwen')}
                                className="inline-flex items-center justify-center gap-1.5 px-4 py-2 bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-700 hover:to-indigo-700 text-white rounded-xl text-xs font-bold shadow-md shadow-purple-500/20 transition-all active:scale-[0.98] cursor-pointer"
                              >
                                <Sparkles className="h-3.5 w-3.5" />
                                <span>生成 Qwen 大片 (推荐)</span>
                              </button>
                              <button
                                type="button"
                                onClick={() => handleGenerateTryOn(outfit, 'aitryon')}
                                className="inline-flex items-center justify-center gap-1.5 px-3 py-2 bg-white hover:bg-purple-50 text-purple-700 border border-purple-200 rounded-xl text-xs font-semibold shadow-xs transition-all active:scale-[0.98] cursor-pointer"
                              >
                                <span>1:1 像素试衣</span>
                              </button>
                            </div>
                          </div>
                        )}
                        {tryOnError[outfit.outfit_id] && !tryOnImages[outfit.outfit_id] && (
                          <p className="text-xs text-red-500 mt-2 text-center font-medium bg-red-50 py-2 rounded-lg">
                            ⚠️ {tryOnError[outfit.outfit_id]}
                          </p>
                        )}
                      </div>

                    </div>
                  </div>
                );
              })}

              {/* 满意度打分 */}
              {result.record_id && (
                <div className="bg-white rounded-xl p-5 border border-gray-200 text-center space-y-2">
                  <div className="text-sm font-semibold text-gray-700">
                    对本次推荐满意吗？请给出您的打分：
                  </div>
                  <div role="group" aria-label="推荐满意度评价" className="flex justify-center gap-2">
                    {[1, 2, 3, 4, 5].map((star) => (
                      <button
                        key={star}
                        type="button"
                        onClick={() => handleRate(star)}
                        aria-label={`打分 ${star} 星`}
                        className={`p-1.5 rounded-lg transition-transform hover:scale-110 cursor-pointer ${
                          feedbackRating && feedbackRating >= star
                            ? 'text-amber-400'
                            : 'text-gray-300 hover:text-amber-300'
                        }`}
                      >
                        <Star className="h-6 w-6 fill-current" aria-hidden="true" />
                      </button>
                    ))}
                  </div>
                  {feedbackSuccess && (
                    <p className="text-xs text-emerald-600 font-medium">
                      ✓ 评价成功！系统已记录您的偏好反馈。
                    </p>
                  )}
                </div>
              )}
            </div>
          )}
        </div>
      )}

      {/* 高清图片大图预览弹窗 (Lightbox Modal) */}
      {previewImageUrl && (
        <div
          role="dialog"
          aria-modal="true"
          aria-label="AI 穿搭高清效果原图预览"
          onClick={() => setPreviewImageUrl(null)}
          className="fixed inset-0 z-50 bg-black/85 backdrop-blur-md flex items-center justify-center p-4 animate-fadeIn cursor-zoom-out"
        >
          <div
            onClick={(e) => e.stopPropagation()}
            className="relative max-w-2xl w-full bg-slate-900 rounded-3xl overflow-hidden shadow-2xl border border-slate-700/80 cursor-default"
          >
            <div className="flex items-center justify-between px-6 py-4 bg-slate-800/80 border-b border-slate-700/80">
              <div className="flex items-center gap-2 text-white text-sm font-bold">
                <Sparkles className="w-4 h-4 text-purple-400" aria-hidden="true" />
                <span>AI 穿搭高清效果原图</span>
              </div>
              <div className="flex items-center gap-2">
                <a
                  href={previewImageUrl}
                  download="yijian_lookbook_hd.png"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="p-2 rounded-xl bg-slate-700 hover:bg-slate-600 text-white text-xs font-semibold inline-flex items-center gap-1.5 transition-colors"
                >
                  <Download className="w-3.5 h-3.5" aria-hidden="true" />
                  <span>下载原图</span>
                </a>
                <button
                  type="button"
                  onClick={() => setPreviewImageUrl(null)}
                  aria-label="关闭原图预览"
                  className="p-2 rounded-xl bg-slate-700 hover:bg-red-500/80 text-white transition-colors cursor-pointer"
                >
                  <X className="w-4 h-4" aria-hidden="true" />
                </button>
              </div>
            </div>
            <div className="p-4 flex items-center justify-center bg-black/40">
              <img
                src={previewImageUrl}
                alt="AI 穿搭高清效果原图大图"
                loading="eager"
                decoding="async"
                className="max-h-[75vh] w-auto rounded-2xl object-contain shadow-xl"
              />
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
