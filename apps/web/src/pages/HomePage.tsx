import { Link } from 'react-router-dom';
import { Shirt, Upload, Sparkles } from 'lucide-react';

export default function HomePage() {
  return (
    <div className="space-y-12">
      <div className="text-center py-16 px-4 sm:px-6 lg:px-8 bg-brand-50 rounded-3xl">
        <h1 className="text-4xl font-extrabold text-gray-900 sm:text-5xl sm:tracking-tight lg:text-6xl">
          衣见 AI
        </h1>
        <p className="max-w-xl mt-5 mx-auto text-xl text-gray-500">
          您的智能数字衣橱与穿搭助手。一键上传，AI 自动分类；智能推荐，每日穿搭不发愁。
        </p>
      </div>

      <div className="grid grid-cols-1 gap-8 sm:grid-cols-3">
        <Link to="/wardrobe" className="block p-6 bg-white rounded-2xl shadow-sm hover:shadow-md transition-shadow">
          <Shirt className="h-10 w-10 text-brand-500 mb-4" />
          <h3 className="text-lg font-medium text-gray-900">数字衣橱</h3>
          <p className="mt-2 text-sm text-gray-500">浏览和管理您的所有衣物。</p>
        </Link>

        <Link to="/upload" className="block p-6 bg-white rounded-2xl shadow-sm hover:shadow-md transition-shadow">
          <Upload className="h-10 w-10 text-brand-500 mb-4" />
          <h3 className="text-lg font-medium text-gray-900">上传衣物</h3>
          <p className="mt-2 text-sm text-gray-500">拍照上传，AI 自动识别标签。</p>
        </Link>

        <Link to="/recommend" className="block p-6 bg-white rounded-2xl shadow-sm hover:shadow-md transition-shadow">
          <Sparkles className="h-10 w-10 text-brand-500 mb-4" />
          <h3 className="text-lg font-medium text-gray-900">智能推荐</h3>
          <p className="mt-2 text-sm text-gray-500">根据天气和场景，为您生成搭配方案。</p>
        </Link>
      </div>
    </div>
  );
}
