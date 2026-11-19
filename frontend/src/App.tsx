import { useEffect, useRef, useState } from 'react';
import {
  LayoutDashboard, CalendarDays, BookOpen, ClipboardCheck, Brain,
  ChartNoAxesCombined, Monitor, Settings, Bell, Search, Plus, Clock3,
  ChevronRight, ChevronLeft, Menu, LogOut, CheckCircle2, Flame,
  ShieldCheck, FileText, RefreshCw, X, UserRound, AlertCircle,
} from 'lucide-react';
import { useI18n, LanguageSwitcher } from './i18n';
import {
  api, localizedApiMessage, setApiLanguage, setAccessTokenUpdated,
  setAuthFailureHandler, refreshAccessToken,
} from './services/api';
import { useNotifications, useConfirm } from './notifications';

type User = { id: string; username: string; full_name: string; role: string };

function usernameSuggestion(name: string) {
  return name.normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '')
    .replace(/\u0111/g, 'd')
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, '.')
    .replace(/^\.+|\.+$/g, '')
    .slice(0, 32);
}

function statusText(value: string | undefined, t: (key: string) => string) {
  if (!value) return '';
  const key = `status.${value.toLowerCase()}`;
  const translated = t(key);
  return translated === key ? value : translated;
}

const allNav = [
  ['common.nav.dashboard', LayoutDashboard, 'dashboard', ['GUARDIAN', 'STUDENT']],
  ['common.nav.schedules', CalendarDays, 'schedules', ['GUARDIAN', 'STUDENT']],
  ['common.nav.assignments', ClipboardCheck, 'assignments', ['GUARDIAN', 'STUDENT']],
  ['common.nav.subjects', BookOpen, 'subjects', ['GUARDIAN', 'STUDENT']],
  ['common.nav.materials', FileText, 'materials', ['GUARDIAN', 'STUDENT']],
  ['common.nav.ai', Brain, 'ai', ['GUARDIAN', 'STUDENT']],
  ['common.nav.quizzes', ClipboardCheck, 'quizzes', ['GUARDIAN', 'STUDENT']],
  ['common.nav.monitoring', Monitor, 'monitoring', ['GUARDIAN', 'STUDENT']],
  ['common.nav.analytics', ChartNoAxesCombined, 'analytics', ['GUARDIAN', 'STUDENT']],
  ['common.nav.settings', Settings, 'settings', ['GUARDIAN', 'STUDENT', 'ADMIN']],
] as const;

