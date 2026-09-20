import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { getClothingList } from '../services/api';
import { ClothingItem } from '../types/clothing';

const CATEGORIES = [
  { label: '全部', value: '' },
  { label: '上装', value: 'top' },
  { label: '下装', value: 'bottom' },
  { label: '外套', value: 'coat' },
  { label: '鞋履', value: 'shoes' },
  { label: '配饰', value: 'accessory' },
];

const WardrobePage: React.FC = () => {
  const [items, setItems] = useState<ClothingItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeCategory, setActiveCategory] = useState<string>('');
  const navigate = useNavigate();

  const fetchItems = async (category: string) => {
    setLoading(true);
    setError(null);
    try {
      const response = await getClothingList(category ? { category } : {});
      if (response.code === 0 && response.data) {
        setItems(response.data.items || []);
      } else {
        setError(response.message || '获取衣物失败');
      }
    } catch (err) {
      setError('网络请求失败');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchItems(activeCategory);
  }, [activeCategory]);

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="flex justify-between items-center mb-8">
        <h1 className="text-3xl font-bold text-gray-800">我的衣橱</h1>
        <button
          onClick={() => navigate('/upload')}
          className="bg-indigo-600 text-white px-4 py-2 rounded-md hover:bg-indigo-700 transition-colors"
        >
          添加衣物
        </button>
      </div>

      <div className="flex space-x-4 mb-6 overflow-x-auto pb-2">
        {CATEGORIES.map((cat) => (
          <button
            key={cat.value}
            onClick={() => setActiveCategory(cat.value)}
            className={`px-4 py-2 rounded-full whitespace-nowrap ${
              activeCategory === cat.value
                ? 'bg-indigo-100 text-indigo-700 font-medium'
                : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
            }`}
          >
            {cat.label}
          </button>
        ))}
      </div>

      {loading ? (
        <div className="flex justify-center items-center py-20">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
        </div>
      ) : error ? (
        <div className="text-center py-20 text-red-500">{error}</div>
      ) : items.length === 0 ? (
        <div className="text-center py-20">
          <p className="text-gray-500 mb-4">暂无衣物，快去添加吧！</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
          {items.map((item) => (
            <div
              key={item.id}
              className="bg-white rounded-lg shadow-md overflow-hidden cursor-pointer hover:shadow-lg transition-shadow"
              onClick={() => navigate(`/wardrobe/${item.id}`)}
            >
              <div className="h-64 overflow-hidden relative bg-gray-100">
                <img
                  src={import.meta.env.VITE_API_BASE_URL ? `${import.meta.env.VITE_API_BASE_URL}${item.image_url}` : item.image_url}
                  alt={item.sub_category}
                  className="w-full h-full object-cover"
                />
                <div className="absolute top-2 right-2 bg-white bg-opacity-90 px-2 py-1 rounded text-xs font-semibold text-gray-700">
                  {item.category === 'top' ? '上装' : item.category === 'bottom' ? '下装' : item.category === 'coat' ? '外套' : item.category === 'shoes' ? '鞋履' : item.category === 'accessory' ? '配饰' : item.category}
                </div>
              </div>
              <div className="p-4">
                <div className="flex justify-between items-center mb-2">
                  <h3 className="text-lg font-semibold text-gray-800">{item.sub_category}</h3>
                  <div className="flex items-center">
                    <div
                      className="w-4 h-4 rounded-full border border-gray-200"
                      style={{ backgroundColor: item.primary_color }}
                      title={item.primary_color}
                    ></div>
                  </div>
                </div>
                <div className="flex flex-wrap gap-2 text-xs text-gray-600 mb-2">
                  <span className="bg-gray-100 px-2 py-1 rounded">{item.style}</span>
                  {item.season.map(s => (
                    <span key={s} className="bg-indigo-50 text-indigo-600 px-2 py-1 rounded">{s}</span>
                  ))}
                </div>
                <div className="text-sm text-gray-500">
                  适宜温度: {item.temp_min}°C - {item.temp_max}°C
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default WardrobePage;
