import { useLocation, useNavigate } from 'react-router-dom'
import { useEffect, useState } from 'react'
import { ArrowLeft, CheckCircle, FileText, User, ShieldCheck, XCircle, Loader2 } from 'lucide-react'
import { submitApplication as apiSubmitApplication, getDocumentStatus, type DocumentStatus } from '../services/api'

export default function SchemeApplyPage() {
    const location = useLocation()
    const navigate = useNavigate()
    const state = location.state as { scheme?: any, profile?: any } | null

    const [docStatus, setDocStatus] = useState<DocumentStatus | null>(null)

    useEffect(() => {
        getDocumentStatus().then(status => {
            console.log("Backend Document Status:", status)
            setDocStatus(status)
        }).catch(err => {
            console.error("Failed to fetch document status", err)
        })
    }, [])

    if (!state?.scheme) {
        return (
            <div className="max-w-lg mx-auto px-6 py-20 text-center">
                <h2 className="text-xl font-bold text-gray-800 mb-2">No Scheme Selected</h2>
                <button onClick={() => navigate('/eligibility')} className="btn-primary">Go Back</button>
            </div>
        )
    }

    const { scheme, profile } = state

    const handleFinalSubmit = async () => {
        try {
            const response = await apiSubmitApplication({
                scheme_id: scheme.scheme_id || 'UNKNOWN',
                scheme_name: scheme.scheme_name,
                user_profile: profile
            })

            navigate('/track', {
                state: {
                    success: true,
                    schemeName: response.scheme_name,
                    appId: response.application_id
                }
            })
        } catch (error) {
            console.error('Submission failed:', error)
            alert('Failed to submit application. Please try again.')
        }
    }

    const renderDocStatus = (status: string | undefined) => {
        if (!status || status === 'not_uploaded') {
            return (
                <div className="flex items-center gap-1.5 text-gray-400">
                    <span className="w-4 h-4 rounded-full bg-gray-200" />
                    <span className="text-xs font-medium italic text-gray-500">Not uploaded</span>
                </div>
            )
        }
        if (status === 'processing') {
            return (
                <div className="flex items-center gap-1.5 text-blue-500">
                    <Loader2 size={16} className="animate-spin" />
                    <span className="text-xs font-medium italic">Processing...</span>
                </div>
            )
        }
        if (status === 'failed') {
            return (
                <div className="flex items-center gap-1.5 text-red-500">
                    <XCircle size={16} />
                    <span className="text-xs font-medium italic">Verification Failed</span>
                </div>
            )
        }
        return (
            <div className="flex items-center gap-1.5 text-green-600">
                <CheckCircle size={16} />
                <span className="text-xs font-medium italic">Verified via AI</span>
            </div>
        )
    }

    const isAllVerified = docStatus?.aadhaar === 'verified' && docStatus?.income_certificate === 'verified'

    return (
        <div className="max-w-3xl mx-auto px-6 py-10">
            <button
                onClick={() => window.history.back()}
                className="flex items-center gap-1.5 text-sm text-gray-500 hover:text-blue-600 transition mb-6"
            >
                <ArrowLeft size={16} /> Back to Results
            </button>

            <h1 className="text-2xl font-bold text-gray-900 mb-2">Application Preview</h1>
            <p className="text-sm text-gray-500 mb-8">Please review your details before final submission for {scheme.scheme_name}.</p>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
                {/* User Details */}
                <div className="card">
                    <h2 className="text-sm font-semibold text-gray-700 mb-4 flex items-center gap-2">
                        <User size={16} className="text-blue-500" /> Applicant Information
                    </h2>
                    <div className="space-y-3">
                        <div>
                            <p className="text-xs text-gray-400 uppercase tracking-wider">Full Name</p>
                            <p className="text-sm font-medium text-gray-800">{profile?.name || 'N/A'}</p>
                        </div>
                        <div>
                            <p className="text-xs text-gray-400 uppercase tracking-wider">Income Group</p>
                            <p className="text-sm font-medium text-gray-800">₹{profile?.income?.toLocaleString() || '0'} / year</p>
                        </div>
                        <div>
                            <p className="text-xs text-gray-400 uppercase tracking-wider">State</p>
                            <p className="text-sm font-medium text-gray-800">{profile?.state || 'N/A'}</p>
                        </div>
                    </div>
                </div>

                {/* Scheme Summary */}
                <div className="card bg-blue-50 border-blue-100">
                    <h2 className="text-sm font-semibold text-blue-800 mb-4 flex items-center gap-2">
                        <ShieldCheck size={16} className="text-blue-600" /> Selected Scheme
                    </h2>
                    <div className="space-y-3">
                        <div>
                            <p className="text-xs text-blue-400 uppercase tracking-wider">Scheme Name</p>
                            <p className="text-sm font-bold text-blue-900">{scheme.scheme_name}</p>
                        </div>
                        <div>
                            <p className="text-xs text-blue-400 uppercase tracking-wider">Status</p>
                            <span className="badge-green text-[10px]">Pre-Verified</span>
                        </div>
                    </div>
                </div>
            </div>

            {/* Documents Section */}
            <div className="card mb-8">
                <div className="flex items-center justify-between mb-4">
                    <h2 className="text-sm font-semibold text-gray-700 flex items-center gap-2">
                        <FileText size={16} className="text-blue-500" /> Documents for Verification
                    </h2>
                    <button
                        onClick={() => navigate('/upload-document')}
                        className="text-xs text-blue-600 font-semibold hover:text-blue-800"
                    >
                        Upload Documents
                    </button>
                </div>
                <div className="flex items-center justify-between border-b pb-3 mb-3">
                    <div className="flex items-center gap-3">
                        <FileText size={16} className="text-gray-500" />
                        <span className="text-sm text-gray-700">Aadhaar Card (Extracted)</span>
                    </div>
                    {renderDocStatus(docStatus?.aadhaar)}
                </div>
                <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                        <FileText size={16} className="text-gray-500" />
                        <span className="text-sm text-gray-700">Income Certificate</span>
                    </div>
                    {renderDocStatus(docStatus?.income_certificate)}
                </div>
            </div>

            {/* Final CTA */}
            <div className="flex flex-col items-center gap-4">
                <button
                    onClick={handleFinalSubmit}
                    disabled={!isAllVerified}
                    className={`w-full sm:w-64 font-bold py-3 rounded-lg shadow-lg transition transform ${isAllVerified
                            ? 'bg-green-600 hover:bg-green-700 text-white hover:scale-[1.02]'
                            : 'bg-gray-300 text-gray-500 cursor-not-allowed'
                        }`}
                >
                    Confirm & Submit Application
                </button>
                {!isAllVerified && (
                    <p className="text-sm text-red-500">
                        Please upload and verify both documents to submit the application.
                    </p>
                )}
                <p className="text-[10px] text-gray-400 text-center max-w-sm">
                    By submitting, you agree that the information provided is correct to the best of your knowledge under the Digital India Citizen Act.
                </p>
            </div>
        </div>
    )
}
