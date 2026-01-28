import React, { useState, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Sparkles, FileText, FileSpreadsheet, Presentation, 
  MessageSquare, Download, Zap, Clock, Shield,
  Upload, CheckCircle, AlertCircle, Loader2, X,
  RefreshCw, Eye, Edit3
} from 'lucide-react';

// API URL
const API_URL = import.meta.env.VITE_API_URL || '';

// Tab ma'lumotlari
const tabs = [
  { id: 'excel', label: 'Excel', icon: FileSpreadsheet, active: true },
  { id: 'autofill', label: 'Auto-Fill', icon: RefreshCw, active: true },
  { id: 'doc', label: 'Doc', icon: FileText, active: false },
  { id: 'pdf', label: 'PDF', icon: FileText, active: false },
  { id: 'slides', label: 'Slaydlar', icon: Presentation, active: false },
  { id: 'chat', label: 'Chat', icon: MessageSquare, active: false },
];

// Feature badges
const features = [
  { icon: Zap, text: 'Cheksiz foydalanish' },
  { icon: Sparkles, text: '1-Click yaratish' },
  { icon: Download, text: 'Bepul yuklab olish' },
  { icon: Shield, text: "Ro'yxatdan o'tish shart emas" },
];

// Coming Soon komponenti
const ComingSoon = () => (
  <motion.div 
    initial={{ opacity: 0 }}
    animate={{ opacity: 1 }}
    className="coming-soon-overlay"
  >
    <div className="text-center">
      <div className="w-16 h-16 bg-gray-100 rounded-2xl flex items-center justify-center mx-auto mb-4">
        <Clock className="w-8 h-8 text-gray-400" />
      </div>
      <h3 className="text-xl font-semibold text-gray-800 mb-2">Tez kunda</h3>
      <p className="text-gray-500">Bu xususiyat ustida ishlamoqdamiz</p>
    </div>
  </motion.div>
);

