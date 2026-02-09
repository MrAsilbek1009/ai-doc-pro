import React, { useState, useCallback, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { createClient } from '@supabase/supabase-js';
import { 
  Sparkles, FileText, FileSpreadsheet, 
  MessageSquare, Download, Zap, Clock, Shield,
  Upload, CheckCircle, AlertCircle, Loader2, X,
  RefreshCw, Edit3, User, LogOut, Crown, Plus,
  Trash2, FolderOpen, Lock, Mail, Eye, EyeOff
} from 'lucide-react';

// Supabase client
const supabaseUrl = import.meta.env.VITE_SUPABASE_URL || 'https://cfzcqykeqpzrqxoyolfi.supabase.co';
const supabaseKey = import.meta.env.VITE_SUPABASE_ANON_KEY || 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImNmemNxeWtlcXB6cnF4b3lvbGZpIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzA2MjA5OTMsImV4cCI6MjA4NjE5Njk5M30.r53bKu2dyR82OY_tFg3pR79LHnsl_-isqmk8tN8PLks';
const supabase = createClient(supabaseUrl, supabaseKey);

// API URL
const API_URL = import.meta.env.VITE_API_URL || '';

// Tab ma'lumotlari
const tabs = [
  { id: 'excel', label: 'Excel', icon: FileSpreadsheet, active: true },
  { id: 'autofill', label: 'Auto-Fill', icon: RefreshCw, active: true },
  { id: 'templates', label: 'Shablonlar', icon: FolderOpen, active: true },
];

// ============ AUTH MODAL ============
const AuthModal = ({ isOpen, onClose, onSuccess }) => {
  const [mode, setMode] = useState('login'); // login, register, forgot
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [fullName, setFullName] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [message, setMessage] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setMessage('');

    try {
      if (mode === 'login') {
        const { data, error } = await supabase.auth.signInWithPassword({
          email,
          password
        });
        if (error) throw error;
        onSuccess(data.user);
        onClose();
      } else if (mode === 'register') {
        const { data, error } = await supabase.auth.signUp({
          email,
          password,
          options: {
            data: { full_name: fullName }
          }
        });
        if (error) throw error;
        setMessage('Ro\'yxatdan o\'tdingiz! Email ni tasdiqlang.');
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
            {mode === 'login' ? 'Kirish' : mode === 'register' ? 'Ro\'yxatdan o\'tish' : 'Parolni tiklash'}
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
                className="w-full px-4 py-2 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-primary-500"
                placeholder="Ismingiz"
                required
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
                className="w-full pl-10 pr-4 py-2 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-primary-500"
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
                  className="w-full pl-10 pr-10 py-2 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-primary-500"
                  placeholder="••••••••"
                  required
                  minLength={6}
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-3 top-1/2 -translate-y-1/2"
                >
                  {showPassword ? <EyeOff className="w-5 h-5 text-gray-400" /> : <Eye className="w-5 h-5 text-gray-400" />}
                </button>
              </div>
            </div>
          )}

          {error && (
            <div className="p-3 bg-red-50 border border-red-100 rounded-xl text-red-600 text-sm">
              {error}
            </div>
          )}

          {message && (
            <div className="p-3 bg-green-50 border border-green-100 rounded-xl text-green-600 text-sm">
              {message}
            </div>
          )}

          <button
            type="submit"
            disabled={loading}
            className="w-full py-3 bg-primary-600 hover:bg-primary-700 text-white font-medium rounded-xl transition-colors disabled:opacity-50 flex items-center justify-center gap-2"
          >
            {loading ? <Loader2 className="w-5 h-5 animate-spin" /> : null}
            {mode === 'login' ? 'Kirish' : mode === 'register' ? 'Ro\'yxatdan o\'tish' : 'Yuborish'}
          </button>
        </form>

        <div className="mt-4 text-center text-sm text-gray-600">
          {mode === 'login' ? (
            <>
              <button onClick={() => setMode('forgot')} className="text-primary-600 hover:underline">
                Parolni unutdingizmi?
              </button>
              <span className="mx-2">•</span>
              <button onClick={() => setMode('register')} className="text-primary-600 hover:underline">
                Ro'yxatdan o'tish
              </button>
            </>
          ) : (
            <button onClick={() => setMode('login')} className="text-primary-600 hover:underline">
              Kirish sahifasiga qaytish
            </button>
          )}
        </div>
      </motion.div>
    </div>
  );
};

