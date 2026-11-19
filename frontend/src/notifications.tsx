import { createContext, useCallback, useContext, useEffect, useMemo, useRef, useState, type ReactNode } from 'react';
import { useI18n } from './i18n';

export type NoticeKind = 'success' | 'error' | 'warning' | 'info';
type Notice = { id: number; kind: NoticeKind; message: string };
type NotificationApi = { notify: (kind: NoticeKind, message: string) => void; confirm: (message: string, title?: string) => Promise<boolean> };
const Context = createContext<NotificationApi | null>(null);

export function NotificationProvider({ children }: { children: ReactNode }) {
  const [notices, setNotices] = useState<Notice[]>([]);
  const timers = useRef(new Map<number, number>());
  const sequence = useRef(0);
  const resolver = useRef<((confirmed: boolean) => void) | null>(null);
  const [confirmation, setConfirmation] = useState<{ title?: string; message: string } | null>(null);
  const { t } = useI18n();
  const dismiss = useCallback((id: number) => {
    const timer = timers.current.get(id);
    if (timer) window.clearTimeout(timer);
    timers.current.delete(id);
    setNotices(current => current.filter(notice => notice.id !== id));
  }, []);
  const notify = useCallback((kind: NoticeKind, message: string) => {
    const newId = ++sequence.current;
    setNotices(current => {
      if (current.some(notice => notice.kind === kind && notice.message === message)) return current;
      return [...current.slice(-3), { id: newId, kind, message }];
    });
    timers.current.set(newId, window.setTimeout(() => dismiss(newId), kind === 'error' ? 9000 : 4500));
  }, [dismiss]);
  const confirm = useCallback((message: string, title?: string) => new Promise<boolean>(resolve => {
    resolver.current = resolve;
    setConfirmation({ title, message });
  }), []);
  const finishConfirmation = useCallback((confirmed: boolean) => {
    setConfirmation(null);
    resolver.current?.(confirmed);
    resolver.current = null;
  }, []);
  useEffect(() => () => { timers.current.forEach(window.clearTimeout); timers.current.clear(); }, []);
  const value = useMemo(() => ({ notify, confirm }), [notify, confirm]);
  return <Context.Provider value={value}>{children}<div className="toast-stack" aria-label={t('notifications.title')}>
    {notices.map(notice => <div key={notice.id} className={`toast toast-${notice.kind}`} role={notice.kind === 'error' ? 'alert' : 'status'} aria-live={notice.kind === 'error' ? 'assertive' : 'polite'}>
      <span className="toast-kind">{t(`notifications.${notice.kind}`)}</span><span>{notice.message}</span>
      <button type="button" aria-label={t('notifications.close')} onClick={() => dismiss(notice.id)}>×</button>
    </div>)}
  </div>{confirmation&&<div className="confirm-backdrop" onMouseDown={event=>{if(event.target===event.currentTarget)finishConfirmation(false)}}><section className="confirm-dialog" role="alertdialog" aria-modal="true" aria-labelledby="confirm-title" aria-describedby="confirm-message" onKeyDown={event=>{if(event.key==='Escape')finishConfirmation(false)}}><h2 id="confirm-title">{confirmation.title||t('common.actionRequired')}</h2><p id="confirm-message">{confirmation.message}</p><div><button type="button" className="secondary" autoFocus onClick={()=>finishConfirmation(false)}>{t('common.cancel')}</button><button type="button" className="primary" onClick={()=>finishConfirmation(true)}>{t('common.confirm')}</button></div></section></div>}</Context.Provider>;
}

export function useNotifications() {
  const context = useContext(Context);
  if (!context) throw new Error('useNotifications must be used inside NotificationProvider');
  return context;
}

export function useConfirm() { return useNotifications().confirm; }