export default function App() {
  const { language, t, formatDate, formatTime, formatDateTime, formatNumber } = useI18n();
  const { notify } = useNotifications();
  const confirm = useConfirm();
  const [token, setToken] = useState('');
  const restoreStarted = useRef(false);
  const [restoring, setRestoring] = useState(true);
  const [user, setUser] = useState<User | null>(null);
  const [page, setPage] = useState('dashboard');
  const [menu, setMenu] = useState(false);
  const [collapsed, setCollapsed] = useState(() => localStorage.getItem('guardian_sidebar') === 'collapsed');
  const [accountMenu, setAccountMenu] = useState(false);
  const [search, setSearch] = useState('');
  const [data, setData] = useState<any>(null);
  const [error, setError] = useState<unknown>(null);
  const [dashboardError, setDashboardError] = useState<unknown>(null);
  const [loading, setLoading] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [login, setLogin] = useState({ username: '', password: '' });
  const [register, setRegister] = useState({ username: '', email: '', full_name: '', password: '' });
  const [registerMode, setRegisterMode] = useState(false);
  const [usernameEdited, setUsernameEdited] = useState(false);
  const [registerNotice, setRegisterNotice] = useState('');
  const [modal, setModal] = useState('');
  const [form, setForm] = useState<any>({});

  useEffect(() => {
    localStorage.removeItem('guardian_token');
  }, []);

  useEffect(() => {
    setApiLanguage(language);
    setAccessTokenUpdated(setToken);
    setAuthFailureHandler(() => {
      setToken('');
      setUser(null);
      setRestoring(false);
      notify('warning', t('errors.AUTH_TOKEN_EXPIRED'));
    });
  }, [language, t, notify]);

  useEffect(() => {
    if (token) {
      api('/auth/me', token).then(setUser).catch((e: any) => {
        if (e.status === 401) {
          setToken('');
          setUser(null);
        } else setError(e);
      }).finally(() => setRestoring(false));
    } else if (!restoreStarted.current) {
      restoreStarted.current = true;
      refreshAccessToken()
        .then((session) => setToken(session.access_token))
        .catch(() => setRestoring(false));
    }
  }, [token]);

  useEffect(() => {
    if (!token) return;
    const timer = window.setInterval(() => {
      refreshAccessToken().then((session) => setToken(session.access_token)).catch((e: any) => {
        if (e.status === 401) {
          setToken('');
          setUser(null);
          setRestoring(false);
          notify('warning', t('errors.AUTH_TOKEN_EXPIRED'));
        }
      });
    }, 10 * 60 * 1000);
    return () => window.clearInterval(timer);
  }, [token, notify, t]);

  useEffect(() => {
    if (!token || !user) return;
    setLoading(true);
    setError('');
    setDashboardError(null);
    if (page === 'ai') {
      setData(null);
      setLoading(false);
      return;
    }
    const path = page === 'dashboard'
      ? `/dashboard/${user.role.toLowerCase()}`
      : page === 'monitoring'
        ? '/monitoring/status'
        : page === 'analytics'
          ? '/analytics'
          : `/${page}`;
    api(path, token).then(setData).catch((e) => {
      setData(null);
      if (page === 'dashboard') setDashboardError(e);
      else setError(e);
    }).finally(() => setLoading(false));
  }, [page, token, user]);

  async function signIn(event: React.FormEvent) {
    event.preventDefault();
    setError('');
    setRegisterNotice('');
    setSubmitting(true);
    try {
      const session = await api('/auth/login', '', {
        method: 'POST',
        body: JSON.stringify(login),
      });
      setToken(session.access_token);
      setUser(session.user);
      notify('success', t('auth.loginSuccess'));
    } catch (e) {
      setError(e);
    } finally {
      setSubmitting(false);
    }
  }

  async function signUp(event: React.FormEvent) {
    event.preventDefault();
    setError('');
    setRegisterNotice('');
    setSubmitting(true);
    try {
      await api('/auth/register', '', {
        method: 'POST',
        body: JSON.stringify(register),
      });
      setRegisterMode(false);
      setLogin({ username: register.username.trim().toLowerCase(), password: '' });
      setRegister({ username: '', email: '', full_name: '', password: '' });
      setUsernameEdited(false);
      setRegisterNotice('auth.registerSuccess');
      notify('success', t('auth.registerSuccess'));
    } catch (e) {
      setError(e);
    } finally {
      setSubmitting(false);
    }
  }

  async function closeModal() {
    if (Object.values(form).some((value) => value !== '' && value !== null && value !== undefined)) {
      if (!await confirm(t('common.discardConfirm'), t('common.discardTitle'))) return;
    }
    setModal('');
    setForm({});
  }

  async function save(event: React.FormEvent) {
    event.preventDefault();
    setSubmitting(true);
    const endpoint = modal === 'subject' ? 'subjects' : modal === 'schedule' ? 'schedules' : 'assignments';
    const payload = { ...form };
    if (endpoint === 'schedules') {
      for (const field of ['start_at', 'end_at']) {
        if (payload[field]) payload[field] = new Date(payload[field]).toISOString();
      }
    }
    try {
      await api(`/${endpoint}`, token, { method: 'POST', body: JSON.stringify({ data: payload }) });
      setModal('');
      setForm({});
      setPage(endpoint);
      setData(await api(`/${endpoint}`, token));
      notify('success', t('notifications.saveSuccess'));
    } catch (e) {
      setError(e);
    } finally {
      setSubmitting(false);
    }
  }

  function toggleCollapsed() {
    setCollapsed((current) => {
      const next = !current;
      localStorage.setItem('guardian_sidebar', next ? 'collapsed' : 'expanded');
      return next;
    });
  }

  if (restoring) {
    return (
      <main className="login">
        <div className="login-card login-loading">
          <LanguageSwitcher />
          <div className="loading" role="status">{t('common.loading')}</div>
        </div>
      </main>
    );
  }

  if (!user) {
    return (
      <main className="login">
        <section className="login-card" aria-labelledby="auth-title">
          <LanguageSwitcher />
          <div className="brand-mark">S</div>
          <p className="eyebrow">{t('common.brand').toUpperCase()}</p>
          <h1 id="auth-title">{registerMode ? t('auth.registerTitle') : t('auth.tagline')}</h1>
          <p className="muted">{registerMode ? t('auth.registerIntro') : t('auth.loginIntro')}</p>
          {registerNotice && <div className="success" role="status">{t(registerNotice)}</div>}
          {registerMode ? (
            <form onSubmit={signUp} noValidate>
              <label>{t('auth.fullName')}
                <input autoComplete="name" maxLength={150} value={register.full_name} onChange={(event) => {
                  const full_name = event.target.value;
                  setRegister((value) => ({ ...value, full_name, username: usernameEdited ? value.username : usernameSuggestion(full_name) }));
                }} required />
              </label>
              <label>{t('auth.username')}
                <input autoComplete="username" minLength={3} maxLength={32} value={register.username} onChange={(event) => {
                  setUsernameEdited(true);
                  setRegister({ ...register, username: event.target.value });
                }} required />
              </label>
              <small className="field-hint">{t('auth.usernameHint')}</small>
              <label>{t('auth.email')}
                <input type="email" autoComplete="email" maxLength={255} value={register.email} onChange={(event) => setRegister({ ...register, email: event.target.value })} required />
              </label>
              <label>{t('auth.passwordHint')}
                <input type="password" autoComplete="new-password" minLength={12} maxLength={128} value={register.password} onChange={(event) => setRegister({ ...register, password: event.target.value })} required />
              </label>
              {Boolean(error) && <div className="error" role="alert">{localizedApiMessage(error, t)}</div>}
              <button className="primary wide" disabled={submitting}>{submitting ? t('auth.registering') : t('auth.register')} <ChevronRight size={17} /></button>
            </form>
          ) : (
            <form onSubmit={signIn} noValidate>
              <label>{t('auth.emailOrUsername')}
                <input autoComplete="username" value={login.username} onChange={(event) => setLogin({ ...login, username: event.target.value })} required />
              </label>
              <label>{t('auth.password')}
                <input type="password" autoComplete="current-password" value={login.password} onChange={(event) => setLogin({ ...login, password: event.target.value })} required />
              </label>
              {Boolean(error) && <div className="error" role="alert">{localizedApiMessage(error, t)}</div>}
              <button className="primary wide" disabled={submitting}>{submitting ? t('auth.signingIn') : t('auth.signIn')} <ChevronRight size={17} /></button>
            </form>
          )}
          <button className="secondary wide" type="button" onClick={() => {
            setRegisterMode(!registerMode);
            setUsernameEdited(false);
            setError('');
            setRegisterNotice('');
          }}>{registerMode ? t('auth.switchToLogin') : t('auth.switchToRegister')}</button>
          <small>{t('auth.studentInvitationNote')}</small>
        </section>
      </main>
    );
  }

  const nav = allNav.filter((item) => item[3].includes(user.role as never));
  const roleLabel = user.role === 'GUARDIAN' ? t('common.guardianAccount') : user.role === 'STUDENT' ? t('common.studentAccount') : user.role;
  const hour = new Date().getHours();
  const greeting = hour < 12 ? t('dashboard.goodMorning') : hour < 18 ? t('dashboard.goodAfternoon') : t('dashboard.goodEvening');
  const visibleRecords = Array.isArray(data)
    ? data.filter((item: any) => JSON.stringify(item).toLowerCase().includes(search.toLowerCase()))
    : [];

  return (
    <div className={`shell ${collapsed ? 'sidebar-collapsed' : ''}`}>
      {menu && <button className="sidebar-backdrop" aria-label={t('common.close')} onClick={() => setMenu(false)} />}
      <aside className={menu ? 'sidebar open' : 'sidebar'} aria-label={t('common.workspaceNav')}>
        <div className="brand">
          <div className="brand-mark">S</div>
          <div className="brand-copy"><b>StudyGuardian</b><small>{t('common.workspaceTag')}</small></div>
          <button className="sidebar-toggle" type="button" onClick={toggleCollapsed} aria-label={collapsed ? t('common.expandSidebar') : t('common.collapseSidebar')}>
            {collapsed ? <ChevronRight size={17} /> : <ChevronLeft size={17} />}
          </button>
        </div>
        <div className="family">
          <div className="avatar">{user.full_name?.[0] || 'G'}</div>
          <div className="family-copy"><b>{user.full_name}</b><small>{roleLabel}</small></div>
        </div>
        <div className="nav-label">{t('common.workspaceNav')}</div>
        <nav>
          {nav.map(([label, Icon, key]) => (
            <button key={key} className={page === key ? 'nav active' : 'nav'} onClick={() => {
              setPage(key);
              setMenu(false);
              setSearch('');
            }} title={collapsed ? t(label) : undefined}>
              <Icon size={18} />
              <span>{t(label)}</span>
              {key === 'monitoring' && <i className="live-dot" />}
            </button>
          ))}
        </nav>
        <div className="sidebar-bottom">
          <div className="privacy-note">
            <ShieldCheck size={17} />
            <span><b>{t('common.transparentMonitoring')}</b><small>{t('common.approvedSignals')}</small></span>
          </div>
          <button className="nav" onClick={async () => {
            if (!await confirm(t('auth.logoutConfirm'), t('auth.logoutTitle'))) return;
            try {
              await api('/auth/logout', token, { method: 'POST' });
              notify('info', t('auth.signedOut'));
            } catch (e) {
              notify('error', localizedApiMessage(e, t));
              return;
            }
            setToken('');
            setUser(null);
          }} title={collapsed ? t('common.signOut') : undefined}>
            <LogOut size={17} /> <span>{t('common.signOut')}</span>
          </button>
        </div>
      </aside>

      <main className="main">
        <header>
          <button className="icon-btn mobile-menu" aria-label={t('common.workspaceNav')} onClick={() => setMenu(!menu)}><Menu /></button>
          <div className="crumb">
            <span>{t('common.workspace')}</span><ChevronRight size={13} />
            <b>{t(nav.find((item) => item[2] === page)?.[0] || 'common.overview')}</b>
          </div>
          <div className="head-actions">
            <LanguageSwitcher />
            <div className="search">
              <Search size={16} />
              <input aria-label={t('common.search')} placeholder={t('common.search')} value={search} onChange={(event) => setSearch(event.target.value)} />
              {search && <button type="button" aria-label={t('common.close')} onClick={() => setSearch('')}><X size={14} /></button>}
            </div>
            <button className="icon-btn notification-button" aria-label={t('notifications.title')}><Bell size={18} /><i /></button>
            <div className="account">
              <button className="avatar small account-button" type="button" aria-haspopup="menu" aria-expanded={accountMenu} onClick={() => setAccountMenu(!accountMenu)}>
                {user.full_name?.[0]}
              </button>
              {accountMenu && (
                <div className="account-menu" role="menu">
                  <div className="account-summary"><b>{user.full_name}</b><small>{roleLabel}</small></div>
                  <button type="button" role="menuitem" onClick={() => { setPage('settings'); setAccountMenu(false); }}><UserRound size={16} /> {t('settings.profile')}</button>
                  <button type="button" role="menuitem" onClick={() => { setPage('settings'); setAccountMenu(false); }}><Settings size={16} /> {t('settings.title')}</button>
                </div>
              )}
            </div>
          </div>
        </header>

        <div className="content">
          <div className="welcome">
            <div>
              <p className="eyebrow">{formatDate(new Date(), { weekday: 'long', month: 'long', day: 'numeric' }).toUpperCase()}</p>
              <h1>{page === 'dashboard'
                ? `${greeting}, ${user.full_name?.split(' ')[0] || ''}`
                : t(nav.find((item) => item[2] === page)?.[0] || 'common.overview')}</h1>
              <p className="muted">{page === 'dashboard' ? t('dashboard.subtitle') : t('subjects.section')}</p>
            </div>
            <div className="welcome-actions">
              <button className="secondary" type="button" onClick={() => {
                if (!token || !user) return;
                setLoading(true);
                setDashboardError(null);
                setError('');
                if (page === 'ai') {
                  setData(null);
                  setLoading(false);
                  return;
                }
                const path = page === 'dashboard' ? `/dashboard/${user.role.toLowerCase()}` : page === 'monitoring' ? '/monitoring/status' : page === 'analytics' ? '/analytics' : `/${page}`;
                api(path, token).then(setData).catch((e) => page === 'dashboard' ? setDashboardError(e) : setError(e)).finally(() => setLoading(false));
              }}><RefreshCw size={16} /> {t('common.refresh')}</button>
              {user.role === 'GUARDIAN' && (
                <button className="primary" type="button" onClick={() => { setModal(page === 'schedules' ? 'schedule' : page === 'subjects' ? 'subject' : 'assignment'); setForm({}); }}>
                  <Plus size={17} /> {t('common.create')}
                </button>
              )}
            </div>
          </div>

          {page !== 'dashboard' && Boolean(error) && (
            <div className="error banner" role="alert">
              {localizedApiMessage(error, t)}
              <button type="button" onClick={() => setError(null)}>{t('common.dismiss')}</button>
            </div>
          )}
          {page === 'dashboard' && Boolean(dashboardError) && (
            <div className="error banner" role="alert">
              {localizedApiMessage(dashboardError, t)}
              <button type="button" onClick={() => window.location.reload()}>{t('common.retry')}</button>
            </div>
          )}

          {page === 'dashboard' && (
            <>
              {loading ? <DashboardSkeleton /> : (
                <>
                  <section className="stats">
                    <Stat icon={Clock3} label={t('dashboard.sessionsToday')} value={data?.metrics?.sessions_today != null ? t('dashboard.sessionCount', { count: formatNumber(data.metrics.sessions_today) }) : '—'} hint={t('dashboard.recordedSessions')} tone="violet" />
                    <Stat icon={CheckCircle2} label={t('dashboard.tasksCompleted')} value={data?.metrics?.completed_tasks != null ? formatNumber(data.metrics.completed_tasks) : '—'} hint={t('dashboard.tasksAssigned', { count: formatNumber(data?.metrics?.tasks ?? 0) })} tone="green" />
                    <Stat icon={CalendarDays} label={t('dashboard.todaySchedule')} value={data?.metrics?.scheduled_today != null ? formatNumber(data.metrics.scheduled_today) : '—'} hint={t('dashboard.plannedBlocks')} tone="blue" />
                    <Stat icon={Flame} label={t('dashboard.streak')} value="—" hint={t('dashboard.noVerifiedHistory')} tone="amber" />
                  </section>
                  <section className="grid">
                    <article className="panel timeline">
                      <div className="panel-head">
                        <div><p className="eyebrow">{t('dashboard.todayLearning').toUpperCase()}</p><h2>{t('dashboard.todayLearning')}</h2></div>
                        <button className="text-btn" type="button" onClick={() => setPage('schedules')}>{t('dashboard.viewSchedule')} <ChevronRight size={15} /></button>
                      </div>
                      {(data?.schedules || []).slice(0, 4).map((item: any, index: number) => (
                        <button className="event" type="button" key={item.id} onClick={() => setPage('schedules')}>
                          <span className="time">{item.start_at ? formatTime(item.start_at) : '—'}</span>
                          <span className={`event-dot c${index}`} />
                          <span className="event-copy"><b>{item.title}</b><small>{statusText(item.study_type, t) || t('schedules.learningSession')}{item.location ? ` · ${item.location}` : ''}</small></span>
                          <ChevronRight size={15} className="faint" />
                        </button>
                      ))}
                      {!data?.schedules?.length && <Empty icon={CalendarDays} title={t('dashboard.noSchedules')} body={t('dashboard.noSchedulesBody')} />}
                    </article>
                    <article className="panel focus">
                      <div className="panel-head">
                        <div><p className="eyebrow">{t('dashboard.nextStep')}</p><h2>{t('dashboard.learningTasks')}</h2></div>
                        <span className="pill">{t('common.total', { count: data?.metrics?.tasks ?? 0 })}</span>
                      </div>
                      {(data?.tasks || []).slice(0, 4).map((task: any) => (
                        <button className="task" type="button" key={task.id} onClick={() => setPage('assignments')}>
                          <span className={task.status === 'COMPLETED' ? 'check done' : 'check'}>{task.status === 'COMPLETED' && <CheckCircle2 size={16} />}</span>
                          <span><b>{task.title}</b><small>{task.due_at ? t('dashboard.dueDate', { date: formatDate(task.due_at) }) : t('dashboard.noDueDate')} · {statusText(task.priority, t) || t('status.normal')}</small></span>
                          <span className="task-state">{statusText(task.status, t)}</span>
                        </button>
                      ))}
                      {!data?.tasks?.length && <Empty icon={ClipboardCheck} title={t('dashboard.noAssignments')} body={t('dashboard.noAssignmentsBody')} />}
                    </article>
                    <article className="panel insight">
                      <div className="insight-icon"><Brain /></div>
                      <div>
                        <p className="eyebrow">{t('dashboard.aiTitle')}</p><h2>{t('dashboard.aiHeadline')}</h2>
                        <p className="muted">{t('dashboard.aiBody')}</p>
                        <button className="secondary" type="button" onClick={() => setPage('ai')}>{t('dashboard.openAI')} <ChevronRight size={15} /></button>
                      </div>
                    </article>
                    <article className="panel status">
                      <div className="panel-head"><div><p className="eyebrow">{t('dashboard.deviceStatus')}</p><h2>{t('dashboard.monitoringTransparency')}</h2></div><ShieldCheck size={20} /></div>
                      <div className="status-row"><span className={data?.state === 'connected' ? 'status-dot online' : 'status-dot'} /><div><b>{data?.state === 'connected' ? t('dashboard.agentConnected') : t('dashboard.agentUnknown')}</b><small>{t('dashboard.agentLabel')}</small></div></div>
                      <p className="privacy">{t('dashboard.browserPrivacy')}</p>
                      <button className="text-btn" type="button" onClick={() => setPage('monitoring')}>{t('dashboard.monitoringDetails')} <ChevronRight size={15} /></button>
                    </article>
                  </section>
                </>
              )}
            </>
          )}

          {page !== 'dashboard' && (
            <section className="panel records">
              <div className="panel-head">
                <div><p className="eyebrow">{t('subjects.section')}</p><h2>{t(nav.find((item) => item[2] === page)?.[0] || 'common.overview')}</h2></div>
                {['assignments', 'schedules', 'subjects'].includes(page) && user.role === 'GUARDIAN' && (
                  <button className="primary" type="button" onClick={() => { setModal(page === 'schedules' ? 'schedule' : page === 'subjects' ? 'subject' : 'assignment'); setForm({}); }}>
                    <Plus size={16} /> {t('common.createNew')}
                  </button>
                )}
              </div>
              {loading ? <RecordsSkeleton /> : page === 'ai' ? (
                <Empty icon={Brain} title={t('ai.providerTitle')} body={t('ai.providerBody')} />
              ) : page === 'quizzes' ? (
                <QuizPanel token={token} user={user} quizzes={visibleRecords} confirm={confirm} />
              ) : page === 'monitoring' ? (
                <>
                  <p className="muted">{t('devices.description')}</p>
                  {(data?.devices || []).map((device: any) => (
                    <div className="record" key={device.id}>
                      <Monitor /><div><b>{device.device_name}</b><small>{device.operating_system || t('devices.windows')} · Agent {device.agent_version || 'unknown'}</small></div>
                      <span className="pill">{statusText(device.agent_status, t)}</span>
                      <small>{t('devices.heartbeat', { time: device.last_heartbeat_at ? formatDateTime(device.last_heartbeat_at) : t('devices.neverConnected') })}</small>
                    </div>
                  ))}
                  {!data?.devices?.length && <Empty icon={Monitor} title={t('devices.noDevice')} body={t('devices.noDeviceBody')} />}
                </>
              ) : error ? (
                <div className="empty"><p>{t('empty.loadFailed')}</p><button className="secondary" type="button" onClick={() => setPage('dashboard')}>{t('common.backDashboard')}</button></div>
              ) : visibleRecords.length ? (
                visibleRecords.map((item: any) => (
                  <button className="record" type="button" key={item.id}>
                    <BookOpen /><div><b>{item.title || item.name || item.domain || item.device_name || item.notification_type || t('common.emptyRecord')}</b><small>{item.description || statusText(item.status, t) || (item.created_at ? formatDateTime(item.created_at) : item.message || '')}</small></div>
                    <span className="pill">{statusText(item.status, t) || statusText(item.priority, t) || t('common.saved')}</span>
                  </button>
                ))
              ) : (
                <Empty icon={page === 'analytics' ? ChartNoAxesCombined : page === 'quizzes' ? Brain : FileText} title={search ? t('common.noSearchResults') : t('empty.sectionTitle')} body={search ? t('common.noSearchResultsBody') : t('empty.sectionBody')} />
              )}
            </section>
          )}
        </div>
      </main>

      {modal && (
        <div className="overlay" role="presentation" onMouseDown={(event) => { if (event.target === event.currentTarget) void closeModal(); }}>
          <form className="modal" onSubmit={save} onClick={(event) => event.stopPropagation()}>
            <button type="button" aria-label={t('common.close')} className="close" onClick={() => void closeModal()}><X size={18} /></button>
            <p className="eyebrow">{t('modal.guardianAction')}</p>
            <h2>{t('modal.create', { item: t(modal === 'subject' ? 'modal.subject' : modal === 'schedule' ? 'modal.schedule' : 'modal.assignment') })}</h2>
            <label>{t('common.title')}<input required value={form.title || ''} onChange={(event) => setForm({ ...form, title: event.target.value })} /></label>
            <label>{t('common.description')}<textarea value={form.description || ''} onChange={(event) => setForm({ ...form, description: event.target.value })} /></label>
            {modal === 'schedule' && (
              <>
                <label>{t('modal.start')}<input required type="datetime-local" value={form.start_at || ''} onChange={(event) => setForm({ ...form, start_at: event.target.value })} /></label>
                <label>{t('modal.end')}<input required type="datetime-local" value={form.end_at || ''} onChange={(event) => setForm({ ...form, end_at: event.target.value })} /></label>
              </>
            )}
            {modal === 'assignment' && (
              <>
                <label>{t('tasks.due')}<input type="datetime-local" value={form.due_at || ''} onChange={(event) => setForm({ ...form, due_at: event.target.value })} /></label>
                <label>{t('tasks.estimatedMinutes')}<input type="number" min="1" value={form.estimated_minutes || ''} onChange={(event) => setForm({ ...form, estimated_minutes: Number(event.target.value) })} /></label>
              </>
            )}
            <div className="modal-actions">
              <button type="button" className="secondary" onClick={() => void closeModal()}>{t('common.cancel')}</button>
              <button className="primary" disabled={submitting}>{submitting ? t('common.saving') : t('common.save')}</button>
            </div>
          </form>
        </div>
      )}
    </div>
  );
}

