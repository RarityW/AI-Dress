import { Link } from 'react-router-dom';
import { Plus } from 'lucide-react';

export default function WardrobePage() {
  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold text-gray-900">我的衣橱</h1>
        <Link to="/upload" className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-brand-600 hover:bg-brand-700">
          <Plus className="-ml-1 mr-2 h-5 w-5" />
          添加衣物
        </Link>
      </div>

      <div className="bg-white rounded-lg shadow-sm border border-gray-100 p-12 text-center">
        <div className="mx-auto h-24 w-24 text-gray-300 bg-gray-50 rounded-full flex items-center justify-center mb-4">
          <span className="text-3xl">👗</span>
        </div>
        <h3 className="text-lg font-medium text-gray-900">暂无衣物</h3>
        <p className="mt-2 text-sm text-gray-500">您的衣橱空空如也，快去上传第一件衣物吧！</p>
        <div className="mt-6">
          <Link to="/upload" className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-brand-700 bg-brand-100 hover:bg-brand-200">
            去上传
          </Link>
        </div>
      </div>
    </div>
  );
}
