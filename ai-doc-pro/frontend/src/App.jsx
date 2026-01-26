import React, { useState, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Sparkles, FileText, FileSpreadsheet, Presentation, 
  Mic, MessageSquare, Download, Zap, Clock, Shield,
  Upload, CheckCircle, AlertCircle, Loader2, X,
  RefreshCw, Eye, Send, Paperclip, ArrowRight
} from 'lucide-react';

// Tab ma'lumotlari
const tabs = [
  { id: 'doc', label: 'Doc', icon: FileText, active: false },
  { id: 'pdf', label: 'PDF', icon: FileText, active: false },
  { id: 'slides', label: 'Slaydlar', icon: Presentation, active: false },
  { id: 'excel', label: 'Excel', icon: FileSpreadsheet, active: true },
  { id: 'autofill', label: 'Auto-Fill', icon: RefreshCw, active: true },
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
      const previewRes = await fetch('/api/excel/preview', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ prompt })
      });
      
      if (previewRes.ok) {
        const data = await previewRes.json();
        setPreview(data.structure);
      }
      
      // Excel yuklab olish
      const response = await fetch('/api/excel/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ prompt })
      });
      
      if (response.ok) {
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `${preview?.title || 'hujjat'}.xlsx`;
        document.body.appendChild(a);
        a.click();
        a.remove();
        window.URL.revokeObjectURL(url);
      } else {
        throw new Error('Xatolik yuz berdi');
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const examplePrompts = [
    "12 oylik moliyaviy prognoz - daromad va xarajatlar bilan",
    "Kafe uchun oylik byudjet rejasi",
    "Mahsulotlar ro'yxati - narx va miqdor bilan"
  ];

  return (
    <div className="space-y-6">
      {/* Input section */}
      <div className="relative">
        <textarea
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
          placeholder="Excel hujjatingizni tasvirlang. Masalan: 12 oylik moliyaviy prognoz yarating..."
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
              {example.substring(0, 40)}...
            </button>
          ))}
        </div>
      </div>

      {/* Action buttons */}
      <div className="flex items-center gap-4">
        <button
          onClick={handleGenerate}
          disabled={loading || !prompt.trim()}
          className="btn-primary flex-1 disabled:opacity-50 disabled:cursor-not-allowed"
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
      </div>

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
            <div>
              <h4 className="font-semibold text-green-800">{preview.title}.xlsx</h4>
              <p className="text-sm text-green-600">Muvaffaqiyatli yaratildi va yuklab olindi!</p>
            </div>
          </div>
          
          {preview.sheets?.[0] && (
            <div className="bg-white rounded-lg p-4 border border-green-200 overflow-x-auto">
              <table className="min-w-full text-sm">
                <thead>
                  <tr>
                    {preview.sheets[0].headers?.slice(0, 5).map((h, i) => (
                      <th key={i} className="px-3 py-2 bg-gray-100 text-left font-medium text-gray-700">
                        {h}
                      </th>
                    ))}
                    {preview.sheets[0].headers?.length > 5 && (
                      <th className="px-3 py-2 bg-gray-100 text-gray-500">...</th>
                    )}
                  </tr>
                </thead>
                <tbody>
                  {preview.sheets[0].data?.slice(0, 3).map((row, i) => (
                    <tr key={i}>
                      {row.slice(0, 5).map((cell, j) => (
                        <td key={j} className="px-3 py-2 border-t border-gray-100">
                          {typeof cell === 'string' && cell.startsWith('=') 
                            ? <span className="text-blue-600 text-xs">{cell}</span>
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

// Auto-Fill Tab komponenti
const AutoFillTab = () => {
  const [file, setFile] = useState(null);
  const [text, setText] = useState('');
  const [instruction, setInstruction] = useState('');
  const [replacements, setReplacements] = useState([]);
  const [loading, setLoading] = useState(false);
  const [analyzing, setAnalyzing] = useState(false);
  const [result, setResult] = useState(null);
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
      handleFile(e.dataTransfer.files[0]);
    }
  }, []);

  const handleFile = async (f) => {
    setFile(f);
    setReplacements([]);
    setResult(null);
    
    // Matnni ajratib olish (local preview uchun)
    if (f.type === 'text/plain') {
      const reader = new FileReader();
      reader.onload = (e) => setText(e.target.result);
      reader.readAsText(f);
    } else {
      setText('Fayl yuklandi. Tahlil qilish uchun ko\'rsatma kiriting.');
    }
  };

  const handleAnalyze = async () => {
    if (!file || !instruction.trim()) return;
    
    setAnalyzing(true);
    
    try {
      const formData = new FormData();
      formData.append('file', file);
      formData.append('instruction', instruction);
      
      const response = await fetch('/api/autofill/analyze', {
        method: 'POST',
        body: formData
      });
      
      if (response.ok) {
        const data = await response.json();
        setText(data.text);
        setReplacements(data.replacements);
      }
    } catch (err) {
      console.error(err);
    } finally {
      setAnalyzing(false);
    }
  };

  const handleApply = async () => {
    if (!file || replacements.length === 0) return;
    
    setLoading(true);
    
    try {
      const formData = new FormData();
      formData.append('file', file);
      formData.append('replacements', JSON.stringify(replacements));
      
      const response = await fetch('/api/autofill/apply', {
        method: 'POST',
        body: formData
      });
      
      if (response.ok) {
        const blob = await response.blob();
        const changes = response.headers.get('X-Changes-Count') || replacements.length;
        
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `modified_${file.name}`;
        document.body.appendChild(a);
        a.click();
        a.remove();
        window.URL.revokeObjectURL(url);
        
        setResult({ changes: parseInt(changes) });
      }
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="grid md:grid-cols-2 gap-6">
      {/* Left - Upload & Instruction */}
      <div className="space-y-4">
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
            onChange={(e) => handleFile(e.target.files[0])}
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
                  onClick={(e) => { e.preventDefault(); setFile(null); setText(''); }}
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

        {/* Instruction */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Ko'rsatma
          </label>
          <textarea
            value={instruction}
            onChange={(e) => setInstruction(e.target.value)}
            placeholder="Masalan: Sanalarni bugungi kunga o'zgartir"
            className="input-field min-h-[100px]"
          />
        </div>

        {/* Action Buttons */}
        <div className="flex gap-3">
          <button
            onClick={handleAnalyze}
            disabled={!file || !instruction.trim() || analyzing}
            className="btn-secondary flex-1 disabled:opacity-50"
          >
            {analyzing ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin" />
                Tahlil...
              </>
            ) : (
              <>
                <Eye className="w-4 h-4" />
                Tahlil qilish
              </>
            )}
          </button>
          
          <button
            onClick={handleApply}
            disabled={replacements.length === 0 || loading}
            className="btn-primary flex-1 disabled:opacity-50"
          >
            {loading ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin" />
                Qo'llanmoqda...
              </>
            ) : (
              <>
                <CheckCircle className="w-4 h-4" />
                Tasdiqlash
              </>
            )}
          </button>
        </div>
      </div>

      {/* Right - Preview & Results */}
      <div className="space-y-4">
        {/* Replacements List */}
        {replacements.length > 0 && (
          <div className="bg-white rounded-xl border border-gray-200 p-4">
            <h4 className="font-medium text-gray-800 mb-3">Topilgan o'zgarishlar</h4>
            <div className="space-y-2 max-h-[200px] overflow-y-auto">
              {replacements.map((r, i) => (
                <div key={i} className="flex items-center gap-2 text-sm p-2 bg-gray-50 rounded-lg">
                  <span className="text-xs px-2 py-0.5 bg-blue-100 text-blue-700 rounded">
                    {r.type}
                  </span>
                  <span className="diff-old">{r.old.substring(0, 30)}</span>
                  <ArrowRight className="w-4 h-4 text-gray-400" />
                  <span className="diff-new">{r.new.substring(0, 30)}</span>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Text Preview */}
        {text && (
          <div className="bg-white rounded-xl border border-gray-200 p-4">
            <h4 className="font-medium text-gray-800 mb-3">Matn ko'rinishi</h4>
            <div className="bg-gray-50 rounded-lg p-3 max-h-[250px] overflow-y-auto">
              <pre className="text-sm text-gray-600 whitespace-pre-wrap font-mono">
                {text.substring(0, 1500)}
                {text.length > 1500 && '...'}
              </pre>
            </div>
          </div>
        )}

        {/* Result */}
        {result && (
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            className="p-4 bg-green-50 border border-green-200 rounded-xl"
          >
            <div className="flex items-center gap-3">
              <CheckCircle className="w-6 h-6 text-green-600" />
              <div>
                <p className="font-semibold text-green-800">
                  {result.changes} ta o'zgarish qo'llandi!
                </p>
                <p className="text-sm text-green-600">Fayl yuklab olindi</p>
              </div>
            </div>
          </motion.div>
        )}
      </div>
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
