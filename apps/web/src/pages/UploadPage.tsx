import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { uploadClothingImage, createClothing } from '../services/api';
import { ClothingItemCreate } from '../types/clothing';

const CATEGORY_MAP = {
  top: '上装',
  bottom: '下装',
  coat: '外套',
  shoes: '鞋履',
  accessory: '配饰',
};

const SUB_CATEGORIES: Record<string, string[]> = {
  top: ['T恤', '衬衫', 'Polo衫', '毛衣', '卫衣', '背心'],
  bottom: ['牛仔裤', '西裤', '短裤', '裙子', '运动裤'],
  coat: ['夹克', '西装', '风衣', '羽绒服', '开衫', '大衣'],
  shoes: ['运动鞋', '靴子', '凉鞋', '乐福鞋', '高跟鞋', '平底鞋'],
  accessory: ['帽子', '围巾', '包', '腰带', '手表', '眼镜'],
};

const STYLE_OPTIONS = [
  { value: '休闲', label: '休闲' },
  { value: '正式', label: '正式' },
  { value: '运动', label: '运动' },
  { value: '简约', label: '简约' },
  { value: '复古', label: '复古' },
  { value: '街头', label: '街头' },
  { value: '优雅', label: '优雅' },
];

const THICKNESS_OPTIONS = [
  { value: '薄', label: '薄' },
  { value: '中等', label: '中等' },
  { value: '厚', label: '厚' },
];

const SEASON_OPTIONS = [
  { value: '春', label: '春' },
  { value: '夏', label: '夏' },
  { value: '秋', label: '秋' },
  { value: '冬', label: '冬' },
];