// ============ LIMIT BANNER ============
const LimitBanner = ({ remaining, isPremium, onUpgrade, onLogin, isLoggedIn }) => {
  if (isPremium) return null;
  
  return (
    <div className="mb-6 p-4 bg-gradient-to-r from-amber-50 to-orange-50 border border-amber-200 rounded-xl">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-amber-100 rounded-xl flex items-center justify-center">
            <Zap className="w-5 h-5 text-amber-600" />
          </div>
          <div>
            <p className="font-medium text-gray-800">
              Bugun {remaining} ta bepul imkoniyat qoldi
            </p>
            <p className="text-sm text-gray-500">
              Premium obuna bilan cheksiz foydalaning
            </p>
          </div>
        </div>
        <div className="flex gap-2">
          {!isLoggedIn && (
            <button
              onClick={onLogin}
              className="px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-100 rounded-lg transition-colors"
            >
              Kirish
            </button>
          )}
          <button
            onClick={onUpgrade}
            className="px-4 py-2 bg-gradient-to-r from-amber-500 to-orange-500 text-white text-sm font-medium rounded-lg hover:opacity-90 transition-opacity flex items-center gap-2"
          >
            <Crown className="w-4 h-4" />
            Premium - 29,000 so'm/oy
          </button>
        </div>
      </div>
    </div>
  );
};

