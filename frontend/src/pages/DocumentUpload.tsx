import { useState, useRef, useEffect } from 'react'
import { CreditCard, FileText, CheckCircle, Loader } from 'lucide-react'
import { uploadDocument, getDocumentStatus } from '../services/api'
import { useNavigate } from 'react-router-dom'

interface DocStatus {
    id: 'income_certificate' | 'aadhaar'
    name: string
    icon: typeof CreditCard
    status: 'not_uploaded' | 'processing' | 'verified' | 'failed'
}

export default function DocumentUpload() {
    const navigate = useNavigate()
    const [isDragging, setIsDragging] = useState(false)
    const [isUploading, setIsUploading] = useState(false)
    const [selectedDocType, setSelectedDocType] = useState<DocStatus['id'] | undefined>()
    const [docs, setDocs] = useState<DocStatus[]>([
        { id: 'income_certificate', name: 'Income Certificate', icon: FileText, status: 'not_uploaded' },
        { id: 'aadhaar', name: 'Aadhaar Card', icon: CreditCard, status: 'not_uploaded' },
    ])
    const fileRef = useRef<HTMLInputElement>(null)

    const fetchStatus = async () => {
        try {
            const status = await getDocumentStatus()
            setDocs([
                { id: 'income_certificate', name: 'Income Certificate', icon: FileText, status: status.income_certificate as any },
                { id: 'aadhaar', name: 'Aadhaar Card', icon: CreditCard, status: status.aadhaar as any },
            ])
        } catch (err) {
            console.error("Failed to fetch document status", err)
        }
    }

    useEffect(() => {
        fetchStatus()
    }, [])

    const handleFile = async (file: File, explicitType?: string) => {
        if (!explicitType) return // Strictly enforce explicit uploads only

        console.log("Uploading:", explicitType, file)
        setIsUploading(true)
        try {
            const res = await uploadDocument(file, explicitType)
            console.log("API response:", res)

            if (res.status === 'success') {
                setDocs(prev => prev.map(d => d.id === explicitType ? { ...d, status: 'verified' } : d))
            } else {
                throw new Error("Upload failed")
            }

            // Refetch real document status
            await fetchStatus()
        } catch (error) {
            console.error("Document upload failed", error)
            // Fetch status again to see if it registered as failed
            await fetchStatus()
        } finally {
            setIsUploading(false)
        }
    }

    const handleDrop = (e: React.DragEvent) => {
        e.preventDefault()
        e.stopPropagation()
        setIsDragging(false)
        const file = e.dataTransfer.files[0]
        if (file) handleFile(file)
    }

    const handleSubmitAll = () => {
        // Just go back to the previous page where they came from (Apply page or Results)
        navigate(-1)
    }

    const statusBadge = (docId: DocStatus['id'], status: DocStatus['status']) => {
        if (status === 'verified') return <span className="badge-green"><CheckCircle size={12} /> Verified via AI</span>
        if (status === 'failed') return <span className="text-xs font-semibold px-2 py-0.5 rounded-full bg-red-100 text-red-700">Upload failed – try again</span>
        if (status === 'processing') return <span className="badge-yellow"><Loader size={12} className="animate-spin" /> Processing</span>
        return (
            <button
                onClick={(e) => {
                    e.stopPropagation()
                    setSelectedDocType(docId)
                    fileRef.current?.click()
                }}
                className="text-xs font-semibold text-blue-600 hover:text-blue-800 transition"
            >
                Upload
            </button>
        )
    }

    return (
        <div className="max-w-3xl mx-auto px-6 py-10">
            {/* Page header */}
            <div className="mb-6">
                <h1 className="text-2xl font-bold text-gray-900">Upload Documents</h1>
                <p className="text-sm text-gray-500 mt-1">Please upload the required documents for your application.</p>
            </div>

            <div className="card flex flex-col gap-6">
                {/* Drop zone */}
                <div
                    onDragOver={(e) => { e.preventDefault(); setIsDragging(true) }}
                    onDragLeave={() => setIsDragging(false)}
                    onDrop={handleDrop}
                    onClick={() => {
                        setSelectedDocType(undefined)
                        fileRef.current?.click()
                    }}
                    className={`border-2 border-dashed rounded-xl p-10 text-center cursor-pointer transition-colors ${isDragging
                        ? 'border-blue-500 bg-blue-50'
                        : 'border-blue-300 hover:border-blue-500 hover:bg-blue-50/50'
                        }`}
                >
                    <input
                        ref={fileRef}
                        type="file"
                        className="hidden"
                        accept="image/*,.pdf"
                        onChange={(e) => {
                            const file = e.target.files?.[0]
                            if (file) handleFile(file, selectedDocType)
                            e.target.value = ''
                            setSelectedDocType(undefined)
                        }}
                    />

                    {isUploading ? (
                        <div className="flex flex-col items-center gap-2">
                            <Loader size={32} className="text-blue-500 animate-spin" />
                            <p className="text-sm text-gray-500">Uploading & Analyzing by AI...</p>
                        </div>
                    ) : (
                        <>
                            <p className="text-sm font-medium text-gray-600 mb-1">Upload Documents Individually</p>
                            <p className="text-xs text-gray-400 mb-6">Click "Upload" next to each required document below</p>

                            <div className="flex justify-center gap-8">
                                {/* Aadhaar Card icon */}
                                <div className="flex flex-col items-center gap-2">
                                    <div className="w-16 h-12 border-2 border-gray-300 rounded-lg flex items-center justify-center bg-white shadow-sm">
                                        <CreditCard size={22} className="text-blue-500" />
                                    </div>
                                    <span className="text-xs text-gray-500">Aadhaar Card</span>
                                </div>
                                {/* Income Certificate icon */}
                                <div className="flex flex-col items-center gap-2">
                                    <div className="w-16 h-12 border-2 border-gray-300 rounded-lg flex items-center justify-center bg-white shadow-sm">
                                        <FileText size={22} className="text-blue-500" />
                                    </div>
                                    <span className="text-xs text-gray-500">Income Certificate</span>
                                </div>
                            </div>
                        </>
                    )}
                </div>

                {/* Document status list */}
                <div className="flex flex-col gap-3">
                    {docs.map((doc) => {
                        const Icon = doc.icon
                        return (
                            <div
                                key={doc.id}
                                className="flex items-center justify-between py-3 px-4 border border-gray-100 rounded-lg bg-gray-50"
                            >
                                <div className="flex items-center gap-3">
                                    <Icon size={18} className={doc.status === 'verified' ? 'text-green-500' : 'text-gray-400'} />
                                    <span className="text-sm font-medium text-gray-700">{doc.name}</span>
                                </div>
                                {statusBadge(doc.id, doc.status)}
                            </div>
                        )
                    })}
                </div>

                {/* Submit */}
                <div className="flex justify-center">
                    <button
                        onClick={handleSubmitAll}
                        className="bg-blue-600 hover:bg-blue-700 text-white font-semibold px-8 py-2.5 rounded-lg transition shadow-sm"
                    >
                        Go Back
                    </button>
                </div>
            </div>

            {/* Footer links */}
            <div className="mt-8 flex flex-col sm:flex-row items-center justify-between text-xs text-gray-400 gap-2">
                <div className="flex gap-4">
                    <a href="#" className="hover:text-blue-600">Quick Links</a>
                    <a href="#" className="hover:text-blue-600">Site map</a>
                    <a href="#" className="hover:text-blue-600">Contact Us</a>
                </div>
                <div className="flex gap-4">
                    <a href="#" className="hover:text-blue-600">Privacy Policy</a>
                    <span>Government of India</span>
                </div>
            </div>
        </div>
    )
}
