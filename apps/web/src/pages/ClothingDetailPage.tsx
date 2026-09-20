import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { getClothingDetail, deleteClothing } from '../services/api';
import { ClothingItem } from '../types/clothing';

const CATEGORY_MAP: Record<string, string> = {
  top: '上装',
  bottom: '下装',
  coat: '外套',
  shoes: '鞋履',
  accessory: '配饰',
};

const ClothingDetailPage: React.FC = () => {
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
        if (response.code === 0 && response.data) {
          setItem(response.data);
        } else {
          setError(response.message || '获取衣物详情失败');
        }
      } catch (err) {
        setError('网络请求失败');
      } finally {
        setLoading(false);
      }
    };
    
    fetchDetail();
  }, [id]);

  const handleDelete = async () => {
    if (!id || !window.confirm('确定要删除这件衣物吗？此操作不可恢复。')) {
      return;
    }
    
    setDeleting(true);
    try {
      const response = await deleteClothing(id);
      if (response.code === 0) {
        navigate('/wardrobe');
      } else {
        alert(response.message || '删除失败');
        setDeleting(false);
      }
    } catch (err) {
      alert('网络请求失败');
      setDeleting(false);
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center py-32">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
      </div>
    );
  }

  if (error || !item) {
    return (
      <div className="container mx-auto px-4 py-16 text-center">
        <p className="text-red-500 mb-6 text-lg">{error || '衣物不存在'}</p>
        <button
          onClick={() => navigate('/wardrobe')}
          className="text-indigo-600 hover:text-indigo-800 font-medium"
        >
          返回衣橱
        </button>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8 max-w-4xl">
      <div className="mb-6 flex justify-between items-center">
        <button
          onClick={() => navigate('/wardrobe')}
          className="flex items-center text-gray-600 hover:text-indigo-600 transition-colors"
        >
          <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
          </svg>
          返回衣橱
        </button>
        <button
          onClick={handleDelete}
          disabled={deleting}
          className="text-red-500 hover:text-red-700 disabled:text-red-300 font-medium"
        >
          {deleting ? '删除中...' : '删除衣物'}
        </button>
      </div>

      <div className="bg-white rounded-xl shadow-lg overflow-hidden flex flex-col md:flex-row">
        <div className="md:w-1/2 h-96 md:h-auto bg-gray-100 relative">
          <img
            src={import.meta.env.VITE_API_BASE_URL ? `${import.meta.env.VITE_API_BASE_URL}${item.image_url}` : item.image_url}
            alt={item.sub_category}
            className="w-full h-full object-cover"
          />
          <div className="absolute top-4 right-4 bg-white/90 backdrop-blur-sm px-3 py-1 rounded-full text-sm font-semibold text-gray-800 shadow-sm">
            {CATEGORY_MAP[item.category] || item.category}
          </div>
        </div>
        
        <div className="md:w-1/2 p-8 flex flex-col justify-center">
          <h1 className="text-3xl font-bold text-gray-800 mb-2">{item.sub_category}</h1>
          <p className="text-gray-500 mb-8 text-sm">添加于 {new Date(item.created_at).toLocaleDateString()}</p>
          
          <div className="space-y-6">
            <div className="grid grid-cols-2 gap-y-6 gap-x-4">
              <div>
                <h3 className="text-sm text-gray-500 mb-1">主色调</h3>
                <div className="flex items-center">
                  <div
                    className="w-6 h-6 rounded-full border border-gray-200 shadow-sm mr-2"
                    style={{ backgroundColor: item.primary_color }}
                  ></div>
                  <span className="text-gray-700">{item.primary_color}</span>
                </div>
              </div>
              
              {item.secondary_color && (
                <div>
                  <h3 className="text-sm text-gray-500 mb-1">辅助色调</h3>
                  <div className="flex items-center">
                    <div
                      className="w-6 h-6 rounded-full border border-gray-200 shadow-sm mr-2"
                      style={{ backgroundColor: item.secondary_color }}
                    ></div>
                    <span className="text-gray-700">{item.secondary_color}</span>
                  </div>
                </div>
              )}
              
              <div>
                <h3 className="text-sm text-gray-500 mb-1">风格</h3>
                <span className="inline-block bg-gray-100 text-gray-700 px-3 py-1 rounded-md">
                  {item.style}
                </span>
              </div>
              
              <div>
                <h3 className="text-sm text-gray-500 mb-1">厚度</h3>
                <span className="inline-block bg-gray-100 text-gray-700 px-3 py-1 rounded-md">
                  {item.thickness}
                </span>
              </div>
            </div>

            <div>
              <h3 className="text-sm text-gray-500 mb-2">适宜季节</h3>
              <div className="flex flex-wrap gap-2">
                {item.season.map(s => (
                  <span key={s} className="bg-indigo-50 text-indigo-600 border border-indigo-100 px-3 py-1 rounded-md">
                    {s}
                  </span>
                ))}
              </div>
            </div>

            <div>
              <h3 className="text-sm text-gray-500 mb-1">适宜温度</h3>
              <div className="flex items-center text-gray-700 font-medium">
                <svg className="w-5 h-5 mr-1 text-orange-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                </svg>
                {item.temp_min}°C ~ {item.temp_max}°C
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ClothingDetailPage;
