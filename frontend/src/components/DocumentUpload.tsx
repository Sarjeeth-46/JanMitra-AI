import { useState, useRef } from 'react'
import { Upload, FileText, Loader2, CheckCircle, Sparkles } from 'lucide-react'
import { uploadDocument } from '../services/api'
import toast from 'react-hot-toast'
import type { UserProfile } from '../types'

interface DocumentUploadProps {
  onDataExtracted: (extractedData: Partial<UserProfile>) => void
}

const DocumentUpload = ({ onDataExtracted }: DocumentUploadProps) => {
  const [isUploading, setIsUploading] = useState(false)
  const [uploadSuccess, setUploadSuccess] = useState(false)
  const [fileName, setFileName] = useState<string | null>(null)
  const fileInputRef = useRef<HTMLInputElement>(null)

  const handleFileSelect = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (!file) return

    setFileName(file.name)
    setIsUploading(true)
    setUploadSuccess(false)

    try {
      toast.loading('Analyzing document securely...', { id: 'ocr' })

      // Upload to backend which now uses AWS Textract
      const response = await uploadDocument(file)

      console.log("AWS Textract Extracted Fields:", response.extracted_fields)

      if (response.extracted_fields && Object.keys(response.extracted_fields).length > 0) {
        toast.success('Document analyzed successfully', { id: 'ocr' })
        setUploadSuccess(true)
        const fields = response.extracted_fields
        onDataExtracted({
          ...fields,
          income: typeof fields.income === 'string' ? parseFloat(fields.income.replace(/,/g, '')) || 0 : fields.income as number | undefined,
        } as Partial<UserProfile>)
      } else {
        toast.success('Document uploaded, but no readable fields found', { id: 'ocr' })
      }

    } catch (error) {
      console.error('Error processing document via Textract:', error)
      toast.error('Failed to analyze document', { id: 'ocr' })
    } finally {
      setIsUploading(false)
    }
  }

  const handleClick = () => {
    fileInputRef.current?.click()
  }

  return (
    <div>
      <div className="flex items-center space-x-3 mb-4">
        <div className="w-8 h-8 bg-gradient-to-br from-saffron-500 to-saffron-600 rounded-lg flex items-center justify-center">
          <FileText className="w-4 h-4 text-white" />
        </div>
        <h3 className="text-lg font-bold">Document Upload</h3>
        {uploadSuccess && (
          <CheckCircle className="w-5 h-5 text-green-500" />
        )}
      </div>

      <input
        ref={fileInputRef}
        type="file"
        accept=".pdf,.jpg,.jpeg,.png"
        onChange={handleFileSelect}
        className="hidden"
      />

      <button
        onClick={handleClick}
        disabled={isUploading}
        className="w-full border-2 border-dashed border-gray-300 dark:border-gray-600 rounded-2xl p-10 hover:border-primary-500 dark:hover:border-primary-500 hover:bg-primary-50/50 dark:hover:bg-primary-900/10 transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed group"
      >
        <div className="flex flex-col items-center space-y-4">
          {isUploading ? (
            <div className="w-16 h-16 bg-gradient-to-br from-primary-500 to-primary-600 rounded-2xl flex items-center justify-center shadow-lg">
              <Loader2 className="w-8 h-8 text-white animate-spin" />
            </div>
          ) : uploadSuccess ? (
            <div className="w-16 h-16 bg-gradient-to-br from-green-500 to-green-600 rounded-2xl flex items-center justify-center shadow-lg">
              <CheckCircle className="w-8 h-8 text-white" />
            </div>
          ) : (
            <div className="w-16 h-16 bg-gradient-to-br from-gray-100 to-gray-200 dark:from-gray-700 dark:to-gray-600 rounded-2xl flex items-center justify-center shadow-lg group-hover:scale-110 transition-transform">
              <Upload className="w-8 h-8 text-gray-600 dark:text-gray-300" />
            </div>
          )}

          <div>
            <p className="text-base font-semibold text-gray-900 dark:text-white">
              {isUploading
                ? 'Processing document...'
                : uploadSuccess
                  ? 'Document processed successfully'
                  : 'Click to upload document'}
            </p>
            {fileName && (
              <p className="text-sm text-gray-600 dark:text-gray-400 mt-2 font-medium">
                {fileName}
              </p>
            )}
            {!isUploading && !uploadSuccess && (
              <p className="text-sm text-gray-500 dark:text-gray-400 mt-2">
                PDF, JPG, or PNG (Max 10MB)
              </p>
            )}
          </div>
        </div>
      </button>

      {uploadSuccess && (
        <div className="mt-4 p-4 bg-gradient-to-r from-green-50 to-green-100 dark:from-green-900/20 dark:to-green-800/20 rounded-xl border-2 border-green-200 dark:border-green-800">
          <p className="text-sm font-semibold text-green-700 dark:text-green-300 flex items-center space-x-2">
            <Sparkles className="w-4 h-4" />
            <span>Data extracted and auto-filled in the form</span>
          </p>
        </div>
      )}
    </div>
  )
}

export default DocumentUpload
