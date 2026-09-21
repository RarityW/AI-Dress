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
  Check
} from 'lucide-react';
import { getRecommendations, submitRecommendationFeedback, getWeather, generateTryOn, outfitsApi } from '../services/api';
import { OutfitRecommendation, RecommendationResponse } from '../types/clothing';
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
    fetchWeather(city);
  }, [city]);

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

  // AI 模特试穿生图状态
  const [gender, setGender] = useState<'unisex' | 'female' | 'male'>('unisex');
  const [tryOnLoading, setTryOnLoading] = useState<Record<string, boolean>>({});
  const [tryOnImages, setTryOnImages] = useState<Record<string, string>>({});
  const [tryOnError, setTryOnError] = useState<Record<string, string>>({});

  const handleGenerateTryOn = async (outfit: OutfitRecommendation) => {
    const outfitId = outfit.outfit_id;
    setTryOnLoading((prev) => ({ ...prev, [outfitId]: true }));
    setTryOnError((prev) => ({ ...prev, [outfitId]: '' }));

    try {
      const resp = await generateTryOn({
        outfit_id: outfitId,
        items: outfit.items.map((i) => ({
          sub_category: i.sub_category,
          primary_color: i.primary_color,
          image_url: i.image_url,
        })),
        gender,
        scene,
        target_style: targetStyle,
      });

      if ((resp.success || (resp as any).code === 200) && resp.data?.image_url && resp.data.source !== 'error') {
        setTryOnImages((prev) => ({ ...prev, [outfitId]: resp.data.image_url }));
      } else {
        setTryOnError((prev) => ({ ...prev, [outfitId]: resp.data?.error || resp.message || '生成试穿大片失败，请重试' }));
      }
    } catch (err: any) {
      console.error('生图异常:', err);
      setTryOnError((prev) => ({
        ...prev,
        [outfitId]: err?.response?.data?.message || '生成模特试穿效果超时或网络异常，请重试',
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

          {/* 模特偏好设置 */}
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pt-3 border-t border-gray-100">
            <div className="flex items-center gap-2.5">
              <Camera className="h-4 w-4 text-purple-600" />
              <span className="text-xs font-semibold text-gray-700">AI 试穿模特偏好:</span>
              <div className="inline-flex rounded-lg border border-gray-200 bg-gray-50 p-0.5 text-xs">
                {[
                  { key: 'unisex' as const, label: '通用' },
                  { key: 'female' as const, label: '女性模特 👩' },
                  { key: 'male' as const, label: '男性模特 👨' },
                ].map((g) => (
                  <button
                    key={g.key}
                    type="button"
                    onClick={() => setGender(g.key)}
                    className={`px-3 py-1 rounded-md transition-all font-medium cursor-pointer ${
                      gender === g.key
                        ? 'bg-white text-purple-700 shadow-sm font-semibold'
                        : 'text-gray-500 hover:text-gray-900'
                    }`}
                  >
                    {g.label}
                  </button>
                ))}
              </div>
            </div>
            <span className="text-[11px] text-gray-400">
              阿里云通义万相 (DashScope Wanx) 视觉生图已就绪
            </span>
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

                      {/* AI 模特试穿可视化区域 */}
                      <div className="pt-2 border-t border-gray-100">
                        {tryOnImages[outfit.outfit_id] ? (
                          <div className="bg-gradient-to-b from-purple-50/40 to-white rounded-2xl p-5 border border-purple-100/80 space-y-4">
                            <div className="flex items-center justify-between">
                              <div className="flex items-center gap-2">
                                <Sparkles className="h-4 w-4 text-purple-600" />
                                <span className="text-sm font-bold text-gray-900">
                                  通义万相 AI 模特全身试穿效果大片
                                </span>
                                <span className="text-[11px] font-semibold text-purple-700 bg-purple-100 px-2 py-0.5 rounded-full">
                                  8K Lookbook
                                </span>
                              </div>
                              <button
                                type="button"
                                onClick={() => handleGenerateTryOn(outfit)}
                                disabled={tryOnLoading[outfit.outfit_id]}
                                className="text-xs text-brand-600 hover:text-brand-700 font-medium inline-flex items-center gap-1 cursor-pointer disabled:opacity-50"
                              >
                                <RefreshCw className={`h-3 w-3 ${tryOnLoading[outfit.outfit_id] ? 'animate-spin' : ''}`} />
                                重新生成
                              </button>
                            </div>
                            <div className="relative rounded-2xl overflow-hidden max-w-sm mx-auto shadow-lg border border-purple-100 aspect-[3/4] bg-gray-100 group">
                              <img
                                src={tryOnImages[outfit.outfit_id]}
                                alt="AI 模特试穿"
                                className="w-full h-full object-cover transition-transform duration-500 group-hover:scale-105"
                              />
                            </div>
                            <p className="text-center text-xs text-gray-400">
                              基于整套单品光影与面料拓扑合成 · 可作为日常出行着装整体质感参考
                            </p>
                          </div>
                        ) : tryOnLoading[outfit.outfit_id] ? (
                          <div className="bg-purple-50/60 rounded-2xl p-8 border border-purple-200/80 text-center space-y-3">
                            <div className="inline-flex p-3 rounded-full bg-purple-100 text-purple-600 animate-pulse">
                              <Sparkles className="h-6 w-6 animate-spin" />
                            </div>
                            <div className="text-sm font-bold text-purple-900">
                              正在由阿里云通义万相 Wanx 渲染真人模特全身试穿大片...
                            </div>
                            <p className="text-xs text-purple-700/80 max-w-sm mx-auto">
                              系统正在构建专业时尚 Lookbook 摄影光影，并对当前搭配进行全身贴合渲染，预计需要 10~15 秒，请稍候。
                            </p>
                          </div>
                        ) : (
                          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 bg-gradient-to-r from-purple-50/70 to-indigo-50/50 rounded-xl p-3.5 border border-purple-100">
                            <div className="text-xs text-purple-900 flex items-center gap-2 font-medium">
                              <Sparkles className="h-4 w-4 text-purple-600 shrink-0" />
                              <span>想看看这套衣服在模特身上的整体上身视觉效果？</span>
                            </div>
                            <button
                              type="button"
                              onClick={() => handleGenerateTryOn(outfit)}
                              className="inline-flex items-center justify-center gap-1.5 px-4 py-2 bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-700 hover:to-indigo-700 text-white rounded-xl text-xs font-semibold shadow-sm transition-all active:scale-[0.98] cursor-pointer"
                            >
                              <Sparkles className="h-3.5 w-3.5" />
                              生成 AI 模特试穿大片
                            </button>
                          </div>
                        )}
                        {tryOnError[outfit.outfit_id] && (
                          <p className="text-xs text-red-500 mt-2 text-center">
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
                  <div className="flex justify-center gap-2">
                    {[1, 2, 3, 4, 5].map((star) => (
                      <button
                        key={star}
                        type="button"
                        onClick={() => handleRate(star)}
                        className={`p-1.5 rounded-lg transition-transform hover:scale-110 cursor-pointer ${
                          feedbackRating && feedbackRating >= star
                            ? 'text-amber-400'
                            : 'text-gray-300 hover:text-amber-300'
                        }`}
                      >
                        <Star className="h-6 w-6 fill-current" />
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
    </div>
  );
}