// ============ EXCEL TAB ============
const ExcelTab = ({ user, remaining, onLimitReached }) => {
  const [prompt, setPrompt] = useState('');
  const [loading, setLoading] = useState(false);
  const [preview, setPreview] = useState(null);
  const [error, setError] = useState(null);

  const handleGenerate = async () => {
    if (!prompt.trim()) return;
    if (remaining === 0) {
      onLimitReached();
      return;
    }
    
    setLoading(true);
    setError(null);
    
    try {
      const headers = { 'Content-Type': 'application/json' };
      if (user?.id) headers['X-User-ID'] = user.id;
      
      const previewRes = await fetch(`${API_URL}/api/excel/preview`, {
        method: 'POST',
        headers,
        body: JSON.stringify({ prompt })
      });
      
      let previewData = null;
      if (previewRes.ok) {
        previewData = await previewRes.json();
        setPreview(previewData);
      }
      
      const response = await fetch(`${API_URL}/api/excel/generate`, {
        method: 'POST',
        headers,
        body: JSON.stringify({ prompt })
      });
      
      if (response.status === 429) {
        onLimitReached();
        throw new Error('Kunlik limit tugadi');
      }
      
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
        throw new Error('Xatolik yuz berdi');
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const examples = [
    "Kichik biznes uchun oylik moliyaviy hisobot",
    "IT kompaniya xodimlari va maoshlari",
    "Haftalik dars jadvali"
  ];

  return (
    <div className="space-y-6">
      <div>
        <textarea
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
          placeholder="Qanday Excel jadval kerak? Masalan: Restoran uchun haftalik tushum hisoboti..."
          className="input-field min-h-[140px] text-base"
          disabled={loading}
        />
        <div className="flex flex-wrap gap-2 mt-3">
          {examples.map((ex, i) => (
            <button key={i} onClick={() => setPrompt(ex)} className="text-xs px-3 py-1.5 bg-gray-50 hover:bg-gray-100 text-gray-600 rounded-lg border border-gray-100">
              {ex.substring(0, 40)}...
            </button>
          ))}
        </div>
      </div>

      <button onClick={handleGenerate} disabled={loading || !prompt.trim()} className="btn-primary w-full disabled:opacity-50">
        {loading ? <><Loader2 className="w-5 h-5 animate-spin" />Yaratilmoqda...</> : <><Sparkles className="w-5 h-5" />Yaratish</>}
      </button>

      {error && (
        <div className="p-4 bg-red-50 border border-red-100 rounded-xl flex items-center gap-3">
          <AlertCircle className="w-5 h-5 text-red-500" />
          <span className="text-red-700">{error}</span>
        </div>
      )}

      {preview && (
        <div className="p-6 bg-green-50 border border-green-100 rounded-xl">
          <div className="flex items-center gap-3 mb-4">
            <CheckCircle className="w-6 h-6 text-green-600" />
            <div>
              <h4 className="font-semibold text-green-800">{preview.title}.xlsx</h4>
              <p className="text-sm text-green-600">Muvaffaqiyatli yaratildi!</p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

// ============ AUTOFILL TAB ============
const AutoFillTab = ({ user, remaining, onLimitReached }) => {
  const [files, setFiles] = useState([]);
  const [instruction, setInstruction] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [dragActive, setDragActive] = useState(false);

  const handleDrag = useCallback((e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") setDragActive(true);
    else if (e.type === "dragleave") setDragActive(false);
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

  const removeFile = (index) => {
    setFiles(prev => prev.filter((_, i) => i !== index));
  };

  const handleProcess = async () => {
    if (files.length === 0 || !instruction.trim()) {
      setError("Fayl va ko'rsatma kiriting");
      return;
    }
    if (remaining === 0) {
      onLimitReached();
      return;
    }
    
    setLoading(true);
    setError(null);
    
    try {
      const formData = new FormData();
      files.forEach(f => formData.append('files', f));
      formData.append('instruction', instruction);
      
      const headers = {};
      if (user?.id) headers['X-User-ID'] = user.id;
      
      const response = await fetch(`${API_URL}/api/autofill/process`, {
        method: 'POST',
        headers,
        body: formData
      });
      
      if (response.status === 429) {
        onLimitReached();
        throw new Error('Kunlik limit tugadi');
      }
      
      if (response.ok) {
        const blob = await response.blob();
        const contentDisposition = response.headers.get('content-disposition');
        let filename = files.length > 1 ? 'tahrirlangan_hujjatlar.zip' : `tahrirlangan_${files[0].name}`;
        
        if (contentDisposition) {
          const match = contentDisposition.match(/filename[^;=\n]*=((['"]).*?\2|[^;\n]*)/);
          if (match) filename = match[1].replace(/['"]/g, '');
        }
        
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        a.remove();
        window.URL.revokeObjectURL(url);
        
        setResult({ success: true, filename, count: files.length });
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
    setFiles([]);
    setInstruction('');
    setResult(null);
    setError(null);
  };

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
          accept=".docx"
          multiple
          className="hidden"
          id="file-upload"
        />
        <label htmlFor="file-upload" className="cursor-pointer block text-center">
          <Upload className="w-10 h-10 text-gray-400 mx-auto mb-3" />
          <p className="text-gray-600 font-medium">Word fayllarni tashlang yoki tanlang</p>
          <p className="text-gray-400 text-sm mt-1">Faqat .docx (maksimum 10 ta)</p>
        </label>
      </div>

      {/* Selected Files */}
      {files.length > 0 && (
        <div className="space-y-2">
          <p className="text-sm font-medium text-gray-700">{files.length} ta fayl tanlandi:</p>
          <div className="flex flex-wrap gap-2">
            {files.map((f, i) => (
              <div key={i} className="flex items-center gap-2 px-3 py-2 bg-gray-50 rounded-lg">
                <FileText className="w-4 h-4 text-blue-500" />
                <span className="text-sm text-gray-700">{f.name}</span>
                <button onClick={() => removeFile(i)} className="p-0.5 hover:bg-gray-200 rounded">
                  <X className="w-4 h-4 text-gray-400" />
                </button>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Instruction */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">Ko'rsatma</label>
        <textarea
          value={instruction}
          onChange={(e) => setInstruction(e.target.value)}
          placeholder="Hujjatlarda qanday o'zgarishlar kerak?

Masalan:
- Shartnoma raqamini 01-25/199B ga o'zgartir
- Mijoz: Karimov Jasur Anvarovich
- Sanalarni bugungi kunga o'zgartir
- Avtomobil narxi: 250 000 000 so'm"
          className="input-field min-h-[150px]"
          disabled={loading}
        />
      </div>

      {/* Action Button */}
      <button onClick={handleProcess} disabled={loading || files.length === 0 || !instruction.trim()} className="btn-primary w-full disabled:opacity-50">
        {loading ? <><Loader2 className="w-5 h-5 animate-spin" />Tahrirlanmoqda...</> : <><Edit3 className="w-5 h-5" />Tasdiqlash va yuklab olish</>}
      </button>

      {/* Error */}
      {error && (
        <div className="p-4 bg-red-50 border border-red-100 rounded-xl flex items-center gap-3">
          <AlertCircle className="w-5 h-5 text-red-500" />
          <span className="text-red-700">{error}</span>
        </div>
      )}

      {/* Success */}
      {result && (
        <div className="p-5 bg-green-50 border border-green-200 rounded-xl">
          <div className="flex items-center gap-3">
            <CheckCircle className="w-8 h-8 text-green-600" />
            <div>
              <p className="font-semibold text-green-800">{result.count} ta hujjat tahrirlandi!</p>
              <p className="text-green-600">Fayl yuklab olindi: {result.filename}</p>
            </div>
          </div>
          <button onClick={resetAll} className="mt-4 text-sm text-green-700 hover:underline">
            Yangi hujjatlar tahrirlash
          </button>
        </div>
      )}
    </div>
  );
};

// ============ TEMPLATES TAB ============
const TemplatesTab = ({ user, onLogin }) => {
  const [templates, setTemplates] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showAddModal, setShowAddModal] = useState(false);

  useEffect(() => {
    loadTemplates();
  }, [user]);

  const loadTemplates = async () => {
    try {
      const headers = {};
      if (user?.id) headers['X-User-ID'] = user.id;
      
      const res = await fetch(`${API_URL}/api/templates`, { headers });
      const data = await res.json();
      setTemplates(data.templates || []);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const deleteTemplate = async (id) => {
    if (!confirm('Shablonni o\'chirmoqchimisiz?')) return;
    try {
      await fetch(`${API_URL}/api/templates/${id}`, {
        method: 'DELETE',
        headers: { 'X-User-ID': user?.id }
      });
      loadTemplates();
    } catch (err) {
      console.error(err);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <Loader2 className="w-8 h-8 animate-spin text-gray-400" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold text-gray-800">Shablonlar</h3>
        {user ? (
          <button onClick={() => setShowAddModal(true)} className="btn-secondary text-sm">
            <Plus className="w-4 h-4" />
            Shablon qo'shish
          </button>
        ) : (
          <button onClick={onLogin} className="btn-secondary text-sm">
            <User className="w-4 h-4" />
            Kirish
          </button>
        )}
      </div>

      {/* Templates Grid */}
      {templates.length === 0 ? (
        <div className="text-center py-12">
          <FolderOpen className="w-12 h-12 text-gray-300 mx-auto mb-4" />
          <p className="text-gray-500">Shablonlar hali yo'q</p>
          {user && (
            <button onClick={() => setShowAddModal(true)} className="mt-4 text-primary-600 hover:underline">
              Birinchi shablonni qo'shing
            </button>
          )}
        </div>
      ) : (
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
          {templates.map((t) => (
            <div key={t.id} className="p-4 bg-white border border-gray-200 rounded-xl hover:shadow-md transition-shadow">
              <div className="flex items-start justify-between">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 bg-blue-50 rounded-lg flex items-center justify-center">
                    <FileText className="w-5 h-5 text-blue-500" />
                  </div>
                  <div>
                    <h4 className="font-medium text-gray-800">{t.name}</h4>
                    <p className="text-xs text-gray-500">{t.category}</p>
                  </div>
                </div>
                {user?.id === t.user_id && (
                  <button onClick={() => deleteTemplate(t.id)} className="p-1 hover:bg-red-50 rounded">
                    <Trash2 className="w-4 h-4 text-red-400" />
                  </button>
                )}
              </div>
              {t.description && (
                <p className="text-sm text-gray-500 mt-3">{t.description}</p>
              )}
              {t.file_url && (
                <a href={t.file_url} download className="mt-3 inline-flex items-center gap-2 text-sm text-primary-600 hover:underline">
                  <Download className="w-4 h-4" />
                  Yuklab olish
                </a>
              )}
            </div>
          ))}
        </div>
      )}

      {/* Add Template Modal */}
      {showAddModal && user && (
        <AddTemplateModal
          user={user}
          onClose={() => setShowAddModal(false)}
          onSuccess={() => {
            setShowAddModal(false);
            loadTemplates();
          }}
        />
      )}
    </div>
  );
};

// ============ ADD TEMPLATE MODAL ============
const AddTemplateModal = ({ user, onClose, onSuccess }) => {
  const [file, setFile] = useState(null);
  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  const [category, setCategory] = useState('other');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!file || !name.trim()) return;

    setLoading(true);
    setError('');

    try {
      const formData = new FormData();
      formData.append('file', file);
      formData.append('name', name);
      formData.append('description', description);
      formData.append('category', category);

      const res = await fetch(`${API_URL}/api/templates`, {
        method: 'POST',
        headers: { 'X-User-ID': user.id },
        body: formData
      });

      if (!res.ok) throw new Error('Xatolik yuz berdi');
      onSuccess();
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <motion.div
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        className="bg-white rounded-2xl p-6 w-full max-w-md"
      >
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-xl font-bold text-gray-800">Shablon qo'shish</h2>
          <button onClick={onClose} className="p-1 hover:bg-gray-100 rounded-lg">
            <X className="w-5 h-5 text-gray-500" />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Fayl (.docx)</label>
            <input
              type="file"
              accept=".docx"
              onChange={(e) => setFile(e.target.files[0])}
              className="w-full"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Nomi</label>
            <input
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              className="w-full px-4 py-2 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-primary-500"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Tavsif</label>
            <textarea
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              className="w-full px-4 py-2 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-primary-500"
              rows={2}
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Kategoriya</label>
            <select
              value={category}
              onChange={(e) => setCategory(e.target.value)}
              className="w-full px-4 py-2 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-primary-500"
            >
              <option value="contract">Shartnoma</option>
              <option value="legal">Huquqiy</option>
              <option value="application">Ariza</option>
              <option value="report">Hisobot</option>
              <option value="other">Boshqa</option>
            </select>
          </div>

          {error && (
            <div className="p-3 bg-red-50 border border-red-100 rounded-xl text-red-600 text-sm">
              {error}
            </div>
          )}

          <button type="submit" disabled={loading} className="w-full py-3 bg-primary-600 text-white font-medium rounded-xl disabled:opacity-50">
            {loading ? 'Saqlanmoqda...' : 'Saqlash'}
          </button>
        </form>
      </motion.div>
    </div>
  );
};

// ============ MAIN APP ============
export default function App() {
  const [activeTab, setActiveTab] = useState('excel');
  const [user, setUser] = useState(null);
  const [showAuthModal, setShowAuthModal] = useState(false);
  const [limitInfo, setLimitInfo] = useState({ remaining: 5, is_premium: false });

  useEffect(() => {
    // Auth state
    supabase.auth.getSession().then(({ data: { session } }) => {
      setUser(session?.user || null);
      if (session?.user) checkLimit(session.user.id);
    });

    supabase.auth.onAuthStateChange((_event, session) => {
      setUser(session?.user || null);
      if (session?.user) checkLimit(session.user.id);
    });

    // Initial limit check
    checkLimit();
  }, []);

  const checkLimit = async (userId = null) => {
    try {
      const headers = {};
      if (userId) headers['X-User-ID'] = userId;
      
      const res = await fetch(`${API_URL}/api/check-limit?user_id=${userId || ''}`, {
        method: 'POST',
        headers
      });
      const data = await res.json();
      setLimitInfo(data);
    } catch (err) {
      console.error(err);
    }
  };

  const handleLogout = async () => {
    await supabase.auth.signOut();
    setUser(null);
    checkLimit();
  };

  const handleLimitReached = () => {
    setShowAuthModal(true);
  };

  const renderTabContent = () => {
    switch (activeTab) {
      case 'excel':
        return <ExcelTab user={user} remaining={limitInfo.remaining} onLimitReached={handleLimitReached} />;
      case 'autofill':
        return <AutoFillTab user={user} remaining={limitInfo.remaining} onLimitReached={handleLimitReached} />;
      case 'templates':
        return <TemplatesTab user={user} onLogin={() => setShowAuthModal(true)} />;
      default:
        return null;
    }
  };

  return (
    <div className="min-h-screen bg-dots">
      <div className="fixed top-20 right-20 w-64 h-64 bg-primary-200/30 rounded-full blur-3xl pointer-events-none" />
      <div className="fixed bottom-20 left-20 w-96 h-96 bg-accent/10 rounded-full blur-3xl pointer-events-none" />
      
      <div className="max-w-5xl mx-auto px-4 py-8 relative">
        {/* Header */}
        <header className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">AI Doc Pro</h1>
            <p className="text-sm text-gray-500">Professional hujjatlar yaratish</p>
          </div>
          
          <div className="flex items-center gap-3">
            {user ? (
              <>
                <div className="text-right">
                  <p className="text-sm font-medium text-gray-800">{user.email}</p>
                  {limitInfo.is_premium && (
                    <span className="text-xs text-amber-600 flex items-center gap-1">
                      <Crown className="w-3 h-3" /> Premium
                    </span>
                  )}
                </div>
                <button onClick={handleLogout} className="p-2 hover:bg-gray-100 rounded-lg">
                  <LogOut className="w-5 h-5 text-gray-500" />
                </button>
              </>
            ) : (
              <button onClick={() => setShowAuthModal(true)} className="btn-secondary">
                <User className="w-4 h-4" />
                Kirish
              </button>
            )}
          </div>
        </header>

        {/* Limit Banner */}
        <LimitBanner
          remaining={limitInfo.remaining}
          isPremium={limitInfo.is_premium}
          onUpgrade={() => alert('To\'lov tizimi tez kunda!')}
          onLogin={() => setShowAuthModal(true)}
          isLoggedIn={!!user}
        />

        {/* Main Card */}
        <main className="glass-card rounded-3xl p-8">
          {/* Tabs */}
          <div className="flex justify-center gap-2 mb-8 p-1.5 bg-gray-50/80 rounded-2xl">
            {tabs.map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`tab-item ${activeTab === tab.id ? 'tab-item-active' : 'tab-item-inactive'}`}
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
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -20 }}
              transition={{ duration: 0.2 }}
            >
              {renderTabContent()}
            </motion.div>
          </AnimatePresence>
        </main>

        {/* Footer */}
        <p className="text-center text-gray-400 text-sm mt-8">
          AI Doc Pro v2.0 • Professional hujjatlar yaratish platformasi
        </p>
      </div>

      {/* Auth Modal */}
      <AuthModal
        isOpen={showAuthModal}
        onClose={() => setShowAuthModal(false)}
        onSuccess={(u) => {
          setUser(u);
          checkLimit(u.id);
        }}
      />
    </div>
  );
}
