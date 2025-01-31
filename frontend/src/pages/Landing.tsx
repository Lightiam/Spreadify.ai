import { Button } from "@/components/ui/button";
import { Link } from "react-router-dom";

export default function Landing() {
  return (
    <div className="min-h-screen bg-background">
      <nav className="container mx-auto px-4 py-6 flex justify-between items-center">
        <div className="text-2xl font-bold">Spreadify</div>
        <div className="space-x-4">
          <Link to="/login">
            <Button variant="ghost">Login</Button>
          </Link>
          <Link to="/pricing">
            <Button>Get Started</Button>
          </Link>
        </div>
      </nav>
      
      <main className="container mx-auto px-4 py-20">
        <div className="text-center max-w-4xl mx-auto">
          <h1 className="text-6xl font-bold tracking-tight">
            Professional Live Streaming Made Easy
          </h1>
          <p className="mt-6 text-xl text-muted-foreground">
            Create professional live streams and recordings with just your browser. 
            Add guests, share your screen, and stream to multiple platforms simultaneously.
          </p>
          <div className="mt-10 flex justify-center gap-4">
            <Link to="/pricing">
              <Button size="lg">Start Streaming</Button>
            </Link>
            <Link to="/studio">
              <Button variant="outline" size="lg">Try Demo</Button>
            </Link>
          </div>
        </div>

        <div className="mt-20 grid grid-cols-1 md:grid-cols-3 gap-8">
          <div className="p-6 rounded-lg border">
            <h3 className="text-xl font-semibold">Multi-Platform Streaming</h3>
            <p className="mt-2 text-muted-foreground">
              Stream to YouTube, Facebook, Twitch and more simultaneously
            </p>
          </div>
          <div className="p-6 rounded-lg border">
            <h3 className="text-xl font-semibold">Browser-Based</h3>
            <p className="mt-2 text-muted-foreground">
              No downloads required. Stream directly from your browser
            </p>
          </div>
          <div className="p-6 rounded-lg border">
            <h3 className="text-xl font-semibold">Guest Management</h3>
            <p className="mt-2 text-muted-foreground">
              Invite guests to join your stream with just a link
            </p>
          </div>
        </div>
      </main>
    </div>
  );
}
