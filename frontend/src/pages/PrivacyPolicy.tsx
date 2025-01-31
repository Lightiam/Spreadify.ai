import { Button } from "@/components/ui/button";
import { Link } from "react-router-dom";

export default function PrivacyPolicy() {
  return (
    <div className="min-h-screen bg-background">
      <nav className="container mx-auto px-4 py-6 flex justify-between items-center">
        <Link to="/" className="text-2xl font-bold">
          Spreadify
        </Link>
        <div className="space-x-4">
          <Link to="/login">
            <Button variant="ghost">Login</Button>
          </Link>
          <Link to="/pricing">
            <Button>Get Started</Button>
          </Link>
        </div>
      </nav>

      <main className="container mx-auto px-4 py-12 max-w-4xl">
        <h1 className="text-4xl font-bold mb-8">Privacy Policy</h1>
        
        <div className="prose prose-lg">
          <section className="mb-8">
            <h2 className="text-2xl font-semibold mb-4">1. Information We Collect</h2>
            <p className="text-muted-foreground">
              We collect information you provide directly to us when using Spreadify, including:
            </p>
            <ul className="list-disc pl-6 mt-2 space-y-2">
              <li>Account information (name, email, profile picture)</li>
              <li>Content you create and share through our platform</li>
              <li>Payment information when you subscribe to our services</li>
              <li>Technical information about your device and connection</li>
            </ul>
          </section>

          <section className="mb-8">
            <h2 className="text-2xl font-semibold mb-4">2. How We Use Your Information</h2>
            <p className="text-muted-foreground">
              We use the collected information to:
            </p>
            <ul className="list-disc pl-6 mt-2 space-y-2">
              <li>Provide and improve our streaming services</li>
              <li>Process your payments and subscriptions</li>
              <li>Send you important updates and notifications</li>
              <li>Analyze and optimize our platform performance</li>
            </ul>
          </section>

          <section className="mb-8">
            <h2 className="text-2xl font-semibold mb-4">3. Data Security</h2>
            <p className="text-muted-foreground">
              We implement appropriate security measures to protect your personal information.
              However, no method of transmission over the Internet is 100% secure.
            </p>
          </section>

          <section className="mb-8">
            <h2 className="text-2xl font-semibold mb-4">4. Contact Us</h2>
            <p className="text-muted-foreground">
              If you have any questions about this Privacy Policy, please contact us at:
              support@spreadify.io
            </p>
          </section>
        </div>

        <div className="mt-12 text-center">
          <Link to="/">
            <Button variant="outline">Back to Home</Button>
          </Link>
        </div>
      </main>
    </div>
  );
}
