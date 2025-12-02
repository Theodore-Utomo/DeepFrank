'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { sendMagicLink } from '@/lib/api';
import { DashboardLayout } from '@/components/layouts/DashboardLayout';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Loader2, Mail, CheckCircle2, AlertCircle, ArrowLeft } from 'lucide-react';

export default function LoginPage() {
  const [email, setEmail] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);
  const router = useRouter();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setLoading(true);

    try {
      await sendMagicLink(email);
      setSuccess(true);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to send magic link');
    } finally {
      setLoading(false);
    }
  };

  return (
    <DashboardLayout showSidebar={false}>
      <div className="min-h-[calc(100vh-8rem)] flex items-center justify-center">
        <div className="w-full max-w-md space-y-6">
          <Card className="p-8">
            {/* Header */}
            <div className="text-center mb-8 space-y-4">
              <Link href="/" className="inline-block">
                <div className="flex items-center justify-center gap-2 mb-4">
                  <div className="w-12 h-12 bg-primary rounded-lg flex items-center justify-center">
                    <span className="text-primary-foreground font-bold text-xl">F</span>
                  </div>
                  <h1 className="text-3xl font-bold text-foreground">DeepFrank</h1>
                </div>
              </Link>
              <h2 className="text-2xl font-bold text-foreground">Sign in to your account</h2>
              <p className="text-sm text-muted-foreground">
                We'll send you a magic link to sign in
              </p>
            </div>

            {success ? (
              <div className="space-y-4">
                <div className="p-4 bg-primary/10 border border-primary/20 rounded-lg">
                  <div className="flex items-start gap-3">
                    <CheckCircle2 className="h-5 w-5 text-primary mt-0.5 flex-shrink-0" />
                    <div className="flex-1">
                      <h3 className="font-semibold text-foreground mb-1">
                        Magic link sent!
                      </h3>
                      <p className="text-sm text-muted-foreground">
                        We've sent a magic link to <strong className="text-foreground">{email}</strong>. 
                        Please check your email and click the link to sign in.
                      </p>
                    </div>
                  </div>
                </div>
                <Button
                  onClick={() => {
                    setSuccess(false);
                    setEmail('');
                  }}
                  variant="outline"
                  className="w-full"
                >
                  Send another link
                </Button>
              </div>
            ) : (
              <form className="space-y-6" onSubmit={handleSubmit}>
                {error && (
                  <div className="p-4 bg-destructive/10 border border-destructive/20 rounded-lg">
                    <div className="flex items-start gap-3">
                      <AlertCircle className="h-5 w-5 text-destructive mt-0.5 flex-shrink-0" />
                      <p className="text-sm text-destructive">{error}</p>
                    </div>
                  </div>
                )}

                <div className="space-y-2">
                  <label htmlFor="email" className="text-sm font-medium text-foreground">
                    Email address
                  </label>
                  <Input
                    id="email"
                    name="email"
                    type="email"
                    autoComplete="email"
                    required
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    placeholder="you@example.com"
                    className="w-full"
                  />
                </div>

                <Button
                  type="submit"
                  disabled={loading}
                  className="w-full"
                  size="lg"
                >
                  {loading ? (
                    <>
                      <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                      Sending...
                    </>
                  ) : (
                    <>
                      <Mail className="mr-2 h-4 w-4" />
                      Send magic link
                    </>
                  )}
                </Button>
              </form>
            )}

            <div className="mt-6 text-center">
              <Link
                href="/"
                className="inline-flex items-center text-sm text-muted-foreground hover:text-foreground transition-colors"
              >
                <ArrowLeft className="mr-2 h-4 w-4" />
                Back to home
              </Link>
            </div>
          </Card>
        </div>
      </div>
    </DashboardLayout>
  );
}