function Stat({ icon: Icon, label, value, hint, tone }: any) {
  return (
    <article className="stat" title={hint}>
      <div className={`stat-icon ${tone}`}><Icon size={19} /></div>
      <div><small>{label}</small><strong>{value}</strong><span>{hint}</span></div>
    </article>
  );
}

function Empty({ icon: Icon, title, body }: any) {
  return <div className="empty"><div className="empty-icon"><Icon size={21} /></div><b>{title}</b><p>{body}</p></div>;
}

function DashboardSkeleton() {
  return (
    <>
      <section className="stats">{[0, 1, 2, 3].map((item) => <div className="stat skeleton" key={item}><div className="skeleton-block icon" /><div className="skeleton-lines"><div /><div /><div /></div></div>)}</section>
      <section className="grid">{[0, 1, 2, 3].map((item) => <div className="panel skeleton-panel" key={item}><div className="skeleton-line short" /><div className="skeleton-line" /><div className="skeleton-line" /></div>)}</section>
    </>
  );
}

function RecordsSkeleton() {
  return <div className="records-skeleton">{[0, 1, 2, 3].map((item) => <div className="record-skeleton" key={item}><div className="skeleton-block" /><div><div className="skeleton-line" /><div className="skeleton-line short" /></div></div>)}</div>;
}

