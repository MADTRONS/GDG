import { LoginForm } from "@/components/auth/LoginForm";

export default function Home() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-4 bg-gradient-to-b from-slate-50 to-slate-100">
      <LoginForm />
    </main>
  );
}