const UploadPage: React.FC = () => {
  const navigate = useNavigate();
  const [step, setStep] = useState<1 | 2>(1);
  const [file, setFile] = useState<File | null>(null);
  const [preview, setPreview] = useState<string>('');
  const [uploading, setUploading] = useState(false);
  const [imageUrl, setImageUrl] = useState('');
  const [error, setError] = useState('');

  const [formData, setFormData] = useState<ClothingItemCreate>({
    category: 'top',
    sub_category: 'T恤',
    primary_color: '#000000',
    secondary_color: '',
    style: '休闲',
    thickness: '中等',
    season: ['春', '秋'],
    temp_min: 15,
    temp_max: 25,
  });

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const selected = e.target.files[0];
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
    }
  };

  const handleUpload = async () => {
    if (!file) return;
    setUploading(true);
    setError('');
    try {
      const res = await uploadClothingImage(file);
      if (res.code === 0 && res.data) {
        setImageUrl(res.data.image_url);
        setStep(2);
      } else {
        setError(res.message || '上传失败');
      }
    } catch (err) {
      setError('网络请求失败');
    } finally {
      setUploading(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (formData.season.length === 0) {
      setError('请至少选择一个适合季节');
      return;
    }
    setUploading(true);
    setError('');
    try {
      const res = await createClothing({ ...formData, image_url: imageUrl });
      if (res.code === 0) {
        navigate('/wardrobe');
      } else {
        setError(res.message || '创建失败');
      }
    } catch (err) {
      setError('提交失败');
    } finally {
      setUploading(false);
    }
  };

  const handleCategoryChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const newCat = e.target.value as string;
    setFormData({
      ...formData,
      category: newCat,
      sub_category: SUB_CATEGORIES[newCat][0],
    });
  };

  const handleSeasonChange = (season: string) => {
    setFormData(prev => {
      const current = new Set(prev.season);
      if (current.has(season)) {
        current.delete(season);
      } else {
        current.add(season);
      }
      return { ...prev, season: Array.from(current) };
    });
  };

  return (
    <div className="container mx-auto px-4 py-8 max-w-2xl">
      <div className="flex items-center justify-between mb-8">
        <h1 className="text-3xl font-bold text-gray-800">
          {step === 1 ? '上传衣物' : '填写衣物信息'}
        </h1>
        <button
          onClick={() => navigate('/wardrobe')}
          className="text-indigo-600 hover:text-indigo-800"
        >
          返回衣橱
        </button>
      </div>

      {error && (
        <div className="bg-red-50 text-red-600 p-4 rounded-md mb-6">
          {error}
        </div>
      )}

      {step === 1 ? (
        <div className="bg-white p-8 rounded-lg shadow-sm border border-gray-200">
          <div className="flex flex-col items-center justify-center border-2 border-dashed border-gray-300 rounded-lg p-10 bg-gray-50 hover:bg-gray-100 transition-colors cursor-pointer relative">
            <input
              type="file"
              className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
              onChange={handleFileSelect}
              accept="image/jpeg,image/png,image/webp"
            />
            {preview ? (
              <img src={preview} alt="Preview" className="max-h-64 object-contain mb-4 rounded" />
            ) : (
              <div className="text-center">
                <svg className="mx-auto h-12 w-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                </svg>
                <p className="mt-2 text-sm text-gray-600">点击或拖拽图片到此处</p>
                <p className="mt-1 text-xs text-gray-500">支持 JPEG, PNG, WEBP (最大 10MB)</p>
              </div>
            )}
          </div>
          
          <button
            onClick={handleUpload}
            disabled={!file || uploading}
            className="w-full mt-6 bg-indigo-600 text-white py-3 rounded-md font-medium hover:bg-indigo-700 disabled:bg-indigo-300 transition-colors"
          >
            {uploading ? '上传中...' : '下一步'}
          </button>
        </div>
      ) : (
        <form onSubmit={handleSubmit} className="bg-white p-6 rounded-lg shadow-sm border border-gray-200 space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">类别</label>
              <select
                value={formData.category}
                onChange={handleCategoryChange}
                className="w-full border border-gray-300 rounded-md p-2 focus:ring-indigo-500 focus:border-indigo-500"
              >
                {Object.entries(CATEGORY_MAP).map(([val, label]) => (
                  <option key={val} value={val}>{label}</option>
                ))}
              </select>
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">子类别</label>
              <select
                value={formData.sub_category}
                onChange={(e) => setFormData({...formData, sub_category: e.target.value})}
                className="w-full border border-gray-300 rounded-md p-2 focus:ring-indigo-500 focus:border-indigo-500"
              >
                {SUB_CATEGORIES[formData.category].map((opt) => (
                  <option key={opt} value={opt}>{opt}</option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">主色调</label>
              <input
                type="color"
                value={formData.primary_color}
                onChange={(e) => setFormData({...formData, primary_color: e.target.value})}
                className="w-full h-10 p-1 border border-gray-300 rounded-md"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">辅助色调 (可选)</label>
              <input
                type="color"
                value={formData.secondary_color || '#ffffff'}
                onChange={(e) => setFormData({...formData, secondary_color: e.target.value})}
                className="w-full h-10 p-1 border border-gray-300 rounded-md"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">风格</label>
              <select
                value={formData.style}
                onChange={(e) => setFormData({...formData, style: e.target.value})}
                className="w-full border border-gray-300 rounded-md p-2 focus:ring-indigo-500 focus:border-indigo-500"
              >
                {STYLE_OPTIONS.map(opt => (
                  <option key={opt.value} value={opt.value}>{opt.label}</option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">厚度</label>
              <select
                value={formData.thickness}
                onChange={(e) => setFormData({...formData, thickness: e.target.value})}
                className="w-full border border-gray-300 rounded-md p-2 focus:ring-indigo-500 focus:border-indigo-500"
              >
                {THICKNESS_OPTIONS.map(opt => (
                  <option key={opt.value} value={opt.value}>{opt.label}</option>
                ))}
              </select>
            </div>

            <div className="md:col-span-2">
              <label className="block text-sm font-medium text-gray-700 mb-2">适合季节</label>
              <div className="flex space-x-4">
                {SEASON_OPTIONS.map(opt => (
                  <label key={opt.value} className="flex items-center space-x-2">
                    <input
                      type="checkbox"
                      checked={formData.season.includes(opt.value)}
                      onChange={() => handleSeasonChange(opt.value)}
                      className="rounded text-indigo-600 focus:ring-indigo-500"
                    />
                    <span>{opt.label}</span>
                  </label>
                ))}
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">最低温度 (°C)</label>
              <input
                type="number"
                value={formData.temp_min}
                onChange={(e) => setFormData({...formData, temp_min: parseInt(e.target.value) || 0})}
                className="w-full border border-gray-300 rounded-md p-2 focus:ring-indigo-500 focus:border-indigo-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">最高温度 (°C)</label>
              <input
                type="number"
                value={formData.temp_max}
                onChange={(e) => setFormData({...formData, temp_max: parseInt(e.target.value) || 0})}
                className="w-full border border-gray-300 rounded-md p-2 focus:ring-indigo-500 focus:border-indigo-500"
              />
            </div>
          </div>

          <button
            type="submit"
            disabled={uploading}
            className="w-full bg-indigo-600 text-white py-3 rounded-md font-medium hover:bg-indigo-700 disabled:bg-indigo-300 transition-colors"
          >
            {uploading ? '提交中...' : '完成添加'}
          </button>
        </form>
      )}
    </div>
  );
};

export default UploadPage;