function QuizPanel({ token, user, quizzes, confirm }: any) {
  const { t, formatNumber } = useI18n();
  const { notify } = useNotifications();
  const [active, setActive] = useState<any>(null);
  const [attempt, setAttempt] = useState('');
  const [answers, setAnswers] = useState<any>({});
  const [result, setResult] = useState<any>(null);

  async function begin(id: string) {
    try {
      const quiz = await api(`/quizzes/${id}`, token);
      const started = await api(`/quizzes/${id}/attempts`, token, { method: 'POST', body: '{}' });
      setActive(quiz);
      setAttempt(started.id);
      setAnswers({});
      setResult(null);
    } catch (error: any) {
      notify('error', localizedApiMessage(error, t));
    }
  }

  async function submit() {
    if (!await confirm(t('quizzes.confirmSubmit'), t('quizzes.confirmTitle'))) return;
    try {
      const response = await api(`/quiz-attempts/${attempt}/submit`, token, {
        method: 'POST',
        body: JSON.stringify({
          answers: Object.entries(answers).map(([question_id, value]: any) => ({ question_id, ...value })),
        }),
      });
      setResult(response);
      notify('success', t('quizzes.submittedSuccess'));
    } catch (error: any) {
      notify('error', localizedApiMessage(error, t));
    }
  }

  if (active) {
    return (
      <div className="quiz">
        <div className="panel-head">
          <div><p className="eyebrow">{t('quizzes.assessment')}</p><h2>{active.title}</h2></div>
          <span className="pill">{t('quizzes.questions', { count: formatNumber(active.questions.length) })}</span>
        </div>
        {active.questions.map((question: any, index: number) => (
          <div className="question" key={question.id}>
            <b>{t('quizzes.question', { number: index + 1, text: question.question_text })}</b>
            {question.options?.length ? question.options.map((option: any) => (
              <label className="option" key={option.id}>
                <input type="radio" name={question.id} checked={answers[question.id]?.selected_option_id === option.id} onChange={() => setAnswers({ ...answers, [question.id]: { selected_option_id: option.id } })} />
                {option.option_label ? `${option.option_label}. ` : ''}{option.option_text}
              </label>
            )) : (
              <textarea placeholder={t('quizzes.answerPlaceholder')} value={answers[question.id]?.answer_text || ''} onChange={(event) => setAnswers({ ...answers, [question.id]: { answer_text: event.target.value } })} />
            )}
          </div>
        ))}
        {result ? (
          <div className="result">
            <CheckCircle2 size={20} /><b>{t('quizzes.resultScore', { score: result.score })}</b>
            <span>{result.passed ? t('quizzes.passed') : t('quizzes.review')}</span>
            <button className="secondary" type="button" onClick={() => setActive(null)}>{t('quizzes.back')}</button>
          </div>
        ) : <button className="primary" type="button" onClick={submit}>{t('quizzes.submit')}</button>}
      </div>
    );
  }

  return (
    <>
      {quizzes.filter((quiz: any) => quiz.is_active).map((quiz: any) => (
        <div className="record" key={quiz.id}>
          <Brain /><div><b>{quiz.title}</b><small>{quiz.description || t('quizzes.summary', { count: quiz.question_count, score: quiz.passing_score })}</small></div>
          {user.role === 'STUDENT' && <button className="primary" type="button" onClick={() => begin(quiz.id)}>{t('quizzes.start')}</button>}
          <span className="pill">{statusText(quiz.difficulty, t) || t('quizzes.assessment')}</span>
        </div>
      ))}
      {!quizzes.length && <Empty icon={Brain} title={t('quizzes.publishedTitle')} body={t('quizzes.publishedBody')} />}
    </>
  );
}
