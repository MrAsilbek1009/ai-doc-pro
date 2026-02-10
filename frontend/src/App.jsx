import React, { useState, useCallback, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { createClient } from '@supabase/supabase-js';
import { 
  Sparkles, FileText, FileSpreadsheet, 
  Download, Zap, Upload, CheckCircle, AlertCircle, Loader2, X,
  RefreshCw, Edit3, User, LogOut, Crown, Lock, Mail, Eye, EyeOff, FolderOpen, Plus
} from 'lucide-react';

// Supabase
const supabaseUrl = 'https://cfzcqykeqpzrqxoyolfi.supabase.co';
const supabaseKey = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImNmemNxeWtlcXB6cnF4b3lvbGZpIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzA2MjA5OTMsImV4cCI6MjA4NjE5Njk5M30.r53bKu2dyR82OY_tFg3pR79LHnsl_-isqmk8tN8PLks';
const supabase = createClient(supabaseUrl, supabaseKey);

// API URL
const API_URL = 'https://ai-doc-pro-production.up.railway.app';

// Tabs
const tabs = [
  { id: 'excel', label: 'Excel', icon: FileSpreadsheet },
  { id: 'autofill', label: 'Auto-Fill', icon: RefreshCw },
  { id: 'templates', label: 'Shablonlar', icon: FolderOpen },
];

// ============ AUTH MODAL ============
const AuthModal = ({ isOpen, onClose, onSuccess }) => {
  const [mode, setMode] = useState('login');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [fullName, setFullName] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [message, setMessage] = useState('');
  const [showPassword, setShowPassword] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setMessage('');

    try {
      if (mode === 'login') {
        const { data, error } = await supabase.auth.signInWithPassword({ email, password });
        if (error) throw error;
        onSuccess(data.user);
        onClose();
      } else if (mode === 'register') {
        const { data, error } = await supabase.auth.signUp({
          email,
          password,
          options: { data: { full_name: fullName } }
        });
        if (error) throw error;
        if (data.user) {
          onSuccess(data.user);
          onClose();
        }
      } else if (mode === 'forgot') {
        const { error } = await supabase.auth.resetPasswordForEmail(email);
        if (error) throw error;
        setMessage('Parolni tiklash havolasi yuborildi!');
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <motion.div
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        className="bg-white rounded-2xl p-6 w-full max-w-md"
      >
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-xl font-bold text-gray-800">
            {mode === 'login' ? 'Kirish' : mode === 'register' ? "Ro'yxatdan o'tish" : 'Parolni tiklash'}
          </h2>
          <button onClick={onClose} className="p-1 hover:bg-gray-100 rounded-lg">
            <X className="w-5 h-5 text-gray-500" />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          {mode === 'register' && (
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Ism</label>
              <input
                type="text"
                value={fullName}
                onChange={(e) => setFullName(e.target.value)}
                className="w-full px-4 py-2 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="Ismingiz"
              />
            </div>
          )}

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Email</label>
            <div className="relative">
              <Mail className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full pl-10 pr-4 py-2 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="email@example.com"
                required
              />
            </div>
          </div>

          {mode !== 'forgot' && (
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Parol</label>
              <div className="relative">
                <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
                <input
                  type={showPassword ? 'text' : 'password'}
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="w-full pl-10 pr-10 py-2 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="••••••••"
                  required
                  minLength={6}
                />
                <button type="button" onClick={() => setShowPassword(!showPassword)} className="absolute right-3 top-1/2 -translate-y-1/2">
                  {showPassword ? <EyeOff className="w-5 h-5 text-gray-400" /> : <Eye className="w-5 h-5 text-gray-400" />}
                </button>
              </div>
            </div>
          )}

          {error && <div className="p-3 bg-red-50 border border-red-100 rounded-xl text-red-600 text-sm">{error}</div>}
          {message && <div className="p-3 bg-green-50 border border-green-100 rounded-xl text-green-600 text-sm">{message}</div>}

          <button type="submit" disabled={loading} className="w-full py-3 bg-blue-600 hover:bg-blue-700 text-white font-medium rounded-xl disabled:opacity-50 flex items-center justify-center gap-2">
            {loading && <Loader2 className="w-5 h-5 animate-spin" />}
            {mode === 'login' ? 'Kirish' : mode === 'register' ? "Ro'yxatdan o'tish" : 'Yuborish'}
          </button>
        </form>

        <div className="mt-4 text-center text-sm text-gray-600">
          {mode === 'login' ? (
            <>
              <button onClick={() => setMode('forgot')} className="text-blue-600 hover:underline">Parolni unutdingizmi?</button>
              <span className="mx-2">•</span>
              <button onClick={() => setMode('register')} className="text-blue-600 hover:underline">Ro'yxatdan o'tish</button>
            </>
          ) : (
            <button onClick={() => setMode('login')} className="text-blue-600 hover:underline">Kirish sahifasiga</button>
          )}
        </div>
      </motion.div>
    </div>
  );
};

// ============ LIMIT BANNER ============
const LimitBanner = ({ remaining, onUpgrade, onLogin, isLoggedIn }) => (
  <div className="mb-6 p-4 bg-gradient-to-r from-amber-50 to-orange-50 border border-amber-200 rounded-xl">
    <div className="flex items-center justify-between flex-wrap gap-3">
      <div className="flex items-center gap-3">
        <div className="w-10 h-10 bg-amber-100 rounded-xl flex items-center justify-center">
          <Zap className="w-5 h-5 text-amber-600" />
        </div>
        <div>
          <p className="font-medium text-gray-800">Bugun {remaining} ta bepul imkoniyat qoldi</p>
          <p className="text-sm text-gray-500">Premium obuna bilan cheksiz foydalaning</p>
        </div>
      </div>
      <div className="flex gap-2">
        {!isLoggedIn && (
          <button onClick={onLogin} className="px-4 py-2 text-sm font-medium text-gray-700 hover:bg-white rounded-lg">
            Kirish
          </button>
        )}
        <button onClick={onUpgrade} className="px-4 py-2 bg-gradient-to-r from-amber-500 to-orange-500 text-white text-sm font-medium rounded-lg flex items-center gap-2">
          <Crown className="w-4 h-4" />
          Premium - 29,000 so'm/oy
        </button>
      </div>
    </div>
  </div>
);

// ============ EXCEL TAB ============
const ExcelTab = ({ onLimitReached, updateRemaining }) => {
  const [prompt, setPrompt] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [showAddTemplate, setShowAddTemplate] = useState(false);
  const [customTemplates, setCustomTemplates] = useState(() => {
    const saved = localStorage.getItem('excel_templates');
    return saved ? JSON.parse(saved) : [];
  });

  const saveTemplates = (templates) => {
    setCustomTemplates(templates);
    localStorage.setItem('excel_templates', JSON.stringify(templates));
  };

  const addTemplate = (text) => {
    if (text.trim() && !customTemplates.includes(text.trim())) {
      saveTemplates([...customTemplates, text.trim()]);
    }
    setShowAddTemplate(false);
  };

  const removeTemplate = (index) => {
    saveTemplates(customTemplates.filter((_, i) => i !== index));
  };

  const handleGenerate = async () => {
    if (!prompt.trim()) return;
    
    setLoading(true);
    setError(null);
    setResult(null);
    
    try {
      const response = await fetch(`${API_URL}/api/excel/generate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ prompt })
      });
      
      if (response.status === 429) {
        onLimitReached();
        setError('Kunlik limit tugadi. Premium obunaga o\'ting!');
        return;
      }
      
      if (!response.ok) {
        const err = await response.json().catch(() => ({}));
        throw new Error(err.detail || 'Xatolik yuz berdi');
      }
      
      const blob = await response.blob();
      const contentDisposition = response.headers.get('content-disposition');
      let filename = 'hujjat.xlsx';
      
      if (contentDisposition) {
        const match = contentDisposition.match(/filename="?([^";\n]+)"?/);
        if (match) filename = match[1];
      }
      
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = filename;
      document.body.appendChild(a);
      a.click();
      a.remove();
      window.URL.revokeObjectURL(url);
      
      setResult({ filename });
      updateRemaining();
      
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const defaultTemplates = [
    "Oylik moliyaviy hisobot - daromad va xarajatlar",
    "Kompaniya xodimlari ro'yxati va maoshlari",
    "Mahsulotlar ro'yxati - narx va miqdor bilan"
  ];

  return (
    <div className="space-y-6">
      <div>
        <textarea
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
          placeholder="Qanday Excel jadval kerak? Masalan: Restoran uchun haftalik tushum hisoboti..."
          className="w-full p-4 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 min-h-[120px] resize-none"
          disabled={loading}
        />
        
        {/* Templates */}
        <div className="flex flex-wrap gap-2 mt-3">
          {defaultTemplates.map((t, i) => (
            <button key={`d-${i}`} onClick={() => setPrompt(t)} className="text-xs px-3 py-1.5 bg-gray-100 hover:bg-gray-200 text-gray-600 rounded-lg">
              {t.substring(0, 35)}...
            </button>
          ))}
          {customTemplates.map((t, i) => (
            <div key={`c-${i}`} className="flex items-center gap-1 text-xs px-3 py-1.5 bg-blue-50 text-blue-600 rounded-lg group">
              <button onClick={() => setPrompt(t)} className="hover:underline">
                {t.substring(0, 30)}...
              </button>
              <button onClick={() => removeTemplate(i)} className="opacity-0 group-hover:opacity-100 ml-1 text-red-400 hover:text-red-600">
                <X className="w-3 h-3" />
              </button>
            </div>
          ))}
        </div>
        
        {/* Add Template Button */}
        {showAddTemplate ? (
          <div className="mt-3 flex gap-2">
            <input
              type="text"
              placeholder="Yangi shablon matni..."
              className="flex-1 px-3 py-2 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              onKeyDown={(e) => {
                if (e.key === 'Enter') addTemplate(e.target.value);
                if (e.key === 'Escape') setShowAddTemplate(false);
              }}
              autoFocus
            />
            <button onClick={() => setShowAddTemplate(false)} className="px-3 py-2 text-gray-500 hover:bg-gray-100 rounded-lg">
              Bekor
            </button>
          </div>
        ) : (
          <button 
            onClick={() => setShowAddTemplate(true)} 
            className="mt-3 w-full py-2 border-2 border-dashed border-gray-200 hover:border-gray-300 text-gray-500 text-sm rounded-lg flex items-center justify-center gap-2"
          >
            <Plus className="w-4 h-4" />
            Shablon qo'shmoq
          </button>
        )}
      </div>

      <button 
        onClick={handleGenerate} 
        disabled={loading || !prompt.trim()} 
        className="w-full py-3 bg-blue-600 hover:bg-blue-700 text-white font-medium rounded-xl disabled:opacity-50 flex items-center justify-center gap-2"
      >
        {loading ? <Loader2 className="w-5 h-5 animate-spin" /> : <Sparkles className="w-5 h-5" />}
        {loading ? 'Yaratilmoqda...' : 'Yaratish'}
      </button>

      {error && (
        <div className="p-4 bg-red-50 border border-red-100 rounded-xl flex items-center gap-3">
          <AlertCircle className="w-5 h-5 text-red-500 flex-shrink-0" />
          <span className="text-red-700">{error}</span>
        </div>
      )}

      {result && (
        <div className="p-4 bg-green-50 border border-green-100 rounded-xl flex items-center gap-3">
          <CheckCircle className="w-5 h-5 text-green-500 flex-shrink-0" />
          <div>
            <p className="font-medium text-green-800">{result.filename}</p>
            <p className="text-sm text-green-600">Muvaffaqiyatli yaratildi!</p>
          </div>
        </div>
      )}
    </div>
  );
};

// ============ AUTOFILL TAB ============
const AutoFillTab = ({ onLimitReached, updateRemaining }) => {
  const [files, setFiles] = useState([]);
  const [instruction, setInstruction] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [dragActive, setDragActive] = useState(false);
  const [showAddTemplate, setShowAddTemplate] = useState(false);
  const [customTemplates, setCustomTemplates] = useState(() => {
    const saved = localStorage.getItem('autofill_templates');
    return saved ? JSON.parse(saved) : [];
  });

  const saveTemplates = (templates) => {
    setCustomTemplates(templates);
    localStorage.setItem('autofill_templates', JSON.stringify(templates));
  };

  const addTemplate = (text) => {
    if (text.trim() && !customTemplates.includes(text.trim())) {
      saveTemplates([...customTemplates, text.trim()]);
    }
    setShowAddTemplate(false);
  };

  const removeTemplate = (index) => {
    saveTemplates(customTemplates.filter((_, i) => i !== index));
  };

  const appendInstruction = (text) => {
    setInstruction(prev => prev ? `${prev}\n${text}` : text);
  };

  const defaultTemplates = [
    "Shartnoma raqamini ___ ga o'zgartir",
    "Sanalarni bugungi kunga o'zgartir", 
    "Mijoz ismi: ___",
    "Pasport raqami: ___",
    "Avtomobil: ___, VIN: ___",
    "Narxni ___ so'm ga o'zgartir"
  ];

  const handleDrag = useCallback((e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(e.type === "dragenter" || e.type === "dragover");
  }, []);

  const handleDrop = useCallback((e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    const droppedFiles = Array.from(e.dataTransfer.files).filter(f => f.name.toLowerCase().endsWith('.docx'));
    if (droppedFiles.length > 0) {
      setFiles(prev => [...prev, ...droppedFiles].slice(0, 10));
      setResult(null);
      setError(null);
    }
  }, []);

  const handleFileChange = (e) => {
    const selectedFiles = Array.from(e.target.files).filter(f => f.name.toLowerCase().endsWith('.docx'));
    if (selectedFiles.length > 0) {
      setFiles(prev => [...prev, ...selectedFiles].slice(0, 10));
      setResult(null);
      setError(null);
    }
  };

  const removeFile = (index) => setFiles(prev => prev.filter((_, i) => i !== index));

  const handleProcess = async () => {
    if (files.length === 0 || !instruction.trim()) {
      setError("Fayl va ko'rsatma kiriting");
      return;
    }
    
    setLoading(true);
    setError(null);
    setResult(null);
    
    try {
      const formData = new FormData();
      files.forEach(f => formData.append('files', f));
      formData.append('instruction', instruction);
      
      const response = await fetch(`${API_URL}/api/autofill/process`, {
        method: 'POST',
        body: formData
      });
      
      if (response.status === 429) {
        onLimitReached();
        setError('Kunlik limit tugadi. Premium obunaga o\'ting!');
        return;
      }
      
      if (!response.ok) {
        const err = await response.json().catch(() => ({}));
        throw new Error(err.detail || 'Xatolik yuz berdi');
      }
      
      const blob = await response.blob();
      const contentDisposition = response.headers.get('content-disposition');
      let filename = files.length > 1 ? 'tahrirlangan_hujjatlar.zip' : `tahrirlangan_${files[0].name}`;
      
      if (contentDisposition) {
        const match = contentDisposition.match(/filename="?([^";\n]+)"?/);
        if (match) filename = decodeURIComponent(match[1]);
      }
      
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = filename;
      document.body.appendChild(a);
      a.click();
      a.remove();
      window.URL.revokeObjectURL(url);
      
      setResult({ filename, count: files.length });
      updateRemaining();
      
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const resetAll = () => {
    setFiles([]);
    setInstruction('');
    setResult(null);
    setError(null);
  };

  return (
    <div className="space-y-6">
      <div
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
        className={`border-2 border-dashed rounded-xl p-8 text-center transition-colors ${
          dragActive ? 'border-blue-500 bg-blue-50' : 'border-gray-200 hover:border-gray-300'
        }`}
      >
        <input type="file" onChange={handleFileChange} accept=".docx" multiple className="hidden" id="file-upload" />
        <label htmlFor="file-upload" className="cursor-pointer">
          <Upload className="w-10 h-10 text-gray-400 mx-auto mb-3" />
          <p className="text-gray-600 font-medium">Word fayllarni tashlang yoki tanlang</p>
          <p className="text-gray-400 text-sm mt-1">Faqat .docx (maksimum 10 ta)</p>
        </label>
      </div>

      {files.length > 0 && (
        <div className="space-y-2">
          <p className="text-sm font-medium text-gray-700">{files.length} ta fayl:</p>
          <div className="flex flex-wrap gap-2">
            {files.map((f, i) => (
              <div key={i} className="flex items-center gap-2 px-3 py-2 bg-gray-100 rounded-lg">
                <FileText className="w-4 h-4 text-blue-500" />
                <span className="text-sm text-gray-700 max-w-[150px] truncate">{f.name}</span>
                <button onClick={() => removeFile(i)} className="p-0.5 hover:bg-gray-200 rounded">
                  <X className="w-4 h-4 text-gray-400" />
                </button>
              </div>
            ))}
          </div>
        </div>
      )}

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">Ko'rsatma</label>
        <textarea
          value={instruction}
          onChange={(e) => setInstruction(e.target.value)}
          placeholder={`Hujjatlarda qanday o'zgarishlar kerak?

Masalan:
- Shartnoma raqamini 01-25/199B ga o'zgartir
- Mijoz ismi: Karimov Jasur
- Sanalarni bugungi kunga`}
          className="w-full p-4 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 min-h-[140px] resize-none"
          disabled={loading}
        />
        
        {/* Instruction Templates */}
        <div className="flex flex-wrap gap-2 mt-3">
          {defaultTemplates.map((t, i) => (
            <button 
              key={`d-${i}`} 
              onClick={() => appendInstruction(t)} 
              className="text-xs px-3 py-1.5 bg-gray-100 hover:bg-gray-200 text-gray-600 rounded-lg"
            >
              {t}
            </button>
          ))}
          {customTemplates.map((t, i) => (
            <div key={`c-${i}`} className="flex items-center gap-1 text-xs px-3 py-1.5 bg-blue-50 text-blue-600 rounded-lg group">
              <button onClick={() => appendInstruction(t)} className="hover:underline">
                {t.substring(0, 25)}{t.length > 25 ? '...' : ''}
              </button>
              <button onClick={() => removeTemplate(i)} className="opacity-0 group-hover:opacity-100 ml-1 text-red-400 hover:text-red-600">
                <X className="w-3 h-3" />
              </button>
            </div>
          ))}
        </div>
        
        {/* Add Template */}
        {showAddTemplate ? (
          <div className="mt-3 flex gap-2">
            <input
              type="text"
              placeholder="Yangi ko'rsatma shabloni..."
              className="flex-1 px-3 py-2 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              onKeyDown={(e) => {
                if (e.key === 'Enter') addTemplate(e.target.value);
                if (e.key === 'Escape') setShowAddTemplate(false);
              }}
              autoFocus
            />
            <button onClick={() => setShowAddTemplate(false)} className="px-3 py-2 text-gray-500 hover:bg-gray-100 rounded-lg">
              Bekor
            </button>
          </div>
        ) : (
          <button 
            onClick={() => setShowAddTemplate(true)} 
            className="mt-3 w-full py-2 border-2 border-dashed border-gray-200 hover:border-gray-300 text-gray-500 text-sm rounded-lg flex items-center justify-center gap-2"
          >
            <Plus className="w-4 h-4" />
            Shablon qo'shmoq
          </button>
        )}
      </div>

      <button 
        onClick={handleProcess} 
        disabled={loading || files.length === 0 || !instruction.trim()} 
        className="w-full py-3 bg-blue-600 hover:bg-blue-700 text-white font-medium rounded-xl disabled:opacity-50 flex items-center justify-center gap-2"
      >
        {loading ? <Loader2 className="w-5 h-5 animate-spin" /> : <Edit3 className="w-5 h-5" />}
        {loading ? 'Tahrirlanmoqda...' : 'Tasdiqlash va yuklab olish'}
      </button>

      {error && (
        <div className="p-4 bg-red-50 border border-red-100 rounded-xl flex items-center gap-3">
          <AlertCircle className="w-5 h-5 text-red-500 flex-shrink-0" />
          <span className="text-red-700">{error}</span>
        </div>
      )}

      {result && (
        <div className="p-4 bg-green-50 border border-green-100 rounded-xl">
          <div className="flex items-center gap-3">
            <CheckCircle className="w-6 h-6 text-green-500" />
            <div>
              <p className="font-medium text-green-800">{result.count} ta hujjat tahrirlandi!</p>
              <p className="text-sm text-green-600">Fayl: {result.filename}</p>
            </div>
          </div>
          <button onClick={resetAll} className="mt-3 text-sm text-green-700 hover:underline">
            Yangi hujjatlar tahrirlash
          </button>
        </div>
      )}
    </div>
  );
};

// ============ TEMPLATES TAB ============
const TemplatesTab = () => {
  const [templates, setTemplates] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch(`${API_URL}/api/templates`)
      .then(res => res.json())
      .then(data => setTemplates(data.templates || []))
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <Loader2 className="w-8 h-8 animate-spin text-gray-400" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <h3 className="text-lg font-semibold text-gray-800">Shablonlar</h3>
      
      {templates.length === 0 ? (
        <div className="text-center py-12">
          <FolderOpen className="w-12 h-12 text-gray-300 mx-auto mb-4" />
          <p className="text-gray-500">Shablonlar tez kunda qo'shiladi</p>
        </div>
      ) : (
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
          {templates.map((t) => (
            <div key={t.id} className="p-4 bg-white border border-gray-200 rounded-xl hover:shadow-md transition-shadow">
              <div className="flex items-center gap-3 mb-2">
                <div className="w-10 h-10 bg-blue-50 rounded-lg flex items-center justify-center">
                  <FileText className="w-5 h-5 text-blue-500" />
                </div>
                <div>
                  <h4 className="font-medium text-gray-800">{t.name}</h4>
                  <p className="text-xs text-gray-500">{t.category}</p>
                </div>
              </div>
              {t.description && <p className="text-sm text-gray-500">{t.description}</p>}
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

// ============ MAIN APP ============
export default function App() {
  const [activeTab, setActiveTab] = useState('excel');
  const [user, setUser] = useState(null);
  const [showAuthModal, setShowAuthModal] = useState(false);
  const [remaining, setRemaining] = useState(5);

  useEffect(() => {
    // URL hash dagi xatolikni tozalash
    if (window.location.hash.includes('error')) {
      window.history.replaceState(null, '', window.location.pathname);
    }

    // Auth tekshirish
    supabase.auth.getSession().then(({ data: { session } }) => {
      setUser(session?.user || null);
    });

    supabase.auth.onAuthStateChange((_event, session) => {
      setUser(session?.user || null);
    });

    // Limit tekshirish
    checkLimit();
  }, []);

  const checkLimit = async () => {
    try {
      const res = await fetch(`${API_URL}/api/check-limit`, { method: 'POST' });
      const data = await res.json();
      setRemaining(data.remaining ?? 5);
    } catch (e) {
      console.error(e);
    }
  };

  const handleLogout = async () => {
    await supabase.auth.signOut();
    setUser(null);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100">
      <div className="max-w-4xl mx-auto px-4 py-8">
        {/* Header */}
        <header className="flex items-center justify-between mb-6">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">AI Doc Pro</h1>
            <p className="text-sm text-gray-500">Professional hujjatlar yaratish</p>
          </div>
          
          {user ? (
            <div className="flex items-center gap-3">
              <span className="text-sm text-gray-600">{user.email}</span>
              <button onClick={handleLogout} className="p-2 hover:bg-gray-200 rounded-lg">
                <LogOut className="w-5 h-5 text-gray-500" />
              </button>
            </div>
          ) : (
            <button 
              onClick={() => setShowAuthModal(true)} 
              className="flex items-center gap-2 px-4 py-2 border border-gray-200 rounded-xl hover:bg-gray-50"
            >
              <User className="w-4 h-4" />
              Kirish
            </button>
          )}
        </header>

        {/* Limit Banner */}
        <LimitBanner
          remaining={remaining}
          onUpgrade={() => alert('To\'lov tizimi tez kunda!')}
          onLogin={() => setShowAuthModal(true)}
          isLoggedIn={!!user}
        />

        {/* Main Card */}
        <main className="bg-white rounded-2xl shadow-sm border border-gray-100 p-6">
          {/* Tabs */}
          <div className="flex justify-center gap-2 mb-6 p-1 bg-gray-100 rounded-xl">
            {tabs.map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`flex items-center gap-2 px-4 py-2 rounded-lg font-medium transition-colors ${
                  activeTab === tab.id
                    ? 'bg-white text-gray-900 shadow-sm'
                    : 'text-gray-500 hover:text-gray-700'
                }`}
              >
                <tab.icon className="w-4 h-4" />
                {tab.label}
              </button>
            ))}
          </div>

          {/* Content */}
          <AnimatePresence mode="wait">
            <motion.div
              key={activeTab}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              transition={{ duration: 0.15 }}
            >
              {activeTab === 'excel' && (
                <ExcelTab onLimitReached={() => setShowAuthModal(true)} updateRemaining={checkLimit} />
              )}
              {activeTab === 'autofill' && (
                <AutoFillTab onLimitReached={() => setShowAuthModal(true)} updateRemaining={checkLimit} />
              )}
              {activeTab === 'templates' && <TemplatesTab />}
            </motion.div>
          </AnimatePresence>
        </main>

        <p className="text-center text-gray-400 text-sm mt-6">
          AI Doc Pro v2.0 • Professional hujjatlar yaratish platformasi
        </p>
      </div>

      {/* Auth Modal */}
      <AuthModal
        isOpen={showAuthModal}
        onClose={() => setShowAuthModal(false)}
        onSuccess={(u) => {
          setUser(u);
          checkLimit();
        }}
      />
    </div>
  );
}
