export function generateStaticParams() {
  return [{ id: 'TA-017' }, { id: 'TA-018' }, { id: 'TA-019' }];
}

export default function Layout({ children }: { children: React.ReactNode }) {
  return <>{children}</>;
}
