import { Upload as UploadIcon } from 'lucide-react';

export default function UploadPage() {
  return (
    <div className="max-w-2xl mx-auto space-y-8">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">上传衣物</h1>
        <p className="mt-1 text-sm text-gray-500">
          上传您的衣物照片，AI 将自动分析并提取特征标签。
        </p>
      </div>

      <div className="mt-8">
        <div className="flex justify-center px-6 pt-5 pb-6 border-2 border-gray-300 border-dashed rounded-lg hover:border-brand-500 transition-colors cursor-pointer bg-white">
          <div className="space-y-1 text-center">
            <UploadIcon className="mx-auto h-12 w-12 text-gray-400" />
            <div className="flex text-sm text-gray-600 justify-center">
              <label htmlFor="file-upload" className="relative cursor-pointer bg-white rounded-md font-medium text-brand-600 hover:text-brand-500 focus-within:outline-none focus-within:ring-2 focus-within:ring-offset-2 focus-within:ring-brand-500">
                <span>点击上传</span>
                <input id="file-upload" name="file-upload" type="file" className="sr-only" accept="image/*" />
              </label>
              <p className="pl-1">或拖拽文件至此</p>
            </div>
            <p className="text-xs text-gray-500">
              PNG, JPG, JPEG 格式，最大 10MB
            </p>
          </div>
        </div>
      </div>

      <div className="flex justify-end">
        <button type="button" className="inline-flex justify-center py-2 px-4 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-brand-600 hover:bg-brand-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-brand-500">
          开始分析
        </button>
      </div>
    </div>
  );
}
