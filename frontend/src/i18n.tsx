import { createContext, useCallback, useContext, useEffect, useMemo, useState, type ReactNode } from 'react';
import vi from './locales/vi';
import en from './locales/en';

export type Language = 'vi' | 'en';
const STORAGE_KEY = 'guardian_language';
const dictionaries = { vi, en } as const;
type I18nValue = {
  language: Language;
  setLanguage: (language: Language) => void;
  t: (key: string, values?: Record<string, string | number>) => string;
  formatDate: (value: string | number | Date, options?: Intl.DateTimeFormatOptions) => string;
  formatTime: (value: string | number | Date, options?: Intl.DateTimeFormatOptions) => string;
  formatDateTime: (value: string | number | Date, options?: Intl.DateTimeFormatOptions) => string;
  formatNumber: (value: number, options?: Intl.NumberFormatOptions) => string;
};
const Context = createContext<I18nValue | null>(null);

export function readLanguage(storage?: Pick<Storage, 'getItem'> | null): Language {
  try {
    const saved = (storage ?? (typeof localStorage === 'undefined' ? null : localStorage))?.getItem(STORAGE_KEY);
    return saved === 'en' ? 'en' : 'vi';
  } catch {
    return 'vi';
  }
}

export function interpolate(template: string, values?: Record<string, string | number>) {
  return template.replace(/\{\{(\w+)\}\}/g, (_, key: string) => String(values?.[key] ?? `{{${key}}}`));
}

export function I18nProvider({ children }: { children: ReactNode }) {
  const [language, setLanguage] = useState<Language>(readLanguage);
  useEffect(() => {
    document.documentElement.lang = language;
    try { localStorage.setItem(STORAGE_KEY, language); } catch { /* storage can be unavailable */ }
  }, [language]);
  const t = useCallback((key: string, values?: Record<string, string | number>) => {
    const dictionary = dictionaries[language] as Record<string, string>;
    const template = dictionary[key] ?? (dictionaries.en as Record<string, string>)[key] ?? key;
    return interpolate(template, values);
  }, [language]);
  const locale = language === 'vi' ? 'vi-VN' : 'en-US';
  const value = useMemo<I18nValue>(() => ({
    language, setLanguage, t,
    formatDate: (value, options) => new Intl.DateTimeFormat(locale, options ?? { day: '2-digit', month: '2-digit', year: 'numeric' }).format(new Date(value)),
    formatTime: (value, options) => new Intl.DateTimeFormat(locale, options ?? { hour: '2-digit', minute: '2-digit' }).format(new Date(value)),
    formatDateTime: (value, options) => new Intl.DateTimeFormat(locale, options ?? { dateStyle: 'short', timeStyle: 'short' }).format(new Date(value)),
    formatNumber: (number, options) => new Intl.NumberFormat(locale, options).format(number),
  }), [language, locale, t]);
  return <Context.Provider value={value}>{children}</Context.Provider>;
}

export function useI18n() {
  const context = useContext(Context);
  if (!context) throw new Error('useI18n must be used inside I18nProvider');
  return context;
}

export function LanguageSwitcher() {
  const { language, setLanguage, t } = useI18n();
  return <div className="language-switch" role="group" aria-label={t('common.language')}>
    <button type="button" aria-pressed={language === 'vi'} className={language === 'vi' ? 'selected' : ''} onClick={() => setLanguage('vi')}>{t('common.vietnamese')}</button>
    <button type="button" aria-pressed={language === 'en'} className={language === 'en' ? 'selected' : ''} onClick={() => setLanguage('en')}>{t('common.english')}</button>
  </div>;
}
