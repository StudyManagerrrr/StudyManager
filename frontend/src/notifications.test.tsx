// @vitest-environment jsdom
import { afterEach, beforeEach, describe, expect, it } from 'vitest';
import { cleanup, fireEvent, render, screen, waitFor } from '@testing-library/react';
import { I18nProvider } from './i18n';
import { NotificationProvider, useNotifications } from './notifications';

afterEach(() => { cleanup(); localStorage.clear(); });
beforeEach(() => { localStorage.setItem('guardian_language', 'en'); });

function NotificationProbe() {
  const { notify, confirm } = useNotifications();
  return <>
    <button onClick={() => { notify('success', 'Changes saved.'); notify('success', 'Changes saved.'); }}>save</button>
    <button onClick={async () => { const accepted = await confirm('Submit this quiz?', 'Submit quiz'); document.body.dataset.confirmed = String(accepted); }}>confirm</button>
  </>;
}

describe('shared feedback system', () => {
  it('shows a deduplicated accessible toast and lets the user dismiss it', () => {
    render(<I18nProvider><NotificationProvider><NotificationProbe /></NotificationProvider></I18nProvider>);
    fireEvent.click(screen.getByText('save'));
    expect(screen.getAllByRole('status').filter(item => item.textContent?.includes('Changes saved.'))).toHaveLength(1);
    fireEvent.click(screen.getByRole('button', { name: 'Dismiss notification' }));
    expect(screen.queryByText('Changes saved.')).toBeNull();
  });

  it('waits for an accessible confirmation choice', async () => {
    render(<I18nProvider><NotificationProvider><NotificationProbe /></NotificationProvider></I18nProvider>);
    fireEvent.click(screen.getByText('confirm'));
    expect(screen.getByRole('alertdialog').textContent).toContain('Submit this quiz?');
    fireEvent.click(screen.getByRole('button', { name: 'Confirm' }));
    await waitFor(() => expect(document.body.dataset.confirmed).toBe('true'));
    expect(screen.queryByRole('alertdialog')).toBeNull();
  });
});
