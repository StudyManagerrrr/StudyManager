// @vitest-environment jsdom
import { afterEach, describe, expect, it } from 'vitest';
import { cleanup, fireEvent, render, screen } from '@testing-library/react';
import { useState } from 'react';
import { I18nProvider, LanguageSwitcher, readLanguage, useI18n } from './i18n';
import vi from './locales/vi';
import en from './locales/en';

afterEach(() => { cleanup(); localStorage.clear(); });

function LanguageProbe() {
  const { language, t, formatDate, formatNumber } = useI18n();
  const [value, setValue] = useState('unsaved form value');
  return <>
    <LanguageSwitcher />
    <input aria-label="draft" value={value} onChange={event => setValue(event.target.value)} />
    <output aria-label="language">{language}</output>
    <output aria-label="sign-in">{t('auth.signIn')}</output>
    <output aria-label="date">{formatDate(new Date('2026-01-02T12:00:00Z'))}</output>
    <output aria-label="number">{formatNumber(1234.5)}</output>
  </>;
}

describe('language preferences and localization', () => {
  it('defaults new users to Vietnamese and reads stored supported preferences', () => {
    expect(readLanguage({ getItem: () => null })).toBe('vi');
    expect(readLanguage({ getItem: () => 'en' })).toBe('en');
    expect(readLanguage({ getItem: () => 'fr' })).toBe('vi');
    render(<I18nProvider><LanguageProbe /></I18nProvider>);
    expect(screen.getByLabelText('language').textContent).toBe('vi');
    expect(screen.getByLabelText('sign-in').textContent).toBe('Đăng nhập');
  });

  it('switches both ways without reloading or discarding an in-progress form', () => {
    render(<I18nProvider><LanguageProbe /></I18nProvider>);
    fireEvent.change(screen.getByLabelText('draft'), { target: { value: 'keep this draft' } });
    fireEvent.click(screen.getByRole('button', { name: 'English' }));
    expect(screen.getByLabelText('language').textContent).toBe('en');
    expect(screen.getByLabelText('sign-in').textContent).toBe('Sign in');
    expect((screen.getByLabelText('draft') as HTMLInputElement).value).toBe('keep this draft');
    fireEvent.click(screen.getByRole('button', { name: 'Tiếng Việt' }));
    expect(screen.getByLabelText('language').textContent).toBe('vi');
    expect((screen.getByLabelText('draft') as HTMLInputElement).value).toBe('keep this draft');
  });

  it('persists preference across provider remounts and formats dates/numbers by locale', () => {
    const first = render(<I18nProvider><LanguageProbe /></I18nProvider>);
    fireEvent.click(screen.getByRole('button', { name: 'English' }));
    expect(localStorage.getItem('guardian_language')).toBe('en');
    expect(screen.getByLabelText('date').textContent).toContain('01/02/2026');
    expect(screen.getByLabelText('number').textContent).toBe('1,234.5');
    first.unmount();
    render(<I18nProvider><LanguageProbe /></I18nProvider>);
    expect(screen.getByLabelText('language').textContent).toBe('en');
    fireEvent.click(screen.getByRole('button', { name: 'Tiếng Việt' }));
    expect(screen.getByLabelText('date').textContent).toContain('02/01/2026');
    expect(screen.getByLabelText('number').textContent).toBe('1.234,5');
  });

  it('keeps translation dictionaries in sync', () => {
    expect(Object.keys(vi).sort()).toEqual(Object.keys(en).sort());
    expect(Object.values(vi).join(' ')).not.toMatch(/Ã|Â|â€|�/);
    expect(Object.values(en).join(' ')).not.toMatch(/Ã|Â|â€|�/);
  });
});