// Excel Tab komponenti
const ExcelTab = () => {
  const [prompt, setPrompt] = useState('');
  const [loading, setLoading] = useState(false);
  const [preview, setPreview] = useState(null);
  const [error, setError] = useState(null);

  const handleGenerate = async () => {
    if (!prompt.trim()) return;
    
    setLoading(true);
    setError(null);
    
    try {
      // Preview olish
      const previewRes = await fetch(`${API_URL}/api/excel/preview`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ prompt })
      });
      
      let previewData = null;
      if (previewRes.ok) {
        previewData = await previewRes.json();
        setPreview(previewData);
      }
      
      // Excel yuklab olish
      const response = await fetch(`${API_URL}/api/excel/generate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ prompt })
      });
      
      if (response.ok) {
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `${previewData?.title || 'hujjat'}.xlsx`;
        document.body.appendChild(a);
        a.click();
        a.remove();
        window.URL.revokeObjectURL(url);
      } else {
        const errData = await response.json().catch(() => ({}));
        throw new Error(errData.detail || 'Xatolik yuz berdi');
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const examplePrompts = [
    "Kichik biznes uchun oylik moliyaviy hisobot",
    "IT kompaniya xodimlari ro'yxati va maoshlari",
    "Talaba uchun haftalik dars jadvali"
  ];

  return (
    <div className="space-y-6">
      {/* Input section */}
      <div className="relative">
        <textarea
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
          placeholder="Qanday Excel jadval kerak? Masalan: Restoran uchun haftalik tushum hisoboti, formulalar bilan..."
          className="input-field min-h-[140px] pr-4 text-base"
          disabled={loading}
        />
        
        {/* Example chips */}
        <div className="flex flex-wrap gap-2 mt-3">
          {examplePrompts.map((example, i) => (
            <button
              key={i}
              onClick={() => setPrompt(example)}
              className="text-xs px-3 py-1.5 bg-gray-50 hover:bg-gray-100 
                       text-gray-600 rounded-lg transition-colors border border-gray-100"
            >
              {example.substring(0, 45)}...
            </button>
          ))}
        </div>
      </div>

      {/* Action buttons */}
      <button
        onClick={handleGenerate}
        disabled={loading || !prompt.trim()}
        className="btn-primary w-full disabled:opacity-50 disabled:cursor-not-allowed"
      >
        {loading ? (
          <>
            <Loader2 className="w-5 h-5 animate-spin" />
            Yaratilmoqda...
          </>
        ) : (
          <>
            <Sparkles className="w-5 h-5" />
            Yaratish
          </>
        )}
      </button>

      {/* Error */}
      {error && (
        <motion.div 
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          className="p-4 bg-red-50 border border-red-100 rounded-xl flex items-center gap-3"
        >
          <AlertCircle className="w-5 h-5 text-red-500" />
          <span className="text-red-700">{error}</span>
        </motion.div>
      )}

      {/* Preview */}
      {preview && (
        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="p-6 bg-green-50 border border-green-100 rounded-xl"
        >
          <div className="flex items-center gap-3 mb-4">
            <CheckCircle className="w-6 h-6 text-green-600" />
            <div className="flex-1">
              <h4 className="font-semibold text-green-800">{preview.title}.xlsx</h4>
              <p className="text-sm text-green-600">Muvaffaqiyatli yaratildi va yuklab olindi!</p>
            </div>
          </div>
          
          {preview.sheets?.[0] && (
            <div className="bg-white rounded-lg p-4 border border-green-200 overflow-x-auto">
              <table className="min-w-full text-sm">
                <thead>
                  <tr>
                    {preview.sheets[0].headers?.slice(0, 6).map((h, i) => (
                      <th key={i} className="px-3 py-2 bg-gray-100 text-left font-medium text-gray-700">
                        {h}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {preview.sheets[0].data?.slice(0, 4).map((row, i) => (
                    <tr key={i}>
                      {row.slice(0, 6).map((cell, j) => (
                        <td key={j} className="px-3 py-2 border-t border-gray-100">
                          {typeof cell === 'string' && cell.startsWith('=') 
                            ? <span className="text-blue-600 text-xs font-mono">{cell}</span>
                            : cell}
                        </td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </motion.div>
      )}
    </div>
  );
};

// Auto-Fill Tab komponenti - YANGILANGAN
const AutoFillTab = () => {
  const [file, setFile] = useState(null);
  const [instruction, setInstruction] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [dragActive, setDragActive] = useState(false);

  const handleDrag = useCallback((e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  }, []);

  const handleDrop = useCallback((e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      setFile(e.dataTransfer.files[0]);
      setResult(null);
      setError(null);
    }
  }, []);

  const handleFileChange = (e) => {
    if (e.target.files[0]) {
      setFile(e.target.files[0]);
      setResult(null);
      setError(null);
    }
  };

  const handleProcess = async () => {
    if (!file || !instruction.trim()) {
      setError("Fayl va ko'rsatma kiriting");
      return;
    }
    
    setLoading(true);
    setError(null);
    
    try {
      const formData = new FormData();
      formData.append('file', file);
      formData.append('instruction', instruction);
      
      const response = await fetch(`${API_URL}/api/autofill/process`, {
        method: 'POST',
        body: formData
      });
      
      if (response.ok) {
        const blob = await response.blob();
        const contentDisposition = response.headers.get('content-disposition');
        let filename = 'tahrirlangan_hujjat';
        
        if (contentDisposition) {
          const match = contentDisposition.match(/filename[^;=\n]*=((['"]).*?\2|[^;\n]*)/);
          if (match) {
            filename = match[1].replace(/['"]/g, '');
          }
        }
        
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        a.remove();
        window.URL.revokeObjectURL(url);
        
        setResult({ success: true, filename });
      } else {
        const errData = await response.json().catch(() => ({}));
        throw new Error(errData.detail || 'Xatolik yuz berdi');
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const resetAll = () => {
    setFile(null);
    setInstruction('');
    setResult(null);
    setError(null);
  };

  const exampleInstructions = [
    "Shartnoma raqamini 01-25/199B ga o'zgartir va sanalarni bugungi sanaga",
    "Mijoz ismini Karimov Jasur ga o'zgartir",
    "Avtomobil narxini 250 000 000 so'm ga o'zgartir"
  ];

  return (
    <div className="space-y-6">
      {/* File Upload */}
      <div
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
        className={`file-upload-zone ${dragActive ? 'file-upload-zone-active' : ''}`}
      >
        <input
          type="file"
          onChange={handleFileChange}
          accept=".pdf,.docx,.txt"
          className="hidden"
          id="file-upload"
        />
        <label htmlFor="file-upload" className="cursor-pointer block text-center">
          {file ? (
            <div className="flex items-center justify-center gap-3">
              <FileText className="w-8 h-8 text-primary-500" />
              <div className="text-left">
                <p className="font-medium text-gray-800">{file.name}</p>
                <p className="text-sm text-gray-500">{(file.size / 1024).toFixed(1)} KB</p>
              </div>
              <button 
                onClick={(e) => { e.preventDefault(); resetAll(); }}
                className="p-1 hover:bg-gray-100 rounded"
              >
                <X className="w-5 h-5 text-gray-400" />
              </button>
            </div>
          ) : (
            <>
              <Upload className="w-10 h-10 text-gray-400 mx-auto mb-3" />
              <p className="text-gray-600 font-medium">Faylni shu yerga tashlang</p>
              <p className="text-gray-400 text-sm mt-1">yoki bosib tanlang</p>
              <p className="text-xs text-gray-400 mt-2">PDF, Word, TXT</p>
            </>
          )}
        </label>
      </div>

      {/* Instruction Input */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Ko'rsatma
        </label>
        <textarea
          value={instruction}
          onChange={(e) => setInstruction(e.target.value)}
          placeholder="Hujjatda qanday o'zgarishlar kerak? Masalan:
- Shartnoma raqamini 01-25/199B ga o'zgartir
- Mijoz ismi - Karimov Jasur Anvarovich
- Sanalarni bugungi sanaga o'zgartir
- Avtomobil narxini 250 000 000 so'm ga o'zgartir"
          className="input-field min-h-[150px] text-base"
          disabled={loading}
        />
        
        {/* Example chips */}
        <div className="flex flex-wrap gap-2 mt-3">
          {exampleInstructions.map((example, i) => (
            <button
              key={i}
              onClick={() => setInstruction(example)}
              className="text-xs px-3 py-1.5 bg-gray-50 hover:bg-gray-100 
                       text-gray-600 rounded-lg transition-colors border border-gray-100"
            >
              {example.substring(0, 40)}...
            </button>
          ))}
        </div>
      </div>

      {/* Action Button */}
      <button
        onClick={handleProcess}
        disabled={loading || !file || !instruction.trim()}
        className="btn-primary w-full disabled:opacity-50 disabled:cursor-not-allowed"
      >
        {loading ? (
          <>
            <Loader2 className="w-5 h-5 animate-spin" />
            Tahrirlanmoqda...
          </>
        ) : (
          <>
            <Edit3 className="w-5 h-5" />
            Tasdiqlash va yuklab olish
          </>
        )}
      </button>

      {/* Error */}
      {error && (
        <motion.div 
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          className="p-4 bg-red-50 border border-red-100 rounded-xl flex items-center gap-3"
        >
          <AlertCircle className="w-5 h-5 text-red-500 flex-shrink-0" />
          <span className="text-red-700">{error}</span>
        </motion.div>
      )}

      {/* Success Result */}
      {result && result.success && (
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          className="p-5 bg-green-50 border border-green-200 rounded-xl"
        >
          <div className="flex items-center gap-3">
            <CheckCircle className="w-8 h-8 text-green-600" />
            <div>
              <p className="font-semibold text-green-800 text-lg">
                Muvaffaqiyatli!
              </p>
              <p className="text-green-600">
                Hujjat tahrirlandi va yuklab olindi: {result.filename}
              </p>
            </div>
          </div>
          <button
            onClick={resetAll}
            className="mt-4 text-sm text-green-700 hover:text-green-800 underline"
          >
            Yangi hujjat tahrirlash
          </button>
        </motion.div>
      )}
    </div>
  );
};

// Asosiy App komponenti
export default function App() {
  const [activeTab, setActiveTab] = useState('excel');

  const renderTabContent = () => {
    switch (activeTab) {
      case 'excel':
        return <ExcelTab />;
      case 'autofill':
        return <AutoFillTab />;
      default:
        return (
          <div className="relative min-h-[300px]">
            <ComingSoon />
          </div>
        );
    }
  };

  return (
    <div className="min-h-screen bg-dots">
      {/* Decorative elements */}
      <div className="fixed top-20 right-20 w-64 h-64 bg-primary-200/30 rounded-full blur-3xl pointer-events-none" />
      <div className="fixed bottom-20 left-20 w-96 h-96 bg-accent/10 rounded-full blur-3xl pointer-events-none" />
      
      <div className="max-w-5xl mx-auto px-4 py-12 relative">
        {/* Header */}
        <motion.header 
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center mb-12"
        >
          {/* Feature badges */}
          <div className="flex flex-wrap justify-center gap-3 mb-8">
            {features.map((f, i) => (
              <motion.div
                key={i}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: i * 0.1 }}
                className="feature-badge"
              >
                <f.icon className="w-4 h-4 text-gray-500" />
                {f.text}
              </motion.div>
            ))}
          </div>

          {/* Title */}
          <h1 className="text-4xl md:text-5xl font-display font-bold text-gray-900 mb-4">
            AI Hujjat Yaratuvchi
          </h1>
          <h2 className="text-2xl md:text-3xl font-display gradient-text font-semibold mb-6">
            Excel & Auto-Fill Pro
          </h2>
          <p className="text-gray-500 max-w-2xl mx-auto text-lg">
            Sun'iy intellekt yordamida professional hujjatlar yarating. 
            Formulalar, jadvallar va avtomatik to'ldirish.
            <span className="text-primary-600 font-medium"> Bepul sinab ko'ring!</span>
          </p>
        </motion.header>

        {/* Main Card */}
        <motion.main
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="glass-card rounded-3xl p-8"
        >
          {/* Tabs */}
          <div className="flex flex-wrap justify-center gap-2 mb-8 p-1.5 bg-gray-50/80 rounded-2xl">
            {tabs.map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`tab-item ${
                  activeTab === tab.id ? 'tab-item-active' : 'tab-item-inactive'
                }`}
              >
                <tab.icon className="w-4 h-4" />
                {tab.label}
                {!tab.active && (
                  <span className="text-[10px] px-1.5 py-0.5 bg-gray-200 text-gray-500 rounded-full">
                    soon
                  </span>
                )}
              </button>
            ))}
          </div>

          {/* Tab Content */}
          <AnimatePresence mode="wait">
            <motion.div
              key={activeTab}
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -20 }}
              transition={{ duration: 0.2 }}
            >
              {renderTabContent()}
            </motion.div>
          </AnimatePresence>
        </motion.main>

        {/* Footer info */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.4 }}
          className="grid md:grid-cols-3 gap-6 mt-12"
        >
          {[
            { 
              icon: MessageSquare, 
              title: "Hujjatingizni tasvirlang", 
              desc: "Oddiy so'zlar bilan yozing" 
            },
            { 
              icon: Sparkles, 
              title: "AI yaratadi", 
              desc: "Formulalar va formatlar bilan" 
            },
            { 
              icon: Download, 
              title: "Yuklab oling", 
              desc: "Excel, PDF, Word formatida" 
            },
          ].map((item, i) => (
            <div key={i} className="flex items-start gap-4 p-4">
              <div className="w-12 h-12 bg-gray-50 rounded-xl flex items-center justify-center flex-shrink-0">
                <item.icon className="w-6 h-6 text-gray-600" />
              </div>
              <div>
                <h4 className="font-semibold text-gray-800">{item.title}</h4>
                <p className="text-sm text-gray-500">{item.desc}</p>
              </div>
            </div>
          ))}
        </motion.div>

        {/* Credits */}
        <p className="text-center text-gray-400 text-sm mt-8">
          AI Doc Pro • Professional hujjatlar yaratish platformasi
        </p>
      </div>
    </div>
  );
}
